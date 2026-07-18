"""
yfinance OHLCV fetching with a data-quality gate, for the crypto market.

The crypto analogue of Macro/market-structure/market_data.py, adapted for a
24/7/365 market in two ways: (1) MAX_STALENESS_DAYS is tightened from 10 to
3, since crypto has no weekend/holiday gaps to allow for -- three straight
missed days is a real staleness signal here, not a long weekend; (2) a
MIN_MEDIAN_DOLLAR_VOLUME liquidity gate is added (absent from the equity
sibling, which only fetches large, obviously-liquid index/sector ETFs) so a
thinly-traded or delisted-in-practice ticker can't sneak into the universe
and produce a misleading structural read. Also adds `download_universe()`,
a batched multi-ticker fetch the equity sibling doesn't need (it only ever
analyzes one ticker's detail view at a time) but this package's
relative_strength ranking does, since ranking N assets against each other
and against BTC is far cheaper as one grouped yfinance call than N
sequential ones.
"""
from __future__ import annotations

import contextlib
import io
import logging
import time
import warnings
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore", category=FutureWarning)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

DEFAULT_PERIOD = "3y"
MIN_BARS = 220  # comfortably above TREND_LOOKBACK_BARS=200, while still admitting large-cap alts with shorter histories (e.g. APT, ARB, OP)
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
    coverage = float(df["Close"].tail(MIN_BARS).notna().mean())
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
    if bars < MIN_BARS:
        return False, f"{bars} bars < {MIN_BARS}", {"bars": bars}
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
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                io.StringIO()
            ):
                raw = yf.download(
                    ticker,
                    period=period,
                    interval="1d",
                    auto_adjust=True,
                    progress=False,
                    timeout=25,
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


def download_universe(
    tickers: list[str], period: str = DEFAULT_PERIOD
) -> tuple[dict[str, OHLCV], list[dict]]:
    """Fetch + quality-gate every ticker in `tickers` with one batched
    yfinance call per DOWNLOAD_CHUNK tickers, isolating any single
    ticker's failure into `dropped` rather than aborting the whole batch.
    Returns (ohlcv_by_ticker, dropped)."""
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
