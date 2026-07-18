import pandas as pd
import pytest

from rates_macro import fred_client


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


class TestResolveFredKey:
    def test_prefers_environment_variable(self, monkeypatch):
        monkeypatch.setenv("FRED_API_KEY", "env-key-123")
        assert fred_client.resolve_fred_key() == "env-key-123"

    def test_falls_back_to_external_config_outside_the_project(self, monkeypatch, tmp_path):
        # The project is slated for open-sourcing, so the real secret must
        # never live in a file inside the project tree -- only an external
        # location the repo doesn't contain.
        monkeypatch.delenv("FRED_API_KEY", raising=False)
        external = tmp_path / "external" / ".env"
        external.parent.mkdir()
        external.write_text("FRED_API_KEY=external-key-789\n")
        monkeypatch.setattr(fred_client, "_EXTERNAL_ENV_PATH", str(external))
        assert fred_client.resolve_fred_key() == "external-key-789"

    def test_external_config_takes_priority_over_project_dotenv(self, monkeypatch, tmp_path):
        monkeypatch.delenv("FRED_API_KEY", raising=False)
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".env").write_text("FRED_API_KEY=project-key-000\n")
        monkeypatch.setattr(fred_client, "_PROJECT_ROOT", str(project_dir))
        external = tmp_path / "external.env"
        external.write_text("FRED_API_KEY=external-key-789\n")
        monkeypatch.setattr(fred_client, "_EXTERNAL_ENV_PATH", str(external))
        assert fred_client.resolve_fred_key() == "external-key-789"

    def test_falls_back_to_project_dotenv_when_no_external_config(self, monkeypatch, tmp_path):
        monkeypatch.delenv("FRED_API_KEY", raising=False)
        (tmp_path / ".env").write_text("FRED_API_KEY=file-key-456\n")
        monkeypatch.setattr(fred_client, "_PROJECT_ROOT", str(tmp_path))
        monkeypatch.setattr(fred_client, "_EXTERNAL_ENV_PATH", str(tmp_path / "nonexistent" / ".env"))
        assert fred_client.resolve_fred_key() == "file-key-456"

    def test_returns_empty_string_when_unconfigured(self, monkeypatch, tmp_path):
        monkeypatch.delenv("FRED_API_KEY", raising=False)
        monkeypatch.setattr(fred_client, "_PROJECT_ROOT", str(tmp_path))
        monkeypatch.setattr(fred_client, "_EXTERNAL_ENV_PATH", str(tmp_path / "nonexistent" / ".env"))
        assert fred_client.resolve_fred_key() == ""


class TestFetchObservations:
    def test_raises_when_no_key_configured(self, monkeypatch):
        monkeypatch.setattr(fred_client, "resolve_fred_key", lambda: "")
        with pytest.raises(ValueError):
            fred_client.fetch_observations("DGS10")

    def test_returns_observations_list(self, monkeypatch):
        payload = {"observations": [{"date": "2026-01-02", "value": "4.5"}]}
        monkeypatch.setattr(
            fred_client.requests, "get", lambda *a, **k: _FakeResponse(payload)
        )
        result = fred_client.fetch_observations("DGS10", api_key="test-key")
        assert result == payload["observations"]


class TestFetchSeries:
    def test_parses_into_indexed_float_series(self, monkeypatch):
        payload = {
            "observations": [
                {"date": "2026-01-02", "value": "4.50"},
                {"date": "2026-01-03", "value": "4.55"},
            ]
        }
        monkeypatch.setattr(
            fred_client.requests, "get", lambda *a, **k: _FakeResponse(payload)
        )
        series = fred_client.fetch_series("DGS10", api_key="test-key")
        assert isinstance(series, pd.Series)
        assert list(series.values) == [4.50, 4.55]
        assert series.index[0] == pd.Timestamp("2026-01-02")

    def test_drops_fred_missing_value_marker(self, monkeypatch):
        payload = {
            "observations": [
                {"date": "2026-01-02", "value": "4.50"},
                {"date": "2026-01-03", "value": "."},
                {"date": "2026-01-04", "value": "4.60"},
            ]
        }
        monkeypatch.setattr(
            fred_client.requests, "get", lambda *a, **k: _FakeResponse(payload)
        )
        series = fred_client.fetch_series("DGS10", api_key="test-key")
        assert len(series) == 2
        assert "." not in series.values

    def test_empty_observations_returns_empty_series(self, monkeypatch):
        monkeypatch.setattr(
            fred_client.requests,
            "get",
            lambda *a, **k: _FakeResponse({"observations": []}),
        )
        series = fred_client.fetch_series("DGS10", api_key="test-key")
        assert series.empty


class TestSeriesCatalog:
    def test_all_series_combines_the_three_catalogs(self):
        assert "DGS10" in fred_client.ALL_SERIES
        assert "BAMLH0A0HYM2" in fred_client.ALL_SERIES
        assert "DTWEXBGS" in fred_client.ALL_SERIES

    def test_vulnerability_inputs_are_catalogued(self):
        # The raw FRED series the Red-Zone score assembles into its three
        # froth legs. Confirmed available on the live API (2026-07 check):
        # BAA10Y deep-history spread, NCBEILQ027S+GDP for market-cap-to-GDP,
        # QUSPAM770A for credit-to-GDP.
        for series_id in ("BAA10Y", "NCBEILQ027S", "GDP", "QUSPAM770A"):
            assert series_id in fred_client.VULNERABILITY_INPUTS

    def test_positioning_default_series_set_is_unchanged(self):
        # ALL_SERIES (the positioning score's default universe) must stay the
        # validated five daily series — vulnerability inputs live separately
        # so the positioning score's behavior is preserved byte-for-byte.
        assert set(fred_client.ALL_SERIES) == {
            "DGS10",
            "DGS2",
            "DFF",
            "BAMLH0A0HYM2",
            "DTWEXBGS",
        }

    def test_vulnerability_inputs_do_not_leak_into_positioning_universe(self):
        assert set(fred_client.ALL_SERIES).isdisjoint(fred_client.VULNERABILITY_INPUTS)
