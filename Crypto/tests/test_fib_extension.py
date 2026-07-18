import pytest

from crypto_structure.fib_extension import build_fib_extension
from crypto_structure.indicators import Pivot


def _pivot(idx, price, type_):
    return Pivot(idx=idx, price=price, type=type_, weight=1.0, age=0)


class TestBuildFibExtension:
    def test_returns_none_for_empty_pivots(self):
        assert build_fib_extension([], n=20, last_close=90.0) is None

    def test_qualifying_drawdown_projects_extension_levels(self):
        pivots = [_pivot(5, 100.0, "high"), _pivot(10, 80.0, "low")]
        ext = build_fib_extension(pivots, n=20, last_close=90.0)
        assert ext is not None
        assert ext.peak_idx == 5 and ext.peak_price == 100.0
        assert ext.trough_idx == 10 and ext.trough_price == 80.0
        assert ext.range == pytest.approx(20.0)
        assert len(ext.levels) == 8
        level_100 = next(l for l in ext.levels if l.ratio == 1.0)
        assert level_100.price == pytest.approx(100.0)
        level_1618 = next(l for l in ext.levels if l.ratio == 1.618)
        assert level_1618.price == pytest.approx(80.0 + 1.618 * 20.0)

    def test_skips_non_qualifying_newer_low_for_an_older_qualifying_one(self):
        pivots = [
            _pivot(5, 100.0, "high"),
            _pivot(8, 80.0, "low"),  # 20% drawdown -- qualifies, but older
            _pivot(12, 97.0, "low"),  # 3% drawdown -- newer, doesn't qualify
        ]
        ext = build_fib_extension(pivots, n=20, last_close=90.0)
        assert ext is not None
        assert ext.trough_idx == 8
        assert ext.trough_price == 80.0

    def test_low_with_no_preceding_high_returns_none(self):
        pivots = [_pivot(5, 80.0, "low")]
        assert build_fib_extension(pivots, n=20, last_close=90.0) is None

    def test_low_below_shallow_drawdown_threshold_returns_none(self):
        pivots = [_pivot(5, 100.0, "high"), _pivot(10, 95.0, "low")]  # 5% drawdown
        assert build_fib_extension(pivots, n=20, last_close=90.0) is None

    def test_low_older_than_lookback_is_excluded(self):
        pivots = [_pivot(5, 100.0, "high"), _pivot(10, 80.0, "low")]
        # n=1000, lookback=50 -> cutoff=950; idx=10 is far outside the window.
        assert build_fib_extension(pivots, n=1000, last_close=90.0, lookback=50) is None

    def test_runaway_extends_ratios_by_phi_until_a_level_clears_last_close(self):
        pivots = [_pivot(5, 100.0, "high"), _pivot(10, 80.0, "low")]
        # last_close way above the standard 2.618x extension (80 + 2.618*20 = 132.36)
        ext = build_fib_extension(pivots, n=20, last_close=200.0)
        assert ext is not None
        assert len(ext.levels) > 8
        assert any(l.price > 200.0 for l in ext.levels)
        assert ext.levels[-1].ratio > 2.618
