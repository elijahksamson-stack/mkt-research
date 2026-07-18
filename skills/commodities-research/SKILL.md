---
name: commodities-research
description: Ranks 21 commodity futures (energy, precious/industrial metals, agriculture, livestock) by a calibrated up-probability, expected return, and downside quantile per horizon, blended into a commodity_opportunity_score, plus COT positioning, seasonality, and curve/carry context (Commodities). Use when the user asks about oil, gold, copper, natural gas, agricultural commodities, or wants a commodities outlook or ranking.
argument-hint: "[optional horizon: 1W, 1M, or 3M (default 1M); optional commodity name for --detail]"
allowed-tools: Bash
---

# Commodities research

Pull the current commodities ranking/forecast for: $ARGUMENTS.

1. Determine the horizon from the arguments (`1W`, `1M`, or `3M`; default
   to `1M` if unspecified) and run:
   ```bash
   cd "$CLAUDE_PLUGIN_ROOT/Commodities" && uv run python -m commodities.report --horizon <HORIZON> --detail 5
   ```
   Increase `--detail` if the user asked about a specific commodity or
   wants more than the top 5 detailed.
2. This is the most model-heavy toolkit in the plugin: `up_probability` is
   an actual walk-forward-validated **calibrated probability**, not a
   composite score like the other toolkits' gauges — you can quote it with
   that meaning, but still pair it with the expected-return and
   downside-quantile figures rather than the probability alone.
3. `render_detail`'s output deliberately never prints a bare "BUY" —
   preserve that discipline in your own summary: report the forecast
   distribution and the features that drove it, not a directive.
4. Cross-reference with `macro-research` when relevant: commodity
   trend/carry often leads or confirms a macro regime read (e.g.
   copper/oil vs. growth, gold vs. real yields, which the report's
   macro-controls features already incorporate).

Before writing anything based on curve/carry or COT positioning, read
`$CLAUDE_PLUGIN_ROOT/CLAUDE.md`'s "Data provenance & limitations"
section — curve/carry is live-only (historical curve
reconstruction is unreliable given Yahoo Finance's dated-contract gaps),
roll timing is a fixed heuristic not an actual liquidity-based roll, and
COT is aggregated Disaggregated-COT z-scores, not per-contract open
interest.
