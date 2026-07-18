"""
Mean-reversion / dislocation signals: Bollinger/ATR-style displacement from
a short moving average, an ADF stationarity gate that only "activates" the
displacement signal when the series is demonstrably range-bound, and
Engle-Granger cointegration tests restricted to economically linked pairs
(never run mechanically on every outright commodity price, per the spec).

Pure math over arrays already fetched elsewhere (no I/O here), matching
market_structure's indicators.py convention -- `features.py` is the only
caller expected to fetch data and hand it to this module.

Why ADF-gate rather than always trusting a Bollinger z-score: a strongly
trending market can sit outside its bands for weeks (that's what a trend
*is*), and treating that as a "buy the dip" mean-reversion signal is a
classic false-positive. `RangeBoundGate.is_range_bound` (ADF p-value below
threshold, i.e. the null of a unit root is rejected) is a necessary
condition before `Displacement.mean_reversion_active` is allowed to be
True at all.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.stattools import adfuller, coint

from market_structure.indicators import average_true_range

BOLLINGER_WINDOW = 20
ADF_PVALUE_THRESHOLD = 0.10
BOLLINGER_Z_ACTIVATION = 1.5  # |bollinger_z| must clear this, on top of the ADF gate, to "activate"
COINT_PVALUE_THRESHOLD = 0.05
COINT_WINDOW = 252
SPREAD_Z_WINDOW = 63


@dataclass(frozen=True)
class RangeBoundGate:
    adf_statistic: float
    adf_pvalue: float
    is_range_bound: bool


@dataclass(frozen=True)
class Displacement:
    canonical_id: str
    bollinger_z: float  # (last_price - SMA_window) / STD_window
    atr_displacement: float  # (last_price - SMA_window) / ATR
    range_bound: RangeBoundGate
    mean_reversion_active: bool  # range_bound.is_range_bound AND |bollinger_z| >= BOLLINGER_Z_ACTIVATION


def adf_gate(close: np.ndarray, pvalue_threshold: float = ADF_PVALUE_THRESHOLD) -> RangeBoundGate:
    """ADF test on the raw close level. Requires >=30 observations;
    returns a non-range-bound gate (p=1.0) below that, since a unit-root
    test on too little data is unreliable in either direction."""
    if len(close) < 30:
        return RangeBoundGate(adf_statistic=float("nan"), adf_pvalue=1.0, is_range_bound=False)
    stat, pvalue, *_ = adfuller(close, autolag="AIC")
    return RangeBoundGate(adf_statistic=float(stat), adf_pvalue=float(pvalue), is_range_bound=bool(pvalue < pvalue_threshold))


def build_displacement(
    canonical_id: str,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    window: int = BOLLINGER_WINDOW,
) -> Displacement:
    """`high`/`low`/`close` should be the raw continuous series (same input
    convention as risk_reward_adapter.py) -- displacement is a price-level
    concept, not a return concept, so it belongs on the same series as the
    structural levels it's meant to complement."""
    tail = close[-window:]
    sma = float(np.mean(tail))
    std = float(np.std(tail))
    last = float(close[-1])
    bollinger_z = (last - sma) / std if std > 1e-9 else 0.0
    atr = average_true_range(high, low, close)
    atr_displacement = (last - sma) / atr if atr > 1e-9 else 0.0

    gate = adf_gate(close)
    active = gate.is_range_bound and abs(bollinger_z) >= BOLLINGER_Z_ACTIVATION

    return Displacement(
        canonical_id=canonical_id, bollinger_z=bollinger_z, atr_displacement=atr_displacement,
        range_bound=gate, mean_reversion_active=active,
    )


@dataclass(frozen=True)
class PairCointegration:
    numerator_id: str
    denominator_id: str
    coint_pvalue: float
    is_cointegrated: bool
    hedge_ratio: float  # OLS beta: numerator ~ beta * denominator
    spread_z: float  # (numerator - beta*denominator) z-scored over SPREAD_Z_WINDOW


def build_pair_cointegration(
    numerator_id: str,
    denominator_id: str,
    numerator_close: pd.Series,
    denominator_close: pd.Series,
    window: int = COINT_WINDOW,
) -> Optional[PairCointegration]:
    """Engle-Granger cointegration test on roll-adjusted close levels
    (aligned on shared dates), restricted by the caller to
    universe.CANONICAL_PAIRS -- never call this on an arbitrary pair, since
    cointegration testing without an economic prior is a multiple-testing
    trap (spurious cointegration turns up by chance across enough pairs)."""
    joined = pd.DataFrame({"num": numerator_close, "den": denominator_close}).dropna().tail(window)
    if len(joined) < 60:
        return None

    stat, pvalue, _crit = coint(joined["num"].to_numpy(), joined["den"].to_numpy())
    model = LinearRegression().fit(joined[["den"]].to_numpy(), joined["num"].to_numpy())
    hedge_ratio = float(model.coef_[0])
    spread = joined["num"].to_numpy() - hedge_ratio * joined["den"].to_numpy()
    tail_spread = spread[-SPREAD_Z_WINDOW:]
    spread_std = float(np.std(tail_spread))
    spread_z = float((spread[-1] - np.mean(tail_spread)) / spread_std) if spread_std > 1e-9 else 0.0

    return PairCointegration(
        numerator_id=numerator_id, denominator_id=denominator_id, coint_pvalue=float(pvalue),
        is_cointegrated=pvalue < COINT_PVALUE_THRESHOLD, hedge_ratio=hedge_ratio, spread_z=spread_z,
    )
