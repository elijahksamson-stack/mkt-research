"""
crypto_analysis.py — single-file crypto risk:reward + relative-strength toolkit.

DATA IN  : a crypto ticker universe (defaults to BTC/ETH + 16 large-cap alts,
           yfinance `<SYMBOL>-USD` format) fetched live via yfinance.
DATA OUT : run(universe) returns one structured dict capturing every stage of
           processing (raw OHLCV-derived indicators, support/resistance levels,
           trendlines, trend-violation reads, stop/target R:R, HAC trend
           regressions, peer/benchmark leadership ranking, and the composite
           risk gauge) and prints an organized, fully-traceable interpretable
           report to stdout — no score in the printed output is implicit; the
           formula legend up top plus each line's breakdown terms let you
           reconstruct any number by hand.

This file is a single-file consolidation of the `crypto_structure/` package
(13 modules, 140 pytest tests — see that package's CLAUDE.md for the
module-by-module design rationale and the equity/macro sources each part
ports from). Every function here is identical to its package counterpart;
only cross-module imports were removed (single namespace) and one name
collision was resolved (`MIN_BARS` meant two different things in two source
modules -- the fetch-side one is renamed FETCH_MIN_BARS below). Keep the
package as the source of truth for tests/maintenance; treat this file as the
portable, paste-anywhere deliverable.

Sections below, in pipeline order:
  INPUT                         — external deps, editable config, ticker universe
  PROCESSING — DATA ACQUISITION — yfinance OHLCV fetch + quality/liquidity gate
  PROCESSING — INDICATORS       — ATR, realized vol, relative volume, pivots
  PROCESSING — LEVELS           — 6 independent S/R methods + convergence clustering
  PROCESSING — TRENDLINES       — quantile-regression + pivot-pair trendline families
  PROCESSING — TREND VIOLATION  — rising-support-line undercut detection
  PROCESSING — FIB EXTENSION    — ATH/no-overhead reward projection
  PROCESSING — STOP/TARGET      — 4-tier stop/target R:R derivation
  PROCESSING — RISK:REWARD      — per-asset orchestration (analyze())
  PROCESSING — TREND REGRESSION — HAC log-regression trend + opportunity model
  PROCESSING — RELATIVE STRENGTH— peer/benchmark leadership + opportunity ranking
  PROCESSING — RISK GAUGE       — cross-asset composite risk score
  OUTPUT                        — report assembly, interpretable rendering, run()
"""
from __future__ import annotations

# =============================================================================
# INPUT
# =============================================================================
import contextlib
import io
import logging
import math
import time
import warnings
from dataclasses import dataclass
from typing import Literal, Optional, Sequence

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import linprog

warnings.filterwarnings("ignore", category=FutureWarning)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

# --- Ticker universe -- MAJORS are BTC/ETH (the market-defining tier and the
# benchmark for relative-strength ranking, playing the role SPY plays for
# equities); ALTCOINS add breadth, weighted lower so one alt's move doesn't
# swing the headline gauge as much as BTC/ETH do. Edit freely -- any dict of
# yfinance `<SYMBOL>-USD` tickers works with every function below.
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
    """Per-ticker weight in the overall gauge. Splits MAJORS_WEIGHT_TOTAL
    evenly across whichever MAJORS are present and ALTCOINS_WEIGHT_TOTAL
    evenly across whichever ALTCOINS are present, renormalized so a trimmed
    or fully custom universe still sums to 1.0."""
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


# =============================================================================
# PROCESSING — DATA ACQUISITION (yfinance OHLCV + quality/liquidity gate)
# =============================================================================
DEFAULT_PERIOD = "3y"
FETCH_MIN_BARS = 220  # comfortably above TREND_LOOKBACK_BARS=200 below, while admitting newer large-cap alts (e.g. APT, ARB, OP)
MIN_COVERAGE = 0.95
MAX_STALENESS_DAYS = 3  # crypto trades every calendar day -- no weekend/holiday gap to allow for
MIN_MEDIAN_DOLLAR_VOLUME = 5_000_000.0
DOWNLOAD_RETRIES = 3
DOWNLOAD_CHUNK = 20

REQUIRED_COLUMNS = ("Open", "High", "Low", "Close", "Volume")


@dataclass(frozen=True)
class OHLCV:
    ticker: str
    dates: pd.DatetimeIndex
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    volume: np.ndarray


def quality_gate(df: pd.DataFrame, as_of: Optional[pd.Timestamp] = None) -> tuple[bool, str, dict]:
    """Gate an OHLCV frame on bar count, coverage, staleness, and liquidity
    before it's trusted for risk_reward analysis. Pure function -- no
    network -- so it is fully unit-testable offline."""
    if df is None or df.empty or "Close" not in df:
        return False, "no price data", {}
    coverage = float(df["Close"].tail(FETCH_MIN_BARS).notna().mean())
    clean = df.dropna(subset=[c for c in REQUIRED_COLUMNS if c in df])
    clean = clean[clean["Close"] > 0]
    bars = len(clean)
    if bars == 0:
        return False, "no valid bars", {}
    latest = pd.Timestamp(clean.index[-1]).tz_localize(None)
    if as_of is not None:
        as_of = pd.Timestamp(as_of).tz_localize(None)
        staleness = (as_of - latest).days
        if staleness > MAX_STALENESS_DAYS:
            return False, f"stale by {staleness} days", {"bars": bars}
    if bars < FETCH_MIN_BARS:
        return False, f"{bars} bars < {FETCH_MIN_BARS}", {"bars": bars}
    if coverage < MIN_COVERAGE:
        return (
            False,
            f"{coverage:.1%} coverage < {MIN_COVERAGE:.0%}",
            {"bars": bars, "coverage": coverage},
        )
    volume = clean["Volume"] if "Volume" in clean else pd.Series(0.0, index=clean.index)
    median_dollar_volume = float((clean["Close"] * volume).tail(63).median())
    if median_dollar_volume < MIN_MEDIAN_DOLLAR_VOLUME:
        return (
            False,
            f"median dollar volume {median_dollar_volume:,.0f} < {MIN_MEDIAN_DOLLAR_VOLUME:,.0f}",
            {"bars": bars, "coverage": coverage, "median_dollar_volume": median_dollar_volume},
        )
    return (
        True,
        "",
        {"bars": bars, "coverage": coverage, "median_dollar_volume": median_dollar_volume, "latest": latest},
    )


def _download(ticker: str, period: str) -> pd.DataFrame:
    raw = pd.DataFrame()
    for attempt in range(DOWNLOAD_RETRIES):
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                raw = yf.download(
                    ticker, period=period, interval="1d", auto_adjust=True, progress=False, timeout=25
                )
            if not raw.empty:
                break
        except Exception:
            pass
        if attempt < DOWNLOAD_RETRIES - 1:
            time.sleep(2**attempt)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    return raw


def fetch_ohlcv(ticker: str, period: str = DEFAULT_PERIOD) -> OHLCV:
    """Download `ticker`'s daily OHLCV and run it through the quality gate.
    Raises RuntimeError if no data is returned or the gate rejects it."""
    raw = _download(ticker, period)
    valid, reason, _ = quality_gate(raw)
    if not valid:
        raise RuntimeError(f"{ticker}: failed quality gate — {reason}")
    clean = raw.dropna(subset=[c for c in REQUIRED_COLUMNS if c in raw])
    clean = clean[clean["Close"] > 0]
    return OHLCV(
        ticker=ticker,
        dates=clean.index,
        high=clean["High"].to_numpy(dtype=float),
        low=clean["Low"].to_numpy(dtype=float),
        close=clean["Close"].to_numpy(dtype=float),
        volume=clean["Volume"].to_numpy(dtype=float),
    )


