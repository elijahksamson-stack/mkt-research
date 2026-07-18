import pytest

from rates_macro import regime as regime_module
from rates_macro.regime import regime, render_regime


class TestRegime:
    def test_high_positioning_low_vulnerability_is_healthy_expansion(self):
        r = regime(positioning_score=70, vulnerability_score=20)
        assert r["quadrant"] == "healthy_expansion"
        assert r["positioning"] == "constructive"
        assert r["vulnerability"] == "contained"

    def test_high_positioning_high_vulnerability_is_red_zone(self):
        r = regime(positioning_score=70, vulnerability_score=80)
        assert r["quadrant"] == "red_zone_froth"
        assert "⚠" in r["flag"]

    def test_low_positioning_low_vulnerability_is_correction(self):
        r = regime(positioning_score=35, vulnerability_score=20)
        assert r["quadrant"] == "correction_reset"

    def test_low_positioning_high_vulnerability_is_crisis_unwind(self):
        r = regime(positioning_score=30, vulnerability_score=85)
        assert r["quadrant"] == "crisis_unwind"
        assert r["flag"].count("⚠") >= 2

    def test_thresholds_are_configurable(self):
        # With a low vulnerability threshold, a mid vuln reads as elevated
        hot = regime(positioning_score=70, vulnerability_score=55, vulnerability_threshold=50)
        cool = regime(positioning_score=70, vulnerability_score=55, vulnerability_threshold=66)
        assert hot["quadrant"] == "red_zone_froth"
        assert cool["quadrant"] == "healthy_expansion"

    def test_vulnerability_uses_a_tail_threshold_by_default(self):
        # Red-Zone is a tail condition (Greenwood: top-quintile froth), so a
        # merely-above-50 vulnerability should NOT trip the red zone by default.
        r = regime(positioning_score=70, vulnerability_score=55)
        assert r["quadrant"] == "healthy_expansion"

    def test_none_vulnerability_degrades_gracefully(self):
        # If the Red-Zone score couldn't be computed (all legs excluded), the
        # regime still returns a positioning-only read rather than crashing.
        r = regime(positioning_score=70, vulnerability_score=None)
        assert r["quadrant"] in ("positioning_only", "healthy_expansion", "correction_reset")
        assert r["vulnerability"] == "unknown"

    def test_rationale_mentions_both_scores(self):
        r = regime(positioning_score=70, vulnerability_score=80)
        assert "70" in r["rationale"]
        assert "80" in r["rationale"]


class TestRenderRegime:
    def test_renders_readable_text(self):
        text = render_regime(regime(positioning_score=70, vulnerability_score=80))
        assert isinstance(text, str)
        assert "Regime" in text or "regime" in text

    def test_renders_when_vulnerability_unknown(self):
        text = render_regime(regime(positioning_score=70, vulnerability_score=None))
        assert isinstance(text, str)
