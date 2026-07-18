import numpy as np
import pandas as pd
import pytest

from equity_rotation.relative_strength import aligned_ratio, rolling_ratio_average


def _series(values, start="2024-01-01"):
    dates = pd.date_range(start, periods=len(values), freq="B")
    return pd.Series(values, index=dates)


class TestAlignedRatio:
    def test_divides_elementwise_on_common_dates(self):
        numerator = _series([10.0, 20.0, 30.0])
        denominator = _series([2.0, 4.0, 5.0])
        ratio = aligned_ratio(numerator, denominator)
        assert list(ratio.to_numpy()) == pytest.approx([5.0, 5.0, 6.0])

    def test_drops_dates_missing_from_either_series(self):
        numerator = _series([10.0, 20.0, 30.0])
        denominator = _series([2.0, 4.0], start="2024-01-01")
        ratio = aligned_ratio(numerator, denominator)
        assert len(ratio) == 2

    def test_drops_nonpositive_values(self):
        numerator = _series([10.0, -5.0, 30.0])
        denominator = _series([2.0, 4.0, 0.0])
        ratio = aligned_ratio(numerator, denominator)
        # row 0 (10/2) is valid; row 1 has a negative numerator, row 2 a
        # zero denominator -- only row 0 survives.
        assert len(ratio) == 1
        assert ratio.iloc[0] == pytest.approx(5.0)

    def test_drops_nan_values(self):
        numerator = _series([10.0, np.nan, 30.0])
        denominator = _series([2.0, 4.0, 5.0])
        ratio = aligned_ratio(numerator, denominator)
        assert len(ratio) == 2


class TestRollingRatioAverage:
    def test_nan_during_warmup(self):
        ratio = _series([1.0, 2.0, 3.0, 4.0])
        avg = rolling_ratio_average(ratio, window=3)
        assert avg.iloc[:2].isna().all()

    def test_matches_manual_mean_after_warmup(self):
        ratio = _series([1.0, 2.0, 3.0, 4.0])
        avg = rolling_ratio_average(ratio, window=3)
        assert avg.iloc[2] == pytest.approx(2.0)
        assert avg.iloc[3] == pytest.approx(3.0)
