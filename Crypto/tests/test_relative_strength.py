import numpy as np
import pandas as pd
import pytest

from crypto_structure.relative_strength import aligned_ratio, pareto_dominated_by, rank_universe


def _synthetic_close(n, drift, noise_scale=0.01, seed=42, start="2024-01-01"):
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, noise_scale, n)
    log_vals = drift * np.arange(n) + noise
    dates = pd.date_range(start, periods=n, freq="D")
    return pd.Series(100 * np.exp(log_vals), index=dates)


class TestAlignedRatio:
    def test_ratio_matches_manual_division_on_overlap(self):
        a = pd.Series([10.0, 20.0, 30.0], index=pd.date_range("2024-01-01", periods=3))
        b = pd.Series([2.0, 4.0, 5.0], index=pd.date_range("2024-01-01", periods=3))
        ratio = aligned_ratio(a, b)
        assert list(ratio) == pytest.approx([5.0, 5.0, 6.0])

    def test_drops_non_overlapping_dates(self):
        a = pd.Series([10.0, 20.0], index=pd.date_range("2024-01-01", periods=2))
        b = pd.Series([5.0], index=pd.date_range("2024-01-01", periods=1))
        ratio = aligned_ratio(a, b)
        assert len(ratio) == 1

    def test_drops_non_positive_values(self):
        a = pd.Series([10.0, -5.0, 20.0], index=pd.date_range("2024-01-01", periods=3))
        b = pd.Series([2.0, 4.0, 5.0], index=pd.date_range("2024-01-01", periods=3))
        ratio = aligned_ratio(a, b)
        assert len(ratio) == 2


class TestParetoDominatedBy:
    def test_undominated_row_has_zero_count(self):
        table = pd.DataFrame({"Leadership": [90.0, 50.0], "Opportunity": [90.0, 50.0]})
        counts = pareto_dominated_by(table)
        assert counts[0] == 0
        assert counts[1] == 1

    def test_equal_rows_do_not_dominate_each_other(self):
        table = pd.DataFrame({"Leadership": [70.0, 70.0], "Opportunity": [60.0, 60.0]})
        assert pareto_dominated_by(table) == [0, 0]

    def test_dominance_requires_at_least_one_strict_improvement(self):
        table = pd.DataFrame({"Leadership": [80.0, 80.0, 60.0], "Opportunity": [90.0, 70.0, 60.0]})
        counts = pareto_dominated_by(table)
        assert counts[0] == 0  # nothing beats row 0 on both axes
        assert counts[1] == 1  # row 0 dominates row 1 (same leadership, higher opportunity)
        assert counts[2] == 2  # rows 0 and 1 both dominate row 2


class TestRankUniverse:
    def test_raises_with_fewer_than_two_tickers(self):
        closes = {"BTC-USD": _synthetic_close(400, drift=0.001)}
        with pytest.raises(ValueError):
            rank_universe(closes, {"BTC-USD": "Bitcoin"})

    def test_leading_asset_ranks_above_lagging_asset(self):
        closes = {
            "BTC-USD": _synthetic_close(400, drift=0.0005, seed=1),
            "WINNER-USD": _synthetic_close(400, drift=0.004, seed=2),
            "LOSER-USD": _synthetic_close(400, drift=-0.003, seed=3),
        }
        labels = {"BTC-USD": "Bitcoin", "WINNER-USD": "Winner", "LOSER-USD": "Loser"}
        ranked, pair_signals = rank_universe(closes, labels, benchmark_ticker="BTC-USD")
        assert ranked.loc["WINNER-USD", "Rank"] < ranked.loc["LOSER-USD", "Rank"]
        assert ranked.loc["WINNER-USD", "Leadership"] > ranked.loc["LOSER-USD", "Leadership"]

    def test_output_columns_and_index(self):
        closes = {
            "BTC-USD": _synthetic_close(400, drift=0.001, seed=1),
            "ETH-USD": _synthetic_close(400, drift=0.002, seed=2),
        }
        labels = {"BTC-USD": "Bitcoin", "ETH-USD": "Ethereum"}
        ranked, pair_signals = rank_universe(closes, labels, benchmark_ticker="BTC-USD")
        for col in ("Rank", "Name", "Leadership", "Opportunity", "Joint", "ParetoDominatedBy"):
            assert col in ranked.columns
        assert set(ranked.index) == {"BTC-USD", "ETH-USD"}
        assert set(pair_signals.index) == {"BTC-USD", "ETH-USD"}

    def test_benchmark_ranked_against_itself_does_not_crash(self):
        # BTC-USD is both a universe member and the benchmark -- the
        # self-ratio is degenerate and must be handled, not raise.
        closes = {
            "BTC-USD": _synthetic_close(400, drift=0.001, seed=1),
            "ETH-USD": _synthetic_close(400, drift=0.0015, seed=2),
        }
        labels = {"BTC-USD": "Bitcoin", "ETH-USD": "Ethereum"}
        ranked, _ = rank_universe(closes, labels, benchmark_ticker="BTC-USD")
        assert ranked.loc["BTC-USD", "BenchmarkLeadership"] == pytest.approx(50.0)

    def test_works_without_a_benchmark_ticker(self):
        closes = {
            "BTC-USD": _synthetic_close(400, drift=0.001, seed=1),
            "ETH-USD": _synthetic_close(400, drift=0.0015, seed=2),
        }
        labels = {"BTC-USD": "Bitcoin", "ETH-USD": "Ethereum"}
        ranked, _ = rank_universe(closes, labels, benchmark_ticker=None)
        assert (ranked["BenchmarkLeadership"] == 50.0).all()

    def test_rank_column_is_contiguous_starting_at_one(self):
        closes = {
            "A-USD": _synthetic_close(400, drift=0.001, seed=1),
            "B-USD": _synthetic_close(400, drift=0.002, seed=2),
            "C-USD": _synthetic_close(400, drift=-0.001, seed=3),
        }
        labels = {t: t for t in closes}
        ranked, _ = rank_universe(closes, labels)
        assert sorted(ranked["Rank"].tolist()) == [1, 2, 3]
