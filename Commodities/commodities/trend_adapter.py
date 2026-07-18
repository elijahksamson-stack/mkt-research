"""
Multi-horizon trend features, reused unchanged from `rates_macro.trend_rr`
(the existing Trend Analysis engine) -- this module adapts its outputs to
commodities and the spec's 5/21/63-day horizon set. It adds no new trend
math of its own; every number here traces back to `hac_log_regression`,
`trend_rr_profile`, or `mean_reversion_snapshot`.

Horizon handling: `hac_log_regression`'s own minimum-bars gate
(`n >= max(18, 0.75*window)`) makes a literal 5-bar regression window
statistically meaningless -- it always returns None below window~24. Per
`rates_macro`'s own signature, `hac_log_regression(series, window,
forecast_days)` fits on `window` bars but *forecasts* `forecast_days`
ahead, and those are independent parameters. So the 5-day "view" the spec
asks for is built by fitting on a stable 21-bar window and projecting the
regression's own AR(1)-residual-based forecast only 5 days out
(`forecast_days=5`) -- not by shrinking the fit window. This gets a
genuine 5-day-horizon forecast without inventing a second regression
engine or fitting on statistically insufficient data.

`persistence` (this module's one added metric, not present in trend_rr) is
the fraction of available regression windows (21/63/126/252, from
`trend_rr_profile`'s own default set) whose t-stat sign agrees with the
blended `trend_signal` -- the spec's "a short rally inside a broken
intermediate trend should not read the same as genuine multi-horizon
confirmation." It's a straightforward aggregation over trend_rr_profile's
existing per-window output, not new trend math.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from rates_macro.trend_rr import hac_log_regression, mean_reversion_snapshot, trend_rr_profile

SPEC_HORIZONS: tuple[int, ...] = (5, 21, 63)
MIN_FIT_WINDOW = 21  # hac_log_regression's own gate makes anything shorter statistically void
MEAN_REVERSION_WINDOW = 252


@dataclass(frozen=True)
class HorizonTrend:
    horizon_days: int
    fit_window: int
    slope_annualized: float
    r2: float
    t_hac: float
    residual_z: float  # price's current distance from the fitted trend, in residual-sigma units
    forecast_return: float  # regression-implied expected return over horizon_days
    channel_rr: float  # asymmetry of the fitted trend channel (upside vs. downside distance)


@dataclass(frozen=True)
class CommodityTrend:
    canonical_id: str
    trend_signal: float  # blended directional score in [-1, 1] (trend_rr_profile, default multi-window blend)
    opportunity: float  # 0-100 trend-opportunity score (trend_rr_profile)
    persistence: float  # fraction of 21/63/126/252 windows agreeing in sign with trend_signal; NaN if none available
    horizons: dict[int, HorizonTrend]  # keyed by SPEC_HORIZONS
    mean_reversion_z: Optional[float]  # distance from 252-day mean, in trailing-stdev units; None if <20 obs
    mean_reversion_percentile: Optional[float]


def _persistence(trend_signal: float, windows: dict[int, Optional[dict]]) -> float:
    available = [s for s in windows.values() if s is not None]
    if not available:
        return float("nan")
    target_sign = np.sign(trend_signal) if trend_signal != 0 else 0
    agreeing = sum(1 for s in available if np.sign(s["t_hac"]) == target_sign)
    return agreeing / len(available)


def build_commodity_trend(canonical_id: str, close: np.ndarray, dates: pd.DatetimeIndex) -> CommodityTrend:
    """`close` should be the roll-adjusted close (market_data.py) -- trend
    regression is return-based math and must not see artificial roll jumps."""
    series = pd.Series(close, index=dates)

    profile = trend_rr_profile(series)  # raises ValueError if no window has enough history; let it propagate
    persistence = _persistence(profile["trend_signal"], profile["windows"])

    horizons: dict[int, HorizonTrend] = {}
    for h in SPEC_HORIZONS:
        fit_window = max(h, MIN_FIT_WINDOW)
        stat = hac_log_regression(series, window=fit_window, forecast_days=h)
        if stat is None:
            continue
        horizons[h] = HorizonTrend(
            horizon_days=h,
            fit_window=fit_window,
            slope_annualized=stat["slope_annual"],
            r2=stat["r2"],
            t_hac=stat["t_hac"],
            residual_z=stat["residual_z"],
            forecast_return=stat["forecast_return"],
            channel_rr=stat["channel_rr"],
        )

    mr = mean_reversion_snapshot(series, window=MEAN_REVERSION_WINDOW)

    return CommodityTrend(
        canonical_id=canonical_id,
        trend_signal=profile["trend_signal"],
        opportunity=profile["opportunity"],
        persistence=persistence,
        horizons=horizons,
        mean_reversion_z=mr["z_score"] if mr else None,
        mean_reversion_percentile=mr["percentile"] if mr else None,
    )
