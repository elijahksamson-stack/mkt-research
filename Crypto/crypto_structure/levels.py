"""
Six independent level-detection methods + convergence clustering — rr.txt
Parts 4 and 6.

Each method proposes support/resistance prices from a different angle
(horizontal channels, fibonacci retracement, anchored VWAP, volume profile,
round numbers — the sixth method, quantile-regression trendlines, lives in
trendlines.py and is fed in here as pre-built Level entries). Their
independence is the point: when >=2 disagreeing-methods land on the same
price, that agreement is the signal (Part 6). Pure math, no I/O, and
price/bar-indexed rather than calendar-indexed, so it needs no
crypto-specific adaptation — verbatim port of Macro/market-structure's
levels.py.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal, Sequence

import numpy as np

from crypto_structure.indicators import Pivot

SR_LOOKBACK_BARS = 252
CHANNEL_ATR_MULT = 1.10
CHANNEL_MIN_PCT = 0.004
CHANNEL_MIN_TOUCHES = 2
RECENT_CHANNEL_MAX_AGE = 40

MAX_SR_DIST_ATR = 8.0
MAX_SR_DIST_PCT = 0.20

FIB_LOOKBACK_BARS = 120
FIB_LEVELS: tuple[float, ...] = (0.236, 0.382, 0.5, 0.618, 0.786)

AVWAP_LOOKBACK_BARS = 120
AVWAP_TOP_N = 3

VP_BINS = 40
VP_HVN_THRESHOLD = 0.70

CLUSTER_ATR_MULT = 0.75
MIN_CLUSTER_METHODS = 2

LevelSide = Literal["support", "resistance"]


def _atr_safe(atr: float) -> float:
    return atr if atr > 0 else 1e-9


@dataclass(frozen=True)
class Level:
    """One method's price proposal, tagged for convergence clustering."""

    price: float
    method: str
    weight: float
    label: str = ""


@dataclass(frozen=True)
class Channel:
    price: float
    strength: float
    touches: int
    newest_age: int
    type: LevelSide
    is_recent: bool


@dataclass(frozen=True)
class FibLevel:
    price: float
    ratio: float
    label: str


@dataclass(frozen=True)
class AnchoredVWAPLevel:
    price: float
    anchor_idx: int


@dataclass(frozen=True)
class VolumeProfileLevel:
    price: float
    volume_pct: float


@dataclass(frozen=True)
class RoundLevel:
    price: float


@dataclass(frozen=True)
class ConvergenceCluster:
    price: float
    strength: int  # number of DISTINCT methods -- the headline read
    methods: int  # number of member levels (can exceed strength)
    total_weight: float
    type: LevelSide


def build_channels(
    pivots: Sequence[Pivot], last_close: float, atr: float
) -> list[Channel]:
    """Method 1 — horizontal S/R channels via greedy pivot anchoring."""
    half_band = max(atr * CHANNEL_ATR_MULT, last_close * CHANNEL_MIN_PCT)
    recent = [p for p in pivots if p.age <= SR_LOOKBACK_BARS]
    if not recent:
        return []
    ordered = sorted(recent, key=lambda p: p.weight, reverse=True)
    used: set[int] = set()
    atr_safe = _atr_safe(atr)
    channels: list[Channel] = []
    for anchor in ordered:
        if id(anchor) in used:
            continue
        touches = [
            p for p in recent if id(p) not in used and abs(p.price - anchor.price) <= half_band
        ]
        for p in touches:
            used.add(id(p))
        if len(touches) < CHANNEL_MIN_TOUCHES:
            continue
        avg_price = float(np.mean([p.price for p in touches]))
        dist_atr = abs(avg_price - last_close) / atr_safe
        dist_pct = abs(avg_price - last_close) / last_close if last_close > 0 else float("inf")
        if dist_atr > MAX_SR_DIST_ATR or dist_pct > MAX_SR_DIST_PCT:
            continue
        newest_age = min(p.age for p in touches)
        channels.append(
            Channel(
                price=avg_price,
                strength=float(sum(p.weight for p in touches)),
                touches=len(touches),
                newest_age=newest_age,
                type="support" if avg_price < last_close else "resistance",
                is_recent=newest_age <= RECENT_CHANNEL_MAX_AGE,
            )
        )
    channels.sort(key=lambda c: c.strength, reverse=True)
    return channels[:10]


def build_fibonacci_levels(
    high: np.ndarray, low: np.ndarray, lookback: int = FIB_LOOKBACK_BARS
) -> list[FibLevel]:
    """Method 3 — fibonacci retracements down from the recent swing high."""
    n = len(high)
    window = min(lookback, n)
    if window == 0:
        return []
    swing_high = float(np.max(high[-window:]))
    swing_low = float(np.min(low[-window:]))
    span = swing_high - swing_low
    if span <= 0:
        return []
    return [
        FibLevel(price=swing_high - span * ratio, ratio=ratio, label=f"{ratio * 100:.1f}% retrace")
        for ratio in FIB_LEVELS
    ]


