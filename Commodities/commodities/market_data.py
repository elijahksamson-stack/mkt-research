"""
Commodity futures data acquisition: continuous-series fetch (reused from
market_structure), dated-contract fetch for curve/carry, and roll-aware
return adjustment.

Two deliberately different price series feed this package, per the spec's
"do not train on a mechanically spliced price series" requirement:

1. **Raw continuous** (`OHLCV` from `market_structure.market_data`, reused
   unchanged -- futures have no splits/dividends so its `auto_adjust=True`
   is a no-op for this asset class). Used for anything level-based:
   `risk_reward_adapter.py` and `trend_adapter.py` draw trendlines,
   supports/resistance, and ATR off this series. Structural levels are
   conventionally read off raw continuous charts -- a ratio-back-adjusted
   series can drift to price levels a real contract never traded at over a
   multi-year lookback, which would make support/resistance clusters
   meaningless.

2. **Roll-adjusted close** (`build_roll_adjusted_close` below). Used for
   anything *return*-based: `momentum.py`, `labels.py`. Yahoo's continuous
   `=F` series splices consecutive front-month contracts with a real price
   jump at each roll (the old contract's last price vs. the new contract's
   first price -- i.e. the calendar-spread/contango-backwardation gap).
   Diffing the raw series treats that gap as a real one-day return, which
   is exactly the "artificial return at contract rolls" the spec warns
   against.

Roll-adjustment approximation, stated plainly: yfinance exposes no
open-interest series for futures and no per-bar "which contract is this"
flag, so there is no direct signal for exactly when volume/OI actually
rolled from one contract to the next. We detect roll *candidates* as
large single-day moves that coincide with a contract-month boundary
implied by `universe.py`'s `valid_months` (see `contracts.py`), then apply
a **ratio back-adjustment**: every price before the detected roll date is
multiplied by `close[roll] / close[roll-1]`, which eliminates the jump
while preserving percentage returns within each contract segment (as
opposed to Panama-canal/additive adjustment, which shifts by a fixed
dollar amount and can distort percentage-return math across very different
price regimes -- ratio adjustment is the more standard choice for
return-based modeling). This is an approximation of true dated-contract
splicing, not a replacement for it; false positives/negatives near the
month-boundary heuristic are possible for products with irregular roll
timing. See `contracts.py`'s module docstring for the matching caveat on
the month-boundary heuristic itself.
"""
from __future__ import annotations

import contextlib
import io
import logging
import time
import warnings
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf

from market_structure.market_data import OHLCV, fetch_ohlcv as fetch_continuous_ohlcv  # noqa: F401  (re-exported)

from commodities.universe import CommodityInstrument

warnings.filterwarnings("ignore", category=FutureWarning)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

DATED_CONTRACT_PERIOD = "1y"
MIN_DATED_BARS = 15  # dated contracts thin out near expiry; a hard 260-bar gate would reject valid curve data
DOWNLOAD_RETRIES = 3

# Roll-jump detection: a day is a roll candidate only if its |log return|
# exceeds JUMP_MAD_MULTIPLIER robust-scaled deviations AND falls within
# ROLL_WINDOW_DAYS of a valid contract-month boundary (see module docstring).
JUMP_MAD_MULTIPLIER = 6.0
ROLL_WINDOW_DAYS = 5


@dataclass(frozen=True)
class RollEvent:
    date: pd.Timestamp
    raw_log_return: float
    adjustment_ratio: float


@dataclass(frozen=True)
class CommoditySeries:
    canonical_id: str
    continuous_symbol: str
    dates: pd.DatetimeIndex
    raw_close: np.ndarray
    roll_adjusted_close: np.ndarray
    roll_events: tuple[RollEvent, ...]


def _download(
    symbol: str, period: Optional[str] = None, start: Optional[date] = None, end: Optional[date] = None
) -> pd.DataFrame:
    """`period` and `start`/`end` are mutually exclusive, per yfinance's own
    API -- `start`/`end` is what makes point-in-time-safe historical fetches
    possible (see fetch_dated_contract_close's `as_of` parameter).

    Retries only on a raised exception, never on a clean-but-empty
    response. An empty response is common and meaningful for dated
    contracts (Yahoo has no history for an expired, rolled-off symbol --
    see fetch_dated_contract_close's docstring) rather than a transient
    failure; retrying it with exponential backoff turned what should be an
    instant "no data" into a ~3-second stall per miss, which made historical
    curve/carry fetches across a multi-year training panel impractically
    slow. A real network error still gets the full retry treatment below."""
    raw = pd.DataFrame()
    for attempt in range(DOWNLOAD_RETRIES):
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                if start is not None or end is not None:
                    raw = yf.download(
                        symbol, start=start, end=end, interval="1d", auto_adjust=False, progress=False, timeout=20
                    )
                else:
                    raw = yf.download(
                        symbol, period=period, interval="1d", auto_adjust=False, progress=False, timeout=20
                    )
            break
        except Exception:
            if attempt < DOWNLOAD_RETRIES - 1:
                time.sleep(2**attempt)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    return raw


def _month_boundary_distance_days(ts: pd.Timestamp) -> int:
    """Days from `ts` to the nearer of this-month-start or next-month-start."""
    month_start = ts.replace(day=1)
    next_month_start = (month_start + pd.DateOffset(months=1)).replace(day=1)
    return int(min((ts - month_start).days, (next_month_start - ts).days))


