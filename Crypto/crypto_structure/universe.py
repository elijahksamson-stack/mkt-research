"""
Default crypto ticker universe for the risk:reward + relative-strength
toolkit.

Two tiers, mirroring Macro/market-structure's BROAD_INDEXES/SECTOR_ETFS
split: MAJORS are BTC and ETH -- the assets that set the tone for the
market itself and the natural benchmark for relative-strength ranking
(BTC plays the role SPY plays for equities: the default "the market"
series everything else is measured against). ALTCOINS add breadth for the
per-asset "which asset is leading, and why" ranking, weighted lower in the
composite gauge so a single altcoin's move doesn't swing the headline
number as much as BTC/ETH do.

Tickers use yfinance's standard `<SYMBOL>-USD` crypto format. The list is
deliberately conservative (liquid, multi-year-history large caps) --
market_data.py's quality/liquidity gate will drop anything that doesn't
actually have enough clean history, so a name here is a candidate, not a
guarantee it survives into a report.
"""
from __future__ import annotations

BENCHMARK_TICKER = "BTC-USD"

MAJORS: dict[str, str] = {
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
}

ALTCOINS: dict[str, str] = {
    "SOL-USD": "Solana",
    "XRP-USD": "XRP",
    "ADA-USD": "Cardano",
    "DOGE-USD": "Dogecoin",
    "AVAX-USD": "Avalanche",
    "LINK-USD": "Chainlink",
    "DOT-USD": "Polkadot",
    "LTC-USD": "Litecoin",
    "BCH-USD": "Bitcoin Cash",
    "ATOM-USD": "Cosmos",
    "UNI-USD": "Uniswap",
    "NEAR-USD": "NEAR Protocol",
    "APT-USD": "Aptos",
    "ARB-USD": "Arbitrum",
    "OP-USD": "Optimism",
    "ETC-USD": "Ethereum Classic",
}

MAJORS_WEIGHT_TOTAL = 0.60
ALTCOINS_WEIGHT_TOTAL = 0.40


def default_universe() -> dict[str, str]:
    """All tickers in the default universe, ticker -> display name."""
    return {**MAJORS, **ALTCOINS}


def composite_weights(universe: dict[str, str] | None = None) -> dict[str, float]:
    """Per-ticker weight in the overall gauge.

    Splits MAJORS_WEIGHT_TOTAL evenly across whichever MAJORS are present
    and ALTCOINS_WEIGHT_TOTAL evenly across whichever ALTCOINS are present,
    so the 60/40 split holds even if the caller passes a trimmed universe.
    Tickers outside both known tiers split whatever weight budget remains,
    so a fully custom universe still sums to 1.0.
    """
    universe = universe or default_universe()
    majors = [t for t in universe if t in MAJORS]
    alts = [t for t in universe if t in ALTCOINS]
    other = [t for t in universe if t not in MAJORS and t not in ALTCOINS]

    weights: dict[str, float] = {}
    if majors:
        share = MAJORS_WEIGHT_TOTAL / len(majors)
        weights.update({t: share for t in majors})
    if alts:
        share = ALTCOINS_WEIGHT_TOTAL / len(alts)
        weights.update({t: share for t in alts})
    if other:
        remaining = max(0.0, 1.0 - sum(weights.values()))
        share = remaining / len(other)
        weights.update({t: share for t in other})
    return weights
