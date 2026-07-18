---
name: crypto-research
description: Ranks BTC/ETH plus 16 liquid large-cap altcoins by BTC-benchmarked leadership and opportunity, and computes a 0-100 risk score / risk-off read for the crypto market (Crypto). Use when the user asks about Bitcoin, Ethereum, altcoins, crypto market risk, or wants a fast risk-appetite check.
argument-hint: "[optional: specific coin ticker, or leave blank for the default universe]"
allowed-tools: Bash
---

# Crypto research

Pull the current crypto risk/leadership read for: $ARGUMENTS (or the
default universe if no argument was given).

1. Run the report:
   ```bash
   cd "$CLAUDE_PLUGIN_ROOT/Crypto" && uv run python -m crypto_structure.report
   ```
2. It prints the formula legend, the overall risk gauge, the
   leadership/opportunity ranking table (BTC-benchmarked), then a
   per-asset breakdown (trend/RR/violation contributions, support cluster
   stack, trendline detail) — every number is traceable to the term that
   produced it, same discipline as `Macro/market-structure`.
3. Crypto tends to be the fastest, most liquid risk-on/risk-off barometer
   of the four research sets — when asked for a broader market view, flag
   explicitly if crypto's risk score has turned before equities/credit
   have (a leading-indicator signal), not just report it as an isolated
   number.

`risk_score` is a relative composite (same formula as
`market-structure`'s `bull_score`, relabeled since crypto has no literal
cash-on-sidelines concept) — not a calibrated probability. See
`$CLAUDE_PLUGIN_ROOT/CLAUDE.md`'s "Data provenance & limitations" section
for coverage caveats (large-cap only, no on-chain data, 3-day staleness
gate for the 24/7 market).
