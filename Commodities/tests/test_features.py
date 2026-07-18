import numpy as np
import pandas as pd

from commodities.features import (
    UniverseData, build_feature_matrix, build_training_matrix,
)
from commodities.labels import build_label_panel
from commodities.market_data import CommoditySeries
from commodities.momentum import build_return_matrix
from commodities.universe import default_universe
from market_structure.market_data import OHLCV


def _synthetic_universe_data(n_bars: int = 360, n_commodities: int = 3, seed: int = 7) -> UniverseData:
    """Offline UniverseData: real CommodityInstrument entries (for valid
    family/symbol fields) paired with synthetic price series. No network:
    empty cot_history/macro_series, and callers pass include_curve=False."""
    rng = np.random.default_rng(seed)
    full = default_universe()
    cids = list(full.keys())[:n_commodities]
    universe = {cid: full[cid] for cid in cids}

    dates = pd.DatetimeIndex(pd.bdate_range("2022-01-03", periods=n_bars))
    commodity_series: dict[str, CommoditySeries] = {}
    raw_ohlcv: dict[str, OHLCV] = {}
    for cid in cids:
        steps = rng.normal(0.0002, 0.012, n_bars)
        close = 100.0 * np.exp(np.cumsum(steps))
        high = close * (1 + np.abs(rng.normal(0, 0.004, n_bars)))
        low = close * (1 - np.abs(rng.normal(0, 0.004, n_bars)))
        volume = rng.integers(1_000, 10_000, n_bars).astype(float)
        commodity_series[cid] = CommoditySeries(
            canonical_id=cid, continuous_symbol=universe[cid].continuous_symbol,
            dates=dates, raw_close=close, roll_adjusted_close=close, roll_events=(),
        )
        raw_ohlcv[cid] = OHLCV(
            ticker=universe[cid].continuous_symbol, dates=dates,
            high=high, low=low, close=close, volume=volume,
        )

    return UniverseData(
        universe=universe, commodity_series=commodity_series, raw_ohlcv=raw_ohlcv,
        return_matrix=build_return_matrix(commodity_series),
        cot_history={}, macro_series={},
    )


class TestBuildFeatureMatrix:
    def test_one_row_per_commodity_as_of_with_no_label_columns(self):
        # Arrange
        data = _synthetic_universe_data()
        label_panel = build_label_panel(data.commodity_series)

        # Act
        matrix = build_feature_matrix(data, label_panel, include_curve=False)

        # Assert: one row per (canonical_id, as_of), and no horizon/label columns
        assert not matrix.empty
        assert not matrix.duplicated(subset=["canonical_id", "as_of"]).any()
        for col in ("horizon_days", "forward_return", "forward_direction"):
            assert col not in matrix.columns
        assert {"canonical_id", "family", "as_of"}.issubset(matrix.columns)


class TestBuildTrainingMatrixEquivalence:
    def test_training_rows_carry_the_same_features_as_the_standalone_matrix(self):
        # Arrange
        data = _synthetic_universe_data()
        label_panel = build_label_panel(data.commodity_series)
        matrix = build_feature_matrix(data, label_panel, include_curve=False)

        # Act
        training = build_training_matrix(data, label_panel, include_curve=False)

        # Assert: label columns are present, and for every training row the
        # feature values equal the standalone matrix's row for that (cid, as_of).
        for col in ("horizon_days", "forward_return", "forward_direction"):
            assert col in training.columns

        feature_cols = [c for c in matrix.columns if c not in ("canonical_id", "as_of", "family")]
        key = ["canonical_id", "as_of"]
        m_indexed = matrix.set_index(key)[feature_cols].sort_index()
        # Collapse training back to one row per key (features are horizon-invariant) and compare.
        t_indexed = (
            training.drop_duplicates(subset=key).set_index(key)[feature_cols].sort_index()
        )
        assert list(t_indexed.index) == list(m_indexed.index)
        pd.testing.assert_frame_equal(
            t_indexed.reset_index(drop=True), m_indexed.reset_index(drop=True),
            check_dtype=False,
        )

    def test_row_count_matches_labels_that_have_a_feature_row(self):
        # Arrange
        data = _synthetic_universe_data()
        label_panel = build_label_panel(data.commodity_series)
        matrix = build_feature_matrix(data, label_panel, include_curve=False)

        # Act
        training = build_training_matrix(data, label_panel, include_curve=False)

        # Assert: inner join semantics -- one training row per label row whose
        # (canonical_id, as_of) produced a feature row.
        have_features = set(map(tuple, matrix[["canonical_id", "as_of"]].to_numpy()))
        expected = sum(
            1 for _, r in label_panel.iterrows()
            if (r["canonical_id"], pd.Timestamp(r["as_of"])) in have_features
        )
        assert len(training) == expected


class TestBuildRankingsUsesSingleFeatureCompute:
    def test_build_rankings_returns_rankings_for_the_universe(self):
        # Arrange
        from commodities.ranking import build_rankings
        data = _synthetic_universe_data()

        # Act
        run = build_rankings(data)

        # Assert: a ranking per commodity that produced a live bundle, sorted by score.
        assert run.rankings, "expected at least one ranking"
        scores = [r.commodity_opportunity_score for r in run.rankings]
        assert scores == sorted(scores, reverse=True)
        assert set(r.canonical_id for r in run.rankings).issubset(set(data.universe))
