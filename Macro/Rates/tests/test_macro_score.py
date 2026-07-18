import pytest

from rates_macro import macro_score as macro_score_module
from rates_macro.macro_score import macro_score, render_macro_score, series_signal


def _series_report(
    label,
    trend_signal=None,
    correlation=None,
    stale=False,
    trend_error=False,
    xref_error=False,
):
    trend_rr = (
        {"error": "insufficient data"}
        if trend_error
        else {"trend_signal": trend_signal, "opportunity": 50.0}
    )
    contemporaneous = (
        {"error": "insufficient data"}
        if xref_error
        else {"correlation": correlation, "beta": 0.1}
    )
    return {
        "label": label,
        "trend_rr": trend_rr,
        "mean_reversion": {"z_score": 0.0},
        "vs_benchmark": {"contemporaneous": contemporaneous, "lead_lag": {"best_lag": 0}},
        "latest": 1.0,
        "as_of": "2026-01-01",
        "stale": stale,
        "staleness_days": 0,
    }


def _report(series: dict) -> dict:
    return {
        "benchmark": "SPY",
        "benchmark_as_of": "2026-01-01",
        "series": series,
        "dropped": [],
    }


class TestSeriesSignal:
    def test_healthy_series_returns_signed_alignment(self):
        report = _series_report("Test", trend_signal=0.6, correlation=-0.1)
        signal = series_signal(report)
        assert signal["signed_alignment"] == pytest.approx(-0.06)

    def test_stale_series_is_excluded(self):
        report = _series_report("Test", trend_signal=0.6, correlation=-0.1, stale=True)
        assert series_signal(report) is None

    def test_trend_error_is_excluded(self):
        report = _series_report("Test", correlation=-0.1, trend_error=True)
        assert series_signal(report) is None

    def test_cross_reference_error_is_excluded(self):
        report = _series_report("Test", trend_signal=0.6, xref_error=True)
        assert series_signal(report) is None


class TestMacroScore:
    def test_matches_hand_calculation_with_all_categories_present(self):
        report = _report(
            {
                "DGS10": _series_report("10Y", trend_signal=0.6, correlation=-0.1),
                "DGS2": _series_report("2Y", trend_signal=0.4, correlation=-0.1),
                "DFF": _series_report("Fed Funds", trend_signal=-0.2, correlation=0.2),
                "BAMLH0A0HYM2": _series_report("HY OAS", trend_signal=-0.5, correlation=-0.8),
                "DTWEXBGS": _series_report("USD", trend_signal=0.5, correlation=-0.4),
            }
        )
        result = macro_score(report)
        # rates avg alignment = (-0.06 -0.04 -0.04)/3 = -0.14/3; credit = 0.4; fx = -0.2
        # contribution = weight(1/3) * avg * 50, summed, weight_used = 1.0
        # score = 50 + (-7/9 + 20/3 - 10/3) = 50 + 23/9
        assert result["score"] == pytest.approx(50 + 23 / 9, abs=0.05)
        assert result["categories"]["credit"]["contribution_points"] > 0
        assert result["categories"]["fx"]["contribution_points"] < 0
        assert result["excluded"] == []

    def test_missing_category_renormalizes_instead_of_silently_diluting(self):
        # Only rates + fx survive (no credit series present at all) -- the
        # score must renormalize over the surviving weight, not silently
        # treat the missing category as a neutral (0-alignment) vote, which
        # would drag every score toward 50 whenever any category happens to
        # be absent from the requested series set.
        report = _report(
            {
                "DGS10": _series_report("10Y", trend_signal=0.6, correlation=-0.1),
                "DGS2": _series_report("2Y", trend_signal=0.4, correlation=-0.1),
                "DFF": _series_report("Fed Funds", trend_signal=-0.2, correlation=0.2),
                "DTWEXBGS": _series_report("USD", trend_signal=0.5, correlation=-0.4),
            }
        )
        result = macro_score(report)
        rates_contribution = (1 / 3) * (-0.14 / 3) * 50
        fx_contribution = (1 / 3) * (-0.2) * 50
        weight_used = 2 / 3
        expected = 50 + (rates_contribution + fx_contribution) / weight_used
        assert result["score"] == pytest.approx(expected, abs=0.05)
        assert "credit" not in result["categories"]

    def test_no_surviving_series_returns_neutral_score_without_crashing(self):
        report = _report(
            {
                "DGS10": _series_report("10Y", trend_signal=0.6, correlation=-0.1, stale=True),
            }
        )
        result = macro_score(report)
        assert result["score"] == 50.0
        assert len(result["excluded"]) == 1

    def test_custom_category_weights_are_respected(self):
        report = _report(
            {
                "BAMLH0A0HYM2": _series_report("HY OAS", trend_signal=-0.5, correlation=-0.8),
                "DTWEXBGS": _series_report("USD", trend_signal=0.5, correlation=-0.4),
            }
        )
        equal = macro_score(report, category_weights={"credit": 0.5, "fx": 0.5})
        credit_heavy = macro_score(report, category_weights={"credit": 0.9, "fx": 0.1})
        # Credit's alignment is positive (+0.4) and fx's is negative (-0.2),
        # so weighting credit more heavily should push the score up.
        assert credit_heavy["score"] > equal["score"]

    def test_score_is_clipped_to_zero_and_hundred(self):
        report = _report(
            {
                "BAMLH0A0HYM2": _series_report("HY OAS", trend_signal=1.0, correlation=1.0),
            }
        )
        result = macro_score(report, category_weights={"credit": 5.0})
        assert 0.0 <= result["score"] <= 100.0


class TestLabelFor:
    @pytest.mark.parametrize(
        "score,expected",
        [
            (65, "bullish"),
            (64.9, "mildly bullish"),
            (55, "mildly bullish"),
            (50, "neutral"),
            (45, "neutral"),
            (35, "mildly bearish"),
            (34.9, "bearish"),
            (0, "bearish"),
            (100, "bullish"),
        ],
    )
    def test_boundaries(self, score, expected):
        assert macro_score_module._label_for(score) == expected


class TestRenderMacroScore:
    def test_renders_without_crashing_on_a_normal_result(self):
        report = _report(
            {
                "BAMLH0A0HYM2": _series_report("HY OAS", trend_signal=-0.5, correlation=-0.8),
                "DTWEXBGS": _series_report("USD", trend_signal=0.5, correlation=-0.4),
            }
        )
        text = render_macro_score(macro_score(report))
        assert "HY OAS" in text
        assert isinstance(text, str)

    def test_renders_without_crashing_when_everything_is_excluded(self):
        report = _report(
            {
                "DGS10": _series_report("10Y", trend_signal=0.6, correlation=-0.1, stale=True),
            }
        )
        text = render_macro_score(macro_score(report))
        assert isinstance(text, str)
        assert "10Y" in text
