"""
Canonical commodity futures universe.

One `CommodityInstrument` per *economic* commodity (not per contract, not
per ETF) -- the mapping the spec calls for so a downstream feature or model
never has to know whether it's looking at a continuous-front proxy or a
specific dated contract. `continuous_symbol` is the yfinance generic
front-month series (e.g. `GC=F`), used for levels/trend/risk-reward and for
momentum returns after roll-adjustment (see `market_data.py`). `root` +
`exchange_suffix` + `valid_months` describe how to build *dated* contract
symbols (e.g. `GCZ26.CMX`) for curve/carry construction (see
`contracts.py`) -- yfinance has no generic "second month" or "third month"
series, only the front continuous and specific contract-month symbols, so
curve work has to address contracts directly.

`valid_months` are the standard exchange-listed delivery-month cycles
(CME/ICE/CBOT rulebooks) for each product's most liquid contracts. These
are real, documented conventions but exchanges do occasionally add/drop
listed months -- if `contracts.py` starts returning empty series for a
product, check the live exchange contract spec before assuming a code bug.

Uranium has no exchange-traded futures series on yfinance (`UX=F` returns
no data, verified against the live feed) -- URA (Global X Uranium ETF) is
carried as an equity-basket proxy with `is_tradable_future=False`. Curve,
carry, and CFTC-positioning features are structurally unavailable for it;
`ranking.py` must not silently zero-fill those fields for URA -- they
should read as missing, not as "flat curve" or "zero positioning".
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

Family = Literal["energy", "precious_metals", "industrial_metals", "agriculture", "livestock"]


@dataclass(frozen=True)
class CommodityInstrument:
    canonical_id: str
    display_name: str
    family: Family
    continuous_symbol: str  # yfinance generic continuous series, e.g. "GC=F"
    root: str  # futures root for dated-contract symbols, e.g. "GC"
    exchange_suffix: str  # yfinance dated-contract suffix, e.g. "CMX"
    valid_months: tuple[str, ...]  # standard delivery-month codes (F,G,H,J,K,M,N,Q,U,V,X,Z)
    is_tradable_future: bool = True
    cftc_market_name: Optional[str] = None  # substring match into CFTC's market_and_exchange_names


ALL_MONTHS = ("F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z")

UNIVERSE: tuple[CommodityInstrument, ...] = (
    # -- Energy --
    CommodityInstrument("wti_crude", "WTI Crude Oil", "energy", "CL=F", "CL", "NYM", ALL_MONTHS,
                         cftc_market_name="CRUDE OIL, LIGHT SWEET-WTI"),
    CommodityInstrument("brent_crude", "Brent Crude Oil", "energy", "BZ=F", "BZ", "NYM", ALL_MONTHS,
                         cftc_market_name="BRENT LAST DAY"),
    CommodityInstrument("natural_gas", "Henry Hub Natural Gas", "energy", "NG=F", "NG", "NYM", ALL_MONTHS,
                         cftc_market_name="NAT GAS NYME"),
    CommodityInstrument("rbob_gasoline", "RBOB Gasoline", "energy", "RB=F", "RB", "NYM", ALL_MONTHS,
                         cftc_market_name="GASOLINE RBOB"),
    CommodityInstrument("heating_oil", "NY Harbor ULSD (Heating Oil)", "energy", "HO=F", "HO", "NYM", ALL_MONTHS,
                         cftc_market_name="NY HARBOR ULSD"),
    CommodityInstrument("uranium", "Uranium (URA ETF proxy)", "energy", "URA", "", "", (),
                         is_tradable_future=False),

    # -- Precious Metals --
    CommodityInstrument("gold", "Gold", "precious_metals", "GC=F", "GC", "CMX",
                         ("G", "J", "M", "Q", "V", "Z"), cftc_market_name="GOLD"),
    CommodityInstrument("silver", "Silver", "precious_metals", "SI=F", "SI", "CMX",
                         ("F", "H", "K", "N", "U", "Z"), cftc_market_name="SILVER"),
    CommodityInstrument("platinum", "Platinum", "precious_metals", "PL=F", "PL", "NYM",
                         ("F", "J", "N", "V"), cftc_market_name="PLATINUM"),
    CommodityInstrument("palladium", "Palladium", "precious_metals", "PA=F", "PA", "NYM",
                         ("H", "M", "U", "Z"), cftc_market_name="PALLADIUM"),

    # -- Industrial Metals --
    CommodityInstrument("copper", "Copper", "industrial_metals", "HG=F", "HG", "CMX", ALL_MONTHS,
                         cftc_market_name="COPPER- #1"),
    CommodityInstrument("aluminum", "Aluminum", "industrial_metals", "ALI=F", "ALI", "CMX", ALL_MONTHS,
                         cftc_market_name="ALUMINUM"),

    # -- Agriculture --
    CommodityInstrument("corn", "Corn", "agriculture", "ZC=F", "ZC", "CBT",
                         ("H", "K", "N", "U", "Z"), cftc_market_name="CORN"),
    CommodityInstrument("wheat", "Chicago SRW Wheat", "agriculture", "ZW=F", "ZW", "CBT",
                         ("H", "K", "N", "U", "Z"), cftc_market_name="WHEAT-SRW"),
    CommodityInstrument("soybeans", "Soybeans", "agriculture", "ZS=F", "ZS", "CBT",
                         ("F", "H", "K", "N", "Q", "U", "X"), cftc_market_name="SOYBEANS"),
    CommodityInstrument("oats", "Oats", "agriculture", "ZO=F", "ZO", "CBT",
                         ("H", "K", "N", "U", "Z"), cftc_market_name="OATS"),
    CommodityInstrument("rough_rice", "Rough Rice", "agriculture", "ZR=F", "ZR", "CBT",
                         ("F", "H", "K", "N", "U", "X"), cftc_market_name="ROUGH RICE"),
    CommodityInstrument("coffee", "Coffee C", "agriculture", "KC=F", "KC", "NYB",
                         ("H", "K", "N", "U", "Z"), cftc_market_name="COFFEE C"),
    CommodityInstrument("sugar", "Sugar No. 11", "agriculture", "SB=F", "SB", "NYB",
                         ("H", "K", "N", "V"), cftc_market_name="SUGAR NO. 11"),
    CommodityInstrument("cotton", "Cotton No. 2", "agriculture", "CT=F", "CT", "NYB",
                         ("H", "K", "N", "V", "Z"), cftc_market_name="COTTON NO. 2"),
    CommodityInstrument("cocoa", "Cocoa", "agriculture", "CC=F", "CC", "NYB",
                         ("H", "K", "N", "U", "Z"), cftc_market_name="COCOA"),
    CommodityInstrument("orange_juice", "Orange Juice", "agriculture", "OJ=F", "OJ", "NYB",
                         ("F", "H", "K", "N", "U", "X"), cftc_market_name="FRZN CONCENTRATED ORANGE JUICE"),

    # -- Livestock --
    CommodityInstrument("live_cattle", "Live Cattle", "livestock", "LE=F", "LE", "CME",
                         ("G", "J", "M", "Q", "V", "Z"), cftc_market_name="LIVE CATTLE"),
    CommodityInstrument("lean_hogs", "Lean Hogs", "livestock", "HE=F", "HE", "CME",
                         ("G", "J", "K", "M", "N", "Q", "V", "Z"), cftc_market_name="LEAN HOGS"),
    CommodityInstrument("feeder_cattle", "Feeder Cattle", "livestock", "GF=F", "GF", "CME",
                         ("F", "H", "J", "K", "Q", "U", "V", "X"), cftc_market_name="FEEDER CATTLE"),
)

# Economically-linked pairs for pair-ratio momentum/mean-reversion (momentum.py, mean_reversion.py).
# Each tuple is (numerator_id, denominator_id); the ratio numerator/denominator is what's modeled.
CANONICAL_PAIRS: tuple[tuple[str, str], ...] = (
    ("wti_crude", "brent_crude"),
    ("gold", "silver"),
    ("copper", "gold"),
    ("corn", "wheat"),
    ("heating_oil", "wti_crude"),  # crack-spread-adjacent, refined vs. crude
    ("platinum", "palladium"),
)


def default_universe() -> dict[str, CommodityInstrument]:
    return {c.canonical_id: c for c in UNIVERSE}


def by_family(family: Family, universe: Optional[dict[str, CommodityInstrument]] = None) -> dict[str, CommodityInstrument]:
    universe = universe or default_universe()
    return {cid: c for cid, c in universe.items() if c.family == family}


def tradable_futures(universe: Optional[dict[str, CommodityInstrument]] = None) -> dict[str, CommodityInstrument]:
    """Subset with real listed futures (excludes ETF-basket proxies like uranium/URA) --
    the set curve_carry.py and positioning.py should iterate over."""
    universe = universe or default_universe()
    return {cid: c for cid, c in universe.items() if c.is_tradable_future}
