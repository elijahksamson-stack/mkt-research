from equity_rotation.universe import (
    BENCHMARK,
    FACTOR_ETFS,
    SECTOR_ETFS,
    default_universe,
    tier_of,
)


class TestDefaultUniverse:
    def test_includes_all_sectors_and_factors(self):
        universe = default_universe()
        assert set(SECTOR_ETFS) <= set(universe)
        assert set(FACTOR_ETFS) <= set(universe)

    def test_no_ticker_overlap_between_tiers(self):
        assert set(SECTOR_ETFS).isdisjoint(set(FACTOR_ETFS))

    def test_benchmark_not_in_either_tier(self):
        assert BENCHMARK not in SECTOR_ETFS
        assert BENCHMARK not in FACTOR_ETFS

    def test_eleven_sector_etfs(self):
        assert len(SECTOR_ETFS) == 11

    def test_six_factor_etfs(self):
        assert len(FACTOR_ETFS) == 6


class TestTierOf:
    def test_sector_ticker(self):
        assert tier_of("XLK") == "sector"

    def test_factor_ticker(self):
        assert tier_of("MTUM") == "factor"

    def test_unknown_ticker(self):
        assert tier_of("ARKK") == "other"
