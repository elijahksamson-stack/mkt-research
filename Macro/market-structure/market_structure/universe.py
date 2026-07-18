"""
Default index/ETF universe for the macro market-structure gauge.

Two tiers: BROAD_INDEXES are the market itself (headline bullishness +
cash-on-sidelines gauge); SECTOR_ETFS add breadth/rotation context for the
per-index "which index is more bullish, and why" breakdown, weighted lower
in the composite so a single sector rotation doesn't move the headline
number as much as the indexes it's actually built from.
"""
from __future__ import annotations

BROAD_INDEXES: dict[str, str] = {
    "SPY": "S&P 500",
    "QQQ": "Nasdaq 100",
    "IWM": "Russell 2000",
    "DIA": "Dow Jones Industrial Average",
    "MDY": "S&P MidCap 400",
}

SECTOR_ETFS: dict[str, str] = {
    "XLC": "Communication Services",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLE": "Energy",
    "XLF": "Financials",
    "XLV": "Health Care",
    "XLI": "Industrials",
    "XLB": "Materials",
    "XLRE": "Real Estate",
    "XLK": "Technology",
    "XLU": "Utilities",
}

BROAD_WEIGHT_TOTAL = 0.70
SECTOR_WEIGHT_TOTAL = 0.30


def default_universe() -> dict[str, str]:
    """All tickers in the default universe, ticker -> display name."""
    return {**BROAD_INDEXES, **SECTOR_ETFS}


def composite_weights(universe: dict[str, str] | None = None) -> dict[str, float]:
    """Per-ticker weight in the overall gauge.

    Splits BROAD_WEIGHT_TOTAL evenly across whichever BROAD_INDEXES are
    present and SECTOR_WEIGHT_TOTAL evenly across whichever SECTOR_ETFS are
    present, so the 70/30 split holds even if the caller passes a trimmed
    universe. Tickers outside both known tiers split whatever weight budget
    remains, so a fully custom universe still sums to 1.0.
    """
    universe = universe or default_universe()
    broad = [t for t in universe if t in BROAD_INDEXES]
    sector = [t for t in universe if t in SECTOR_ETFS]
    other = [t for t in universe if t not in BROAD_INDEXES and t not in SECTOR_ETFS]

    weights: dict[str, float] = {}
    if broad:
        share = BROAD_WEIGHT_TOTAL / len(broad)
        weights.update({t: share for t in broad})
    if sector:
        share = SECTOR_WEIGHT_TOTAL / len(sector)
        weights.update({t: share for t in sector})
    if other:
        remaining = max(0.0, 1.0 - sum(weights.values()))
        share = remaining / len(other)
        weights.update({t: share for t in other})
    return weights
