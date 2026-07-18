import numpy as np
import pytest

from crypto_structure.indicators import Pivot
from crypto_structure.levels import (
    Level,
    build_anchored_vwap,
    build_channels,
    build_convergence_clusters,
    build_fibonacci_levels,
    build_round_levels,
    build_volume_profile,
    collect_all_levels,
)


def _pivot(idx, price, type_, weight, age):
    return Pivot(idx=idx, price=price, type=type_, weight=weight, age=age)


class TestBuildChannels:
    def test_two_nearby_pivots_form_a_support_channel(self):
        pivots = [
            _pivot(90, 98.5, "low", 0.9, 10),
            _pivot(50, 98.6, "low", 0.5, 50),
        ]
        channels = build_channels(pivots, last_close=100.0, atr=1.0)
        assert len(channels) == 1
        assert channels[0].type == "support"
        assert channels[0].touches == 2
        assert channels[0].price == pytest.approx(98.55)

    def test_isolated_pivot_does_not_form_a_channel(self):
        pivots = [_pivot(90, 98.5, "low", 0.9, 10)]
        channels = build_channels(pivots, last_close=100.0, atr=1.0)
        assert channels == []

    def test_channel_too_far_from_price_is_dropped(self):
        pivots = [
            _pivot(90, 50.0, "low", 0.9, 10),
            _pivot(50, 50.1, "low", 0.5, 50),
        ]
        channels = build_channels(pivots, last_close=100.0, atr=1.0)
        assert channels == []

    def test_old_pivot_beyond_lookback_is_excluded(self):
        pivots = [
            _pivot(90, 98.5, "low", 0.9, 10),
            _pivot(1, 98.6, "low", 0.5, 300),  # age > SR_LOOKBACK_BARS=252
        ]
        channels = build_channels(pivots, last_close=100.0, atr=1.0)
        assert channels == []  # only one pivot survives the lookback filter


class TestBuildFibonacciLevels:
    def test_five_retracement_levels_from_swing_range(self):
        high = np.array([100.0, 110.0, 105.0])
        low = np.array([90.0, 95.0, 92.0])
        levels = build_fibonacci_levels(high, low, lookback=3)
        assert len(levels) == 5
        span = 110.0 - 90.0
        expected_50pct = 110.0 - span * 0.5
        matched = next(l for l in levels if l.ratio == 0.5)
        assert matched.price == pytest.approx(expected_50pct)

    def test_flat_range_returns_no_levels(self):
        high = np.full(10, 100.0)
        low = np.full(10, 100.0)
        assert build_fibonacci_levels(high, low, lookback=10) == []


class TestBuildAnchoredVWAP:
    def test_vwap_matches_manual_calculation_from_anchor(self):
        high = np.array([10.0, 11.0, 12.0, 13.0])
        low = np.array([9.0, 10.0, 11.0, 12.0])
        close = np.array([9.5, 10.5, 11.5, 12.5])
        volume = np.array([100.0, 200.0, 300.0, 400.0])
        pivots = [_pivot(1, 10.0, "low", 1.0, 0)]
        results = build_anchored_vwap(pivots, high, low, close, volume, lookback=4, top_n=3)
        assert len(results) == 1
        tp = (high + low + close) / 3.0
        expected = float(np.sum(tp[1:] * volume[1:]) / np.sum(volume[1:]))
        assert results[0].price == pytest.approx(expected)
        assert results[0].anchor_idx == 1

    def test_zero_volume_from_anchor_onward_is_skipped(self):
        high = np.array([10.0, 11.0])
        low = np.array([9.0, 10.0])
        close = np.array([9.5, 10.5])
        volume = np.array([100.0, 0.0])
        pivots = [_pivot(1, 10.0, "low", 1.0, 0)]
        results = build_anchored_vwap(pivots, high, low, close, volume, lookback=2, top_n=3)
        assert results == []

    def test_no_candidate_pivots_in_window_returns_empty(self):
        high = np.array([10.0, 11.0])
        low = np.array([9.0, 10.0])
        close = np.array([9.5, 10.5])
        volume = np.array([100.0, 200.0])
        assert build_anchored_vwap([], high, low, close, volume, lookback=2) == []


