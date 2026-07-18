import numpy as np
import pytest

from market_structure.indicators import InsufficientDataError
from market_structure.risk_reward import analyze
from market_structure.stop_target import StopTarget
from market_structure.trend_violation import TrendViolation


def _synthetic_ohlcv(n=300, seed=11):
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(rng.normal(0.05, 1.0, n))
    high = close + rng.uniform(0.2, 1.5, n)
    low = close - rng.uniform(0.2, 1.5, n)
    volume = rng.uniform(1_000_000, 5_000_000, n)
    return high, low, close, volume


class TestAnalyze:
    def test_raises_below_minimum_bars(self):
        high, low, close, volume = _synthetic_ohlcv(n=30)
        with pytest.raises(InsufficientDataError):
            analyze("TEST", high, low, close, volume)

    def test_returns_a_fully_populated_report(self):
        high, low, close, volume = _synthetic_ohlcv()
        report = analyze("TEST", high, low, close, volume)
        assert report.ticker == "TEST"
        assert report.last_close == pytest.approx(close[-1])
        assert report.atr >= 0
        assert 0.005 <= report.hv <= 0.08
        assert isinstance(report.stop_target, StopTarget)
        assert isinstance(report.trend_violation, TrendViolation)
        assert report.stop_target.target_source in {"cluster", "trendline", "fib_extension", "synthetic"}
        assert report.trend_violation.status in {"intact", "undercut", "no_active_trendline"}

    def test_rr_ratio_is_nonnegative(self):
        high, low, close, volume = _synthetic_ohlcv(seed=99)
        report = analyze("TEST", high, low, close, volume)
        assert report.stop_target.rr_ratio >= 0

    def test_stop_sits_below_last_close(self):
        high, low, close, volume = _synthetic_ohlcv(seed=42)
        report = analyze("TEST", high, low, close, volume)
        assert report.stop_target.stop < report.last_close
