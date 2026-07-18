"""
Point-in-time feature matrix assembly -- the integration layer joining
every signal family (trend, risk/reward, momentum, curve/carry,
mean-reversion, positioning, seasonality, macro controls) into one row per
(commodity, as_of).

Two entry points:

- `build_live_bundles(universe_data)` -- one FeatureBundle per commodity
  at "today," for `ranking.py`. Fast: no historical replay, one curve
  fetch per commodity.
- `build_training_matrix(universe_data, label_panel)` -- a flat numeric
  DataFrame (one row per (commodity, as_of, horizon) x feature columns +
  forward_return/forward_direction), for `models.py`/`validation.py`.

Performance/coverage note, confirmed empirically during this build (not
speculative): every signal family except curve/carry is pure math over
data fetched *once* up front (`UniverseData`) and sliced per as_of --
cheap and fully historical. curve_carry.py is the exception, and worse
than a performance cost: Yahoo Finance only serves history for
dated-contract symbols currently among a product's near listed months --
an expired, rolled-off contract returns empty data for *any* date range,
even dates during its real trading life. Practically, this makes
curve/carry a **live-only** feature family with this data source --
`build_training_matrix`'s historical rows will have curve_* columns as
NaN for most of a multi-year window, by design, not by bug (see
`market_data.fetch_dated_contract_close`'s docstring for the confirming
evidence). `models.py` must not assume curve/carry has meaningful
training coverage; it will still be fully populated for `build_live_bundles`'s
"today" snapshot, which is what `ranking.py` actually shows a user.

Missing-data policy, applied uniformly: any signal family that a
commodity structurally lacks (curve/carry and positioning for the uranium
ETF proxy; a cointegration snapshot for a commodity with no configured
pair; a trend/risk-reward read below the reused engines' own minimum-bar
gates) produces NaN in the flattened row, never a fabricated zero or
neutral value. `models.py` is expected to handle NaN via imputation or
NaN-tolerant estimators, not have missingness silently disappear here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from market_structure.market_data import OHLCV

from commodities.curve_carry import CommodityCurve, build_curve
from commodities.labels import build_label_panel
from commodities.macro_controls import MacroSeriesSnapshot, build_macro_snapshot, fetch_macro_series
from commodities.market_data import CommoditySeries, fetch_commodity_series, fetch_continuous_ohlcv
from commodities.mean_reversion import Displacement, build_displacement
from commodities.momentum import MomentumSnapshot, PairTrend, build_momentum_table, build_pair_trends, build_return_matrix
from commodities.positioning import PositioningSnapshot, build_positioning_snapshot, fetch_cot_history
from commodities.risk_reward_adapter import CommodityRiskReward, build_commodity_risk_reward
from commodities.seasonality import SeasonalSnapshot, build_seasonal_snapshot
from commodities.trend_adapter import CommodityTrend, build_commodity_trend
from commodities.universe import CommodityInstrument, default_universe

SEASONALITY_HORIZONS: tuple[int, ...] = (5, 21, 63)


@dataclass(frozen=True)
class UniverseData:
    universe: dict[str, CommodityInstrument]
    commodity_series: dict[str, CommoditySeries]
    raw_ohlcv: dict[str, OHLCV]
    return_matrix: pd.DataFrame
    cot_history: dict[str, pd.DataFrame]
    macro_series: dict[str, pd.Series]


def fetch_universe_data(universe: Optional[dict[str, CommodityInstrument]] = None, period: str = "3y") -> UniverseData:
    """Fetches everything reusable across every (commodity, as_of) pair,
    exactly once. Per-commodity fetch failures are isolated (skipped, not
    fatal) -- matching market_structure.report's convention of never
    letting one bad ticker sink the whole run."""
    universe = universe or default_universe()
    commodity_series: dict[str, CommoditySeries] = {}
    raw_ohlcv: dict[str, OHLCV] = {}
    for cid, inst in universe.items():
        try:
            commodity_series[cid] = fetch_commodity_series(inst, period=period)
            raw_ohlcv[cid] = fetch_continuous_ohlcv(inst.continuous_symbol, period=period)
        except Exception:
            continue

    return_matrix = build_return_matrix(commodity_series)
    cot_history = {
        cid: fetch_cot_history(inst.cftc_market_name) for cid, inst in universe.items() if inst.is_tradable_future
    }
    macro_series = fetch_macro_series(period)

    return UniverseData(
        universe=universe, commodity_series=commodity_series, raw_ohlcv=raw_ohlcv,
        return_matrix=return_matrix, cot_history=cot_history, macro_series=macro_series,
    )


def _slice_ohlcv(ohlcv: OHLCV, as_of: Optional[pd.Timestamp]) -> OHLCV:
    if as_of is None:
        return ohlcv
    idx = int(np.searchsorted(ohlcv.dates.values, np.datetime64(pd.Timestamp(as_of)), side="right"))
    return OHLCV(
        ticker=ohlcv.ticker, dates=ohlcv.dates[:idx], high=ohlcv.high[:idx], low=ohlcv.low[:idx],
        close=ohlcv.close[:idx], volume=ohlcv.volume[:idx],
    )


def _slice_series(series: CommoditySeries, as_of: Optional[pd.Timestamp]) -> CommoditySeries:
    if as_of is None:
        return series
    idx = int(np.searchsorted(series.dates.values, np.datetime64(pd.Timestamp(as_of)), side="right"))
    return CommoditySeries(
        canonical_id=series.canonical_id, continuous_symbol=series.continuous_symbol, dates=series.dates[:idx],
        raw_close=series.raw_close[:idx], roll_adjusted_close=series.roll_adjusted_close[:idx],
        roll_events=tuple(e for e in series.roll_events if e.date <= pd.Timestamp(as_of)),
    )


@dataclass(frozen=True)
class FeatureBundle:
    canonical_id: str
    family: str
    as_of: pd.Timestamp
    trend: Optional[CommodityTrend]
    risk_reward: Optional[CommodityRiskReward]
    momentum: dict[int, MomentumSnapshot]
    curve: Optional[CommodityCurve]
    displacement: Optional[Displacement]
    positioning: Optional[PositioningSnapshot]
    seasonality: dict[int, Optional[SeasonalSnapshot]]
    macro: dict[str, MacroSeriesSnapshot]


def _build_one_bundle(
    inst: CommodityInstrument,
    as_of: Optional[pd.Timestamp],
    data: UniverseData,
    momentum_table_row: dict[int, MomentumSnapshot],
    macro_snapshots: dict[str, MacroSeriesSnapshot],
    include_curve: bool = True,
) -> Optional[FeatureBundle]:
    cid = inst.canonical_id
    if cid not in data.commodity_series or cid not in data.raw_ohlcv:
        return None
    series = _slice_series(data.commodity_series[cid], as_of)
    ohlcv = _slice_ohlcv(data.raw_ohlcv[cid], as_of)
    if len(series.dates) < 60 or len(ohlcv.dates) < 60:
        return None

    trend: Optional[CommodityTrend] = None
    try:
        trend = build_commodity_trend(cid, series.roll_adjusted_close, series.dates)
    except ValueError:
        pass

    risk_reward: Optional[CommodityRiskReward] = None
    try:
        risk_reward = build_commodity_risk_reward(cid, ohlcv)
    except Exception:
        pass

    # include_curve=False skips the network fetch entirely for historical as_of -- confirmed
    # empirically (see market_data.fetch_dated_contract_close's docstring) that Yahoo has no
    # data for most historical dated contracts anyway, so build_training_matrix defaults this
    # off rather than pay the request cost for what is, in practice, almost always None.
    curve = build_curve(inst, as_of=as_of.date() if as_of is not None else None) if include_curve else None
    displacement = build_displacement(cid, ohlcv.high, ohlcv.low, ohlcv.close)

    positioning = None
    if cid in data.cot_history:
        positioning = build_positioning_snapshot(cid, data.cot_history[cid], as_of=as_of)

    seasonality = {
        h: build_seasonal_snapshot(cid, series.dates, series.roll_adjusted_close, horizon=h, as_of=as_of)
        for h in SEASONALITY_HORIZONS
    }

    return FeatureBundle(
        canonical_id=cid, family=inst.family, as_of=pd.Timestamp(as_of) if as_of is not None else series.dates[-1],
        trend=trend, risk_reward=risk_reward, momentum=momentum_table_row, curve=curve,
        displacement=displacement, positioning=positioning, seasonality=seasonality, macro=macro_snapshots,
    )


def _bundles_for_as_of(data: UniverseData, as_of: Optional[pd.Timestamp], include_curve: bool = True) -> dict[str, FeatureBundle]:
    momentum_table = build_momentum_table(data.return_matrix, data.universe, as_of=as_of)
    macro_snapshots: dict[str, MacroSeriesSnapshot] = {}
    for name, series in data.macro_series.items():
        snap = build_macro_snapshot(name, series, as_of.date() if as_of is not None else None)
        if snap is not None:
            macro_snapshots[name] = snap

    bundles: dict[str, FeatureBundle] = {}
    for cid, inst in data.universe.items():
        bundle = _build_one_bundle(inst, as_of, data, momentum_table.get(cid, {}), macro_snapshots, include_curve=include_curve)
        if bundle is not None:
            bundles[cid] = bundle
    return bundles


def build_live_bundles(data: UniverseData) -> tuple[dict[str, FeatureBundle], list[PairTrend]]:
    """Feature bundles for every commodity as of "today" (the most recent
    fetched bar), plus the pair-ratio trend table -- what ranking.py and
    report.py consume for a live snapshot. Curve/carry IS fetched here
    (include_curve=True, the default) since "today" is exactly the case
    where Yahoo has the data -- see build_training_matrix for the opposite
    default."""
    bundles = _bundles_for_as_of(data, as_of=None)
    pairs = build_pair_trends(data.commodity_series)
    return bundles, pairs


def build_feature_matrix(
    data: UniverseData, label_panel: Optional[pd.DataFrame] = None, include_curve: bool = False
) -> pd.DataFrame:
    """One row per (canonical_id, as_of) of horizon-INDEPENDENT features.

    Features never depend on the forecast horizon -- only labels do -- so
    this is computed exactly once and reused across every horizon (see
    build_training_matrix / ranking.build_rankings). Groups by as_of so each
    date's universe-wide momentum table + macro snapshot is built once and
    reused across that date's commodities.

    `include_curve` defaults False for the same reason build_training_matrix
    does: historical dated-contract curve fetches are almost always empty and
    each miss is a real network round-trip.
    """
    label_panel = label_panel if label_panel is not None else build_label_panel(data.commodity_series)
    if label_panel.empty:
        return pd.DataFrame()

    rows: list[dict] = []
    for as_of in sorted(label_panel["as_of"].unique()):
        as_of_ts = pd.Timestamp(as_of)
        bundles = _bundles_for_as_of(data, as_of=as_of_ts, include_curve=include_curve)
        for cid, bundle in bundles.items():
            feature_row = flatten_feature_row(bundle)
            feature_row.update(canonical_id=cid, family=data.universe[cid].family, as_of=as_of_ts)
            rows.append(feature_row)
    return pd.DataFrame(rows)


NUMERIC_FIELD_PATHS: tuple[str, ...] = (
    "trend.trend_signal", "trend.opportunity", "trend.persistence",
    "trend.mean_reversion_z", "trend.mean_reversion_percentile",
    "risk_reward.rr_ratio",
    "curve.front_second_annualized", "curve.front_third_annualized", "curve.curvature",
    "curve.roll_yield_annualized", "curve.front_second_annualized_change",
    "displacement.bollinger_z", "displacement.atr_displacement",
    "positioning.managed_money_net_zscore", "positioning.managed_money_net_percentile",
    "positioning.managed_money_net_weekly_change", "positioning.producer_merchant_net_zscore",
    "positioning.producer_merchant_net_percentile", "positioning.producer_merchant_net_weekly_change",
)


def _get_path(obj, path: str) -> float:
    value = obj
    for part in path.split("."):
        if value is None:
            return float("nan")
        value = getattr(value, part, None)
    return float("nan") if value is None else float(value)


def flatten_feature_row(bundle: FeatureBundle) -> dict[str, float]:
    """Flattens a FeatureBundle into the numeric dict models.py trains on.
    Categorical fields (target_source, curve_state, trend_violation_status)
    become explicit binary flags rather than being dropped, so the model
    can still use them; the underlying objects on FeatureBundle remain
    available for report.py's narrative rendering."""
    row: dict[str, float] = {p.replace(".", "_"): _get_path(bundle, p) for p in NUMERIC_FIELD_PATHS}

    for h, ht in (bundle.trend.horizons.items() if bundle.trend else {}):
        row[f"trend_{h}d_r2"] = ht.r2
        row[f"trend_{h}d_t_hac"] = ht.t_hac
        row[f"trend_{h}d_residual_z"] = ht.residual_z
        row[f"trend_{h}d_forecast_return"] = ht.forecast_return
        row[f"trend_{h}d_channel_rr"] = ht.channel_rr

    for h, m in bundle.momentum.items():
        row[f"mom_{h}d_vol_adj_return"] = m.vol_adjusted_return
        row[f"mom_{h}d_cross_sectional_pct"] = m.cross_sectional.percentile if m.cross_sectional else float("nan")
        row[f"mom_{h}d_family_pct"] = m.family_relative.percentile if m.family_relative else float("nan")
        row[f"mom_{h}d_residual"] = m.residual_momentum

    for h, s in bundle.seasonality.items():
        row[f"seasonal_{h}d_mean_return"] = s.mean_return if s else float("nan")
        row[f"seasonal_{h}d_hit_rate"] = s.hit_rate if s else float("nan")

    for name, snap in bundle.macro.items():
        row[f"macro_{name}_level"] = snap.level
        row[f"macro_{name}_change_63d"] = snap.change_63d if snap.change_63d is not None else float("nan")
        row[f"macro_{name}_trend_signal"] = snap.trend_signal if snap.trend_signal is not None else float("nan")

    row["rr_actionable"] = float(bundle.risk_reward.actionable) if bundle.risk_reward else float("nan")
    row["rr_target_quality"] = (
        {"cluster": 1.0, "trendline": 0.85, "fib_extension": 0.70, "synthetic": 0.50}.get(
            bundle.risk_reward.target_source, float("nan")
        ) if bundle.risk_reward else float("nan")
    )
    row["rr_undercut"] = (
        float(bundle.risk_reward.trend_violation_status == "undercut") if bundle.risk_reward else float("nan")
    )
    row["curve_is_backwardation"] = float(bundle.curve.curve_state == "backwardation") if bundle.curve else float("nan")
    row["curve_is_contango"] = float(bundle.curve.curve_state == "contango") if bundle.curve else float("nan")
    row["mean_reversion_active"] = float(bundle.displacement.mean_reversion_active) if bundle.displacement else float("nan")
    row["range_bound"] = (
        float(bundle.displacement.range_bound.is_range_bound) if bundle.displacement else float("nan")
    )
    return row


