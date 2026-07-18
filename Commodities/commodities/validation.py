"""
Leakage-safe walk-forward validation: expanding-window folds with an
embargo gap, evaluated against both the fitted model and the two naive
benchmarks from models.py, per the spec's Section 6.

Embargo, stated precisely: `labels.py`'s as-of grid is spaced by trading
days but this module reasons in calendar days (the panel only carries
`as_of` timestamps, not each commodity's own trading-day index), so the
embargo converts `horizon_days` trading days to calendar days via a
5-trading-day-per-7-calendar-day approximation
(`_trading_days_to_calendar_days`). This is intentionally conservative
(rounds up) -- a slightly wider embargo than strictly necessary is the
safe direction to err in; a narrower one risks leakage.

Every metric here is computed on one fold's test set at a time and
returned per-fold, not pre-averaged, so `block_bootstrap_ci` can be
applied across folds/rows by the caller without re-deriving per-row
values -- daily/overlapping-horizon observations are serially dependent,
which is exactly why the spec asks for block-bootstrap rather than a
naive iid confidence interval.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import brier_score_loss, log_loss, mean_absolute_error, mean_pinball_loss

from commodities.models import (
    HorizonModelSet, fit_horizon_models, naive_constant_probability, naive_momentum_rule,
    predict_direction_probability, predict_magnitude, predict_quantiles,
)

CALIBRATION_FRACTION = 0.15
TOP_QUINTILE = 0.2
CALIBRATION_BINS = 10
BOOTSTRAP_BLOCK_SIZE = 5
BOOTSTRAP_N = 500
BOOTSTRAP_CI = 0.90


def _trading_days_to_calendar_days(trading_days: int) -> int:
    return math.ceil(trading_days * 7 / 5)


@dataclass(frozen=True)
class WalkForwardFold:
    fold_index: int
    horizon_days: int
    fit_df: pd.DataFrame
    calibration_df: pd.DataFrame
    test_df: pd.DataFrame


def generate_walk_forward_folds(
    panel: pd.DataFrame, horizon_days: int, n_folds: int = 4, calibration_fraction: float = CALIBRATION_FRACTION,
) -> list[WalkForwardFold]:
    """Expanding-window folds: fold i trains on blocks 0..i of the as-of
    timeline and tests on block i+1, with an embargo dropping any test row
    whose window could overlap the train cutoff. A fold is skipped (not
    padded/faked) if the embargo leaves no test rows -- see the spec's
    "reject added complexity unless it improves multiple out-of-sample
    windows" spirit: an empty fold is signal, not something to paper over."""
    rows = panel[panel["horizon_days"] == horizon_days].sort_values("as_of")
    unique_as_of = sorted(rows["as_of"].unique())
    if len(unique_as_of) < n_folds + 1:
        return []

    block_edges = np.linspace(0, len(unique_as_of), n_folds + 1, dtype=int)
    blocks = [unique_as_of[block_edges[i]:block_edges[i + 1]] for i in range(n_folds)]
    embargo_days = _trading_days_to_calendar_days(horizon_days)

    folds: list[WalkForwardFold] = []
    for i in range(n_folds - 1):
        train_dates = [d for block in blocks[: i + 1] for d in block]
        test_block = blocks[i + 1]
        if not train_dates or not test_block:
            continue
        train_end = pd.Timestamp(train_dates[-1])
        test_dates = [d for d in test_block if (pd.Timestamp(d) - train_end).days >= embargo_days]
        if not test_dates:
            continue

        n_calib = max(1, int(len(train_dates) * calibration_fraction))
        fit_dates, calib_dates = train_dates[:-n_calib], train_dates[-n_calib:]
        if not fit_dates:
            continue

        fit_df = rows[rows["as_of"].isin(fit_dates)]
        calib_df = rows[rows["as_of"].isin(calib_dates)]
        test_df = rows[rows["as_of"].isin(test_dates)]
        folds.append(WalkForwardFold(fold_index=i, horizon_days=horizon_days, fit_df=fit_df, calibration_df=calib_df, test_df=test_df))
    return folds


