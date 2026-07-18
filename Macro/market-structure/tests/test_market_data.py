import numpy as np
import pandas as pd
import pytest

from market_structure import market_data


def _healthy_ohlcv(n=300):
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    close = 100 + np.cumsum(np.random.default_rng(1).normal(0, 0.5, n))
    high = close + 1.0
    low = close - 1.0
    open_ = close - 0.2
    volume = np.full(n, 1_000_000.0)
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume}, index=dates
    )


class TestQualityGate:
    def test_rejects_empty_frame(self):
        valid, reason, _ = market_data.quality_gate(pd.DataFrame())
        assert not valid
        assert "no price data" in reason

    def test_rejects_frame_with_no_positive_closes(self):
        df = _healthy_ohlcv(n=300)
        df["Close"] = np.nan
        valid, reason, _ = market_data.quality_gate(df)
        assert not valid
        assert "no valid bars" in reason

    def test_rejects_too_few_bars(self):
        df = _healthy_ohlcv(n=100)
        valid, reason, metrics = market_data.quality_gate(df)
        assert not valid
        assert "bars" in reason
        assert metrics["bars"] == 100

    def test_accepts_healthy_frame(self):
        df = _healthy_ohlcv(n=300)
        valid, reason, metrics = market_data.quality_gate(df)
        assert valid
        assert reason == ""
        assert metrics["bars"] >= market_data.MIN_BARS

    def test_rejects_when_stale_relative_to_as_of(self):
        df = _healthy_ohlcv(n=300)
        far_future = df.index[-1] + pd.Timedelta(days=30)
        valid, reason, _ = market_data.quality_gate(df, as_of=far_future)
        assert not valid
        assert "stale" in reason


class TestFetchOHLCV:
    def test_raises_when_download_returns_empty(self, monkeypatch):
        monkeypatch.setattr(market_data, "_download", lambda ticker, period: pd.DataFrame())
        with pytest.raises(RuntimeError, match="quality gate"):
            market_data.fetch_ohlcv("SPY")

    def test_raises_when_quality_gate_rejects(self, monkeypatch):
        short_df = _healthy_ohlcv(n=50)
        monkeypatch.setattr(market_data, "_download", lambda ticker, period: short_df)
        with pytest.raises(RuntimeError, match="quality gate"):
            market_data.fetch_ohlcv("SPY")

    def test_returns_ohlcv_arrays_when_healthy(self, monkeypatch):
        df = _healthy_ohlcv(n=300)
        monkeypatch.setattr(market_data, "_download", lambda ticker, period: df)
        result = market_data.fetch_ohlcv("SPY")
        assert result.ticker == "SPY"
        assert len(result.close) == 300
        assert len(result.high) == len(result.low) == len(result.volume) == 300
        assert np.all(result.high >= result.low)
