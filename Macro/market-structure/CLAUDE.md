# Macro/market-structure

Python toolkit that ports the risk:reward + trendline-discovery methodology
documented in `/Users/elisamson/Desktop/wisdom/rr.txt`, adds a trend-violation
detector that methodology was missing, and rolls both up into a cross-index
macro bullishness gauge + cash-on-sidelines gauge. No MCP wrapper — this is
plain, importable Python, run via `uv run`.

Sibling of `Macro/Rates` (same `uv` + pytest conventions). `rates_macro.trend_rr`
is reused here as an editable path dependency (see `pyproject.toml`'s
`[tool.uv.sources]`) rather than duplicated — this package is the trend-signal
consumer, `Rates` is the trend-signal source of truth.

## Setup

```bash
cd Macro/market-structure
uv sync              # installs deps incl. the rates-macro path dependency
uv run pytest -q     # 95 tests, all pure-math / monkeypatched-network, no live calls
```

## Entry point

```bash
uv run python -m market_structure.report
```

Fetches the default universe (5 broad indexes + 11 sector ETFs, see
`universe.py`) via yfinance, runs the full pipeline per ticker, and prints the
gauge + per-index blurbs + rationale. `report.build_report(universe=...)`
takes a custom `{ticker: name}` dict to run a smaller/different set.

## Module map — read in this order to understand the pipeline

Each module's docstring cites which Part of `rr.txt` it ports; start there if a
formula looks unfamiliar.

1. **`indicators.py`** — ATR / realized vol / relative volume / recency-weighted
   swing pivots. Everything else is built from this. (rr.txt Parts 2-3)
2. **`levels.py`** — the six independent level-detection methods (horizontal
   channels, fib retracement, anchored VWAP, volume profile HVN, round
   numbers, + a slot for trendline levels) and convergence clustering — the
   "when ≥2 independent methods agree, that agreement is the signal" logic.
   (rr.txt Parts 4, 6)
3. **`trendlines.py`** — both trendline families: Family A (one global
   quantile-regression line per side, feeds convergence clusters) and Family B
   (many segment-specific pivot-pair lines, validated bar-by-bar). (rr.txt
   Part 5)
4. **`trend_violation.py`** — **the refinement**, not in the original
   methodology. Detects when price has closed below its own most relevant
   *recent* ascending Family-B support line — the "undercut support of
   uptrend = take some risk off" case from the screenshots. Read this
   module's docstring; it explains a real bug found and fixed during
   development (naively picking the highest-*scored* line favors old broad
   channels over the fresh line that just broke — the opposite of what this
   detector needs) and why `detect_trend_violation` recomputes its own larger
   candidate pool instead of reusing `risk_reward.py`'s capped top-12 list.
5. **`fib_extension.py`** — ATH/no-overhead reward projection. (rr.txt Part 7)
6. **`stop_target.py`** — the 4-tier stop/target fallback (cluster →
   trendline → fib_extension → synthetic) with `target_source` attribution.
   (rr.txt Part 8)
7. **`risk_reward.py`** — orchestrates 1-6 into one `RiskRewardReport` per
   ticker. `analyze(ticker, high, low, close, volume) -> RiskRewardReport`.
   (rr.txt Part 12, end-to-end pipeline order)
8. **`macro_gauge.py`** — combines `RiskRewardReport` + a reused
   `rates_macro.trend_rr` trend signal into a per-ticker 0-100 bull score, the
   overall weighted gauge, and the cash-on-sidelines gauge (amplified when a
   majority of the universe shows an undercut trendline simultaneously — a
   breadth/regime-break read). Every term of the scoring formula is a public
   dataclass field (`TickerGauge.trend_component`/`.rr`/`.violation`, etc.) —
   nothing is computed only for display and thrown away, so `report.py` can
   print the exact number that produced each score. `FORMULA_LEGEND` is the
   formula itself, generated from the same constants used to compute it (not
   a separately-maintained docstring), so it can't drift out of sync.
9. **`market_data.py`** — yfinance OHLCV fetch + quality gate (the only I/O
   in the package; everything above is pure math and fully offline-testable).
10. **`report.py`** — top-level orchestration + CLI entry point.
    `render_summary()` is deliberately over-explicit: formula legend up top,
    then per ticker the exact trend/rr/violation contributions, the support
    cluster stack with gap-%/ATR distances (so a "vacuum" to the next support
    level is visible, not just the nearest one), and the actual trendline
    dates/prices behind any undercut read. The goal is that the printed
    report needs no external narration to understand — if a score looks
    surprising, the line above it names the term that produced it.
11. **`universe.py`** — the default ticker universe and its composite
    weighting (70% broad indexes / 30% sectors, renormalized to whatever
    subset is actually available).

## Conventions

- Pure math modules take numpy arrays / dataclasses and do no I/O — only
  `market_data.py` touches the network. Keep new analysis logic in that
  offline-testable style.
- Dataclasses are `frozen=True` throughout (immutability per the user's global
  coding-style rules).
- Tests mirror the module list 1:1 (`tests/test_<module>.py`), pytest classes
  named `Test<Thing>`, synthetic data built with `np.random.default_rng(seed)`
  for determinism. Network calls are monkeypatched at the `_download`/
  `fetch_ohlcv` boundary, never hit live in tests.
- If `rr.txt` changes, re-distill the affected module from it — the docstrings
  say exactly which Part each function ports, so diffing is straightforward.

## Known validation

Live-checked against the screenshots that motivated this build: QQQ's
stop/target landed almost exactly on the screenshot's numbers, and
`trend_violation` correctly flagged QQQ's break of its Mar–Jun 2026 rally
support line — the case the original methodology had no way to surface.