def calibration_error(y_true: np.ndarray, y_prob: np.ndarray, bins: int = CALIBRATION_BINS) -> float:
    """Expected calibration error: mean absolute gap between predicted
    probability and realized frequency, averaged across `bins` equal-width
    probability buckets (weighted by bucket size)."""
    edges = np.linspace(0, 1, bins + 1)
    bucket = np.clip(np.digitize(y_prob, edges) - 1, 0, bins - 1)
    total_gap, total_n = 0.0, 0
    for b in range(bins):
        mask = bucket == b
        if not mask.any():
            continue
        gap = abs(float(np.mean(y_prob[mask])) - float(np.mean(y_true[mask])))
        total_gap += gap * mask.sum()
        total_n += mask.sum()
    return total_gap / total_n if total_n > 0 else float("nan")


def top_quintile_hit_rate_and_spread(cross_sectional_scores: pd.DataFrame) -> tuple[float, float]:
    """`cross_sectional_scores` must have columns [as_of, score, forward_return,
    forward_direction]. Ranks by `score` WITHIN each as_of date (this is a
    cross-sectional ranking metric -- comparing scores across different
    as_of dates would be meaningless) and compares the top vs. bottom
    quintile."""
    hit_rates, spreads = [], []
    for _, group in cross_sectional_scores.groupby("as_of"):
        if len(group) < 5:
            continue
        ranked = group.sort_values("score", ascending=False)
        n_top = max(1, int(len(ranked) * TOP_QUINTILE))
        top, bottom = ranked.iloc[:n_top], ranked.iloc[-n_top:]
        hit_rates.append(float(top["forward_direction"].mean()))
        spreads.append(float(top["forward_return"].mean() - bottom["forward_return"].mean()))
    if not hit_rates:
        return float("nan"), float("nan")
    return float(np.mean(hit_rates)), float(np.mean(spreads))


def turnover_rate(cross_sectional_scores: pd.DataFrame) -> float:
    """Fraction of top-quintile membership that changes between
    consecutive as_of dates in the test set -- a churn proxy standing in
    for true portfolio turnover, since this package has no position sizer
    or trade simulator to measure turnover directly against."""
    dates = sorted(cross_sectional_scores["as_of"].unique())
    if len(dates) < 2:
        return float("nan")
    prev_top: Optional[set] = None
    churns = []
    for d in dates:
        group = cross_sectional_scores[cross_sectional_scores["as_of"] == d]
        if len(group) < 5:
            continue
        n_top = max(1, int(len(group) * TOP_QUINTILE))
        top = set(group.sort_values("score", ascending=False).iloc[:n_top]["canonical_id"])
        if prev_top is not None:
            churns.append(len(top.symmetric_difference(prev_top)) / (2 * n_top))
        prev_top = top
    return float(np.mean(churns)) if churns else float("nan")


@dataclass(frozen=True)
class EvaluationResult:
    label: str  # "model", "naive_constant", "naive_momentum"
    n_test_rows: int
    brier_score: float
    log_loss: float
    calibration_error: float
    spearman_ic: float  # rank correlation of direction probability vs. realized forward_return
    top_quintile_hit_rate: float
    return_spread: float
    mae_magnitude: Optional[float]
    pinball_loss: Optional[dict[float, float]]
    quantile_coverage: Optional[dict[float, float]]
    turnover: float


def _direction_metrics(label: str, test_df: pd.DataFrame, prob: np.ndarray) -> EvaluationResult:
    y = test_df["forward_direction"].astype(int).to_numpy()
    prob = np.clip(prob, 1e-6, 1 - 1e-6)
    # A constant-probability benchmark has zero-variance predictions -- rank correlation is
    # undefined by construction (not a bug), so skip the call rather than let scipy warn about it.
    ic = float("nan") if np.ptp(prob) < 1e-9 else spearmanr(prob, test_df["forward_return"].to_numpy())[0]
    cross = pd.DataFrame({
        "as_of": test_df["as_of"].to_numpy(), "canonical_id": test_df["canonical_id"].to_numpy(),
        "score": prob, "forward_return": test_df["forward_return"].to_numpy(), "forward_direction": test_df["forward_direction"].to_numpy(),
    })
    hit_rate, spread = top_quintile_hit_rate_and_spread(cross)
    return EvaluationResult(
        label=label, n_test_rows=len(test_df), brier_score=float(brier_score_loss(y, prob)),
        log_loss=float(log_loss(y, prob, labels=[0, 1])), calibration_error=calibration_error(y, prob),
        spearman_ic=float(ic) if ic == ic else float("nan"), top_quintile_hit_rate=hit_rate, return_spread=spread,
        mae_magnitude=None, pinball_loss=None, quantile_coverage=None, turnover=turnover_rate(cross),
    )


