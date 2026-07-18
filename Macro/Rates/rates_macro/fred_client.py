"""
FRED (Federal Reserve Economic Data) client.

Key resolution and provenance conventions mirror
InvestorPro/python/tools/macro_sentiment.py::_resolve_fred_key — never
fabricate a number; a missing key or failed fetch raises so the caller
decides how to surface that, instead of silently returning a stale/fake
value.
"""
from __future__ import annotations

import os
from typing import Optional

import pandas as pd
import requests

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_HERE, ".."))

# Kept outside the project tree entirely (not project-root/.env) since this
# repo is slated for open-sourcing — a secret must never be a file this repo
# could accidentally ship, gitignored or not.
_EXTERNAL_ENV_PATH = os.path.join(
    os.path.expanduser("~"), ".config", "rates-macro", ".env"
)

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
_TIMEOUT = 15

# Series named directly by Macro/Rates/CLAUDE.md ("high yield credits and
# rates", "US Dollar series"), plus the short end so "rates" (plural) covers
# more than one point on the curve.
RATES_SERIES = {
    "DGS10": "10-Year Treasury Constant Maturity Rate",
    "DGS2": "2-Year Treasury Constant Maturity Rate",
    "DFF": "Effective Federal Funds Rate",
}
CREDIT_SERIES = {
    "BAMLH0A0HYM2": "ICE BofA US High Yield Index Option-Adjusted Spread",
}
FX_SERIES = {
    "DTWEXBGS": "Trade Weighted U.S. Dollar Index: Broad, Goods and Services",
}
ALL_SERIES = {**RATES_SERIES, **CREDIT_SERIES, **FX_SERIES}

# Raw FRED inputs the vulnerability (Red-Zone) score assembles into its three
# froth legs. Kept SEPARATE from ALL_SERIES so the positioning score's default
# universe — and thus its validated behavior — stays unchanged.
#
# Why these specific IDs (all confirmed live on the FRED API, 2026-07):
# - BAA10Y: Moody's Baa-minus-10Y credit spread. Deep DAILY history back to
#   1986 and NOT license-restricted, unlike the ICE BofA OAS series
#   (BAMLH0A0HYM2/BAMLC0A0CM), whose API access is capped at ~3 recent years —
#   too short to place today's spread against history. This is the
#   percentile backbone of the price-of-credit froth leg.
# - NCBEILQ027S / GDP: nonfinancial corporate equities market value over GDP,
#   i.e. a market-cap-to-GDP ("Buffett indicator") for the asset-froth leg.
#   Both quarterly back to the 1940s. The millions-vs-billions unit mismatch
#   is irrelevant because froth is scored on the ratio's PERCENTILE, which is
#   scale-invariant.
# - QUSPAM770A: BIS credit-to-GDP for the US private non-financial sector —
#   exactly Greenwood-Hanson's credit-expansion variable. The quantity-froth
#   leg scores the percentile of its trailing multi-quarter CHANGE (it's the
#   change, not the level, that Greenwood flags).
VULNERABILITY_INPUTS = {
    "BAA10Y": "Moody's Seasoned Baa Corporate Bond Yield Relative to 10-Year Treasury",
    "NCBEILQ027S": "Nonfinancial Corporate Business; Corporate Equities; Market Value",
    "GDP": "Gross Domestic Product (nominal)",
    "QUSPAM770A": "BIS Credit to Private Non-Financial Sector, % of GDP (US)",
}


def _read_env_file(path: str, key: str) -> str:
    """Pull KEY=value from a .env-style file without a dotenv dependency."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key}="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
    except OSError:
        pass
    return ""


def resolve_fred_key() -> str:
    """FRED_API_KEY from the environment, else an external config file
    outside this project directory (~/.config/rates-macro/.env), else this
    project's own local .env (for anyone who prefers that instead)."""
    if env := os.environ.get("FRED_API_KEY"):
        return env
    if key := _read_env_file(_EXTERNAL_ENV_PATH, "FRED_API_KEY"):
        return key
    return _read_env_file(os.path.join(_PROJECT_ROOT, ".env"), "FRED_API_KEY")


def fetch_observations(
    series_id: str, api_key: Optional[str] = None, limit: int = 100_000
) -> list[dict]:
    """Raw ascending-order observation rows for a FRED series.

    Raises ValueError if no API key is configured, requests.HTTPError if the
    request fails.
    """
    key = api_key or resolve_fred_key()
    if not key:
        raise ValueError(
            "No FRED_API_KEY configured (set the env var or add it to .env)."
        )
    resp = requests.get(
        FRED_BASE_URL,
        params={
            "series_id": series_id,
            "api_key": key,
            "file_type": "json",
            "sort_order": "asc",
            "limit": limit,
        },
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json().get("observations", [])


def fetch_series(series_id: str, api_key: Optional[str] = None) -> pd.Series:
    """A FRED series as a float pandas Series indexed by date.

    FRED's missing-value marker ('.') is dropped rather than coerced to 0 —
    a market holiday or unreported print is not the same as a zero reading.
    """
    observations = fetch_observations(series_id, api_key=api_key)
    rows = [
        (pd.Timestamp(obs["date"]), float(obs["value"]))
        for obs in observations
        if obs.get("value") not in (".", "", None)
    ]
    if not rows:
        return pd.Series(dtype=float)
    dates, values = zip(*rows)
    return pd.Series(values, index=pd.DatetimeIndex(dates), name=series_id)
