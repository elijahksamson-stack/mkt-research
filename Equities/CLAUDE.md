# Equities

Two halves of one equities toolset, now unified as skills in the
Blog-level `market-research` plugin (`/Users/elisamson/Desktop/Blog/`)
rather than each living behind its own interface:

- **Industry expertise** (qualitative) -- was a standalone plugin at
  `Equities/sector-lvl-expertise/` (its own `.claude-plugin/`, MCP server,
  git history); that directory no longer exists here. Its 39
  sector/industry research modules, MCP server, and routing skill were
  folded into the unified plugin's `skills/industry-research/` and
  `server/` at the Blog root. Original git history is preserved at its
  GitHub remote, `elijahksamson-stack/industry-expert-plugin`, untouched.
  Answers "what do I need to know about this industry to interpret what
  I'm seeing."

- **`equity-rotation/`** (quantitative) -- still lives here as a plain
  Python `uv`-managed project; the unified plugin's `market-outlook` skill
  drives it via `uv run python -m equity_rotation.report` rather than
  wrapping it in its own MCP server. Ranks the 11 GICS sector ETFs and 6
  style-factor ETFs by peer/benchmark-blended leadership + opportunity,
  plus an RRG-style relative-technicals table (data only, no charts).
  Answers "what is the market currently pricing across sectors and
  factors, and is it still attractive."

Run `uv run python -m equity_rotation.report` from `equity-rotation/` for
a live snapshot; see that directory's `CLAUDE.md` for the full module map.
For the plugin-level view (skills, MCP server, install instructions), see
`/Users/elisamson/Desktop/Blog/README.md` and `CLAUDE.md`.

## Why the fold-in happened now

The previous split ("not yet one MCP -- `equity-rotation` still settling")
was superseded by a decision to unify *all four* research sets (Macro,
Equities, Commodities, Crypto) under one plugin at once, not just the two
equities halves. The quant toolkits (including `equity-rotation`) are
exposed as skills that shell out to their existing `report.py` CLIs rather
than each getting a bespoke MCP server -- this matches Claude Code's own
guidance to prefer skills over MCP for local CLI actions, and meant
`equity-rotation` didn't need its interface "finalized" first the way an
MCP server would have required. Use them together as before: pull the
quant read from the `equity-rotation` engine to see *which* sectors/factors
are moving, then pull qualitative context from `industry-research` to
understand *why*.
