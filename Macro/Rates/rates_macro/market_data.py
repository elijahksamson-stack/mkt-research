"""
yfinance close-price fetching with a data-quality gate.

Generalizes the download_universe/quality_gate pattern from the Macro/Rates
CLAUDE.md example script down to a single ticker (S&P via SPY) — kept
separate from fred_client since this feed is Yahoo Finance OHLCV, not
FRED's release-schedule levels.
"""
from __future__ import annotations

import contextlib
import io
import logging
import time
import warnings
from typing import Optional

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore", category=FutureWarning)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

DEFAULT_PERIOD = "5y"
MIN_BARS = 252
MIN_COVERAGE = 0.95
MAX_STALENESS_DAYS = 10
DOWNLOAD_RETRIES = 3


def quality_gate(
    close: pd.Series, as_of: Optional[pd.Timestamp] = None
) -> tuple[bool, str, dict]:
    """Gate a close-price series on bar count, coverage, and (optionally)
    staleness vs. `as_of` before it's trusted for trend/RR analysis.

    Pure function — no network — so it is fully unit-testable offline.
    """
    if close is None or close.empty:
        return False, "no price data", {}
    coverage = float(close.tail(MIN_BARS).notna().mean())
    clean = close.dropna()
    clean = clean[clean > 0]
    bars = len(clean)
    if bars == 0:
        return False, "no valid closes", {}
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
    return raw


def fetch_close(ticker: str, period: str = DEFAULT_PERIOD) -> pd.Series:
    """Download `ticker`'s daily close series and run it through the quality
    gate. Raises RuntimeError if no data is returned or the gate rejects it.
    """
    raw = _download(ticker, period)
    if raw.empty or "Close" not in raw:
        raise RuntimeError(f"{ticker}: no price data returned")
    close = raw["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    # Gate BEFORE dropna(): quality_gate's coverage check reads
    # close.tail(MIN_BARS).notna().mean(), which is always 1.0 once NaNs
    # are already removed — the gate would never fire on a gappy series.
    valid, reason, _ = quality_gate(close)
    if not valid:
        raise RuntimeError(f"{ticker}: failed quality gate — {reason}")
    return close.dropna()
