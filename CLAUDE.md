# Blog — Market Research Toolkits

Four independent quantitative/qualitative research sets, unified as of this
writing into a single Claude Code plugin (`market-research`) rooted here.
This file is the dev-facing deep dive (methodology, shared DNA, data
limitations, synthesis workflow); see `README.md` for the plugin-facing
view (install, skills, MCP server) and `.claude-plugin/plugin.json` for
the manifest. Each research set's underlying code is still a standalone
`uv`-managed Python project (or, for industry expertise, the bundled MCP
server) — the plugin's `skills/` are a thin orchestration layer over them,
not a rewrite.

```
Blog/
├── .claude-plugin/         plugin.json, marketplace.json
├── server/                 industry-expertise MCP server (Node, stdio)
├── skills/                 industry-research, market-outlook (market-outlook
│                           drives all four quant engines directly)
├── Macro/
│   ├── Rates/               FRED + yfinance: HY credit, rates, USD vs S&P
│   └── market-structure/    equity index/sector risk:reward + trend engine (source of truth)
├── Equities/
│   └── equity-rotation/     quant: sector/factor leadership + opportunity + RRG
├── Commodities/             ML ranking/forecast engine, 21 futures, reuses Macro's engines
└── Crypto/                  self-contained port of the market-structure engine for 24/7 markets
```

Industry expertise (formerly the standalone `Equities/sector-lvl-expertise/`
plugin) now lives at `skills/industry-research/` + `server/` here — folded
in, not duplicated. Its original git history remains at its GitHub remote,
`elijahksamson-stack/industry-expert-plugin`, untouched.

## The shared DNA

Two pieces of methodology, both documented in
`/Users/elisamson/Desktop/wisdom/rr.txt`, run through most of these
projects. Know which one you're touching before you edit it:

1. **The risk:reward / trendline engine** (pivots → six level-detection
   methods → convergence clustering → two trendline families →
   trend-violation detection → 4-tier stop/target). Source of truth:
   `Macro/market-structure/market_structure/`.
2. **The HAC (Newey-West) log-regression trend model**
   (`trend_signal`/`opportunity` from a multi-window regression). Source of
   truth: `Macro/Rates/rates_macro/trend_rr.py`.

| Project | RR engine | Trend engine | How |
|---|---|---|---|
| `Macro/market-structure` | **origin** | imports | `[tool.uv.sources]` path dep on `rates-macro` |
| `Macro/Rates` | — | **origin** | — |
| `Commodities` | imports | imports | `[tool.uv.sources]` path deps on both `market-structure` and `rates-macro` |
| `Crypto` | verbatim port | crypto-adapted port | fully self-contained, no runtime import |
| `Equities/equity-rotation` | — | intentional duplicate | self-contained, doesn't import `Rates` |
| `skills/industry-research` | — | — | unrelated (qualitative, no shared math) |

**Practical consequence:** if you fix a bug or improve a formula in
`market-structure` or `rates_macro`, `Commodities` inherits it automatically
(path dependency — re-run `uv sync` there if the change is structural).
`Crypto` and `equity-rotation` will **not** — they copied the logic on
purpose to stay standalone, so check whether the same issue exists in their
ported copy and fix it there too.

## The four research sets

### 1. Macro — regime backdrop

- **`Macro/Rates`** — HY credit spreads, the Treasury curve, and the USD
  index (FRED) cross-referenced against S&P trend/mean-reversion.
  ```bash
  cd Macro/Rates && uv run python -m rates_macro.report
  ```
- **`Macro/market-structure`** — risk:reward + trend-violation + a 0-100
  bullishness gauge and cash-on-sidelines read across 5 broad indexes + 11
  sector ETFs. This is also the RR engine's source of truth (see above).
  ```bash
  cd Macro/market-structure && uv run python -m market_structure.report
  ```
  Every number in its output is a traceable formula term (`FORMULA_LEGEND`,
  per-ticker breakdown, support-cluster stack, trendline detail) —
  deliberately built so it needs no narration to interpret.

### 2. Equities — what's moving, and why

