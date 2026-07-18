# Macro/Rates — FRED + S&P Cross-Reference Toolkit

## What this is

A Python toolkit that pulls FRED macro series (HY credit spread, Treasury
yields, Fed funds, the USD index) and the S&P (via yfinance/SPY), computes a
trend + mean-reversion profile for each series, and cross-references each one
against the S&P to show how it relates to equities (correlation, beta,
lead-lag).

Original ask: build something that reads HY credit and rates off FRED,
cross-references to S&P to see how one affects the other, and runs the same
trend/RR-style regression model used in `Desktop/Stuff/ClaudeApps/InvestorPro`
(see `rr.txt` in `Desktop/wisdom/` for the fuller RR methodology that toolkit
uses on individual tickers — this one adapts the lighter regression-channel
model from that project's sector-ranking script, since FRED series are
level-only and have no OHLCV).

This is step one: an accurate standalone analysis tool. It is not yet wired
into an agent or MCP server — that's a later step.

## Layout

```
rates_macro/
  trend_rr.py         pure math: HAC log-regression trend/RR, mean-reversion Z
  cross_reference.py   pure math: correlation, beta, lead-lag between 2 series
  fred_client.py        FRED HTTP client + API key resolution + series catalog
  market_data.py         yfinance close-price fetch + data-quality gate
  macro_score.py           POSITIONING score: momentum × equity-correlation
  red_zone.py               VULNERABILITY score: Greenwood-Hanson Red-Zone froth
  regime.py                  REGIME read: 2×2 quadrant from the two scores
  report.py                   orchestrator: wires the above into one report + CLI
tests/                      125 unit tests, TDD throughout, no network required
```

There are **two independent scores, kept deliberately separate** (never blended
into one number — see the Red-Zone section for why):
- **Positioning** (`macro_score.py`) — momentum: where the market is leaning now.
- **Vulnerability** (`red_zone.py`) — latent crisis fragility, à la
  Greenwood-Hanson. Froth reads bullish to positioning and dangerous to
  vulnerability *at the same time*; the divergence is the signal.
They combine into a `regime.py` 2×2 quadrant, not an average.

## Setup

```bash
cd /Users/elisamson/Desktop/Blog/Macro/Rates
uv sync
```

### FRED API key

Free key: https://fred.stlouisfed.org/docs/api/api_key.html

`fred_client.resolve_fred_key()` checks, in this order:
1. `FRED_API_KEY` environment variable
2. `~/.config/rates-macro/.env` — **outside this project directory on
   purpose**, because this repo is slated to be open-sourced eventually (as
   an MCP plugin). The real key lives there (`chmod 600`), never inside this
   folder.
3. `.env` in this project directory (gitignored) — a fallback for anyone who
   clones the eventual open-source repo and prefers a local key instead.

`.env.example` in this directory is a template only — it ships empty.

## Running it

```bash
uv run python -m rates_macro.report
```

Or from Python:

```python
from rates_macro.report import build_report, render_summary

report = build_report()          # dict — see "How to interpret" below
print(render_summary(report))    # plain-text table
```

`build_report(series_ids=None, benchmark="SPY")` — pass a custom
`{series_id: label}` dict to analyze a different set of FRED series than the
defaults in `fred_client.ALL_SERIES`.

## How to interpret the output

Each series in `report["series"][series_id]` has:

| Field | Meaning |
|---|---|
| `latest` / `as_of` | most recent value and its date |
| `trend_rr.trend_signal` | -1..+1. HAC-regression trend direction/strength across 21/63/126/252-day windows, blended. Positive = uptrend, negative = downtrend, ~0 = no reliable trend. |
| `trend_rr.opportunity` | 0..100. How favorable the current regression-channel setup looks (distance from the fitted trend, forecast direction, asymmetry of the residual channel). Higher = more attractive risk:reward on the regression channel, not a buy signal by itself. |
| `mean_reversion.z_score` | How many std devs the latest value sits from its own trailing mean (252-day window by default). +2 = unusually high vs. its own history, -2 = unusually low. This is distance from the **raw mean**, distinct from `trend_rr`'s residual_z which is distance from the **fitted trend line**. |
| `mean_reversion.percentile` | Where the latest value ranks (0-100) within its own trailing window. |
| `stale` / `staleness_days` | `stale=True` when the series' latest print trails the S&P benchmark's by more than 10 days — treat that series' cross-reference numbers with less confidence (could be an API hiccup or a genuinely low-frequency series). |
| `vs_benchmark.contemporaneous.correlation` | Pearson correlation of this series' period-over-period changes against the S&P's log returns. FRED level series (yields, spreads, USD index) use simple diffs; the S&P uses log returns — that's the market convention for each. |
| `vs_benchmark.contemporaneous.beta` | How many units this series moves per unit the S&P moves (OLS slope), same change basis as correlation. |
| `vs_benchmark.lead_lag.best_lag` | The lag (in trading days) at which this series' changes correlate most strongly with the S&P's. Positive = this series tends to move **before** the S&P by that many days; negative = it tends to move **after**. `0` = contemporaneous is the strongest relationship found. |

