import numpy as np
import pandas as pd
import pytest

from rates_macro.trend_rr import (
    hac_log_regression,
    mean_reversion_snapshot,
    sigmoid,
    trend_rr_profile,
)


def _synthetic_series(n, drift, noise_scale=0.01, seed=42):
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, noise_scale, n)
    log_vals = drift * np.arange(n) + noise
    return pd.Series(np.exp(log_vals))


class TestSigmoid:
    def test_zero_is_half(self):
        assert sigmoid(0.0) == pytest.approx(0.5)

    def test_large_positive_saturates_near_one(self):
        assert sigmoid(50) == pytest.approx(1.0, abs=1e-6)

    def test_large_negative_saturates_near_zero(self):
        assert sigmoid(-50) == pytest.approx(0.0, abs=1e-6)


class TestHacLogRegression:
    def test_returns_none_below_minimum_observations(self):
        series = pd.Series(np.exp(np.linspace(0, 1, 10)))
        assert hac_log_regression(series, window=63) is None

    def test_uptrend_has_positive_slope_and_high_r2(self):
        series = _synthetic_series(300, drift=0.002)
        result = hac_log_regression(series, window=252)
        assert result is not None
        assert result["slope_daily"] > 0
        assert result["t_hac"] > 2
        assert result["r2"] > 0.8

    def test_downtrend_has_negative_slope_and_negative_t_stat(self):
        series = _synthetic_series(300, drift=-0.002)
        result = hac_log_regression(series, window=252)
        assert result["slope_daily"] < 0
        assert result["t_hac"] < -2

    def test_flat_noisy_series_has_low_confidence(self):
        series = _synthetic_series(300, drift=0.0, noise_scale=0.02)
        result = hac_log_regression(series, window=252)
        assert abs(result["t_hac"]) < 3

    def test_ignores_non_positive_values_instead_of_crashing(self):
        values = list(np.exp(np.linspace(0, 1, 260)))
        values[10] = -5.0
        series = pd.Series(values)
        result = hac_log_regression(series, window=252)
        assert result is not None

    def test_channel_rr_is_nonnegative(self):
        series = _synthetic_series(300, drift=0.001)
        result = hac_log_regression(series, window=252)
        assert result["channel_rr"] >= 0

    def test_r2_is_bounded_zero_to_one(self):
        series = _synthetic_series(300, drift=0.001, noise_scale=0.05)
        result = hac_log_regression(series, window=252)
        assert 0.0 <= result["r2"] <= 1.0


class TestTrendRRProfile:
    def test_raises_when_no_window_has_enough_data(self):
        series = pd.Series(np.exp(np.linspace(0, 0.1, 5)))
        with pytest.raises(ValueError):
            trend_rr_profile(series)

    def test_uptrend_yields_positive_trend_signal(self):
        series = _synthetic_series(300, drift=0.0015)
        profile = trend_rr_profile(series)
        assert profile["trend_signal"] > 0
        assert 0 <= profile["opportunity"] <= 100

    def test_downtrend_yields_negative_trend_signal(self):
        series = _synthetic_series(300, drift=-0.0015)
        profile = trend_rr_profile(series)
        assert profile["trend_signal"] < 0

    def test_trend_signal_stays_bounded_under_extreme_drift(self):
        series = _synthetic_series(300, drift=0.05)
        profile = trend_rr_profile(series)
        assert -1 <= profile["trend_signal"] <= 1


class TestMeanReversionSnapshot:
    def test_returns_none_below_minimum_observations(self):
        series = pd.Series([1.0, 2.0, 3.0])
        assert mean_reversion_snapshot(series, window=252) is None

    def test_z_score_of_constant_series_is_zero(self):
        series = pd.Series([5.0] * 50)
        snap = mean_reversion_snapshot(series, window=50)
        assert snap["z_score"] == 0.0

    def test_latest_value_above_mean_has_positive_z(self):
        series = pd.Series([5.0] * 49 + [10.0])
        snap = mean_reversion_snapshot(series, window=50)
        assert snap["z_score"] > 0

    def test_latest_value_below_mean_has_negative_z(self):
        series = pd.Series([5.0] * 49 + [1.0])
        snap = mean_reversion_snapshot(series, window=50)
        assert snap["z_score"] < 0

    def test_percentile_is_between_zero_and_hundred(self):
        series = pd.Series(np.linspace(1, 100, 100))
        snap = mean_reversion_snapshot(series, window=100)
        assert 0 <= snap["percentile"] <= 100
