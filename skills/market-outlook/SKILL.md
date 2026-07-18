---
name: market-outlook
description: Synthesizes macro, equity, commodities, and crypto research into a market outlook or opinion piece on the current market environment. Use when the user asks for a market outlook, a view/opinion on where markets are headed, a cross-asset synthesis, or "what's happening in markets right now."
argument-hint: "[optional: focus area or specific question to frame the outlook around]"
allowed-tools: Bash
---

# Market outlook synthesis

Write a market outlook/opinion piece, focused on: $ARGUMENTS (or the
broad market if no specific focus was given). This skill does not produce
data itself — it orchestrates the other four research skills and the
`industry-expertise` MCP server, then synthesizes.

## 1. Gather every read first

Run these — independent, so run them in parallel rather than one at a
time. `$CLAUDE_PLUGIN_ROOT` is set by Claude Code to this plugin's actual
install directory, so these work regardless of where it was installed:

```bash
cd "$CLAUDE_PLUGIN_ROOT/Macro/Rates" && uv run python -m rates_macro.report
cd "$CLAUDE_PLUGIN_ROOT/Macro/market-structure" && uv run python -m market_structure.report
cd "$CLAUDE_PLUGIN_ROOT/Equities/equity-rotation" && uv run python -m equity_rotation.report
cd "$CLAUDE_PLUGIN_ROOT/Commodities" && uv run python -m commodities.report --horizon 1M --detail 5
cd "$CLAUDE_PLUGIN_ROOT/Crypto" && uv run python -m crypto_structure.report
```

For whichever sector stood out in the equity-rotation output, call the
`industry-expertise` MCP server's `get_industry_expertise` (or
`search_industry_expertise` if the classification is uncertain) to ground
the piece in that industry's actual structure and economics.

## 2. Synthesize in this order

1. **Regime backdrop** — from `Macro/Rates` + `Macro/market-structure`:
   risk-on or risk-off, and how confident is that read (bull score,
   cash-on-sidelines, credit spread trend, curve shape, USD trend,
   breadth of trend-violation across the index/sector universe).
2. **What's actually being bought** — from `equity-rotation`: leadership/
   opportunity ranking and RRG quadrants. Call out any disagreement
   between the quadrant read and the leadership score explicitly — that
   disagreement is itself informative, not noise to smooth over.
3. **Why** — the qualitative grounding pulled from `industry-expertise`
   for whichever sector stood out in step 2.
4. **Cross-asset confirmation** — from `Commodities`: does commodity
   trend/carry (and its macro-controls features) agree with the regime
   read from step 1, or diverge?
5. **Fastest-moving check** — from `Crypto`: has its risk score already
   turned ahead of equities/credit? Crypto is usually the earliest mover
   of the four.
6. **Write the divergences, not just the agreements.** Four reads
   agreeing is a higher-conviction but lower-information thesis
   ("everything says risk-on"). Four reads diverging is the more specific,
   usually more interesting thing to write about — name which model is
   the outlier and hypothesize why (e.g. a genuine leading-indicator
   lead/lag gap vs. noise).
7. **Separate observation from forecast from opinion, explicitly.** These
   tools output observations, associations, and — only for Commodities'
   `up_probability` — an actual calibrated forecast. Everything else
   (`bull_score`, `risk_score`, `leadership`/`opportunity`/`joint`) is a
   relative composite, not a probability. When the piece moves from "the
   data shows X" to "therefore Y will happen" to "therefore you should
   Z," say so in those terms instead of blending them together.

Full detail on all of the above — the shared-DNA table between projects,
per-project data provenance and limitations, and the reasoning behind this
exact synthesis order — lives in `$CLAUDE_PLUGIN_ROOT/CLAUDE.md`. Read it
if anything here is ambiguous; don't guess at a project's methodology or
caveats when that file already states them.
