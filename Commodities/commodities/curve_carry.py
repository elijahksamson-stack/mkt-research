"""
Futures curve shape and carry: front/second/third slope, roll yield,
curvature, and contango/backwardation classification, plus a curve-shape
change measure over a trailing window.

Sign convention (stated once, used everywhere below): `contango_pct` and
the annualized slopes are `(deferred - nearby) / nearby`. Positive means
the deferred contract is pricier -- contango. Negative means backwardation.
Roll yield is the return earned by holding the nearby contract and rolling
forward before expiry, which is the *opposite* sign: positive roll yield
in backwardation (sell the expensive nearby, buy the cheaper deferred),
negative in contango.

Curve-shape change deliberately reuses the same two dated-contract series
already fetched for the current snapshot (comparing today's close to the
close `change_lookback_days` bars earlier, *for the same two contracts*)
rather than re-deriving "front/second" at a past date -- that would risk
comparing different contracts entirely if a roll occurred inside the
lookback window, which would misread a roll as a curve-shape change.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal, Optional

from commodities.contracts import ContractMonth, next_contract_months
from commodities.market_data import fetch_dated_contract_close
from commodities.universe import CommodityInstrument

CURVE_CHANGE_LOOKBACK_DAYS = 21
FLAT_BAND_ANNUALIZED = 0.01  # within +-1%/yr, call the curve "flat" rather than contango/backwardation
CurveState = Literal["contango", "backwardation", "flat"]


@dataclass(frozen=True)
class CurveLeg:
    month: ContractMonth
    close: float
    close_lagged: Optional[float]  # close `CURVE_CHANGE_LOOKBACK_DAYS` bars earlier, same contract


@dataclass(frozen=True)
class CommodityCurve:
    canonical_id: str
    as_of: date
    legs: tuple[CurveLeg, ...]  # 2 or 3, chronological
    front_second_annualized: float  # (second-front)/front, annualized by month gap
    front_third_annualized: Optional[float]
    curvature: Optional[float]  # front_third_annualized - front_second_annualized; None with only 2 legs
    roll_yield_annualized: float  # -front_second_annualized
    curve_state: CurveState
    front_second_annualized_change: Optional[float]  # today's front_second_annualized minus the lagged one


def _month_gap(a: ContractMonth, b: ContractMonth) -> int:
    return (b.year * 12 + b.month) - (a.year * 12 + a.month)


def _annualized_slope(a_close: float, b_close: float, month_gap: int) -> float:
    if month_gap <= 0 or a_close <= 0:
        return float("nan")
    return (b_close - a_close) / a_close * (12.0 / month_gap)


def _classify(front_second_annualized: float) -> CurveState:
    if front_second_annualized > FLAT_BAND_ANNUALIZED:
        return "contango"
    if front_second_annualized < -FLAT_BAND_ANNUALIZED:
        return "backwardation"
    return "flat"


def build_curve(
    instrument: CommodityInstrument,
    as_of: Optional[date] = None,
    change_lookback_days: int = CURVE_CHANGE_LOOKBACK_DAYS,
) -> Optional[CommodityCurve]:
    """None if `instrument` has no futures (e.g. the uranium ETF proxy) or
    fewer than 2 of its next-3 dated contracts have usable data -- curve
    features must read as missing for those cases, not as a fabricated
    flat curve (see universe.py's module docstring)."""
    if not instrument.is_tradable_future:
        return None
    as_of = as_of or date.today()
    months = next_contract_months(instrument, as_of, count=3)

    legs: list[CurveLeg] = []
    for m in months:
        series = fetch_dated_contract_close(m.symbol, as_of=as_of)
        if series is None:
            continue
        close = float(series.iloc[-1])
        lagged = float(series.iloc[-1 - change_lookback_days]) if len(series) > change_lookback_days else None
        legs.append(CurveLeg(month=m, close=close, close_lagged=lagged))

    if len(legs) < 2:
        return None

    front, second = legs[0], legs[1]
    fs_gap = _month_gap(front.month, second.month)
    front_second_annualized = _annualized_slope(front.close, second.close, fs_gap)

    front_second_change = None
    if front.close_lagged is not None and second.close_lagged is not None:
        prior = _annualized_slope(front.close_lagged, second.close_lagged, fs_gap)
        if not (prior != prior):  # not NaN
            front_second_change = front_second_annualized - prior

    front_third_annualized = None
    curvature = None
    if len(legs) >= 3:
        third = legs[2]
        ft_gap = _month_gap(front.month, third.month)
        front_third_annualized = _annualized_slope(front.close, third.close, ft_gap)
        curvature = front_third_annualized - front_second_annualized

    return CommodityCurve(
        canonical_id=instrument.canonical_id,
        as_of=as_of,
        legs=tuple(legs),
        front_second_annualized=front_second_annualized,
        front_third_annualized=front_third_annualized,
        curvature=curvature,
        roll_yield_annualized=-front_second_annualized,
        curve_state=_classify(front_second_annualized),
        front_second_annualized_change=front_second_change,
    )
