import numpy as np
import pandas as pd
import pytest

from equity_rotation.relative_technicals import (
    MA_LONG,
    MIN_BARS,
    QUADRANT_IMPROVING,
    QUADRANT_LAGGING,
    QUADRANT_LEADING,
    QUADRANT_WEAKENING,
    RelativeTechnicals,
    relative_technicals,
    relative_technicals_table,
)


def _dates(n, start="2023-01-01"):
    return pd.date_range(start, periods=n, freq="B")


def _flat_baseline_then_ramp(n_total, ramp_bars, ramp_total_pct, baseline=1.0, wobble=0.003, seed=7):
    """A ratio series that's ~flat (small deterministic wobble, so rolling
    std is nonzero) for n_total-ramp_bars bars, then ramps by
    ramp_total_pct (can be negative) over the final ramp_bars bars."""
    rng = np.random.default_rng(seed)
    flat_n = n_total - ramp_bars
    flat = baseline + wobble * np.sin(np.arange(flat_n) / 3.0) + rng.normal(0, wobble / 10, flat_n)
    ramp = baseline * (1 + np.linspace(0, ramp_total_pct, ramp_bars))
    return np.concatenate([flat, ramp])


def _ticker_and_benchmark(ratio_values, benchmark_level=100.0):
    """Recover a (ticker_close, benchmark_close) pair whose aligned ratio
    is exactly `ratio_values`, by holding the benchmark constant."""
    dates = _dates(len(ratio_values))
    benchmark_close = pd.Series(benchmark_level, index=dates)
    ticker_close = pd.Series(ratio_values * benchmark_level, index=dates)
    return ticker_close, benchmark_close


class TestRelativeTechnicalsValidation:
    def test_raises_below_min_bars(self):
        ratio_values = _flat_baseline_then_ramp(MIN_BARS - 1, ramp_bars=10, ramp_total_pct=0.1)
        ticker_close, benchmark_close = _ticker_and_benchmark(ratio_values)
        with pytest.raises(ValueError):
            relative_technicals("TICK", "Ticker", ticker_close, benchmark_close)

    def test_succeeds_at_min_bars_plus_buffer(self):
        ratio_values = _flat_baseline_then_ramp(MIN_BARS + 30, ramp_bars=10, ramp_total_pct=0.1)
        ticker_close, benchmark_close = _ticker_and_benchmark(ratio_values)
        result = relative_technicals("TICK", "Ticker", ticker_close, benchmark_close)
        assert isinstance(result, RelativeTechnicals)


class TestQuadrantClassification:
    def test_strong_recent_ramp_up_is_leading_or_weakening(self):
        # A sharp, still-in-progress ramp up should show an elevated
        # RS-Ratio; whether momentum still reads >=100 on the final bar
        # depends on curvature, so accept either "still leading" outcome.
        ratio_values = _flat_baseline_then_ramp(MIN_BARS + 40, ramp_bars=15, ramp_total_pct=0.35)
        ticker_close, benchmark_close = _ticker_and_benchmark(ratio_values)
        result = relative_technicals("TICK", "Ticker", ticker_close, benchmark_close)
        assert result.rs_ratio > 100.0
        assert result.quadrant in (QUADRANT_LEADING, QUADRANT_WEAKENING)

    def test_strong_recent_ramp_down_is_lagging_or_improving(self):
        ratio_values = _flat_baseline_then_ramp(MIN_BARS + 40, ramp_bars=15, ramp_total_pct=-0.35)
        ticker_close, benchmark_close = _ticker_and_benchmark(ratio_values)
        result = relative_technicals("TICK", "Ticker", ticker_close, benchmark_close)
        assert result.rs_ratio < 100.0
        assert result.quadrant in (QUADRANT_LAGGING, QUADRANT_IMPROVING)

    def test_quadrant_is_always_one_of_the_four_labels(self):
        ratio_values = _flat_baseline_then_ramp(MIN_BARS + 40, ramp_bars=15, ramp_total_pct=0.2)
        ticker_close, benchmark_close = _ticker_and_benchmark(ratio_values)
        result = relative_technicals("TICK", "Ticker", ticker_close, benchmark_close)
        assert result.quadrant in (
            QUADRANT_LEADING,
            QUADRANT_WEAKENING,
            QUADRANT_LAGGING,
            QUADRANT_IMPROVING,
        )

    def test_days_in_quadrant_at_least_one(self):
        ratio_values = _flat_baseline_then_ramp(MIN_BARS + 40, ramp_bars=15, ramp_total_pct=0.2)
        ticker_close, benchmark_close = _ticker_and_benchmark(ratio_values)
        result = relative_technicals("TICK", "Ticker", ticker_close, benchmark_close)
        assert result.days_in_quadrant >= 1


class TestMovingAverageCross:
    def test_no_200dma_reads_below_ma_long_bars(self):
        assert MIN_BARS < MA_LONG  # sanity: our minimum history is shorter than the long MA window
        ratio_values = _flat_baseline_then_ramp(MIN_BARS + 10, ramp_bars=10, ramp_total_pct=0.1)
        ticker_close, benchmark_close = _ticker_and_benchmark(ratio_values)
        result = relative_technicals("TICK", "Ticker", ticker_close, benchmark_close)
        assert result.ratio_vs_200dma_pct is None
        assert result.ma_cross is None
        assert result.ratio_vs_50dma_pct is not None

    def test_200dma_reads_present_with_enough_history(self):
        ratio_values = _flat_baseline_then_ramp(MA_LONG + 60, ramp_bars=10, ramp_total_pct=0.1)
        ticker_close, benchmark_close = _ticker_and_benchmark(ratio_values)
        result = relative_technicals("TICK", "Ticker", ticker_close, benchmark_close)
        assert result.ratio_vs_200dma_pct is not None
        assert result.ma_cross in ("golden", "death")


class TestRelativeVolatility:
    def test_choppier_ticker_has_higher_relative_volatility(self):
        dates = _dates(150)
        rng = np.random.default_rng(11)
        benchmark_returns = rng.normal(0, 0.005, 150)
        benchmark_close = pd.Series(100 * np.exp(np.cumsum(benchmark_returns)), index=dates)

        calm_returns = rng.normal(0, 0.003, 150)
        calm_close = pd.Series(100 * np.exp(np.cumsum(calm_returns)), index=dates)
        choppy_returns = rng.normal(0, 0.03, 150)
        choppy_close = pd.Series(100 * np.exp(np.cumsum(choppy_returns)), index=dates)

        calm_result = relative_technicals("CALM", "Calm", calm_close, benchmark_close)
        choppy_result = relative_technicals("CHOP", "Choppy", choppy_close, benchmark_close)
        assert choppy_result.relative_volatility > calm_result.relative_volatility


class TestRelativeTechnicalsTable:
    def test_sorted_by_rs_ratio_descending(self):
        n = MIN_BARS + 40
        up = _flat_baseline_then_ramp(n, ramp_bars=15, ramp_total_pct=0.3, seed=1)
        down = _flat_baseline_then_ramp(n, ramp_bars=15, ramp_total_pct=-0.3, seed=2)
        ticker_up, benchmark_close = _ticker_and_benchmark(up)
        ticker_down, _ = _ticker_and_benchmark(down)
        closes = {"UP": ticker_up, "DOWN": ticker_down}
        labels = {"UP": "Up Ticker", "DOWN": "Down Ticker"}

        table = relative_technicals_table(closes, labels, benchmark_close)
        assert [row.ticker for row in table] == ["UP", "DOWN"]
        assert table[0].rs_ratio > table[1].rs_ratio