def _extract_frames(raw: pd.DataFrame, tickers: list[str]) -> dict[str, pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        try:
            if isinstance(raw.columns, pd.MultiIndex):
                if ticker in raw.columns.get_level_values(0):
                    frame = raw[ticker].copy()
                elif ticker in raw.columns.get_level_values(1):
                    frame = raw.xs(ticker, axis=1, level=1).copy()
                else:
                    continue
            else:
                frame = raw.copy() if len(tickers) == 1 else pd.DataFrame()
            frame.columns = [str(c).title() for c in frame.columns]
            frame = frame.reindex(columns=list(REQUIRED_COLUMNS))
            frames[ticker] = frame.replace([np.inf, -np.inf], np.nan)
        except Exception:
            pass
    return frames


def _download_batch(tickers: list[str], period: str) -> pd.DataFrame:
    raw = pd.DataFrame()
    for attempt in range(DOWNLOAD_RETRIES):
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                raw = yf.download(
                    tickers,
                    period=period,
                    interval="1d",
                    auto_adjust=True,
                    group_by="ticker",
                    threads=min(8, len(tickers)),
                    progress=False,
                    timeout=25,
                )
            if not raw.empty:
                break
        except Exception:
            pass
        if attempt < DOWNLOAD_RETRIES - 1:
            time.sleep(2**attempt)
    return raw


def download_universe(tickers: list[str], period: str = DEFAULT_PERIOD) -> tuple[dict[str, OHLCV], list[dict]]:
    """Fetch + quality-gate every ticker in `tickers` with one batched
    yfinance call per DOWNLOAD_CHUNK tickers, isolating any single ticker's
    failure into `dropped` rather than aborting the whole batch. Returns
    (ohlcv_by_ticker, dropped)."""
    tickers = list(dict.fromkeys(t.upper().strip() for t in tickers if t.strip()))
    results: dict[str, OHLCV] = {}
    dropped: list[dict] = []
    for start in range(0, len(tickers), DOWNLOAD_CHUNK):
        chunk = tickers[start : start + DOWNLOAD_CHUNK]
        raw = _download_batch(chunk, period)
        frames = _extract_frames(raw, chunk) if not raw.empty else {}
        for ticker in chunk:
            frame = frames.get(ticker)
            if frame is None or frame.empty:
                dropped.append({"ticker": ticker, "reason": "no price data"})
                continue
            valid, reason, _ = quality_gate(frame)
            if not valid:
                dropped.append({"ticker": ticker, "reason": reason})
                continue
            clean = frame.dropna(subset=[c for c in REQUIRED_COLUMNS if c in frame])
            clean = clean[clean["Close"] > 0]
            results[ticker] = OHLCV(
                ticker=ticker,
                dates=clean.index,
                high=clean["High"].to_numpy(dtype=float),
                low=clean["Low"].to_numpy(dtype=float),
                close=clean["Close"].to_numpy(dtype=float),
                volume=clean["Volume"].to_numpy(dtype=float),
            )
    return results, dropped


# =============================================================================
# PROCESSING — INDICATORS + PIVOT DETECTION
# =============================================================================
ATR_PERIOD = 14
VOL_PERIOD = 20
RVOL_PERIOD = 20
HV_CLIP = (0.005, 0.08)
PIVOT_WINDOW = 5
PIVOT_HALFLIFE_BARS = 60
MIN_BARS = 60  # analyze()'s minimum bar count -- distinct from FETCH_MIN_BARS (the fetch-quality floor) above


class InsufficientDataError(ValueError):
    """Fewer than MIN_BARS bars are available — nothing downstream can run."""


def require_min_bars(n: int, minimum: int = MIN_BARS) -> None:
    if n < minimum:
        raise InsufficientDataError(f"{n} bars < minimum {minimum}")


def average_true_range(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = ATR_PERIOD) -> float:
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


def find_local_extrema(high: np.ndarray, low: np.ndarray, window: int = PIVOT_WINDOW) -> tuple[list[int], list[int]]:
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
    high: np.ndarray, low: np.ndarray, window: int = PIVOT_WINDOW, halflife: int = PIVOT_HALFLIFE_BARS
) -> list[Pivot]:
    """Recency-weighted pivot list, sorted by bar index ascending. Weight
    decays exponentially with age (bars since the pivot), halving every
    `halflife` bars."""
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


# =============================================================================
# PROCESSING — SIX LEVEL-DETECTION METHODS + CONVERGENCE CLUSTERING
# =============================================================================
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


def build_channels(pivots: Sequence[Pivot], last_close: float, atr: float) -> list[Channel]:
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
        touches = [p for p in recent if id(p) not in used and abs(p.price - anchor.price) <= half_band]
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


def build_fibonacci_levels(high: np.ndarray, low: np.ndarray, lookback: int = FIB_LOOKBACK_BARS) -> list[FibLevel]:
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
    """Pool every method's output into one tagged, weighted list.
    `trendline_levels` must already be tagged method="trendline",
    weight=r2 by the caller (see regression_trendlines_as_levels below)."""
    pool: list[Level] = []
    pool += [Level(price=c.price, method="channel", weight=c.strength) for c in channels]
    pool += list(trendline_levels)
    pool += [Level(price=f.price, method="fibonacci", weight=0.5, label=f.label) for f in fib_levels]
    pool += [Level(price=a.price, method="avwap", weight=0.7) for a in avwap_levels]
    pool += [Level(price=v.price, method="volume_profile", weight=v.volume_pct / 100) for v in vp_levels]
    pool += [Level(price=r.price, method="round_number", weight=0.3) for r in round_levels]
    return pool


def build_convergence_clusters(pool: Sequence[Level], last_close: float, atr: float) -> list[ConvergenceCluster]:
    """Greedy price-ascending sweep merging levels within
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


# =============================================================================
# PROCESSING — TRENDLINE DISCOVERY (quantile-regression + pivot-pair families)
# =============================================================================
TREND_LOOKBACK_BARS = 200
MIN_PIVOTS_FOR_TREND = 4
R2_MIN = 0.55
CHANNEL_ATR_MULT_TREND = 1.25

PAIR_MAX_VIOLATION_PCT = 0.12
PAIR_MIN_TOUCHES = 2
PAIR_MAX_LINES = 12

LineSide = Literal["upper", "lower"]


@dataclass(frozen=True)
class RegressionTrendline:
    """Family A — one line, GLOBAL over the lookback window."""

    type: LineSide
    slope: float
    intercept: float
    r2: float
    start_price: float
    end_price: float  # value at the LAST bar of the full series
    channel_width: float


@dataclass(frozen=True)
class TrendlineSegment:
    """Family B — one segment-specific line anchored between two pivots,
    extended forward to the last bar."""

    type: LineSide
    start_idx: int
    end_idx: int  # the later anchor pivot's index
    start_price: float
    end_price: float  # value extended to the LAST bar of the full series
    slope: float
    score: float  # touch/span/violation quality
    span: int


def _quantile_regression(x: np.ndarray, y: np.ndarray, tau: float) -> Optional[tuple[float, float]]:
    """Fit y ~ slope*x + intercept minimizing the tilted (pinball) loss for
    quantile tau, via linear programming. tau=0.95 hugs the tops of the
    points (robust resistance fit); tau=0.05 hugs the bottoms (support)."""
    n = len(x)
    if n < 4:
        return None
    c = np.concatenate([[0.0, 0.0], np.full(n, tau), np.full(n, 1 - tau)])
    X = np.column_stack([x, np.ones(n)])
    A_eq = np.hstack([X, np.eye(n), -np.eye(n)])
    bounds = [(None, None), (None, None)] + [(0, None)] * (2 * n)
    result = linprog(c, A_eq=A_eq, b_eq=y, bounds=bounds, method="highs")
    if not result.success:
        return None
    return float(result.x[0]), float(result.x[1])


def _r_squared(y: np.ndarray, y_fit: np.ndarray) -> float:
    ss_res = float(np.sum((y - y_fit) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    return 1 - ss_res / ss_tot if ss_tot > 0 else 0.0


def _regression_line(
    pivots: Sequence[Pivot], side: LineSide, tau: float, start_idx: int, window: int, atr: float
) -> Optional[RegressionTrendline]:
    matched = [p for p in pivots if p.type == ("high" if side == "upper" else "low") and p.idx >= start_idx]
    if len(matched) < MIN_PIVOTS_FOR_TREND:
        return None
    x = np.array([p.idx - start_idx for p in matched], dtype=float)
    y = np.array([p.price for p in matched], dtype=float)
    fit = _quantile_regression(x, y, tau)
    if fit is None:
        return None
    slope, intercept = fit
    r2 = _r_squared(y, slope * x + intercept)
    if r2 < R2_MIN:
        return None
    return RegressionTrendline(
        type=side,
        slope=slope,
        intercept=intercept,
        r2=r2,
        start_price=intercept,
        end_price=slope * (window - 1) + intercept,
        channel_width=atr * CHANNEL_ATR_MULT_TREND,
    )


def build_regression_trendlines(
    pivots: Sequence[Pivot], n: int, atr: float, lookback: int = TREND_LOOKBACK_BARS
) -> list[RegressionTrendline]:
    """Family A — at most one upper + one lower GLOBAL trendline."""
    window = min(lookback, n)
    start_idx = n - window
    lines = []
    upper = _regression_line(pivots, "upper", 0.95, start_idx, window, atr)
    if upper is not None:
        lines.append(upper)
    lower = _regression_line(pivots, "lower", 0.05, start_idx, window, atr)
    if lower is not None:
        lines.append(lower)
    return lines


def regression_trendlines_as_levels(trendlines: Sequence[RegressionTrendline]) -> list[Level]:
    """Family A end_prices feed the convergence-cluster pool, weighted by
    the line's own R^2."""
    return [Level(price=t.end_price, method="trendline", weight=t.r2) for t in trendlines]


