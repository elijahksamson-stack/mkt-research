import numpy as np
import pandas as pd

from commodities.labels import compute_forward_label, max_as_of_index, trading_day_grid


def _dates(n: int) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(pd.bdate_range("2023-01-01", periods=n))


class TestMaxAsOfIndex:
    def test_matches_hand_computed_value(self):
        assert max_as_of_index(n_bars=300, max_horizon=63) == 300 - 63 - 1


class TestTradingDayGrid:
    def test_empty_when_history_is_shorter_than_warmup(self):
        dates = _dates(100)

        grid = trading_day_grid(dates, horizons=(21,), warmup_bars=260)

        assert grid == []

    def test_grid_never_includes_a_day_without_a_fully_realized_longest_horizon_label(self):
        dates = _dates(400)

        grid = trading_day_grid(dates, horizons=(5, 21, 63), warmup_bars=260, step=5)

        last_allowed_idx = max_as_of_index(len(dates), 63)
        assert all(d <= dates[last_allowed_idx] for d in grid)

    def test_step_controls_spacing_between_grid_points(self):
        dates = _dates(400)

        grid = trading_day_grid(dates, horizons=(21,), warmup_bars=260, step=10)

        assert len(grid) >= 2
        # Grid points should be 10 trading days apart (bdate_range has no gaps to worry about here).
        gaps = {(grid[i + 1] - grid[i]).days for i in range(len(grid) - 1)}
        assert gaps == {14}  # 10 business days = 14 calendar days


class TestComputeForwardLabel:
    def test_uptrend_produces_a_positive_forward_return(self):
        dates = _dates(40)
        close = 100 * np.exp(0.01 * np.arange(40))

        label = compute_forward_label(dates, close, as_of=dates[10], horizon=5)

        assert label is not None
        assert label.forward_return > 0
        assert label.forward_direction is True

    def test_as_of_not_in_the_series_returns_none(self):
        dates = _dates(40)
        close = np.full(40, 100.0)
        missing_date = pd.Timestamp("2099-01-01")

        label = compute_forward_label(dates, close, as_of=missing_date, horizon=5)

        assert label is None

    def test_horizon_reaching_past_the_end_of_history_returns_none(self):
        dates = _dates(10)
        close = np.full(10, 100.0)

        label = compute_forward_label(dates, close, as_of=dates[8], horizon=5)

        assert label is None
