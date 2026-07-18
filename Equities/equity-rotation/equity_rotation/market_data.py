"""
Batch yfinance OHLCV fetch + data-quality gate for the sector/factor
universe.

Unlike Macro/market-structure's market_data.py (one fetch_ohlcv() call per
ticker), this batches the whole universe into a single yf.download() call --
adapted from the original sector-rotation script's download_universe(),
which chunks large universes and retries chunk-by-chunk. Equity-rotation's
default universe is small (11 sectors + 6 factors + 1 benchmark = 18
tickers), well under one chunk; DOWNLOAD_CHUNK exists so a larger custom
universe doesn't silently get crammed into one oversized request.

Only I/O module in the package -- everything else (trend_regression,
relative_strength, rotation_ranking, relative_technicals) is pure math and
fully unit-testable offline. `_download_chunk` is the network boundary;
tests monkeypatch it rather than hitting yfinance live.
"""
from __future__ import annotations

import contextlib
import io
import logging
import time
import warnings
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore", category=FutureWarning)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

DEFAULT_PERIOD = "5y"
MIN_BARS = 252
MIN_COVERAGE = 0.95
MIN_MEDIAN_DOLLAR_VOLUME = 1_000_000.0
MAX_STALENESS_DAYS = 10
DOWNLOAD_CHUNK = 20
DOWNLOAD_RETRIES = 3
REQUIRED_COLUMNS = ("Open", "High", "Low", "Close", "Volume")


@dataclass(frozen=True)
class QualityMetrics:
    bars: int
    coverage: float
    median_dollar_volume: float
    latest: pd.Timestamp


@dataclass(frozen=True)
class FetchResult:
    closes: dict[str, pd.Series]
    quality: dict[str, QualityMetrics]
    dropped: list[dict]  # [{"ticker": ..., "name": ..., "reason": ...}]
    as_of: pd.Timestamp


def quality_gate(
    frame: Optional[pd.DataFrame], as_of: Optional[pd.Timestamp] = None
) -> tuple[bool, str, Optional[QualityMetrics]]:
    """Gate a raw OHLCV frame on bar count, coverage, staleness vs. `as_of`,
    and trailing median dollar volume (a liquidity floor -- some factor
    ETFs are thin enough that a rotation read on them would be noise, not
    signal). Pure function, no network, fully unit-testable offline."""
    if frame is None or frame.empty or "Close" not in frame:
        return False, "no price data", None

    coverage = float(frame["Close"].tail(MIN_BARS).notna().mean())
    clean = frame.dropna(subset=["Close"])
    clean = clean[clean["Close"] > 0]
    bars = len(clean)
    if bars == 0:
        return False, "no valid closes", None

    latest = pd.Timestamp(clean.index[-1]).tz_localize(None)
    if as_of is not None:
        staleness = (pd.Timestamp(as_of).tz_localize(None) - latest).days
        if staleness > MAX_STALENESS_DAYS:
            return False, f"stale by {staleness} days", None
    if bars < MIN_BARS:
        return False, f"{bars} bars < {MIN_BARS}", None
    if coverage < MIN_COVERAGE:
        return False, f"{coverage:.1%} coverage < {MIN_COVERAGE:.0%}", None

    volume = clean["Volume"].fillna(0) if "Volume" in clean else pd.Series(0.0, index=clean.index)
    median_dollar_volume = float((clean["Close"] * volume).tail(63).median())
    if median_dollar_volume < MIN_MEDIAN_DOLLAR_VOLUME:
        return (
            False,
            f"median dollar volume {median_dollar_volume:,.0f} below threshold "
            f"{MIN_MEDIAN_DOLLAR_VOLUME:,.0f}",
            None,
        )

    metrics = QualityMetrics(
        bars=bars, coverage=coverage, median_dollar_volume=median_dollar_volume, latest=latest
    )
    return True, "", metrics


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
            frames[ticker] = frame.reindex(columns=list(REQUIRED_COLUMNS))
        except Exception:
            pass
    return frames


def _download_chunk(tickers: list[str], period: str) -> pd.DataFrame:
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


def download_universe(tickers: list[str], period: str = DEFAULT_PERIOD) -> dict[str, pd.DataFrame]:
    """Batch-download raw (ungated) OHLCV for every ticker, chunked at
    DOWNLOAD_CHUNK and retried per chunk."""
    tickers = list(dict.fromkeys(t.upper().strip() for t in tickers if t.strip()))
    frames: dict[str, pd.DataFrame] = {}
    for start in range(0, len(tickers), DOWNLOAD_CHUNK):
        chunk = tickers[start : start + DOWNLOAD_CHUNK]
        raw = _download_chunk(chunk, period)
        if not raw.empty:
            frames.update(_extract_frames(raw, chunk))
    return frames


def fetch_universe(universe: dict[str, str], period: str = DEFAULT_PERIOD) -> FetchResult:
    """Download + quality-gate every ticker in `universe`. Never lets one
    ticker's bad data sink the whole fetch -- isolates it into `dropped`
    and returns closes/quality only for tickers that passed the gate."""
    raw_frames = download_universe(list(universe), period=period)
    available_dates = [
        frame["Close"].dropna().index[-1]
        for frame in raw_frames.values()
        if not frame.empty and frame["Close"].notna().any()
    ]
    if not available_dates:
        raise RuntimeError("No data was downloaded for the requested universe.")
    as_of = max(pd.Timestamp(d).tz_localize(None) for d in available_dates)

    closes: dict[str, pd.Series] = {}
    quality: dict[str, QualityMetrics] = {}
    dropped: list[dict] = []
    for ticker, name in universe.items():
        valid, reason, metrics = quality_gate(raw_frames.get(ticker), as_of)
        if valid:
            clean = raw_frames[ticker].dropna(subset=["Close"])
            closes[ticker] = clean["Close"]
            quality[ticker] = metrics
        else:
            dropped.append({"ticker": ticker, "name": name, "reason": reason})

    return FetchResult(closes=closes, quality=quality, dropped=dropped, as_of=as_of)
