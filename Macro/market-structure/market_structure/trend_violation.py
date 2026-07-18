"""
Ascending-support trendline violation detection.

This is the refinement this toolkit adds beyond rr.txt's original
methodology, motivated directly by a gap the source model has: it computes
multi-lookback pivot-pair trendlines (Family B, rr.txt Part 5.B) purely for
the chart overlay and the tier-2 target fallback -- Part 5's own
side-by-side comparison notes Family B "does NOT feed clusters." Nothing in
the original stop/target/R:R pipeline (Part 8) ever asks whether price has
broken back BELOW its own most relevant rising support line. That is
exactly the setup a discretionary trader flags by eye ("undercut support of
uptrend = take some risk off"), and exactly the case a still-positive R:R
snapshot can miss, because R:R measures level-to-level distance, not trend
integrity -- a stop/target pair can look fine on the same bar a supporting
trendline just broke.

This module closes that gap: it identifies the most relevant currently-
active ascending (rising) support line from Family B and reports whether
the latest close has undercut it, and for how many consecutive bars.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Sequence

import numpy as np

from market_structure.trendlines import TrendlineSegment, build_pivot_pair_trendlines

# A line anchored further back than this is stale -- not "the" current
# uptrend line a chart-watcher would still be tracking. Matches the
# SR_LOOKBACK_BARS convention levels.py uses for "recent enough to matter."
RELEVANCE_LOOKBACK_BARS = 252

# Same proximity convention as levels.py's MAX_SR_DIST_ATR: a line that
# isn't even near price isn't structurally "in play" right now.
MAX_LINE_DIST_ATR = 8.0

# build_pivot_pair_trendlines' default cap (12) serves the chart-overlay /
# tier-2-target use case, where the source's own score formula
# (touches^1.5*span^0.5/(1+violations*3)) can favor an old, high-touch,
# near-flat segment over a genuinely recent, cleaner ascending line -- so a
# recent-but-lower-scoring line can be crowded out of the top 12 entirely
# before this module ever gets a chance to consider it. Recomputing with a
# much larger pool (instead of reusing risk_reward.py's capped list) is
# what makes this detector actually find "the most relevant RECENT
# support line" rather than whatever survived an unrelated ranking.
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

    Selection is NOT simply "highest quality score": the source's own score
    formula (touches^1.5*span^0.5/(1+violations*3)) rewards long-running,
    heavily-touched channels, which tends to pick a broad multi-quarter
    channel that's still comfortably intact over the tighter, more recent
    higher-low line that just got undercut -- exactly backwards for a
    detector whose job is to catch a fresh break. So: if any eligible line
    is currently violated, prefer the most recently anchored VIOLATED one
    (the break someone is actually reacting to right now); only fall back
    to the highest-scoring line when nothing is currently broken, where
    picking the best-established channel as "the" intact support is the
    more stable, less noise-prone read.
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
    trendline, and if so, for how long has it been broken?

    `pivot_pair_lines` lets a caller pass in a specific candidate set (e.g.
    for testing, or to intentionally reuse another set). When omitted, this
    recomputes its own larger candidate pool (CANDIDATE_POOL_SIZE) rather
    than the tier-2-target-oriented top-12 -- see CANDIDATE_POOL_SIZE's
    comment for why reusing that capped list would silently miss recent
    lines.
    """
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
