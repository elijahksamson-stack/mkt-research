"""
Cross-sectional rotation ranking: which ticker in a universe (sector ETFs,
or factor ETFs -- see universe.py) is both leading its peers right now
*and* still has room to run.

This is the reformed, genuinely-novel core of the sector-rotation script
this package was ported from -- unlike trend_regression.py (a duplicate of
math that already exists in Macro/Rates), nothing else in the repo builds
this peer/benchmark-blended leadership+opportunity ranking. Reformed here
as pure functions over immutable dataclasses instead of the original's
DataFrame built with `.sort_values(...)` / `.insert(...)` mutation chain.

Two scores per ticker, blended from three regression_profile reads:
  - `leadership` (0-100): is this ticker outperforming, weighted 60% on
    its trend vs. every *other* ticker in the universe (peer-relative --
    the actual rotation signal), 25% on its trend vs. the benchmark, 15%
    on its own outright trend (a ticker can lead its peers while the
    whole universe drifts down, so the peer read dominates the blend).
  - `opportunity` (0-100): how much forward room is left, 65% from the
    ticker's own regression_profile.opportunity, 35% from its
    benchmark-relative ratio's opportunity (an opportunity that shows up
    both outright and relative to the benchmark is more robust than one
    that's just relative-strength noise).
  - `joint`: harmonic mean of leadership and opportunity -- a ticker has
    to score reasonably on *both* to rank well; harmonic mean punishes a
    lopsided score (e.g. leadership=95, opportunity=5) more than an
    arithmetic mean would.

Ranking sorts by `joint` descending, tie-broken by Pareto dominance count
ascending (fewer tickers that beat this one on both axes at once is
better), then leadership, then opportunity.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from equity_rotation.relative_strength import aligned_ratio
from equity_rotation.trend_regression import regression_profile

PEER_LEADERSHIP_WEIGHT = 0.60
BENCHMARK_LEADERSHIP_WEIGHT = 0.25
ABSOLUTE_LEADERSHIP_WEIGHT = 0.15

ABSOLUTE_OPPORTUNITY_WEIGHT = 0.65
BENCHMARK_OPPORTUNITY_WEIGHT = 0.35

NEUTRAL_LEADERSHIP = 50.0


@dataclass(frozen=True)
class RotationRank:
    rank: int
    ticker: str
    name: str
    leadership: float
    opportunity: float
    joint: float
    peer_leadership: float
    benchmark_leadership: float
    absolute_leadership: float
    absolute_opportunity: float
    benchmark_opportunity: float
    pareto_dominated_by: int


@dataclass(frozen=True)
class RotationTable:
    ranks: list[RotationRank]  # sorted best (rank 1) first
    pair_signals: dict[str, dict[str, float]]  # ticker -> {other: ratio trend_signal}


def _leadership_score(trend_signal: float) -> float:
    """Map a trend_signal in [-1, 1] to a 0-100 leadership score."""
    return NEUTRAL_LEADERSHIP + NEUTRAL_LEADERSHIP * trend_signal


def _pareto_dominated_by(scores: dict[str, tuple[float, float]]) -> dict[str, int]:
    """For each ticker, count how many other tickers are weakly better on
    both (leadership, opportunity) and strictly better on at least one --
    i.e. how many tickers Pareto-dominate it. 0 means undominated: nothing
    in the universe beats this ticker on both axes at once."""
    counts: dict[str, int] = {}
    for ticker, (leadership, opportunity) in scores.items():
        dominated_by = 0
        for other_ticker, (other_leadership, other_opportunity) in scores.items():
            if other_ticker == ticker:
                continue
            weakly_better = other_leadership >= leadership and other_opportunity >= opportunity
            strictly_better = other_leadership > leadership or other_opportunity > opportunity
            if weakly_better and strictly_better:
                dominated_by += 1
        counts[ticker] = dominated_by
    return counts


def rank_universe(
    closes: dict[str, pd.Series],
    labels: dict[str, str],
    benchmark_close: pd.Series | None = None,
) -> RotationTable:
    """Rank every ticker in `closes` by peer/benchmark-blended leadership
    and opportunity. `closes` and `labels` share keys; `benchmark_close`
    is optional (omit to rank purely on peer-relative + absolute reads).

    Raises ValueError with fewer than 2 tickers -- peer-relative leadership
    is undefined with no peers. Propagates regression_profile's ValueError
    for any ticker with insufficient history rather than silently excluding
    it from the peer average, which would bias every other ticker's score
    on whichever tickers happened to fail.
    """
    tickers = list(closes)
    if len(tickers) < 2:
        raise ValueError("rank_universe needs at least 2 tickers to compute peer-relative leadership")

    absolute_profiles = {t: regression_profile(closes[t]) for t in tickers}

    pair_signals: dict[str, dict[str, float]] = {t: {} for t in tickers}
    for numerator in tickers:
        for denominator in tickers:
            if numerator == denominator:
                continue
            ratio = aligned_ratio(closes[numerator], closes[denominator])
            pair_signals[numerator][denominator] = regression_profile(ratio).trend_signal

    benchmark_profiles = {}
    if benchmark_close is not None:
        for ticker in tickers:
            ratio = aligned_ratio(closes[ticker], benchmark_close)
            benchmark_profiles[ticker] = regression_profile(ratio)

    unsorted: list[dict] = []
    for ticker in tickers:
        absolute = absolute_profiles[ticker]
        peer_signals = [pair_signals[ticker][other] for other in tickers if other != ticker]
        peer_leadership = _leadership_score(sum(peer_signals) / len(peer_signals))

        benchmark_profile = benchmark_profiles.get(ticker)
        benchmark_leadership = (
            _leadership_score(benchmark_profile.trend_signal) if benchmark_profile else NEUTRAL_LEADERSHIP
        )
        absolute_leadership = _leadership_score(absolute.trend_signal)
        leadership = (
            PEER_LEADERSHIP_WEIGHT * peer_leadership
            + BENCHMARK_LEADERSHIP_WEIGHT * benchmark_leadership
            + ABSOLUTE_LEADERSHIP_WEIGHT * absolute_leadership
        )

        benchmark_opportunity = benchmark_profile.opportunity if benchmark_profile else absolute.opportunity
        opportunity = (
            ABSOLUTE_OPPORTUNITY_WEIGHT * absolute.opportunity
            + BENCHMARK_OPPORTUNITY_WEIGHT * benchmark_opportunity
        )
        joint = 2 * leadership * opportunity / max(leadership + opportunity, 1e-9)

        unsorted.append(
            {
                "ticker": ticker,
                "name": labels.get(ticker, ticker),
                "leadership": leadership,
                "opportunity": opportunity,
                "joint": joint,
                "peer_leadership": peer_leadership,
                "benchmark_leadership": benchmark_leadership,
                "absolute_leadership": absolute_leadership,
                "absolute_opportunity": absolute.opportunity,
                "benchmark_opportunity": benchmark_opportunity,
            }
        )

    dominance = _pareto_dominated_by({e["ticker"]: (e["leadership"], e["opportunity"]) for e in unsorted})
    ordered = sorted(
        unsorted,
        key=lambda e: (-e["joint"], dominance[e["ticker"]], -e["leadership"], -e["opportunity"]),
    )
    ranks = [
        RotationRank(
            rank=i + 1,
            ticker=e["ticker"],
            name=e["name"],
            leadership=e["leadership"],
            opportunity=e["opportunity"],
            joint=e["joint"],
            peer_leadership=e["peer_leadership"],
            benchmark_leadership=e["benchmark_leadership"],
            absolute_leadership=e["absolute_leadership"],
            absolute_opportunity=e["absolute_opportunity"],
            benchmark_opportunity=e["benchmark_opportunity"],
            pareto_dominated_by=dominance[e["ticker"]],
        )
        for i, e in enumerate(ordered)
    ]
    return RotationTable(ranks=ranks, pair_signals=pair_signals)
