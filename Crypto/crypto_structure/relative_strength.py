"""
Peer/benchmark relative-strength ranking — "which crypto asset is leading,
and which has the most room left to run" — generalizing the sector-ETF
ranking script (Leadership/Opportunity/Joint, Pareto-dominance tie-break)
onto crypto_structure.trend_rr.trend_rr_profile instead of duplicating that
script's own inline HAC-regression code.

Three ingredients per asset, exactly mirroring the equity script's design:
  - peer leadership: mean pairwise trend_signal of asset/other ratio series
    across every OTHER asset in the universe -- "is this asset outperforming
    its peers broadly, not just one rival."
  - benchmark leadership: trend_signal of asset/BENCHMARK (BTC-USD by
    default) -- "is this asset outperforming the market itself."
  - absolute leadership: trend_signal of the asset's own raw close series --
    "is this asset trending up in dollar terms, independent of anything
    else." Included at a low weight per the equity script's own design,
    since a rising tide (a broad crypto bull market) would otherwise get
    mistaken for asset-specific leadership.
  leadership = 0.60*peer + 0.25*benchmark + 0.15*absolute   (0-100 scale)

Opportunity blends the asset's own regression-implied reward/asymmetry with
the same read on its benchmark-relative ratio series:
  opportunity = 0.65*absolute_opportunity + 0.35*benchmark_opportunity

joint = harmonic mean of leadership and opportunity (rewards assets strong
on BOTH axes over one that maxes a single axis). ParetoDominatedBy counts
how many other assets weakly dominate an asset on both axes -- a
non-parametric "how many strictly better alternatives exist" tie-break,
ranked ascending (0 dominators = not dominated by anyone = best).

The benchmark asset itself (BTC-USD ranked against BTC-USD) is a
degenerate self-ratio (constant 1.0, R^2=0 by construction) -- handled by
scoring its benchmark_leadership as neutral (50) rather than letting a
zero-variance regression silently distort its rank.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from crypto_structure.trend_rr import trend_rr_profile

PEER_WEIGHT = 0.60
BENCHMARK_WEIGHT = 0.25
ABSOLUTE_LEADERSHIP_WEIGHT = 0.15

ABSOLUTE_OPPORTUNITY_WEIGHT = 0.65
BENCHMARK_OPPORTUNITY_WEIGHT = 0.35

NEUTRAL_SCORE = 50.0


def aligned_ratio(series_a: pd.Series, series_b: pd.Series) -> pd.Series:
    """Numerator/denominator ratio over their overlapping, positive-valued
    dates only -- the ratio series a relative-strength trend is fit
    against."""
    pair = pd.concat([series_a, series_b], axis=1, join="inner").dropna()
    pair = pair[(pair.iloc[:, 0] > 0) & (pair.iloc[:, 1] > 0)]
    return pair.iloc[:, 0] / pair.iloc[:, 1]


def pareto_dominated_by(table: pd.DataFrame) -> list[int]:
    """For each row, count how many OTHER rows weakly dominate it on both
    Leadership and Opportunity (>= on both, > on at least one). Fewer
    dominators is better; 0 means no asset in the table beats this one on
    both axes simultaneously."""
    leadership = table["Leadership"].to_numpy()
    opportunity = table["Opportunity"].to_numpy()
    counts = []
    for i in range(len(table)):
        dominates = (
            (leadership >= leadership[i])
            & (opportunity >= opportunity[i])
            & ((leadership > leadership[i]) | (opportunity > opportunity[i]))
        )
        counts.append(int(dominates.sum()))
    return counts


def _safe_profile(series: pd.Series) -> Optional[dict]:
    try:
        return trend_rr_profile(series)
    except ValueError:
        return None


def rank_universe(
    closes: dict[str, pd.Series],
    labels: dict[str, str],
    benchmark_ticker: Optional[str] = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Rank every ticker in `closes` by Leadership (relative strength vs.
    peers + benchmark) and Opportunity (regression-implied reward), mirror
    of the equity sector-rotation script's rank_universe. `closes` maps
    ticker -> a close-price pd.Series (DatetimeIndex); `labels` maps ticker
    -> display name; `benchmark_ticker` must be a key of `closes` if given.

    Returns (ranked_table, pair_signals) where pair_signals[a][b] is the
    trend_signal of a/b's ratio series (the peer matrix, exposed for
    callers that want the full pairwise detail, not just the aggregate
    leadership score).
    """
    tickers = list(closes)
    if len(tickers) < 2:
        raise ValueError("rank_universe needs at least 2 tickers to compute peer-relative signals")

    absolute_profiles = {t: _safe_profile(closes[t]) for t in tickers}

    pair_signals = pd.DataFrame(0.0, index=tickers, columns=tickers)
    for numerator in tickers:
        for denominator in tickers:
            if numerator == denominator:
                continue
            ratio = aligned_ratio(closes[numerator], closes[denominator])
            profile = _safe_profile(ratio)
            pair_signals.loc[numerator, denominator] = profile["trend_signal"] if profile else 0.0

    rows = []
    for ticker in tickers:
        absolute = absolute_profiles[ticker]
        peers = [t for t in tickers if t != ticker]
        peer_leadership = (
            NEUTRAL_SCORE + 50.0 * float(pair_signals.loc[ticker, peers].mean()) if peers else NEUTRAL_SCORE
        )

        if benchmark_ticker and benchmark_ticker in closes and benchmark_ticker != ticker:
            benchmark_profile = _safe_profile(aligned_ratio(closes[ticker], closes[benchmark_ticker]))
        else:
            # The benchmark ranked against itself is a degenerate constant
            # ratio -- score it neutral rather than letting a zero-variance
            # regression distort its own rank.
            benchmark_profile = None
        benchmark_leadership = NEUTRAL_SCORE + 50.0 * benchmark_profile["trend_signal"] if benchmark_profile else NEUTRAL_SCORE

        absolute_leadership = NEUTRAL_SCORE + 50.0 * absolute["trend_signal"] if absolute else NEUTRAL_SCORE
        leadership = (
            PEER_WEIGHT * peer_leadership
            + BENCHMARK_WEIGHT * benchmark_leadership
            + ABSOLUTE_LEADERSHIP_WEIGHT * absolute_leadership
        )

        absolute_opportunity = absolute["opportunity"] if absolute else NEUTRAL_SCORE
        benchmark_opportunity = benchmark_profile["opportunity"] if benchmark_profile else absolute_opportunity
        opportunity = (
            ABSOLUTE_OPPORTUNITY_WEIGHT * absolute_opportunity + BENCHMARK_OPPORTUNITY_WEIGHT * benchmark_opportunity
        )

        joint = 2 * leadership * opportunity / max(leadership + opportunity, 1e-9)

        rows.append(
            {
                "Ticker": ticker,
                "Name": labels.get(ticker, ticker),
                "Leadership": leadership,
                "Opportunity": opportunity,
                "Joint": joint,
                "PeerLeadership": peer_leadership,
                "BenchmarkLeadership": benchmark_leadership,
                "AbsoluteLeadership": absolute_leadership,
                "AbsoluteOpportunity": absolute_opportunity,
                "BenchmarkOpportunity": benchmark_opportunity,
                "TrendSignal": absolute["trend_signal"] if absolute else 0.0,
            }
        )

    ranked = pd.DataFrame(rows).set_index("Ticker")
    ranked["ParetoDominatedBy"] = pareto_dominated_by(ranked)
    ranked = ranked.sort_values(
        ["Joint", "ParetoDominatedBy", "Leadership", "Opportunity"],
        ascending=[False, True, False, False],
    )
    ranked.insert(0, "Rank", np.arange(1, len(ranked) + 1))
    return ranked, pair_signals
