import pytest

from crypto_structure.crypto_gauge import build_gauge
from crypto_structure.risk_reward import RiskRewardReport
from crypto_structure.stop_target import StopTarget
from crypto_structure.trend_violation import TrendViolation


def _report(ticker, rr_ratio, target_source, violation_status, breach_atr=0.0, bars_since_break=None):
    stop_target = StopTarget(
        stop=95.0, target=110.0, risk=5.0, reward=10.0, risk_pct=5.0, reward_pct=10.0,
        rr_ratio=rr_ratio, stop_cluster=95.0, target_cluster=110.0, vol_factor=1.0,
        target_source=target_source, target_fib_ratio=None,
    )
    trend_violation = TrendViolation(
        status=violation_status, trendline=None, breach_atr=breach_atr, bars_since_break=bars_since_break
    )
    return RiskRewardReport(
        ticker=ticker, last_close=100.0, atr=1.0, hv=0.02, rvol=1.0,
        clusters=[], regression_trendlines=[], pivot_pair_lines=[], fib_extension=None,
        stop_target=stop_target, trend_violation=trend_violation,
    )


SMALL_UNIVERSE = {"BTC-USD": "Bitcoin", "ETH-USD": "Ethereum"}


class TestBuildGauge:
    def test_strong_trend_and_rr_yields_high_risk_score(self):
        reports = {
            "BTC-USD": _report("BTC-USD", rr_ratio=3.0, target_source="cluster", violation_status="intact"),
            "ETH-USD": _report("ETH-USD", rr_ratio=3.0, target_source="cluster", violation_status="intact"),
        }
        trend_signals = {"BTC-USD": 0.8, "ETH-USD": 0.8}
        gauge = build_gauge(reports, trend_signals, universe=SMALL_UNIVERSE)
        assert gauge.overall_risk_score > 80

    def test_undercut_trend_pulls_risk_score_down(self):
        base_reports = {
            "BTC-USD": _report("BTC-USD", rr_ratio=3.0, target_source="cluster", violation_status="intact"),
            "ETH-USD": _report("ETH-USD", rr_ratio=3.0, target_source="cluster", violation_status="intact"),
        }
        undercut_reports = {
            "BTC-USD": _report(
                "BTC-USD", rr_ratio=3.0, target_source="cluster", violation_status="undercut",
                breach_atr=2.0, bars_since_break=3,
            ),
            "ETH-USD": _report("ETH-USD", rr_ratio=3.0, target_source="cluster", violation_status="intact"),
        }
        trend_signals = {"BTC-USD": 0.8, "ETH-USD": 0.8}
        base_gauge = build_gauge(base_reports, trend_signals, universe=SMALL_UNIVERSE)
        undercut_gauge = build_gauge(undercut_reports, trend_signals, universe=SMALL_UNIVERSE)
        assert undercut_gauge.overall_risk_score < base_gauge.overall_risk_score

    def test_synthetic_target_source_scores_lower_than_cluster_at_same_ratio(self):
        cluster_reports = {
            "BTC-USD": _report("BTC-USD", rr_ratio=2.0, target_source="cluster", violation_status="intact"),
            "ETH-USD": _report("ETH-USD", rr_ratio=2.0, target_source="cluster", violation_status="intact"),
        }
        synthetic_reports = {
            "BTC-USD": _report("BTC-USD", rr_ratio=2.0, target_source="synthetic", violation_status="intact"),
            "ETH-USD": _report("ETH-USD", rr_ratio=2.0, target_source="synthetic", violation_status="intact"),
        }
        trend_signals = {"BTC-USD": 0.0, "ETH-USD": 0.0}
        cluster_gauge = build_gauge(cluster_reports, trend_signals, universe=SMALL_UNIVERSE)
        synthetic_gauge = build_gauge(synthetic_reports, trend_signals, universe=SMALL_UNIVERSE)
        assert synthetic_gauge.overall_risk_score < cluster_gauge.overall_risk_score

    def test_breadth_undercut_pct_reflects_weighted_share(self):
        reports = {
            "BTC-USD": _report(
                "BTC-USD", rr_ratio=1.0, target_source="cluster", violation_status="undercut",
                breach_atr=1.0, bars_since_break=1,
            ),
            "ETH-USD": _report("ETH-USD", rr_ratio=1.0, target_source="cluster", violation_status="intact"),
        }
        trend_signals = {"BTC-USD": 0.0, "ETH-USD": 0.0}
        gauge = build_gauge(reports, trend_signals, universe=SMALL_UNIVERSE)
        assert gauge.breadth_undercut_pct == pytest.approx(0.5)

    def test_majority_undercut_amplifies_risk_off_pct(self):
        reports = {
            "BTC-USD": _report(
                "BTC-USD", rr_ratio=1.0, target_source="cluster", violation_status="undercut",
                breach_atr=1.0, bars_since_break=1,
            ),
            "ETH-USD": _report(
                "ETH-USD", rr_ratio=1.0, target_source="cluster", violation_status="undercut",
                breach_atr=1.0, bars_since_break=1,
            ),
        }
        trend_signals = {"BTC-USD": 0.0, "ETH-USD": 0.0}
        gauge = build_gauge(reports, trend_signals, universe=SMALL_UNIVERSE)
        # 100% breadth undercut -> full +20 amplifier on top of the base,
        # clamped at the gauge's 100 ceiling.
        expected = min(100.0, 100.0 - gauge.overall_risk_score + 20.0)
        assert gauge.risk_off_pct == pytest.approx(expected)
        assert gauge.risk_off_pct == pytest.approx(100.0)

    def test_missing_ticker_is_skipped_and_weights_renormalize(self):
        reports = {"BTC-USD": _report("BTC-USD", rr_ratio=2.0, target_source="cluster", violation_status="intact")}
        trend_signals = {"BTC-USD": 0.5}
        gauge = build_gauge(reports, trend_signals, universe=SMALL_UNIVERSE)
        assert len(gauge.assets) == 1
        assert gauge.assets[0].weight == pytest.approx(1.0)

    def test_raises_when_no_overlap_with_universe(self):
        with pytest.raises(ValueError):
            build_gauge({}, {}, universe=SMALL_UNIVERSE)

    def test_blurb_mentions_undercut_language_when_violated(self):
        reports = {
            "BTC-USD": _report(
                "BTC-USD", rr_ratio=1.5, target_source="cluster", violation_status="undercut",
                breach_atr=1.5, bars_since_break=2,
            ),
        }
        trend_signals = {"BTC-USD": -0.2}
        gauge = build_gauge(reports, trend_signals, universe={"BTC-USD": "Bitcoin"})
        assert "undercut" in gauge.assets[0].blurb
        assert "risk off" in gauge.assets[0].blurb

    def test_risk_score_breakdown_fields_reconstruct_the_final_score(self):
        reports = {
            "BTC-USD": _report(
                "BTC-USD", rr_ratio=0.85, target_source="cluster", violation_status="undercut",
                breach_atr=3.9, bars_since_break=12,
            ),
        }
        trend_signals = {"BTC-USD": 0.54}
        gauge = build_gauge(reports, trend_signals, universe={"BTC-USD": "Bitcoin"})
        ag = gauge.assets[0]
        # trend_component = (0.54+1)*50 = 77.0 -> contribution 0.55*77.0 = 42.35
        assert ag.trend_component == pytest.approx(77.0)
        assert ag.trend_contribution == pytest.approx(0.55 * 77.0)
        # rr magnitude = min(0.85,3)/3*100 = 28.333..., quality(cluster)=1.0
        assert ag.rr.magnitude == pytest.approx(0.85 / 3.0 * 100.0)
        assert ag.rr.quality_multiplier == pytest.approx(1.0)
        assert ag.rr_contribution == pytest.approx(0.45 * ag.rr.component)
        # violation: base 15 + streak min(5*12,25)=25 + breach min(5*3.9,15)=15 -> 55
        assert ag.violation.base == pytest.approx(15.0)
        assert ag.violation.streak_penalty == pytest.approx(25.0)
        assert ag.violation.breach_penalty == pytest.approx(15.0)
        assert ag.violation.total == pytest.approx(55.0)
        # the stored breakdown fields must reconstruct risk_score exactly (clipped 0-100)
        reconstructed = min(100.0, max(0.0, ag.trend_contribution + ag.rr_contribution - ag.violation.total))
        assert ag.risk_score == pytest.approx(reconstructed)

    def test_intact_ticker_has_zero_violation_penalty(self):
        reports = {"BTC-USD": _report("BTC-USD", rr_ratio=1.0, target_source="cluster", violation_status="intact")}
        gauge = build_gauge(reports, {"BTC-USD": 0.0}, universe={"BTC-USD": "Bitcoin"})
        v = gauge.assets[0].violation
        assert (v.base, v.streak_penalty, v.breach_penalty, v.total) == (0.0, 0.0, 0.0, 0.0)

    def test_assets_sorted_by_risk_score_descending(self):
        reports = {
            "BTC-USD": _report("BTC-USD", rr_ratio=3.0, target_source="cluster", violation_status="intact"),
            "ETH-USD": _report("ETH-USD", rr_ratio=0.1, target_source="synthetic", violation_status="undercut",
                                breach_atr=3.0, bars_since_break=10),
        }
        trend_signals = {"BTC-USD": 0.9, "ETH-USD": -0.9}
        gauge = build_gauge(reports, trend_signals, universe=SMALL_UNIVERSE)
        assert gauge.assets[0].ticker == "BTC-USD"
        assert gauge.assets[-1].ticker == "ETH-USD"
