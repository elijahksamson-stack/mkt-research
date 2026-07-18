"""
equity-rotation report -- orchestrates market_data + rotation_ranking +
relative_technicals into one snapshot: sector rotation ranking, factor
rotation ranking, and a combined RRG-style relative-technicals table.

Three plain-text tables, no charts -- render_summary() prints exactly the
fields computed by rotation_ranking.py/relative_technicals.py, nothing
derived only for display. If a ranking looks surprising, every number that
produced it is a named column in the same table.
"""
from __future__ import annotations

from typing import Optional

import pandas as pd

from equity_rotation.market_data import DEFAULT_PERIOD, fetch_universe
from equity_rotation.relative_technicals import RelativeTechnicals, relative_technicals
from equity_rotation.rotation_ranking import RotationTable, rank_universe
from equity_rotation.universe import BENCHMARK, FACTOR_ETFS, SECTOR_ETFS, default_universe

MIN_TICKERS_TO_RANK = 2


def build_report(universe: Optional[dict[str, str]] = None, period: str = DEFAULT_PERIOD) -> dict:
    """Fetch + analyze the full universe (default: 11 sectors + 6 factors).
    Never lets one ticker's fetch/analysis failure sink the whole report --
    isolates it into `dropped` instead, matching market-structure's
    per-series isolation convention."""
    universe = universe or default_universe()
    sector_universe = {t: n for t, n in universe.items() if t in SECTOR_ETFS}
    factor_universe = {t: n for t, n in universe.items() if t in FACTOR_ETFS}

    fetch_targets = {**universe, BENCHMARK: "Benchmark"}
    fetch = fetch_universe(fetch_targets, period=period)
    benchmark_close = fetch.closes.get(BENCHMARK)
    if benchmark_close is None:
        raise RuntimeError(f"Benchmark {BENCHMARK} failed the data-quality gate -- cannot rank without it")

    dropped = list(fetch.dropped)
    sector_closes = {t: fetch.closes[t] for t in sector_universe if t in fetch.closes}
    factor_closes = {t: fetch.closes[t] for t in factor_universe if t in fetch.closes}

    sector_table = (
        rank_universe(sector_closes, sector_universe, benchmark_close)
        if len(sector_closes) >= MIN_TICKERS_TO_RANK
        else None
    )
    factor_table = (
        rank_universe(factor_closes, factor_universe, benchmark_close)
        if len(factor_closes) >= MIN_TICKERS_TO_RANK
        else None
    )

    all_closes = {**sector_closes, **factor_closes}
    all_labels = {**sector_universe, **factor_universe}
    technicals: list[RelativeTechnicals] = []
    for ticker, close in all_closes.items():
        try:
            technicals.append(relative_technicals(ticker, all_labels[ticker], close, benchmark_close))
        except Exception as e:  # noqa: BLE001 -- per-ticker isolation, reason recorded below
            dropped.append({"ticker": ticker, "name": all_labels[ticker], "reason": f"relative_technicals: {e}"})
    technicals.sort(key=lambda r: r.rs_ratio, reverse=True)

    return {
        "as_of": fetch.as_of,
        "sector_table": sector_table,
        "factor_table": factor_table,
        "technicals": technicals,
        "dropped": dropped,
    }


def _rotation_frame(table: RotationTable) -> pd.DataFrame:
    rows = [
        {
            "Rank": r.rank,
            "Ticker": r.ticker,
            "Name": r.name,
            "Leadership": round(r.leadership, 1),
            "Opportunity": round(r.opportunity, 1),
            "Joint": round(r.joint, 1),
            "ParetoDominatedBy": r.pareto_dominated_by,
        }
        for r in table.ranks
    ]
    return pd.DataFrame(rows).set_index("Rank")


def _technicals_frame(technicals: list[RelativeTechnicals]) -> pd.DataFrame:
    def pct(value: Optional[float]) -> str:
        return "n/a" if value is None else f"{value:+.1%}"

    rows = [
        {
            "Ticker": t.ticker,
            "Name": t.name,
            "Quadrant": t.quadrant,
            "DaysInQuadrant": t.days_in_quadrant,
            "RS-Ratio": round(t.rs_ratio, 1),
            "RS-Momentum": round(t.rs_momentum, 1),
            "vs50DMA": pct(t.ratio_vs_50dma_pct),
            "vs200DMA": pct(t.ratio_vs_200dma_pct),
            "MACross": t.ma_cross or "n/a",
            "RelVol": round(t.relative_volatility, 2),
        }
        for t in technicals
    ]
    return pd.DataFrame(rows)


def render_summary(result: dict) -> str:
    lines = [
        f"equity-rotation snapshot -- data through {result['as_of'].date()}",
        "",
    ]

    if result["sector_table"] is not None:
        lines.append("SECTOR ROTATION RANKING")
        lines.append(_rotation_frame(result["sector_table"]).to_string())
        lines.append("")
    else:
        lines.append("SECTOR ROTATION RANKING: not enough sectors passed the data gate to rank")
        lines.append("")

    if result["factor_table"] is not None:
        lines.append("FACTOR ROTATION RANKING")
        lines.append(_rotation_frame(result["factor_table"]).to_string())
        lines.append("")
    else:
        lines.append("FACTOR ROTATION RANKING: not enough factors passed the data gate to rank")
        lines.append("")

    if result["technicals"]:
        lines.append("RELATIVE TECHNICALS (RRG-style, vs. benchmark) -- sorted by RS-Ratio")
        lines.append(_technicals_frame(result["technicals"]).to_string(index=False))
        lines.append("")

    if result["dropped"]:
        lines.append("Dropped tickers:")
        for d in result["dropped"]:
            lines.append(f"  {d['ticker']} ({d['name']}): {d['reason']}")

    return "\n".join(lines)


def main() -> None:
    result = build_report()
    print(render_summary(result))


if __name__ == "__main__":
    main()
