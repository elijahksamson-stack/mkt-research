"""
Calendar-seasonal forward-return features, built on an expanding
historical window so future years never leak into earlier observations.

Leakage rule (the spec's explicit requirement): a historical instance at
date `t` only counts toward `as_of`'s seasonal snapshot if the *entire*
forward-return window `t..t+horizon` had already completed strictly before
`as_of` -- not merely "before this year," which would still leak a
same-year-earlier-in-the-window observation. That single condition
(`t + horizon <= as_of_index`) is sufficient and is what's actually
enforced below; requiring a strictly prior calendar year is layered on top
only because the spec phrases it that way ("using only prior years"), not
because it adds any additional leakage protection beyond the index check.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

SEASONAL_WINDOW_DAYS = 10  # calendar-day tolerance around as_of's day-of-year to count as "the same season"
MIN_OBSERVATIONS = 3
DAYS_IN_YEAR = 365.25


@dataclass(frozen=True)
class SeasonalSnapshot:
    canonical_id: str
    horizon_days: int
    n_observations: int
    mean_return: float
    median_return: float
    hit_rate: float  # fraction of historical instances with a positive forward return
    years_covered: tuple[int, ...]


def _circular_doy_distance(a: pd.Timestamp, b: pd.Timestamp) -> float:
    doy_a, doy_b = a.dayofyear, b.dayofyear
    diff = abs(doy_a - doy_b)
    return min(diff, DAYS_IN_YEAR - diff)


def build_seasonal_snapshot(
    canonical_id: str,
    dates: pd.DatetimeIndex,
    roll_adjusted_close: np.ndarray,
    horizon: int,
    as_of: Optional[pd.Timestamp] = None,
    window_days: int = SEASONAL_WINDOW_DAYS,
    min_observations: int = MIN_OBSERVATIONS,
) -> Optional[SeasonalSnapshot]:
    """`roll_adjusted_close` (not raw) since this is a return-based
    feature -- see market_data.py's module docstring on which series feeds
    which signal family. Returns None below `min_observations` qualifying
    historical instances."""
    dates = pd.DatetimeIndex(dates)
    as_of = pd.Timestamp(as_of) if as_of is not None else dates[-1]
    as_of_idx = int(np.searchsorted(dates.values, np.datetime64(as_of), side="right")) - 1
    if as_of_idx < horizon:
        return None

    fwd_returns = np.log(roll_adjusted_close[horizon:] / roll_adjusted_close[:-horizon])
    # fwd_returns[t] is the return realized starting at index t; only usable if t+horizon <= as_of_idx.
    usable_end = as_of_idx - horizon + 1  # exclusive upper bound on t

    matches: list[float] = []
    years: set[int] = set()
    current_year = as_of.year
    for t in range(usable_end):
        d = dates[t]
        if d.year >= current_year:
            continue
        if _circular_doy_distance(d, as_of) > window_days:
            continue
        matches.append(float(fwd_returns[t]))
        years.add(int(d.year))

    if len(matches) < min_observations:
        return None

    arr = np.array(matches)
    return SeasonalSnapshot(
        canonical_id=canonical_id,
        horizon_days=horizon,
        n_observations=len(arr),
        mean_return=float(np.mean(arr)),
        median_return=float(np.median(arr)),
        hit_rate=float(np.mean(arr > 0)),
        years_covered=tuple(sorted(years)),
    )
