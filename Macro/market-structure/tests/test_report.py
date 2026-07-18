import numpy as np
import pandas as pd
import pytest

from market_structure import report
from market_structure.market_data import OHLCV

SMALL_UNIVERSE = {"SPY": "S&P 500", "QQQ": "Nasdaq 100"}


def _synthetic_ohlcv(ticker, n=300, seed=1, drift=0.05):
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(rng.normal(drift, 1.0, n))
    high = close + rng.uniform(0.2, 1.5, n)
    low = close - rng.uniform(0.2, 1.5, n)
    volume = rng.uniform(1_000_000, 5_000_000, n)
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    return OHLCV(ticker=ticker, dates=dates, high=high, low=low, close=close, volume=volume)


class TestBuildReport:
    def test_builds_report_for_all_tickers_when_data_is_healthy(self, monkeypatch):
        monkeypatch.setattr(
            report, "fetch_ohlcv", lambda ticker, **kw: _synthetic_ohlcv(ticker, seed=hash(ticker) % 1000)
        )
        result = report.build_report(universe=SMALL_UNIVERSE)
        assert set(result["reports"]) == set(SMALL_UNIVERSE)
        assert result["dropped"] == []
        assert result["gauge"].tickers
        assert 0 <= result["gauge"].overall_bull_score <= 100
        assert 0 <= result["gauge"].cash_on_sidelines_pct <= 100
        assert set(result["dates"]) == set(SMALL_UNIVERSE)

    def test_isolates_a_failing_ticker_into_dropped(self, monkeypatch):
        def fake_fetch(ticker, **kw):
            if ticker == "QQQ":
                raise RuntimeError("QQQ: failed quality gate — no price data")
            return _synthetic_ohlcv(ticker)

        monkeypatch.setattr(report, "fetch_ohlcv", fake_fetch)
        result = report.build_report(universe=SMALL_UNIVERSE)
        assert "QQQ" not in result["reports"]
        assert any(d["ticker"] == "QQQ" for d in result["dropped"])
        assert "SPY" in result["reports"]

    def test_raises_when_every_ticker_fails(self, monkeypatch):
        monkeypatch.setattr(
            report, "fetch_ohlcv", lambda ticker, **kw: (_ for _ in ()).throw(RuntimeError("no data"))
        )
        with pytest.raises(ValueError):
            report.build_report(universe=SMALL_UNIVERSE)


class TestRenderSummary:
    def test_output_contains_gauge_headline_and_ticker_rows(self, monkeypatch):
        monkeypatch.setattr(
            report, "fetch_ohlcv", lambda ticker, **kw: _synthetic_ohlcv(ticker, seed=hash(ticker) % 1000)
        )
        result = report.build_report(universe=SMALL_UNIVERSE)
        text = report.render_summary(result)
        assert "OVERALL BULLISHNESS" in text
        assert "CASH ON SIDELINES" in text
        assert "SPY" in text
        assert "QQQ" in text

    def test_output_is_fully_quantitative_breakdown_not_narrative_only(self, monkeypatch):
        # Every score must be traceable to a printed number -- this is the
        # whole point of the breakdown: no term of the formula is implicit.
        monkeypatch.setattr(
            report, "fetch_ohlcv", lambda ticker, **kw: _synthetic_ohlcv(ticker, seed=hash(ticker) % 1000)
        )
        result = report.build_report(universe=SMALL_UNIVERSE)
        text = report.render_summary(result)
        assert "bull_score       = clip(" in text  # the formula legend itself
        assert "trend_component=" in text
        assert "rr_component=" in text
        assert "violation_penalty=" in text
        assert "support stack" in text
        assert "trendline (" in text

    def test_trendline_dates_are_resolved_from_ohlcv_dates_not_bar_indices(self, monkeypatch):
        monkeypatch.setattr(
            report, "fetch_ohlcv", lambda ticker, **kw: _synthetic_ohlcv(ticker, seed=hash(ticker) % 1000)
        )
        result = report.build_report(universe={"SPY": "S&P 500"})
        text = report.render_summary(result)
        tv = result["reports"]["SPY"].trend_violation
        if tv.trendline is not None:
            # A real calendar year should appear in the trendline line, not
            # a "bar <index>" fallback -- proof render_summary is using the
            # OHLCV dates it was given rather than raw bar positions.
            assert "2024" in text or "2025" in text
            assert "bar " not in text
