---
name: industry-research
description: Ground company, security, sector, and thematic investment research in the relevant industry's structure, economics, value chain, operating mechanics, competitive dynamics, regulation, geography, risks, and disruption. Use whenever an investment investigation needs industry-level context.
argument-hint: "[company, ticker, sector, industry, or research question]"
---

# Industry research

Use the bundled `industry-expertise` MCP server to add subject-level context to: $ARGUMENTS

1. Identify the relevant sector and industry. If the classification is uncertain, call `list_industries` before selecting a module.
2. Call `get_industry_expertise` for the selected industry. Retrieve only the sections needed for the investigation; use character pagination when a full section is too large.
3. Call `search_industry_expertise` when the question spans industries or requires a narrow concept, metric, technology, regulation, geography, or failure pattern.
4. Apply the module to the company or security: locate it in the value chain, identify its economic drivers and bottlenecks, distinguish durable advantages from cycle effects, and map external forces to risks, catalysts, and valuation.
5. Treat the modules as orientation, not as a substitute for current evidence. Verify time-sensitive claims, rules, market data, and company facts against current primary sources.

State which industry module you used. Clearly separate sourced facts, estimates, and your own inferences.
