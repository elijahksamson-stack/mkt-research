import math

import numpy as np
import pytest

from market_structure.indicators import (
    InsufficientDataError,
    average_true_range,
    build_pivots,
    find_local_extrema,
    realized_volatility,
    relative_volume,
    require_min_bars,
)


class TestRequireMinBars:
    def test_passes_at_or_above_minimum(self):
        require_min_bars(60, minimum=60)  # no raise

    def test_raises_below_minimum(self):
        with pytest.raises(InsufficientDataError):
            require_min_bars(59, minimum=60)


class TestAverageTrueRange:
    def test_falls_back_to_mean_high_low_below_period_plus_one_bars(self):
        high = np.array([10.0, 11.0, 12.0])
        low = np.array([9.0, 9.5, 10.5])
        close = np.array([9.5, 10.5, 11.5])
        atr = average_true_range(high, low, close, period=14)
        assert atr == pytest.approx(np.mean(high - low))

    def test_matches_manual_ema_recurrence_on_small_period(self):
        # period=2 so the recurrence is easy to hand-verify.
        high = np.array([10.0, 11.0, 10.5, 12.0, 13.0])
        low = np.array([9.0, 9.5, 9.8, 10.5, 11.5])
        close = np.array([9.5, 10.8, 10.0, 11.8, 12.5])
        period = 2
        prev_close = close[:-1]
        tr = np.maximum(
            high[1:] - low[1:],
            np.maximum(np.abs(high[1:] - prev_close), np.abs(low[1:] - prev_close)),
        )
        expected_seed = np.mean(tr[:period])
        expected = expected_seed
        for i in range(period, len(tr)):
            expected = (expected * (period - 1) + tr[i]) / period
        atr = average_true_range(high, low, close, period=period)
        assert atr == pytest.approx(expected)

    def test_atr_is_nonnegative(self):
        rng = np.random.default_rng(1)
        close = 100 + np.cumsum(rng.normal(0, 1, 80))
        high = close + rng.uniform(0.1, 1.0, 80)
        low = close - rng.uniform(0.1, 1.0, 80)
        atr = average_true_range(high, low, close)
        assert atr >= 0


class TestRealizedVolatility:
    def test_returns_default_below_period_plus_one_bars(self):
        close = np.array([100.0, 101.0, 99.0])
        assert realized_volatility(close, period=20) == 0.02

    def test_flat_price_clips_to_lower_bound(self):
        close = np.full(30, 100.0)
        assert realized_volatility(close, period=20) == pytest.approx(0.005)

    def test_result_stays_within_clip_band(self):
        rng = np.random.default_rng(2)
        close = 100 * np.exp(np.cumsum(rng.normal(0, 0.05, 60)))
        hv = realized_volatility(close, period=20)
        assert 0.005 <= hv <= 0.08


class TestRelativeVolume:
    def test_returns_neutral_below_period_plus_one_bars(self):
        volume = np.array([1000.0, 1200.0])
        assert relative_volume(volume, period=20) == 1.0

    def test_returns_neutral_when_last_volume_is_zero(self):
        volume = np.array([1000.0] * 21 + [0.0])
        assert relative_volume(volume, period=20) == 1.0

    def test_computes_ratio_against_prior_average(self):
        volume = np.array([100.0] * 20 + [200.0])
        assert relative_volume(volume, period=20) == pytest.approx(2.0)


class TestFindLocalExtrema:
    def test_detects_single_clear_peak_and_trough(self):
        # window=2 -> 5-bar centered window. Index 5 is the max, index 10 the min.
        high = np.array([1, 2, 3, 4, 5, 10, 5, 4, 3, 2, 1, 2, 3, 4], dtype=float)
        low = np.array([1, 2, 3, 4, 5, 10, 5, 4, 3, 2, -5, 2, 3, 4], dtype=float)
        high_idx, low_idx = find_local_extrema(high, low, window=2)
        assert 5 in high_idx
        assert 10 in low_idx

    def test_empty_when_series_shorter_than_window(self):
        high = np.array([1.0, 2.0, 3.0])
        low = np.array([1.0, 2.0, 3.0])
        high_idx, low_idx = find_local_extrema(high, low, window=5)
        assert high_idx == []
        assert low_idx == []


class TestBuildPivots:
    def test_sorted_by_index_ascending(self):
        rng = np.random.default_rng(3)
        n = 100
        close = 100 + np.cumsum(rng.normal(0, 1, n))
        high = close + rng.uniform(0.1, 1.0, n)
        low = close - rng.uniform(0.1, 1.0, n)
        pivots = build_pivots(high, low, window=5, halflife=60)
        indices = [p.idx for p in pivots]
        assert indices == sorted(indices)

    def test_older_pivot_has_lower_weight_than_newer_pivot(self):
        high = np.array([1, 2, 3, 4, 5, 10, 5, 4, 3, 2, 3, 4, 5, 12, 5, 4, 3, 2, 1], dtype=float)
        low = high - 1
        pivots = build_pivots(high, low, window=2, halflife=60)
        by_idx = {p.idx: p for p in pivots if p.type == "high"}
        assert 5 in by_idx and 13 in by_idx
        older, newer = by_idx[5], by_idx[13]
        assert older.age > newer.age
        assert older.weight < newer.weight

    def test_weight_matches_exponential_decay_formula(self):
        high = np.array([1, 2, 3, 4, 5, 10, 5, 4, 3, 2, 1], dtype=float)
        low = high - 1
        halflife = 60
        pivots = build_pivots(high, low, window=2, halflife=halflife)
        pivot = next(p for p in pivots if p.type == "high")
        decay = math.log(2) / halflife
        expected_weight = math.exp(-decay * pivot.age)
        assert pivot.weight == pytest.approx(expected_weight)
