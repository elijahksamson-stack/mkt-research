import numpy as np
import pandas as pd

from commodities.seasonality import build_seasonal_snapshot


def _dates(n: int, start: str = "2020-01-01") -> pd.DatetimeIndex:
    return pd.DatetimeIndex(pd.bdate_range(start, periods=n))


class TestBuildSeasonalSnapshot:
    def test_never_uses_the_current_or_future_years_own_season(self):
        # ~300 business days doesn't even reach a second calendar year, so as_of
        # partway through it must find zero strictly-prior-year observations.
        dates = _dates(300, start="2020-01-01")
        close = 100 * np.exp(np.cumsum(np.full(300, 0.0005)))

        snapshot = build_seasonal_snapshot("test", dates, close, horizon=5, as_of=dates[150])

        assert snapshot is None  # no strictly-prior year exists yet

    def test_finds_observations_once_a_prior_year_exists(self):
        dates = _dates(600, start="2020-01-01")
        rng = np.random.default_rng(3)
        close = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 600)))

        snapshot = build_seasonal_snapshot("test", dates, close, horizon=5, as_of=dates[-1], min_observations=1)

        assert snapshot is not None
        assert snapshot.n_observations >= 1
        assert all(y < dates[-1].year for y in snapshot.years_covered)

    def test_below_min_observations_returns_none(self):
        dates = _dates(600, start="2020-01-01")
        close = np.full(600, 100.0)

        snapshot = build_seasonal_snapshot("test", dates, close, horizon=5, as_of=dates[-1], min_observations=999)

        assert snapshot is None
