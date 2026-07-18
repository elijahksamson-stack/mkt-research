"""
Relative technicals at the index/sector/factor level -- an RRG-style
(Relative Rotation Graph) read, output as plain data instead of a chart.

The classic RRG plots two 100-centered series against each other:
  - RS-Ratio: is this ticker's relative strength ABOVE or BELOW its own
    recent normal level right now (a level read).
  - RS-Momentum: is that relative strength ACCELERATING or DECELERATING
    (a rate-of-change read on top of the level read).
Those two axes classify every ticker into one of four quadrants:
  Leading    RS-Ratio >= 100, RS-Momentum >= 100  -- outperforming, and gaining pace
  Weakening  RS-Ratio >= 100, RS-Momentum < 100   -- still outperforming, but losing pace
  Lagging    RS-Ratio < 100,  RS-Momentum < 100   -- underperforming, still losing ground
  Improving  RS-Ratio < 100,  RS-Momentum >= 100  -- underperforming, but closing the gap

This module computes the same two numbers and the same quadrant label the
chart would plot, but never plots anything -- every value is a named,
auditable field, and the formulas below are fully specified (there is no
single public "official" RRG formula; this is an original, documented
normalization, not a reproduction of any proprietary implementation):

  ratio          = aligned_ratio(ticker_close, benchmark_close)   [relative_strength.py]
  rs_ratio       = 100 + SCALE * zscore(ratio, RATIO_WINDOW)
                   -- how many (scaled) standard deviations the current
                   ratio sits from its own RATIO_WINDOW-bar mean.
  rs_momentum    = 100 * rs_ratio_t / rs_ratio_{t-MOMENTUM_LOOKBACK}
                   -- percent change of RS-Ratio itself over the lookback;
                   100 = unchanged, >100 = RS-Ratio rising (momentum
                   building), <100 = RS-Ratio falling (momentum fading).

`relative_technicals()` also reports two supporting, more classically
"technical" reads that corroborate or contradict the quadrant call:
  - the ratio's position vs. its own 50/200-bar moving averages, and
    whether the 50 sits above (golden) or below (death) the 200 -- a
    slower, lagging confirmation of the same relative-strength trend.
  - relative volatility: the ticker's own trailing realized vol divided
    by the benchmark's -- is this ticker's move choppier or calmer than
    the market it's being compared to.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from equity_rotation.relative_strength import aligned_ratio, rolling_ratio_average

RATIO_WINDOW = 63  # ~1 quarter, z-score window for RS-Ratio
RS_RATIO_SCALE = 2.0
MOMENTUM_LOOKBACK = 21  # ~1 month, rate-of-change window for RS-Momentum
VOL_WINDOW = 21
TRADING_DAYS_PER_YEAR = 252
MA_SHORT = 50
MA_LONG = 200
MIN_BARS = RATIO_WINDOW + MOMENTUM_LOOKBACK + 20  # buffer for a stable rolling std at series start

QUADRANT_LEADING = "leading"
QUADRANT_WEAKENING = "weakening"
QUADRANT_LAGGING = "lagging"
QUADRANT_IMPROVING = "improving"


@dataclass(frozen=True)
class RelativeTechnicals:
    ticker: str
    name: str
    rs_ratio: float
    rs_momentum: float
    quadrant: str
    days_in_quadrant: int
    ratio_vs_50dma_pct: Optional[float]
    ratio_vs_200dma_pct: Optional[float]
    ma_cross: Optional[str]  # "golden" | "death" | None if 200dma unavailable
    relative_volatility: float


def _rs_ratio_series(ratio: pd.Series, window: int = RATIO_WINDOW) -> pd.Series:
    mean = ratio.rolling(window=window, min_periods=window).mean()
    std = ratio.rolling(window=window, min_periods=window).std()
    z = (ratio - mean) / std.replace(0.0, np.nan)
    return 100.0 + RS_RATIO_SCALE * z


def _rs_momentum_series(rs_ratio: pd.Series, lookback: int = MOMENTUM_LOOKBACK) -> pd.Series:
    return 100.0 * rs_ratio / rs_ratio.shift(lookback)


def _quadrant(rs_ratio: float, rs_momentum: float) -> str:
    if rs_ratio >= 100.0:
        return QUADRANT_LEADING if rs_momentum >= 100.0 else QUADRANT_WEAKENING
    return QUADRANT_IMPROVING if rs_momentum >= 100.0 else QUADRANT_LAGGING


def _days_in_quadrant(quadrants: pd.Series) -> int:
    """Consecutive trailing bars matching the most recent quadrant label."""
    valid = quadrants.dropna()
    if valid.empty:
        return 0
    current = valid.iloc[-1]
    count = 0
    for label in reversed(valid.tolist()):
        if label != current:
            break
        count += 1
    return count


def _relative_volatility(
    ticker_close: pd.Series, benchmark_close: pd.Series, window: int = VOL_WINDOW
) -> float:
    pair = pd.concat(
        [ticker_close.rename("ticker"), benchmark_close.rename("benchmark")], axis=1, join="inner"
    ).dropna()
    ticker_returns = np.log(pair["ticker"]).diff().tail(window)
    benchmark_returns = np.log(pair["benchmark"]).diff().tail(window)
    ticker_vol = float(ticker_returns.std(ddof=1)) * np.sqrt(TRADING_DAYS_PER_YEAR)
    benchmark_vol = float(benchmark_returns.std(ddof=1)) * np.sqrt(TRADING_DAYS_PER_YEAR)
    if benchmark_vol <= 1e-12:
        return float("nan")
    return ticker_vol / benchmark_vol


def _ma_cross_reads(ratio: pd.Series) -> tuple[Optional[float], Optional[float], Optional[str]]:
    latest = ratio.iloc[-1]
    ma_short = rolling_ratio_average(ratio, MA_SHORT).iloc[-1]
    vs_50dma = float(latest / ma_short - 1.0) if pd.notna(ma_short) else None

    if len(ratio) < MA_LONG:
        return vs_50dma, None, None
    ma_long = rolling_ratio_average(ratio, MA_LONG).iloc[-1]
    if pd.isna(ma_long):
        return vs_50dma, None, None
    vs_200dma = float(latest / ma_long - 1.0)
    cross = "golden" if ma_short > ma_long else "death"
    return vs_50dma, vs_200dma, cross


def relative_technicals(
    ticker: str, name: str, ticker_close: pd.Series, benchmark_close: pd.Series
) -> RelativeTechnicals:
    """RRG-style relative-technicals read for one ticker vs. `benchmark_close`.

    Raises ValueError when fewer than MIN_BARS aligned observations are
    available -- RS-Ratio's z-score and RS-Momentum's lookback both need
    real history, not just a handful of points, to mean anything.
    """
    ratio = aligned_ratio(ticker_close, benchmark_close)
    if len(ratio) < MIN_BARS:
        raise ValueError(
            f"relative_technicals needs at least {MIN_BARS} aligned observations, got {len(ratio)}"
        )

    rs_ratio_series = _rs_ratio_series(ratio)
    rs_momentum_series = _rs_momentum_series(rs_ratio_series)
    quadrant_series = pd.Series(
        [
            _quadrant(r, m) if pd.notna(r) and pd.notna(m) else None
            for r, m in zip(rs_ratio_series, rs_momentum_series)
        ],
        index=ratio.index,
    )

    rs_ratio_latest = float(rs_ratio_series.iloc[-1])
    rs_momentum_latest = float(rs_momentum_series.iloc[-1])
    if pd.isna(rs_ratio_latest) or pd.isna(rs_momentum_latest):
        raise ValueError("RS-Ratio/RS-Momentum did not converge for the latest bar -- insufficient history")

    vs_50dma, vs_200dma, ma_cross = _ma_cross_reads(ratio)

    return RelativeTechnicals(
        ticker=ticker,
        name=name,
        rs_ratio=rs_ratio_latest,
        rs_momentum=rs_momentum_latest,
        quadrant=_quadrant(rs_ratio_latest, rs_momentum_latest),
        days_in_quadrant=_days_in_quadrant(quadrant_series),
        ratio_vs_50dma_pct=vs_50dma,
        ratio_vs_200dma_pct=vs_200dma,
        ma_cross=ma_cross,
        relative_volatility=_relative_volatility(ticker_close, benchmark_close),
    )


def relative_technicals_table(
    closes: dict[str, pd.Series], labels: dict[str, str], benchmark_close: pd.Series
) -> list[RelativeTechnicals]:
    """relative_technicals() for every ticker in `closes`, sorted by
    RS-Ratio descending (strongest relative level first)."""
    rows = [
        relative_technicals(ticker, labels.get(ticker, ticker), closes[ticker], benchmark_close)
        for ticker in closes
    ]
    return sorted(rows, key=lambda r: r.rs_ratio, reverse=True)
