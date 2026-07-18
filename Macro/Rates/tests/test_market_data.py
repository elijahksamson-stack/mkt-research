import numpy as np
import pandas as pd
import pytest

from rates_macro import market_data


def _healthy_close(n=260):
    dates = pd.date_range("2025-01-01", periods=n, freq="B")
    values = 100 + np.cumsum(np.random.default_rng(1).normal(0, 0.5, n))
    return pd.Series(values, index=dates)


class TestQualityGate:
    def test_rejects_empty_series(self):
        valid, reason, _ = market_data.quality_gate(pd.Series(dtype=float))
        assert not valid
        assert "no price data" in reason

    def test_rejects_series_with_no_positive_closes(self):
        series = pd.Series([np.nan] * 300)
        valid, reason, _ = market_data.quality_gate(series)
        assert not valid
        assert "no valid closes" in reason

    def test_rejects_too_few_bars(self):
        series = _healthy_close(n=100)
        valid, reason, metrics = market_data.quality_gate(series)
        assert not valid
        assert "bars" in reason
        assert metrics["bars"] == 100

    def test_rejects_low_coverage_within_lookback(self):
        # 300 bars total so dropna() still clears MIN_BARS even after the
        # gap below is removed — otherwise the bars-count check fires first.
        series = _healthy_close(n=300)
        gappy = series.copy()
        gappy.iloc[270:283] = np.nan  # 13 gaps inside the trailing 252-bar window
        valid, reason, _ = market_data.quality_gate(gappy)
        assert not valid
        assert "coverage" in reason

    def test_accepts_healthy_series(self):
        series = _healthy_close(n=260)
        valid, reason, metrics = market_data.quality_gate(series)
        assert valid
        assert reason == ""
        assert metrics["bars"] >= market_data.MIN_BARS

    def test_rejects_when_stale_relative_to_as_of(self):
        series = _healthy_close(n=260)
        far_future = series.index[-1] + pd.Timedelta(days=30)
        valid, reason, _ = market_data.quality_gate(series, as_of=far_future)
        assert not valid
        assert "stale" in reason

    def test_accepts_when_within_staleness_window(self):
        series = _healthy_close(n=260)
        near_future = series.index[-1] + pd.Timedelta(days=2)
        valid, reason, _ = market_data.quality_gate(series, as_of=near_future)
        assert valid


class TestFetchClose:
    def test_raises_when_download_returns_empty(self, monkeypatch):
        monkeypatch.setattr(market_data, "_download", lambda ticker, period: pd.DataFrame())
        with pytest.raises(RuntimeError, match="no price data"):
            market_data.fetch_close("SPY")

    def test_raises_when_quality_gate_rejects(self, monkeypatch):
        short_series = _healthy_close(n=50)
        raw = pd.DataFrame({"Close": short_series})
        monkeypatch.setattr(market_data, "_download", lambda ticker, period: raw)
        with pytest.raises(RuntimeError, match="quality gate"):
            market_data.fetch_close("SPY")

    def test_returns_close_series_when_healthy(self, monkeypatch):
        healthy = _healthy_close(n=260)
        raw = pd.DataFrame({"Close": healthy})
        monkeypatch.setattr(market_data, "_download", lambda ticker, period: raw)
        result = market_data.fetch_close("SPY")
        assert isinstance(result, pd.Series)
        assert len(result) == 260

    def test_rejects_gappy_series_through_the_real_fetch_path(self, monkeypatch):
        # Regression: fetch_close used to call close.dropna() BEFORE
        # quality_gate(), which made quality_gate's coverage computation
        # (close.tail(MIN_BARS).notna().mean()) always see a NaN-free
        # series and always evaluate to 1.0 -- the coverage gate could
        # never fire through the real fetch path, only when quality_gate
        # was called directly (as the unit tests above do).
        series = _healthy_close(n=300)
        gappy = series.copy()
        gappy.iloc[270:283] = np.nan  # 13 gaps inside the trailing 252-bar window
        raw = pd.DataFrame({"Close": gappy})
        monkeypatch.setattr(market_data, "_download", lambda ticker, period: raw)
        with pytest.raises(RuntimeError, match="quality gate"):
            market_data.fetch_close("SPY")
