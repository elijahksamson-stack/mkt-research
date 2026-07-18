"""
Cross-index macro gauge — amalgamates per-ticker risk:reward + trend health
into a single 0-100 market bullishness read, a cash-on-sidelines allocation
gauge, and a per-index breakdown with an auto-generated one-line rationale.

Combines three signals per ticker, each capturing something the others
miss:
  - trend_signal (rates_macro.trend_rr, HAC log-regression): the ticker's
    own directional trend, reused rather than duplicated (see
    Macro/Rates/rates_macro/trend_rr.py).
  - rr_ratio + target_source (risk_reward.py): how much structural reward
    is on the table right now, and how solidly anchored that reward is.
  - trend_violation (trend_violation.py): whether the ticker's own rising
    support trendline has just been undercut -- a signal the trend_signal
    regression and the R:R snapshot can each individually miss on their
    own (see trend_violation.py's module docstring for why).

The cash-on-sidelines gauge isn't just 100 - bull_score: when a majority of
the universe is simultaneously showing an undercut support trendline, that
breadth is itself informative (a systemic/regime-break read, not
independent noise scattered across tickers), so it adds an amplifier on top
of the inverse-of-bullishness base.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from market_structure.risk_reward import RiskRewardReport
from market_structure.universe import composite_weights, default_universe

TREND_WEIGHT = 0.55
RR_WEIGHT = 0.45

RR_QUALITY_MULTIPLIER: dict[str, float] = {
    "cluster": 1.0,
    "trendline": 0.85,
    "fib_extension": 0.70,
    "synthetic": 0.50,
}
RR_SATURATION_RATIO = 3.0  # rr_ratio at/above this maps to a full 100 rr_component pre-discount

VIOLATION_BASE_PENALTY = 15.0
VIOLATION_STREAK_PENALTY_PER_BAR = 5.0
VIOLATION_STREAK_PENALTY_CAP = 25.0
VIOLATION_BREACH_PENALTY_PER_ATR = 5.0
VIOLATION_BREACH_PENALTY_CAP = 15.0

BREADTH_UNDERCUT_THRESHOLD = 0.5
BREADTH_CASH_AMPLIFIER_MAX = 20.0

FORMULA_LEGEND = f"""\
bull_score       = clip({TREND_WEIGHT}*trend_component + {RR_WEIGHT}*rr_component - violation_penalty, 0, 100)
  trend_component  = (trend_signal + 1) * 50                    [trend_signal in -1..1, rates_macro HAC regression]
  rr_component     = min(rr_ratio, {RR_SATURATION_RATIO:.0f}) / {RR_SATURATION_RATIO:.0f} * 100 * quality_multiplier
                     quality_multiplier by target_source: {RR_QUALITY_MULTIPLIER}
  violation_penalty= 0 unless trend_violation.status == "undercut", else:
                     {VIOLATION_BASE_PENALTY:.0f} (base)
                     + min({VIOLATION_STREAK_PENALTY_PER_BAR:.0f}*bars_since_break, {VIOLATION_STREAK_PENALTY_CAP:.0f}) (streak)
                     + min({VIOLATION_BREACH_PENALTY_PER_ATR:.0f}*breach_atr, {VIOLATION_BREACH_PENALTY_CAP:.0f}) (breach)
overall_bull_score = weight-average of bull_score across the universe (universe.py composite_weights)
cash_on_sidelines  = 100 - overall_bull_score, + up to {BREADTH_CASH_AMPLIFIER_MAX:.0f} amplifier when
                     breadth_undercut_pct > {BREADTH_UNDERCUT_THRESHOLD:.0%} (a majority of the universe broken
                     at once is treated as a breadth/regime signal, not independent per-ticker noise)\