class TestBuildVolumeProfile:
    def test_dominant_volume_bin_is_flagged_as_hvn(self):
        close = np.array([100.0] * 5 + [110.0] * 95)
        volume = np.array([1_000_000.0] * 5 + [100.0] * 95)
        results = build_volume_profile(close, volume, last_close=100.0, atr=1.0)
        assert any(abs(r.price - 100.0) < 1.0 for r in results)

    def test_flat_price_series_returns_no_levels(self):
        close = np.full(50, 100.0)
        volume = np.full(50, 1000.0)
        assert build_volume_profile(close, volume, last_close=100.0, atr=1.0) == []

    def test_far_hvn_dropped_by_proximity_filter(self):
        close = np.array([50.0] * 5 + [200.0] * 95)
        volume = np.array([1_000_000.0] * 5 + [100.0] * 95)
        results = build_volume_profile(close, volume, last_close=200.0, atr=1.0)
        assert all(r.price > 100 for r in results)


class TestBuildRoundLevels:
    def test_step_ten_for_close_between_fifty_and_hundred(self):
        levels = build_round_levels(last_close=73.0, atr=1.0)
        prices = sorted(l.price for l in levels)
        assert 70.0 in prices
        assert 80.0 in prices

    def test_step_fifty_for_close_above_five_hundred(self):
        levels = build_round_levels(last_close=712.0, atr=5.0)
        prices = {l.price for l in levels}
        assert 700.0 in prices

    def test_nonpositive_close_returns_no_levels(self):
        assert build_round_levels(last_close=0.0, atr=1.0) == []

    def test_far_levels_dropped_by_proximity_filter(self):
        # ATR tiny -> even the nearest round step is > 8 ATR away.
        levels = build_round_levels(last_close=73.0, atr=0.01)
        assert levels == []


class TestConvergenceClustering:
    def test_two_agreeing_methods_form_a_cluster(self):
        pool = [
            Level(price=98.5, method="channel", weight=1.0),
            Level(price=98.6, method="avwap", weight=0.7),
        ]
        clusters = build_convergence_clusters(pool, last_close=100.0, atr=1.0)
        assert len(clusters) == 1
        assert clusters[0].strength == 2
        assert clusters[0].type == "support"
        assert clusters[0].price == pytest.approx(98.55)

    def test_single_method_alone_does_not_form_a_cluster(self):
        pool = [Level(price=98.5, method="channel", weight=1.0)]
        assert build_convergence_clusters(pool, last_close=100.0, atr=1.0) == []

    def test_resistance_above_price_is_typed_correctly(self):
        pool = [
            Level(price=101.5, method="channel", weight=1.0),
            Level(price=101.6, method="round_number", weight=0.3),
        ]
        clusters = build_convergence_clusters(pool, last_close=100.0, atr=1.0)
        assert clusters[0].type == "resistance"

    def test_empty_pool_returns_no_clusters(self):
        assert build_convergence_clusters([], last_close=100.0, atr=1.0) == []

    def test_collect_all_levels_tags_each_method(self):
        from crypto_structure.levels import (
            AnchoredVWAPLevel,
            Channel,
            FibLevel,
            RoundLevel,
            VolumeProfileLevel,
        )

        channels = [Channel(price=99.0, strength=1.0, touches=2, newest_age=1, type="support", is_recent=True)]
        trendline_levels = [Level(price=105.0, method="trendline", weight=0.8)]
        fib_levels = [FibLevel(price=97.0, ratio=0.5, label="50.0% retrace")]
        avwap_levels = [AnchoredVWAPLevel(price=99.5, anchor_idx=0)]
        vp_levels = [VolumeProfileLevel(price=98.0, volume_pct=10.0)]
        round_levels = [RoundLevel(price=100.0)]
        pool = collect_all_levels(
            channels, trendline_levels, fib_levels, avwap_levels, vp_levels, round_levels
        )
        methods = {lv.method for lv in pool}
        assert methods == {"channel", "trendline", "fibonacci", "avwap", "volume_profile", "round_number"}
