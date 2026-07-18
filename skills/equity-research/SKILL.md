---
name: equity-research
description: Ranks the 11 GICS sector ETFs and 6 style-factor ETFs by peer/benchmark-blended leadership and opportunity, plus an RRG-style leading/weakening/lagging/improving quadrant read (Equities/equity-rotation). Use when the user asks which sectors or factors are leading, what's being bought right now, sector/factor rotation, or relative equity performance.
argument-hint: "[optional: specific sector/factor ticker, or leave blank for the full ranking]"
allowed-tools: Bash
---

# Equity rotation research

Pull the current sector/factor rotation read for: $ARGUMENTS (or the full
default universe if no argument was given).

1. Run the report:
   ```bash
   cd "$CLAUDE_PLUGIN_ROOT/Equities/equity-rotation" && uv run python -m equity_rotation.report
   ```
2. It prints three plain-text tables: sector ranking, factor ranking, and
   a combined RRG-style relative-technicals table. Read the numbers
   directly — `leadership`, `opportunity`, and `joint` are already
   computed composites, not raw data you need to reinterpret.
3. Note explicitly when the RRG quadrant (leading/weakening/lagging/
   improving) disagrees with the leadership/opportunity ranking for the
   same ticker — this happens by design (two different models of "leading"
   over different horizons) and is usually more informative to call out
   than either read alone.
4. When a specific sector stands out (top-ranked, or a notable
   quadrant/leadership disagreement), use the `industry-research` skill
   next to ground *why* it's moving in that sector's actual structure,
   economics, and competitive dynamics — this skill only tells you *what*
   is moving.

`leadership`/`opportunity`/`joint` are relative composite scores, not
calibrated probabilities — see `$CLAUDE_PLUGIN_ROOT/CLAUDE.md`'s "Data
provenance & limitations" section before writing anything that leans on
this read.
