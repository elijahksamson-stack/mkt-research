# Market Research Suite

A single Claude Code plugin unifying four cross-asset research toolkits —
macro, equities, commodities, and crypto — plus a qualitative
industry-expertise knowledge base and a synthesis skill for writing market
outlook/opinion pieces. The repository root is the plugin root.

This plugin replaces what used to be a separate, standalone
`industry-expertise` plugin (formerly `Equities/sector-lvl-expertise/`,
still preserved at its original GitHub remote,
`elijahksamson-stack/industry-expert-plugin`, for history) — everything now
lives under one `.claude-plugin/` here instead of one sub-plugin per
research area.

## Project structure

```text
.
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── .mcp.json
├── server/                        industry-expertise MCP server (Node, stdio)
├── skills/
│   ├── macro-research/            Macro/Rates + Macro/market-structure
│   ├── equity-research/           Equities/equity-rotation
│   ├── industry-research/         39 sector/industry reference modules (MCP-backed)
│   ├── commodities-research/      Commodities
│   ├── crypto-research/           Crypto
│   └── market-outlook/            synthesizes all of the above into one piece
├── Macro/Rates/                   Python toolkit (uv), invoked via macro-research
├── Macro/market-structure/        Python toolkit (uv), invoked via macro-research
├── Equities/equity-rotation/      Python toolkit (uv), invoked via equity-research
├── Commodities/                   Python toolkit (uv), invoked via commodities-research
├── Crypto/                        Python toolkit (uv), invoked via crypto-research
├── package.json
├── README.md                      this file (plugin-facing: install, components)
└── CLAUDE.md                      dev-facing: full methodology, shared DNA, limitations
```

The marketplace entry uses `"source": "./"`, so Claude Code copies this
repository root as the plugin. The marketplace slug is `market-research`;
its user-facing label is controlled by `displayName` in
`.claude-plugin/plugin.json`.

## Install

From the published repository:

```text
/plugin marketplace add elijahksamson-stack/mkt-research
/plugin install market-research@market-research
/reload-plugins
```

For local development, use an absolute path instead:

```text
/plugin marketplace add /absolute/path/to/this/repository
/plugin install market-research@market-research
/reload-plugins
```

Use `/mcp` to confirm `industry-expertise` is connected.

## Use

Ask Claude naturally — each skill's `description` is written to trigger on
the kind of question it answers:

- "What's the macro regime right now — risk-on or risk-off?" → `macro-research`
- "Which sectors are leading right now?" → `equity-research`
- "What drives margins in the semiconductor equipment industry?" → `industry-research`
- "Give me a commodities outlook for the next month." → `commodities-research`
- "How's crypto's risk appetite looking?" → `crypto-research`
- "Write me a market outlook piece." → `market-outlook` (orchestrates all five)

Or invoke any skill directly:

```text
/market-research:macro-research
/market-research:equity-research
/market-research:industry-research "Analyze the industry context for a regional bank"
/market-research:commodities-research 3M
/market-research:crypto-research
/market-research:market-outlook "focus on rate-sensitive sectors"
```

The MCP server (`industry-expertise`) exposes:

- `list_industries` — the supported sector/industry taxonomy.
- `get_industry_expertise` — a full module or section, character-paginated.
- `search_industry_expertise` — full-text search across all modules.
- `industry-expertise://<sector>/<industry>` resources.
- `investigate-industry` prompt.

The four quant skills don't go through MCP — they shell out directly to
each toolkit's `uv run python -m <package>.report`, whose output is
deliberately self-explanatory (formula legend + per-line-item breakdown),
so Claude reads the numbers rather than reinterpreting them.

## Prerequisites

- Node.js 18+ (MCP server)
- [`uv`](https://docs.astral.sh/uv/) (Python toolkits) — each of
  `Macro/Rates`, `Macro/market-structure`, `Equities/equity-rotation`,
  `Commodities`, `Crypto` is independently `uv sync`-able; run that once
  per directory before first use.

## Develop and validate

```bash
npm test               # node --test server/index.test.js
npm run validate:plugin
npm run check
```

For the Python toolkits, `cd` into each directory and run `uv run pytest -q`.

## Publishing

Published at `elijahksamson-stack/mkt-research`. The plugin version
appears in `package.json`, `.claude-plugin/plugin.json`, and
`.claude-plugin/marketplace.json`; bump all three when publishing a
release.

See `CLAUDE.md` for the full methodology behind each research set, how
they share (or intentionally duplicate) underlying math, and the data
provenance/limitations to know before trusting any single number.
