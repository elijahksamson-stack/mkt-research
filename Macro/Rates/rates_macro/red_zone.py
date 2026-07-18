"""
Vulnerability (Red-Zone) score — Greenwood-Hanson style.

Where macro_score.py reads *momentum* (trend × how a series co-moves with the
S&P right now), this reads *latent fragility*: how much financial-crisis risk
is building, scored on each input's own level/change vs. its OWN history —
deliberately NOT on its current correlation to equities. That's the whole
point: crisis-warning signals matter precisely when they are NOT yet reflected
in market prices, so scoring them by equity co-movement would suppress the
early warning. The two scores are kept separate on purpose (see regime.py for
how they combine) — a single blended number would hide the divergence that is
the entire lesson of the Greenwood-Hanson "Red-Zone" work.

The Red-Zone is a CONJUNCTION of three froth legs, each a 0-100 percentile:
  - price   : credit-spread compression (investors stopped pricing downside)
  - asset   : market-cap-to-GDP elevation (asset prices high)
  - quantity: credit-to-GDP EXPANSION (credit growing faster than the economy)
Greenwood is explicit that a crisis needs the COMBINATION, not any one leg —
so the legs are combined with a weighted GEOMETRIC mean, which any single cold
leg drags down. That is what reproduces his Aug-2024 read: spreads tight
(price hot) but credit expansion modest (quantity cold) => not a bubble.
"""
from __future__ import annotations

import math
from typing import Callable, Optional

import pandas as pd

from rates_macro.fred_client import VULNERABILITY_INPUTS, fetch_series

MIN_HISTORY = 20
QUANTITY_LOOKBACK_QUARTERS = 12  # trailing 3y change in credit-to-GDP
DEFAULT_WEIGHTS = {"quantity": 1.0, "asset": 1.0, "price": 1.0}
_EPS = 1e-6

PRICE_SERIES = "BAA10Y"
CREDIT_TO_GDP_SERIES = "QUSPAM770A"
EQUITIES_SERIES = "NCBEILQ027S"
GDP_SERIES = "GDP"

# NCBEILQ027S is in $millions, GDP in $billions, so their raw ratio is 1000x
# the true market-cap-to-GDP. Froth is a PERCENTILE, which is scale-invariant,
# so scoring is unaffected — this only rescales the DISPLAYED latest into the
# ~1-3 range a reader expects from a Buffett-indicator ratio instead of a
# ~1000x number that looks like a data bug.
ASSET_DISPLAY_SCALE = 0.001


def percentile_rank(series: pd.Series, value: Optional[float] = None) -> Optional[float]:
    """Percentile (0-100) of `value` (latest observation if None) within the
    series' own history: the share of observations strictly below it.

    Returns None below MIN_HISTORY observations, or when the series has no
    variance (a flat series has no meaningful percentile — treating the latest
    as its 0th or 100th percentile would fabricate a signal that isn't there).
    """
    clean = pd.Series(series).dropna().astype(float)
    if len(clean) < MIN_HISTORY:
        return None
    if clean.nunique() < 2:
        return None
    v = float(clean.iloc[-1]) if value is None else float(value)
    return float((clean < v).mean() * 100)


def spread_compression_froth(spread_series: pd.Series) -> Optional[float]:
    """Froth from a credit spread: a TIGHT (low-percentile) spread is frothy,
    so froth = 100 - percentile. None if history is insufficient."""
    p = percentile_rank(spread_series)
    return None if p is None else 100.0 - p


def level_elevation_froth(level_series: pd.Series) -> Optional[float]:
    """Froth from a level/change series: a HIGH (high-percentile) reading is
    frothy, so froth = percentile. None if history is insufficient."""
    return percentile_rank(level_series)


def credit_to_gdp_change(
    credit_to_gdp: pd.Series, periods: int = QUANTITY_LOOKBACK_QUARTERS
) -> pd.Series:
    """Trailing `periods`-quarter change in a credit-to-GDP series — Greenwood's
    'is credit expanding faster than the economy' measure (the change, not the
    level).

    Calendar-aware: the series is snapped to quarter periods and reindexed onto
    a gap-free quarterly grid before differencing, so `periods` means QUARTERS,
    not rows. A missing/revised quarter therefore can't silently widen the
    trailing window (the same 'align before differencing' discipline
    cross_reference.py applies to correlation).
    """
    s = pd.Series(credit_to_gdp).dropna().astype(float)
    if s.empty:
        return s
    s = pd.Series(s.to_numpy(), index=pd.PeriodIndex(s.index, freq="Q"))
    s = s[~s.index.duplicated(keep="last")].sort_index()
    s = s.reindex(pd.period_range(s.index.min(), s.index.max(), freq="Q"))
    change = s.diff(periods).dropna()
    change.index = change.index.to_timestamp()
    return change


def market_cap_to_gdp(equities: pd.Series, gdp: pd.Series) -> pd.Series:
    """Market-cap-to-GDP ratio, aligning the two series on shared dates first.

    The ratio's absolute scale is meaningless (equities and GDP are in
    different units) but its PERCENTILE is scale-invariant, which is all the
    froth leg needs.
    """
    joint = pd.concat(
        [pd.Series(equities).rename("e"), pd.Series(gdp).rename("g")],
        axis=1,
        join="inner",
    ).dropna()
    joint = joint[joint["g"] != 0]
    return joint["e"] / joint["g"]