Any sub-computation that fails for a given series (too little history, a
data quirk like a duplicate FRED timestamp) degrades to `{"error": "..."}`
in that field rather than crashing the whole report — one bad series never
takes down the others. A series that fails at the fetch stage entirely (bad
series ID, FRED outage, empty response) shows up in `report["dropped"]`
instead of `report["series"]`.

**Reference read**: HY OAS (`BAMLH0A0HYM2`) correlating strongly negative
with the S&P (roughly -0.5 to -0.7 on a live pull) is the expected,
economically sane relationship — spreads widen when equities sell off. If
that correlation ever comes back positive or near zero, something's likely
wrong with the data or the alignment, not with the market.

### The composite macro score

`macro_score.macro_score(report)` blends everything above into one 0-100
bullish/bearish read for equities (50 = neutral), fully attributable back to
the numbers that produced it.

**Methodology — deliberately data-driven, not hardcoded market lore.** For
each series: `signed_alignment = trend_signal × correlation`. A series
trending in the direction that has *recently, measurably* coincided with the
S&P moving the same way scores positive; trending opposite to its measured
relationship scores negative. This is intentional: it does NOT assume
"rising rates are bad for stocks" as a fixed rule — if a series' correlation
to the S&P is near zero right now (as 10Y's -0.07 is, in a live pull), that
series contributes almost nothing to the score, whatever a textbook prior
would say. The score only moves on relationships that are actually showing
up in the data.

Series are grouped into categories from `fred_client`'s catalog (`rates`,
`credit`, `fx`), averaged within each category, then weighted (equal thirds
by default — pass `category_weights={"rates": ..., "credit": ..., "fx": ...}`
to `macro_score()` to override). If a whole category has no surviving series
(all stale or errored), the score renormalizes over the remaining weight
instead of silently treating the missing category as neutral — otherwise a
score would drift toward 50 just because one category happened to drop out,
not because the macro backdrop actually got more neutral.

Excluded series (stale, or a math failure upstream) are listed in
`result["excluded"]` with a reason — never silently folded into the score as
if they were neutral.

```python
from rates_macro.macro_score import macro_score, render_macro_score
print(render_macro_score(macro_score(report)))
```

`report.main()` (i.e. `uv run python -m rates_macro.report`) prints this
automatically after the per-series table.

### The vulnerability score (Red-Zone) — `red_zone.py`

The positioning score above is *momentum* — trend-confirming, so it reads
bullish exactly when froth is building. `red_zone.build_red_zone()` is the
opposite lens: how much latent **crisis fragility** is present, scored on each
input's own level/change vs. its OWN long history — **not** its correlation to
the S&P. That omission is deliberate: crisis-warning signals matter precisely
when they are *not yet* in market prices, so scoring them by equity co-movement
would suppress the early warning.

Built to Greenwood-Hanson: the Red-Zone is a **conjunction** of three froth
legs, each a 0-100 percentile-vs-history:

| Leg | FRED input | Froth = |
|---|---|---|
| **quantity** | trailing 12q change in credit-to-GDP (`QUSPAM770A`) | high percentile of the *change* — credit expanding faster than the economy |
| **asset** | market-cap-to-GDP (`NCBEILQ027S` ÷ `GDP`) | high percentile of the level — asset prices elevated |
| **price** | Moody's Baa−10Y spread (`BAA10Y`, deep history) | *low* spread percentile → high froth — investors stopped pricing downside |

