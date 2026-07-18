---
name: macro-research
description: Pulls the macro regime backdrop -- HY credit spreads, the Treasury curve, and USD trend vs the S&P (Macro/Rates), plus the broad-index/sector bullishness, cash-on-sidelines, and trend-violation-breadth gauge (Macro/market-structure). Use when the user asks about interest rates, credit spreads, the yield curve, the US dollar, macro regime, risk-on/risk-off conditions, or wants a macro snapshot before discussing anything else.
argument-hint: "[optional: specific ticker/series, or leave blank for the default universe]"
allowed-tools: Bash
---

# Macro research

Pull the current macro regime backdrop for: $ARGUMENTS (or the default
universe if no argument was given).

1. Run both reports (`$CLAUDE_PLUGIN_ROOT` is set by Claude Code to this
   plugin's actual install directory, so this works regardless of where
   it was installed):
   ```bash
   cd "$CLAUDE_PLUGIN_ROOT/Macro/Rates" && uv run python -m rates_macro.report
   cd "$CLAUDE_PLUGIN_ROOT/Macro/market-structure" && uv run python -m market_structure.report
   ```
2. Both outputs are deliberately self-explanatory — every score is printed
   alongside the formula term that produced it (`market_structure.report`
   prints a `FORMULA_LEGEND` and a per-ticker breakdown; `rates_macro.report`
   prints trend signal, opportunity score, mean-reversion Z, and
   correlation/beta/lead-lag vs. the S&P per series). Read the numbers
   directly rather than re-deriving or guessing at what produced them.
3. Summarize using the actual printed values: overall bull score,
   cash-on-sidelines %, breadth of trend-violation across the
   index/sector universe, HY spread level and trend, curve shape, USD
   trend, and any series correlation/lead-lag worth noting.
4. `bull_score` is a relative composite, not a calibrated probability —
   don't quote it with more confidence than that. See
   `$CLAUDE_PLUGIN_ROOT/CLAUDE.md`'s "Data provenance & limitations"
   section for the full caveats (yfinance/FRED data quality, what each
   score does and doesn't mean) before writing anything that leans on
   this read.

If asked for a full market outlook rather than just the macro piece, use
the `market-outlook` skill instead — it orchestrates this skill's output
together with equities/commodities/crypto.
