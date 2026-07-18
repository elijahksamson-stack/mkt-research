"""
Absolute, cross-sectional, family-relative, and residual momentum, plus
pair-ratio trends for economically linked markets.

Distinct from `trend_adapter.py` on purpose: trend_adapter wraps the
reused HAC-regression Trend Analysis engine (fit quality, channel
asymmetry, persistence). This module is the spec's separate "Absolute and
Relative Momentum" signal family -- plain vol-scaled realized returns and
their cross-sectional comparison, which the regression engine doesn't
produce. Pair-ratio trends *do* reuse the regression engine
(`rates_macro.trend_rr.trend_rr_profile`) applied to a ratio series,
rather than inventing a second trend-fitting method for pairs.

Every function here is point-in-time safe: they take a `return_matrix`
(dates x commodity_id daily log returns) and an `as_of` cutoff, and only
ever look at `return_matrix.loc[:as_of]`. `features.py` relies on this to
build historical training rows without leakage -- calling these functions
with the true "today" cutoff for a live ranking is just the `as_of=None`
default.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from rates_macro.trend_rr import trend_rr_profile
from sklearn.linear_model import LinearRegression

from commodities.market_data import CommoditySeries
from commodities.universe import CANONICAL_PAIRS, CommodityInstrument, by_family

MOMENTUM_HORIZONS: tuple[int, ...] = (5, 21, 63, 126)
VOL_WINDOW = 20
RESIDUAL_LOOKBACK = 252
MIN_RESIDUAL_LOOKBACK = 60
WINSORIZE_LIMIT = 0.05


@dataclass(frozen=True)
class NormalizedScore:
    value: float
    winsorized_z: float
    percentile: float  # 0-100


def build_return_matrix(commodity_series: dict[str, CommoditySeries]) -> pd.DataFrame:
    """Daily log-return matrix (dates x canonical_id) from each series'
    roll-adjusted close -- outer-joined on date, so products with slightly
    different trading calendars/holidays still align correctly (missing
    days are NaN, not silently misaligned)."""
    columns = {}
    for cid, s in commodity_series.items():
        log_ret = np.diff(np.log(s.roll_adjusted_close))
        columns[cid] = pd.Series(log_ret, index=pd.DatetimeIndex(s.dates[1:]))
    return pd.DataFrame(columns).sort_index()


def _window(return_matrix: pd.DataFrame, as_of: Optional[pd.Timestamp]) -> pd.DataFrame:
    return return_matrix if as_of is None else return_matrix.loc[:as_of]


def vol_adjusted_horizon_return(
    return_matrix: pd.DataFrame, canonical_id: str, horizon: int, as_of: Optional[pd.Timestamp] = None,
    vol_window: int = VOL_WINDOW,
) -> float:
    """Cumulative log return over the trailing `horizon` bars, scaled by
    trailing realized vol projected to the same horizon (sqrt-time) --
    the standard time-series-momentum normalization (Moskowitz, Ooi &
    Pedersen 2012), so a 5% move in a low-vol product and a 5% move in a
    high-vol product aren't treated as equally significant."""
    if canonical_id not in return_matrix.columns:
        return float("nan")
    series = _window(return_matrix, as_of)[canonical_id].dropna()
    if len(series) < max(horizon, vol_window) + 1:
        return float("nan")
    cum_return = float(series.tail(horizon).sum())
    daily_vol = float(series.tail(vol_window).std())
    horizon_vol = daily_vol * np.sqrt(horizon)
    if horizon_vol < 1e-9:
        return float("nan")
    return cum_return / horizon_vol


def cross_sectional_normalize(values: dict[str, float]) -> dict[str, NormalizedScore]:
    """Winsorized z-score + percentile rank across whatever set of ids is
    passed in -- caller decides universe-wide vs. family-only by which
    dict it builds (see build_momentum_snapshot)."""
    ids = [k for k, v in values.items() if v is not None and not np.isnan(v)]
    if not ids:
        return {}
    arr = np.array([values[i] for i in ids], dtype=float)
    lo, hi = np.quantile(arr, [WINSORIZE_LIMIT, 1 - WINSORIZE_LIMIT])
    clipped = np.clip(arr, lo, hi)
    std = clipped.std()
    mean = clipped.mean()
    z = (clipped - mean) / std if std > 1e-12 else np.zeros_like(clipped)
    ranks = pd.Series(arr).rank(pct=True).to_numpy() * 100.0
    return {i: NormalizedScore(value=float(v), winsorized_z=float(zi), percentile=float(p))
            for i, v, zi, p in zip(ids, arr, z, ranks)}


