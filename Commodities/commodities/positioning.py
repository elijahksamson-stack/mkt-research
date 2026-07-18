"""
CFTC Commitments of Traders (Disaggregated Futures-Only Combined report)
positioning, converted to rolling z-scores/percentiles, with point-in-time
publication lag.

Data source verified live against the CFTC Socrata API
(`https://publicreporting.cftc.gov/resource/72hh-3qpy.json`, dataset
"Disaggregated Futures-Only Combined") -- field names below
(`m_money_positions_long_all`, `prod_merc_positions_long`, etc.) and every
`universe.py` `cftc_market_name` value were confirmed against real API
responses, not assumed from memory. The Disaggregated report (not the
older Legacy comm/non-comm report) is used because the spec specifically
asks for "commercial, managed-money, and producer positioning" --
Disaggregated is the CFTC's own split of "commercial" into
Producer/Merchant vs. Swap Dealers, and separates out Managed Money from
the old catch-all "Non-Commercial" category.

Publication lag: CFTC's `report_date_as_yyyy_mm_dd` is the Tuesday the
report reflects, but the report isn't published until the following
Friday (COT_PUBLICATION_LAG_DAYS below). A feature built as of any date
between that Tuesday and Friday must not see this report yet -- every
function here filters on `publication_date <= as_of`, not `report_date`,
for exactly that reason.
"""
from __future__ import annotations

import urllib.parse
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
import requests

CFTC_BASE_URL = "https://publicreporting.cftc.gov/resource/72hh-3qpy.json"
COT_PUBLICATION_LAG_DAYS = 3  # Tuesday report_date -> Friday publication
DEFAULT_HISTORY_WEEKS = 260  # ~5 years of weekly reports
ZSCORE_WINDOW_WEEKS = 156  # ~3 years, per spec's "own five-year seasonal range" spirit but bounded for recency
REQUEST_TIMEOUT_SECONDS = 20

FIELDS = (
    "report_date_as_yyyy_mm_dd", "open_interest_all",
    "m_money_positions_long_all", "m_money_positions_short_all",
    "prod_merc_positions_long", "prod_merc_positions_short",
)


def fetch_cot_history(cftc_market_name: str, weeks: int = DEFAULT_HISTORY_WEEKS) -> pd.DataFrame:
    """Weekly COT history for one CFTC `contract_market_name` (exact match,
    verified names live in universe.py), oldest first. Returns an empty
    DataFrame (not a raised exception) on any request failure -- one
    commodity's CFTC outage shouldn't take down the whole ranking run,
    matching market-structure's per-ticker isolation convention."""
    params = {
        "$select": ",".join(FIELDS),
        "$where": f"contract_market_name = '{cftc_market_name}'",
        "$order": "report_date_as_yyyy_mm_dd DESC",
        "$limit": weeks,
    }
    url = f"{CFTC_BASE_URL}?{urllib.parse.urlencode(params)}"
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
        records = resp.json()
    except (requests.RequestException, ValueError):
        return pd.DataFrame(columns=list(FIELDS))

    if not records:
        return pd.DataFrame(columns=list(FIELDS))

    df = pd.DataFrame(records)
    df["report_date"] = pd.to_datetime(df["report_date_as_yyyy_mm_dd"])
    df["publication_date"] = df["report_date"] + pd.Timedelta(days=COT_PUBLICATION_LAG_DAYS)
    for col in ("open_interest_all", "m_money_positions_long_all", "m_money_positions_short_all",
                "prod_merc_positions_long", "prod_merc_positions_short"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["m_money_net"] = df["m_money_positions_long_all"] - df["m_money_positions_short_all"]
    df["prod_merc_net"] = df["prod_merc_positions_long"] - df["prod_merc_positions_short"]
    return df.sort_values("report_date").reset_index(drop=True)


def _zscore_and_percentile(series: pd.Series, window: int) -> tuple[float, float]:
    tail = series.tail(window).dropna()
    if len(tail) < 8:
        return float("nan"), float("nan")
    latest = float(tail.iloc[-1])
    std = float(tail.std())
    z = (latest - float(tail.mean())) / std if std > 1e-9 else 0.0
    percentile = float((tail < latest).mean() * 100)
    return z, percentile


@dataclass(frozen=True)
class PositioningSnapshot:
    canonical_id: str
    as_of: pd.Timestamp
    report_date: pd.Timestamp
    weeks_of_history: int
    open_interest: float
    managed_money_net: float
    managed_money_net_zscore: float
    managed_money_net_percentile: float
    managed_money_net_weekly_change: float
    producer_merchant_net: float
    producer_merchant_net_zscore: float
    producer_merchant_net_percentile: float
    producer_merchant_net_weekly_change: float


def build_positioning_snapshot(
    canonical_id: str,
    cot_df: pd.DataFrame,
    as_of: Optional[pd.Timestamp] = None,
    zscore_window: int = ZSCORE_WINDOW_WEEKS,
) -> Optional[PositioningSnapshot]:
    """None if `cot_df` is empty or no report has been published as of
    `as_of` yet (point-in-time gate on `publication_date`) -- positioning
    features must read as missing in that case, not zero-filled."""
    if cot_df.empty:
        return None
    visible = cot_df if as_of is None else cot_df[cot_df["publication_date"] <= as_of]
    if visible.empty:
        return None

    mm_z, mm_pct = _zscore_and_percentile(visible["m_money_net"], zscore_window)
    pm_z, pm_pct = _zscore_and_percentile(visible["prod_merc_net"], zscore_window)
    latest = visible.iloc[-1]
    prior = visible.iloc[-2] if len(visible) >= 2 else None

    return PositioningSnapshot(
        canonical_id=canonical_id,
        as_of=pd.Timestamp(as_of) if as_of is not None else pd.Timestamp(latest["publication_date"]),
        report_date=pd.Timestamp(latest["report_date"]),
        weeks_of_history=len(visible),
        open_interest=float(latest["open_interest_all"]),
        managed_money_net=float(latest["m_money_net"]),
        managed_money_net_zscore=mm_z,
        managed_money_net_percentile=mm_pct,
        managed_money_net_weekly_change=float(latest["m_money_net"] - prior["m_money_net"]) if prior is not None else float("nan"),
        producer_merchant_net=float(latest["prod_merc_net"]),
        producer_merchant_net_zscore=pm_z,
        producer_merchant_net_percentile=pm_pct,
        producer_merchant_net_weekly_change=float(latest["prod_merc_net"] - prior["prod_merc_net"]) if prior is not None else float("nan"),
    )
