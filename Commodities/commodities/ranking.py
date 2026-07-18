"""
Ranking assembly: trains one production HorizonModelSet per spec horizon
(5/21/63d) on the full historical panel, applies it to today's live
feature bundles, and assembles the ten required output fields (spec
Section 5) per commodity.

Weight derivation, the spec's central constraint here ("do not hand-
optimize weights on the full history... do not add [trend/RR] again as
arbitrary bonus points afterward"): `commodity_opportunity_score` blends
only the statistical model's own three outputs -- up_probability,
expected_return, downside_quantile -- never trend_score/carry_score/
relative_strength_score/risk_reward a second time (those already entered
the model as point-in-time features in features.py; they are display-only
columns here). The blend weights come from each component's own
out-of-sample Spearman IC against realized forward returns, measured via
the SAME walk-forward machinery as validation.py, on the 21-day (primary)
horizon -- not picked by hand. A component with a non-positive historical
IC gets zero weight rather than a negative one, since there's no
principled reading of "make the score worse when this component is
higher" for a rank ordering.

`forecast_confidence` dampens the raw score multiplicatively rather than
sitting purely as a separate diagnostic -- a deliberate design choice,
not implied by the spec, made because a ranking that can't distinguish a
well-supported call from a coin-flip is a worse ranking. It's built from
measured quality (calibration error, sample coverage, cross-horizon
agreement), never from how extreme the forecast itself looks, per the
spec's explicit warning against that shortcut.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from commodities.features import (
    FeatureBundle, UniverseData, build_feature_matrix, build_live_bundles,
    build_training_matrix, flatten_feature_row,
)
from commodities.labels import build_label_panel
from commodities.models import HorizonModelSet, fit_horizon_models, predict_direction_probability, predict_magnitude, predict_quantiles
from commodities.momentum import PairTrend
from commodities.validation import CALIBRATION_FRACTION, WalkForwardFold, calibration_error, generate_walk_forward_folds

SPEC_HORIZONS: tuple[int, ...] = (5, 21, 63)
PRIMARY_HORIZON = 21
DOWNSIDE_QUANTILE = 0.1
IC_LOOKBACK_FOLDS = 4
MODEL_QUALITY_TARGET_ROWS = 150  # sample-coverage saturation point for forecast_confidence


@dataclass(frozen=True)
class ComponentWeights:
    direction: float
    magnitude: float
    downside: float
    direction_ic: float
    magnitude_ic: float
    downside_ic: float


def _fold_component_ics(fold: WalkForwardFold) -> Optional[tuple[float, float, float, float]]:
    """One fold's (direction_ic, magnitude_ic, downside_ic, calibration_error)
    -- refits on the fold's own fit/calibration split, exactly like
    validation.run_walk_forward, so this never sees its own test data."""
    model_set = fit_horizon_models(fold.fit_df, fold.horizon_days, calibration_df=fold.calibration_df)
    if model_set is None:
        return None
    test_df = fold.test_df
    y = test_df["forward_return"].to_numpy()
    prob = predict_direction_probability(model_set, test_df)
    magnitude = predict_magnitude(model_set, test_df)
    downside = predict_quantiles(model_set, test_df)[DOWNSIDE_QUANTILE]

    dir_ic = float("nan") if np.ptp(prob) < 1e-9 else spearmanr(prob, y)[0]
    mag_ic = float("nan") if np.ptp(magnitude) < 1e-9 else spearmanr(magnitude, y)[0]
    down_ic = float("nan") if np.ptp(downside) < 1e-9 else spearmanr(downside, y)[0]
    cal_err = calibration_error(test_df["forward_direction"].astype(int).to_numpy(), np.clip(prob, 1e-6, 1 - 1e-6))
    return dir_ic, mag_ic, down_ic, cal_err


def derive_component_weights(panel: pd.DataFrame, horizon_days: int, n_folds: int = IC_LOOKBACK_FOLDS) -> tuple[ComponentWeights, float]:
    """Walks the historical panel forward exactly like validation.py and
    averages each component's out-of-sample IC across folds. Returns the
    weights plus a mean calibration_error (folded into forecast_confidence
    upstream) so the walk-forward pass isn't repeated a second time.
    Falls back to equal weights (documented, not silent) if no fold
    produced a usable IC -- e.g. too little history for this horizon yet."""
    folds = generate_walk_forward_folds(panel, horizon_days, n_folds)
    dir_ics, mag_ics, down_ics, cal_errs = [], [], [], []
    for fold in folds:
        result = _fold_component_ics(fold)
        if result is None:
            continue
        d, m, dn, c = result
        if d == d:
            dir_ics.append(d)
        if m == m:
            mag_ics.append(m)
        if dn == dn:
            down_ics.append(dn)
        if c == c:
            cal_errs.append(c)

    dir_ic = float(np.mean(dir_ics)) if dir_ics else 0.0
    mag_ic = float(np.mean(mag_ics)) if mag_ics else 0.0
    down_ic = float(np.mean(down_ics)) if down_ics else 0.0
    mean_cal_err = float(np.mean(cal_errs)) if cal_errs else float("nan")

    positive = {"direction": max(dir_ic, 0.0), "magnitude": max(mag_ic, 0.0), "downside": max(down_ic, 0.0)}
    total = sum(positive.values())
    if total < 1e-9:
        positive = {k: 1 / 3 for k in positive}  # documented fallback: no component showed positive skill
    else:
        positive = {k: v / total for k, v in positive.items()}

    weights = ComponentWeights(
        direction=positive["direction"], magnitude=positive["magnitude"], downside=positive["downside"],
        direction_ic=dir_ic, magnitude_ic=mag_ic, downside_ic=down_ic,
    )
    return weights, mean_cal_err


def _cross_sectional_z(values: dict[str, float]) -> dict[str, float]:
    ids = [k for k, v in values.items() if v == v]
    if len(ids) < 2:
        return {k: 0.0 for k in values}
    arr = np.array([values[i] for i in ids])
    std = arr.std()
    mean = arr.mean()
    z = (arr - mean) / std if std > 1e-9 else np.zeros_like(arr)
    return {i: float(zi) for i, zi in zip(ids, z)}


@dataclass(frozen=True)
class CommodityRanking:
    canonical_id: str
    family: str
    up_probability: dict[int, float]  # keyed by horizon
    expected_return: dict[int, float]
    downside_quantile: dict[int, float]
    relative_return_rank: float  # 0-100 percentile of expected_return at PRIMARY_HORIZON, universe-wide
    trend_score: Optional[float]
    carry_score: Optional[float]
    relative_strength_score: Optional[float]
    risk_reward: Optional[float]
    forecast_confidence: float
    commodity_opportunity_score: float


def _carry_score(bundle: FeatureBundle) -> Optional[float]:
    if bundle.curve is None:
        return None
    return float(np.clip(50 + bundle.curve.roll_yield_annualized * 100, 0, 100))


def _relative_strength_score(bundle: FeatureBundle) -> Optional[float]:
    snap = bundle.momentum.get(PRIMARY_HORIZON)
    if snap is None or snap.cross_sectional is None:
        return None
    return snap.cross_sectional.percentile


@dataclass(frozen=True)
class RankingRun:
    rankings: list[CommodityRanking]
    bundles: dict[str, FeatureBundle]
    pairs: list[PairTrend]
    weights_by_horizon: dict[int, ComponentWeights]
    model_sets: dict[int, HorizonModelSet]


def build_rankings(data: UniverseData, horizons: tuple[int, ...] = SPEC_HORIZONS) -> RankingRun:
    bundles, pairs = build_live_bundles(data)
    label_panel = build_label_panel(data.commodity_series)

    model_sets: dict[int, HorizonModelSet] = {}
    weights_by_horizon: dict[int, ComponentWeights] = {}
    cal_err_by_horizon: dict[int, float] = {}

    # Features are horizon-independent: compute the matrix ONCE, then merge each
    # horizon's labels onto it. This replaces calling build_training_matrix per
    # horizon (which re-ran the whole feature replay 3x). Byte-identical per-horizon
    # panels, ~3x less feature compute.
    feature_matrix = build_feature_matrix(data, label_panel)
    label_cols = ["canonical_id", "as_of", "horizon_days", "forward_return", "forward_direction"]
    for h in horizons:
        labels_h = label_panel[label_panel["horizon_days"] == h][label_cols].copy()
        if feature_matrix.empty or labels_h.empty:
            continue
        labels_h["as_of"] = pd.to_datetime(labels_h["as_of"])
        panel_h = feature_matrix.merge(labels_h, on=["canonical_id", "as_of"], how="inner")
        if panel_h.empty:
            continue
        weights, cal_err = derive_component_weights(panel_h, h)
        weights_by_horizon[h] = weights
        cal_err_by_horizon[h] = cal_err

        n_calib = max(1, int(len(panel_h) * CALIBRATION_FRACTION))
        panel_h_sorted = panel_h.sort_values("as_of")
        fit_df, calib_df = panel_h_sorted.iloc[:-n_calib], panel_h_sorted.iloc[-n_calib:]
        model_set = fit_horizon_models(fit_df, h, calibration_df=calib_df)
        if model_set is not None:
            model_sets[h] = model_set

    up_probability: dict[str, dict[int, float]] = {cid: {} for cid in bundles}
    expected_return: dict[str, dict[int, float]] = {cid: {} for cid in bundles}
    downside: dict[str, dict[int, float]] = {cid: {} for cid in bundles}
    for h, model_set in model_sets.items():
        rows = {cid: flatten_feature_row(b) for cid, b in bundles.items()}
        X = pd.DataFrame(rows).T
        X = X.reindex(columns=list(model_set.feature_names))
        prob = predict_direction_probability(model_set, X)
        mag = predict_magnitude(model_set, X)
        down = predict_quantiles(model_set, X)[DOWNSIDE_QUANTILE]
        for cid, p, m, d in zip(X.index, prob, mag, down):
            up_probability[cid][h] = float(p)
            expected_return[cid][h] = float(m)
            downside[cid][h] = float(d)

    primary_expected = {cid: expected_return[cid].get(PRIMARY_HORIZON, float("nan")) for cid in bundles}
    relative_rank = (pd.Series(primary_expected).rank(pct=True) * 100).to_dict()

    primary_weights = weights_by_horizon.get(PRIMARY_HORIZON)
    prob_z = _cross_sectional_z({cid: up_probability[cid].get(PRIMARY_HORIZON, float("nan")) for cid in bundles})
    mag_z = _cross_sectional_z(primary_expected)
    down_z = _cross_sectional_z({cid: downside[cid].get(PRIMARY_HORIZON, float("nan")) for cid in bundles})

    rankings: list[CommodityRanking] = []
    for cid, bundle in bundles.items():
        directions = [up_probability[cid][h] > 0.5 for h in up_probability[cid] if h != PRIMARY_HORIZON]
        primary_dir = up_probability[cid].get(PRIMARY_HORIZON, 0.5) > 0.5
        agreement = float(np.mean([d == primary_dir for d in directions])) if directions else float("nan")
        model_quality = float("nan")
        if primary_weights is not None:
            cal_err = cal_err_by_horizon.get(PRIMARY_HORIZON, float("nan"))
            coverage = min(1.0, model_sets[PRIMARY_HORIZON].n_train_rows / MODEL_QUALITY_TARGET_ROWS) if PRIMARY_HORIZON in model_sets else 0.0
            model_quality = float(np.clip(1 - cal_err, 0, 1)) * coverage if cal_err == cal_err else coverage
        confidence_parts = [x for x in (model_quality, agreement) if x == x]
        forecast_confidence = float(np.mean(confidence_parts)) if confidence_parts else 0.5

        raw_score = 0.0
        if primary_weights is not None:
            raw_score = (
                primary_weights.direction * prob_z.get(cid, 0.0)
                + primary_weights.magnitude * mag_z.get(cid, 0.0)
                + primary_weights.downside * down_z.get(cid, 0.0)
            )
        opportunity_score = float(np.clip(50 + 50 * np.tanh(raw_score), 0, 100)) * (0.5 + 0.5 * forecast_confidence)

        rankings.append(CommodityRanking(
            canonical_id=cid, family=bundle.family, up_probability=up_probability[cid],
            expected_return=expected_return[cid], downside_quantile=downside[cid],
            relative_return_rank=relative_rank.get(cid, float("nan")),
            trend_score=bundle.trend.opportunity if bundle.trend else None,
            carry_score=_carry_score(bundle), relative_strength_score=_relative_strength_score(bundle),
            risk_reward=bundle.risk_reward.rr_ratio if bundle.risk_reward else None,
            forecast_confidence=forecast_confidence, commodity_opportunity_score=opportunity_score,
        ))

    rankings.sort(key=lambda r: r.commodity_opportunity_score, reverse=True)
    return RankingRun(rankings=rankings, bundles=bundles, pairs=pairs, weights_by_horizon=weights_by_horizon, model_sets=model_sets)
