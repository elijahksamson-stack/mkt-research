import numpy as np
import pytest

from crypto_structure.indicators import Pivot
from crypto_structure.trendlines import (
    build_pivot_pair_trendlines,
    build_regression_trendlines,
    regression_trendlines_as_levels,
)


class TestBuildRegressionTrendlines:
    def test_fewer_than_four_pivots_yields_no_lines(self):
        pivots = [Pivot(idx=i * 10, price=100 + i, type="high", weight=1.0, age=0) for i in range(3)]
        assert build_regression_trendlines(pivots, n=61, atr=1.0) == []

    def test_clean_linear_highs_yield_a_high_r2_upper_trendline(self):
        pivots = [Pivot(idx=i, price=100.0 + 2.0 * i, type="high", weight=1.0, age=0) for i in range(4)]
        lines = build_regression_trendlines(pivots, n=4, atr=1.0)
        upper = next((l for l in lines if l.type == "upper"), None)
        assert upper is not None
        assert upper.r2 > 0.9
        assert upper.slope == pytest.approx(2.0, abs=0.05)

    def test_noisy_alternating_highs_fail_the_r2_gate(self):
        pivots = [
            Pivot(idx=i * 10, price=(100.0 if i % 2 == 0 else 60.0), type="high", weight=1.0, age=0)
            for i in range(6)
        ]
        lines = build_regression_trendlines(pivots, n=61, atr=1.0)
        assert all(l.type != "upper" for l in lines)

    def test_regression_trendlines_as_levels_tags_method_and_weight(self):
        pivots = [Pivot(idx=i * 20, price=100.0 + 2.0 * i, type="high", weight=1.0, age=0) for i in range(4)]
        lines = build_regression_trendlines(pivots, n=61, atr=1.0)
        levels = regression_trendlines_as_levels(lines)
        assert len(levels) == len(lines)
        assert all(lv.method == "trendline" for lv in levels)
        assert levels[0].weight == pytest.approx(lines[0].r2)


class TestBuildPivotPairTrendlines:
    def _ascending_support_series(self, n=68, dip_centers=(10, 50), depth=5.0, radius=6.0, slope=0.5):
        # Rising baseline with a local downward "V" dip (a genuine swing
        # low, lower than its neighbors on both sides) carved out at each
        # dip center, so find_local_extrema actually flags idx 10 and 50 as
        # pivots -- a plain "baseline + small oscillation" series won't
        # work here since a monotonically rising baseline never has an
        # interior local minimum on its own.
        idxs = np.arange(n)
        baseline = 100 + slope * idxs
        dip = np.zeros(n)
        for center in dip_centers:
            dip += depth * np.maximum(0, 1 - np.abs(idxs - center) / radius)
        low = baseline - dip
        high = low + 1.0
        return high, low

    def test_detects_ascending_support_line_between_two_higher_lows(self):
        high, low = self._ascending_support_series()
        lines = build_pivot_pair_trendlines(high, low, atr=1.0)
        lower_lines = [l for l in lines if l.type == "lower"]
        matched = next((l for l in lower_lines if l.start_idx == 10 and l.end_idx == 50), None)
        assert matched is not None
        assert matched.slope == pytest.approx(0.5, abs=0.01)
        assert matched.score > 0

    def test_flat_series_produces_no_ascending_or_descending_lines(self):
        high = np.full(80, 100.0)
        low = np.full(80, 99.0)
        lines = build_pivot_pair_trendlines(high, low, atr=1.0)
        assert all(l.slope == 0 for l in lines)

    def test_result_is_capped_at_twelve_lines(self):
        rng = np.random.default_rng(7)
        n = 300
        close = 100 + np.cumsum(rng.normal(0, 1.5, n))
        high = close + rng.uniform(0.2, 1.5, n)
        low = close - rng.uniform(0.2, 1.5, n)
        lines = build_pivot_pair_trendlines(high, low, atr=1.0)
        assert len(lines) <= 12