- **`Equities/equity-rotation`** (quant) — ranks the 11 GICS sector ETFs and
  6 style-factor ETFs by peer/benchmark-blended leadership + opportunity,
  plus an RRG-style (leading/weakening/lagging/improving) quadrant read.
  Driven by the `market-outlook` skill; can also be run directly:
  ```bash
  cd Equities/equity-rotation && uv run python -m equity_rotation.report
  ```
- **`skills/industry-research`** (qualitative) — the bundled
  `industry-expertise` MCP server (`server/`) plus 39 sector/industry
  research modules, exposed via the `industry-research` skill. Formerly a
  standalone plugin (`Equities/sector-lvl-expertise/`); now part of this
  plugin, no separate install.

Use them together: the equity-rotation engine says *what* is leading;
`industry-research` says *why* (industry structure, economics, competitive
dynamics) once you know what to ask about.

### 3. Commodities — cross-asset forecast + confirmation

21 futures across energy, precious/industrial metals, agriculture, and
livestock. The most model-heavy of the four: walk-forward-validated
elastic-net/quantile-regression models produce a calibrated up-probability,
expected return, and downside quantile per horizon, blended into an
`commodity_opportunity_score` with out-of-sample IC-derived (never
hand-tuned) weights. Also pulls COT positioning, seasonality, term
structure/carry, and macro controls (USD, real yields, ^SPGSCI).
```bash
cd Commodities && uv run python -m commodities.report --horizon 1M --detail 5
```
`--horizon` accepts `1W`/`1M`/`3M`. `render_detail` deliberately never
prints a bare "BUY" — only the forecast distribution and the features that
drove it.

### 4. Crypto — risk-appetite barometer

