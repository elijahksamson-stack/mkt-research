"""
HAC (Newey-West) corrected log-linear trend regression for a single
strictly-positive series (a price, or a relative-strength ratio -- see
relative_strength.py).

Deliberately self-contained: Macro/Rates/rates_macro/trend_rr.py already
implements the same HAC-log-regression + AR(1)-forecast + residual-channel
model (its docstring notes it was "originally sketched for sector-ETF
ranking" -- i.e. an earlier version of this exact math). This package
intentionally keeps its own copy rather than taking a cross-domain
dependency on Macro/Rates, so if the formula is ever retuned, check both
this module and rates_macro/trend_rr.py.

Per-window regression:
  1. Fit log(price) ~ a + b*t by OLS over the trailing `window` bars.
  2. Correct the slope's standard error for serial correlation in the
     residuals (Newey-West/HAC) -- trend residuals are autocorrelated
     day-to-day, so naive OLS standard errors overstate confidence.
  3. `residual_z`: how far today's close sits from the fitted trend line,
     in residual-sigma units (positive = above trend).
  4. An AR(1) fit to the residuals produces a `forecast_return`: where the
     price is expected to land `forecast_days` out if the trend continues
     and the current residual mean-reverts at its own persistence rate.
  5. `channel_rr`: asymmetry of a +/-CHANNEL_SIGMA residual channel around
     today's price -- how much more room is left to the top of the channel
     than to the bottom.

`regression_profile` blends the per-window fits across multiple windows
into two summary numbers:
  - `trend_signal` in [-1, 1]: weighted, R2-discounted tanh of the HAC
    t-stat -- a directional read that discounts low-confidence fits.
  - `opportunity` in [0, 100]: how favorably the forecast, channel
    asymmetry, entry timing (residual_z), and fit confidence line up,
    gated by trend strength so a strong opportunity score still requires
    a trend actually being present.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

DEFAULT_WINDOWS: tuple[int, ...] = (21, 63, 126, 252)
DEFAULT_WEIGHTS: dict[int, float] = {21: 0.18, 63: 0.32, 126: 0.30, 252: 0.20}
OPPORTUNITY_WINDOWS: tuple[tuple[int, float], ...] = ((63, 0.45), (126, 0.35), (252, 0.20))
CHANNEL_SIGMA = 2.0
FORECAST_DAYS = 21
MIN_OBSERVATIONS_FLOOR = 18
MIN_OBSERVATIONS_WINDOW_FRACTION = 0.75


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


@dataclass(frozen=True)
class WindowRegression:
    window: int
    slope_daily: float
    slope_annual: float
    r2: float
    t_hac: float
    residual_sigma: float
    residual_z: float
    residual_phi: float
    forecast_return: float
    channel_rr: float


@dataclass(frozen=True)
class RegressionProfile:
    trend_signal: float  # -1..1
    opportunity: float  # 0..100
    windows: dict[int, WindowRegression] = field(default_factory=dict)


def hac_log_regression(
    series: pd.Series, window: int, forecast_days: int = FORECAST_DAYS
) -> Optional[WindowRegression]:
    """Fit + HAC-correct a single window. Returns None when fewer than
    max(18, 0.75*window) valid positive observations are available."""
    values = pd.Series(series).dropna().astype(float)
    values = values[values > 0].tail(window)
    n = len(values)
    if n < max(MIN_OBSERVATIONS_FLOOR, int(window * MIN_OBSERVATIONS_WINDOW_FRACTION)):
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

    # Newey-West/HAC: correct slope variance for serially correlated residuals.
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

    # AR(1) residual persistence -> a regression-only forward forecast.
    denom = float(resid[:-1] @ resid[:-1])
    phi = float(np.clip((resid[:-1] @ resid[1:]) / denom, -0.99, 0.99)) if denom > 1e-18 else 0.0
    expected_resid = (phi**forecast_days) * current_resid
    forecast_log_return = slope * forecast_days + expected_resid - current_resid
    upper_distance = max(CHANNEL_SIGMA * sigma - current_resid, 0.0)
    lower_distance = max(CHANNEL_SIGMA * sigma + current_resid, sigma * 0.05)
    channel_rr = upper_distance / lower_distance

    return WindowRegression(
        window=window,
        slope_daily=slope,
        slope_annual=float(np.expm1(np.clip(slope * 252, -5, 5))),
        r2=float(np.clip(r2, 0, 1)),
        t_hac=float(t_hac),
        residual_sigma=sigma,
        residual_z=float(z),
        residual_phi=phi,
        forecast_return=float(np.expm1(np.clip(forecast_log_return, -2, 2))),
        channel_rr=float(channel_rr),
    )


def _opportunity_component(stat: WindowRegression) -> float:
    sigma = max(stat.residual_sigma, 1e-9)
    forecast_score = sigmoid(1.35 * np.log1p(stat.forecast_return) / sigma)
    asymmetry_score = stat.channel_rr / (1 + stat.channel_rr)
    entry_score = np.exp(-0.5 * ((stat.residual_z + 0.35) / 0.90) ** 2)
    confidence = min(abs(stat.t_hac) / 4.0, 1.0) * np.sqrt(stat.r2)
    trend_gate = 0.45 + 0.55 * sigmoid(stat.t_hac / 2.0)
    return trend_gate * (
        0.38 * forecast_score + 0.32 * asymmetry_score + 0.20 * entry_score + 0.10 * confidence
    )


def regression_profile(
    series: pd.Series,
    windows: tuple[int, ...] = DEFAULT_WINDOWS,
    weights: dict[int, float] = DEFAULT_WEIGHTS,
) -> RegressionProfile:
    """Blend hac_log_regression across `windows` into trend_signal + opportunity.

    Raises ValueError if no window has enough observations to fit."""
    stats = {w: hac_log_regression(series, w) for w in windows}
    available = {w: s for w, s in stats.items() if s is not None}
    if not available:
        raise ValueError("No regression window has sufficient observations.")

    weight_total = sum(weights[w] for w in available)
    directional = 0.0
    for w, s in available.items():
        certainty = np.sqrt(max(s.r2, 0))
        directional += weights[w] * np.tanh(s.t_hac / 3.0) * certainty
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
        # shorter window did, so a young series still scores.
        fallback = next(iter(available.values()))
        opportunity = 100 * _opportunity_component(fallback)

    return RegressionProfile(
        trend_signal=float(np.clip(directional, -1, 1)),
        opportunity=float(np.clip(opportunity, 0, 100)),
        windows=available,
    )
