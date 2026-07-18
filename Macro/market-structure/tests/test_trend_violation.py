import numpy as np

from market_structure.trend_violation import detect_trend_violation


def _ascending_support_series(n, dip_centers=(10, 50), depth=5.0, radius=6.0, slope=0.5, stall_from=None):
    # Same dip-based construction as test_trendlines.py: a rising baseline
    # with genuine local "V" dips at each dip center, so find_local_extrema
    # actually flags those bars as swing lows (a monotonic rising baseline
    # alone never has an interior local minimum).
    idxs = np.arange(n)
    baseline = 100 + slope * idxs
    dip = np.zeros(n)
    for center in dip_centers:
        dip += depth * np.maximum(0, 1 - np.abs(idxs - center) / radius)
    low = baseline - dip
    if stall_from is not None:
        low = low.copy()
        low[stall_from:] = low[stall_from - 1]
    high = low + 1.0
    close = low + 0.3
    return high, low, close


def _ascending_support_then_stall(n=80, stall_from=51):
    """An uptrend with two higher-low touches (idx 10, 50) on a rising
    support line, then price stalls flat instead of keeping pace with the
    line -- the "undercut support of uptrend" setup from the screenshot."""
    return _ascending_support_series(n, stall_from=stall_from)


def _ascending_support_intact(n=68):
    return _ascending_support_series(n)


class TestDetectTrendViolation:
    def test_flags_undercut_when_price_stalls_below_the_rising_line(self):
        high, low, close = _ascending_support_then_stall()
        result = detect_trend_violation(high, low, close, atr=5.0)
        assert result.status == "undercut"
        assert result.trendline is not None
        assert result.breach_atr > 0
        assert result.bars_since_break is not None
        assert result.bars_since_break >= 1

    def test_reports_intact_when_price_holds_above_the_rising_line(self):
        high, low, close = _ascending_support_intact()
        result = detect_trend_violation(high, low, close, atr=1.0)
        assert result.status == "intact"
        assert result.trendline is not None
        assert result.breach_atr <= 0
        assert result.bars_since_break is None

    def test_reports_no_active_trendline_on_a_flat_series(self):
        n = 80
        high = np.full(n, 100.0)
        low = np.full(n, 99.0)
        close = np.full(n, 99.5)
        result = detect_trend_violation(high, low, close, atr=1.0)
        assert result.status == "no_active_trendline"
        assert result.trendline is None
        assert result.bars_since_break is None
        assert result.breach_atr == 0.0

    def test_reuses_precomputed_pivot_pair_lines_when_provided(self):
        from market_structure.trendlines import build_pivot_pair_trendlines

        high, low, close = _ascending_support_then_stall()
        lines = build_pivot_pair_trendlines(high, low, atr=5.0)
        result = detect_trend_violation(high, low, close, atr=5.0, pivot_pair_lines=lines)
        assert result.status == "undercut"
