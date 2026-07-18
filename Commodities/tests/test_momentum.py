import numpy as np
import pandas as pd

from commodities.momentum import cross_sectional_normalize, vol_adjusted_horizon_return


def _return_matrix(values: dict[str, np.ndarray]) -> pd.DataFrame:
    n = len(next(iter(values.values())))
    dates = pd.bdate_range("2024-01-01", periods=n)
    return pd.DataFrame({cid: pd.Series(v, index=dates) for cid, v in values.items()})


class TestVolAdjustedHorizonReturn:
    def test_a_steady_uptrend_scores_positive(self):
        n = 60
        rng = np.random.default_rng(0)
        returns = _return_matrix({"gold": np.full(n, 0.01) + rng.normal(0, 0.0005, n)})

        score = vol_adjusted_horizon_return(returns, "gold", horizon=21, vol_window=20)

        assert score > 0

    def test_unknown_commodity_returns_nan(self):
        returns = _return_matrix({"gold": np.full(30, 0.01)})

        score = vol_adjusted_horizon_return(returns, "silver", horizon=21)

        assert score != score  # NaN

    def test_too_little_history_returns_nan(self):
        returns = _return_matrix({"gold": np.full(5, 0.01)})

        score = vol_adjusted_horizon_return(returns, "gold", horizon=21, vol_window=20)

        assert score != score

    def test_larger_move_scores_higher_than_a_smaller_one_at_equal_volatility(self):
        n = 60
        rng = np.random.default_rng(2)
        noise = rng.normal(0, 0.001, n)
        small_move = _return_matrix({"c": np.full(n, 0.002) + noise})
        big_move = _return_matrix({"c": np.full(n, 0.02) + noise})

        small_score = vol_adjusted_horizon_return(small_move, "c", horizon=21, vol_window=20)
        big_score = vol_adjusted_horizon_return(big_move, "c", horizon=21, vol_window=20)

        assert big_score > small_score


class TestCrossSectionalNormalize:
    def test_percentile_of_the_max_value_is_the_highest(self):
        values = {"a": 1.0, "b": 5.0, "c": 3.0}

        scores = cross_sectional_normalize(values)

        assert scores["b"].percentile == max(s.percentile for s in scores.values())

    def test_nan_inputs_are_excluded_from_the_output(self):
        values = {"a": 1.0, "b": float("nan"), "c": 3.0}

        scores = cross_sectional_normalize(values)

        assert set(scores) == {"a", "c"}

    def test_empty_input_returns_empty_output(self):
        scores = cross_sectional_normalize({})

        assert scores == {}

    def test_extreme_outlier_is_winsorized_before_scoring(self):
        values = {"a": 1.0, "b": 2.0, "c": 3.0, "d": 4.0, "e": 1000.0}

        scores = cross_sectional_normalize(values)

        # A raw z-score would put e's |z| far above 3; winsorizing should pull it back down.
        assert abs(scores["e"].winsorized_z) < 3