def build_training_matrix(
    data: UniverseData, label_panel: Optional[pd.DataFrame] = None, include_curve: bool = False
) -> pd.DataFrame:
    """One row per (canonical_id, as_of, horizon_days): flattened features
    joined to the forward_return/forward_direction label. Groups by as_of
    so each date's universe-wide momentum table/macro snapshot is computed
    once and reused across that date's commodities (see module docstring
    on why per-date, not per-row, is the right granularity).

    `include_curve` defaults False: historical curve/carry fetches are, in
    practice, almost always empty (see market_data.fetch_dated_contract_close's
    docstring) and each miss is still a real network round-trip, so paying
    that cost by default across a multi-year x ~24-commodity panel would
    make this function impractically slow for what it returns. Pass True
    only if curve/carry training coverage specifically needs to be
    (re-)measured -- expect it to still come back mostly NaN."""
    label_panel = label_panel if label_panel is not None else build_label_panel(data.commodity_series)
    if label_panel.empty:
        return label_panel

    rows: list[dict] = []
    for as_of, group in label_panel.groupby("as_of"):
        bundles = _bundles_for_as_of(data, as_of=as_of, include_curve=include_curve)
        for _, label_row in group.iterrows():
            bundle = bundles.get(label_row["canonical_id"])
            if bundle is None:
                continue
            feature_row = flatten_feature_row(bundle)
            feature_row.update(
                canonical_id=label_row["canonical_id"], family=data.universe[label_row["canonical_id"]].family,
                as_of=as_of, horizon_days=label_row["horizon_days"],
                forward_return=label_row["forward_return"], forward_direction=label_row["forward_direction"],
            )
            rows.append(feature_row)
    return pd.DataFrame(rows)
