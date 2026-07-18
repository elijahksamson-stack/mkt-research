from datetime import date

from commodities.contracts import next_contract_months
from commodities.universe import CANONICAL_PAIRS, by_family, default_universe, tradable_futures


class TestDefaultUniverse:
    def test_every_instrument_has_a_unique_canonical_id(self):
        universe = default_universe()
        ids = [inst.canonical_id for inst in universe.values()]

        assert len(ids) == len(set(ids))

    def test_every_family_is_one_of_the_five_spec_families(self):
        universe = default_universe()
        allowed = {"energy", "precious_metals", "industrial_metals", "agriculture", "livestock"}

        assert all(inst.family in allowed for inst in universe.values())

    def test_tradable_futures_excludes_the_uranium_etf_proxy(self):
        futures = tradable_futures()

        assert "uranium" not in futures
        assert futures["gold"].is_tradable_future is True

    def test_by_family_returns_only_matching_members(self):
        metals = by_family("precious_metals")

        assert set(metals) == {"gold", "silver", "platinum", "palladium"}


class TestCanonicalPairs:
    def test_every_pair_leg_is_a_real_universe_member(self):
        universe = default_universe()

        for numerator_id, denominator_id in CANONICAL_PAIRS:
            assert numerator_id in universe
            assert denominator_id in universe


class TestContractMonthCycle:
    def test_every_tradable_instrument_yields_three_chronological_months(self):
        universe = tradable_futures()
        as_of = date(2026, 7, 18)

        for inst in universe.values():
            months = next_contract_months(inst, as_of, count=3)

            assert len(months) == 3
            year_month = [(m.year, m.month) for m in months]
            assert year_month == sorted(year_month)

    def test_selected_months_never_include_the_current_calendar_month(self):
        universe = tradable_futures()
        as_of = date(2026, 7, 18)

        for inst in universe.values():
            months = next_contract_months(inst, as_of, count=1)

            assert (months[0].year, months[0].month) != (as_of.year, as_of.month)