def geometric_conjunction(legs: dict, weights: dict) -> Optional[float]:
    """Weighted geometric mean of froth legs (each 0-100). Conjunctive: any
    single cold leg drags the whole score toward zero, so the Red-Zone only
    lights up when froth is broad-based — not when one hot leg averages out a
    cold one.

    Returns None (not 0.0) when no leg carries positive weight — a score with
    zero contributing legs does not exist, and a fabricated 0.0 would read as
    'no froth' and flow into the regime as a real contained-vulnerability
    input.
    """
    num = 0.0
    den = 0.0
    for name, value in legs.items():
        w = weights.get(name, 0.0)
        if w <= 0:
            continue
        num += w * math.log(max(value, _EPS))
        den += w
    return math.exp(num / den) if den > 0 else None


def _leg_detail(
    label: str, series: pd.Series, froth: float, kind: str, display_scale: float = 1.0
) -> dict:
    clean = pd.Series(series).dropna()
    return {
        "label": label,
        "froth": round(froth, 1),
        "kind": kind,  # 'compression' | 'elevation'
        "latest": round(float(clean.iloc[-1]) * display_scale, 4) if not clean.empty else None,
        "observations": int(len(clean)),
        "history_start": str(clean.index[0].date()) if not clean.empty else None,
        "as_of": str(clean.index[-1].date()) if not clean.empty else None,
    }


def _insufficient_reason(series: pd.Series) -> str:
    """Distinguish the two causes percentile_rank returns None for, so an
    excluded leg's reason is actionable."""
    clean = pd.Series(series).dropna().astype(float)
    if len(clean) < MIN_HISTORY:
        return f"insufficient history ({len(clean)} < {MIN_HISTORY} obs)"
    if clean.nunique() < 2:
        return "no variance (flat series)"
    return "insufficient history or no variance"


def build_red_zone(
    fetch: Callable[[str], pd.Series] = fetch_series,
    weights: Optional[dict] = None,
) -> dict:
    """Assemble the three froth legs from FRED and combine them into the
    Red-Zone score. `fetch` is injectable for testing. Each leg degrades to an
    `excluded` entry (never crashes the score) if its fetch fails or its
    history is too short."""
    weights = weights or DEFAULT_WEIGHTS
    legs: dict[str, dict] = {}
    excluded: list[dict] = []

    def _add_leg(
        name: str,
        label: str,
        series: pd.Series,
        froth: Optional[float],
        kind: str,
        display_scale: float = 1.0,
    ):
        if froth is None:
            excluded.append({"leg": name, "reason": _insufficient_reason(series)})
        else:
            legs[name] = _leg_detail(label, series, froth, kind, display_scale)

    # --- price-of-credit froth: spread compression ---
    try:
        spread = fetch(PRICE_SERIES)
        _add_leg(
            "price",
            VULNERABILITY_INPUTS[PRICE_SERIES],
            spread,
            spread_compression_froth(spread),
            "compression",
        )
    except Exception as e:  # noqa: BLE001 — per-leg isolation
        excluded.append({"leg": "price", "reason": str(e)})

    # --- quantity froth: credit-to-GDP expansion ---
    try:
        credit = fetch(CREDIT_TO_GDP_SERIES)
        change = credit_to_gdp_change(credit)
        _add_leg(
            "quantity",
            f"{VULNERABILITY_INPUTS[CREDIT_TO_GDP_SERIES]} — trailing "
            f"{QUANTITY_LOOKBACK_QUARTERS}q change",
            change,
            level_elevation_froth(change),
            "elevation",
        )
    except Exception as e:  # noqa: BLE001 — per-leg isolation
        excluded.append({"leg": "quantity", "reason": str(e)})

    # --- asset froth: market-cap-to-GDP elevation ---
    try:
        equities = fetch(EQUITIES_SERIES)
        gdp = fetch(GDP_SERIES)
        ratio = market_cap_to_gdp(equities, gdp)
        _add_leg(
            "asset",
            "Market-cap-to-GDP (nonfinancial corp equities / GDP)",
            ratio,
            level_elevation_froth(ratio),
            "elevation",
            display_scale=ASSET_DISPLAY_SCALE,
        )
    except Exception as e:  # noqa: BLE001 — per-leg isolation
        excluded.append({"leg": "asset", "reason": str(e)})

    froth_by_leg = {name: leg["froth"] for name, leg in legs.items()}
    raw_score = geometric_conjunction(froth_by_leg, weights) if froth_by_leg else None
    score = round(raw_score, 1) if raw_score is not None else None

    return {
        "score": score,
        "legs": legs,
        "excluded": excluded,
        "weights": {k: weights.get(k, 0.0) for k in ("quantity", "asset", "price")},
    }


def render_red_zone(result: dict) -> str:
    """Plain-text Red-Zone score with per-leg froth attribution."""
    score = result["score"]
    header = (
        f"Vulnerability / Red-Zone score: {score}/100"
        if score is not None
        else "Vulnerability / Red-Zone score: n/a (no legs available)"
    )
    lines = [
        header,
        "  (higher = more froth/fragility; a crisis needs all legs hot at once)",
        "",
    ]
    order = ["quantity", "asset", "price"]
    for name in order:
        leg = result["legs"].get(name)
        if leg is None:
            continue
        lines.append(
            f"  {name:9} froth {leg['froth']:>5.1f}  "
            f"(latest {leg['latest']}, {leg['observations']} obs since "
            f"{leg['history_start']}) — {leg['label']}"
        )
    if result["excluded"]:
        lines.append("")
        lines.append("  Excluded legs:")
        for e in result["excluded"]:
            lines.append(f"    {e['leg']}: {e['reason']}")
    return "\n".join(lines)
