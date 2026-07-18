import numpy as np
import pandas as pd
import pytest

from crypto_structure import market_data


def _healthy_ohlcv(n=300, price=100.0, volume=1_000_000.0):
    dates = pd.date_range("2024-01-01", periods=n, freq="D")  # crypto trades every calendar day
    noise_scale = min(0.5, price * 0.01)  # keep noise proportional so a tiny `price` stays positive
    close = price + np.cumsum(np.random.default_rng(1).normal(0, noise_scale, n))
    high = close + noise_scale * 2
    low = close - noise_scale * 2
    open_ = close - noise_scale * 0.4
    vol = np.full(n, volume)
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": vol}, index=dates
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

    def test_accepts_healthy_liquid_frame(self):
        df = _healthy_ohlcv(n=300, price=100.0, volume=1_000_000.0)  # $100M/day dollar volume
        valid, reason, metrics = market_data.quality_gate(df)
        assert valid
        assert reason == ""
        assert metrics["bars"] >= market_data.MIN_BARS

    def test_rejects_when_stale_relative_to_as_of(self):
        df = _healthy_ohlcv(n=300)
        far_future = df.index[-1] + pd.Timedelta(days=10)  # tighter than equities' 10-day tolerance
        valid, reason, _ = market_data.quality_gate(df, as_of=far_future)
        assert not valid
        assert "stale" in reason

    def test_rejects_illiquid_frame_below_dollar_volume_threshold(self):
        df = _healthy_ohlcv(n=300, price=0.001, volume=100.0)  # ~$0.10/day dollar volume
        valid, reason, metrics = market_data.quality_gate(df)
        assert not valid
        assert "dollar volume" in reason


class TestFetchOHLCV:
    def test_raises_when_download_returns_empty(self, monkeypatch):
        monkeypatch.setattr(market_data, "_download", lambda ticker, period: pd.DataFrame())
        with pytest.raises(RuntimeError, match="quality gate"):
            market_data.fetch_ohlcv("BTC-USD")

    def test_raises_when_quality_gate_rejects(self, monkeypatch):
        short_df = _healthy_ohlcv(n=50)
        monkeypatch.setattr(market_data, "_download", lambda ticker, period: short_df)
        with pytest.raises(RuntimeError, match="quality gate"):
            market_data.fetch_ohlcv("BTC-USD")

    def test_returns_ohlcv_arrays_when_healthy(self, monkeypatch):
        df = _healthy_ohlcv(n=300)
        monkeypatch.setattr(market_data, "_download", lambda ticker, period: df)
        result = market_data.fetch_ohlcv("BTC-USD")
        assert result.ticker == "BTC-USD"
        assert len(result.close) == 300
        assert len(result.high) == len(result.low) == len(result.volume) == 300
        assert np.all(result.high >= result.low)


class TestDownloadUniverse:
    def test_splits_healthy_and_unhealthy_tickers(self, monkeypatch):
        def fake_batch(tickers, period):
            frames = {}
            for t in tickers:
                if t == "BTC-USD":
                    frames[t] = _healthy_ohlcv(n=300)
                # ETH-USD deliberately omitted -> no price data
            multi = pd.concat(frames, axis=1) if frames else pd.DataFrame()
            return multi

        monkeypatch.setattr(market_data, "_download_batch", fake_batch)
        results, dropped = market_data.download_universe(["BTC-USD", "ETH-USD"])
        assert "BTC-USD" in results
        assert any(d["ticker"] == "ETH-USD" for d in dropped)

    def test_empty_batch_response_drops_every_ticker(self, monkeypatch):
        monkeypatch.setattr(market_data, "_download_batch", lambda tickers, period: pd.DataFrame())
        results, dropped = market_data.download_universe(["BTC-USD", "ETH-USD"])
        assert results == {}
        assert {d["ticker"] for d in dropped} == {"BTC-USD", "ETH-USD"}

    def test_deduplicates_and_normalizes_ticker_casing(self, monkeypatch):
        captured = []

        def fake_batch(tickers, period):
            captured.extend(tickers)
            frames = {t: _healthy_ohlcv(n=300) for t in tickers}
            return pd.concat(frames, axis=1)

        monkeypatch.setattr(market_data, "_download_batch", fake_batch)
        market_data.download_universe(["btc-usd", "BTC-USD", " eth-usd "])
        assert captured == ["BTC-USD", "ETH-USD"]
