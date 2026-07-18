# Design: Outlook report tool + Commodities speed-up + skill prune

**Date:** 2026-07-18
**Status:** Approved

## Problem

Two requests against the `market-research` plugin:

1. Make a **reports tool** that goes out, compiles every research read, and
   writes a market-outlook *article* in the spirit of a provided example —
   as **guideline principles, not a hard template**.
2. The **Commodities** run is too slow ("the ML logic is too complex causing
   the shell to run for too long"); fix it.

Plus a scoping instruction taken during brainstorming: **prune the plugin's
skill surface** down to just the report skill and the subject-knowledge
(industry-expertise) skill; remove the other four research-set skill
wrappers.

## Decisions (from brainstorming)

- **Data sourcing for the article:** *Hybrid.* The four Python research
  engines are the quantitative spine; the skill also does primary-source web
  research (FRED, EIA, BLS/GDPNow, FactSet, VIX/Cboe, NAAIM/AAII) to ground
  the narrative **and to cross-check/challenge the tools' composite scores**,
  exactly as the example article does (e.g. it flags market-structure's
  "cash on the sidelines" reading as suspect against NAAIM/AAII).
- **Commodities fix:** *Speed-only refactor.* No methodology change; outputs
  stay identical. Keep the full statistical rigor the project's `CLAUDE.md`
  emphasizes.
- **Skill surface:** keep only `market-outlook` and `industry-research`.

## Part A — Prune the skill surface to two

The plugin registers skills via `"skills": "./skills/"` (directory
auto-discovery), so removing a skill = deleting its directory.

- **Keep:** `skills/market-outlook/`, `skills/industry-research/`.
- **Delete:** `skills/macro-research/`, `skills/equity-research/`,
  `skills/commodities-research/`, `skills/crypto-research/`.
- **Unchanged:** the underlying Python engines (`Macro/`, `Equities/`,
  `Commodities/`, `Crypto/`) and the `server/` MCP server. `market-outlook`
  invokes the Python directly (`uv run python -m ...`), not the sub-skills,
  so deleting the wrappers does not break orchestration.
- **Docs/manifest scrub:** remove the four skill names from `plugin.json`
  keywords, `marketplace.json` tags, and update `README.md` + top-level
  `CLAUDE.md` prose to describe a plugin that now exposes exactly two skills
  over the same engines + MCP server. `Equities/CLAUDE.md`'s reference is to
  the equity-rotation *project*, not the skill wrapper — leave engine docs
  intact; only fix references that describe the removed *skills*.

## Part B — `market-outlook` becomes the article/report tool

Rewrite `skills/market-outlook/SKILL.md`. It stays an orchestration +
synthesis skill (produces no data itself).

1. **Keep** the "gather every read first" step (run the four `uv run python
   -m *.report` commands in parallel + the `industry-expertise` MCP calls).
2. **`allowed-tools`:** add `WebSearch` and `WebFetch` alongside `Bash` and
   the `industry-expertise` MCP tools (exa web tools acceptable as a
   fallback if present).
3. **Hybrid enrichment step:** after gathering the tool reads, pull
   primary-source data to (a) ground the narrative with real figures and
   citations and (b) **cross-check and, where warranted, challenge** the
   tools' composite scores. Named sources to reach for when relevant: FRED
   series (nominal/real yields, breakevens, HY OAS), EIA (energy), BLS +
   Atlanta Fed GDPNow (growth/inflation/labor), FactSet (earnings), Cboe
   (VIX/correlation), NAAIM/AAII (positioning/sentiment). Be explicitly
   skeptical when a composite looks off rather than parroting it.
4. **Article-craft principles** (framed as guidelines to adapt, explicitly
   NOT a fixed template — do not force the example's oil/Hormuz framing):
   - Lead with a **thesis + causal chain** (catalyst → transmission →
     outcome), not a data dump.
   - Preserve the synthesis arc: regime backdrop → what's being bought →
     why (industry grounding) → cross-asset (commodities) → fastest-mover
     (crypto) → **write the divergences, not just the agreements**.
   - **Cite sources.** Keep price levels internally consistent (one
     stop/target engine — don't mix tile levels with narrative levels).
   - **Separate observation / forecast / opinion explicitly**; only
     Commodities' `up_probability` is a calibrated probability — everything
     else (`bull_score`, `risk_score`, leadership/opportunity) is a relative
     composite, not a probability.
   - Close with a **scenario state-vector** (named regimes with numeric
     triggers) and a **watch-hierarchy** (what to watch first, second, …).
5. Keep the pointer to top-level `CLAUDE.md` for methodology/provenance
   depth.

## Part C — Commodities speed-only refactor

**Root cause:** `ranking.build_rankings` calls `build_training_matrix` once
per horizon (5/21/63d). Each call re-runs the full feature replay — HAC
trend regressions + the risk/reward pivot engine + ADF/cointegration — over
~86 as-of dates × ~25 commodities. But `flatten_feature_row` does **not**
depend on the horizon; only the labels (`forward_return`/`forward_direction`)
do. So ~2/3 of the heaviest compute is redundant.

**Fix (identical outputs):**

- Add `build_feature_matrix(data, include_curve=False) -> pd.DataFrame` in
  `features.py`: one row per `(canonical_id, as_of)` with feature columns
  only (plus `canonical_id`, `family`, `as_of`) — the current per-as_of
  replay done **once**, over the union of as-of dates from the label grid.
- Re-express `build_training_matrix(data, label_panel, include_curve=False)`
  as `build_feature_matrix` + a pandas merge with `label_panel` on
  `(canonical_id, as_of)`. Its returned DataFrame (columns, dtypes, row set,
  values) must be **unchanged** so existing tests and callers keep working.
- Refactor `build_rankings` to compute `build_feature_matrix` **once** and,
  per horizon, merge with `label_panel[label_panel.horizon_days == h]` —
  feeding `derive_component_weights` and the production `fit_horizon_models`
  the exact same per-horizon rows/values as before.

**Equivalence guarantee:** the per-horizon panel that `build_rankings` feeds
the models must equal (same rows, same values, ignoring row order — sort
before compare) what the old code produced via
`build_training_matrix(data, label_panel[horizon==h])`.

### Testing (TDD, per repo rules)

- Write, first (RED): a test asserting `build_feature_matrix` returns one
  row per `(canonical_id, as_of)` (no `horizon_days`/label columns) over a
  small synthetic `UniverseData`.
- Write, first (RED): an **equivalence test** — for each horizon, the
  merged (feature-matrix ⋈ labels) panel equals the legacy
  `build_training_matrix` output (sorted, same columns/values).
- Keep the existing 57 tests green; synthetic data via
  `np.random.default_rng(seed)`, no live network (monkeypatch at fetch
  boundaries), matching the project's conventions.

## Verification

- `cd Commodities && uv run pytest -q` → all green.
- Timed small-universe `build_report` before vs. after → demonstrate the
  speedup (expect ≈3× on the feature-build portion).
- Dry check that `market-outlook`'s orchestration commands still resolve
  (paths + module entry points exist).
- Confirm only `market-outlook` and `industry-research` remain under
  `skills/`, and no dangling references to the removed skills in
  manifest/README/CLAUDE.

## Out of scope

- No change to the statistical model math (estimators, folds, grid, solver
  settings) — speed-only.
- No new fetch of external data *inside* the Python engines; web enrichment
  lives in the `market-outlook` skill layer.
- Crypto/equity-rotation duplicated math is untouched.

## Files expected to change

- Delete: `skills/{macro-research,equity-research,commodities-research,crypto-research}/`
- Edit: `skills/market-outlook/SKILL.md`
- Edit: `Commodities/commodities/features.py`, `Commodities/commodities/ranking.py`
- Add/Edit: `Commodities/tests/test_features.py` (equivalence + shape tests)
- Edit: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`,
  `README.md`, `CLAUDE.md`
