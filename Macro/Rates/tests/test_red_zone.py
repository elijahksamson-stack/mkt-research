import numpy as np
import pandas as pd
import pytest

from rates_macro import red_zone as rz
from rates_macro.red_zone import (
    build_red_zone,
    credit_to_gdp_change,
    geometric_conjunction,
    level_elevation_froth,
    market_cap_to_gdp,
    percentile_rank,
    render_red_zone,
    spread_compression_froth,
)


def _quarterly(values, start="1990-01-01"):
    idx = pd.date_range(start, periods=len(values), freq="QS")
    return pd.Series(values, index=idx, dtype=float)


def _daily(values, start="1990-01-01"):
    idx = pd.date_range(start, periods=len(values), freq="D")
    return pd.Series(values, index=idx, dtype=float)


class TestPercentileRank:
    def test_returns_none_below_min_history(self):
        assert percentile_rank(pd.Series([1.0, 2.0, 3.0])) is None

    def test_latest_at_top_of_history_is_high_percentile(self):
        s = pd.Series(list(range(100)), dtype=float)  # latest = 99, the max
        assert percentile_rank(s) == pytest.approx(99.0)

    def test_latest_at_bottom_of_history_is_low_percentile(self):
        s = pd.Series(list(range(99, -1, -1)), dtype=float)  # latest = 0, the min
        assert percentile_rank(s) == pytest.approx(0.0)

    def test_latest_at_median_is_mid_percentile(self):
        s = pd.Series([50.0] + list(range(100)), dtype=float)
        # explicit value in the middle of the 0..99 support
        assert percentile_rank(s, value=50.0) == pytest.approx(50.0, abs=1.0)


class TestFrothTransforms:
    def test_spread_compression_inverts_percentile(self):
        # a tight (low) latest spread sits at a low percentile -> HIGH froth
        s = pd.Series(list(range(99, -1, -1)), dtype=float)  # latest 0 = tightest ever
        assert spread_compression_froth(s) == pytest.approx(100.0)

    def test_wide_spread_is_low_froth(self):
        s = pd.Series(list(range(100)), dtype=float)  # latest 99 = widest ever
        assert spread_compression_froth(s) == pytest.approx(1.0, abs=1.0)

    def test_level_elevation_is_the_percentile_itself(self):
        s = pd.Series(list(range(100)), dtype=float)  # latest 99 = highest ever
        assert level_elevation_froth(s) == pytest.approx(99.0)

    def test_froth_none_when_insufficient_history(self):
        assert spread_compression_froth(pd.Series([1.0, 2.0])) is None
        assert level_elevation_froth(pd.Series([1.0, 2.0])) is None


class TestDerivedSeries:
    def test_credit_to_gdp_change_is_trailing_diff(self):
        cg = _quarterly([100, 101, 102, 104, 108])  # already %-of-GDP
        change = credit_to_gdp_change(cg, periods=2)
        # index 2: 102-100=2, index 3: 104-101=3, index 4: 108-102=6
        assert list(change.values) == pytest.approx([2.0, 3.0, 6.0])

    def test_market_cap_to_gdp_aligns_then_divides(self):
        equities = _quarterly([200, 220, 240])  # millions
        gdp = _quarterly([100, 110, 120])  # billions — unit mismatch is fine
        ratio = market_cap_to_gdp(equities, gdp)
        assert list(ratio.values) == pytest.approx([2.0, 2.0, 2.0])

    def test_market_cap_to_gdp_inner_joins_mismatched_calendars(self):
        equities = pd.Series([200.0, 220.0], index=pd.to_datetime(["2020-01-01", "2020-04-01"]))
        gdp = pd.Series([100.0, 110.0, 120.0], index=pd.to_datetime(
            ["2020-01-01", "2020-04-01", "2020-07-01"]))
        ratio = market_cap_to_gdp(equities, gdp)
        assert len(ratio) == 2

    def test_credit_to_gdp_change_is_calendar_aware_across_a_gap(self):
        # A missing quarter must NOT widen the trailing-change window: the
        # change must span `periods` real QUARTERS, not `periods` rows.
        idx = pd.date_range("2000-01-01", periods=20, freq="QS")
        level = pd.Series(range(20), index=idx, dtype=float)  # level == row number
        gapped = level.drop(idx[2])  # drop 2000-07-01
        change = credit_to_gdp_change(gapped, periods=4)
        # 2001-04-01 (level 5) minus 2000-04-01 (level 1) == 4, regardless of
        # the earlier dropped quarter. A positional diff(4) would give 5.
        assert change.loc[pd.Timestamp("2001-04-01")] == pytest.approx(4.0)


