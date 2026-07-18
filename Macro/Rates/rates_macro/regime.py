"""
Regime read — combine the positioning score (momentum) and the vulnerability
score (Red-Zone froth) into a 2x2 quadrant WITHOUT blending them into one
number. Keeping them on separate axes is the point: froth reads bullish to the
positioning score and dangerous to the vulnerability score at the same time,
and that divergence — high positioning AND high vulnerability — is the
late-cycle "Red-Zone" quadrant the Greenwood-Hanson work is about.

                     LOW vulnerability        HIGH vulnerability
  HIGH positioning   healthy_expansion        red_zone_froth        ⚠
  LOW  positioning   correction_reset         crisis_unwind         ⚠⚠
"""
from __future__ import annotations

from typing import Optional

POSITIONING_THRESHOLD = 50.0  # positioning is symmetric around 50 = neutral
# Red-Zone froth is a TAIL condition (Greenwood: crises come from top-quintile
# credit+asset froth), so "elevated" is well above the midpoint, not just >50.
VULNERABILITY_THRESHOLD = 66.0

_QUADRANTS = {
    (True, False): (
        "healthy_expansion",
        "",
        "Constructive momentum with contained fragility — a healthy expansion.",
    ),
    (True, True): (
        "red_zone_froth",
        "⚠",
        "Momentum looks strong precisely while froth is elevated — the "
        "late-cycle Red-Zone: attractive on the surface, structurally fragile.",
    ),
    (False, False): (
        "correction_reset",
        "",
        "Weak momentum but low systemic froth — a correction/reset, not a "
        "credit-driven crisis setup.",
    ),
    (False, True): (
        "crisis_unwind",
        "⚠⚠",
        "Weak momentum WITH elevated froth — the dangerous unwind quadrant, "
        "where built-up fragility meets deteriorating price action.",
    ),
}


def regime(
    positioning_score: float,
    vulnerability_score: Optional[float],
    positioning_threshold: float = POSITIONING_THRESHOLD,
    vulnerability_threshold: float = VULNERABILITY_THRESHOLD,
) -> dict:
    """Map (positioning, vulnerability) onto a regime quadrant.

    `vulnerability_score` may be None (Red-Zone score uncomputable — all legs
    excluded); the read degrades to positioning-only rather than crashing.
    """
    hi_pos = positioning_score >= positioning_threshold
    positioning_label = "constructive" if hi_pos else "defensive"

    if vulnerability_score is None:
        return {
            "quadrant": "positioning_only",
            "flag": "",
            "positioning": positioning_label,
            "vulnerability": "unknown",
            "positioning_score": positioning_score,
            "vulnerability_score": None,
            "rationale": (
                f"Positioning {positioning_score:.0f}/100 ({positioning_label}); "
                "vulnerability unavailable (Red-Zone legs could not be computed), "
                "so no regime quadrant is assigned."
            ),
        }

    hi_vul = vulnerability_score >= vulnerability_threshold
    quadrant, flag, description = _QUADRANTS[(hi_pos, hi_vul)]
    vulnerability_label = "elevated" if hi_vul else "contained"

    rationale = (
        f"Positioning {positioning_score:.0f}/100 ({positioning_label}) × "
        f"vulnerability {vulnerability_score:.0f}/100 ({vulnerability_label}). "
        f"{description}"
    )
    return {
        "quadrant": quadrant,
        "flag": flag,
        "positioning": positioning_label,
        "vulnerability": vulnerability_label,
        "positioning_score": positioning_score,
        "vulnerability_score": vulnerability_score,
        "rationale": rationale,
    }


def render_regime(result: dict) -> str:
    """One-line-ish plain-text regime read."""
    flag = f" {result['flag']}" if result["flag"] else ""
    title = result["quadrant"].replace("_", " ").title()
    return f"Regime: {title}{flag}\n  {result['rationale']}"
