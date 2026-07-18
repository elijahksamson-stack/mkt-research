import numpy as np
import pandas as pd
import pytest

from equity_rotation.rotation_ranking import RotationRank, RotationTable, rank_universe


def _price_series(n, drift, noise, seed):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2023-01-01", periods=n, freq="B")
    log_returns = drift + rng.normal(0, noise, n)
    prices = 100 * np.exp(np.cumsum(log_returns))
    return pd.Series(prices, index=dates)


@pytest.fixture
def universe_closes():
    # LEAD: strong steady uptrend. LAG: strong steady downtrend.
    # MID_A/MID_B: flat/noisy, indistinguishable from each other.
    return {
        "LEAD": _price_series(300, drift=0.0030, noise=0.004, seed=1),
        "MID_A": _price_series(300, drift=0.0002, noise=0.006, seed=2),
        "MID_B": _price_series(300, drift=0.0001, noise=0.006, seed=3),
        "LAG": _price_series(300, drift=-0.0030, noise=0.004, seed=4),
    }


@pytest.fixture
def labels():
    return {"LEAD": "Leader", "MID_A": "Mid A", "MID_B": "Mid B", "LAG": "Laggard"}


@pytest.fixture
def benchmark_close():
    return _price_series(300, drift=0.0005, noise=0.005, seed=99)


class TestRankUniverse:
    def test_raises_with_fewer_than_two_tickers(self, universe_closes, labels):
        with pytest.raises(ValueError):
            rank_universe({"LEAD": universe_closes["LEAD"]}, labels)

    def test_returns_one_rank_per_ticker(self, universe_closes, labels, benchmark_close):
        table = rank_universe(universe_closes, labels, benchmark_close)
        assert isinstance(table, RotationTable)
        assert len(table.ranks) == len(universe_closes)
        assert {r.ticker for r in table.ranks} == set(universe_closes)

    def test_ranks_are_1_indexed_and_contiguous(self, universe_closes, labels, benchmark_close):
        table = rank_universe(universe_closes, labels, benchmark_close)
        assert [r.rank for r in table.ranks] == list(range(1, len(universe_closes) + 1))

    def test_sorted_by_joint_descending(self, universe_closes, labels, benchmark_close):
        table = rank_universe(universe_closes, labels, benchmark_close)
        joints = [r.joint for r in table.ranks]
        assert joints == sorted(joints, reverse=True)

    def test_strong_leader_ranks_first(self, universe_closes, labels, benchmark_close):
        table = rank_universe(universe_closes, labels, benchmark_close)
        assert table.ranks[0].ticker == "LEAD"

    def test_strong_laggard_ranks_last(self, universe_closes, labels, benchmark_close):
        table = rank_universe(universe_closes, labels, benchmark_close)
        assert table.ranks[-1].ticker == "LAG"

    def test_leader_is_pareto_undominated(self, universe_closes, labels, benchmark_close):
        table = rank_universe(universe_closes, labels, benchmark_close)
        leader = next(r for r in table.ranks if r.ticker == "LEAD")
        assert leader.pareto_dominated_by == 0

    def test_leadership_and_opportunity_bounded(self, universe_closes, labels, benchmark_close):
        table = rank_universe(universe_closes, labels, benchmark_close)
        for r in table.ranks:
            assert 0.0 <= r.leadership <= 100.0
            assert 0.0 <= r.opportunity <= 100.0

    def test_works_without_benchmark(self, universe_closes, labels):
        table = rank_universe(universe_closes, labels, benchmark_close=None)
        assert len(table.ranks) == len(universe_closes)
        leader = next(r for r in table.ranks if r.ticker == "LEAD")
        assert leader.benchmark_leadership == 50.0

    def test_pair_signals_has_no_self_comparison(self, universe_closes, labels, benchmark_close):
        table = rank_universe(universe_closes, labels, benchmark_close)
        for ticker, others in table.pair_signals.items():
            assert ticker not in others
            assert set(others) == set(universe_closes) - {ticker}

    def test_names_pulled_from_labels(self, universe_closes, labels, benchmark_close):
        table = rank_universe(universe_closes, labels, benchmark_close)
        leader = next(r for r in table.ranks if r.ticker == "LEAD")
        assert leader.name == "Leader"
