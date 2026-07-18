"""
yfinance OHLCV fetching with a data-quality gate.

The market-structure analogue of Macro/Rates/rates_macro/market_data.py,
extended from a single close series to full OHLCV since risk_reward.py's
pivot/ATR/volume-profile machinery needs high/low/volume too, not just
close.
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
MIN_BARS = 260  # comfortably above TREND_LOOKBACK_BARS=200 for a meaningful trend fit
MIN_COVERAGE = 0.95
MAX_STALENESS_DAYS = 10
DOWNLOAD_RETRIES = 3

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
    """Gate an OHLCV frame on bar count, coverage, and (optionally)
    staleness vs. `as_of` before it's trusted for risk_reward analysis.
    Pure function -- no network -- so it is fully unit-testable offline."""
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
    return True, "", {"bars": bars, "coverage": coverage, "latest": latest}


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