The legs combine with a **weighted geometric mean** (`geometric_conjunction`),
not an average — because Greenwood is explicit a crisis needs *all* cylinders
firing. Any single cold leg drags the whole score down. Weights default to
equal thirds; pass `weights={"quantity": ..., "asset": ..., "price": ...}` to
`build_red_zone()`. Legs whose fetch fails or whose history is too short are
listed in `result["excluded"]` and the score is computed on the survivors —
never fabricated.

**Why geometric, validated live (2026-07):** market-cap-to-GDP is at its 98.7th
percentile and Baa spreads at their ~11th (froth 88.8) — two legs near-max —
but credit-to-GDP is *contracting* (quantity froth 6.0). The geometric
conjunction lands at **37.5/100 (contained)**; a naive arithmetic mean would
read 64.5 and falsely flag near-Red-Zone. That 37.5 reproduces Greenwood's own
Aug-2024 conclusion — "spreads are tight but credit expansion is modest, so
it's not a bubble" — by the exact same mechanism, on independent 2026 data.

**Note on ICE BofA vs. Moody's:** the article's exact HY OAS series
(`BAMLH0A0HYM2`) is capped at ~3 recent years on the FRED API (ICE licensing),
too short for a "vs. history" percentile — so the price-froth percentile leg
uses Moody's `BAA10Y` (daily back to 1986). HY OAS still appears in the
positioning score and the per-series table for continuity with the article.

### The regime read — `regime.py`

`regime(positioning_score, vulnerability_score)` maps the two scores onto a 2×2
quadrant (never a blended number — the whole point is to keep the axes
separate so their divergence stays visible):

```
                     LOW vulnerability        HIGH vulnerability
  HIGH positioning   healthy_expansion        red_zone_froth        ⚠
  LOW  positioning   correction_reset         crisis_unwind         ⚠⚠
```

Vulnerability uses a **tail threshold** (default 66, configurable) because a
Red-Zone is a top-quintile condition, not merely "above average." If the
vulnerability score is `None` (all legs excluded), the regime degrades to a
positioning-only read rather than crashing.

`report.main()` prints all four blocks in order: per-series table → positioning
score → vulnerability score → regime.

## Testing

```bash
uv run pytest -q
```

130 tests, all pure-math or mocked-HTTP — no live network calls, no FRED key
needed to run the suite. Includes a Greenwood-pattern regression test
(`test_red_zone.py`) asserting that a cold quantity leg drags down two hot
legs — the behavior that reproduces the "no bubble" read — plus regression
tests for the code-review fixes below.

### Notes on the vulnerability leg internals

- **Score is `None`, never a fabricated `0.0`, when no leg carries positive
  weight** (e.g. custom weights concentrated on a leg that then gets excluded).
  `geometric_conjunction` returns `None` in that case and `regime()` degrades
  to a positioning-only read — consistent with "never fabricate a number."
- **`credit_to_gdp_change` is calendar-aware**: it snaps to quarter periods and
  reindexes onto a gap-free quarterly grid before differencing, so the trailing
  change spans real quarters even if the BIS series ever skips/revises one — the
  same "align before differencing" discipline used in `cross_reference.py`.
- **The asset leg's displayed `latest` is unit-scaled** (`ASSET_DISPLAY_SCALE`,
  ×0.001) because `NCBEILQ027S` is in $millions and `GDP` in $billions; froth is
  a scale-invariant percentile so scoring is unaffected, but the printed value
  now reads as ~2.18 (market-cap-to-GDP ≈ 218%) rather than a ~2181 that looks
  like a bug.

## Design notes

- **`diff` vs `log_return`**: level series (yields, spreads, the USD index)
  use simple differences (the market convention, quoted in level/bps terms);
  price series (S&P) use log returns. Mixing bases would make correlation/
  beta numbers not comparable across series.
- **Align before differencing**: `cross_reference.py` aligns two series on
  their shared calendar dates *before* computing changes, not after —
  otherwise a FRED series skipping a bond-market-only holiday the S&P trades
  through would silently pair a multi-day change against the S&P's
  single-day change on that date, corrupting correlation.
- **Never fabricate a number**: a failed fetch or missing FRED value raises
  or is dropped — it never gets coerced into 0 or silently reused from a
  stale cache. Mirrors the same principle in
  `InvestorPro/python/tools/macro_sentiment.py`.
