"""
market-structure report — orchestrates market_data + risk_reward +
trend_rr (reused from rates_macro) + macro_gauge into one cross-index
snapshot: per-ticker risk:reward/trend/trend-violation reads, and the
amalgamated 0-100 bullishness gauge + cash-on-sidelines read.

render_summary() is written to be self-explanatory on its own: it prints
macro_gauge.FORMULA_LEGEND once up top, then every number in the per-ticker
breakdown reconstructs directly from that formula, plus the underlying
support-cluster stack and trendline that produced the trend_violation read.
Nothing here needs a narrative gloss to interpret -- if a score looks
surprising, the breakdown line above it says exactly which term did it.
"""
from __future__ import annotations

from typing import Optional

import pandas as pd
from rates_macro.trend_rr import trend_rr_profile

from market_structure.macro_gauge import FORMULA_LEGEND, MacroGauge, TickerGauge, build_gauge
from market_structure.market_data import fetch_ohlcv
from market_structure.risk_reward import RiskRewardReport, analyze
from market_structure.universe import default_universe

MAX_SUPPORTS_SHOWN = 3


def build_report(universe: Optional[dict[str, str]] = None) -> dict:
    """Fetch + analyze every ticker in `universe` (default: the full
    broad-index + sector universe). Never lets one ticker's fetch/analysis
    failure sink the whole report -- isolates it into `dropped` instead,
    matching Rates/report.py's per-series isolation convention."""
    universe = universe or default_universe()
    reports: dict[str, RiskRewardReport] = {}
    trend_signals: dict[str, float] = {}
    dates: dict[str, pd.DatetimeIndex] = {}
    dropped: list[dict] = []

    for ticker, name in universe.items():
        try:
            ohlcv = fetch_ohlcv(ticker)
            report = analyze(ticker, ohlcv.high, ohlcv.low, ohlcv.close, ohlcv.volume)
            trend_signals[ticker] = trend_rr_profile(ohlcv.close)["trend_signal"]
        except Exception as e:  # noqa: BLE001 -- per-ticker isolation, reason recorded below
            dropped.append({"ticker": ticker, "name": name, "reason": str(e)})
            continue
        reports[ticker] = report
        dates[ticker] = ohlcv.dates

    gauge = build_gauge(reports, trend_signals, universe=universe)
    return {"universe": universe, "gauge": gauge, "reports": reports, "dates": dates, "dropped": dropped}


def _support_stack_lines(report: RiskRewardReport) -> list[str]:
    supports = sorted(
        (c for c in report.clusters if c.price < report.last_close), key=lambda c: c.price, reverse=True
    )
    if not supports:
        return [
            "  support stack: none -- stop fell back to the ATR/pct cap "
            f"({report.stop_target.stop:.2f}, no cluster below price)"
        ]
    lines = [f"  support stack below {report.last_close:.2f}:"]
    for i, c in enumerate(supports[:MAX_SUPPORTS_SHOWN]):
        pct = (report.last_close - c.price) / report.last_close * 100
        atr_dist = (report.last_close - c.price) / report.atr if report.atr > 0 else float("nan")
        gap = ""
        if i > 0:
            prev = supports[i - 1]
            gap_pct = (prev.price - c.price) / report.last_close * 100
            gap = f"  (gap from prior support: {gap_pct:.1f}%)"
        lines.append(
            f"    #{i + 1}: {c.price:.2f}  -{pct:.1f}%  -{atr_dist:.1f} ATR  strength={c.strength}{gap}"
        )
    return lines


def _trendline_detail_lines(report: RiskRewardReport, dates: Optional[pd.DatetimeIndex]) -> list[str]:
    tv = report.trend_violation
    if tv.status == "no_active_trendline" or tv.trendline is None:
        return ["  trendline: no recent ascending support line in range"]
    line = tv.trendline
    start_date = dates[line.start_idx].date() if dates is not None else f"bar {line.start_idx}"
    end_date = dates[line.end_idx].date() if dates is not None else f"bar {line.end_idx}"
    status_word = "undercut" if tv.status == "undercut" else "intact"
    breach_note = (
        f" -- price sits {tv.breach_atr:.2f} ATR below it, broken {tv.bars_since_break} bar"
        f"{'s' if tv.bars_since_break != 1 else ''} ago"
        if tv.status == "undercut"
        else f" -- price sits {-tv.breach_atr:.2f} ATR above it"
    )
    anchor_price_at_end_idx = line.start_price + line.slope * (line.end_idx - line.start_idx)
    return [
        f"  trendline ({status_word}): rising support from {start_date} (${line.start_price:.2f}) "
        f"through {end_date} (${anchor_price_at_end_idx:.2f} at anchor, slope {line.slope:+.3f}/bar), "
        f"extended to ${line.end_price:.2f} today{breach_note}"
    ]


def _ticker_block_lines(tg: TickerGauge, report: RiskRewardReport, dates: Optional[pd.DatetimeIndex]) -> list[str]:
    lines = [
        f"{tg.ticker:6} {tg.name:35} bull_score={tg.bull_score:.1f}/100",
        f"  trend_component={tg.trend_component:.1f} (trend_signal={tg.trend_signal:+.2f}) "
        f"-> contributes {tg.trend_contribution:.1f}",
        f"  rr_component={tg.rr.component:.1f} (rr_ratio={tg.rr_ratio:.2f}x, source={tg.target_source}, "
        f"magnitude={tg.rr.magnitude:.1f}, quality={tg.rr.quality_multiplier:.2f}) "
        f"-> contributes {tg.rr_contribution:.1f}",
        f"  violation_penalty={tg.violation.total:.1f} = base {tg.violation.base:.1f} "
        f"+ streak {tg.violation.streak_penalty:.1f} + breach {tg.violation.breach_penalty:.1f}",
    ]
    lines += _support_stack_lines(report)
    lines += _trendline_detail_lines(report, dates)
    lines.append(f"  summary: {tg.blurb}")
    return lines


def render_summary(result: dict) -> str:
    gauge: MacroGauge = result["gauge"]
    lines = [
        f"Macro/market-structure snapshot — {len(gauge.tickers)}/{len(result['universe'])} tickers analyzed",
        "",
        FORMULA_LEGEND,
        "",
        f"OVERALL BULLISHNESS: {gauge.overall_bull_score:.1f}/100",
        f"CASH ON SIDELINES:   {gauge.cash_on_sidelines_pct:.1f}%",
        f"BREADTH UNDERCUT:    {gauge.breadth_undercut_pct:.0%} of universe (weighted)",
    ]
    for tg in gauge.tickers:
        report = result["reports"][tg.ticker]
        dates = result["dates"].get(tg.ticker)
        lines.append("")
        lines.append("-" * 80)
        lines += _ticker_block_lines(tg, report, dates)
    if result["dropped"]:
        lines.append("")
        lines.append("Dropped tickers:")
        for d in result["dropped"]:
            lines.append(f"  {d['ticker']} ({d['name']}): {d['reason']}")
    return "\n".join(lines)


def main() -> None:
    result = build_report()
    print(render_summary(result))


if __name__ == "__main__":
    main()
