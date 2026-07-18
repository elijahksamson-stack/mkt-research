import numpy as np
import pandas as pd

from commodities.validation import block_bootstrap_ci, calibration_error, generate_walk_forward_folds, turnover_rate


def _synthetic_panel(n_dates: int = 60, n_commodities: int = 6, horizon: int = 21, seed: int = 5) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2022-01-01", periods=n_dates, freq="5B")
    rows = []
    for cid in [f"c{i}" for i in range(n_commodities)]:
        momentum = rng.normal(0, 1, n_dates)
        forward_return = 0.02 * momentum + rng.normal(0, 0.02, n_dates)
        for i, d in enumerate(dates):
            rows.append({
                "canonical_id": cid, "family": "test", "as_of": d, "horizon_days": horizon,
                "mom_21d_vol_adj_return": momentum[i], "mom_63d_vol_adj_return": rng.normal(0, 1),
                "forward_return": forward_return[i], "forward_direction": forward_return[i] > 0,
            })
    return pd.DataFrame(rows)


class TestGenerateWalkForwardFolds:
    def test_no_fold_lets_test_rows_start_before_the_embargo_gap(self):
        panel = _synthetic_panel()

        folds = generate_walk_forward_folds(panel, horizon_days=21, n_folds=4)

        for fold in folds:
            train_end = fold.fit_df["as_of"].max()
            calib_end = fold.calibration_df["as_of"].max() if not fold.calibration_df.empty else train_end
            latest_seen = max(train_end, calib_end)
            earliest_test = fold.test_df["as_of"].min()
            assert (earliest_test - latest_seen).days >= 21  # at least horizon-ish calendar days

    def test_fit_and_test_rows_never_overlap_in_time(self):
        panel = _synthetic_panel()

        folds = generate_walk_forward_folds(panel, horizon_days=21, n_folds=4)

        for fold in folds:
            fit_dates = set(fold.fit_df["as_of"])
            test_dates = set(fold.test_df["as_of"])
            assert fit_dates.isdisjoint(test_dates)

    def test_too_little_history_yields_no_folds(self):
        panel = _synthetic_panel(n_dates=3)

        folds = generate_walk_forward_folds(panel, horizon_days=21, n_folds=4)

        assert folds == []


class TestCalibrationError:
    def test_perfectly_calibrated_predictions_score_near_zero(self):
        rng = np.random.default_rng(0)
        prob = rng.uniform(0, 1, 2000)
        y = (rng.uniform(0, 1, 2000) < prob).astype(int)

        error = calibration_error(y, prob, bins=10)

        assert error < 0.05

    def test_a_systematically_overconfident_model_scores_high(self):
        y = np.array([0, 1] * 50)
        prob = np.where(y == 1, 0.95, 0.95)  # always predicts 95% up regardless of outcome

        error = calibration_error(y, prob, bins=10)

        assert error > 0.3


class TestTurnoverRate:
    def test_identical_top_quintile_every_period_has_zero_turnover(self):
        dates = pd.bdate_range("2023-01-01", periods=3, freq="5B")
        rows = []
        for d in dates:
            for i in range(10):
                rows.append({"as_of": d, "canonical_id": f"c{i}", "score": float(i)})
        df = pd.DataFrame(rows)

        churn = turnover_rate(df)

        assert churn == 0.0


class TestBlockBootstrapCi:
    def test_too_few_observations_returns_nan(self):
        lo, hi = block_bootstrap_ci(np.array([1.0, 2.0]), block_size=5)

        assert lo != lo and hi != hi

    def test_ci_brackets_the_true_mean_of_a_stable_series(self):
        rng = np.random.default_rng(1)
        values = rng.normal(0.1, 0.05, 200)

        lo, hi = block_bootstrap_ci(values, block_size=5, n_bootstrap=200)

        assert lo < 0.1 < hi
