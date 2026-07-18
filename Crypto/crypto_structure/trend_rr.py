"""
Trend and mean-reversion analytics for a single price/ratio series — the
core regression engine behind both the per-asset trend signal fed into
crypto_gauge.py and the peer/benchmark leadership ranking in
relative_strength.py (run it on a raw close series for "absolute" trend, or
on a ratio series like BTC-USD/ETH-USD for "relative strength").

HAC (Newey-West) corrected log-linear regression + a residual channel,
adapted from Macro/Rates/rates_macro/trend_rr.py (itself the distillation
behind the equity sector-rotation script this package's relative_strength
ranking mirrors). The one deliberate change from that source: crypto trades
every calendar day, not ~252 trading days/year, so window lengths are
calendar-day equivalents (30/91/182/365 for ~1mo/3mo/6mo/1yr) and
annualization uses PERIODS_PER_YEAR=365 instead of 252 -- using 252 here
would understate annualized growth by roughly 31% because it would treat
365 real days of drift as if they were only 252 trading days' worth. No
network or I/O — pure math on a pandas/numpy series, fully unit-testable
offline.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

PERIODS_PER_YEAR = 365  # crypto trades every calendar day, unlike equities' ~252 trading days/year
DEFAULT_WINDOWS = (30, 91, 182, 365)  # ~1mo / ~3mo / ~6mo / ~1yr in calendar days
DEFAULT_WEIGHTS = {30: 0.18, 91: 0.32, 182: 0.30, 365: 0.20}
OPPORTUNITY_WINDOWS = ((91, 0.45), (182, 0.35), (365, 0.20))
CHANNEL_SIGMA = 2.0
FORECAST_DAYS = 21


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


def hac_log_regression(
    series: pd.Series, window: int, forecast_days: int = FORECAST_DAYS
) -> Optional[dict]:
    """HAC (Newey-West) corrected log-linear trend regression over the last
    `window` observations of `series`.

    Returns None when fewer than max(18, 0.75*window) valid positive
    observations are available to fit against.
    """
    values = pd.Series(series).dropna().astype(float)
    values = values[values > 0].tail(window)
    n = len(values)
    if n < max(18, int(window * 0.75)):
        return None

    y = np.log(values.to_numpy())
    x = np.arange(n, dtype=float)
    X = np.column_stack([np.ones(n), x])
    inv_xx = np.linalg.pinv(X.T @ X)
    beta_vec = inv_xx @ X.T @ y
    fitted = X @ beta_vec
    resid = y - fitted
    sse = float(resid @ resid)
    sst = float((y - y.mean()) @ (y - y.mean()))
    r2 = 1 - sse / sst if sst > 0 else 0.0

    # Newey-West/HAC slope uncertainty corrects for serially correlated
    # trend residuals (crypto series are heavily autocorrelated day to day).
    lag = max(1, int(4 * (n / 100) ** (2 / 9)))
    meat = np.zeros((2, 2))
    for t in range(n):
        xt = X[t][:, None]
        meat += resid[t] ** 2 * (xt @ xt.T)
    for j in range(1, lag + 1):
        weight = 1 - j / (lag + 1)
        for t in range(j, n):
            xt, xlag = X[t][:, None], X[t - j][:, None]
            meat += weight * resid[t] * resid[t - j] * (xt @ xlag.T + xlag @ xt.T)
    cov = inv_xx @ meat @ inv_xx
    slope = float(beta_vec[1])
    slope_se = float(np.sqrt(max(cov[1, 1], 1e-18)))
    t_hac = slope / slope_se if slope_se > 0 else 0.0
    sigma = float(np.sqrt(sse / max(n - 2, 1)))
    current_resid = float(resid[-1])
    z = current_resid / sigma if sigma > 1e-12 else 0.0

    # AR(1) residual persistence drives a regression-only forward forecast.
    denom = float(resid[:-1] @ resid[:-1])
    phi = (
        float(np.clip((resid[:-1] @ resid[1:]) / denom, -0.99, 0.99))
        if denom > 1e-18
        else 0.0
    )
    expected_resid = (phi**forecast_days) * current_resid
    forecast_log_return = slope * forecast_days + expected_resid - current_resid
    upper_distance = max(CHANNEL_SIGMA * sigma - current_resid, 0.0)
    lower_distance = max(CHANNEL_SIGMA * sigma + current_resid, sigma * 0.05)
    channel_rr = upper_distance / lower_distance

    return {
        "window": window,
        "slope_daily": slope,
        "slope_annual": float(np.expm1(np.clip(slope * PERIODS_PER_YEAR, -5, 5))),
        "r2": float(np.clip(r2, 0, 1)),
        "t_hac": float(t_hac),
        "residual_sigma": sigma,
        "residual_z": float(z),
        "residual_phi": phi,
        "forecast_return": float(np.expm1(np.clip(forecast_log_return, -2, 2))),
        "channel_rr": float(channel_rr),
    }


def _opportunity_component(stat: dict) -> float:
    sigma = max(stat["residual_sigma"], 1e-9)
    forecast_score = sigmoid(1.35 * np.log1p(stat["forecast_return"]) / sigma)
    asymmetry_score = stat["channel_rr"] / (1 + stat["channel_rr"])
    entry_score = np.exp(-0.5 * ((stat["residual_z"] + 0.35) / 0.90) ** 2)
    confidence = min(abs(stat["t_hac"]) / 4.0, 1.0) * np.sqrt(stat["r2"])
    trend_gate = 0.45 + 0.55 * sigmoid(stat["t_hac"] / 2.0)
    return trend_gate * (
        0.38 * forecast_score
        + 0.32 * asymmetry_score
        + 0.20 * entry_score
        + 0.10 * confidence
    )


def trend_rr_profile(
    series: pd.Series,
    windows: tuple = DEFAULT_WINDOWS,
    weights: dict = DEFAULT_WEIGHTS,
) -> dict:
    """Blend hac_log_regression across multiple windows into a single
    trend_signal in [-1, 1] and an opportunity score in [0, 100].

    Raises ValueError if no window has enough observations to fit.
    """
    stats = {w: hac_log_regression(series, w) for w in windows}
    available = {w: s for w, s in stats.items() if s is not None}
    if not available:
        raise ValueError("No regression window has sufficient observations.")

    weight_total = sum(weights[w] for w in available)
    directional = 0.0
    for w, s in available.items():
        certainty = np.sqrt(max(s["r2"], 0))
        directional += weights[w] * np.tanh(s["t_hac"] / 3.0) * certainty
    directional /= weight_total

    opportunity_parts, opportunity_weights = [], []
    for w, ow in OPPORTUNITY_WINDOWS:
        s = available.get(w)
        if s is None:
            continue
        opportunity_parts.append(_opportunity_component(s))
        opportunity_weights.append(ow)

    if opportunity_parts:
        opportunity = 100 * np.average(opportunity_parts, weights=opportunity_weights)
    else:
        # None of the preferred windows fit -- fall back to whichever
        # shorter window did, so a young asset still scores.
        fallback = next(iter(available.values()))
        opportunity = 100 * _opportunity_component(fallback)

    return {
        "trend_signal": float(np.clip(directional, -1, 1)),
        "opportunity": float(np.clip(opportunity, 0, 100)),
        "windows": stats,
    }


def mean_reversion_snapshot(series: pd.Series, window: int = 365) -> Optional[dict]:
    """How far the latest level sits from its own trailing mean, in units of
    trailing standard deviation. Complements trend_rr_profile's
    HAC-detrended residual_z (distance from the FITTED TREND) with the more
    literal "distance from its own recent history" read. Default window is
    365 calendar days (one crypto year) rather than the 252-trading-day
    equity default. Returns None below 20 observations.
    """
    values = pd.Series(series).dropna().astype(float).tail(window)
    n = len(values)
    if n < 20:
        return None
    mean = float(values.mean())
    std = float(values.std(ddof=1))
    latest = float(values.iloc[-1])
    z = (latest - mean) / std if std > 1e-12 else 0.0
    percentile = float((values < latest).mean() * 100)
    return {
        "window": window,
        "observations": n,
        "latest": latest,
        "mean": mean,
        "std": std,
        "z_score": z,
        "percentile": percentile,
    }
