# Equities/equity-rotation

Python toolkit for rotation *within* the US equity market: which sectors
and which style factors are currently leading, and how much room each has
left to run, plus an RRG-style (Relative Rotation Graph) relative-technicals
read output as plain data instead of a chart.

Ported and reformed from a standalone sector-rotation script (peer/
benchmark-blended leadership+opportunity ranking with Pareto-dominance
filtering), extended with a new relative-technicals model. Deliberately
self-contained -- no dependency on `Macro/Rates` or `Macro/market-structure`,
even though `trend_regression.py`'s HAC-log-regression math is a documented
intentional duplicate of `Macro/Rates/rates_macro/trend_rr.py` (see that
module's docstring for why, and where to look if the formula needs retuning
in both places).

Sibling of `Equities/sector-lvl-expertise` (qualitative, per-industry MCP)
-- this package is the quantitative half. Both are meant to roll up into a
single Blog-level MCP eventually; neither wraps itself as an MCP yet (plain
importable Python, run via `uv run`, matching `Macro/market-structure`'s
convention).

## Setup

```bash
cd Equities/equity-rotation
uv sync              # installs deps (pandas/numpy/scipy/yfinance + pytest)
uv run pytest -q     # 65 tests, all pure-math / monkeypatched-network, no live calls
```

## Entry point

```bash
uv run python -m equity_rotation.report
```

Fetches the default universe (11 SPDR sector ETFs + 6 style-factor ETFs,
see `universe.py`) vs. SPY via yfinance, and prints three plain-text
tables: sector rotation ranking, factor rotation ranking, and a combined
RRG-style relative-technicals table. `report.build_report(universe=...)`
takes a custom `{ticker: name}` dict to run a smaller/different set.

## Module map -- read in this order to understand the pipeline

1. **`universe.py`** -- the two independently-scored tiers (11 sector ETFs,
   6 factor ETFs) and the benchmark (SPY). Deliberately excludes broad
   indexes (SPY/QQQ/IWM/DIA/MDY) -- that market-vs-macro read already
   lives in `Macro/market-structure`'s gauge; this package's job is the
   layer beneath it, rotation *within* the equity market.
2. **`trend_regression.py`** -- HAC (Newey-West) log-linear trend
   regression + AR(1) forecast + residual-channel model for a single
   series (price, or a relative-strength ratio). Self-contained duplicate
   of `rates_macro.trend_rr` by design (see module docstring).
3. **`relative_strength.py`** -- `aligned_ratio()`: the relative-strength
   ratio line every cross-sectional read is built from. Small and pure.
4. **`rotation_ranking.py`** -- **the genuinely novel core.** Peer/
   benchmark-blended Leadership + Opportunity scores, Pareto-dominance
   filtering. Reformed from the original script's DataFrame-mutation
   chain into pure functions over frozen dataclasses (`RotationRank`,
   `RotationTable`) -- no `.sort_values()`/`.insert()` in place.
5. **`relative_technicals.py`** -- **new model**, answers "relative
   technicals at the index/sector/factor level, data only, no graphs."
   RRG-style RS-Ratio (level) + RS-Momentum (rate of change) -> quadrant
   classification (leading/weakening/lagging/improving), plus supporting
   ratio-vs-its-own-50/200dma and relative-volatility reads. Every formula
   is specified in the module docstring -- there's no single "official"
   RRG formula, so this is an original, auditable normalization, not a
   reproduction of a proprietary one.
6. **`market_data.py`** -- batch yfinance OHLCV fetch + quality gate
   (bars, coverage, staleness, median-dollar-volume liquidity floor). The
   only I/O module; everything above is pure math and fully
   offline-testable. `_download_chunk` is the mockable network boundary.
7. **`report.py`** -- top-level orchestration + CLI entry point.
   `render_summary()` prints exactly the fields the modules above
   computed -- nothing derived only for display. Per-ticker fetch/
   analysis failures are isolated into a `dropped` list rather than
   sinking the whole report, matching `market-structure`'s convention.

## Conventions

- Pure math modules take numpy/pandas and do no I/O -- only
  `market_data.py` touches the network. Keep new analysis logic in that
  offline-testable style.
- Dataclasses are `frozen=True` throughout (immutability per the user's
  global coding-style rules). No DataFrame `.sort_values()`/mutation
  chains in the math layer -- sort in plain Python over dataclasses;
  DataFrames are for the display layer (`report.py`) only.
- Tests mirror the module list 1:1 (`tests/test_<module>.py`), pytest
  classes named `Test<Thing>`, synthetic data built with
  `np.random.default_rng(seed)` for determinism. Network calls are
  monkeypatched at the `_download_chunk`/`fetch_universe` boundary, never
  hit live in tests.
- Sector and factor tiers are scored *independently*, never blended into
  one composite number -- "which sector is leading" and "is the market
  rewarding growth or value" are different questions, and conflating them
  would hide which one is actually moving.

## Known validation

Live-checked 2026-07-17: sector ranking put **XLK (Technology)** first
(Joint 72.7, Pareto-undominated) and **MTUM (Momentum)** first among
factors (Joint 71.3, Pareto-undominated) -- consistent with the original
script's own live run on the same data. The relative-technicals table
adds a read the ranking alone can't show: despite leading on the
medium/long-horizon regression, XLK's RRG quadrant was **lagging**
(RS-Momentum 96.9, below the 100 line) -- its near-term relative strength
vs. SPY was fading even as its longer trend still led. That's the
intended non-redundant signal between the two models, not a bug.
