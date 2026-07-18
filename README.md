# Market Research Suite
<img width="1672" height="941" alt="exec-1fb85d97-f0b0-4385-a415-ffa31043a41d" src="https://github.com/user-attachments/assets/7177b649-ba6e-4eb6-96b6-f038c7b0aeec" />

A single Claude Code plugin that exposes two skills over four cross-asset
research engines (macro, equities, commodities, crypto) plus a qualitative
industry-expertise knowledge base: `market-outlook`, which compiles every
engine into one market outlook/opinion piece, and `industry-research`, which
grounds analysis in an industry's structure and economics via the MCP
server. The repository root is the plugin root.

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
│   ├── industry-research/         39 sector/industry reference modules (MCP-backed)
│   └── market-outlook/            compiles every engine into one outlook/opinion piece
├── Macro/Rates/                   Python engine (uv), driven by market-outlook
├── Macro/market-structure/        Python engine (uv), driven by market-outlook
├── Equities/equity-rotation/      Python engine (uv), driven by market-outlook
├── Commodities/                   Python engine (uv), driven by market-outlook
├── Crypto/                        Python engine (uv), driven by market-outlook
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

- "Write me a market outlook piece." / "What's happening in markets right
  now?" / "Risk-on or risk-off, and what's leading?" → `market-outlook`
  (compiles all four engines + industry grounding + primary-source
  enrichment into one piece)
- "What drives margins in the semiconductor equipment industry?" →
  `industry-research`

Or invoke either skill directly:

```text
/market-research:market-outlook "focus on rate-sensitive sectors"
/market-research:industry-research "Analyze the industry context for a regional bank"
```

The MCP server (`industry-expertise`) exposes:

- `list_industries` — the supported sector/industry taxonomy.
- `get_industry_expertise` — a full module or section, character-paginated.
- `search_industry_expertise` — full-text search across all modules.
- `industry-expertise://<sector>/<industry>` resources.
- `investigate-industry` prompt.

The four quant engines don't go through MCP — `market-outlook` shells out
directly to each toolkit's `uv run python -m <package>.report`, whose output
is deliberately self-explanatory (formula legend + per-line-item breakdown),
so Claude reads the numbers rather than reinterpreting them. They are no
longer exposed as standalone skills; `market-outlook` is the entry point
that drives them.

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
