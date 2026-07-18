"""
Commodities report — top-level orchestration + CLI entry point, mirroring
market_structure/report.py's shape: build_report() fetches + assembles
everything, render_table()/render_detail() turn it into the spec's
Section 7 product surface as plain text (no web UI in this package --
see the top-level CLAUDE.md for why).

`render_table` is the "fast ranking surface, not a statistical dashboard"
the spec asks for: one line per commodity, the exact column set Section 7
names. `render_detail` is the "select a commodity" panel: forecast
distribution across all three horizons, curve/carry, relative-performance
reads, and the direction model's top feature contributions -- never a
bare "BUY" label, per the spec's explicit instruction to translate the
score into what's driving it, what contradicts it, and whether the trade
geometry is actionable at the current price.
"""
from __future__ import annotations

import argparse
from typing import Optional

from commodities.features import FeatureBundle, UniverseData, fetch_universe_data
from commodities.models import top_feature_contributions
from commodities.ranking import PRIMARY_HORIZON, SPEC_HORIZONS, CommodityRanking, RankingRun, build_rankings
from commodities.universe import CommodityInstrument, default_universe

HORIZON_LABELS = {5: "1W", 21: "1M", 63: "3M"}
TOP_DETAIL_COUNT = 5


def build_report(universe: Optional[dict[str, CommodityInstrument]] = None, period: str = "3y") -> dict:
    """Never lets one commodity's fetch failure sink the whole run --
    `dropped` records what was skipped and why, matching
    market_structure.report's per-ticker isolation convention."""
    universe = universe or default_universe()
    data: UniverseData = fetch_universe_data(universe, period=period)
    dropped = [cid for cid in universe if cid not in data.commodity_series]
    run: RankingRun = build_rankings(data)
    return {"universe": universe, "data": data, "run": run, "dropped": dropped}


def _fmt_pct(x: Optional[float], digits: int = 1) -> str:
    return f"{x:+.{digits}%}" if x is not None and x == x else "n/a"


def _fmt_score(x: Optional[float], digits: int = 0) -> str:
    return f"{x:.{digits}f}" if x is not None and x == x else "n/a"


def render_table(run: RankingRun, horizon: int = PRIMARY_HORIZON) -> str:
    label = HORIZON_LABELS.get(horizon, f"{horizon}d")
    lines = [
        f"Commodities ranking — horizon {label} ({horizon} trading days), {len(run.rankings)} commodities",
        "",
        f"{'Rank':>4} {'Commodity':22} {'Family':18} {'P(Up)':>7} {'ExpRet':>8} "
        f"{'RelStr':>7} {'Trend':>6} {'Curve':>13} {'R:R':>6} {'Conf':>6} {'Score':>6}",
    ]
    for i, r in enumerate(run.rankings, start=1):
        bundle = run.bundles[r.canonical_id]
        curve_state = bundle.curve.curve_state if bundle.curve else "n/a"
        lines.append(
            f"{i:>4} {r.canonical_id:22} {r.family:18} "
            f"{_fmt_pct(r.up_probability.get(horizon)):>7} {_fmt_pct(r.expected_return.get(horizon)):>8} "
            f"{_fmt_score(r.relative_strength_score):>7} {_fmt_score(r.trend_score):>6} {curve_state:>13} "
            f"{_fmt_score(r.risk_reward, 2):>6} {_fmt_score(r.forecast_confidence * 100):>6} "
            f"{_fmt_score(r.commodity_opportunity_score):>6}"
        )
    return "\n".join(lines)


def _forecast_distribution_lines(r: CommodityRanking) -> list[str]:
    lines = ["  forecast distribution:"]
    for h in SPEC_HORIZONS:
        label = HORIZON_LABELS.get(h, f"{h}d")
        lines.append(
            f"    {label:4} P(up)={_fmt_pct(r.up_probability.get(h))}  "
            f"E[return]={_fmt_pct(r.expected_return.get(h))}  "
            f"P10 downside={_fmt_pct(r.downside_quantile.get(h))}"
        )
    return lines


def _curve_lines(bundle: FeatureBundle) -> list[str]:
    if bundle.curve is None:
        return ["  curve/carry: unavailable (no listed futures, or dated-contract data not currently served)"]
    c = bundle.curve
    lines = [
        f"  curve: {c.curve_state} — front/second annualized {c.front_second_annualized:+.2%}, "
        f"roll yield {c.roll_yield_annualized:+.2%}/yr"
    ]
    if c.front_third_annualized is not None:
        lines.append(f"    front/third annualized {c.front_third_annualized:+.2%}, curvature {c.curvature:+.4f}")
    if c.front_second_annualized_change is not None:
        lines.append(f"    curve-shape change over ~21d: {c.front_second_annualized_change:+.2%}/yr")
    return lines


