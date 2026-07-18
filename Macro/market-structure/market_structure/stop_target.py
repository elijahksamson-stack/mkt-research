"""
Stop/target computation — rr.txt Part 8.

Four-tier target fallback (cluster -> trendline -> fib_extension ->
synthetic) with a `target_source` attribution tag telling the consumer how
anchored the reward is. Before this tiering existed, an ATH ticker with no
resistance overhead silently produced a synthetic 2.00x indistinguishable
from a genuinely cluster-anchored 2.00x -- the tiers make that distinction
visible. Pure math, no I/O.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Sequence

from market_structure.fib_extension import FibExtension
from market_structure.levels import ConvergenceCluster
from market_structure.trendlines import RegressionTrendline, TrendlineSegment

STOP_ATR_MULT = 0.5
TARGET_ATR_MULT = 0.5
RR_TARGET = 2.0
MIN_TARGET_ATR = 1.25
MAX_STOP_ATR = 3.0
MAX_STOP_PCT = 0.08
VOL_FACTOR_CLIP = (0.75, 2.25)

TargetSource = Literal["cluster", "trendline", "fib_extension", "synthetic"]


@dataclass(frozen=True)
class StopTarget:
    stop: float
    target: float
    risk: float
    reward: float
    risk_pct: float
    reward_pct: float
    rr_ratio: float
    stop_cluster: Optional[float]
    target_cluster: Optional[float]
    vol_factor: float
    target_source: TargetSource
    target_fib_ratio: Optional[float]


def _vol_factor(hv: float) -> float:
    lo, hi = VOL_FACTOR_CLIP
    return float(min(max(hv / 0.02, lo), hi))


def _split_clusters(
    clusters: Sequence[ConvergenceCluster], last_close: float
) -> tuple[list[ConvergenceCluster], list[ConvergenceCluster]]:
    supports = sorted((c for c in clusters if c.price < last_close), key=lambda c: c.price, reverse=True)
    resistances = sorted((c for c in clusters if c.price >= last_close), key=lambda c: c.price)
    return supports, resistances


def _compute_stop(
    supports: Sequence[ConvergenceCluster], last_close: float, atr: float, vol_factor: float
) -> tuple[float, Optional[float]]:
    if supports:
        stop_cluster = supports[0].price
        raw_stop = stop_cluster - atr * STOP_ATR_MULT * vol_factor
    else:
        stop_cluster = None
        raw_stop = last_close * (1 - MAX_STOP_PCT)
    max_stop = last_close - atr * MAX_STOP_ATR
    pct_stop = last_close * (1 - MAX_STOP_PCT)
    # The tightest (highest) of the three candidates wins -- the stop can
    # never sit further than MAX_STOP_ATR/MAX_STOP_PCT below price.
    return max(raw_stop, max_stop, pct_stop), stop_cluster


def _upper_trendline_endpoints(
    regression_trendlines: Sequence[RegressionTrendline],
    pivot_pair_lines: Sequence[TrendlineSegment],
    last_close: float,
) -> list[float]:
    endpoints = [t.end_price for t in regression_trendlines if t.type == "upper" and t.end_price > last_close]
    endpoints += [t.end_price for t in pivot_pair_lines if t.type == "upper" and t.end_price > last_close]
    return endpoints


def _compute_target(
    resistances: Sequence[ConvergenceCluster],
    regression_trendlines: Sequence[RegressionTrendline],
    pivot_pair_lines: Sequence[TrendlineSegment],
    fib_extension: Optional[FibExtension],
    last_close: float,
    atr: float,
    vol_factor: float,
    stop: float,
) -> tuple[float, Optional[float], TargetSource, Optional[float]]:
    if resistances:
        target_cluster = resistances[0].price
        raw_target = target_cluster + atr * TARGET_ATR_MULT * vol_factor
        return raw_target, target_cluster, "cluster", None

    endpoints = _upper_trendline_endpoints(regression_trendlines, pivot_pair_lines, last_close)
    if endpoints:
        raw_target = min(endpoints) + atr * TARGET_ATR_MULT * vol_factor
        return raw_target, None, "trendline", None

    if fib_extension is not None:
        above = [lv for lv in fib_extension.levels if lv.price > last_close]
        if above:
            nearest = min(above, key=lambda lv: lv.price)
            # Tier 3 intentionally does NOT add an ATR pad -- the projected
            # level IS the target (the floor below may still bump it up).
            return nearest.price, None, "fib_extension", nearest.ratio

    risk_for_synth = last_close - stop
    raw_target = last_close + risk_for_synth * RR_TARGET
    return raw_target, None, "synthetic", None


def compute_stop_target(
    clusters: Sequence[ConvergenceCluster],
    regression_trendlines: Sequence[RegressionTrendline],
    pivot_pair_lines: Sequence[TrendlineSegment],
    fib_extension: Optional[FibExtension],
    last_close: float,
    atr: float,
    hv: float,
) -> StopTarget:
    vol_factor = _vol_factor(hv)
    supports, resistances = _split_clusters(clusters, last_close)
    stop, stop_cluster = _compute_stop(supports, last_close, atr, vol_factor)
    raw_target, target_cluster, target_source, target_fib_ratio = _compute_target(
        resistances, regression_trendlines, pivot_pair_lines, fib_extension, last_close, atr, vol_factor, stop
    )
    min_target = last_close + atr * MIN_TARGET_ATR
    target = max(raw_target, min_target)

    risk = last_close - stop
    reward = target - last_close
    rr_ratio = reward / risk if risk > 0 else 0.0

    return StopTarget(
        stop=stop,
        target=target,
        risk=risk,
        reward=reward,
        risk_pct=risk / last_close * 100 if last_close else 0.0,
        reward_pct=reward / last_close * 100 if last_close else 0.0,
        rr_ratio=rr_ratio,
        stop_cluster=stop_cluster,
        target_cluster=target_cluster,
        vol_factor=vol_factor,
        target_source=target_source,
        target_fib_ratio=target_fib_ratio,
    )
