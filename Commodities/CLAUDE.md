# Macro/Commodities

Statistical ranking + forecasting module for the commodity futures universe
(energy, precious metals, industrial metals, agriculture, livestock): a
calibrated probability of a near-term price increase, expected return,
downside quantile, and cross-commodity relative strength for each commodity
— built on `yfinance` futures data (`GC=F`-style continuous series plus
dated contract symbols for curve/carry) and wired to two reused engines
from the sibling `Macro/market-structure` project rather than reimplementing
trend or trade-geometry logic. No MCP wrapper, no web UI — plain, importable
Python, run via `uv run`, following `market-structure`'s own conventions.

Sibling of `Macro/market-structure` and `Macro/Rates` (same `uv` + pytest
conventions). Both are reused as editable path dependencies (see
`pyproject.toml`'s `[tool.uv.sources]`):

- `market_structure.risk_reward` — the existing **Risk/Reward** engine
  (recency-weighted pivots, six-method convergence clustering, dual
  trendline families, ATR/HV/rvol-adjusted stop/target tiering,
  trend-violation detection). Reused unchanged via `risk_reward_adapter.py`.
- `rates_macro.trend_rr` — the existing **Trend Analysis** engine
  (multi-window HAC log-regression, forecast/channel-asymmetry blend).
  Reused unchanged via `trend_adapter.py` and also inside `momentum.py`
  (pair-ratio trends) and `macro_controls.py` (macro-series trends).

## Setup

```bash
cd Commodities
uv sync              # installs deps incl. the market-structure + rates-macro path dependencies
uv run pytest -q     # 57 tests, pure-math / synthetic-data, no live network calls
```

## Entry point

```bash
uv run python -m commodities.report --horizon 1M --detail 5
```

Fetches the full 25-commodity universe (`universe.py`), builds the
point-in-time feature matrix, fits one direction/magnitude/quantile model
set per horizon on the historical panel, applies it to today's data, and
prints the ranked table + detail panels. `--horizon` accepts `1W`/`1M`/`3M`
(5/21/63 trading days); `--detail N` controls how many top-ranked
commodities get a full narrative breakdown. `report.build_report(universe=...)`
takes a custom `{canonical_id: CommodityInstrument}` dict to run a
smaller/different set — useful for fast iteration, since the full universe
walk-forward fit takes several minutes (see Performance below).

## Section 1 audit — what was reused, generalized, or built new

Required before any implementation, per the spec. Findings:

- **Reused unchanged**: `market_structure.risk_reward.analyze()` (trade
  geometry) and `rates_macro.trend_rr.{hac_log_regression,trend_rr_profile,
  mean_reversion_snapshot}` (trend analysis). Neither was modified — both
  are called with the same signatures their own test suites exercise.
- **Reused as infrastructure**: `market_structure.market_data.fetch_ohlcv`
  (continuous OHLCV + quality gate) and `market_structure.indicators.
  average_true_range` (reused inside `mean_reversion.py`'s displacement
  calc, avoiding a second ATR implementation).
- **Generalized from equities to commodities**: none of the reused engines
  needed modification to run on futures continuous series — they operate
  on plain OHLCV arrays and don't assume an equity-specific structure. What
  *did* need building from scratch was everything equities don't have:
  contract-month cycles, curve/carry, roll-adjustment, and CFTC positioning.
- **Missing and built new**: canonical commodity universe with roll-aware
  data contracts (`universe.py`, `contracts.py`, `market_data.py`), the five
  new signal families (`momentum.py`, `curve_carry.py`, `mean_reversion.py`,
  `positioning.py`, `seasonality.py`, `macro_controls.py`), the statistical
  framework (`models.py`, `validation.py`), and the ranking/report layer
  (`ranking.py`, `report.py`).
- **Different assumptions futures introduce vs. equities**: no dividends/
  splits (so `auto_adjust=True` is a no-op, unlike for equities); price
  series are per-contract, not per-issuer, so a "ticker" is really a family
  of expiring contracts requiring roll handling; there's a real term
  structure (curve/carry) with no equity analogue; and positioning data
  (CFTC COT) exists for futures with no equivalent for single stocks.

## Module map — read in this order to understand the pipeline

1. **`universe.py`** — canonical commodity registry (25 instruments, 5
   families), yfinance continuous symbol + CFTC market name per commodity,
   `CANONICAL_PAIRS` for pair-ratio analysis. Uranium is carried as an ETF
   proxy (`URA`, `is_tradable_future=False`) since no uranium futures series
   exists on yfinance (verified: `UX=F` returns no data).
2. **`contracts.py`** — turns `(root, exchange_suffix, valid_months)` +
   an as-of date into dated-contract symbols (`GCZ26.CMX`) for curve/carry.
   `valid_months` are real exchange delivery-month cycles, live-verified
   against yfinance during this build, not guessed.
3. **`market_data.py`** — re-exports `market_structure.market_data.
   fetch_ohlcv` for continuous series (risk_reward/trend inputs), adds
   **ratio-back-adjustment** (`build_roll_adjusted_close`) for return-based
   modeling, and dated-contract fetch for curve/carry. Read this module's
   docstring closely — it documents a confirmed Yahoo Finance limitation
   that materially shapes how curve/carry can be used (see Limitations).
4. **`trend_adapter.py`** — wraps `rates_macro.trend_rr` for 5/21/63-day
   horizon views plus a `persistence` metric (fraction of 21/63/126/252-day
   regression windows agreeing in sign).
5. **`risk_reward_adapter.py`** — thin wrapper around `market_structure.
   risk_reward.analyze()`; adds only an `actionable` flag (R:R above a
   floor).
6. **`momentum.py`** — absolute/cross-sectional/family-relative/residual
   momentum (vol-scaled realized returns, distinct from the regression-based
   trend signal) + pair-ratio trends (reuses `trend_rr_profile` on the ratio
   series rather than a second trend-fitting method).
7. **`curve_carry.py`** — front/second/third annualized slope, roll yield,
   curvature, contango/backwardation classification, curve-shape change.
8. **`mean_reversion.py`** — Bollinger/ATR displacement gated by an ADF
   stationarity test (only "activates" on a demonstrably range-bound
   series), plus Engle-Granger cointegration restricted to
   `universe.CANONICAL_PAIRS`.
9. **`positioning.py`** — CFTC Disaggregated Futures-Only COT, fetched live
   from `publicreporting.cftc.gov`'s Socrata API, converted to rolling
   z-scores/percentiles with a 3-day publication lag.
10. **`seasonality.py`** — expanding-window calendar-seasonal forward
    returns; a historical instance only counts if its full outcome window
    completed strictly before `as_of`.
11. **`macro_controls.py`** — USD index, real 10Y yield (FRED `DFII10`),
    10Y breakeven inflation (FRED `T10YIE`), broad commodity index
    (`^SPGSCI`), each with a reused `trend_rr_profile` trend read.
12. **`labels.py`** — leakage-safe forward-return labels + the shared
    as-of trading-day grid (`trading_day_grid`) used to build historical
    training rows.
13. **`features.py`** — the integration layer. `fetch_universe_data()`
    fetches everything once; `build_live_bundles()` and
    `build_training_matrix()` assemble point-in-time `FeatureBundle`s for
    "today" and for historical training rows, respectively.
14. **`models.py`** — Elastic-Net logistic (direction, sigmoid-calibrated),
    Huber regression (magnitude), linear quantile regression (downside/
    median/upside) — one `HorizonModelSet` per horizon, all standardized
    inside the same `Pipeline` so coefficients are directly comparable.
    Two naive benchmarks (`naive_constant_probability`, `naive_momentum_rule`).
15. **`validation.py`** — expanding-window walk-forward folds with a
    calendar-day embargo, evaluated with Brier score, log loss, calibration
    error, Spearman IC, top-quintile hit rate/spread, MAE, pinball loss,
    quantile coverage, turnover, and a block-bootstrap CI helper.
16. **`ranking.py`** — trains production model sets on the full historical
    panel, applies them live, and assembles the ten required output fields.
    `commodity_opportunity_score` blends only the model's own three outputs
    (weighted by their own out-of-sample IC) — trend/carry/relative-strength/
    R:R are display fields, not re-added into the score.
17. **`report.py`** — CLI entry point + text rendering (ranked table +
    per-commodity detail panel), the spec's Section 7 product surface.

## Conventions

- Pure-math modules (`contracts.py`, `momentum.py`'s normalization,
  `curve_carry.py`'s slope math, `mean_reversion.py`, `models.py`) take
  arrays/dataclasses and do no I/O, matching `market_structure`'s
  convention. Network I/O lives in `market_data.py`, `positioning.py`,
  `macro_controls.py` only.
- Dataclasses are `frozen=True` throughout (project-wide immutability
  convention).
- Missing data is `None`/`NaN`, never a fabricated neutral value — see
  `features.py`'s "Missing-data policy" docstring. A commodity structurally
  lacking a signal (curve for uranium, cointegration for an unpaired
  commodity) must read as missing in both the feature matrix and the
  report, not as a zero/neutral score.
- Tests mirror the module list for every pure-math module
  (`tests/test_<module>.py`), pytest classes named `Test<Thing>`, synthetic
  data via `np.random.default_rng(seed)`, no live network calls. Modules
  that are pure network I/O with no interesting branching logic of their
  own (`market_data.py`'s `_download`, `positioning.fetch_cot_history`,
  `macro_controls.fetch_fred_series`) are intentionally not unit-tested —
  they were instead live-verified against the real APIs during this build
  (see the field names and sample responses documented in each module's
  docstring).

## Interpretation guidelines

**What each output field means, and its honest confidence level:**

- **`up_probability`** — sigmoid-calibrated `P(forward return > 0)` from
  the Elastic-Net logistic model. Calibration quality (how close a stated
  65% is to a realized 65%) depends entirely on how much historical
  training data was available for that horizon — check `forecast_confidence`
  before trusting an extreme probability from a thin fold.
- **`expected_return`** — Huber-regression point estimate, robust to
  outliers but still a linear model on ~20-80 features. Treat it as a
  *ranking* signal (is this commodity's expected return higher than that
  one's) more than as a literal return forecast — the magnitude can run
  large in a small-universe test and should be sanity-checked against the
  commodity's own realized volatility before being read literally.
- **`downside_quantile`** — the 10th-percentile linear quantile regression
  prediction. This is a *conditional* quantile given today's features, not
  a worst-case guarantee; `quantile_coverage` in `validation.py`'s output
  is the diagnostic for whether it's actually tracking a 10% exceedance
  rate out-of-sample.
- **`relative_return_rank`** — a pure cross-sectional percentile of
  `expected_return` at the primary (21d) horizon. Only meaningful relative
  to the other commodities in the same run — it says nothing about
  absolute attractiveness.
- **`trend_score` / `carry_score` / `relative_strength_score` / `risk_reward`**
  — display/diagnostic fields, already consumed as model *inputs*
  upstream. Do not re-weight them into a personal "final score" on top of
  `commodity_opportunity_score` — that's exactly the "arbitrary bonus
  points" the spec warns against, and doing so double-counts information
  the model already used.
- **`forecast_confidence`** — a measured quality signal (calibration error
  + sample coverage + cross-horizon direction agreement), not a measure of
  how extreme the forecast looks. A commodity with `up_probability=0.95`
  and low `forecast_confidence` is a *less* trustworthy call than one with
  `up_probability=0.65` and high confidence.
- **`commodity_opportunity_score`** — the final rank driver. A high score
  means the model's calibrated direction/magnitude/downside views are
  jointly favorable *and* well-supported; it is not a buy signal on its
  own. Always read it alongside the risk/reward detail (entry/stop/target,
  `actionable`) before treating it as a trade idea — a top-ranked commodity
  with `actionable=False` has no attractive entry at the current price
  regardless of the forecast.

**On statistical rigor**: this is a genuinely fitted linear ensemble
(Elastic-Net / Huber / quantile regression), not a lookup table or a
disguised technical composite, and `validation.py`'s walk-forward harness
is real (embargo gap, calibration held out chronologically, naive
benchmarks always computed alongside the model). But treat any single run's
numbers as provisional until `validation.run_walk_forward` has been run for
that horizon and its Brier score / IC / calibration error have been checked
against the naive benchmarks — a model that doesn't beat
`naive_constant_probability` and `naive_momentum_rule` on out-of-sample
folds should not be trusted for ranking, however plausible its live output
looks.

## Known limitations (confirmed during this build, not speculative)

- **Curve/carry is effectively live-only.** Confirmed via live requests:
  Yahoo Finance only serves history for dated-contract symbols currently
  among a product's near listed months. An expired, rolled-off contract
  returns empty data for *any* requested date range, even dates during its
  real trading life (e.g. `GCQ25.CMX` returns 0 rows even when queried for
  2024-07-30..2025-07-31, squarely inside when it was trading). Practically,
  `build_training_matrix` defaults `include_curve=False` — historical
  curve/carry training coverage is sparse-to-empty across most of a
  multi-year window, while `build_live_bundles` ("today") gets full
  coverage. If backtesting `carry_score` specifically becomes a priority,
  the fix is a dedicated futures-history vendor (CME DataMine, Nasdaq Data
  Link, Barchart), not more retries against yfinance.
- **Roll-adjustment is a documented approximation.** `build_roll_adjusted_close`
  detects roll jumps via a robust-z threshold on daily returns near a
  contract-month boundary (no open-interest series is available from
  yfinance to detect the true roll date), then ratio-back-adjusts around
  them. This can mis-time a roll for a product whose actual roll happens
  unusually early or late in the month. Cross-checked during this build:
  1-3 roll events detected per commodity per 2-year window, directionally
  consistent with real roll frequency, but not exact.
- **Contract-month "front" selection is a heuristic**, not driven by real
  open-interest data (`contracts.py`'s `ROLL_BUFFER_MONTHS`) — it can be a
  few trading days off from what a desk would call front month right at a
  roll.
- **CFTC lag is a fixed 3-day approximation** (Tuesday report date + 3
  calendar days ≈ Friday release), not the exact historical release
  calendar (which has occasional holiday-driven shifts).
- **No true portfolio turnover simulator** — `validation.turnover_rate` is
  a top-quintile-membership churn proxy, not turnover against an actual
  position sizer.
- **No web UI.** The spec's Section 7 "Product Experience" describes a
  ranked page + detail panel; this package delivers that as a CLI text
  report (`report.py`) per the explicit instruction to build ".py tools",
  not a web frontend.

## Performance

Every signal family except curve/carry is pure math over data fetched once
and sliced per as-of date — fast. Historical curve/carry defaults off in
training for the reason above. The remaining cost driver for a full-universe
run is CFTC/FRED network fetches (once per commodity, cached across the
whole run) plus `ranking.py`'s per-horizon walk-forward IC estimation
(`derive_component_weights`, which refits models across `IC_LOOKBACK_FOLDS`
folds). A full 25-commodity, 3-horizon run takes several minutes; pass a
smaller `universe` dict to `build_report`/`fetch_universe_data` for fast
iteration during development.