class TestGeometricConjunction:
    def test_equal_legs_return_that_value(self):
        assert geometric_conjunction({"a": 60, "b": 60, "c": 60}, {"a": 1, "b": 1, "c": 1}) == pytest.approx(60.0)

    def test_one_low_leg_drags_the_whole_score_down(self):
        # arithmetic mean would be (90+90+2)/3 ~= 60.7; geometric is far lower
        result = geometric_conjunction({"a": 90, "b": 90, "c": 2}, {"a": 1, "b": 1, "c": 1})
        assert result < 30

    def test_weights_tilt_the_result(self):
        legs = {"hot": 90, "cold": 10}
        hot_heavy = geometric_conjunction(legs, {"hot": 3, "cold": 1})
        cold_heavy = geometric_conjunction(legs, {"hot": 1, "cold": 3})
        assert hot_heavy > cold_heavy

    def test_ignores_zero_weight_legs(self):
        both = geometric_conjunction({"a": 80, "b": 20}, {"a": 1, "b": 1})
        only_a = geometric_conjunction({"a": 80, "b": 20}, {"a": 1, "b": 0})
        assert only_a == pytest.approx(80.0)
        assert both < only_a

    def test_all_zero_weight_returns_none_not_a_fabricated_zero(self):
        # No leg contributes any weight -> there is no score, which must be
        # None (not 0.0, which would read as "no froth" and flow into regime).
        assert geometric_conjunction({"a": 50, "b": 50}, {"a": 0, "b": 0}) is None


# Non-degenerate synthetic credit-to-GDP histories. Both must have genuine
# variance in their trailing CHANGE (a perfectly linear series has constant
# change -> a degenerate percentile input, the zero-variance trap).
def _credit_modest_expansion(n=120):
    # rises early (large positive change) then plateaus (latest change ~0 ->
    # low percentile of its own change history) -> LOW quantity froth today.
    rise = np.linspace(100.0, 180.0, n - 40)
    plateau = np.full(40, 180.0)
    return _quarterly(list(np.concatenate([rise, plateau])))


def _credit_accelerating(n=120):
    # convex: the most recent trailing change is the largest ever seen ->
    # HIGH percentile -> HIGH quantity froth today.
    return _quarterly(list(100.0 + 0.01 * np.arange(n) ** 2))