BTC/ETH + 16 liquid large-cap alts, BTC-benchmarked leadership ranking, and
a 0-100 risk score / risk-off read (the crypto-market analogue of
`market-structure`'s bull score / cash-on-sidelines — crypto has no literal
"cash on the sidelines," so the label changed but the formula didn't).
```bash
cd Crypto && uv run python -m crypto_structure.report
```
Crypto tends to be the fastest, most liquid risk-on/risk-off barometer of
the four — useful as an early cross-check against the macro/equity read.

## Bringing it together: writing an outlook or opinion piece

None of these tools produces a market view on its own — they each answer a
narrower, well-defined question. An outlook piece is the synthesis. The
plugin's `market-outlook` skill (`skills/market-outlook/SKILL.md`)
automates this exact workflow — invoke it directly for "write me a market
outlook" style requests. The order it (and this section) follows:

1. **Set the regime backdrop first.** Pull `Macro/Rates` (credit spreads
   widening/tightening, curve shape, USD trend) and `Macro/market-structure`
   (overall bull score, cash-on-sidelines, breadth of trend-violation
   across the index/sector universe). This answers "risk-on or risk-off,
   and how confident is that read" before anything else.
2. **Check what's actually being bought.** Pull `equity-rotation`'s
   leadership/opportunity ranking and RRG quadrants. Where the RRG quadrant
   and the regression-based leadership score disagree (this happens — see
   that project's own `CLAUDE.md` for a live example) is itself worth a
   sentence: two different models of "leading" are telling you different
   things.
3. **Pull qualitative grounding** from `industry-research` for whichever
   sector stood out in step 2, so the piece explains *why* a sector is
   moving, not just *that* it's moving.
4. **Cross-check with Commodities.** Commodity trend/carry often leads or
   confirms a macro regime read (e.g. copper/oil vs. growth, gold vs. real
   yields already captured in `macro_controls.py`). Note whether the
   forecast distributions agree with the equity/macro read or diverge.
5. **Cross-check with Crypto's risk gauge** as the fastest-moving read.
   Crypto turning risk-off before equities/credit do is itself a signal
   worth flagging, not just background color.
6. **Write the divergences, not just the agreements.** Four models
   agreeing is a higher-conviction, lower-information thesis ("everything
   says risk-on"). Four models diverging is usually the more interesting,
   more specific thing to actually write about — say which model is the
   outlier and why that might be (e.g. "equities and commodities still
   read bullish, but the macro credit/trend-violation gauges and crypto's
   risk score have already turned — a classic leading-indicator lead/lag
   gap, not yet a confirmed reversal").
7. **Separate observation from forecast from opinion explicitly.** These
   tools output observations, associations, and (for Commodities only)
   calibrated forecasts — not certainties. When the piece moves from "the
   data shows X" to "therefore Y will happen" to "therefore you should Z,"
   say so in those terms rather than blending them. A `bull_score` or
   `leadership` rank is a relative composite read; only Commodities'
   `up_probability` is an actual calibrated probability — don't present the
   others with that same confidence.

## Data provenance & limitations

Read this before trusting any single number too far, and before writing
"the data shows" language into an outlook piece.

- **yfinance** is the common data backbone across all four sets (free, no
  API key). It's generally reliable for daily OHLCV on liquid tickers, but
  has no official audit trail, occasional gaps/outages, and adjusted-close
  quirks around splits/dividends. Every project's `market_data.py` runs a
  quality gate (bar count, coverage, staleness) before trusting a series,
  but a gate passing means "enough data," not "verified-correct data."
- **FRED** (`Macro/Rates`, `Commodities/macro_controls.py`) is
  official-source but revision- and release-lag-prone — a point-in-time
  backtest needs to account for vintage effects, not just the latest
  revised values.
- **Commodities-specific:**
  - No CFTC per-contract open interest — `positioning.py` uses
    Disaggregated COT z-scores/percentiles with the correct publication
    lag, which is real positioning data, just aggregated rather than
    contract-level.
  - Roll timing is a fixed-day-before-expiry heuristic in `contracts.py`,
    not the liquidity-based roll a professional desk would actually
    execute — roll-adjusted returns near expiry should be read with that
    in mind.
  - Curve/carry (`curve_carry.py`) is **live-only**: Yahoo Finance's
    dated-contract history has gaps that make historical curve
    reconstruction unreliable, so curve-based backtests aren't trustworthy
    today — only live curve/carry reads are.
- **Crypto:** large-cap universe only (no small-cap/DeFi-token coverage),
  price/volume only — no on-chain data (exchange flows, funding rates,
  liquidations). `MAX_STALENESS_DAYS` is tightened to 3 (vs. 10 for
  equities/macro) since crypto trades every calendar day with no weekend
  gap to allow for.
- **Duplicated math drifts independently.** `equity-rotation` and `Crypto`
  copied `trend_rr.py`'s HAC regression rather than importing it (see "The
  shared DNA" above) — a fix in `Rates` does not propagate to them.
- **Score semantics vary by project.** `bull_score` (market-structure),
  `risk_score` (Crypto), `leadership`/`opportunity`/`joint`
  (equity-rotation) are internally consistent, fully code-computed relative
  composites — not calibrated probabilities. Only Commodities'
  `up_probability` is a walk-forward-validated calibrated probability.
  Don't quote the others with equivalent confidence language.

## Shared conventions

All five Python projects (everything except `skills/industry-research`'s
Node MCP server) follow the same shape, established in `Macro/Rates` and
`Macro/market-structure` and carried forward by every sibling since:

- `uv`-managed, `pyproject.toml` + `uv.lock`, `uv sync` / `uv run pytest -q`
  / `uv run python -m <package>.report`.
- Pure-math analysis modules (numpy arrays / `frozen=True` dataclasses, no
  I/O) with exactly one network boundary module, always named
  `market_data.py`.
- Tests mirror the module list 1:1 (`tests/test_<module>.py`), synthetic
  data via `np.random.default_rng(seed)`, network calls monkeypatched at
  the `_download`/`fetch_*` boundary — no test ever hits a live API.
- `report.py` is the CLI entry point: `build_report()` returns a plain
  dict, `render_summary()`/`render_table()` prints a fully quantitative,
  self-explanatory snapshot (formula legend + per-line-item breakdown, not
  a narrative summary a reader has to trust blindly).

When extending one project's methodology, check the "shared DNA" table
above for whether siblings duplicated it — an improvement made in one place
may need to be manually ported to the others.
