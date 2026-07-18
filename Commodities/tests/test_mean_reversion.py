import numpy as np

from commodities.mean_reversion import adf_gate, build_displacement


def _sine_range_bound_series(n: int = 300, amplitude: float = 5.0, center: float = 100.0) -> np.ndarray:
    x = np.linspace(0, 12 * np.pi, n)
    return center + amplitude * np.sin(x)


def _trending_series(n: int = 300, drift: float = 0.3) -> np.ndarray:
    return 100.0 + drift * np.arange(n)


class TestAdfGate:
    def test_an_oscillating_series_is_flagged_range_bound(self):
        close = _sine_range_bound_series()

        gate = adf_gate(close)

        assert gate.is_range_bound is True

    def test_a_persistent_trend_is_not_flagged_range_bound(self):
        close = _trending_series()

        gate = adf_gate(close)

        assert gate.is_range_bound is False

    def test_too_little_data_is_conservatively_not_range_bound(self):
        close = np.array([100.0, 101.0, 99.0])

        gate = adf_gate(close)

        assert gate.is_range_bound is False
        assert gate.adf_pvalue == 1.0


class TestBuildDisplacement:
    def test_price_above_its_moving_average_gives_a_positive_bollinger_z(self):
        close = np.concatenate([np.full(30, 100.0), np.full(5, 110.0)])
        high, low = close + 1, close - 1

        d = build_displacement("test", high, low, close, window=20)

        assert d.bollinger_z > 0

    def test_mean_reversion_only_activates_when_both_range_bound_and_displaced(self):
        # Strongly trending -> ADF gate should be closed even if price is far from its SMA.
        close = _trending_series()
        high, low = close + 1, close - 1

        d = build_displacement("test", high, low, close, window=20)

        assert d.range_bound.is_range_bound is False
        assert d.mean_reversion_active is False