def residual_momentum(
    return_matrix: pd.DataFrame,
    universe: dict[str, CommodityInstrument],
    canonical_id: str,
    horizon: int,
    as_of: Optional[pd.Timestamp] = None,
    lookback: int = RESIDUAL_LOOKBACK,
) -> float:
    """Cumulative return over the trailing `horizon` bars left over after
    regressing daily returns on the commodity's family-average and
    broad-universe-average daily returns (OLS over the trailing `lookback`
    bars). Approximation: the family/broad averages include the commodity
    itself -- with a ~24-name universe this self-weight is small (~4-8%
    within a family, ~4% broad) and is accepted rather than recomputing a
    separate leave-one-out average per commodity per call. Returns NaN
    below MIN_RESIDUAL_LOOKBACK bars of history."""
    if canonical_id not in return_matrix.columns:
        return float("nan")
    inst = universe.get(canonical_id)
    family_ids = [c for c in by_family(inst.family, universe) if c in return_matrix.columns] if inst else []

    window = _window(return_matrix, as_of).tail(lookback)
    own = window[canonical_id]
    broad = window[[c for c in return_matrix.columns]].mean(axis=1)
    family = window[family_ids].mean(axis=1) if family_ids else broad

    frame = pd.DataFrame({"own": own, "family": family, "broad": broad}).dropna()
    if len(frame) < MIN_RESIDUAL_LOOKBACK or len(frame) <= horizon:
        return float("nan")

    model = LinearRegression()
    model.fit(frame[["family", "broad"]].to_numpy(), frame["own"].to_numpy())
    fitted = model.predict(frame[["family", "broad"]].to_numpy())
    residuals = frame["own"].to_numpy() - fitted
    return float(np.sum(residuals[-horizon:]))


@dataclass(frozen=True)
class MomentumSnapshot:
    canonical_id: str
    horizon_days: int
    vol_adjusted_return: float
    cross_sectional: Optional[NormalizedScore]
    family_relative: Optional[NormalizedScore]
    residual_momentum: float


def build_momentum_table(
    return_matrix: pd.DataFrame,
    universe: dict[str, CommodityInstrument],
    as_of: Optional[pd.Timestamp] = None,
    horizons: tuple[int, ...] = MOMENTUM_HORIZONS,
) -> dict[str, dict[int, MomentumSnapshot]]:
    """Full momentum table: {canonical_id: {horizon: MomentumSnapshot}}.
    Cross-sectional and family-relative normalization are computed once per
    horizon across the whole universe snapshot, then attached back to each
    id -- this is the point where "absolute momentum" becomes "relative to
    what" per the spec's four momentum sub-signals."""
    table: dict[str, dict[int, MomentumSnapshot]] = {cid: {} for cid in universe}
    for h in horizons:
        raw = {cid: vol_adjusted_horizon_return(return_matrix, cid, h, as_of) for cid in universe}
        universe_norm = cross_sectional_normalize(raw)
        for family in {c.family for c in universe.values()}:
            members = by_family(family, universe)
            family_raw = {cid: raw[cid] for cid in members if cid in raw}
            family_norm = cross_sectional_normalize(family_raw)
            for cid in members:
                resid = residual_momentum(return_matrix, universe, cid, h, as_of)
                table[cid][h] = MomentumSnapshot(
                    canonical_id=cid,
                    horizon_days=h,
                    vol_adjusted_return=raw.get(cid, float("nan")),
                    cross_sectional=universe_norm.get(cid),
                    family_relative=family_norm.get(cid),
                    residual_momentum=resid,
                )
    return table


@dataclass(frozen=True)
class PairTrend:
    numerator_id: str
    denominator_id: str
    ratio_last: float
    trend_signal: float
    opportunity: float


def build_pair_trends(
    commodity_series: dict[str, CommoditySeries],
    pairs: tuple[tuple[str, str], ...] = CANONICAL_PAIRS,
    as_of: Optional[pd.Timestamp] = None,
) -> list[PairTrend]:
    """Trend-analysis (reused HAC regression) applied to the ratio series
    of each economically linked pair, e.g. WTI/Brent, Gold/Silver,
    Copper/Gold, Corn/Wheat. Skips a pair if either leg is missing from
    `commodity_series` or the aligned ratio history is too short for
    trend_rr_profile to fit any window."""
    results: list[PairTrend] = []
    for num_id, den_id in pairs:
        if num_id not in commodity_series or den_id not in commodity_series:
            continue
        num = commodity_series[num_id]
        den = commodity_series[den_id]
        num_series = pd.Series(num.roll_adjusted_close, index=pd.DatetimeIndex(num.dates))
        den_series = pd.Series(den.roll_adjusted_close, index=pd.DatetimeIndex(den.dates))
        if as_of is not None:
            num_series = num_series.loc[:as_of]
            den_series = den_series.loc[:as_of]
        ratio = (num_series / den_series).dropna()
        if len(ratio) < 24:
            continue
        try:
            profile = trend_rr_profile(ratio)
        except ValueError:
            continue
        results.append(
            PairTrend(
                numerator_id=num_id, denominator_id=den_id, ratio_last=float(ratio.iloc[-1]),
                trend_signal=profile["trend_signal"], opportunity=profile["opportunity"],
            )
        )
    return results
