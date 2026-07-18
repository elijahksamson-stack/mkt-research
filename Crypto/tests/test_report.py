import re

import numpy as np
import pandas as pd
import pytest

from crypto_structure import report
from crypto_structure.market_data import OHLCV

SMALL_UNIVERSE = {"BTC-USD": "Bitcoin", "ETH-USD": "Ethereum", "SOL-USD": "Solana"}


def _synthetic_ohlcv(ticker, n=400, seed=1, drift=0.05):
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(rng.normal(drift, 1.0, n))
    high = close + rng.uniform(0.2, 1.5, n)
    low = close - rng.uniform(0.2, 1.5, n)
    volume = rng.uniform(1_000_000, 5_000_000, n)
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    return OHLCV(ticker=ticker, dates=dates, high=high, low=low, close=close, volume=volume)


def _fake_download_universe(tickers, **kw):
    return {t: _synthetic_ohlcv(t, seed=hash(t) % 1000) for t in tickers}, []


class TestBuildReport:
    def test_builds_report_for_all_tickers_when_data_is_healthy(self, monkeypatch):
        monkeypatch.setattr(report, "download_universe", _fake_download_universe)
        result = report.build_report(universe=SMALL_UNIVERSE)
        assert set(result["reports"]) == set(SMALL_UNIVERSE)
        assert result["dropped"] == []
        assert result["gauge"].assets
        assert 0 <= result["gauge"].overall_risk_score <= 100
        assert 0 <= result["gauge"].risk_off_pct <= 100
        assert set(result["dates"]) == set(SMALL_UNIVERSE)
        assert set(result["leadership_table"].index) == set(SMALL_UNIVERSE)

    def test_isolates_a_failing_ticker_into_dropped(self, monkeypatch):
        def fake_download(tickers, **kw):
            ohlcv = {}
            for t in tickers:
                if t == "SOL-USD":
                    ohlcv[t] = _synthetic_ohlcv(t, n=30)  # below the 60-bar analyze() minimum
                else:
                    ohlcv[t] = _synthetic_ohlcv(t, seed=hash(t) % 1000)
            return ohlcv, []

        monkeypatch.setattr(report, "download_universe", fake_download)
        result = report.build_report(universe=SMALL_UNIVERSE)
        assert "SOL-USD" not in result["reports"]
        assert any(d["ticker"] == "SOL-USD" for d in result["dropped"])
        assert "BTC-USD" in result["reports"]

    def test_passes_through_download_dropped_tickers(self, monkeypatch):
        def fake_download(tickers, **kw):
            ohlcv = {t: _synthetic_ohlcv(t, seed=hash(t) % 1000) for t in tickers if t != "SOL-USD"}
            return ohlcv, [{"ticker": "SOL-USD", "reason": "no price data"}]

        monkeypatch.setattr(report, "download_universe", fake_download)
        result = report.build_report(universe=SMALL_UNIVERSE)
        assert any(d["ticker"] == "SOL-USD" for d in result["dropped"])

    def test_raises_when_fewer_than_two_tickers_survive(self, monkeypatch):
        monkeypatch.setattr(report, "download_universe", lambda tickers, **kw: ({}, []))
        with pytest.raises(RuntimeError):
            report.build_report(universe=SMALL_UNIVERSE)


class TestRenderSummary:
    def test_output_contains_gauge_headline_leadership_table_and_asset_rows(self, monkeypatch):
        monkeypatch.setattr(report, "download_universe", _fake_download_universe)
        result = report.build_report(universe=SMALL_UNIVERSE)
        text = report.render_summary(result)
        assert "OVERALL RISK SCORE" in text
        assert "RISK-OFF READ" in text
        assert "LEADERSHIP / OPPORTUNITY RANKING" in text
        assert "BTC-USD" in text
        assert "ETH-USD" in text
        assert "SOL-USD" in text

    def test_output_is_fully_quantitative_breakdown_not_narrative_only(self, monkeypatch):
        # Every score must be traceable to a printed number -- no term of
        # the formula is implicit.
        monkeypatch.setattr(report, "download_universe", _fake_download_universe)
        result = report.build_report(universe=SMALL_UNIVERSE)
        text = report.render_summary(result)
        assert "risk_score       = clip(" in text  # the formula legend itself
        assert "trend_component=" in text
        assert "rr_component=" in text
        assert "violation_penalty=" in text
        assert "support stack" in text
        assert "trendline (" in text

    def test_trendline_dates_are_resolved_from_ohlcv_dates_not_bar_indices(self, monkeypatch):
        monkeypatch.setattr(report, "download_universe", _fake_download_universe)
        result = report.build_report(universe={"BTC-USD": "Bitcoin", "ETH-USD": "Ethereum"})
        text = report.render_summary(result)
        tv = result["reports"]["BTC-USD"].trend_violation
        if tv.trendline is not None:
            assert "2024" in text or "2025" in text
            # The bar-index fallback format is "bar <digits>" (no date
            # available); the blurb's legitimate "N bar(s) ago" phrasing
            # never has a digit immediately after "bar ", so this pattern
            # unambiguously targets the fallback, not that phrasing.
            assert re.search(r"bar \d", text) is None
