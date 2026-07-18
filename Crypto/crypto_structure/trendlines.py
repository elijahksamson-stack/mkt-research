"""
Trendline discovery — rr.txt Part 5, both families.

Family A (quantile-regression): one GLOBAL upper + one GLOBAL lower line,
fit across all pivots in a 200-bar window via quantile regression (tau=0.95
on highs, tau=0.05 on lows), kept only if R^2 >= 0.55. Robust, but a single
global line smooths through segmented structure.

Family B (multi-lookback pivot-pair): many segment-specific lines, each
drawn between two significant swing pivots and validated bar-by-bar against
real price action (a touch/violation gate), mimicking how a discretionary
trader actually draws a trendline. Catches ascending channels / descending
wedges Family A smooths over. This is also the family the trend-violation
detector (trend_violation.py) is built on.

Pure math, bar-indexed rather than calendar-indexed, so it needs no
crypto-specific adaptation — verbatim port of Macro/market-structure's
trendlines.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Sequence

import numpy as np
from scipy.optimize import linprog

from crypto_structure.indicators import Pivot, find_local_extrema
from crypto_structure.levels import Level

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
    score: float  # touch/span/violation quality (the source's r2 field)
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
    the line's own R^2 (Part 6.1)."""
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
    `max_lines` (rr.txt's own PAIR_MAX_LINES=12 by default). Pass
    max_lines=None (or a larger number) to see the full ranked candidate
    pool -- the source's own touches^1.5*span^0.5/(1+violations*3) score
    formula can rank an old, high-touch, near-flat segment above a
    genuinely recent, cleaner ascending line, so a caller that specifically
    needs "the most relevant RECENT line" (trend_violation.py) should not
    rely on the top-12-only view."""
    n = len(high)
    swing_w, min_span, touch_band = _adaptive_pair_params(n, atr)
    high_idx, low_idx = find_local_extrema(high, low, window=swing_w)
    lines = _pair_lines(high_idx, high, n, min_span, touch_band, max_violation_pct, min_touches, "upper")
    lines += _pair_lines(low_idx, low, n, min_span, touch_band, max_violation_pct, min_touches, "lower")
    lines.sort(key=lambda l: l.score, reverse=True)
    deduped = _dedup_pair_lines(lines, atr)
    return deduped if max_lines is None else deduped[:max_lines]
