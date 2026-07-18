"""
Dated futures-contract symbol generation for curve/carry construction.

yfinance has no "second nearby" or "third nearby" continuous series -- only
the generic front continuous (`GC=F`) and specific dated contracts
(`GCZ26.CMX`). To build a term structure at all, `curve_carry.py` needs
concrete dated symbols to fetch. This module turns
(`root`, `exchange_suffix`, `valid_months`) from `universe.py` plus an
as-of date into an ordered list of upcoming contract symbols.

Approximation, stated plainly: we do not have an open-interest or exchange
expiry-calendar feed (yfinance returns no open-interest for futures, and
CFTC COT is weekly/aggregate, not per-contract), so there is no direct
signal for exactly when liquidity rolls from one contract to the next.
`ROLL_BUFFER_MONTHS` sidesteps this by never treating the *current* calendar
month's contract as the front -- it starts counting from next month, which
keeps curve_carry.py off contracts that are within days of expiry and thin.
This is a real precision limit, not a bug: if a product's actual roll
happens unusually early or late in the month, the "front" contract picked
here can be a few trading days off from what a trading desk would call
front month. Documented in the top-level CLAUDE.md's limitations section.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from commodities.universe import CommodityInstrument

MONTH_CODE_TO_NUM: dict[str, int] = {
    "F": 1, "G": 2, "H": 3, "J": 4, "K": 5, "M": 6,
    "N": 7, "Q": 8, "U": 9, "V": 10, "X": 11, "Z": 12,
}
NUM_TO_MONTH_CODE: dict[int, str] = {v: k for k, v in MONTH_CODE_TO_NUM.items()}

ROLL_BUFFER_MONTHS = 1  # never treat the current calendar month's contract as "front"
SEARCH_HORIZON_MONTHS = 36  # far enough ahead to always find 3 valid months for sparse-month products


@dataclass(frozen=True)
class ContractMonth:
    year: int
    month: int  # 1-12
    month_code: str
    symbol: str  # yfinance dated-contract symbol, e.g. "GCZ26.CMX"


def dated_symbol(root: str, month_code: str, year: int, exchange_suffix: str) -> str:
    yy = f"{year % 100:02d}"
    return f"{root}{month_code}{yy}.{exchange_suffix}"


def next_contract_months(
    instrument: CommodityInstrument,
    as_of: date,
    count: int = 3,
    roll_buffer_months: int = ROLL_BUFFER_MONTHS,
) -> list[ContractMonth]:
    """The next `count` valid delivery months for `instrument`, starting
    `roll_buffer_months` after `as_of`'s month, in chronological order.
    Raises ValueError if `instrument.is_tradable_future` is False (no
    contract-month cycle exists, e.g. the uranium ETF proxy) or if fewer
    than `count` valid months are found within SEARCH_HORIZON_MONTHS."""
    if not instrument.is_tradable_future:
        raise ValueError(f"{instrument.canonical_id} has no listed futures contract cycle")

    valid_nums = {MONTH_CODE_TO_NUM[m] for m in instrument.valid_months}
    start_month_idx = as_of.year * 12 + (as_of.month - 1) + roll_buffer_months

    found: list[ContractMonth] = []
    for offset in range(SEARCH_HORIZON_MONTHS):
        month_idx = start_month_idx + offset
        year, month = divmod(month_idx, 12)
        month += 1  # divmod gives 0-11
        if month not in valid_nums:
            continue
        code = NUM_TO_MONTH_CODE[month]
        symbol = dated_symbol(instrument.root, code, year, instrument.exchange_suffix)
        found.append(ContractMonth(year=year, month=month, month_code=code, symbol=symbol))
        if len(found) >= count:
            break

    if len(found) < count:
        raise ValueError(
            f"{instrument.canonical_id}: only found {len(found)}/{count} valid contract months "
            f"within {SEARCH_HORIZON_MONTHS} months of {as_of} -- check universe.py's valid_months"
        )
    return found


def curve_symbols(instrument: CommodityInstrument, as_of: date) -> tuple[str, str, str]:
    """Front/second/third dated-contract symbols for curve_carry.py."""
    months = next_contract_months(instrument, as_of, count=3)
    return tuple(m.symbol for m in months)  # type: ignore[return-value]