def build_anchored_vwap(
    pivots: Sequence[Pivot],
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray,
    lookback: int = AVWAP_LOOKBACK_BARS,
    top_n: int = AVWAP_TOP_N,
) -> list[AnchoredVWAPLevel]:
    """Method 4 — VWAP anchored at each of the top_n most-extreme recent
    swing pivots, run forward to the last bar."""
    n = len(close)
    window = min(lookback, n)
    cutoff = n - window
    candidates = [p for p in pivots if p.idx >= cutoff]
    if not candidates:
        return []
    mid = (float(np.max(high[cutoff:])) + float(np.min(low[cutoff:]))) / 2.0
    ranked = sorted(candidates, key=lambda p: abs(p.price - mid), reverse=True)[:top_n]
    typical_price = (high + low + close) / 3.0
    results: list[AnchoredVWAPLevel] = []
    for anchor in ranked:
        vol_slice = volume[anchor.idx :]
        cum_vol = float(np.sum(vol_slice))
        if cum_vol == 0:
            continue
        tp_slice = typical_price[anchor.idx :]
        vwap = float(np.sum(tp_slice * vol_slice) / cum_vol)
        results.append(AnchoredVWAPLevel(price=vwap, anchor_idx=anchor.idx))
    return results


def build_volume_profile(
    close: np.ndarray,
    volume: np.ndarray,
    last_close: float,
    atr: float,
    bins: int = VP_BINS,
    threshold_pct: float = VP_HVN_THRESHOLD,
) -> list[VolumeProfileLevel]:
    """Method 5 — high-volume-node bins from a 40-bin volume-at-close
    histogram, kept only within MAX_SR_DIST_ATR of last_close."""
    price_min = float(np.min(close))
    price_max = float(np.max(close))
    if price_max <= price_min:
        return []
    edges = np.linspace(price_min, price_max, bins + 1)
    bin_idx = np.clip(np.digitize(close, edges) - 1, 0, bins - 1)
    bin_volume = np.zeros(bins)
    for i, b in enumerate(bin_idx):
        bin_volume[b] += volume[i]
    total_vol = float(np.sum(bin_volume))
    if total_vol == 0:
        return []
    threshold = float(np.percentile(bin_volume, threshold_pct * 100))
    atr_safe = _atr_safe(atr)
    results: list[VolumeProfileLevel] = []
    for b in range(bins):
        if bin_volume[b] < threshold:
            continue
        midpoint = float((edges[b] + edges[b + 1]) / 2.0)
        if abs(midpoint - last_close) / atr_safe > MAX_SR_DIST_ATR:
            continue
        results.append(VolumeProfileLevel(price=midpoint, volume_pct=bin_volume[b] / total_vol * 100))
    results.sort(key=lambda v: v.volume_pct, reverse=True)
    return results[:5]


def _round_step(last_close: float) -> float:
    if last_close > 500:
        return 50.0
    if last_close > 100:
        return 25.0
    if last_close > 50:
        return 10.0
    return 5.0


def build_round_levels(last_close: float, atr: float) -> list[RoundLevel]:
    """Method 6 — psychological round-number levels around last_close."""
    if last_close <= 0:
        return []
    step = _round_step(last_close)
    base = math.floor(last_close / step) * step
    atr_safe = _atr_safe(atr)
    results = []
    for mult in range(-3, 4):
        level = base + mult * step
        if level > 0 and abs(level - last_close) / atr_safe <= MAX_SR_DIST_ATR:
            results.append(RoundLevel(price=level))
    return results


def collect_all_levels(
    channels: Sequence[Channel],
    trendline_levels: Sequence[Level],
    fib_levels: Sequence[FibLevel],
    avwap_levels: Sequence[AnchoredVWAPLevel],
    vp_levels: Sequence[VolumeProfileLevel],
    round_levels: Sequence[RoundLevel],
) -> list[Level]:
    """Pool every method's output into one tagged, weighted list (Part 6.1).
    `trendline_levels` must already be tagged method="trendline",
    weight=r2 by the caller (see trendlines.py Family A)."""
    pool: list[Level] = []
    pool += [Level(price=c.price, method="channel", weight=c.strength) for c in channels]
    pool += list(trendline_levels)
    pool += [Level(price=f.price, method="fibonacci", weight=0.5, label=f.label) for f in fib_levels]
    pool += [Level(price=a.price, method="avwap", weight=0.7) for a in avwap_levels]
    pool += [
        Level(price=v.price, method="volume_profile", weight=v.volume_pct / 100) for v in vp_levels
    ]
    pool += [Level(price=r.price, method="round_number", weight=0.3) for r in round_levels]
    return pool


def build_convergence_clusters(
    pool: Sequence[Level], last_close: float, atr: float
) -> list[ConvergenceCluster]:
    """Part 6.2 — greedy price-ascending sweep merging levels within
    CLUSTER_ATR_MULT*ATR, keeping only clusters where >=2 DISTINCT methods
    agree. This convergence is the discriminating signal every downstream
    stop/target/trend read is built on."""
    if not pool or atr <= 0:
        return []
    band = atr * CLUSTER_ATR_MULT
    ordered = sorted(pool, key=lambda lv: lv.price)
    used = [False] * len(ordered)
    clusters: list[ConvergenceCluster] = []
    for i, anchor in enumerate(ordered):
        if used[i]:
            continue
        members = []
        for j, lv in enumerate(ordered):
            if not used[j] and abs(lv.price - anchor.price) <= band:
                members.append(lv)
                used[j] = True
        methods_set = {m.method for m in members}
        if len(methods_set) < MIN_CLUSTER_METHODS:
            continue
        price = float(np.mean([m.price for m in members]))
        clusters.append(
            ConvergenceCluster(
                price=price,
                strength=len(methods_set),
                methods=len(members),
                total_weight=float(sum(m.weight for m in members)),
                type="support" if price < last_close else "resistance",
            )
        )
    clusters.sort(key=lambda c: (c.strength, c.total_weight), reverse=True)
    return clusters[:10]
