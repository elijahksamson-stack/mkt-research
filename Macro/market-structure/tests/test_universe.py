import pytest

from market_structure.universe import (
    BROAD_INDEXES,
    SECTOR_ETFS,
    composite_weights,
    default_universe,
)


class TestDefaultUniverse:
    def test_includes_all_broad_indexes_and_sectors(self):
        universe = default_universe()
        assert set(BROAD_INDEXES) <= set(universe)
        assert set(SECTOR_ETFS) <= set(universe)

    def test_no_ticker_overlap_between_tiers(self):
        assert set(BROAD_INDEXES).isdisjoint(set(SECTOR_ETFS))


class TestCompositeWeights:
    def test_weights_sum_to_one_for_default_universe(self):
        weights = composite_weights()
        assert sum(weights.values()) == pytest.approx(1.0)

    def test_broad_indexes_split_seventy_percent_evenly(self):
        weights = composite_weights()
        per_index = 0.70 / len(BROAD_INDEXES)
        for ticker in BROAD_INDEXES:
            assert weights[ticker] == pytest.approx(per_index)

    def test_sector_etfs_split_thirty_percent_evenly(self):
        weights = composite_weights()
        per_sector = 0.30 / len(SECTOR_ETFS)
        for ticker in SECTOR_ETFS:
            assert weights[ticker] == pytest.approx(per_sector)

    def test_trimmed_universe_still_sums_to_one(self):
        trimmed = {"SPY": "S&P 500", "QQQ": "Nasdaq 100", "XLK": "Technology"}
        weights = composite_weights(trimmed)
        assert sum(weights.values()) == pytest.approx(1.0)
        assert weights["SPY"] == weights["QQQ"]  # even split within broad tier

    def test_custom_tickers_outside_known_tiers_still_sum_to_one(self):
        custom = {"ARKK": "ARK Innovation"}
        weights = composite_weights(custom)
        assert sum(weights.values()) == pytest.approx(1.0)
