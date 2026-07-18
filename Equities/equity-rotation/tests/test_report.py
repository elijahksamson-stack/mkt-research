import numpy as np
import pandas as pd
import pytest

from equity_rotation import report
from equity_rotation.market_data import FetchResult, QualityMetrics
from equity_rotation.universe import BENCHMARK, FACTOR_ETFS, SECTOR_ETFS


def _price_series(n, drift, noise, seed):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2023-01-01", periods=n, freq="B")
    log_returns = drift + rng.normal(0, noise, n)
    prices = 100 * np.exp(np.cumsum(log_returns))
    return pd.Series(prices, index=dates)


def _fake_fetch_result(n=300):
    closes = {}
    quality = {}
    seed = 0
    tickers = list(SECTOR_ETFS)[:4] + list(FACTOR_ETFS)[:3] + [BENCHMARK]
    for ticker in tickers:
        seed += 1
        drift = 0.001 if seed % 2 == 0 else -0.0005
        closes[ticker] = _price_series(n, drift=drift, noise=0.01, seed=seed)
        quality[ticker] = QualityMetrics(
            bars=n, coverage=1.0, median_dollar_volume=5_000_000.0, latest=closes[ticker].index[-1]
        )
    as_of = pd.Timestamp(closes[BENCHMARK].index[-1])
    return FetchResult(closes=closes, quality=quality, dropped=[], as_of=as_of)


def _test_universe():
    universe = {t: SECTOR_ETFS[t] for t in list(SECTOR_ETFS)[:4]}
    universe.update({t: FACTOR_ETFS[t] for t in list(FACTOR_ETFS)[:3]})
    return universe


class TestBuildReport:
    def test_returns_sector_and_factor_tables(self, monkeypatch):
        fake = _fake_fetch_result()
        monkeypatch.setattr(report, "fetch_universe", lambda targets, period: fake)
        result = report.build_report(universe=_test_universe())
        assert result["sector_table"] is not None
        assert result["factor_table"] is not None
        assert len(result["technicals"]) == 7

    def test_raises_when_benchmark_missing(self, monkeypatch):
        fake = _fake_fetch_result()
        closes_without_benchmark = {t: s for t, s in fake.closes.items() if t != BENCHMARK}
        broken = FetchResult(
            closes=closes_without_benchmark,
            quality=fake.quality,
            dropped=[{"ticker": BENCHMARK, "name": "Benchmark", "reason": "boom"}],
            as_of=fake.as_of,
        )
        monkeypatch.setattr(report, "fetch_universe", lambda targets, period: broken)
        with pytest.raises(RuntimeError, match="Benchmark"):
            report.build_report()

    def test_isolates_relative_technicals_failure_without_dropping_from_ranking(self, monkeypatch):
        fake = _fake_fetch_result()
        short_ticker = list(SECTOR_ETFS)[0]
        # Below relative_technicals.MIN_BARS but still enough for several
        # trend_regression windows -- isolates the technicals failure
        # without necessarily removing the ticker from rotation ranking.
        fake.closes[short_ticker] = fake.closes[short_ticker].iloc[-50:]
        monkeypatch.setattr(report, "fetch_universe", lambda targets, period: fake)
        result = report.build_report(universe=_test_universe())
        assert any(d["ticker"] == short_ticker for d in result["dropped"])
        assert len(result["technicals"]) == 6

    def test_dropped_from_fetch_is_carried_through(self, monkeypatch):
        fake = _fake_fetch_result()
        fake_with_drop = FetchResult(
            closes=fake.closes,
            quality=fake.quality,
            dropped=[{"ticker": "ZZZ", "name": "Bad", "reason": "boom"}],
            as_of=fake.as_of,
        )
        monkeypatch.setattr(report, "fetch_universe", lambda targets, period: fake_with_drop)
        result = report.build_report(universe=_test_universe())
        assert any(d["ticker"] == "ZZZ" for d in result["dropped"])


class TestRenderSummary:
    def test_produces_text_with_all_sections(self, monkeypatch):
        fake = _fake_fetch_result()
        monkeypatch.setattr(report, "fetch_universe", lambda targets, period: fake)
        result = report.build_report(universe=_test_universe())
        text = report.render_summary(result)
        assert "SECTOR ROTATION RANKING" in text
        assert "FACTOR ROTATION RANKING" in text
        assert "RELATIVE TECHNICALS" in text
        assert str(result["as_of"].date()) in text

    def test_notes_missing_tier_when_not_enough_tickers(self, monkeypatch):
        fake = _fake_fetch_result()
        universe = {list(SECTOR_ETFS)[0]: SECTOR_ETFS[list(SECTOR_ETFS)[0]]}  # only 1 sector ticker
        universe.update({t: FACTOR_ETFS[t] for t in list(FACTOR_ETFS)[:3]})
        monkeypatch.setattr(report, "fetch_universe", lambda targets, period: fake)
        result = report.build_report(universe=universe)
        text = report.render_summary(result)
        assert "not enough sectors" in text
