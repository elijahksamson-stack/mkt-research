"""
Leakage-safe forward-return labels and the shared as-of trading-day grid
used to build historical training panels.

A label at `(canonical_id, as_of, horizon)` is only ever computed from
`roll_adjusted_close[as_of_idx]` and `roll_adjusted_close[as_of_idx +
horizon]` -- the second point is strictly in `as_of`'s future, which is
exactly what a label is supposed to be (the thing being predicted, not a
feature). The leakage risk this package actually has to guard against is
*features* seeing `as_of`'s future, which is each feature module's own
responsibility (see market_data.py, momentum.py, positioning.py). This
module's only real leakage duty is `trading_day_grid`: it must never
include a day whose full `horizon`-bar-ahead window has already run past
the end of history, or `validation.py` would train on a label that will
retroactively be "seen" only when the full series is fetched -- see
`max_as_of_index`.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from commodities.market_data import CommoditySeries

DEFAULT_HORIZONS: tuple[int, ...] = (5, 21, 63)
DEFAULT_GRID_STEP_DAYS = 5  # spacing between training as_of points -- see module docstring on tractability


@dataclass(frozen=True)
class ForwardLabel:
    canonical_id: str
    as_of: pd.Timestamp
    horizon_days: int
    forward_return: float
    forward_direction: bool  # forward_return > 0


def max_as_of_index(n_bars: int, max_horizon: int) -> int:
    """The last valid integer index into a `n_bars`-long series that still
    has a fully realized `max_horizon`-bar-ahead label -- one past this is
    where `trading_day_grid` must stop."""
    return n_bars - max_horizon - 1


def trading_day_grid(
    dates: pd.DatetimeIndex, horizons: tuple[int, ...] = DEFAULT_HORIZONS, step: int = DEFAULT_GRID_STEP_DAYS,
    warmup_bars: int = 260,
) -> list[pd.Timestamp]:
    """Every `step`-th trading day between `warmup_bars` (enough history
    for the reused trend/risk-reward engines to fit at all) and the last
    day with a fully realized label at the longest horizon. Sparser than
    daily on purpose: curve_carry.py's per-row historical fetch is a real
    network call per as_of, and a 3-year daily grid across ~24 commodities
    would mean tens of thousands of such calls -- see features.py's module
    docstring for the full tradeoff."""
    last_idx = max_as_of_index(len(dates), max(horizons))
    if last_idx <= warmup_bars:
        return []
    return [pd.Timestamp(d) for d in dates[warmup_bars:last_idx + 1:step]]


def compute_forward_label(
    dates: pd.DatetimeIndex, roll_adjusted_close: np.ndarray, as_of: pd.Timestamp, horizon: int
) -> ForwardLabel | None:
    """None if `as_of` isn't an exact trading day in `dates`, or its
    `horizon`-bar-ahead point falls outside the fetched history."""
    matches = np.flatnonzero(dates.values == np.datetime64(pd.Timestamp(as_of)))
    if len(matches) == 0:
        return None
    idx = int(matches[0])
    target_idx = idx + horizon
    if target_idx >= len(roll_adjusted_close):
        return None
    forward_return = float(np.log(roll_adjusted_close[target_idx] / roll_adjusted_close[idx]))
    return ForwardLabel(
        canonical_id="",  # filled in by build_label_panel, which knows the id this series belongs to
        as_of=pd.Timestamp(as_of), horizon_days=horizon, forward_return=forward_return,
        forward_direction=forward_return > 0,
    )


def build_label_panel(
    commodity_series: dict[str, CommoditySeries],
    horizons: tuple[int, ...] = DEFAULT_HORIZONS,
    step: int = DEFAULT_GRID_STEP_DAYS,
) -> pd.DataFrame:
    """Long-format label panel: one row per (canonical_id, as_of, horizon).
    Each commodity gets its own as-of grid from its own trading calendar
    (products don't all share identical holiday calendars) -- callers that
    need a shared grid across the universe should intersect the `as_of`
    column across commodities themselves rather than assume alignment."""
    rows = []
    for cid, series in commodity_series.items():
        grid = trading_day_grid(series.dates, horizons, step)
        for as_of in grid:
            for h in horizons:
                label = compute_forward_label(series.dates, series.roll_adjusted_close, as_of, h)
                if label is None:
                    continue
                rows.append(
                    {"canonical_id": cid, "as_of": label.as_of, "horizon_days": h,
                     "forward_return": label.forward_return, "forward_direction": label.forward_direction}
                )
    return pd.DataFrame(rows, columns=["canonical_id", "as_of", "horizon_days", "forward_return", "forward_direction"])
