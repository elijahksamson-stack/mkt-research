import pytest

from market_structure.fib_extension import FibExtension, FibExtensionLevel
from market_structure.levels import ConvergenceCluster
from market_structure.stop_target import compute_stop_target
from market_structure.trendlines import RegressionTrendline, TrendlineSegment


def _cluster(price, side):
    return ConvergenceCluster(price=price, strength=2, methods=2, total_weight=1.0, type=side)


class TestComputeStopTarget:
    def test_tier1_cluster_target_when_resistance_present(self):
        clusters = [_cluster(95.0, "support"), _cluster(110.0, "resistance")]
        result = compute_stop_target(clusters, [], [], None, last_close=100.0, atr=1.0, hv=0.02)
        assert result.target_source == "cluster"
        assert result.target_cluster == 110.0
        assert result.target == pytest.approx(110.0 + 1.0 * 0.5 * 1.0)
        assert result.stop_cluster == 95.0

    def test_tier2_trendline_target_when_no_resistance_cluster(self):
        clusters = [_cluster(95.0, "support")]
        reg = [RegressionTrendline(type="upper", slope=0.1, intercept=100, r2=0.8, start_price=100, end_price=112.0, channel_width=1.0)]
        pair = [TrendlineSegment(type="upper", start_idx=0, end_idx=10, start_price=100, end_price=115.0, slope=0.1, score=5.0, span=10)]
        result = compute_stop_target(clusters, reg, pair, None, last_close=100.0, atr=1.0, hv=0.02)
        assert result.target_source == "trendline"
        # nearest (lowest) endpoint above price wins
        assert result.target == pytest.approx(112.0 + 1.0 * 0.5 * 1.0)

    def test_tier3_fib_extension_target_with_no_atr_pad(self):
        fib = FibExtension(
            peak_idx=0, peak_price=100.0, trough_idx=5, trough_price=80.0, range=20.0,
            levels=[FibExtensionLevel(ratio=1.272, price=105.44)],
        )
        result = compute_stop_target([], [], [], fib, last_close=100.0, atr=1.0, hv=0.02)
        assert result.target_source == "fib_extension"
        assert result.target_fib_ratio == 1.272
        assert result.target == pytest.approx(105.44)  # no ATR pad on tier 3

    def test_tier4_synthetic_flat_two_to_one_fallback(self):
        result = compute_stop_target([], [], [], None, last_close=100.0, atr=1.0, hv=0.02)
        assert result.target_source == "synthetic"
        expected_risk = 100.0 - result.stop
        assert result.target == pytest.approx(100.0 + expected_risk * 2.0)

    def test_stop_is_capped_when_cluster_is_too_far_below_price(self):
        clusters = [_cluster(50.0, "support")]  # way below price
        result = compute_stop_target(clusters, [], [], None, last_close=100.0, atr=1.0, hv=0.02)
        # raw_stop from the cluster (49.5) is looser than both caps; the
        # ATR cap (last_close - 3*ATR = 97) is tighter than the pct cap
        # (last_close*0.92 = 92) at this ATR, so it wins (max = tightest).
        assert result.stop == pytest.approx(100.0 - 1.0 * 3.0)

    def test_vol_factor_is_clipped_to_band(self):
        low_hv_result = compute_stop_target([], [], [], None, last_close=100.0, atr=1.0, hv=0.0001)
        high_hv_result = compute_stop_target([], [], [], None, last_close=100.0, atr=1.0, hv=1.0)
        assert low_hv_result.vol_factor == pytest.approx(0.75)
        assert high_hv_result.vol_factor == pytest.approx(2.25)

    def test_target_floor_overrides_a_target_too_close_to_price(self):
        # Tiny cluster reward that would land below the MIN_TARGET_ATR floor.
        clusters = [_cluster(100.01, "resistance")]
        result = compute_stop_target(clusters, [], [], None, last_close=100.0, atr=1.0, hv=0.02)
        assert result.target == pytest.approx(100.0 + 1.0 * 1.25)

    def test_rr_ratio_matches_reward_over_risk(self):
        clusters = [_cluster(95.0, "support"), _cluster(110.0, "resistance")]
        result = compute_stop_target(clusters, [], [], None, last_close=100.0, atr=1.0, hv=0.02)
        assert result.rr_ratio == pytest.approx(result.reward / result.risk)