"""


@dataclass(frozen=True)
class RRComponentBreakdown:
    magnitude: float  # 0-100, rr_ratio scaled before the target_source quality discount
    quality_multiplier: float  # RR_QUALITY_MULTIPLIER[target_source]
    component: float  # magnitude * quality_multiplier -- what actually feeds bull_score


@dataclass(frozen=True)
class ViolationPenaltyBreakdown:
    base: float
    streak_penalty: float
    breach_penalty: float
    total: float


@dataclass(frozen=True)
class TickerGauge:
    ticker: str
    name: str
    weight: float
    bull_score: float
    trend_signal: float
    trend_component: float  # 0-100, (trend_signal+1)*50
    trend_contribution: float  # TREND_WEIGHT * trend_component -- what actually feeds bull_score
    rr_ratio: float
    rr: RRComponentBreakdown
    rr_contribution: float  # RR_WEIGHT * rr.component -- what actually feeds bull_score
    target_source: str
    trend_violation_status: str
    violation: ViolationPenaltyBreakdown
    blurb: str


@dataclass(frozen=True)
class MacroGauge:
    overall_bull_score: float
    cash_on_sidelines_pct: float
    breadth_undercut_pct: float
    tickers: list[TickerGauge]


def _rr_breakdown(rr_ratio: float, target_source: str) -> RRComponentBreakdown:
    magnitude = min(max(rr_ratio, 0.0), RR_SATURATION_RATIO) / RR_SATURATION_RATIO * 100.0
    quality = RR_QUALITY_MULTIPLIER.get(target_source, 0.5)
    return RRComponentBreakdown(magnitude=magnitude, quality_multiplier=quality, component=magnitude * quality)


def _violation_breakdown(
    status: str, breach_atr: float, bars_since_break: Optional[int]
) -> ViolationPenaltyBreakdown:
    if status != "undercut":
        return ViolationPenaltyBreakdown(base=0.0, streak_penalty=0.0, breach_penalty=0.0, total=0.0)
    streak = bars_since_break or 0
    streak_penalty = min(streak * VIOLATION_STREAK_PENALTY_PER_BAR, VIOLATION_STREAK_PENALTY_CAP)
    breach_penalty = min(max(breach_atr, 0.0) * VIOLATION_BREACH_PENALTY_PER_ATR, VIOLATION_BREACH_PENALTY_CAP)
    total = VIOLATION_BASE_PENALTY + streak_penalty + breach_penalty
    return ViolationPenaltyBreakdown(
        base=VIOLATION_BASE_PENALTY, streak_penalty=streak_penalty, breach_penalty=breach_penalty, total=total
    )


def _target_source_phrase(source: str, ratio: Optional[float]) -> str:
    if source == "cluster":
        return "a cluster-anchored"
    if source == "trendline":
        return "a trendline-anchored"
    if source == "fib_extension":
        return f"a {ratio:.3f}x fib-extension" if ratio is not None else "a fib-extension"
    return "an unanchored synthetic"


def _blurb(
    name: str,
    trend_signal: float,
    rr_ratio: float,
    target_source: str,
    target_fib_ratio: Optional[float],
    violation_status: str,
    breach_atr: float,
    bars_since_break: Optional[int],
) -> str:
    parts = []
    if violation_status == "undercut":
        streak = bars_since_break or 0
        parts.append(
            f"support trendline undercut {streak} bar{'s' if streak != 1 else ''} ago "
            f"({breach_atr:.1f} ATR below) -- take some risk off"
        )
    elif violation_status == "intact":
        parts.append("uptrend support holding")
    trend_word = "rising" if trend_signal > 0.15 else "falling" if trend_signal < -0.15 else "flat"
    parts.append(f"{trend_word} trend (signal {trend_signal:+.2f})")
    parts.append(f"{rr_ratio:.2f}x R:R via {_target_source_phrase(target_source, target_fib_ratio)} target")
    return f"{name}: " + "; ".join(parts) + "."


def _ticker_gauge(report: RiskRewardReport, name: str, weight: float, trend_signal: float) -> TickerGauge:
    tv = report.trend_violation
    trend_component = (trend_signal + 1.0) * 50.0
    trend_contribution = TREND_WEIGHT * trend_component
    rr = _rr_breakdown(report.stop_target.rr_ratio, report.stop_target.target_source)
    rr_contribution = RR_WEIGHT * rr.component
    violation = _violation_breakdown(tv.status, tv.breach_atr, tv.bars_since_break)
    bull_score = min(100.0, max(0.0, trend_contribution + rr_contribution - violation.total))
    blurb = _blurb(
        name,
        trend_signal,
        report.stop_target.rr_ratio,
        report.stop_target.target_source,
        report.stop_target.target_fib_ratio,
        tv.status,
        tv.breach_atr,
        tv.bars_since_break,
    )
    return TickerGauge(
        ticker=report.ticker,
        name=name,
        weight=weight,
        bull_score=bull_score,
        trend_signal=trend_signal,
        trend_component=trend_component,
        trend_contribution=trend_contribution,
        rr_ratio=report.stop_target.rr_ratio,
        rr=rr,
        rr_contribution=rr_contribution,
        target_source=report.stop_target.target_source,
        trend_violation_status=tv.status,
        violation=violation,
        blurb=blurb,
    )


def _cash_on_sidelines(overall_bull_score: float, breadth_undercut_pct: float) -> float:
    base = 100.0 - overall_bull_score
    amplifier = 0.0
    if breadth_undercut_pct > BREADTH_UNDERCUT_THRESHOLD:
        excess = (breadth_undercut_pct - BREADTH_UNDERCUT_THRESHOLD) / (1.0 - BREADTH_UNDERCUT_THRESHOLD)
        amplifier = excess * BREADTH_CASH_AMPLIFIER_MAX
    return float(min(100.0, max(0.0, base + amplifier)))


def build_gauge(
    reports: dict[str, RiskRewardReport],
    trend_signals: dict[str, float],
    universe: Optional[dict[str, str]] = None,
) -> MacroGauge:
    """Combine per-ticker risk_reward.RiskRewardReport + a trend_signal
    (from rates_macro.trend_rr.trend_rr_profile, in [-1, 1]) into the
    overall gauge. `reports`/`trend_signals` need not cover every ticker in
    `universe` -- tickers missing from either are skipped and the
    remaining weights are renormalized, so the composite reflects only
    what was actually computed rather than silently under-weighting."""
    universe = universe or default_universe()
    weights = composite_weights(universe)
    covered = {t: universe[t] for t in universe if t in reports and t in trend_signals}
    if not covered:
        raise ValueError("No tickers in `reports`/`trend_signals` overlap with `universe`")
    covered_weight_total = sum(weights[t] for t in covered)

    tickers = [
        _ticker_gauge(reports[t], name, weights[t] / covered_weight_total, trend_signals[t])
        for t, name in covered.items()
    ]
    overall_bull_score = sum(tg.bull_score * tg.weight for tg in tickers)
    breadth_undercut_pct = sum(tg.weight for tg in tickers if tg.trend_violation_status == "undercut")
    cash_on_sidelines_pct = _cash_on_sidelines(overall_bull_score, breadth_undercut_pct)

    return MacroGauge(
        overall_bull_score=overall_bull_score,
        cash_on_sidelines_pct=cash_on_sidelines_pct,
        breadth_undercut_pct=breadth_undercut_pct,
        tickers=sorted(tickers, key=lambda tg: tg.bull_score, reverse=True),
    )
