"""
Macro/Rates report — orchestrates fred_client + market_data + trend_rr +
cross_reference into a single snapshot of where HY credit, the Treasury
curve, and the USD sit relative to their own trend and mean-reversion, and
how each one currently relates to the S&P.
"""
from __future__ import annotations

from typing import Optional

import pandas as pd

from rates_macro.cross_reference import cross_reference_report
from rates_macro.fred_client import ALL_SERIES, fetch_series
from rates_macro.macro_score import macro_score, render_macro_score
from rates_macro.market_data import fetch_close
from rates_macro.red_zone import build_red_zone, render_red_zone
from rates_macro.regime import regime, render_regime
from rates_macro.trend_rr import mean_reversion_snapshot, trend_rr_profile

BENCHMARK = "SPY"

# A FRED series whose latest print trails the equity benchmark by more than
# this is flagged `stale` rather than silently cross-referenced with the
# same confidence as a fresh print (mirrors market_data.MAX_STALENESS_DAYS).
MAX_STALENESS_DAYS = 10

# Level series (yields, spreads, the USD index) are conventionally read in
# level/bps terms -> diff; the equity benchmark is a price -> log_return.
FRED_CHANGE_METHOD = "diff"
EQUITY_CHANGE_METHOD = "log_return"


def build_series_report(label: str, series: pd.Series, benchmark_close: pd.Series) -> dict:
    """Trend/RR + mean-reversion for one FRED series, cross-referenced
    against the equity benchmark.

    Never raises on a single series' math failure (e.g. too little history
    for any regression window, or a data quirk like a duplicate timestamp
    tripping cross_reference's alignment) — every sub-computation degrades
    to an `error` key so one bad series doesn't sink the whole report.
    """
    result: dict = {"label": label}
    try:
        result["trend_rr"] = trend_rr_profile(series)
    except ValueError as e:
        result["trend_rr"] = {"error": str(e)}
    try:
        result["mean_reversion"] = mean_reversion_snapshot(series)
    except Exception as e:  # noqa: BLE001 — per-series isolation
        result["mean_reversion"] = {"error": str(e)}
    try:
        result["vs_benchmark"] = cross_reference_report(
            series,
            benchmark_close,
            name_a=label,
            name_b=BENCHMARK,
            method_a=FRED_CHANGE_METHOD,
            method_b=EQUITY_CHANGE_METHOD,
        )
    except Exception as e:  # noqa: BLE001 — per-series isolation
        result["vs_benchmark"] = {"error": str(e)}
    clean = series.dropna()
    result["latest"] = float(clean.iloc[-1]) if not clean.empty else None
    result["as_of"] = str(clean.index[-1].date()) if not clean.empty else None

    benchmark_clean = benchmark_close.dropna()
    if not clean.empty and not benchmark_clean.empty:
        staleness_days = (benchmark_clean.index[-1] - clean.index[-1]).days
    else:
        staleness_days = None
    result["staleness_days"] = staleness_days
    result["stale"] = staleness_days is not None and staleness_days > MAX_STALENESS_DAYS
    return result


def build_report(series_ids: Optional[dict] = None, benchmark: str = BENCHMARK) -> dict:
    """Pull every configured FRED series plus the equity benchmark and
    produce the full macro/rates report.

    Raises whatever fetch_close raises if the benchmark itself can't be
    fetched — every cross-reference downstream needs it. Individual FRED
    series failures are isolated into `dropped` instead of aborting the run.
    """
    series_ids = series_ids or ALL_SERIES
    benchmark_close = fetch_close(benchmark)

    series_reports: dict[str, dict] = {}
    dropped: list[dict] = []
    for series_id, label in series_ids.items():
        try:
            raw = fetch_series(series_id)
        except Exception as e:  # noqa: BLE001 — per-series isolation, reason recorded below
            dropped.append({"series_id": series_id, "label": label, "reason": str(e)})
            continue
        if raw.empty:
            dropped.append(
                {"series_id": series_id, "label": label, "reason": "no observations"}
            )
            continue
        try:
            series_reports[series_id] = build_series_report(label, raw, benchmark_close)
        except Exception as e:  # noqa: BLE001 — belt-and-suspenders isolation
            dropped.append({"series_id": series_id, "label": label, "reason": str(e)})

    return {
        "benchmark": benchmark,
        "benchmark_as_of": str(benchmark_close.index[-1].date()),
        "series": series_reports,
        "dropped": dropped,
    }


def _fmt(x, digits=2):
    return f"{x:.{digits}f}" if isinstance(x, (int, float)) else "n/a"


def render_summary(report: dict) -> str:
    """Plain-text summary table: one row per series — latest level, trend
    signal, opportunity score, mean-reversion Z, and correlation/beta/lead-lag
    vs. the benchmark."""
    lines = [
        f"Macro/Rates snapshot vs {report['benchmark']} "
        f"(data through {report['benchmark_as_of']})",
        "",
        f"{'Series':40} {'Latest':>9} {'Trend':>7} {'Opp':>6} "
        f"{'Z(mean)':>8} {'Corr':>7} {'Beta':>8} {'LeadLag':>8}",
    ]
    for r in report["series"].values():
        trend = r["trend_rr"]
        mr = r["mean_reversion"] or {}
        vs_benchmark = r["vs_benchmark"]
        xref = vs_benchmark.get("contemporaneous", {})
        lag = vs_benchmark.get("lead_lag", {})
        trend_signal = trend.get("trend_signal")
        opportunity = trend.get("opportunity")
        z = mr.get("z_score")
        corr = xref.get("correlation")
        beta = xref.get("beta")
        best_lag = lag.get("best_lag")
        lines.append(
            f"{r['label']:40} {_fmt(r['latest']):>9} "
            f"{_fmt(trend_signal):>7} {_fmt(opportunity, 1):>6} "
            f"{_fmt(z):>8} {_fmt(corr):>7} {_fmt(beta, 3):>8} "
            f"{best_lag if best_lag is not None else 'n/a':>8}"
        )
    if report["dropped"]:
        lines.append("")
        lines.append("Dropped series:")
        for d in report["dropped"]:
            lines.append(f"  {d['series_id']} ({d['label']}): {d['reason']}")
    return "\n".join(lines)


def main() -> None:
    report = build_report()
    print(render_summary(report))

    positioning = macro_score(report)
    print()
    print(render_macro_score(positioning))

    vulnerability = build_red_zone(fetch=fetch_series)
    print()
    print(render_red_zone(vulnerability))

    print()
    print(render_regime(regime(positioning["score"], vulnerability["score"])))


if __name__ == "__main__":
    main()
