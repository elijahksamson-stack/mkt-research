"""
Cross-referencing two series: how does one affect the other.

Used to relate HY credit spreads, rates, and the USD index (all FRED level
series) to S&P 500 price action — correlation and beta of period-over-period
changes, plus lead-lag cross-correlation to see whether one series tends to
move ahead of the other. Pure math, no I/O.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

DEFAULT_MIN_OBSERVATIONS = 20


def to_changes(series: pd.Series, method: str = "diff") -> pd.Series:
    """Turn a level series into a stationary period-over-period change series.

    method="diff": simple difference — the market convention for yields,
      spreads (in bps), and index levels.
    method="log_return": log return — the convention for prices, since it
      makes percentage moves additive and comparable across price levels.
    """
    values = pd.Series(series).dropna().astype(float)
    if method == "diff":
        return values.diff().dropna()
    if method == "log_return":
        values = values[values > 0]
        return np.log(values).diff().dropna()
    raise ValueError(f"Unknown method: {method!r} (expected 'diff' or 'log_return')")


def align(a: pd.Series, b: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Inner-join two series on their index; return aligned numpy arrays."""
    df = pd.concat(
        [pd.Series(a).rename("a"), pd.Series(b).rename("b")], axis=1, join="inner"
    ).dropna()
    return df["a"].to_numpy(), df["b"].to_numpy()


def _aligned_changes(
    a: pd.Series, b: pd.Series, method_a: str, method_b: str
) -> tuple[pd.Series, pd.Series]:
    """Align `a` and `b` on their shared dates BEFORE differencing.

    Diffing each series independently on its own index (as to_changes alone
    does) and only aligning the resulting changes afterward lets a calendar
    mismatch — e.g. a FRED series skipping a bond-market-only holiday that
    the equity benchmark trades through — silently pair a two-day change on
    one side with a one-day change on the other. Aligning the levels first
    guarantees both sides' diffs are always computed over identical,
    corresponding date spans.
    """
    joint = pd.concat(
        [pd.Series(a).rename("a"), pd.Series(b).rename("b")], axis=1, join="inner"
    ).dropna()
    return to_changes(joint["a"], method_a), to_changes(joint["b"], method_b)


def pearson_correlation(
    xs, ys, min_observations: int = DEFAULT_MIN_OBSERVATIONS
) -> Optional[float]:
    n = min(len(xs), len(ys))
    if n < min_observations:
        return None
    xs = np.asarray(xs[:n], dtype=float)
    ys = np.asarray(ys[:n], dtype=float)
    mx, my = xs.mean(), ys.mean()
    vx = float(((xs - mx) ** 2).sum())
    vy = float(((ys - my) ** 2).sum())
    if vx == 0 or vy == 0:
        return None
    cov = float(((xs - mx) * (ys - my)).sum())
    return cov / np.sqrt(vx * vy)


def beta_of(
    xs, ys, min_observations: int = DEFAULT_MIN_OBSERVATIONS
) -> Optional[float]:
    """Beta of `ys` on `xs`: the OLS slope of ys regressed on xs (how many
    units ys moves per unit move in xs)."""
    n = min(len(xs), len(ys))
    if n < min_observations:
        return None
    xs = np.asarray(xs[:n], dtype=float)
    ys = np.asarray(ys[:n], dtype=float)
    mx, my = xs.mean(), ys.mean()
    var_x = float(((xs - mx) ** 2).sum())
    if var_x == 0:
        return None
    cov = float(((xs - mx) * (ys - my)).sum())
    return cov / var_x


def correlate_series(
    a: pd.Series,
    b: pd.Series,
    method_a: str = "diff",
    method_b: str = "log_return",
    min_observations: int = DEFAULT_MIN_OBSERVATIONS,
) -> dict:
    """Contemporaneous correlation + beta of b's changes on a's changes."""
    ca, cb = _aligned_changes(a, b, method_a, method_b)
    xs, ys = align(ca, cb)
    n = min(len(xs), len(ys))
    if n < min_observations:
        return {
            "error": f"insufficient overlapping observations ({n} < {min_observations})"
        }
    corr = pearson_correlation(xs, ys, min_observations)
    if corr is None:
        return {"error": "zero variance in one or both change series — cannot correlate"}
    beta = beta_of(xs, ys, min_observations)
    return {
        "observations": int(min(len(xs), len(ys))),
        "correlation": round(float(corr), 3),
        "r_squared": round(float(corr) ** 2, 3),
        "beta": round(float(beta), 4) if beta is not None else None,
        "method_a": method_a,
        "method_b": method_b,
    }


def lead_lag_correlation(
    a: pd.Series,
    b: pd.Series,
    max_lag: int = 10,
    method_a: str = "diff",
    method_b: str = "log_return",
    min_observations: int = DEFAULT_MIN_OBSERVATIONS,
) -> dict:
    """Cross-correlation of a's change at t against b's change at t+lag, for
    lag in [-max_lag, max_lag]. Positive lag means a leads b (a's move today
    is associated with b's move `lag` periods later).
    """
    ca, cb = _aligned_changes(a, b, method_a, method_b)
    df = pd.concat([ca.rename("a"), cb.rename("b")], axis=1, join="inner").dropna()

    correlations: dict[int, Optional[float]] = {}
    for lag in range(-max_lag, max_lag + 1):
        shifted_b = df["b"].shift(-lag)
        paired = pd.concat([df["a"], shifted_b], axis=1).dropna()
        corr = pearson_correlation(
            paired.iloc[:, 0].to_numpy(), paired.iloc[:, 1].to_numpy(), min_observations
        )
        correlations[lag] = round(float(corr), 3) if corr is not None else None

    valid = {lag: c for lag, c in correlations.items() if c is not None}
    if valid:
        best_lag = max(valid, key=lambda lag: abs(valid[lag]))
        best_correlation = valid[best_lag]
    else:
        best_lag, best_correlation = None, None

    return {
        "correlations_by_lag": correlations,
        "best_lag": best_lag,
        "best_correlation": best_correlation,
    }


def cross_reference_report(
    a: pd.Series,
    b: pd.Series,
    name_a: str = "Series A",
    name_b: str = "Series B",
    method_a: str = "diff",
    method_b: str = "log_return",
    max_lag: int = 10,
    min_observations: int = DEFAULT_MIN_OBSERVATIONS,
) -> dict:
    """Bundle contemporaneous correlation/beta with lead-lag analysis for a
    named pair of series."""
    return {
        "name_a": name_a,
        "name_b": name_b,
        "contemporaneous": correlate_series(
            a, b, method_a, method_b, min_observations
        ),
        "lead_lag": lead_lag_correlation(
            a, b, max_lag, method_a, method_b, min_observations
        ),
    }
