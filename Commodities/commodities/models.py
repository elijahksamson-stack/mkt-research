"""
Interpretable ensemble: Elastic-Net logistic regression for calibrated
direction probability, Huber regression for expected-return magnitude, and
linear quantile regression for the downside/median/upside distribution --
one `HorizonModelSet` per forecast horizon, per the spec's Section 4.

Every estimator is linear and every feature is standardized inside the
same `Pipeline`, so `top_feature_contributions` can read coefficients
directly off the fitted model in a mutually comparable scale -- no SHAP,
no post-hoc explainer, because the model itself is the explanation. This
is the deliberate tradeoff the spec asks for ("transparent statistical
framework rather than a black-box forecast"): a shallow gradient-boosted
challenger may be added later, but only after this linear baseline has a
credible out-of-sample track record (validation.py), never as the first
model built.

Two naive benchmarks live here rather than in validation.py because they
need the same fitted `train_base_rate` / feature-column contract as the
real models to be compared apples-to-apples: `naive_constant_probability`
(always predict the training set's realized up-rate) and
`naive_momentum_rule` (sign of trailing 63-day vol-adjusted momentum,
already computed by momentum.py -- no new logic, just a lookup).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.impute import SimpleImputer
from sklearn.linear_model import HuberRegressor, LogisticRegression, QuantileRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

NON_FEATURE_COLUMNS = {"canonical_id", "family", "as_of", "horizon_days", "forward_return", "forward_direction"}
QUANTILES: tuple[float, ...] = (0.1, 0.5, 0.9)
QUANTILE_ALPHA = 0.05  # QuantileRegressor's L1 regularization strength
DIRECTION_L1_RATIO = 0.5
DIRECTION_C = 1.0
MOMENTUM_RULE_COLUMN = "mom_63d_vol_adj_return"
MIN_TRAIN_ROWS = 30
MIN_CALIBRATION_ROWS = 15


def feature_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in NON_FEATURE_COLUMNS]


def _base_pipeline(estimator) -> Pipeline:
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("model", estimator),
    ])


def build_direction_pipeline() -> Pipeline:
    # sklearn >=1.8: passing l1_ratio as a float implies elastic-net penalty directly;
    # the explicit penalty="elasticnet" kwarg is deprecated (see sklearn's own FutureWarning).
    return _base_pipeline(
        LogisticRegression(l1_ratio=DIRECTION_L1_RATIO, C=DIRECTION_C, solver="saga", max_iter=2000)
    )


def build_magnitude_pipeline() -> Pipeline:
    return _base_pipeline(HuberRegressor(max_iter=2000))


def build_quantile_pipeline(quantile: float) -> Pipeline:
    return _base_pipeline(QuantileRegressor(quantile=quantile, alpha=QUANTILE_ALPHA, solver="highs"))


@dataclass(frozen=True)
class HorizonModelSet:
    horizon_days: int
    feature_names: tuple[str, ...]
    direction_pipeline: Pipeline  # uncalibrated -- kept for coefficient introspection
    direction_calibrator: Optional[CalibratedClassifierCV]  # None if too little data to hold out a calibration slice
    magnitude_pipeline: Pipeline
    quantile_pipelines: dict[float, Pipeline]
    train_base_rate: float
    n_train_rows: int


def fit_horizon_models(
    train_df: pd.DataFrame,
    horizon_days: int,
    calibration_df: Optional[pd.DataFrame] = None,
    quantiles: tuple[float, ...] = QUANTILES,
) -> Optional[HorizonModelSet]:
    """Fits all three model heads for one horizon on `train_df` (rows
    already filtered to `horizon_days` by the caller -- see validation.py).
    `calibration_df` should be a chronologically LATER, disjoint slice
    (validation.py's walk-forward split enforces this); direction
    probabilities are calibrated against it with sigmoid (Platt) scaling.
    Returns None below MIN_TRAIN_ROWS -- too little data to fit anything
    meaningfully."""
    rows = train_df[train_df["horizon_days"] == horizon_days]
    if len(rows) < MIN_TRAIN_ROWS:
        return None
    cols = feature_columns(rows)
    X = rows[cols]
    y_dir = rows["forward_direction"].astype(int)
    y_mag = rows["forward_return"].astype(float)

    direction_pipeline = build_direction_pipeline()
    direction_pipeline.fit(X, y_dir)

    direction_calibrator = None
    if calibration_df is not None:
        calib_rows = calibration_df[calibration_df["horizon_days"] == horizon_days]
        if len(calib_rows) >= MIN_CALIBRATION_ROWS:
            # FrozenEstimator marks direction_pipeline as already-fit, so CalibratedClassifierCV
            # only fits the sigmoid calibration map on calib_rows -- the sklearn >=1.6 replacement
            # for the removed cv="prefit" API.
            direction_calibrator = CalibratedClassifierCV(FrozenEstimator(direction_pipeline), method="sigmoid")
            direction_calibrator.fit(calib_rows[cols], calib_rows["forward_direction"].astype(int))

    magnitude_pipeline = build_magnitude_pipeline()
    magnitude_pipeline.fit(X, y_mag)

    quantile_pipelines = {}
    for q in quantiles:
        pipe = build_quantile_pipeline(q)
        pipe.fit(X, y_mag)
        quantile_pipelines[q] = pipe

    return HorizonModelSet(
        horizon_days=horizon_days, feature_names=tuple(cols), direction_pipeline=direction_pipeline,
        direction_calibrator=direction_calibrator, magnitude_pipeline=magnitude_pipeline,
        quantile_pipelines=quantile_pipelines, train_base_rate=float(y_dir.mean()), n_train_rows=len(rows),
    )


def predict_direction_probability(model_set: HorizonModelSet, X: pd.DataFrame) -> np.ndarray:
    X = X[list(model_set.feature_names)]
    estimator = model_set.direction_calibrator or model_set.direction_pipeline
    return estimator.predict_proba(X)[:, 1]


def predict_magnitude(model_set: HorizonModelSet, X: pd.DataFrame) -> np.ndarray:
    return model_set.magnitude_pipeline.predict(X[list(model_set.feature_names)])


def predict_quantiles(model_set: HorizonModelSet, X: pd.DataFrame) -> dict[float, np.ndarray]:
    X = X[list(model_set.feature_names)]
    return {q: pipe.predict(X) for q, pipe in model_set.quantile_pipelines.items()}


def top_feature_contributions(model_set: HorizonModelSet, n: int = 5) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
    """Top-n positive and negative standardized coefficients from the
    direction model -- legible by construction since every feature was
    z-scored by the same pipeline before fitting, so coefficients are
    directly comparable in magnitude."""
    coefs = model_set.direction_pipeline.named_steps["model"].coef_[0]
    pairs = sorted(zip(model_set.feature_names, coefs), key=lambda p: p[1])
    negative = [p for p in pairs if p[1] < 0][:n]
    positive = [p for p in reversed(pairs) if p[1] > 0][:n]
    return positive, negative


def naive_constant_probability(model_set: HorizonModelSet, n_rows: int) -> np.ndarray:
    return np.full(n_rows, model_set.train_base_rate)


def naive_momentum_rule(df: pd.DataFrame, momentum_column: str = MOMENTUM_RULE_COLUMN) -> np.ndarray:
    """Hard 0/1 directional call from the sign of trailing 63-day
    vol-adjusted momentum -- a rule, not a probabilistic model, matching
    the spec's "simple multi-horizon momentum rule" benchmark. NaN
    momentum (missing history) maps to 0.5 (no call)."""
    values = df[momentum_column].to_numpy()
    calls = np.where(np.isnan(values), 0.5, (values > 0).astype(float))
    return calls
