"""
Trade-geometry adapter around `market_structure.risk_reward` (the existing
Risk/Reward engine: recency-weighted pivots, six-method convergence
clustering, dual trendline families, ATR/HV/rvol-adjusted stop/target
tiering, trend-violation detection). Reused unchanged and in full --
`analyze()` is called exactly as market-structure's own report.py calls
it. Nothing here is a forecast; per the spec, this is trade geometry only
(entry/stop/target/R:R), consumed as one input among several into
`ranking.py`'s statistical model, never as a standalone probability.
"""
from __future__ import annotations

from dataclasses import dataclass

from market_structure.market_data import OHLCV
from market_structure.risk_reward import RiskRewardReport, analyze

MIN_ACTIONABLE_RR = 1.25  # below this, the structure isn't worth trading regardless of forecast


@dataclass(frozen=True)
class CommodityRiskReward:
    canonical_id: str
    report: RiskRewardReport  # full reused report, exposed as-is for report.py's detail view
    entry: float
    stop: float
    target: float
    rr_ratio: float
    target_source: str
    trend_violation_status: str
    actionable: bool  # rr_ratio meets a minimum bar at the current price -- see is_actionable()


def is_actionable(rr_ratio: float) -> bool:
    return rr_ratio >= MIN_ACTIONABLE_RR


def build_commodity_risk_reward(canonical_id: str, ohlcv: OHLCV) -> CommodityRiskReward:
    """Raises InsufficientDataError (from market_structure.indicators) below
    60 bars, propagated unchanged -- callers should catch it the same way
    market-structure's own report.py isolates per-ticker failures."""
    report = analyze(canonical_id, ohlcv.high, ohlcv.low, ohlcv.close, ohlcv.volume)
    st = report.stop_target
    return CommodityRiskReward(
        canonical_id=canonical_id,
        report=report,
        entry=report.last_close,
        stop=st.stop,
        target=st.target,
        rr_ratio=st.rr_ratio,
        target_source=st.target_source,
        trend_violation_status=report.trend_violation.status,
        actionable=is_actionable(st.rr_ratio),
    )
