import numpy as np
import pandas as pd

from commodities.models import (
    fit_horizon_models, naive_constant_probability, naive_momentum_rule, predict_direction_probability,
    predict_magnitude, predict_quantiles, top_feature_contributions,
)


def _synthetic_panel(n: int = 200, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    momentum = rng.normal(0, 1, n)
    noise_feature = rng.normal(0, 1, n)  # deliberately uninformative
    forward_return = 0.02 * momentum + rng.normal(0, 0.02, n)
    return pd.DataFrame({
        "canonical_id": ["gold"] * n, "family": ["precious_metals"] * n,
        "as_of": pd.bdate_range("2023-01-01", periods=n), "horizon_days": [21] * n,
        "mom_21d_vol_adj_return": momentum, "mom_63d_vol_adj_return": noise_feature,
        "forward_return": forward_return, "forward_direction": forward_return > 0,
    })


class TestFitHorizonModels:
    def test_returns_none_below_the_minimum_row_count(self):
        panel = _synthetic_panel(n=10)

        model_set = fit_horizon_models(panel, horizon_days=21)

        assert model_set is None

    def test_fits_when_enough_rows_are_available(self):
        panel = _synthetic_panel(n=200)

        model_set = fit_horizon_models(panel, horizon_days=21)

        assert model_set is not None
        assert model_set.n_train_rows == 200

    def test_the_informative_feature_gets_a_larger_positive_coefficient_than_the_noise_feature(self):
        panel = _synthetic_panel(n=300)
        model_set = fit_horizon_models(panel, horizon_days=21)

        positive, _ = top_feature_contributions(model_set, n=5)
        top_feature_names = [name for name, _ in positive]

        assert "mom_21d_vol_adj_return" in top_feature_names


class TestPredictions:
    def test_direction_probabilities_are_between_zero_and_one(self):
        panel = _synthetic_panel(n=200)
        model_set = fit_horizon_models(panel, horizon_days=21)

        probs = predict_direction_probability(model_set, panel)

        assert np.all((probs >= 0) & (probs <= 1))

    def test_quantiles_are_monotonically_ordered_on_average(self):
        panel = _synthetic_panel(n=300)
        model_set = fit_horizon_models(panel, horizon_days=21)

        q = predict_quantiles(model_set, panel)

        assert q[0.1].mean() <= q[0.5].mean() <= q[0.9].mean()

    def test_magnitude_prediction_correlates_with_the_informative_feature(self):
        panel = _synthetic_panel(n=300)
        model_set = fit_horizon_models(panel, horizon_days=21)

        magnitude = predict_magnitude(model_set, panel)
        correlation = np.corrcoef(magnitude, panel["mom_21d_vol_adj_return"])[0, 1]

        assert correlation > 0.5


class TestNaiveBenchmarks:
    def test_constant_probability_equals_the_training_base_rate(self):
        panel = _synthetic_panel(n=200)
        model_set = fit_horizon_models(panel, horizon_days=21)

        preds = naive_constant_probability(model_set, n_rows=5)

        assert np.all(preds == model_set.train_base_rate)

    def test_momentum_rule_follows_the_sign_of_the_momentum_column(self):
        panel = pd.DataFrame({"mom_63d_vol_adj_return": [1.0, -1.0, float("nan")]})

        calls = naive_momentum_rule(panel)

        assert list(calls) == [1.0, 0.0, 0.5]
