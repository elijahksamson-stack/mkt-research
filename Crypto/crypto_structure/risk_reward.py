"""
Per-asset risk:reward analysis — orchestrates indicators, pivots, the six
level-detection methods, both trendline families, fib extensions, and the
stop/target tiering into one report, per rr.txt Part 12's end-to-end
pipeline order -- plus the trend-violation refinement (trend_violation.py).
Pure math, no I/O: caller supplies OHLCV arrays already fetched and
quality-gated (see market_data.py). Verbatim port of Macro/market-structure's
risk_reward.py -- this is the module that answers "RR on all crypto
assets": call `analyze()` once per asset in the universe.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from crypto_structure.fib_extension import FibExtension, build_fib_extension
from crypto_structure.indicators import (
    average_true_range,
    build_pivots,
    realized_volatility,
    relative_volume,
    require_min_bars,
)
from crypto_structure.levels import (
    ConvergenceCluster,
    build_anchored_vwap,
    build_channels,
    build_convergence_clusters,
    build_fibonacci_levels,
    build_round_levels,
    build_volume_profile,
    collect_all_levels,
)
from crypto_structure.stop_target import StopTarget, compute_stop_target
from crypto_structure.trend_violation import TrendViolation, detect_trend_violation
from crypto_structure.trendlines import (
    RegressionTrendline,
    TrendlineSegment,
    build_pivot_pair_trendlines,
    build_regression_trendlines,
    regression_trendlines_as_levels,
)


@dataclass(frozen=True)
class RiskRewardReport:
    ticker: str
    last_close: float
    atr: float
    hv: float
    rvol: float
    clusters: list[ConvergenceCluster]
    regression_trendlines: list[RegressionTrendline]
    pivot_pair_lines: list[TrendlineSegment]
    fib_extension: Optional[FibExtension]
    stop_target: StopTarget
    trend_violation: TrendViolation


def analyze(
    ticker: str,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray,
) -> RiskRewardReport:
    """Run the full pipeline (rr.txt Part 12, steps 1-9) for one asset.
    Raises InsufficientDataError below 60 bars (Part 2's minimum data
    gate)."""
    n = len(close)
    require_min_bars(n)

    last_close = float(close[-1])
    atr = average_true_range(high, low, close)
    hv = realized_volatility(close)
    rvol = relative_volume(volume)

    pivots = build_pivots(high, low)

    channels = build_channels(pivots, last_close, atr)
    regression_trendlines = build_regression_trendlines(pivots, n, atr)
    fib_levels = build_fibonacci_levels(high, low)
    avwap_levels = build_anchored_vwap(pivots, high, low, close, volume)
    vp_levels = build_volume_profile(close, volume, last_close, atr)
    round_levels = build_round_levels(last_close, atr)

    pool = collect_all_levels(
        channels,
        regression_trendlines_as_levels(regression_trendlines),
        fib_levels,
        avwap_levels,
        vp_levels,
        round_levels,
    )
    clusters = build_convergence_clusters(pool, last_close, atr)

    pivot_pair_lines = build_pivot_pair_trendlines(high, low, atr)
    fib_ext = build_fib_extension(pivots, n, last_close)

    stop_target = compute_stop_target(
        clusters, regression_trendlines, pivot_pair_lines, fib_ext, last_close, atr, hv
    )
    # Deliberately NOT passing pivot_pair_lines here -- that list is capped
    # for the tier-2-target/chart use case above and can crowd out the
    # recent line this detector specifically needs. See trend_violation.py's
    # CANDIDATE_POOL_SIZE comment.
    trend_violation = detect_trend_violation(high, low, close, atr)

    return RiskRewardReport(
        ticker=ticker,
        last_close=last_close,
        atr=atr,
        hv=hv,
        rvol=rvol,
        clusters=clusters,
        regression_trendlines=regression_trendlines,
        pivot_pair_lines=pivot_pair_lines,
        fib_extension=fib_ext,
        stop_target=stop_target,
        trend_violation=trend_violation,
    )