class TestBuildRedZone:
    def _fake_fetch(self, quantity_change_high=False, spreads_tight=True, assets_high=True):
        # Build synthetic histories so each leg's LATEST lands where we want.
        n = 120

        def fetch(series_id):
            if series_id == "BAA10Y":
                if spreads_tight:
                    # history 5..1 wide-to-tight, latest = tightest -> high froth
                    return _daily(list(np.linspace(5.0, 1.0, n)))
                return _daily(list(np.linspace(1.0, 5.0, n)))  # latest widest -> low froth
            if series_id == "QUSPAM770A":
                return (
                    _credit_accelerating(n)
                    if quantity_change_high
                    else _credit_modest_expansion(n)
                )
            if series_id == "NCBEILQ027S":
                if assets_high:
                    return _quarterly(list(np.linspace(100, 300, n)))  # latest highest
                return _quarterly(list(np.linspace(300, 100, n)))
            if series_id == "GDP":
                return _quarterly(list(100 + np.zeros(n)))  # flat GDP -> ratio tracks equities
            raise AssertionError(f"unexpected series {series_id}")

        return fetch

    def test_greenwood_pattern_low_quantity_drags_down_hot_price_and_assets(self):
        # THE validation case: price froth HIGH (spreads tight) + asset froth
        # HIGH, but quantity froth LOW (no credit expansion) -> the geometric
        # conjunction must be dragged DOWN, reproducing Greenwood's Aug-2024
        # "spreads are tight but it's not a bubble" conclusion.
        fetch = self._fake_fetch(quantity_change_high=False, spreads_tight=True, assets_high=True)
        result = build_red_zone(fetch=fetch)
        assert result["legs"]["price"]["froth"] > 70
        assert result["legs"]["asset"]["froth"] > 70
        assert result["legs"]["quantity"]["froth"] < 30
        assert result["score"] < 40  # dragged down despite two hot legs

    def test_all_three_legs_hot_produces_a_high_red_zone(self):
        fetch = self._fake_fetch(quantity_change_high=True, spreads_tight=True, assets_high=True)
        result = build_red_zone(fetch=fetch)
        assert result["score"] > 60

    def test_leg_with_insufficient_history_is_excluded_and_renormalized(self):
        def fetch(series_id):
            if series_id == "BAA10Y":
                return _daily([1.0, 2.0, 3.0])  # too short -> excluded
            if series_id == "QUSPAM770A":
                return _credit_accelerating(120)
            if series_id == "NCBEILQ027S":
                return _quarterly(list(np.linspace(100, 300, 120)))
            if series_id == "GDP":
                return _quarterly(list(100 + np.zeros(120)))
            raise AssertionError(series_id)

        result = build_red_zone(fetch=fetch)
        assert "price" in [e["leg"] for e in result["excluded"]]
        assert "price" not in result["legs"]
        assert result["score"] is not None  # still scores on the surviving two legs

    def test_a_failing_fetch_excludes_only_that_leg(self):
        def fetch(series_id):
            if series_id == "BAA10Y":
                raise RuntimeError("simulated FRED outage")
            if series_id == "QUSPAM770A":
                return _credit_accelerating(120)
            if series_id == "NCBEILQ027S":
                return _quarterly(list(np.linspace(100, 300, 120)))
            if series_id == "GDP":
                return _quarterly(list(100 + np.zeros(120)))
            raise AssertionError(series_id)

        result = build_red_zone(fetch=fetch)
        assert any(e["leg"] == "price" for e in result["excluded"])
        assert "quantity" in result["legs"]

    def test_custom_weights_are_respected(self):
        fetch = self._fake_fetch(quantity_change_high=False, spreads_tight=True, assets_high=True)
        default = build_red_zone(fetch=fetch)
        # down-weighting the cold quantity leg should lift the score
        quantity_light = build_red_zone(
            fetch=fetch, weights={"quantity": 0.1, "asset": 1.0, "price": 1.0}
        )
        assert quantity_light["score"] > default["score"]

    def test_score_is_none_when_all_surviving_legs_carry_zero_weight(self):
        # All weight is on price; price is excluded (fetch fails). The two
        # surviving legs carry zero weight -> the score must be None, NOT a
        # fabricated 0.0 that reads as "contained" and flows into regime().
        def fetch(series_id):
            if series_id == "BAA10Y":
                raise RuntimeError("simulated FRED outage")
            if series_id == "QUSPAM770A":
                return _credit_accelerating(120)
            if series_id == "NCBEILQ027S":
                return _quarterly(list(np.linspace(100, 300, 120)))
            if series_id == "GDP":
                return _quarterly(list(100 + np.zeros(120)))
            raise AssertionError(series_id)

        result = build_red_zone(
            fetch=fetch, weights={"price": 1.0, "quantity": 0.0, "asset": 0.0}
        )
        assert result["score"] is None

    def test_excluded_leg_reason_names_the_specific_cause(self):
        def fetch(series_id):
            if series_id == "BAA10Y":
                return _daily([1.0, 2.0, 3.0])  # too short -> insufficient history
            if series_id == "QUSPAM770A":
                return _credit_accelerating(120)
            if series_id == "NCBEILQ027S":
                return _quarterly(list(np.linspace(100, 300, 120)))
            if series_id == "GDP":
                return _quarterly(list(100 + np.zeros(120)))
            raise AssertionError(series_id)

        result = build_red_zone(fetch=fetch)
        price_excluded = [e for e in result["excluded"] if e["leg"] == "price"][0]
        assert "insufficient history" in price_excluded["reason"]

    def test_asset_leg_latest_is_unit_scaled_for_display(self):
        # NCBEILQ027S ($millions) / GDP ($billions) is 1000x the true
        # market-cap-to-GDP; the displayed latest must be rescaled so it reads
        # in the ~1-3 range, not as a ~1000x number that looks like a bug.
        fetch = self._fake_fetch()  # equities linspace(100,300), gdp flat 100
        result = build_red_zone(fetch=fetch)
        # raw ratio latest = 300/100 = 3.0; displayed = 3.0 * 0.001
        assert result["legs"]["asset"]["latest"] == pytest.approx(0.003)


class TestRenderRedZone:
    def test_renders_without_crashing(self):
        fetch = TestBuildRedZone()._fake_fetch()
        text = render_red_zone(build_red_zone(fetch=fetch))
        assert "Red-Zone" in text or "vulnerability" in text.lower()
        assert isinstance(text, str)
