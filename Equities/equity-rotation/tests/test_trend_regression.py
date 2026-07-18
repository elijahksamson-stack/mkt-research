import numpy as np
import pandas as pd
import pytest

from equity_rotation.trend_regression import (
    WindowRegression,
    hac_log_regression,
    regression_profile,
)


def _rising_series(n=300, drift=0.0015, noise=0.01, seed=1):
    rng = np.random.default_rng(seed)
    log_returns = drift + rng.normal(0, noise, n)
    prices = 100 * np.exp(np.cumsum(log_returns))
    return pd.Series(prices)


def _falling_series(n=300, drift=-0.0015, noise=0.01, seed=2):
    return _rising_series(n=n, drift=drift, noise=noise, seed=seed)


def _flat_noisy_series(n=300, noise=0.01, seed=3):
    return _rising_series(n=n, drift=0.0, noise=noise, seed=seed)


class TestHacLogRegression:
    def test_returns_none_below_minimum_observations(self):
        series = pd.Series(np.full(10, 100.0))
        assert hac_log_regression(series, window=63) is None

    def test_returns_window_regression_with_enough_observations(self):
        series = _rising_series(n=100)
        result = hac_log_regression(series, window=63)
        assert isinstance(result, WindowRegression)
        assert result.window == 63

    def test_positive_slope_for_rising_series(self):
        result = hac_log_regression(_rising_series(), window=252)
        assert result.slope_daily > 0
        assert result.slope_annual > 0

    def test_negative_slope_for_falling_series(self):
        result = hac_log_regression(_falling_series(), window=252)
        assert result.slope_daily < 0

    def test_r2_bounded_zero_to_one(self):
        result = hac_log_regression(_rising_series(), window=252)
        assert 0.0 <= result.r2 <= 1.0

    def test_ignores_nonpositive_and_missing_values(self):
        values = _rising_series(n=280).to_numpy()
        values = np.concatenate([np.array([np.nan, -5.0, 0.0]), values])
        result = hac_log_regression(pd.Series(values), window=252)
        assert result is not None


class TestRegressionProfile:
    def test_trend_signal_bounded(self):
        profile = regression_profile(_rising_series())
        assert -1.0 <= profile.trend_signal <= 1.0

    def test_opportunity_bounded(self):
        profile = regression_profile(_rising_series())
        assert 0.0 <= profile.opportunity <= 100.0

    def test_rising_series_has_positive_trend_signal(self):
        profile = regression_profile(_rising_series(n=300, drift=0.003, noise=0.005))
        assert profile.trend_signal > 0

    def test_falling_series_has_negative_trend_signal(self):
        profile = regression_profile(_falling_series(n=300, drift=-0.003, noise=0.005))
        assert profile.trend_signal < 0

    def test_raises_when_no_window_has_enough_observations(self):
        series = pd.Series(np.full(5, 100.0))
        with pytest.raises(ValueError):
            regression_profile(series)

    def test_windows_dict_only_contains_fitted_windows(self):
        # 100 bars: 21/63 windows fit (>= 0.75*window), 126/252 do not.
        profile = regression_profile(_rising_series(n=100))
        assert set(profile.windows) <= {21, 63, 126, 252}
        assert 21 in profile.windows
        assert 252 not in profile.windows
