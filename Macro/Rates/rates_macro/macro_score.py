"""
Composite macro score: blends each FRED series' current trend direction with
its *measured* relationship to the S&P into one 0-100 bullish/bearish read
for equities (50 = neutral), with full per-series and per-category
attribution.

Deliberately data-driven rather than built on hardcoded market lore ("rising
rates are bearish"): a series only moves the score if it currently HAS a
measured relationship to equities. signed_alignment = trend_signal *
correlation — a series trending in the direction that, historically over the
lookback, has coincided with equities moving the SAME way scores positive; a
series trending in the direction that has coincided with equities moving the
OPPOSITE way scores negative. A series with near-zero measured correlation
right now contributes near-zero, whatever a textbook prior would say about
it — see build_report's `vs_benchmark.contemporaneous.correlation` for the
number driving each series' sign and magnitude here.
"""
from __future__ import annotations

from typing import Optional

from rates_macro.fred_client import CREDIT_SERIES, FX_SERIES, RATES_SERIES

DEFAULT_CATEGORY_WEIGHTS = {"rates": 1 / 3, "credit": 1 / 3, "fx": 1 / 3}


def _category_of(series_id: str) -> str:
    if series_id in RATES_SERIES:
        return "rates"
    if series_id in CREDIT_SERIES:
        return "credit"
    if series_id in FX_SERIES:
        return "fx"
    return "other"


def series_signal(series_report: dict) -> Optional[dict]:
    """Signed equity-alignment for one series' build_series_report() output.

    Returns None (excluded from the score) if the series is stale, or if
    either its trend_rr or vs_benchmark.contemporaneous sub-computation
    degraded to an `error` dict.
    """
    if series_report.get("stale"):
        return None
    trend = series_report.get("trend_rr") or {}
    xref = (series_report.get("vs_benchmark") or {}).get("contemporaneous") or {}
    if "error" in trend or "error" in xref:
        return None
    trend_signal = trend.get("trend_signal")
    correlation = xref.get("correlation")
    if trend_signal is None or correlation is None:
        return None
    return {
        "trend_signal": trend_signal,
        "correlation": correlation,
        "signed_alignment": trend_signal * correlation,
    }


def _label_for(score: float) -> str:
    if score >= 65:
        return "bullish"
    if score >= 55:
        return "mildly bullish"
    if score >= 45:
        return "neutral"
    if score >= 35:
        return "mildly bearish"
    return "bearish"


def macro_score(report: dict, category_weights: Optional[dict] = None) -> dict:
    """0-100 macro score (50 = neutral) built from build_report()'s output.

    Series are grouped into categories (rates/credit/fx, from fred_client's
    catalog) and averaged within each category before weighting, so a
    category with more series in the default catalog (rates currently has
    three) doesn't dominate the score just by having more entries. Missing
    categories renormalize over the surviving weight rather than silently
    pulling the score toward neutral.
    """
    weights = category_weights or DEFAULT_CATEGORY_WEIGHTS

    by_category: dict[str, list] = {}
    excluded: list[dict] = []
    for series_id, series_report in report["series"].items():
        signal = series_signal(series_report)
        if signal is None:
            reason = (
                "stale"
                if series_report.get("stale")
                else "no measured trend/benchmark relationship available"
            )
            excluded.append(
                {"series_id": series_id, "label": series_report["label"], "reason": reason}
            )
            continue
        category = _category_of(series_id)
        by_category.setdefault(category, []).append(
            {"series_id": series_id, "label": series_report["label"], **signal}
        )

    categories: dict[str, dict] = {}
    total_weighted = 0.0
    total_weight_used = 0.0
    for category, members in by_category.items():
        weight = weights.get(category, 0.0)
        avg_alignment = sum(m["signed_alignment"] for m in members) / len(members)
        contribution_points = weight * avg_alignment * 50
        categories[category] = {
            "avg_alignment": avg_alignment,
            "weight": weight,
            "contribution_points": contribution_points,
            "members": members,
        }
        total_weighted += contribution_points
        total_weight_used += weight

    score = 50.0 + (total_weighted / total_weight_used if total_weight_used > 0 else 0.0)
    score = max(0.0, min(100.0, score))

    return {
        "score": round(score, 1),
        "label": _label_for(score),
        "categories": categories,
        "excluded": excluded,
        "benchmark": report["benchmark"],
        "benchmark_as_of": report["benchmark_as_of"],
    }


def render_macro_score(result: dict) -> str:
    """Plain-text score + per-category, per-series attribution."""
    lines = [
        f"Macro score vs {result['benchmark']} (data through {result['benchmark_as_of']}): "
        f"{result['score']}/100 — {result['label']}",
        "",
    ]
    for category, data in sorted(
        result["categories"].items(), key=lambda kv: -abs(kv[1]["contribution_points"])
    ):
        sign = "+" if data["contribution_points"] >= 0 else ""
        lines.append(
            f"  {category:8} {sign}{data['contribution_points']:.2f} pts "
            f"(weight {data['weight']:.2f}, avg alignment {data['avg_alignment']:+.3f})"
        )
        for m in data["members"]:
            lines.append(
                f"      {m['label']:40} trend {m['trend_signal']:+.2f} "
                f"× corr {m['correlation']:+.2f} = {m['signed_alignment']:+.3f}"
            )
    if result["excluded"]:
        lines.append("")
        lines.append("Excluded from score:")
        for e in result["excluded"]:
            lines.append(f"  {e['label']}: {e['reason']}")
    return "\n".join(lines)