def _adaptive_pair_params(n: int, atr: float) -> tuple[int, int, float]:
    swing_w = max(8, min(n // 40, 15))
    min_span = max(15, n // 25)
    touch_band = atr * 0.6
    return swing_w, min_span, touch_band


def _pair_lines(
    indices: Sequence[int],
    prices: np.ndarray,
    n: int,
    min_span: int,
    touch_band: float,
    max_violation_pct: float,
    min_touches: int,
    line_type: LineSide,
) -> list[TrendlineSegment]:
    lines: list[TrendlineSegment] = []
    for a in range(len(indices)):
        idx_a = indices[a]
        price_a = float(prices[idx_a])
        for b in range(a + 1, len(indices)):
            idx_b = indices[b]
            span = idx_b - idx_a
            if span < min_span:
                continue
            price_b = float(prices[idx_b])
            slope = (price_b - price_a) / span
            offsets = np.arange(span + 1, dtype=float)
            line_vals = price_a + slope * offsets
            segment = prices[idx_a : idx_b + 1]
            if line_type == "upper":
                dists = segment - line_vals  # + means bar poked above resistance
            else:
                dists = line_vals - segment  # + means bar broke below support
            violations = int(np.sum(dists > touch_band))
            touches = int(np.sum(np.abs(dists) <= touch_band))
            total = span + 1
            if violations / total > max_violation_pct or touches < min_touches:
                continue
            end_price = price_a + slope * (n - 1 - idx_a)
            score = (touches**1.5) * (span**0.5) / (1 + violations * 3)
            lines.append(
                TrendlineSegment(
                    type=line_type,
                    start_idx=idx_a,
                    end_idx=idx_b,
                    start_price=price_a,
                    end_price=end_price,
                    slope=slope,
                    score=score,
                    span=span,
                )
            )
    return lines


def _dedup_pair_lines(lines: list[TrendlineSegment], atr: float) -> list[TrendlineSegment]:
    """Assumes `lines` is already sorted by score descending, so the first
    line encountered in a near-duplicate group is the one kept."""
    kept: list[TrendlineSegment] = []
    for line in lines:
        duplicate = any(
            k.type == line.type
            and abs(k.slope - line.slope) < atr * 0.003
            and abs(k.end_price - line.end_price) < atr * 1.2
            for k in kept
        )
        if not duplicate:
            kept.append(line)
    return kept


def build_pivot_pair_trendlines(
    high: np.ndarray,
    low: np.ndarray,
    atr: float,
    max_violation_pct: float = PAIR_MAX_VIOLATION_PCT,
    min_touches: int = PAIR_MIN_TOUCHES,
    max_lines: Optional[int] = PAIR_MAX_LINES,
) -> list[TrendlineSegment]:
    """Family B — segment-specific lines after ranking + dedup, capped at
    `max_lines`. Pass max_lines=None (or a larger number) to see the full
    ranked candidate pool -- the score formula can rank an old, high-touch,
    near-flat segment above a genuinely recent, cleaner ascending line, so
    a caller that specifically needs "the most relevant RECENT line"
    (detect_trend_violation below) should not rely on the top-12-only view."""
    n = len(high)
    swing_w, min_span, touch_band = _adaptive_pair_params(n, atr)
    high_idx, low_idx = find_local_extrema(high, low, window=swing_w)
    lines = _pair_lines(high_idx, high, n, min_span, touch_band, max_violation_pct, min_touches, "upper")
    lines += _pair_lines(low_idx, low, n, min_span, touch_band, max_violation_pct, min_touches, "lower")
    lines.sort(key=lambda l: l.score, reverse=True)
    deduped = _dedup_pair_lines(lines, atr)
    return deduped if max_lines is None else deduped[:max_lines]


# =============================================================================
# PROCESSING — TREND VIOLATION (rising-support-line undercut detection)
# =============================================================================
# A line anchored further back than this is stale -- not "the" current
# uptrend line a chart-watcher would still be tracking.
RELEVANCE_LOOKBACK_BARS = 252

# Same proximity convention as MAX_SR_DIST_ATR above: a line that isn't
# even near price isn't structurally "in play" right now.
MAX_LINE_DIST_ATR = 8.0

# build_pivot_pair_trendlines' default cap (12) serves the chart-overlay /
# tier-2-target use case, where the score formula can favor an old,
# high-touch, near-flat segment over a genuinely recent, cleaner ascending
# line -- so recomputing with a much larger pool here (instead of reusing a
# capped list) is what makes this detector actually find "the most
# relevant RECENT support line."
CANDIDATE_POOL_SIZE = 60

TrendStatus = Literal["intact", "undercut", "no_active_trendline"]


@dataclass(frozen=True)
class TrendViolation:
    status: TrendStatus
    trendline: Optional[TrendlineSegment]
    # (line_value_at_last_bar - last_close) / ATR. Positive means the close
    # sits below the line (an undercut); zero or negative means it holds
    # above it (intact).
    breach_atr: float
    # Consecutive most-recent bars closed below the line, or None if intact
    # / no active trendline.
    bars_since_break: Optional[int]


def _line_value_at(line: TrendlineSegment, idx: int) -> float:
    return line.start_price + line.slope * (idx - line.start_idx)


def _select_active_support_line(
    lines: Sequence[TrendlineSegment], n: int, last_close: float, atr: float
) -> Optional[TrendlineSegment]:
    """The rising support line a discretionary trader would actually be
    watching right now: an ascending (positive-slope) Family-B support
    line, anchored recently enough to still be "the" current trend, close
    enough to price to be structurally relevant.

    Selection is NOT simply "highest quality score": the score formula
    rewards long-running, heavily-touched channels, which tends to pick a
    broad multi-quarter channel that's still comfortably intact over the
    tighter, more recent higher-low line that just got undercut -- exactly
    backwards for a detector whose job is to catch a fresh break. So: if
    any eligible line is currently violated, prefer the most recently
    anchored VIOLATED one (the break someone is actually reacting to right
    now); only fall back to the highest-scoring line when nothing is
    currently broken.
    """
    atr_safe = atr if atr > 0 else 1e-9
    candidates = [
        line
        for line in lines
        if line.type == "lower"
        and line.slope > 0
        and (n - 1 - line.end_idx) <= RELEVANCE_LOOKBACK_BARS
        and abs(line.end_price - last_close) / atr_safe <= MAX_LINE_DIST_ATR
    ]
    if not candidates:
        return None
    violated = [line for line in candidates if _line_value_at(line, n - 1) > last_close]
    if violated:
        return max(violated, key=lambda line: (line.end_idx, line.score))
    return max(candidates, key=lambda line: line.score)


def detect_trend_violation(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    atr: float,
    pivot_pair_lines: Optional[Sequence[TrendlineSegment]] = None,
) -> TrendViolation:
    """Is the current close undercutting the most relevant rising support
    trendline, and if so, for how long has it been broken?"""
    n = len(close)
    last_close = float(close[-1])
    lines = (
        pivot_pair_lines
        if pivot_pair_lines is not None
        else build_pivot_pair_trendlines(high, low, atr, max_lines=CANDIDATE_POOL_SIZE)
    )
    line = _select_active_support_line(lines, n, last_close, atr)
    if line is None:
        return TrendViolation(status="no_active_trendline", trendline=None, breach_atr=0.0, bars_since_break=None)

    atr_safe = atr if atr > 0 else 1e-9
    breach_atr = (_line_value_at(line, n - 1) - last_close) / atr_safe

    if breach_atr <= 0:
        return TrendViolation(status="intact", trendline=line, breach_atr=breach_atr, bars_since_break=None)

    # Walk backward from the last bar, counting the consecutive run of
    # closes below the extended line, to distinguish a fresh single-bar
    # undercut from a sustained breakdown.
    streak = 0
    floor_idx = max(line.start_idx, n - 1 - RELEVANCE_LOOKBACK_BARS)
    for idx in range(n - 1, floor_idx - 1, -1):
        if close[idx] < _line_value_at(line, idx):
            streak += 1
        else:
            break
    return TrendViolation(status="undercut", trendline=line, breach_atr=breach_atr, bars_since_break=streak)


# =============================================================================
# PROCESSING — FIBONACCI EXTENSION TARGETS (ATH / no-overhead reward)
# =============================================================================
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


# =============================================================================
# PROCESSING — STOP/TARGET (4-tier R:R derivation)
# =============================================================================
STOP_ATR_MULT = 0.5
TARGET_ATR_MULT = 0.5
RR_TARGET = 2.0
MIN_TARGET_ATR = 1.25
MAX_STOP_ATR = 3.0
MAX_STOP_PCT = 0.08
VOL_FACTOR_CLIP = (0.75, 2.25)

TargetSource = Literal["cluster", "trendline", "fib_extension", "synthetic"]


@dataclass(frozen=True)
class StopTarget:
    stop: float
    target: float
    risk: float
    reward: float
    risk_pct: float
    reward_pct: float
    rr_ratio: float
    stop_cluster: Optional[float]
    target_cluster: Optional[float]
    vol_factor: float
    target_source: TargetSource
    target_fib_ratio: Optional[float]


def _vol_factor(hv: float) -> float:
    lo, hi = VOL_FACTOR_CLIP
    return float(min(max(hv / 0.02, lo), hi))


def _split_clusters(
    clusters: Sequence[ConvergenceCluster], last_close: float
) -> tuple[list[ConvergenceCluster], list[ConvergenceCluster]]:
    supports = sorted((c for c in clusters if c.price < last_close), key=lambda c: c.price, reverse=True)
    resistances = sorted((c for c in clusters if c.price >= last_close), key=lambda c: c.price)
    return supports, resistances


def _compute_stop(
    supports: Sequence[ConvergenceCluster], last_close: float, atr: float, vol_factor: float
) -> tuple[float, Optional[float]]:
    if supports:
        stop_cluster = supports[0].price
        raw_stop = stop_cluster - atr * STOP_ATR_MULT * vol_factor
    else:
        stop_cluster = None
        raw_stop = last_close * (1 - MAX_STOP_PCT)
    max_stop = last_close - atr * MAX_STOP_ATR
    pct_stop = last_close * (1 - MAX_STOP_PCT)
    # The tightest (highest) of the three candidates wins -- the stop can
    # never sit further than MAX_STOP_ATR/MAX_STOP_PCT below price.
    return max(raw_stop, max_stop, pct_stop), stop_cluster


def _upper_trendline_endpoints(
    regression_trendlines: Sequence[RegressionTrendline],
    pivot_pair_lines: Sequence[TrendlineSegment],
    last_close: float,
) -> list[float]:
    endpoints = [t.end_price for t in regression_trendlines if t.type == "upper" and t.end_price > last_close]
    endpoints += [t.end_price for t in pivot_pair_lines if t.type == "upper" and t.end_price > last_close]
    return endpoints


def _compute_target(
    resistances: Sequence[ConvergenceCluster],
    regression_trendlines: Sequence[RegressionTrendline],
    pivot_pair_lines: Sequence[TrendlineSegment],
    fib_extension: Optional[FibExtension],
    last_close: float,
    atr: float,
    vol_factor: float,
    stop: float,
) -> tuple[float, Optional[float], TargetSource, Optional[float]]:
    if resistances:
        target_cluster = resistances[0].price
        raw_target = target_cluster + atr * TARGET_ATR_MULT * vol_factor
        return raw_target, target_cluster, "cluster", None

    endpoints = _upper_trendline_endpoints(regression_trendlines, pivot_pair_lines, last_close)
    if endpoints:
        raw_target = min(endpoints) + atr * TARGET_ATR_MULT * vol_factor
        return raw_target, None, "trendline", None

    if fib_extension is not None:
        above = [lv for lv in fib_extension.levels if lv.price > last_close]
        if above:
            nearest = min(above, key=lambda lv: lv.price)
            # Tier 3 intentionally does NOT add an ATR pad -- the projected
            # level IS the target (the floor below may still bump it up).
            return nearest.price, None, "fib_extension", nearest.ratio

    risk_for_synth = last_close - stop
    raw_target = last_close + risk_for_synth * RR_TARGET
    return raw_target, None, "synthetic", None


def compute_stop_target(
    clusters: Sequence[ConvergenceCluster],
    regression_trendlines: Sequence[RegressionTrendline],
    pivot_pair_lines: Sequence[TrendlineSegment],
    fib_extension: Optional[FibExtension],
    last_close: float,
    atr: float,
    hv: float,
) -> StopTarget:
    vol_factor = _vol_factor(hv)
    supports, resistances = _split_clusters(clusters, last_close)
    stop, stop_cluster = _compute_stop(supports, last_close, atr, vol_factor)
    raw_target, target_cluster, target_source, target_fib_ratio = _compute_target(
        resistances, regression_trendlines, pivot_pair_lines, fib_extension, last_close, atr, vol_factor, stop
    )
    min_target = last_close + atr * MIN_TARGET_ATR
    target = max(raw_target, min_target)

    risk = last_close - stop
    reward = target - last_close
    rr_ratio = reward / risk if risk > 0 else 0.0

    return StopTarget(
        stop=stop,
        target=target,
        risk=risk,
        reward=reward,
        risk_pct=risk / last_close * 100 if last_close else 0.0,
        reward_pct=reward / last_close * 100 if last_close else 0.0,
        rr_ratio=rr_ratio,
        stop_cluster=stop_cluster,
        target_cluster=target_cluster,
        vol_factor=vol_factor,
        target_source=target_source,
        target_fib_ratio=target_fib_ratio,
    )


# =============================================================================
# PROCESSING — PER-ASSET RISK:REWARD ORCHESTRATION
# =============================================================================
@dataclass(frozen=True)
class RiskRewardReport:
    ticker: str
    last_close: float
    atr: float
    hv: float
    rvol: float
    clusters: list[ConvergenceCluster]
    regression_trendlines: list[RegressionTrendline]
    pivot_pair_lines: list[TrendlineSegment]
    fib_extension: Optional[FibExtension]
    stop_target: StopTarget
    trend_violation: TrendViolation


def analyze(ticker: str, high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray) -> RiskRewardReport:
    """Run the full per-asset pipeline for one crypto asset: indicators ->
    pivots -> six level-detection methods -> convergence clusters -> both
    trendline families -> fib extension -> stop/target tiering -> trend
    violation. Raises InsufficientDataError below 60 bars. This is the
    function that answers "RR on all crypto assets" -- call it once per
    ticker in the universe."""
    n = len(close)
    require_min_bars(n)

    last_close = float(close[-1])
    atr = average_true_range(high, low, close)
    hv = realized_volatility(close)
    rvol = relative_volume(volume)

    pivots = build_pivots(high, low)

    channels = build_channels(pivots, last_close, atr)
    regression_trendlines = build_regression_trendlines(pivots, n, atr)
    fib_levels = build_fibonacci_levels(high, low)
    avwap_levels = build_anchored_vwap(pivots, high, low, close, volume)
    vp_levels = build_volume_profile(close, volume, last_close, atr)
    round_levels = build_round_levels(last_close, atr)

    pool = collect_all_levels(
        channels,
        regression_trendlines_as_levels(regression_trendlines),
        fib_levels,
        avwap_levels,
        vp_levels,
        round_levels,
    )
    clusters = build_convergence_clusters(pool, last_close, atr)

    pivot_pair_lines = build_pivot_pair_trendlines(high, low, atr)
    fib_ext = build_fib_extension(pivots, n, last_close)

    stop_target = compute_stop_target(
        clusters, regression_trendlines, pivot_pair_lines, fib_ext, last_close, atr, hv
    )
    # Deliberately NOT passing pivot_pair_lines here -- that list is capped
    # for the tier-2-target/chart use case above and can crowd out the
    # recent line the violation detector specifically needs.
    trend_violation = detect_trend_violation(high, low, close, atr)

    return RiskRewardReport(
        ticker=ticker,
        last_close=last_close,
        atr=atr,
        hv=hv,
        rvol=rvol,
        clusters=clusters,
        regression_trendlines=regression_trendlines,
        pivot_pair_lines=pivot_pair_lines,
        fib_extension=fib_ext,
        stop_target=stop_target,
        trend_violation=trend_violation,
    )


# =============================================================================
# PROCESSING — TREND REGRESSION (HAC log-regression trend + opportunity)
# =============================================================================
# Crypto trades every calendar day, not ~252 trading days/year like
# equities, so window lengths are calendar-day equivalents (30/91/182/365
# for ~1mo/3mo/6mo/1yr) and annualization uses PERIODS_PER_YEAR=365 instead
# of 252 -- using 252 here would understate annualized growth by roughly
# 31% because it would treat 365 real days of drift as if they were only
# 252 trading days' worth.
PERIODS_PER_YEAR = 365
DEFAULT_WINDOWS = (30, 91, 182, 365)
DEFAULT_WEIGHTS = {30: 0.18, 91: 0.32, 182: 0.30, 365: 0.20}
OPPORTUNITY_WINDOWS = ((91, 0.45), (182, 0.35), (365, 0.20))
CHANNEL_SIGMA = 2.0
FORECAST_DAYS = 21


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


def hac_log_regression(series: pd.Series, window: int, forecast_days: int = FORECAST_DAYS) -> Optional[dict]:
    """HAC (Newey-West) corrected log-linear trend regression over the last
    `window` observations of `series`. Works on any strictly-positive
    series -- a raw close series (absolute trend) or a ratio series like
    BTC-USD/ETH-USD (relative strength, see rank_universe below). Returns
    None when fewer than max(18, 0.75*window) valid positive observations
    are available to fit against."""
    values = pd.Series(series).dropna().astype(float)
    values = values[values > 0].tail(window)
    n = len(values)
    if n < max(18, int(window * 0.75)):
        return None

    y = np.log(values.to_numpy())
    x = np.arange(n, dtype=float)
    X = np.column_stack([np.ones(n), x])
    inv_xx = np.linalg.pinv(X.T @ X)
    beta_vec = inv_xx @ X.T @ y
    fitted = X @ beta_vec
    resid = y - fitted
    sse = float(resid @ resid)
    sst = float((y - y.mean()) @ (y - y.mean()))
    r2 = 1 - sse / sst if sst > 0 else 0.0

    # Newey-West/HAC slope uncertainty corrects for serially correlated
    # trend residuals (crypto series are heavily autocorrelated day to day).
    lag = max(1, int(4 * (n / 100) ** (2 / 9)))
    meat = np.zeros((2, 2))
    for t in range(n):
        xt = X[t][:, None]
        meat += resid[t] ** 2 * (xt @ xt.T)
    for j in range(1, lag + 1):
        weight = 1 - j / (lag + 1)
        for t in range(j, n):
            xt, xlag = X[t][:, None], X[t - j][:, None]
            meat += weight * resid[t] * resid[t - j] * (xt @ xlag.T + xlag @ xt.T)
    cov = inv_xx @ meat @ inv_xx
    slope = float(beta_vec[1])
    slope_se = float(np.sqrt(max(cov[1, 1], 1e-18)))
    t_hac = slope / slope_se if slope_se > 0 else 0.0
    sigma = float(np.sqrt(sse / max(n - 2, 1)))
    current_resid = float(resid[-1])
    z = current_resid / sigma if sigma > 1e-12 else 0.0

    # AR(1) residual persistence drives a regression-only forward forecast.
    denom = float(resid[:-1] @ resid[:-1])
    phi = float(np.clip((resid[:-1] @ resid[1:]) / denom, -0.99, 0.99)) if denom > 1e-18 else 0.0
    expected_resid = (phi**forecast_days) * current_resid
    forecast_log_return = slope * forecast_days + expected_resid - current_resid
    upper_distance = max(CHANNEL_SIGMA * sigma - current_resid, 0.0)
    lower_distance = max(CHANNEL_SIGMA * sigma + current_resid, sigma * 0.05)
    channel_rr = upper_distance / lower_distance

    return {
        "window": window,
        "slope_daily": slope,
        "slope_annual": float(np.expm1(np.clip(slope * PERIODS_PER_YEAR, -5, 5))),
        "r2": float(np.clip(r2, 0, 1)),
        "t_hac": float(t_hac),
        "residual_sigma": sigma,
        "residual_z": float(z),
        "residual_phi": phi,
        "forecast_return": float(np.expm1(np.clip(forecast_log_return, -2, 2))),
        "channel_rr": float(channel_rr),
    }


def _opportunity_component(stat: dict) -> float:
    sigma = max(stat["residual_sigma"], 1e-9)
    forecast_score = sigmoid(1.35 * np.log1p(stat["forecast_return"]) / sigma)
    asymmetry_score = stat["channel_rr"] / (1 + stat["channel_rr"])
    entry_score = np.exp(-0.5 * ((stat["residual_z"] + 0.35) / 0.90) ** 2)
    confidence = min(abs(stat["t_hac"]) / 4.0, 1.0) * np.sqrt(stat["r2"])
    trend_gate = 0.45 + 0.55 * sigmoid(stat["t_hac"] / 2.0)
    return trend_gate * (
        0.38 * forecast_score + 0.32 * asymmetry_score + 0.20 * entry_score + 0.10 * confidence
    )


def trend_rr_profile(series: pd.Series, windows: tuple = DEFAULT_WINDOWS, weights: dict = DEFAULT_WEIGHTS) -> dict:
    """Blend hac_log_regression across multiple windows into a single
    trend_signal in [-1, 1] and an opportunity score in [0, 100]. Raises
    ValueError if no window has enough observations to fit."""
    stats = {w: hac_log_regression(series, w) for w in windows}
    available = {w: s for w, s in stats.items() if s is not None}
    if not available:
        raise ValueError("No regression window has sufficient observations.")

    weight_total = sum(weights[w] for w in available)
    directional = 0.0
    for w, s in available.items():
        certainty = np.sqrt(max(s["r2"], 0))
        directional += weights[w] * np.tanh(s["t_hac"] / 3.0) * certainty
    directional /= weight_total

    opportunity_parts, opportunity_weights = [], []
    for w, ow in OPPORTUNITY_WINDOWS:
        s = available.get(w)
        if s is None:
            continue
        opportunity_parts.append(_opportunity_component(s))
        opportunity_weights.append(ow)

    if opportunity_parts:
        opportunity = 100 * np.average(opportunity_parts, weights=opportunity_weights)
    else:
        # None of the preferred windows fit -- fall back to whichever
        # shorter window did, so a young asset still scores.
        fallback = next(iter(available.values()))
        opportunity = 100 * _opportunity_component(fallback)

    return {
        "trend_signal": float(np.clip(directional, -1, 1)),
        "opportunity": float(np.clip(opportunity, 0, 100)),
        "windows": stats,
    }


def mean_reversion_snapshot(series: pd.Series, window: int = 365) -> Optional[dict]:
    """How far the latest level sits from its own trailing mean, in units
    of trailing standard deviation. Default window is 365 calendar days
    (one crypto year). Returns None below 20 observations."""
    values = pd.Series(series).dropna().astype(float).tail(window)
    n = len(values)
    if n < 20:
        return None
    mean = float(values.mean())
    std = float(values.std(ddof=1))
    latest = float(values.iloc[-1])
    z = (latest - mean) / std if std > 1e-12 else 0.0
    percentile = float((values < latest).mean() * 100)
    return {"window": window, "observations": n, "latest": latest, "mean": mean, "std": std, "z_score": z, "percentile": percentile}


# =============================================================================
# PROCESSING — RELATIVE STRENGTH RANKING (peer + BTC-benchmark leadership)
# =============================================================================
# The "relative trend indications" deliverable: generalizes the sector-ETF
# ranking script's Leadership/Opportunity/Joint/Pareto-dominance logic onto
# trend_rr_profile above.
PEER_WEIGHT = 0.60
BENCHMARK_WEIGHT = 0.25
ABSOLUTE_LEADERSHIP_WEIGHT = 0.15

ABSOLUTE_OPPORTUNITY_WEIGHT = 0.65
BENCHMARK_OPPORTUNITY_WEIGHT = 0.35

NEUTRAL_SCORE = 50.0


def aligned_ratio(series_a: pd.Series, series_b: pd.Series) -> pd.Series:
    """Numerator/denominator ratio over their overlapping, positive-valued
    dates only -- the ratio series a relative-strength trend is fit
    against."""
    pair = pd.concat([series_a, series_b], axis=1, join="inner").dropna()
    pair = pair[(pair.iloc[:, 0] > 0) & (pair.iloc[:, 1] > 0)]
    return pair.iloc[:, 0] / pair.iloc[:, 1]


def pareto_dominated_by(table: pd.DataFrame) -> list[int]:
    """For each row, count how many OTHER rows weakly dominate it on both
    Leadership and Opportunity (>= on both, > on at least one). Fewer
    dominators is better; 0 means no asset in the table beats this one on
    both axes simultaneously."""
    leadership = table["Leadership"].to_numpy()
    opportunity = table["Opportunity"].to_numpy()
    counts = []
    for i in range(len(table)):
        dominates = (
            (leadership >= leadership[i])
            & (opportunity >= opportunity[i])
            & ((leadership > leadership[i]) | (opportunity > opportunity[i]))
        )
        counts.append(int(dominates.sum()))
    return counts


def _safe_profile(series: pd.Series) -> Optional[dict]:
    try:
        return trend_rr_profile(series)
    except ValueError:
        return None


def rank_universe(
    closes: dict[str, pd.Series], labels: dict[str, str], benchmark_ticker: Optional[str] = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Rank every ticker in `closes` by Leadership (relative strength vs.
    peers + benchmark) and Opportunity (regression-implied reward).
    `closes` maps ticker -> a close-price pd.Series (DatetimeIndex);
    `labels` maps ticker -> display name; `benchmark_ticker` must be a key
    of `closes` if given.

    Returns (ranked_table, pair_signals) where pair_signals[a][b] is the
    trend_signal of a/b's ratio series (the peer matrix, exposed for
    callers that want the full pairwise detail, not just the aggregate
    leadership score).
    """
    tickers = list(closes)
    if len(tickers) < 2:
        raise ValueError("rank_universe needs at least 2 tickers to compute peer-relative signals")

    absolute_profiles = {t: _safe_profile(closes[t]) for t in tickers}

    pair_signals = pd.DataFrame(0.0, index=tickers, columns=tickers)
    for numerator in tickers:
        for denominator in tickers:
            if numerator == denominator:
                continue
            ratio = aligned_ratio(closes[numerator], closes[denominator])
            profile = _safe_profile(ratio)
            pair_signals.loc[numerator, denominator] = profile["trend_signal"] if profile else 0.0

    rows = []
    for ticker in tickers:
        absolute = absolute_profiles[ticker]
        peers = [t for t in tickers if t != ticker]
        peer_leadership = (
            NEUTRAL_SCORE + 50.0 * float(pair_signals.loc[ticker, peers].mean()) if peers else NEUTRAL_SCORE
        )

        if benchmark_ticker and benchmark_ticker in closes and benchmark_ticker != ticker:
            benchmark_profile = _safe_profile(aligned_ratio(closes[ticker], closes[benchmark_ticker]))
        else:
            # The benchmark ranked against itself is a degenerate constant
            # ratio -- score it neutral rather than letting a zero-variance
            # regression distort its own rank.
            benchmark_profile = None
        benchmark_leadership = NEUTRAL_SCORE + 50.0 * benchmark_profile["trend_signal"] if benchmark_profile else NEUTRAL_SCORE

        absolute_leadership = NEUTRAL_SCORE + 50.0 * absolute["trend_signal"] if absolute else NEUTRAL_SCORE
        leadership = (
            PEER_WEIGHT * peer_leadership
            + BENCHMARK_WEIGHT * benchmark_leadership
            + ABSOLUTE_LEADERSHIP_WEIGHT * absolute_leadership
        )

        absolute_opportunity = absolute["opportunity"] if absolute else NEUTRAL_SCORE
        benchmark_opportunity = benchmark_profile["opportunity"] if benchmark_profile else absolute_opportunity
        opportunity = (
            ABSOLUTE_OPPORTUNITY_WEIGHT * absolute_opportunity + BENCHMARK_OPPORTUNITY_WEIGHT * benchmark_opportunity
        )

        joint = 2 * leadership * opportunity / max(leadership + opportunity, 1e-9)

        rows.append(
            {
                "Ticker": ticker,
                "Name": labels.get(ticker, ticker),
                "Leadership": leadership,
                "Opportunity": opportunity,
                "Joint": joint,
                "PeerLeadership": peer_leadership,
                "BenchmarkLeadership": benchmark_leadership,
                "AbsoluteLeadership": absolute_leadership,
                "AbsoluteOpportunity": absolute_opportunity,
                "BenchmarkOpportunity": benchmark_opportunity,
                "TrendSignal": absolute["trend_signal"] if absolute else 0.0,
            }
        )

    ranked = pd.DataFrame(rows).set_index("Ticker")
    ranked["ParetoDominatedBy"] = pareto_dominated_by(ranked)
    ranked = ranked.sort_values(
        ["Joint", "ParetoDominatedBy", "Leadership", "Opportunity"], ascending=[False, True, False, False]
    )
    ranked.insert(0, "Rank", np.arange(1, len(ranked) + 1))
    return ranked, pair_signals


# =============================================================================
# PROCESSING — CROSS-ASSET RISK GAUGE
# =============================================================================
TREND_WEIGHT = 0.55
RR_WEIGHT = 0.45

RR_QUALITY_MULTIPLIER: dict[str, float] = {
    "cluster": 1.0,
    "trendline": 0.85,
    "fib_extension": 0.70,
    "synthetic": 0.50,
}
RR_SATURATION_RATIO = 3.0  # rr_ratio at/above this maps to a full 100 rr_component pre-discount

VIOLATION_BASE_PENALTY = 15.0
VIOLATION_STREAK_PENALTY_PER_BAR = 5.0
VIOLATION_STREAK_PENALTY_CAP = 25.0
VIOLATION_BREACH_PENALTY_PER_ATR = 5.0
VIOLATION_BREACH_PENALTY_CAP = 15.0

BREADTH_UNDERCUT_THRESHOLD = 0.5
BREADTH_RISK_OFF_AMPLIFIER_MAX = 20.0

FORMULA_LEGEND = f"""\
risk_score       = clip({TREND_WEIGHT}*trend_component + {RR_WEIGHT}*rr_component - violation_penalty, 0, 100)
  trend_component  = (trend_signal + 1) * 50                    [trend_signal in -1..1, HAC regression]
  rr_component     = min(rr_ratio, {RR_SATURATION_RATIO:.0f}) / {RR_SATURATION_RATIO:.0f} * 100 * quality_multiplier
                     quality_multiplier by target_source: {RR_QUALITY_MULTIPLIER}
  violation_penalty= 0 unless trend_violation.status == "undercut", else:
                     {VIOLATION_BASE_PENALTY:.0f} (base)
                     + min({VIOLATION_STREAK_PENALTY_PER_BAR:.0f}*bars_since_break, {VIOLATION_STREAK_PENALTY_CAP:.0f}) (streak)
                     + min({VIOLATION_BREACH_PENALTY_PER_ATR:.0f}*breach_atr, {VIOLATION_BREACH_PENALTY_CAP:.0f}) (breach)
overall_risk_score = weight-average of risk_score across the universe (composite_weights)
risk_off_pct       = 100 - overall_risk_score, + up to {BREADTH_RISK_OFF_AMPLIFIER_MAX:.0f} amplifier when
                     breadth_undercut_pct > {BREADTH_UNDERCUT_THRESHOLD:.0%} (a majority of the universe broken
                     at once is treated as a breadth/regime signal, not independent per-asset noise)\
"""


@dataclass(frozen=True)
class RRComponentBreakdown:
    magnitude: float  # 0-100, rr_ratio scaled before the target_source quality discount
    quality_multiplier: float  # RR_QUALITY_MULTIPLIER[target_source]
    component: float  # magnitude * quality_multiplier -- what actually feeds risk_score


@dataclass(frozen=True)
class ViolationPenaltyBreakdown:
    base: float
    streak_penalty: float
    breach_penalty: float
    total: float


@dataclass(frozen=True)
class AssetGauge:
    ticker: str
    name: str
    weight: float
    risk_score: float
    trend_signal: float
    trend_component: float
    trend_contribution: float
    rr_ratio: float
    rr: RRComponentBreakdown
    rr_contribution: float
    target_source: str
    trend_violation_status: str
    violation: ViolationPenaltyBreakdown
    blurb: str


@dataclass(frozen=True)
class CryptoGauge:
    overall_risk_score: float
    risk_off_pct: float
    breadth_undercut_pct: float
    assets: list[AssetGauge]


def _rr_breakdown(rr_ratio: float, target_source: str) -> RRComponentBreakdown:
    magnitude = min(max(rr_ratio, 0.0), RR_SATURATION_RATIO) / RR_SATURATION_RATIO * 100.0
    quality = RR_QUALITY_MULTIPLIER.get(target_source, 0.5)
    return RRComponentBreakdown(magnitude=magnitude, quality_multiplier=quality, component=magnitude * quality)


def _violation_breakdown(status: str, breach_atr: float, bars_since_break: Optional[int]) -> ViolationPenaltyBreakdown:
    if status != "undercut":
        return ViolationPenaltyBreakdown(base=0.0, streak_penalty=0.0, breach_penalty=0.0, total=0.0)
    streak = bars_since_break or 0
    streak_penalty = min(streak * VIOLATION_STREAK_PENALTY_PER_BAR, VIOLATION_STREAK_PENALTY_CAP)
    breach_penalty = min(max(breach_atr, 0.0) * VIOLATION_BREACH_PENALTY_PER_ATR, VIOLATION_BREACH_PENALTY_CAP)
    total = VIOLATION_BASE_PENALTY + streak_penalty + breach_penalty
    return ViolationPenaltyBreakdown(base=VIOLATION_BASE_PENALTY, streak_penalty=streak_penalty, breach_penalty=breach_penalty, total=total)


def _target_source_phrase(source: str, ratio: Optional[float]) -> str:
    if source == "cluster":
        return "a cluster-anchored"
    if source == "trendline":
        return "a trendline-anchored"
    if source == "fib_extension":
        return f"a {ratio:.3f}x fib-extension" if ratio is not None else "a fib-extension"
    return "an unanchored synthetic"


def _blurb(
    name: str,
    trend_signal: float,
    rr_ratio: float,
    target_source: str,
    target_fib_ratio: Optional[float],
    violation_status: str,
    breach_atr: float,
    bars_since_break: Optional[int],
) -> str:
    parts = []
    if violation_status == "undercut":
        streak = bars_since_break or 0
        parts.append(
            f"support trendline undercut {streak} bar{'s' if streak != 1 else ''} ago "
            f"({breach_atr:.1f} ATR below) -- take some risk off"
        )
    elif violation_status == "intact":
        parts.append("uptrend support holding")
    trend_word = "rising" if trend_signal > 0.15 else "falling" if trend_signal < -0.15 else "flat"
    parts.append(f"{trend_word} trend (signal {trend_signal:+.2f})")
    parts.append(f"{rr_ratio:.2f}x R:R via {_target_source_phrase(target_source, target_fib_ratio)} target")
    return f"{name}: " + "; ".join(parts) + "."


def _asset_gauge(report: RiskRewardReport, name: str, weight: float, trend_signal: float) -> AssetGauge:
    tv = report.trend_violation
    trend_component = (trend_signal + 1.0) * 50.0
    trend_contribution = TREND_WEIGHT * trend_component
    rr = _rr_breakdown(report.stop_target.rr_ratio, report.stop_target.target_source)
    rr_contribution = RR_WEIGHT * rr.component
    violation = _violation_breakdown(tv.status, tv.breach_atr, tv.bars_since_break)
    risk_score = min(100.0, max(0.0, trend_contribution + rr_contribution - violation.total))
    blurb = _blurb(
        name,
        trend_signal,
        report.stop_target.rr_ratio,
        report.stop_target.target_source,
        report.stop_target.target_fib_ratio,
        tv.status,
        tv.breach_atr,
        tv.bars_since_break,
    )
    return AssetGauge(
        ticker=report.ticker,
        name=name,
        weight=weight,
        risk_score=risk_score,
        trend_signal=trend_signal,
        trend_component=trend_component,
        trend_contribution=trend_contribution,
        rr_ratio=report.stop_target.rr_ratio,
        rr=rr,
        rr_contribution=rr_contribution,
        target_source=report.stop_target.target_source,
        trend_violation_status=tv.status,
        violation=violation,
        blurb=blurb,
    )


def _risk_off_pct(overall_risk_score: float, breadth_undercut_pct: float) -> float:
    base = 100.0 - overall_risk_score
    amplifier = 0.0
    if breadth_undercut_pct > BREADTH_UNDERCUT_THRESHOLD:
        excess = (breadth_undercut_pct - BREADTH_UNDERCUT_THRESHOLD) / (1.0 - BREADTH_UNDERCUT_THRESHOLD)
        amplifier = excess * BREADTH_RISK_OFF_AMPLIFIER_MAX
    return float(min(100.0, max(0.0, base + amplifier)))


def build_gauge(
    reports: dict[str, RiskRewardReport], trend_signals: dict[str, float], universe: Optional[dict[str, str]] = None
) -> CryptoGauge:
    """Combine per-asset RiskRewardReport + a trend_signal (from
    trend_rr_profile, in [-1, 1]) into the overall gauge. `reports`/
    `trend_signals` need not cover every ticker in `universe` -- missing
    tickers are skipped and remaining weights renormalized."""
    universe = universe or default_universe()
    weights = composite_weights(universe)
    covered = {t: universe[t] for t in universe if t in reports and t in trend_signals}
    if not covered:
        raise ValueError("No tickers in `reports`/`trend_signals` overlap with `universe`")
    covered_weight_total = sum(weights[t] for t in covered)

    assets = [
        _asset_gauge(reports[t], name, weights[t] / covered_weight_total, trend_signals[t])
        for t, name in covered.items()
    ]
    overall_risk_score = sum(ag.risk_score * ag.weight for ag in assets)
    breadth_undercut_pct = sum(ag.weight for ag in assets if ag.trend_violation_status == "undercut")
    risk_off_pct = _risk_off_pct(overall_risk_score, breadth_undercut_pct)

    return CryptoGauge(
        overall_risk_score=overall_risk_score,
        risk_off_pct=risk_off_pct,
        breadth_undercut_pct=breadth_undercut_pct,
        assets=sorted(assets, key=lambda ag: ag.risk_score, reverse=True),
    )


# =============================================================================
# OUTPUT — REPORT ASSEMBLY + INTERPRETABLE RENDERING
# =============================================================================
MAX_SUPPORTS_SHOWN = 3
MAX_LEADERSHIP_ROWS_SHOWN = 25


def build_report(universe: Optional[dict[str, str]] = None) -> dict:
    """Fetch + analyze every ticker in `universe` via one batched yfinance
    call. Never lets one ticker's analysis failure sink the whole report --
    isolates it into `dropped` instead."""
    universe = universe or default_universe()
    ohlcv_by_ticker, download_dropped = download_universe(list(universe.keys()))

    reports: dict[str, RiskRewardReport] = {}
    trend_signals: dict[str, float] = {}
    closes: dict[str, pd.Series] = {}
    dates: dict[str, pd.DatetimeIndex] = {}
    dropped: list[dict] = list(download_dropped)

    for ticker, ohlcv in ohlcv_by_ticker.items():
        name = universe.get(ticker, ticker)
        close_series = pd.Series(ohlcv.close, index=ohlcv.dates)
        try:
            report = analyze(ticker, ohlcv.high, ohlcv.low, ohlcv.close, ohlcv.volume)
            trend_signals[ticker] = trend_rr_profile(close_series)["trend_signal"]
        except Exception as e:  # noqa: BLE001 -- per-ticker isolation, reason recorded below
            dropped.append({"ticker": ticker, "name": name, "reason": str(e)})
            continue
        reports[ticker] = report
        closes[ticker] = close_series
        dates[ticker] = ohlcv.dates

    if len(closes) < 2:
        raise RuntimeError(f"Only {len(closes)} ticker(s) survived analysis -- need >=2 for relative ranking")

    benchmark = BENCHMARK_TICKER if BENCHMARK_TICKER in closes else None
    leadership_table, pair_signals = rank_universe(closes, universe, benchmark_ticker=benchmark)

    gauge = build_gauge(reports, trend_signals, universe=universe)
    return {
        "universe": universe,
        "gauge": gauge,
        "reports": reports,
        "dates": dates,
        "dropped": dropped,
        "leadership_table": leadership_table,
        "pair_signals": pair_signals,
    }


def _support_stack_lines(report: RiskRewardReport) -> list[str]:
    supports = sorted((c for c in report.clusters if c.price < report.last_close), key=lambda c: c.price, reverse=True)
    if not supports:
        return [
            "  support stack: none -- stop fell back to the ATR/pct cap "
            f"({report.stop_target.stop:.2f}, no cluster below price)"
        ]
    lines = [f"  support stack below {report.last_close:.2f}:"]
    for i, c in enumerate(supports[:MAX_SUPPORTS_SHOWN]):
        pct = (report.last_close - c.price) / report.last_close * 100
        atr_dist = (report.last_close - c.price) / report.atr if report.atr > 0 else float("nan")
        gap = ""
        if i > 0:
            prev = supports[i - 1]
            gap_pct = (prev.price - c.price) / report.last_close * 100
            gap = f"  (gap from prior support: {gap_pct:.1f}%)"
        lines.append(f"    #{i + 1}: {c.price:.4g}  -{pct:.1f}%  -{atr_dist:.1f} ATR  strength={c.strength}{gap}")
    return lines


def _trendline_detail_lines(report: RiskRewardReport, dates: Optional[pd.DatetimeIndex]) -> list[str]:
    tv = report.trend_violation
    if tv.status == "no_active_trendline" or tv.trendline is None:
        return ["  trendline: no recent ascending support line in range"]
    line = tv.trendline
    start_date = dates[line.start_idx].date() if dates is not None else f"bar {line.start_idx}"
    end_date = dates[line.end_idx].date() if dates is not None else f"bar {line.end_idx}"
    status_word = "undercut" if tv.status == "undercut" else "intact"
    breach_note = (
        f" -- price sits {tv.breach_atr:.2f} ATR below it, broken {tv.bars_since_break} bar"
        f"{'s' if tv.bars_since_break != 1 else ''} ago"
        if tv.status == "undercut"
        else f" -- price sits {-tv.breach_atr:.2f} ATR above it"
    )
    anchor_price_at_end_idx = line.start_price + line.slope * (line.end_idx - line.start_idx)
    return [
        f"  trendline ({status_word}): rising support from {start_date} (${line.start_price:.4g}) "
        f"through {end_date} (${anchor_price_at_end_idx:.4g} at anchor, slope {line.slope:+.4g}/bar), "
        f"extended to ${line.end_price:.4g} today{breach_note}"
    ]


def _asset_block_lines(ag: AssetGauge, report: RiskRewardReport, dates: Optional[pd.DatetimeIndex]) -> list[str]:
    lines = [
        f"{ag.ticker:9} {ag.name:20} risk_score={ag.risk_score:.1f}/100  last_close=${report.last_close:.4g}",
        f"  trend_component={ag.trend_component:.1f} (trend_signal={ag.trend_signal:+.2f}) "
        f"-> contributes {ag.trend_contribution:.1f}",
        f"  rr_component={ag.rr.component:.1f} (rr_ratio={ag.rr_ratio:.2f}x, source={ag.target_source}, "
        f"magnitude={ag.rr.magnitude:.1f}, quality={ag.rr.quality_multiplier:.2f}) "
        f"-> contributes {ag.rr_contribution:.1f}",
        f"  stop={report.stop_target.stop:.4g}  target={report.stop_target.target:.4g}  "
        f"risk={report.stop_target.risk_pct:.1f}%  reward={report.stop_target.reward_pct:.1f}%",
        f"  violation_penalty={ag.violation.total:.1f} = base {ag.violation.base:.1f} "
        f"+ streak {ag.violation.streak_penalty:.1f} + breach {ag.violation.breach_penalty:.1f}",
    ]
    lines += _support_stack_lines(report)
    lines += _trendline_detail_lines(report, dates)
    lines.append(f"  summary: {ag.blurb}")
    return lines


def _leadership_table_lines(leadership_table: pd.DataFrame) -> list[str]:
    view = leadership_table.head(MAX_LEADERSHIP_ROWS_SHOWN)
    lines = [f"{'Rank':>4} {'Ticker':9} {'Name':20} {'Leadership':>10} {'Opportunity':>11} {'Joint':>8} {'DomBy':>6}"]
    for ticker, row in view.iterrows():
        lines.append(
            f"{int(row['Rank']):>4} {ticker:9} {str(row['Name'])[:20]:20} "
            f"{row['Leadership']:>10.1f} {row['Opportunity']:>11.1f} {row['Joint']:>8.1f} "
            f"{int(row['ParetoDominatedBy']):>6}"
        )
    return lines


def render_summary(result: dict) -> str:
    """Turn build_report()'s structured output into a self-explanatory
    printed report: formula legend, leadership/opportunity ranking table,
    then per-asset the exact trend/rr/violation contributions, support
    cluster stack, and trendline detail. No score in the output is
    implicit -- the line above it names the term that produced it."""
    gauge: CryptoGauge = result["gauge"]
    lines = [
        f"crypto-analysis snapshot — {len(gauge.assets)}/{len(result['universe'])} assets analyzed "
        f"(benchmark: {BENCHMARK_TICKER})",
        "",
        FORMULA_LEGEND,
        "",
        f"OVERALL RISK SCORE: {gauge.overall_risk_score:.1f}/100",
        f"RISK-OFF READ:      {gauge.risk_off_pct:.1f}%",
        f"BREADTH UNDERCUT:   {gauge.breadth_undercut_pct:.0%} of universe (weighted)",
        "",
        "-" * 80,
        "LEADERSHIP / OPPORTUNITY RANKING (relative trend indications, peer + BTC-benchmark)",
        "-" * 80,
    ]
    lines += _leadership_table_lines(result["leadership_table"])

    for ag in gauge.assets:
        report = result["reports"][ag.ticker]
        dates = result["dates"].get(ag.ticker)
        lines.append("")
        lines.append("-" * 80)
        lines += _asset_block_lines(ag, report, dates)
    if result["dropped"]:
        lines.append("")
        lines.append("Dropped tickers:")
        for d in result["dropped"]:
            lines.append(f"  {d['ticker']} ({d.get('name', '')}): {d['reason']}")
    return "\n".join(lines)


def run(universe: Optional[dict[str, str]] = None, print_report: bool = True) -> dict:
    """DATA IN  -> a crypto ticker universe (default: BTC/ETH + 16 alts).
    DATA OUT -> the full structured processing result (gauge, per-asset
    RiskRewardReport objects, leadership/opportunity ranking table,
    pairwise trend-signal matrix, dropped tickers) -- everything computed
    above, in one dict. Also prints an organized, interpretable report to
    stdout unless print_report=False."""
    result = build_report(universe)
    if print_report:
        print(render_summary(result))
    return result


if __name__ == "__main__":
    run()
