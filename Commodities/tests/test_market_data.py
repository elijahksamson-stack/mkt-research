import numpy as np
import pandas as pd
import pytest

from commodities.market_data import build_roll_adjusted_close


def _dates(n: int, start: str = "2024-01-01") -> pd.DatetimeIndex:
    return pd.DatetimeIndex(pd.bdate_range(start, periods=n))


class TestBuildRollAdjustedClose:
    def test_smooth_series_produces_no_roll_events(self):
        rng = np.random.default_rng(1)
        n = 120
        close = 100 * np.exp(np.cumsum(rng.normal(0, 0.005, n)))
        dates = _dates(n)

        adjusted, events = build_roll_adjusted_close(dates, close)

        assert events == ()
        np.testing.assert_allclose(adjusted, close)

    def test_a_jump_at_a_month_boundary_is_detected_and_removed(self):
        n = 80
        dates = _dates(n)
        close = np.full(n, 100.0)
        jump_idx = max(next(i for i in range(1, n) if dates[i].day <= 3), 1)
        close[jump_idx:] *= 1.08

        adjusted, events = build_roll_adjusted_close(dates, close)

        assert len(events) == 1
        # Post-adjustment, the segment before the roll should trade continuously into the segment after it.
        assert adjusted[jump_idx - 1] == pytest.approx(adjusted[jump_idx], rel=1e-6)

    def test_a_large_jump_mid_month_is_not_treated_as_a_roll(self):
        n = 80
        dates = _dates(n)
        close = np.full(n, 100.0)
        mid_month_idx = next(i for i in range(10, n) if dates[i].day > 10)
        close[mid_month_idx:] *= 1.08

        adjusted, events = build_roll_adjusted_close(dates, close)

        assert events == ()
        np.testing.assert_allclose(adjusted, close)

    def test_short_series_returns_unchanged_copy(self):
        dates = _dates(2)
        close = np.array([100.0, 101.0])

        adjusted, events = build_roll_adjusted_close(dates, close)

        assert events == ()
        np.testing.assert_allclose(adjusted, close)
        assert adjusted is not close  # copy, not the same array (immutability convention)
