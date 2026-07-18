"""
Fibonacci extension targets — rr.txt Part 7.

When an asset is at/near all-time highs there's no resistance cluster and no
upper trendline overhead (nothing above to measure reward against), so the
target would otherwise fall to a flat synthetic 2:1 fallback. This engine
manufactures a real structural reward by projecting Fibonacci extensions up
from the trough of the most recent meaningful (>=10% drawdown) pullback.
Feeds tier-3 of the stop/target logic (stop_target.py Part 8). Pure math,
bar-indexed rather than calendar-indexed, so it needs no crypto-specific
adaptation — verbatim port of Macro/market-structure's fib_extension.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from crypto_structure.indicators import Pivot

FIB_EXT_RATIOS: tuple[float, ...] = (1.000, 1.272, 1.382, 1.500, 1.618, 1.786, 2.000, 2.618)
FIB_EXT_LOOKBACK_BARS = 504
FIB_EXT_MIN_DRAWDOWN_PCT = 0.10
FIB_EXT_PHI = 1.618033988749895
FIB_EXT_MAX_RATIOS = 32


@dataclass(frozen=True)
class FibExtensionLevel:
    ratio: float
    price: float


@dataclass(frozen=True)
class FibExtension:
    peak_idx: int
    peak_price: float
    trough_idx: int
    trough_price: float
    range: float
    levels: list[FibExtensionLevel]


def build_fib_extension(
    pivots: Sequence[Pivot], n: int, last_close: float, lookback: int = FIB_EXT_LOOKBACK_BARS
) -> Optional[FibExtension]:
    """Walk lows newest-first; accept the first (most recent) low whose
    nearest preceding high represents a drawdown of >=10%, then project
    FIB_EXT_RATIOS up from that trough. Extends the ratio set by phi if
    every level already sits at/below last_close (a "runaway" that already
    ran past the standard extension set), capped at FIB_EXT_MAX_RATIOS."""
    if n == 0 or not pivots:
        return None
    cutoff = n - lookback
    lows_newest_first = sorted(
        (p for p in pivots if p.type == "low" and p.idx >= cutoff), key=lambda p: p.idx, reverse=True
    )
    highs_by_idx = sorted((p for p in pivots if p.type == "high"), key=lambda p: p.idx)

    peak: Optional[Pivot] = None
    trough: Optional[Pivot] = None
    for low in lows_newest_first:
        preceding_highs = [h for h in highs_by_idx if h.idx < low.idx]
        if not preceding_highs:
            continue
        candidate_peak = max(preceding_highs, key=lambda h: h.idx)
        drawdown = candidate_peak.price - low.price
        if drawdown > 0 and drawdown / candidate_peak.price >= FIB_EXT_MIN_DRAWDOWN_PCT:
            peak, trough = candidate_peak, low
            break
    if peak is None or trough is None:
        return None

    rng = peak.price - trough.price
    ratios = list(FIB_EXT_RATIOS)
    levels = [FibExtensionLevel(ratio=r, price=trough.price + r * rng) for r in ratios]
    if all(lv.price <= last_close for lv in levels):
        last_ratio = ratios[-1]
        while all(lv.price <= last_close for lv in levels) and len(ratios) < FIB_EXT_MAX_RATIOS:
            last_ratio *= FIB_EXT_PHI
            ratios.append(last_ratio)
            levels.append(FibExtensionLevel(ratio=last_ratio, price=trough.price + last_ratio * rng))

    return FibExtension(
        peak_idx=peak.idx,
        peak_price=peak.price,
        trough_idx=trough.idx,
        trough_price=trough.price,
        range=rng,
        levels=levels,
    )
