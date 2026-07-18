import numpy as np
import pandas as pd
import pytest

from equity_rotation import market_data


def _healthy_frame(n=300, price=100.0, dollar_volume=5_000_000.0):
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    close = price + np.cumsum(np.random.default_rng(1).normal(0, 0.5, n))
    close = np.clip(close, 1.0, None)
    volume = np.full(n, dollar_volume / price)
    return pd.DataFrame(
        {
            "Open": close - 0.2,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": volume,
        },
        index=dates,
    )


def _multiindex_raw(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return pd.concat(frames, axis=1)


class TestQualityGate:
    def test_rejects_none(self):
        valid, reason, metrics = market_data.quality_gate(None)
        assert not valid
        assert "no price data" in reason
        assert metrics is None

    def test_rejects_empty_frame(self):
        valid, reason, _ = market_data.quality_gate(pd.DataFrame())
        assert not valid
        assert "no price data" in reason

    def test_rejects_frame_with_no_positive_closes(self):
        df = _healthy_frame()
        df["Close"] = np.nan
        valid, reason, _ = market_data.quality_gate(df)
        assert not valid
        assert "no valid closes" in reason

    def test_rejects_too_few_bars(self):
        df = _healthy_frame(n=100)
        valid, reason, _ = market_data.quality_gate(df)
        assert not valid
        assert "bars" in reason

    def test_rejects_thin_liquidity(self):
        df = _healthy_frame(n=300, dollar_volume=100_000.0)
        valid, reason, _ = market_data.quality_gate(df)
        assert not valid
        assert "dollar volume" in reason

    def test_accepts_healthy_liquid_frame(self):
        df = _healthy_frame(n=300, dollar_volume=5_000_000.0)
        valid, reason, metrics = market_data.quality_gate(df)
        assert valid
        assert reason == ""
        assert metrics.bars >= market_data.MIN_BARS
        assert metrics.median_dollar_volume >= market_data.MIN_MEDIAN_DOLLAR_VOLUME

    def test_rejects_when_stale_relative_to_as_of(self):
        df = _healthy_frame()
        far_future = df.index[-1] + pd.Timedelta(days=30)
        valid, reason, _ = market_data.quality_gate(df, as_of=far_future)
        assert not valid
        assert "stale" in reason


class TestExtractFrames:
    def test_extracts_each_ticker_from_multiindex(self):
        raw = _multiindex_raw({"AAA": _healthy_frame(n=10), "BBB": _healthy_frame(n=10)})
        frames = market_data._extract_frames(raw, ["AAA", "BBB"])
        assert set(frames) == {"AAA", "BBB"}
        assert list(frames["AAA"].columns) == list(market_data.REQUIRED_COLUMNS)

    def test_skips_ticker_missing_from_raw(self):
        raw = _multiindex_raw({"AAA": _healthy_frame(n=10)})
        frames = market_data._extract_frames(raw, ["AAA", "ZZZ"])
        assert set(frames) == {"AAA"}


class TestFetchUniverse:
    def test_raises_when_nothing_downloaded(self, monkeypatch):
        monkeypatch.setattr(market_data, "_download_chunk", lambda tickers, period: pd.DataFrame())
        with pytest.raises(RuntimeError, match="No data"):
            market_data.fetch_universe({"AAA": "Ticker A"})

    def test_isolates_bad_ticker_into_dropped(self, monkeypatch):
        raw = _multiindex_raw({"GOOD": _healthy_frame(n=300), "BAD": _healthy_frame(n=50)})
        monkeypatch.setattr(market_data, "_download_chunk", lambda tickers, period: raw)
        result = market_data.fetch_universe({"GOOD": "Good Co", "BAD": "Bad Co"})
        assert "GOOD" in result.closes
        assert "BAD" not in result.closes
        assert any(d["ticker"] == "BAD" for d in result.dropped)

    def test_returns_close_series_and_quality_for_healthy_universe(self, monkeypatch):
        raw = _multiindex_raw({"AAA": _healthy_frame(n=300), "BBB": _healthy_frame(n=300)})
        monkeypatch.setattr(market_data, "_download_chunk", lambda tickers, period: raw)
        result = market_data.fetch_universe({"AAA": "A Co", "BBB": "B Co"})
        assert set(result.closes) == {"AAA", "BBB"}
        assert set(result.quality) == {"AAA", "BBB"}
        assert len(result.dropped) == 0
        assert isinstance(result.as_of, pd.Timestamp)
