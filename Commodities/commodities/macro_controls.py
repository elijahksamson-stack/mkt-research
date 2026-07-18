"""
Small macro control set: USD index, real yields, inflation expectations,
and a broad commodity index -- the spec's "small macro control set" for
features.py to condition on, distinct from any single commodity's own
series.

Sources, verified live (see the Bash checks run during this build):
- USD index: yfinance `DX-Y.NYB` (ICE US Dollar Index spot).
- Real 10-year yield: FRED `DFII10` (10-Year Treasury Inflation-Indexed
  Security yield) via FRED's public `fredgraph.csv` endpoint -- no API key
  required, confirmed with a live curl returning real observations through
  the current date.
- 10-year breakeven inflation expectations: FRED `T10YIE`, same endpoint.
- Broad commodity index: yfinance `^SPGSCI` (S&P GSCI).

`trend_signal` on each snapshot reuses `rates_macro.trend_rr.trend_rr_profile`
(the same reused Trend Analysis engine as trend_adapter.py) rather than
computing a second ad hoc trend measure for macro series.
"""
from __future__ import annotations

import io
from dataclasses import dataclass
from datetime import date
from typing import Optional

import pandas as pd
import requests
from rates_macro.trend_rr import trend_rr_profile

from commodities.market_data import fetch_generic_series

FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
REQUEST_TIMEOUT_SECONDS = 20
CHANGE_WINDOW_DAYS = 63

MACRO_SERIES: dict[str, tuple[str, str]] = {
    # name -> (source, identifier)
    "usd_index": ("yfinance", "DX-Y.NYB"),
    "real_yield_10y": ("fred", "DFII10"),
    "inflation_expectations_10y": ("fred", "T10YIE"),
    "broad_commodity_index": ("yfinance", "^SPGSCI"),
}


def fetch_fred_series(series_id: str) -> Optional[pd.Series]:
    """FRED's public CSV export -- no API key needed. Returns None on any
    request failure or if the series comes back empty, matching this
    package's per-series graceful-degradation convention."""
    try:
        resp = requests.get(FRED_CSV_URL, params={"id": series_id}, timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text))
    except (requests.RequestException, ValueError):
        return None
    if series_id not in df.columns or "observation_date" not in df.columns:
        return None
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    values = pd.to_numeric(df[series_id], errors="coerce")  # FRED uses "." for missing observations
    series = pd.Series(values.to_numpy(), index=df["observation_date"]).dropna()
    return series if len(series) > 0 else None


@dataclass(frozen=True)
class MacroSeriesSnapshot:
    name: str
    as_of: pd.Timestamp
    level: float
    change_63d: Optional[float]
    trend_signal: Optional[float]


def build_macro_snapshot(name: str, series: pd.Series, as_of: Optional[date] = None) -> Optional[MacroSeriesSnapshot]:
    visible = series if as_of is None else series.loc[:pd.Timestamp(as_of)]
    if visible.empty:
        return None
    level = float(visible.iloc[-1])
    change_63d = float(level - visible.iloc[-1 - CHANGE_WINDOW_DAYS]) if len(visible) > CHANGE_WINDOW_DAYS else None
    trend_signal = None
    try:
        trend_signal = trend_rr_profile(visible)["trend_signal"]
    except ValueError:
        pass  # not enough history for any regression window -- trend_signal stays None
    return MacroSeriesSnapshot(
        name=name, as_of=pd.Timestamp(visible.index[-1]), level=level, change_63d=change_63d, trend_signal=trend_signal
    )


def fetch_macro_series(period: str = "3y") -> dict[str, pd.Series]:
    """Raw series for every entry in MACRO_SERIES, fetched once. Exposed
    separately from fetch_macro_controls so features.py can build a
    MacroSeriesSnapshot at many different historical `as_of` points from a
    single fetch, instead of re-fetching per as_of."""
    series_by_name: dict[str, pd.Series] = {}
    for name, (source, identifier) in MACRO_SERIES.items():
        series = fetch_fred_series(identifier) if source == "fred" else fetch_generic_series(identifier, period=period)
        if series is not None:
            series_by_name[name] = series
    return series_by_name


def fetch_macro_controls(as_of: Optional[date] = None, period: str = "3y") -> dict[str, MacroSeriesSnapshot]:
    """Fetches every series in MACRO_SERIES and builds a point-in-time
    snapshot for each. A series that fails to fetch or has no usable
    history as of `as_of` is simply absent from the result dict --
    features.py must treat a missing macro control as missing, not zero."""
    snapshots: dict[str, MacroSeriesSnapshot] = {}
    for name, series in fetch_macro_series(period).items():
        snap = build_macro_snapshot(name, series, as_of)
        if snap is not None:
            snapshots[name] = snap
    return snapshots
