import numpy as np
import pandas as pd
import pytest

from rates_macro import report as report_module


def _synthetic_fred_series(n=300, drift=0.01, seed=1):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    values = 100 + drift * np.arange(n) + rng.normal(0, 0.3, n)
    return pd.Series(values, index=dates)


def _synthetic_benchmark(n=300, seed=2):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    values = 400 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, n)))
    return pd.Series(values, index=dates)


def _duplicate_timestamp_series(n=30):
    # Emulates a revised/re-published FRED observation landing on a date
    # that's already present -- a real-world duplicate-timestamp scenario,
    # not just an artificial non-date index.
    dates = pd.date_range("2024-01-01", periods=n // 3, freq="D").repeat(3)
    return pd.Series(np.arange(len(dates), dtype=float), index=dates)


class TestBuildSeriesReport:
    def test_bundles_trend_mean_reversion_and_cross_reference(self):
        series = _synthetic_fred_series()
        benchmark = _synthetic_benchmark()
        result = report_module.build_series_report("Test Series", series, benchmark)
        assert result["label"] == "Test Series"
        assert "trend_signal" in result["trend_rr"]
        assert "z_score" in result["mean_reversion"]
        assert (
            "correlation" in result["vs_benchmark"]["contemporaneous"]
            or "error" in result["vs_benchmark"]["contemporaneous"]
        )
        assert result["latest"] == pytest.approx(series.iloc[-1])

    def test_short_series_degrades_to_error_not_exception(self):
        series = _synthetic_fred_series(n=10)
        benchmark = _synthetic_benchmark()
        result = report_module.build_series_report("Too Short", series, benchmark)
        assert "error" in result["trend_rr"]
        assert result["mean_reversion"] is None

    def test_flags_a_fred_series_stale_relative_to_the_benchmark(self):
        # A FRED series whose latest print trails the equity benchmark by
        # more than MAX_STALENESS_DAYS should be flagged, not silently
        # blended into the cross-reference with the same confidence as a
        # fresh print (e.g. an API hiccup or a discontinued series).
        benchmark = _synthetic_benchmark(n=300)
        stale_series = _synthetic_fred_series(n=270)  # ends ~30 calendar days earlier
        result = report_module.build_series_report("Stale Series", stale_series, benchmark)
        assert result["stale"] is True
        assert result["staleness_days"] > report_module.MAX_STALENESS_DAYS

    def test_does_not_flag_a_fresh_fred_series(self):
        benchmark = _synthetic_benchmark(n=300)
        fresh_series = _synthetic_fred_series(n=300)
        result = report_module.build_series_report("Fresh Series", fresh_series, benchmark)
        assert result["stale"] is False

    def test_cross_reference_failure_degrades_to_error_not_exception(self):
        # Regression: a duplicate-timestamp series (which does happen with
        # revised/re-published FRED observations) makes
        # cross_reference.align()'s pd.concat raise ValueError. That used to
        # propagate straight out of build_series_report; it must now degrade
        # to an `error` key so the series' own trend/mean-reversion numbers
        # (which don't depend on the benchmark) are still returned.
        benchmark = _synthetic_benchmark()
        result = report_module.build_series_report(
            "Duplicate Index", _duplicate_timestamp_series(), benchmark
        )
        assert "error" in result["vs_benchmark"]


class TestBuildReport:
    def test_a_series_with_a_bad_cross_reference_still_reports_its_own_numbers(
        self, monkeypatch
    ):
        # Regression: build_series_report only wrapped trend_rr_profile in
        # try/except -- a failure in mean_reversion_snapshot or
        # cross_reference_report (e.g. a duplicate-timestamp FRED series
        # tripping cross_reference.align()'s pd.concat) propagated all the
        # way out of build_report and wiped out every other series that had
        # already computed successfully in the same run. Now it must degrade
        # to a per-field `error` instead, so GOOD and BAD both come back
        # (BAD missing only its vs_benchmark numbers).
        benchmark = _synthetic_benchmark()
        monkeypatch.setattr(report_module, "fetch_close", lambda ticker: benchmark)

        good_series = _synthetic_fred_series(seed=5)

        def fake_fetch_series(series_id):
            if series_id == "BAD":
                return _duplicate_timestamp_series()
            return good_series

        monkeypatch.setattr(report_module, "fetch_series", fake_fetch_series)

        result = report_module.build_report(
            series_ids={"GOOD": "Good Series", "BAD": "Bad Series"}
        )
        assert "GOOD" in result["series"]
        assert "trend_signal" in result["series"]["GOOD"]["trend_rr"]
        assert "BAD" in result["series"]
        assert "error" in result["series"]["BAD"]["vs_benchmark"]
        assert result["dropped"] == []

    def test_isolates_a_failing_series_from_the_rest(self, monkeypatch):
        benchmark = _synthetic_benchmark()
        monkeypatch.setattr(report_module, "fetch_close", lambda ticker: benchmark)

        good_series = _synthetic_fred_series(seed=5)

        def fake_fetch_series(series_id):
            if series_id == "BAD":
                raise RuntimeError("simulated FRED failure")
            return good_series

        monkeypatch.setattr(report_module, "fetch_series", fake_fetch_series)

        result = report_module.build_report(
            series_ids={"GOOD": "Good Series", "BAD": "Bad Series"}
        )
        assert "GOOD" in result["series"]
        assert "BAD" not in result["series"]
        assert any(d["series_id"] == "BAD" for d in result["dropped"])

    def test_empty_series_is_dropped_not_crashed_on(self, monkeypatch):
        benchmark = _synthetic_benchmark()
        monkeypatch.setattr(report_module, "fetch_close", lambda ticker: benchmark)
        monkeypatch.setattr(
            report_module, "fetch_series", lambda series_id: pd.Series(dtype=float)
        )
        result = report_module.build_report(series_ids={"EMPTY": "Empty Series"})
        assert result["series"] == {}
        assert result["dropped"][0]["reason"] == "no observations"

    def test_raises_when_benchmark_fetch_fails(self, monkeypatch):
        def failing_fetch_close(ticker):
            raise RuntimeError("no benchmark data")

        monkeypatch.setattr(report_module, "fetch_close", failing_fetch_close)
        with pytest.raises(RuntimeError):
            report_module.build_report(series_ids={"X": "X Series"})


class TestRenderSummary:
    def test_produces_readable_text_without_crashing(self, monkeypatch):
        benchmark = _synthetic_benchmark()
        monkeypatch.setattr(report_module, "fetch_close", lambda ticker: benchmark)
        monkeypatch.setattr(
            report_module,
            "fetch_series",
            lambda series_id: _synthetic_fred_series(seed=9),
        )
        result = report_module.build_report(series_ids={"X": "X Series"})
        text = report_module.render_summary(result)
        assert "X Series" in text
        assert isinstance(text, str)

    def test_does_not_crash_when_a_series_has_error_dicts(self, monkeypatch):
        # Regression: once build_series_report started degrading
        # mean_reversion/vs_benchmark failures to {"error": ...} dicts
        # instead of raising, render_summary's mr["z_score"] and
        # r["vs_benchmark"]["contemporaneous"] lookups became unsafe --
        # both raise KeyError on an error dict shaped that way.
        benchmark = _synthetic_benchmark()
        monkeypatch.setattr(report_module, "fetch_close", lambda ticker: benchmark)
        monkeypatch.setattr(
            report_module,
            "fetch_series",
            lambda series_id: _duplicate_timestamp_series(),
        )
        result = report_module.build_report(series_ids={"BAD": "Bad Series"})
        text = report_module.render_summary(result)
        assert "Bad Series" in text


class TestMain:
    def test_prints_series_table_positioning_vulnerability_and_regime(
        self, monkeypatch, capsys
    ):
        benchmark = _synthetic_benchmark()
        monkeypatch.setattr(report_module, "fetch_close", lambda ticker: benchmark)
        monkeypatch.setattr(
            report_module,
            "fetch_series",
            lambda series_id: _synthetic_fred_series(seed=3),
        )
        monkeypatch.setattr(
            report_module,
            "ALL_SERIES",
            {"BAMLH0A0HYM2": "HY OAS", "DTWEXBGS": "USD"},
        )
        report_module.main()
        captured = capsys.readouterr().out
        assert "HY OAS" in captured
        assert "Macro score" in captured  # positioning score
        assert "Red-Zone" in captured  # vulnerability score
        assert "Regime" in captured  # regime read
        assert "/100" in captured