def build_roll_adjusted_close(dates: pd.DatetimeIndex, raw_close: np.ndarray) -> tuple[np.ndarray, tuple[RollEvent, ...]]:
    """Ratio-back-adjust `raw_close` against detected roll jumps. See
    module docstring for the detection heuristic and its limitations."""
    n = len(raw_close)
    if n < 3:
        return raw_close.copy(), ()

    log_ret = np.diff(np.log(raw_close))
    med = float(np.median(log_ret))
    mad = float(np.median(np.abs(log_ret - med))) or 1e-8
    robust_z = np.abs(log_ret - med) / (1.4826 * mad)

    roll_idx: list[int] = []  # index i means the jump is between raw_close[i-1] and raw_close[i]
    for i in range(1, n):
        if robust_z[i - 1] < JUMP_MAD_MULTIPLIER:
            continue
        if _month_boundary_distance_days(pd.Timestamp(dates[i])) > ROLL_WINDOW_DAYS:
            continue
        roll_idx.append(i)

    adjusted = raw_close.astype(float).copy()
    events: list[RollEvent] = []
    # Walk backward so each earlier segment is adjusted by every roll after it, compounding.
    for i in reversed(roll_idx):
        ratio = raw_close[i] / raw_close[i - 1] if raw_close[i - 1] != 0 else 1.0
        adjusted[:i] *= ratio
        events.append(
            RollEvent(date=pd.Timestamp(dates[i]), raw_log_return=float(log_ret[i - 1]), adjustment_ratio=float(ratio))
        )
    return adjusted, tuple(reversed(events))


def fetch_commodity_series(instrument: CommodityInstrument, period: str = "3y") -> CommoditySeries:
    """Fetch `instrument`'s continuous series and derive the roll-adjusted
    close used by momentum.py/labels.py. Raises RuntimeError on a failed
    quality gate (delegated to market_structure's fetch_continuous_ohlcv)."""
    ohlcv: OHLCV = fetch_continuous_ohlcv(instrument.continuous_symbol, period=period)
    roll_adjusted, events = build_roll_adjusted_close(ohlcv.dates, ohlcv.close)
    return CommoditySeries(
        canonical_id=instrument.canonical_id,
        continuous_symbol=instrument.continuous_symbol,
        dates=ohlcv.dates,
        raw_close=ohlcv.close,
        roll_adjusted_close=roll_adjusted,
        roll_events=events,
    )


def fetch_dated_contract_close(
    symbol: str, as_of: Optional[date] = None, lookback: str = DATED_CONTRACT_PERIOD
) -> Optional[pd.Series]:
    """Daily close series for one dated contract symbol (e.g. `GCZ26.CMX`),
    ending at `as_of` (default: today). Returns None (not raises) on
    empty/too-thin data -- curve_carry.py treats a missing leg as a data
    gap to skip, not a fatal error, since thin/unlisted dated contracts are
    an expected steady-state condition near the edge of a product's
    listed-month horizon.

    Point-in-time note, CONFIRMED (not speculative) during this build via
    live requests: Yahoo only serves history for dated-contract symbols
    that are *currently* among a product's near listed months. A contract
    that has since expired and rolled off returns an empty response for
    ANY date range, including dates during its actual active trading life
    -- e.g. `GCQ25.CMX` (gold, Aug 2025) returns 0 rows even when queried
    for 2024-07-30..2025-07-31, squarely inside when it was trading. This
    means passing a historical `as_of` here is *correct* (keeps the fetch
    honestly point-in-time rather than leaking today's price) but
    *ineffective* for as_of dates old enough that the then-current near
    contracts have since expired -- which in practice is most of a
    multi-year walk-forward window. A None return in that case should be
    read as "Yahoo no longer has this data," not "no curve," and
    validation.py must tolerate curve/carry being sparse-to-empty across
    most of a historical backtest -- it is effectively a live-only feature
    family with this data source. See CLAUDE.md's limitations section for
    the fix path (a dedicated futures-history vendor) if backtesting
    carry_score specifically becomes a priority."""
    end = as_of + timedelta(days=1) if as_of is not None else None  # yfinance's `end` is exclusive
    start = (as_of or date.today()) - _period_to_timedelta(lookback)
    raw = _download(symbol, start=start, end=end)
    if raw.empty or "Close" not in raw:
        return None
    close = raw["Close"].dropna()
    close = close[close > 0]
    if len(close) < MIN_DATED_BARS:
        return None
    return close


def _period_to_timedelta(period: str) -> timedelta:
    if period.endswith("mo"):
        return timedelta(days=int(period[:-2]) * 30)
    unit, n = period[-1], int(period[:-1])
    days_per_unit = {"d": 1, "y": 365}
    return timedelta(days=n * days_per_unit.get(unit, 1))


def fetch_generic_series(symbol: str, period: str = "3y") -> Optional[pd.Series]:
    """Plain close-price series for macro-control inputs (USD index, yields,
    broad commodity index) that don't go through the futures universe/quality
    gate -- these are auxiliary features, not primary risk_reward/trend
    subjects, so a lighter-weight fetch is appropriate."""
    raw = _download(symbol, period)
    if raw.empty or "Close" not in raw:
        return None
    close = raw["Close"].dropna()
    return close if len(close) > 0 else None
