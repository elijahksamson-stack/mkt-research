"""
Default ETF universe for equity-rotation: which sectors and which style
factors are currently leading/lagging the broad US equity market.

Deliberately excludes broad indexes (SPY/QQQ/IWM/DIA/MDY) -- that
market-vs-macro read already lives in Macro/market-structure's macro
gauge. This package's job is the layer beneath that: rotation *within*
the equity market itself.

Two tiers, scored independently (see rotation_ranking.py) rather than
blended into one composite -- a sector rotation and a factor rotation are
different questions ("which industry is leading" vs. "is the market
rewarding growth or value, momentum or quality right now") and conflating
them into a single number would hide which one is actually moving.
"""
from __future__ import annotations

BENCHMARK = "SPY"

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

FACTOR_ETFS: dict[str, str] = {
    "IWF": "Growth (Russell 1000 Growth)",
    "IWD": "Value (Russell 1000 Value)",
    "IJR": "Size (S&P SmallCap 600)",
    "MTUM": "Momentum (MSCI USA Momentum)",
    "QUAL": "Quality (MSCI USA Quality)",
    "USMV": "Low Volatility (MSCI USA Min Vol)",
}


def default_universe() -> dict[str, str]:
    """All tickers in the default universe (both tiers), ticker -> display name."""
    return {**SECTOR_ETFS, **FACTOR_ETFS}


def tier_of(ticker: str) -> str:
    """Which tier `ticker` belongs to: 'sector', 'factor', or 'other' (a
    custom ticker passed outside the two known tiers)."""
    if ticker in SECTOR_ETFS:
        return "sector"
    if ticker in FACTOR_ETFS:
        return "factor"
    return "other"
