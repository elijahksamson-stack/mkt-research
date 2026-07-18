"""
Relative-strength ratio construction: the building block every
cross-sectional read in this package (rotation_ranking.py,
relative_technicals.py) is computed from.

A "relative-strength ratio" is simply numerator_close / denominator_close
on their aligned trading dates -- a rising line means the numerator is
outperforming the denominator regardless of what either is doing in
absolute terms. Feeding that ratio into trend_regression.regression_profile
turns "is XLK beating SPY" into the same trend_signal/opportunity read used
for an outright price series.
"""
from __future__ import annotations

import pandas as pd


def aligned_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Align two price series on their common dates and return the
    elementwise ratio numerator/denominator.

    Drops any date where either series is missing or non-positive --
    ratios involving a non-positive price are meaningless and would break
    the downstream log-regression (regression_profile takes log() of the
    series it's given).
    """
    pair = pd.concat(
        [numerator.rename("numerator"), denominator.rename("denominator")],
        axis=1,
        join="inner",
    ).dropna()
    pair = pair[(pair["numerator"] > 0) & (pair["denominator"] > 0)]
    return pair["numerator"] / pair["denominator"]


def rolling_ratio_average(ratio: pd.Series, window: int) -> pd.Series:
    """Simple moving average of a ratio series, min_periods=window so the
    warm-up period returns NaN rather than a noisy partial-window average."""
    return ratio.rolling(window=window, min_periods=window).mean()
