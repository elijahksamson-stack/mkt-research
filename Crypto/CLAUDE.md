# Crypto/crypto-structure

Python toolkit that ports the risk:reward + trendline-discovery methodology
documented in `/Users/elisamson/Desktop/wisdom/rr.txt` (originally built for
equities in the sibling `Macro/market-structure` project) and the HAC
log-regression trend model from `Macro/Rates/rates_macro/trend_rr.py`
(originally built for the sector-ETF leadership/opportunity script pasted
into this project's founding request), and adapts both **specifically for
the crypto market**: a 24/7/365 trading calendar, a curated large-cap
ticker universe, and a peer/BTC-benchmark relative-strength ranking. No MCP
wrapper — plain, importable Python, run via `uv run`.

Fully self-contained (no path dependency on the `Macro/` siblings) — every
module that's asset-agnostic pure math was ported verbatim; only
`trend_rr.py`, `market_data.py`, `universe.py`, and the two new modules
(`relative_strength.py`, `crypto_gauge.py`) contain crypto-specific
adaptation. See each module's docstring for exactly what changed and why.

## Setup

```bash
cd Crypto
uv sync              # installs deps (pandas, numpy, scipy, yfinance, pytest)
uv run pytest -q     # 140 tests, all pure-math / monkeypatched-network, no live calls
```

## Entry point

```bash
uv run python -m crypto_structure.report
```

Fetches the default universe (BTC + ETH + 16 large-cap alts, see
`universe.py`) via one batched yfinance call, runs the full risk:reward
pipeline per asset, ranks every asset by peer/BTC-benchmark leadership and
regression-implied opportunity, and prints the market risk gauge + ranking
table + per-asset blurbs. `report.build_report(universe=...)` takes a
custom `{ticker: name}` dict to run a smaller/different set (tickers must
be yfinance's `<SYMBOL>-USD` crypto format).

## Module map — read in this order to understand the pipeline

Each pure-math module's docstring cites which Part of `rr.txt` it ports;
start there if a formula looks unfamiliar. The three "crypto-adapted"
modules explain their specific deviation from the equity/macro source in
their own docstrings.

1. **`indicators.py`** *(verbatim port)* — ATR / realized vol / relative
   volume / recency-weighted swing pivots. (rr.txt Parts 2-3)
2. **`levels.py`** *(verbatim port)* — the six independent level-detection
   methods + convergence clustering. (rr.txt Parts 4, 6)
3. **`trendlines.py`** *(verbatim port)* — both trendline families:
   quantile-regression (global) and pivot-pair (segment-specific). (rr.txt
   Part 5)
4. **`trend_violation.py`** *(verbatim port)* — detects when price has
   closed below its own most relevant rising support line, a gap in rr.txt's
   original methodology that a still-positive R:R snapshot can miss.
5. **`fib_extension.py`** *(verbatim port)* — ATH/no-overhead reward
   projection. (rr.txt Part 7)
6. **`stop_target.py`** *(verbatim port)* — the 4-tier stop/target fallback
   (cluster → trendline → fib_extension → synthetic) with `target_source`
   attribution. (rr.txt Part 8)
7. **`risk_reward.py`** *(verbatim port)* — orchestrates 1-6 into one
   `RiskRewardReport` per asset. `analyze(ticker, high, low, close, volume)
   -> RiskRewardReport`. This is the module that answers "RR on all crypto
   assets" — call it once per ticker in the universe.
8. **`trend_rr.py`** *(crypto-adapted)* — HAC (Newey-West) log-regression
   trend + opportunity model. Windows are calendar-day equivalents
   (30/91/182/365 for ~1mo/3mo/6mo/1yr) and annualization uses
   `PERIODS_PER_YEAR=365` instead of equities' 252 trading days — crypto
   trades every calendar day, so 252 would understate annualized growth by
   roughly 31%. Works on any positive series, including ratio series (feeds
   `relative_strength.py`'s peer/benchmark ranking as well as each asset's
   own absolute trend signal).
9. **`relative_strength.py`** *(new)* — the "relative trend indications"
   deliverable: generalizes the pasted equity sector-rotation script's
   `rank_universe`/Leadership/Opportunity/Pareto-dominance logic onto
   `trend_rr.trend_rr_profile`, ranking every crypto asset by peer-relative
   + BTC-benchmark-relative trend strength and regression-implied
   opportunity. `rank_universe(closes, labels, benchmark_ticker) ->
   (ranked_table, pair_signals)`.
10. **`market_data.py`** *(crypto-adapted)* — yfinance OHLCV fetch + quality
    gate, adapted for a 24/7 market: `MAX_STALENESS_DAYS` tightened from 10
    to 3 (no weekend gap to allow for), plus a `MIN_MEDIAN_DOLLAR_VOLUME`
    liquidity gate the equity sibling doesn't need (it only ever fetches
    obviously-liquid index/sector ETFs). Adds `download_universe()`, a
    batched multi-ticker fetch for the relative-strength ranking.
11. **`crypto_gauge.py`** *(crypto-adapted)* — combines `RiskRewardReport` +
    a `trend_rr` trend signal into a per-asset 0-100 risk score, the overall
    weighted gauge, and a risk-off read (renamed from the equity sibling's
    "cash on sidelines" — crypto has no literal cash-on-sidelines concept;
    the formula is unchanged, only the label). Every term of the scoring
    formula is a public dataclass field, and `FORMULA_LEGEND` is generated
    from the same constants used to compute it.
12. **`report.py`** *(new orchestration)* — top-level CLI entry point.
    `render_summary()` prints the formula legend, the leadership/opportunity
    ranking table, then per-asset the exact trend/rr/violation contributions,
    support cluster stack, and trendline detail — no term of any score is
    implicit.
13. **`universe.py`** *(crypto-specific)* — MAJORS (BTC, ETH — the
    market-defining tier and `BENCHMARK_TICKER` for relative-strength
    ranking) + ALTCOINS (16 liquid large-caps), and `composite_weights()`
    (60/40 majors/altcoins split, renormalized to whatever subset is
    actually available).

## Conventions

- Pure math modules take numpy arrays / dataclasses and do no I/O — only
  `market_data.py` touches the network. Keep new analysis logic in that
  offline-testable style.
- Dataclasses are `frozen=True` throughout (immutability per the user's
  global coding-style rules).
- Tests mirror the module list 1:1 (`tests/test_<module>.py`), pytest
  classes named `Test<Thing>`, synthetic data built with
  `np.random.default_rng(seed)` for determinism. Network calls are
  monkeypatched at the `_download`/`_download_batch`/`download_universe`
  boundary, never hit live in tests.
- If `rr.txt` changes, re-distill the affected pure-math module from it —
  the docstrings say exactly which Part each function ports.
- Crypto ticker format is yfinance's `<SYMBOL>-USD` (e.g. `BTC-USD`).