def _relative_performance_lines(bundle: FeatureBundle) -> list[str]:
    lines = ["  relative performance (percentile, universe / family):"]
    for h in SPEC_HORIZONS:
        snap = bundle.momentum.get(h)
        if snap is None:
            continue
        universe_pct = f"{snap.cross_sectional.percentile:.0f}" if snap.cross_sectional else "n/a"
        family_pct = f"{snap.family_relative.percentile:.0f}" if snap.family_relative else "n/a"
        label = HORIZON_LABELS.get(h, f"{h}d")
        lines.append(f"    {label:4} universe={universe_pct:>4}pct  family={family_pct:>4}pct  residual={snap.residual_momentum:+.4f}")
    return lines


def _feature_contribution_lines(run: RankingRun, horizon: int) -> list[str]:
    model_set = run.model_sets.get(horizon)
    if model_set is None:
        return ["  feature contributions: model unavailable for this horizon (insufficient training history)"]
    positive, negative = top_feature_contributions(model_set, n=4)
    lines = ["  top direction-model contributions (standardized coefficients):"]
    lines.append("    positive: " + ", ".join(f"{name} ({coef:+.2f})" for name, coef in positive) if positive else "    positive: none")
    lines.append("    negative: " + ", ".join(f"{name} ({coef:+.2f})" for name, coef in negative) if negative else "    negative: none")
    return lines


def render_detail(run: RankingRun, canonical_id: str, horizon: int = PRIMARY_HORIZON) -> str:
    r = next((x for x in run.rankings if x.canonical_id == canonical_id), None)
    if r is None:
        return f"{canonical_id}: not found in this run's rankings"
    bundle = run.bundles[canonical_id]

    lines = [f"=== {canonical_id} ({r.family}) — opportunity score {r.commodity_opportunity_score:.1f}/100 ==="]
    lines += _forecast_distribution_lines(r)
    lines.append(
        f"  relative_return_rank (universe percentile, {HORIZON_LABELS[PRIMARY_HORIZON]} expected return): "
        f"{_fmt_score(r.relative_return_rank)}"
    )
    lines += _curve_lines(bundle)
    lines += _relative_performance_lines(bundle)

    if bundle.risk_reward is not None:
        rr = bundle.risk_reward
        lines.append(
            f"  risk/reward: entry {rr.entry:.4g}, stop {rr.stop:.4g}, target {rr.target:.4g}, "
            f"R:R {rr.rr_ratio:.2f}x (source={rr.target_source}), trend_violation={rr.trend_violation_status}, "
            f"actionable={rr.actionable}"
        )
    else:
        lines.append("  risk/reward: unavailable (insufficient bar history for the reused engine)")

    if bundle.trend is not None:
        persistence_str = f"{bundle.trend.persistence:.0%}" if bundle.trend.persistence == bundle.trend.persistence else "n/a"
        lines.append(
            f"  trend: signal={bundle.trend.trend_signal:+.2f}, opportunity={bundle.trend.opportunity:.1f}, "
            f"persistence={persistence_str}"
        )

    if bundle.positioning is not None:
        p = bundle.positioning
        lines.append(
            f"  CFTC positioning (as of {p.report_date.date()}): managed-money net z={p.managed_money_net_zscore:+.2f} "
            f"({p.managed_money_net_percentile:.0f}pct), producer/merchant net z={p.producer_merchant_net_zscore:+.2f} "
            f"({p.producer_merchant_net_percentile:.0f}pct)"
        )

    lines += _feature_contribution_lines(run, horizon)
    lines.append(f"  data as_of: {bundle.as_of.date()}")
    return "\n".join(lines)


def render_pairs(run: RankingRun) -> str:
    if not run.pairs:
        return ""
    lines = ["", "Pair-ratio trends:"]
    for p in run.pairs:
        lines.append(f"  {p.numerator_id}/{p.denominator_id}: ratio={p.ratio_last:.4g}, trend_signal={p.trend_signal:+.2f}, opportunity={p.opportunity:.1f}")
    return "\n".join(lines)


def render_summary(result: dict, horizon: int = PRIMARY_HORIZON, detail_count: int = TOP_DETAIL_COUNT) -> str:
    run: RankingRun = result["run"]
    parts = [render_table(run, horizon), render_pairs(run)]
    if detail_count > 0:
        parts.append("")
        parts.append(f"Detail — top {min(detail_count, len(run.rankings))} by opportunity score:")
        for r in run.rankings[:detail_count]:
            parts.append("")
            parts.append(render_detail(run, r.canonical_id, horizon))
    if result["dropped"]:
        parts.append("")
        parts.append("Dropped (fetch/quality-gate failure): " + ", ".join(result["dropped"]))
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Macro/Commodities statistical ranking")
    parser.add_argument("--horizon", choices=["1W", "1M", "3M"], default="1M", help="Ranking horizon (default: 1M / 21 trading days)")
    parser.add_argument("--detail", type=int, default=TOP_DETAIL_COUNT, help="Number of top commodities to show detail for")
    args = parser.parse_args()
    horizon = {v: k for k, v in HORIZON_LABELS.items()}[args.horizon]

    result = build_report()
    print(render_summary(result, horizon=horizon, detail_count=args.detail))


if __name__ == "__main__":
    main()
