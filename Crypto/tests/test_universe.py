import pytest

from crypto_structure.universe import (
    ALTCOINS,
    BENCHMARK_TICKER,
    MAJORS,
    composite_weights,
    default_universe,
)


class TestDefaultUniverse:
    def test_includes_all_majors_and_altcoins(self):
        universe = default_universe()
        assert set(MAJORS) <= set(universe)
        assert set(ALTCOINS) <= set(universe)

    def test_no_ticker_overlap_between_tiers(self):
        assert set(MAJORS).isdisjoint(set(ALTCOINS))

    def test_benchmark_ticker_is_a_major(self):
        assert BENCHMARK_TICKER in MAJORS

    def test_all_tickers_use_yfinance_usd_pair_format(self):
        for ticker in default_universe():
            assert ticker.endswith("-USD")


class TestCompositeWeights:
    def test_weights_sum_to_one_for_default_universe(self):
        weights = composite_weights()
        assert sum(weights.values()) == pytest.approx(1.0)

    def test_majors_split_sixty_percent_evenly(self):
        weights = composite_weights()
        per_major = 0.60 / len(MAJORS)
        for ticker in MAJORS:
            assert weights[ticker] == pytest.approx(per_major)

    def test_altcoins_split_forty_percent_evenly(self):
        weights = composite_weights()
        per_alt = 0.40 / len(ALTCOINS)
        for ticker in ALTCOINS:
            assert weights[ticker] == pytest.approx(per_alt)

    def test_trimmed_universe_still_sums_to_one(self):
        trimmed = {"BTC-USD": "Bitcoin", "ETH-USD": "Ethereum", "SOL-USD": "Solana"}
        weights = composite_weights(trimmed)
        assert sum(weights.values()) == pytest.approx(1.0)
        assert weights["BTC-USD"] == weights["ETH-USD"]  # even split within majors tier

    def test_custom_tickers_outside_known_tiers_still_sum_to_one(self):
        custom = {"PEPE-USD": "Pepe"}
        weights = composite_weights(custom)
        assert sum(weights.values()) == pytest.approx(1.0)
