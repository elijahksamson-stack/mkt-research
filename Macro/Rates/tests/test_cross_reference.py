import numpy as np
import pandas as pd
import pytest

from rates_macro.cross_reference import (
    align,
    beta_of,
    correlate_series,
    cross_reference_report,
    lead_lag_correlation,
    pearson_correlation,
    to_changes,
)


class TestToChanges:
    def test_diff_method(self):
        series = pd.Series([1.0, 3.0, 6.0, 10.0])
        changes = to_changes(series, method="diff")
        assert list(changes) == pytest.approx([2.0, 3.0, 4.0])

    def test_log_return_method(self):
        series = pd.Series([1.0, np.e, np.e**2])
        changes = to_changes(series, method="log_return")
        assert list(changes) == pytest.approx([1.0, 1.0])

    def test_log_return_drops_non_positive_values(self):
        series = pd.Series([1.0, -2.0, 4.0])
        changes = to_changes(series, method="log_return")
        # -2.0 is filtered before the diff, so no changes survive the gap
        assert len(changes) <= 1

    def test_unknown_method_raises(self):
        with pytest.raises(ValueError):
            to_changes(pd.Series([1.0, 2.0]), method="bogus")


class TestAlign:
    def test_inner_joins_on_overlapping_index(self):
        a = pd.Series([1.0, 2.0, 3.0], index=[0, 1, 2])
        b = pd.Series([10.0, 20.0], index=[1, 2])
        xs, ys = align(a, b)
        assert list(xs) == pytest.approx([2.0, 3.0])
        assert list(ys) == pytest.approx([10.0, 20.0])


class TestPearsonCorrelation:
    def test_perfect_positive_correlation(self):
        xs = np.arange(30, dtype=float)
        ys = 2 * xs + 1
        assert pearson_correlation(xs, ys) == pytest.approx(1.0)

    def test_perfect_negative_correlation(self):
        xs = np.arange(30, dtype=float)
        ys = -3 * xs + 5
        assert pearson_correlation(xs, ys) == pytest.approx(-1.0)

    def test_returns_none_below_min_observations(self):
        xs = np.arange(5, dtype=float)
        ys = np.arange(5, dtype=float)
        assert pearson_correlation(xs, ys, min_observations=20) is None

    def test_returns_none_for_zero_variance(self):
        xs = np.ones(30)
        ys = np.arange(30, dtype=float)
        assert pearson_correlation(xs, ys) is None


class TestBetaOf:
    def test_beta_of_double_relationship(self):
        xs = np.arange(30, dtype=float)
        ys = 2 * xs
        assert beta_of(xs, ys) == pytest.approx(2.0)

    def test_beta_of_inverse_relationship(self):
        xs = np.arange(30, dtype=float)
        ys = -0.5 * xs
        assert beta_of(xs, ys) == pytest.approx(-0.5)

    def test_returns_none_below_min_observations(self):
        xs = np.arange(5, dtype=float)
        ys = np.arange(5, dtype=float)
        assert beta_of(xs, ys, min_observations=20) is None


class TestCalendarMismatch:
    def test_correlation_survives_a_series_missing_dates_the_other_has(self):
        # Regression: to_changes() used to diff each series on its OWN index
        # independently, then align() joined the resulting CHANGE series by
        # date afterward. When `a` is missing dates `b` has (e.g. a
        # bond-market-only holiday `b`'s equity calendar doesn't observe),
        # a's diff on the next available date silently spans two days while
        # b's diff on that same date spans only one -- correlating
        # mismatched-period "changes" as if they were contemporaneous.
        # Fix: align on shared LEVEL dates first, then diff, so both sides'
        # changes are always computed over identical date spans.
        rng = np.random.default_rng(42)
        n = 90
        master_dates = pd.date_range("2024-01-01", periods=n, freq="D")
        shock = rng.normal(0, 1, n)
        b_full = pd.Series(
            np.cumsum(-0.5 * shock + rng.normal(0, 0.001, n)) + 100, index=master_dates
        )
        a_full = pd.Series(np.cumsum(shock) + 100, index=master_dates)
        a = a_full[np.arange(n) % 3 != 0]  # drop every 3rd date from a only

        result = correlate_series(a, b_full, method_a="diff", method_b="diff")
        assert result["correlation"] < -0.95


class TestCorrelateSeries:
    def test_insufficient_data_returns_error(self):
        a = pd.Series(np.arange(5, dtype=float))
        b = pd.Series(np.arange(5, dtype=float) * 2)
        result = correlate_series(a, b, min_observations=20)
        assert "error" in result

    def test_inversely_related_diff_series(self):
        # widening credit spread (a rises, noisily) alongside falling equities
        # (b's log-return is the negated, scaled spread move plus tiny noise)
        rng = np.random.default_rng(3)
        da = rng.normal(1.0, 0.3, 60)
        b_log_returns = -0.5 * da + rng.normal(0, 0.01, 60)
        a = pd.Series(np.cumsum(da) + 100)
        b = pd.Series(np.exp(np.cumsum(b_log_returns)) * 100)
        result = correlate_series(a, b, method_a="diff", method_b="log_return")
        assert result["correlation"] < -0.9
        assert result["beta"] < 0


class TestLeadLagCorrelation:
    def test_a_leads_b_by_known_lag(self):
        rng = np.random.default_rng(7)
        da = rng.normal(0, 1, 200)
        lag_true = 3
        # b's diff at t equals a's diff at t - lag_true: a leads b by lag_true.
        b_diffs = np.zeros(200)
        b_diffs[lag_true:] = da[:-lag_true]
        a = pd.Series(np.cumsum(da) + 100)
        b = pd.Series(np.cumsum(b_diffs) + 100)
        result = lead_lag_correlation(a, b, max_lag=6, method_a="diff", method_b="diff")
        assert result["best_lag"] == lag_true
        assert result["best_correlation"] == pytest.approx(1.0, abs=1e-6)

    def test_returns_none_when_insufficient_overlap(self):
        a = pd.Series(np.arange(5, dtype=float))
        b = pd.Series(np.arange(5, dtype=float))
        result = lead_lag_correlation(a, b, max_lag=2, min_observations=20)
        assert result["best_lag"] is None
        assert result["best_correlation"] is None


class TestCrossReferenceReport:
    def test_report_bundles_contemporaneous_and_lead_lag(self):
        rng = np.random.default_rng(11)
        da = rng.normal(1.0, 0.3, 80)
        b_log_returns = -0.5 * da + rng.normal(0, 0.01, 80)
        a = pd.Series(np.cumsum(da) + 100)
        b = pd.Series(np.exp(np.cumsum(b_log_returns)) * 100)
        report = cross_reference_report(
            a, b, name_a="HY OAS", name_b="S&P 500", method_a="diff", method_b="log_return"
        )
        assert report["name_a"] == "HY OAS"
        assert report["name_b"] == "S&P 500"
        assert "correlation" in report["contemporaneous"]
        assert "best_lag" in report["lead_lag"]
