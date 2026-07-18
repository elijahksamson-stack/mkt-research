---
name: market-outlook
description: Compiles every research read (macro, equities, commodities, crypto) plus industry expertise into a market outlook / opinion article. Use when the user asks for a market outlook, a view on where markets are headed, a cross-asset synthesis, or "what's happening in markets right now."
argument-hint: "[optional: focus area or specific question to frame the outlook around]"
allowed-tools: Bash, WebSearch, WebFetch
---

# Market outlook — the report tool

Compile every research read and write a market outlook / opinion article,
focused on: $ARGUMENTS (or the broad market if no focus was given). This
skill produces no data of its own — it orchestrates the four research
engines and the `industry-expertise` MCP server, enriches with
primary-source data, and synthesizes.

The example that shaped this skill is a *guideline for craft, not a
template*. Do not force its oil/Hormuz framing, its section headings, or its
exact scenarios onto a different market. Follow the principles; let the
current data pick the story.

## 1. Gather every read first

Run these in parallel (independent). `$CLAUDE_PLUGIN_ROOT` is set by Claude
Code to this plugin's install directory:

```bash
cd "$CLAUDE_PLUGIN_ROOT/Macro/Rates" && uv run python -m rates_macro.report
cd "$CLAUDE_PLUGIN_ROOT/Macro/market-structure" && uv run python -m market_structure.report
cd "$CLAUDE_PLUGIN_ROOT/Equities/equity-rotation" && uv run python -m equity_rotation.report
cd "$CLAUDE_PLUGIN_ROOT/Commodities" && uv run python -m commodities.report --horizon 1M --detail 5
cd "$CLAUDE_PLUGIN_ROOT/Crypto" && uv run python -m crypto_structure.report
```

For whichever sector stood out in the equity-rotation output, call the
`industry-expertise` MCP server (`get_industry_expertise`, or
`search_industry_expertise` if the classification is uncertain) to ground
the piece in that industry's structure and economics.

## 2. Enrich and cross-check against primary sources (hybrid)

The four engines are the quantitative spine. They are not the whole story,
and their composite scores are not above scrutiny. Use `WebSearch`/`WebFetch`
to pull current primary-source data and to **challenge** the tools where a
reading looks off:

- **Ground the narrative** with real, cited figures. Reach for, when
  relevant: FRED series (nominal yield `DGS10`, real yield `DFII10`,
  breakevens `T10YIE`, HY OAS `BAMLH0A0HYM2`); EIA (energy); BLS + Atlanta
  Fed GDPNow (growth/inflation/labor); FactSet (earnings season);
  Cboe (VIX, implied correlation); NAAIM / AAII (positioning, sentiment).
- **Cross-check the composites.** If `market-structure` reports an extreme
  "cash on the sidelines," sanity-check it against NAAIM exposure / AAII
  bulls-bears and *say so* if they disagree — do not parrot a composite that
  external positioning data contradicts. The same skepticism applies to any
  single-number reading that drives the thesis.
- Verify time-sensitive claims against the source; link it.

## 3. Synthesize — principles, in this order

1. **Lead with a thesis and a causal chain**, not a data dump. State what
   the market is doing and *why* (catalyst → transmission mechanism →
   outcome). Name the one variable that actually drives the others rather
   than treating a downstream signal as the cause.
2. **Regime backdrop** — from `Macro/Rates` + `Macro/market-structure`:
   risk-on or risk-off, and how confident that read is (bull score,
   cash-on-sidelines, credit-spread trend, curve shape, USD trend, breadth
   of trend-violation).
3. **What's actually being bought** — from `equity-rotation`: leadership /
   opportunity ranking and RRG quadrants. Call out disagreement between the
   quadrant read and the leadership score explicitly — that disagreement is
   informative, not noise. Distinguish "what's being bought this week"
   (tactical rotation) from "what owns the cycle" (durable leadership).
4. **Why** — the qualitative grounding from `industry-expertise` for the
   sector that stood out.
5. **Cross-asset confirmation** — from `Commodities`: does commodity
   trend/carry (and its macro-controls features) agree with the regime read,
   or diverge?
6. **Fastest-moving check** — from `Crypto`: has its risk score turned ahead
   of equities/credit? Crypto is usually the earliest of the four to move.
7. **Write the divergences, not just the agreements.** Four reads agreeing
   is higher-conviction but lower-information. Four diverging is the more
   specific, usually more interesting story — name the outlier and
   hypothesize why (a genuine leading-indicator lead/lag gap vs. noise).
8. **Separate observation / forecast / opinion explicitly.** Only
   Commodities' `up_probability` is a calibrated probability; `bull_score`,
   `risk_score`, `leadership`/`opportunity`/`joint` are relative composites,
   not probabilities — never quote them with equivalent confidence. When the
   piece moves from "the data shows X" to "therefore Y" to "therefore you
   should Z," mark the transition in those terms.

## 4. Craft requirements for the article

- **Cite sources** for external figures (link them). Attribute tool figures
  to the tool.
- **Keep price levels internally consistent.** If you quote a stop/target,
  they come from one engine — do not mix a tool's tile levels with different
  narrative levels as if they share one stop-and-target model.
- **Close with a scenario state-vector and a watch-hierarchy.** Give a few
  named regimes with *numeric* triggers (e.g. "spreads widen through X, VIX
  holds above Y") and state what to watch first, second, third — the
  hierarchy of drivers, not a single number.
- End with a one-line data-provenance + not-advice note.

Full methodology, the shared-DNA table between engines, and per-engine data
provenance/limitations live in `$CLAUDE_PLUGIN_ROOT/CLAUDE.md`. Read it if
anything here is ambiguous; don't guess at an engine's methodology or caveats
when that file already states them.