def evaluate_fold(model_set: HorizonModelSet, fold: WalkForwardFold) -> list[EvaluationResult]:
    """Returns [model_result, naive_constant_result, naive_momentum_result]
    for one fold -- always all three, so a caller comparing "did the model
    beat the benchmarks" never has to special-case a missing arm."""
    test_df = fold.test_df
    results = []

    prob = predict_direction_probability(model_set, test_df)
    model_result = _direction_metrics("model", test_df, prob)
    magnitude = predict_magnitude(model_set, test_df)
    quantiles = predict_quantiles(model_set, test_df)
    y_return = test_df["forward_return"].to_numpy()
    pinball = {q: float(mean_pinball_loss(y_return, pred, alpha=q)) for q, pred in quantiles.items()}
    coverage = {q: float(np.mean(y_return <= pred)) for q, pred in quantiles.items()}
    model_result = EvaluationResult(
        **{**model_result.__dict__, "mae_magnitude": float(mean_absolute_error(y_return, magnitude)),
           "pinball_loss": pinball, "quantile_coverage": coverage}
    )
    results.append(model_result)

    results.append(_direction_metrics("naive_constant", test_df, naive_constant_probability(model_set, len(test_df))))

    momentum_call = naive_momentum_rule(test_df)
    # Rescale the hard {0, 0.5, 1} rule into a mild probability so Brier/log-loss are still meaningful
    # (a literal 0/1 probability makes log-loss infinite on any miss, which would misleadingly
    # dominate the comparison rather than reflect the rule's actual directional skill).
    momentum_prob = 0.5 + 0.3 * (momentum_call - 0.5) * 2
    results.append(_direction_metrics("naive_momentum", test_df, momentum_prob))

    return results


def run_walk_forward(panel: pd.DataFrame, horizon_days: int, n_folds: int = 4) -> list[list[EvaluationResult]]:
    """Fits+evaluates one HorizonModelSet per fold (never trains on a
    fold's own test data) and returns [fold][arm] results. Folds where
    fit_horizon_models declines to fit (too little data) are skipped."""
    folds = generate_walk_forward_folds(panel, horizon_days, n_folds)
    out = []
    for fold in folds:
        model_set = fit_horizon_models(fold.fit_df, horizon_days, calibration_df=fold.calibration_df)
        if model_set is None:
            continue
        out.append(evaluate_fold(model_set, fold))
    return out


def block_bootstrap_ci(
    values: np.ndarray, statistic_fn: Callable[[np.ndarray], float] = np.nanmean,
    block_size: int = BOOTSTRAP_BLOCK_SIZE, n_bootstrap: int = BOOTSTRAP_N, ci: float = BOOTSTRAP_CI,
) -> tuple[float, float]:
    """Moving-block bootstrap CI for `statistic_fn(values)`, respecting
    time-ordering within `values` (caller must pass values already sorted
    by as_of) -- daily/overlapping-horizon observations are serially
    dependent, so an iid bootstrap would understate the true CI width."""
    values = np.asarray(values)
    values = values[~np.isnan(values)]
    n = len(values)
    if n < block_size * 2:
        return float("nan"), float("nan")

    n_blocks_needed = math.ceil(n / block_size)
    starts = np.arange(n - block_size + 1)
    stats = []
    rng = np.random.default_rng(0)
    for _ in range(n_bootstrap):
        chosen = rng.choice(starts, size=n_blocks_needed, replace=True)
        sample = np.concatenate([values[s:s + block_size] for s in chosen])[:n]
        stats.append(statistic_fn(sample))
    lo_pct, hi_pct = (1 - ci) / 2 * 100, (1 + ci) / 2 * 100
    return float(np.percentile(stats, lo_pct)), float(np.percentile(stats, hi_pct))
