"""
crypto-structure report — orchestrates market_data + risk_reward + trend_rr
+ relative_strength + crypto_gauge into one cross-asset snapshot: per-asset
risk:reward/trend/trend-violation reads, the peer/benchmark leadership +
opportunity ranking table (the "relative trend indications" deliverable),
and the amalgamated 0-100 risk-appetite gauge + risk-off read.

render_summary() is written to be self-explanatory on its own: it prints
crypto_gauge.FORMULA_LEGEND once up top, then the leadership/opportunity
ranking table, then every number in the per-asset breakdown reconstructs
directly from that formula, plus the underlying support-cluster stack and
trendline that produced the trend_violation read. Nothing here needs a
narrative gloss to interpret -- if a score looks surprising, the breakdown
line above it says exactly which term did it. Mirrors
Macro/market-structure/report.py's structure.
"""
from __future__ import annotations

from typing import Optional

import pandas as pd

from crypto_structure.crypto_gauge import FORMULA_LEGEND, AssetGauge, CryptoGauge, build_gauge
from crypto_structure.market_data import download_universe
from crypto_structure.relative_strength import rank_universe
from crypto_structure.risk_reward import RiskRewardReport, analyze
from crypto_structure.trend_rr import trend_rr_profile
from crypto_structure.universe import BENCHMARK_TICKER, default_universe

MAX_SUPPORTS_SHOWN = 3
MAX_LEADERSHIP_ROWS_SHOWN = 25


def build_report(universe: Optional[dict[str, str]] = None) -> dict:
    """Fetch + analyze every ticker in `universe` (default: MAJORS +
    ALTCOINS, see universe.py) via one batched yfinance call. Never lets
    one ticker's analysis failure sink the whole report -- isolates it into
    `dropped` instead, matching market-structure/report.py's per-ticker
    isolation convention."""
    universe = universe or default_universe()
    ohlcv_by_ticker, download_dropped = download_universe(list(universe.keys()))

    reports: dict[str, RiskRewardReport] = {}
    trend_signals: dict[str, float] = {}
    closes: dict[str, pd.Series] = {}
    dates: dict[str, pd.DatetimeIndex] = {}
    dropped: list[dict] = list(download_dropped)

    for ticker, ohlcv in ohlcv_by_ticker.items():
        name = universe.get(ticker, ticker)
        close_series = pd.Series(ohlcv.close, index=ohlcv.dates)
        try:
            report = analyze(ticker, ohlcv.high, ohlcv.low, ohlcv.close, ohlcv.volume)
            trend_signals[ticker] = trend_rr_profile(close_series)["trend_signal"]
        except Exception as e:  # noqa: BLE001 -- per-ticker isolation, reason recorded below
            dropped.append({"ticker": ticker, "name": name, "reason": str(e)})
            continue
        reports[ticker] = report
        closes[ticker] = close_series
        dates[ticker] = ohlcv.dates

    if len(closes) < 2:
        raise RuntimeError(f"Only {len(closes)} ticker(s) survived analysis -- need >=2 for relative ranking")

    benchmark = BENCHMARK_TICKER if BENCHMARK_TICKER in closes else None
    leadership_table, pair_signals = rank_universe(closes, universe, benchmark_ticker=benchmark)

    gauge = build_gauge(reports, trend_signals, universe=universe)
    return {
        "universe": universe,
        "gauge": gauge,
        "reports": reports,
        "dates": dates,
        "dropped": dropped,
        "leadership_table": leadership_table,
        "pair_signals": pair_signals,
    }


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
            f"    #{i + 1}: {c.price:.4g}  -{pct:.1f}%  -{atr_dist:.1f} ATR  strength={c.strength}{gap}"
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
        f"  trendline ({status_word}): rising support from {start_date} (${line.start_price:.4g}) "
        f"through {end_date} (${anchor_price_at_end_idx:.4g} at anchor, slope {line.slope:+.4g}/bar), "
        f"extended to ${line.end_price:.4g} today{breach_note}"
    ]


def _asset_block_lines(ag: AssetGauge, report: RiskRewardReport, dates: Optional[pd.DatetimeIndex]) -> list[str]:
    lines = [
        f"{ag.ticker:9} {ag.name:20} risk_score={ag.risk_score:.1f}/100  last_close=${report.last_close:.4g}",
        f"  trend_component={ag.trend_component:.1f} (trend_signal={ag.trend_signal:+.2f}) "
        f"-> contributes {ag.trend_contribution:.1f}",
        f"  rr_component={ag.rr.component:.1f} (rr_ratio={ag.rr_ratio:.2f}x, source={ag.target_source}, "
        f"magnitude={ag.rr.magnitude:.1f}, quality={ag.rr.quality_multiplier:.2f}) "
        f"-> contributes {ag.rr_contribution:.1f}",
        f"  stop={report.stop_target.stop:.4g}  target={report.stop_target.target:.4g}  "
        f"risk={report.stop_target.risk_pct:.1f}%  reward={report.stop_target.reward_pct:.1f}%",
        f"  violation_penalty={ag.violation.total:.1f} = base {ag.violation.base:.1f} "
        f"+ streak {ag.violation.streak_penalty:.1f} + breach {ag.violation.breach_penalty:.1f}",
    ]
    lines += _support_stack_lines(report)
    lines += _trendline_detail_lines(report, dates)
    lines.append(f"  summary: {ag.blurb}")
    return lines


def _leadership_table_lines(leadership_table: pd.DataFrame) -> list[str]:
    view = leadership_table.head(MAX_LEADERSHIP_ROWS_SHOWN)
    lines = [
        f"{'Rank':>4} {'Ticker':9} {'Name':20} {'Leadership':>10} {'Opportunity':>11} {'Joint':>8} {'DomBy':>6}"
    ]
    for ticker, row in view.iterrows():
        lines.append(
            f"{int(row['Rank']):>4} {ticker:9} {str(row['Name'])[:20]:20} "
            f"{row['Leadership']:>10.1f} {row['Opportunity']:>11.1f} {row['Joint']:>8.1f} "
            f"{int(row['ParetoDominatedBy']):>6}"
        )
    return lines


def render_summary(result: dict) -> str:
    gauge: CryptoGauge = result["gauge"]
    lines = [
        f"crypto-structure snapshot — {len(gauge.assets)}/{len(result['universe'])} assets analyzed "
        f"(benchmark: {BENCHMARK_TICKER})",
        "",
        FORMULA_LEGEND,
        "",
        f"OVERALL RISK SCORE: {gauge.overall_risk_score:.1f}/100",
        f"RISK-OFF READ:      {gauge.risk_off_pct:.1f}%",
        f"BREADTH UNDERCUT:   {gauge.breadth_undercut_pct:.0%} of universe (weighted)",
        "",
        "-" * 80,
        "LEADERSHIP / OPPORTUNITY RANKING (relative trend indications, peer + BTC-benchmark)",
        "-" * 80,
    ]
    lines += _leadership_table_lines(result["leadership_table"])

    for ag in gauge.assets:
        report = result["reports"][ag.ticker]
        dates = result["dates"].get(ag.ticker)
        lines.append("")
        lines.append("-" * 80)
        lines += _asset_block_lines(ag, report, dates)
    if result["dropped"]:
        lines.append("")
        lines.append("Dropped tickers:")
        for d in result["dropped"]:
            lines.append(f"  {d['ticker']} ({d.get('name', '')}): {d['reason']}")
    return "\n".join(lines)


def main() -> None:
    result = build_report()
    print(render_summary(result))


if __name__ == "__main__":
    main()
