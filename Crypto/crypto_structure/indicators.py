"""
Indicators + pivot detection — rr.txt Parts 2-3.

ATR, realized volatility, relative volume, and recency-weighted swing
pivots are the raw material every level-detection method and trendline
family in this package builds on. Pure math over numpy arrays, bar-indexed
rather than calendar-indexed, so it needs no crypto-specific adaptation --
verbatim port of Macro/market-structure's indicators.py, itself a port of
RiskRewardAnalyzer's _atr / _realized_vol / _relative_volume /
_find_local_extrema / _build_pivots_with_macd_filter, distilled in
/Users/elisamson/Desktop/wisdom/rr.txt Parts 2-3 (the source-of-truth spec
this module follows constant-for-constant).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

import numpy as np

ATR_PERIOD = 14
VOL_PERIOD = 20
RVOL_PERIOD = 20
HV_CLIP = (0.005, 0.08)
PIVOT_WINDOW = 5
PIVOT_HALFLIFE_BARS = 60
MIN_BARS = 60


class InsufficientDataError(ValueError):
    """Fewer than MIN_BARS bars are available — nothing downstream can run."""


def require_min_bars(n: int, minimum: int = MIN_BARS) -> None:
    if n < minimum:
        raise InsufficientDataError(f"{n} bars < minimum {minimum}")


def average_true_range(
    high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = ATR_PERIOD
) -> float:
    """EMA-style ATR(period). Falls back to mean(high-low) below period+1
    bars, and to mean(TR[-period:]) if the recurrence produces a
    non-positive value."""
    n = len(close)
    if n < period + 1:
        return float(np.mean(high - low))
    prev_close = close[:-1]
    tr = np.maximum(
        high[1:] - low[1:],
        np.maximum(np.abs(high[1:] - prev_close), np.abs(low[1:] - prev_close)),
    )
    atr = np.empty(len(tr))
    atr[period - 1] = np.mean(tr[:period])
    for i in range(period, len(tr)):
        atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
    value = float(atr[-1])
    if value <= 0:
        value = float(np.mean(tr[-period:]))
    return value


def realized_volatility(close: np.ndarray, period: int = VOL_PERIOD) -> float:
    """Clipped stdev of the last `period` daily log returns. Returns the
    0.02 default below period+1 bars (too little history to estimate)."""
    if len(close) < period + 1:
        return 0.02
    log_ret = np.diff(np.log(close[-(period + 1) :]))
    hv = float(np.std(log_ret))
    return float(np.clip(hv, *HV_CLIP))


def relative_volume(volume: np.ndarray, period: int = RVOL_PERIOD) -> float:
    """Last bar's volume vs the mean of the prior `period` bars (excluding
    today). Returns 1.0 (neutral) below period+1 bars or on a zero
    last/average volume."""
    if len(volume) < period + 1 or volume[-1] == 0:
        return 1.0
    avg_vol = np.mean(volume[-(period + 1) : -1])
    if avg_vol == 0:
        return 1.0
    return float(volume[-1] / avg_vol)


PivotType = Literal["high", "low"]


@dataclass(frozen=True)
class Pivot:
    idx: int
    price: float
    type: PivotType
    weight: float
    age: int


def find_local_extrema(
    high: np.ndarray, low: np.ndarray, window: int = PIVOT_WINDOW
) -> tuple[list[int], list[int]]:
    """Indices of swing highs/lows: a bar equal to the max/min of the
    (2*window+1)-bar window centered on it."""
    n = len(high)
    high_idx: list[int] = []
    low_idx: list[int] = []
    for i in range(window, n - window):
        lo, hi = i - window, i + window + 1
        if high[i] == np.max(high[lo:hi]):
            high_idx.append(i)
        if low[i] == np.min(low[lo:hi]):
            low_idx.append(i)
    return high_idx, low_idx


def build_pivots(
    high: np.ndarray,
    low: np.ndarray,
    window: int = PIVOT_WINDOW,
    halflife: int = PIVOT_HALFLIFE_BARS,
) -> list[Pivot]:
    """Recency-weighted pivot list, sorted by bar index ascending. Weight
    decays exponentially with age (bars since the pivot), halving every
    `halflife` bars. Despite the original method's name
    (_build_pivots_with_macd_filter), no MACD filter is active in the
    source build — this is recency weighting only.
    """
    n = len(high)
    high_idx, low_idx = find_local_extrema(high, low, window)
    decay = math.log(2) / halflife
    last = n - 1
    pivots = [
        Pivot(idx=idx, price=float(high[idx]), type="high", weight=math.exp(-decay * (last - idx)), age=last - idx)
        for idx in high_idx
    ] + [
        Pivot(idx=idx, price=float(low[idx]), type="low", weight=math.exp(-decay * (last - idx)), age=last - idx)
        for idx in low_idx
    ]
    return sorted(pivots, key=lambda p: p.idx)
