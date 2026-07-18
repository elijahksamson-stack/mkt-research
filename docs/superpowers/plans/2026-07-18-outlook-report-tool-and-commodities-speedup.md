# Outlook Report Tool + Commodities Speed-up + Skill Prune — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `market-outlook` a compile-everything article/report tool guided by (not templated on) the example piece, cut Commodities runtime ~3× with an outputs-identical refactor, prune the plugin's skills down to `market-outlook` + `industry-research`, then version-bump and push to GitHub.

**Architecture:** Independent workstreams. (C) A pure performance refactor in `Commodities/commodities/{features,ranking}.py`: compute the horizon-independent feature matrix once, then merge each horizon's labels — no math changes. (B) A rewrite of `skills/market-outlook/SKILL.md` adding web enrichment + article-craft guideline principles. (A) Deleting four skill directories and scrubbing their names from manifest/docs. (D) Bump the plugin version and push to the `mkt-research` remote.

**Tech Stack:** Python 3, `uv`, pytest, numpy/pandas/scikit-learn (Commodities engine); Markdown + YAML frontmatter (skills); JSON (plugin manifests); git/gh (release).

## Global Constraints

- Immutability: dataclasses stay `frozen=True`; never mutate inputs — return new objects/DataFrames. (repo coding-style)
- Type annotations on all new function signatures; PEP 8; `from __future__ import annotations` at module top as in siblings.
- Missing data is `None`/`NaN`, never a fabricated neutral value. (Commodities/CLAUDE.md)
- Tests: pytest, synthetic data via `np.random.default_rng(seed)`, **no live network** — monkeypatch at fetch boundaries or pass `include_curve=False` and empty `cot_history`/`macro_series`. AAA structure, descriptive names. (repo testing rules)
- Commodities Part C is **speed-only**: no change to estimators, folds, grid step, solver settings, or output values. Per-horizon model-input rows must be identical (same rows + values) to the pre-refactor `build_training_matrix(data, label_panel[horizon==h])`.
- Run all Commodities commands from the `Commodities/` directory via `uv run`.
- Commit after each task. Attribution is disabled globally — do not add Co-Authored-By trailers.
- Remote: `origin` → `https://github.com/elijahksamson-stack/mkt-research.git`.

---

## Task 1: `build_feature_matrix` — compute features once per (commodity, as_of)

**Files:**
- Modify: `Commodities/commodities/features.py` (add `build_feature_matrix`)
- Test: `Commodities/tests/test_features.py` (create)

**Interfaces:**
- Consumes: `UniverseData`, `_bundles_for_as_of`, `flatten_feature_row`, `build_label_panel` (all already in `features.py`).
- Produces: `build_feature_matrix(data: UniverseData, label_panel: Optional[pd.DataFrame] = None, include_curve: bool = False) -> pd.DataFrame` — one row per `(canonical_id, as_of)`; columns = every key from `flatten_feature_row` plus `canonical_id`, `family`, `as_of`; **no** `horizon_days`/`forward_return`/`forward_direction`. as_of values are the unique `as_of` in `label_panel` (built via `build_label_panel(data.commodity_series)` when `label_panel is None`).

- [ ] **Step 1: Write the shared synthetic-UniverseData fixture + the failing shape test**

Create `Commodities/tests/test_features.py`:

```python
import numpy as np
import pandas as pd

from commodities.features import (
    UniverseData, build_feature_matrix, build_training_matrix,
)
from commodities.labels import build_label_panel
from commodities.market_data import CommoditySeries
from commodities.momentum import build_return_matrix
from commodities.universe import default_universe
from market_structure.market_data import OHLCV


def _synthetic_universe_data(n_bars: int = 360, n_commodities: int = 3, seed: int = 7) -> UniverseData:
    """Offline UniverseData: real CommodityInstrument entries (for valid
    family/symbol fields) paired with synthetic price series. No network:
    empty cot_history/macro_series, and callers pass include_curve=False."""
    rng = np.random.default_rng(seed)
    full = default_universe()
    cids = list(full.keys())[:n_commodities]
    universe = {cid: full[cid] for cid in cids}

    dates = pd.DatetimeIndex(pd.bdate_range("2022-01-03", periods=n_bars))
    commodity_series: dict[str, CommoditySeries] = {}
    raw_ohlcv: dict[str, OHLCV] = {}
    for cid in cids:
        steps = rng.normal(0.0002, 0.012, n_bars)
        close = 100.0 * np.exp(np.cumsum(steps))
        high = close * (1 + np.abs(rng.normal(0, 0.004, n_bars)))
        low = close * (1 - np.abs(rng.normal(0, 0.004, n_bars)))
        volume = rng.integers(1_000, 10_000, n_bars).astype(float)
        commodity_series[cid] = CommoditySeries(
            canonical_id=cid, continuous_symbol=universe[cid].continuous_symbol,
            dates=dates, raw_close=close, roll_adjusted_close=close, roll_events=(),
        )
        raw_ohlcv[cid] = OHLCV(
            ticker=universe[cid].continuous_symbol, dates=dates,
            high=high, low=low, close=close, volume=volume,
        )

    return UniverseData(
        universe=universe, commodity_series=commodity_series, raw_ohlcv=raw_ohlcv,
        return_matrix=build_return_matrix(commodity_series),
        cot_history={}, macro_series={},
    )


class TestBuildFeatureMatrix:
    def test_one_row_per_commodity_as_of_with_no_label_columns(self):
        # Arrange
        data = _synthetic_universe_data()
        label_panel = build_label_panel(data.commodity_series)

        # Act
        matrix = build_feature_matrix(data, label_panel, include_curve=False)

        # Assert: one row per (canonical_id, as_of), and no horizon/label columns
        assert not matrix.empty
        assert not matrix.duplicated(subset=["canonical_id", "as_of"]).any()
        for col in ("horizon_days", "forward_return", "forward_direction"):
            assert col not in matrix.columns
        assert {"canonical_id", "family", "as_of"}.issubset(matrix.columns)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd Commodities && uv run pytest tests/test_features.py -q`
Expected: FAIL with `ImportError: cannot import name 'build_feature_matrix'`.

- [ ] **Step 3: Implement `build_feature_matrix` in `features.py`**

Add after `build_live_bundles` (and before `NUMERIC_FIELD_PATHS`), in `Commodities/commodities/features.py`:

```python
def build_feature_matrix(
    data: UniverseData, label_panel: Optional[pd.DataFrame] = None, include_curve: bool = False
) -> pd.DataFrame:
    """One row per (canonical_id, as_of) of horizon-INDEPENDENT features.

    Features never depend on the forecast horizon -- only labels do -- so
    this is computed exactly once and reused across every horizon (see
    build_training_matrix / ranking.build_rankings). Groups by as_of so each
    date's universe-wide momentum table + macro snapshot is built once and
    reused across that date's commodities.

    `include_curve` defaults False for the same reason build_training_matrix
    does: historical dated-contract curve fetches are almost always empty and
    each miss is a real network round-trip.
    """
    label_panel = label_panel if label_panel is not None else build_label_panel(data.commodity_series)
    if label_panel.empty:
        return pd.DataFrame()

    rows: list[dict] = []
    for as_of in sorted(label_panel["as_of"].unique()):
        as_of_ts = pd.Timestamp(as_of)
        bundles = _bundles_for_as_of(data, as_of=as_of_ts, include_curve=include_curve)
        for cid, bundle in bundles.items():
            feature_row = flatten_feature_row(bundle)
            feature_row.update(canonical_id=cid, family=data.universe[cid].family, as_of=as_of_ts)
            rows.append(feature_row)
    return pd.DataFrame(rows)
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd Commodities && uv run pytest tests/test_features.py -q`
Expected: PASS (1 passed).

- [ ] **Step 5: Commit**

```bash
git add Commodities/commodities/features.py Commodities/tests/test_features.py
git commit -m "perf(commodities): add build_feature_matrix (features computed once per as_of)"
```

---

## Task 2: Re-express `build_training_matrix` as feature-matrix ⋈ labels

**Files:**
- Modify: `Commodities/commodities/features.py` (`build_training_matrix` body only — keep its signature)
- Test: `Commodities/tests/test_features.py` (add equivalence test)

**Interfaces:**
- Consumes: `build_feature_matrix` (Task 1).
- Produces: unchanged public signature `build_training_matrix(data: UniverseData, label_panel: Optional[pd.DataFrame] = None, include_curve: bool = False) -> pd.DataFrame`. Output row set + feature values unchanged vs. the pre-refactor implementation; every feature column present on the standalone matrix appears with identical values on the joined row for the same `(canonical_id, as_of)`.

- [ ] **Step 1: Write the failing equivalence test**

Add to `Commodities/tests/test_features.py`:

```python
class TestBuildTrainingMatrixEquivalence:
    def test_training_rows_carry_the_same_features_as_the_standalone_matrix(self):
        # Arrange
        data = _synthetic_universe_data()
        label_panel = build_label_panel(data.commodity_series)
        matrix = build_feature_matrix(data, label_panel, include_curve=False)

        # Act
        training = build_training_matrix(data, label_panel, include_curve=False)

        # Assert: label columns are present, and for every training row the
        # feature values equal the standalone matrix's row for that (cid, as_of).
        for col in ("horizon_days", "forward_return", "forward_direction"):
            assert col in training.columns

        feature_cols = [c for c in matrix.columns if c not in ("canonical_id", "as_of", "family")]
        key = ["canonical_id", "as_of"]
        m_indexed = matrix.set_index(key)[feature_cols].sort_index()
        # Collapse training back to one row per key (features are horizon-invariant) and compare.
        t_indexed = (
            training.drop_duplicates(subset=key).set_index(key)[feature_cols].sort_index()
        )
        assert list(t_indexed.index) == list(m_indexed.index)
        pd.testing.assert_frame_equal(
            t_indexed.reset_index(drop=True), m_indexed.reset_index(drop=True),
            check_dtype=False,
        )

    def test_row_count_matches_labels_that_have_a_feature_row(self):
        # Arrange
        data = _synthetic_universe_data()
        label_panel = build_label_panel(data.commodity_series)
        matrix = build_feature_matrix(data, label_panel, include_curve=False)

        # Act
        training = build_training_matrix(data, label_panel, include_curve=False)

        # Assert: inner join semantics -- one training row per label row whose
        # (canonical_id, as_of) produced a feature row.
        have_features = set(map(tuple, matrix[["canonical_id", "as_of"]].to_numpy()))
        expected = sum(
            1 for _, r in label_panel.iterrows()
            if (r["canonical_id"], pd.Timestamp(r["as_of"])) in have_features
        )
        assert len(training) == expected
```

- [ ] **Step 2: Run the test to verify current behavior**

Run: `cd Commodities && uv run pytest tests/test_features.py::TestBuildTrainingMatrixEquivalence -q`
Expected: the equivalence test may FAIL on column ordering / dtype before the rewrite, or pass incidentally. Either way, proceed to Step 3 so `build_training_matrix` uses the single-compute path (the test must PASS after Step 3).

- [ ] **Step 3: Rewrite `build_training_matrix` to delegate + merge**

Replace the body of `build_training_matrix` in `Commodities/commodities/features.py` (keep the `include_curve` note; update the leading sentence) with:

```python
def build_training_matrix(
    data: UniverseData, label_panel: Optional[pd.DataFrame] = None, include_curve: bool = False
) -> pd.DataFrame:
    """One row per (canonical_id, as_of, horizon_days): the horizon-independent
    feature matrix (build_feature_matrix, computed once) inner-joined to each
    forward_return/forward_direction label. Splitting features from labels this
    way is what lets ranking.build_rankings compute features a single time
    instead of once per horizon.

    `include_curve` defaults False: historical curve/carry fetches are, in
    practice, almost always empty (see market_data.fetch_dated_contract_close's
    docstring) and each miss is still a real network round-trip, so paying that
    cost by default across a multi-year x ~24-commodity panel would make this
    function impractically slow for what it returns. Pass True only if
    curve/carry training coverage specifically needs to be (re-)measured --
    expect it to still come back mostly NaN."""
    label_panel = label_panel if label_panel is not None else build_label_panel(data.commodity_series)
    if label_panel.empty:
        return label_panel

    features = build_feature_matrix(data, label_panel, include_curve=include_curve)
    if features.empty:
        return features

    labels = label_panel[["canonical_id", "as_of", "horizon_days", "forward_return", "forward_direction"]].copy()
    labels["as_of"] = pd.to_datetime(labels["as_of"])
    return features.merge(labels, on=["canonical_id", "as_of"], how="inner")
```

- [ ] **Step 4: Run the equivalence + shape tests**

Run: `cd Commodities && uv run pytest tests/test_features.py -q`
Expected: PASS (all 3 tests in the file).

- [ ] **Step 5: Commit**

```bash
git add Commodities/commodities/features.py Commodities/tests/test_features.py
git commit -m "perf(commodities): build_training_matrix delegates to build_feature_matrix + label merge"
```

---

## Task 3: `build_rankings` computes the feature matrix once

**Files:**
- Modify: `Commodities/commodities/ranking.py` (`build_rankings`, lines ~173-193)
- Test: `Commodities/tests/test_features.py` (add a `build_rankings` smoke test)

**Interfaces:**
- Consumes: `build_feature_matrix` (Task 1), `build_label_panel`, `derive_component_weights`, `fit_horizon_models`.
- Produces: `build_rankings` unchanged public behavior/return type (`RankingRun`); internally computes features once and merges per-horizon label subsets.

- [ ] **Step 1: Write the failing smoke test**

Add to `Commodities/tests/test_features.py`:

```python
class TestBuildRankingsUsesSingleFeatureCompute:
    def test_build_rankings_returns_rankings_for_the_universe(self):
        # Arrange
        from commodities.ranking import build_rankings
        data = _synthetic_universe_data()

        # Act
        run = build_rankings(data)

        # Assert: a ranking per commodity that produced a live bundle, sorted by score.
        assert run.rankings, "expected at least one ranking"
        scores = [r.commodity_opportunity_score for r in run.rankings]
        assert scores == sorted(scores, reverse=True)
        assert set(r.canonical_id for r in run.rankings).issubset(set(data.universe))
```

- [ ] **Step 2: Run the test to verify current behavior**

Run: `cd Commodities && uv run pytest tests/test_features.py::TestBuildRankingsUsesSingleFeatureCompute -q`
Expected: PASS against the current (slow, per-horizon) code — this is a behavior-preservation guard; it must still PASS after Step 3.

- [ ] **Step 3: Refactor `build_rankings` to compute features once**

In `Commodities/commodities/ranking.py`, add `build_feature_matrix` to the import from `commodities.features` (line ~39):

```python
from commodities.features import (
    FeatureBundle, UniverseData, build_feature_matrix, build_live_bundles,
    build_training_matrix, flatten_feature_row,
)
```

Then replace the per-horizon panel loop (currently lines ~177-193) — the block that starts `model_sets: dict[int, HorizonModelSet] = {}` through the end of the `for h in horizons:` loop — with:

```python
    model_sets: dict[int, HorizonModelSet] = {}
    weights_by_horizon: dict[int, ComponentWeights] = {}
    cal_err_by_horizon: dict[int, float] = {}

    # Features are horizon-independent: compute the matrix ONCE, then merge each
    # horizon's labels onto it. This replaces calling build_training_matrix per
    # horizon (which re-ran the whole feature replay 3x). Byte-identical per-horizon
    # panels, ~3x less feature compute.
    feature_matrix = build_feature_matrix(data, label_panel)
    label_cols = ["canonical_id", "as_of", "horizon_days", "forward_return", "forward_direction"]
    for h in horizons:
        labels_h = label_panel[label_panel["horizon_days"] == h][label_cols].copy()
        if feature_matrix.empty or labels_h.empty:
            continue
        labels_h["as_of"] = pd.to_datetime(labels_h["as_of"])
        panel_h = feature_matrix.merge(labels_h, on=["canonical_id", "as_of"], how="inner")
        if panel_h.empty:
            continue
        weights, cal_err = derive_component_weights(panel_h, h)
        weights_by_horizon[h] = weights
        cal_err_by_horizon[h] = cal_err

        n_calib = max(1, int(len(panel_h) * CALIBRATION_FRACTION))
        panel_h_sorted = panel_h.sort_values("as_of")
        fit_df, calib_df = panel_h_sorted.iloc[:-n_calib], panel_h_sorted.iloc[-n_calib:]
        model_set = fit_horizon_models(fit_df, h, calibration_df=calib_df)
        if model_set is not None:
            model_sets[h] = model_set
```

Note: `label_panel` is already computed earlier in `build_rankings` (line ~175: `label_panel = build_label_panel(...)`). `build_training_matrix` stays imported (still used elsewhere) — do not remove it.

- [ ] **Step 4: Run the smoke test + the whole file**

Run: `cd Commodities && uv run pytest tests/test_features.py -q`
Expected: PASS (all 4 tests).

- [ ] **Step 5: Run the full Commodities suite (no regressions)**

Run: `cd Commodities && uv run pytest -q`
Expected: PASS — all pre-existing tests (57) plus the 4 new ones green.

- [ ] **Step 6: Commit**

```bash
git add Commodities/commodities/ranking.py Commodities/tests/test_features.py
git commit -m "perf(commodities): build_rankings computes feature matrix once, merges labels per horizon"
```

---

## Task 4: Rewrite `market-outlook` into the article/report tool

**Files:**
- Modify: `skills/market-outlook/SKILL.md` (full rewrite)

**Interfaces:**
- Consumes: the four `uv run python -m *.report` engines + `industry-expertise` MCP tools (unchanged commands). Adds `WebSearch`/`WebFetch` for enrichment.
- Produces: no code interface — a skill definition. Downstream "consumers" are humans invoking `/market-outlook`.

- [ ] **Step 1: Rewrite `skills/market-outlook/SKILL.md`**

Replace the entire file with:

````markdown
---
name: market-outlook
description: Compiles every research read (macro, equities, commodities, crypto) plus industry expertise into a market outlook / opinion article. Use when the user asks for a market outlook, a view on where markets are headed, a cross-asset synthesis, or "what's happening in markets right now."
argument-hint: "[optional: focus area or specific question to frame the outlook around]"
allowed-tools: Bash, WebSearch, WebFetch
---

# Market outlook — the report tool

Compile every research read and write a market outlook / opinion article,
focused on: $ARGUMENTS (or the broad market if no focus was given). This
skill produces no data of its own — it orchestrates the four research
engines and the `industry-expertise` MCP server, enriches with
primary-source data, and synthesizes.

The example that shaped this skill is a *guideline for craft, not a
template*. Do not force its oil/Hormuz framing, its section headings, or its
exact scenarios onto a different market. Follow the principles; let the
current data pick the story.

## 1. Gather every read first

Run these in parallel (independent). `$CLAUDE_PLUGIN_ROOT` is set by Claude
Code to this plugin's install directory:

```bash
cd "$CLAUDE_PLUGIN_ROOT/Macro/Rates" && uv run python -m rates_macro.report
cd "$CLAUDE_PLUGIN_ROOT/Macro/market-structure" && uv run python -m market_structure.report
cd "$CLAUDE_PLUGIN_ROOT/Equities/equity-rotation" && uv run python -m equity_rotation.report
cd "$CLAUDE_PLUGIN_ROOT/Commodities" && uv run python -m commodities.report --horizon 1M --detail 5
cd "$CLAUDE_PLUGIN_ROOT/Crypto" && uv run python -m crypto_structure.report
```

For whichever sector stood out in the equity-rotation output, call the
`industry-expertise` MCP server (`get_industry_expertise`, or
`search_industry_expertise` if the classification is uncertain) to ground
the piece in that industry's structure and economics.

## 2. Enrich and cross-check against primary sources (hybrid)

The four engines are the quantitative spine. They are not the whole story,
and their composite scores are not above scrutiny. Use `WebSearch`/`WebFetch`
to pull current primary-source data and to **challenge** the tools where a
reading looks off:

- **Ground the narrative** with real, cited figures. Reach for, when
  relevant: FRED series (nominal yield `DGS10`, real yield `DFII10`,
  breakevens `T10YIE`, HY OAS `BAMLH0A0HYM2`); EIA (energy); BLS + Atlanta
  Fed GDPNow (growth/inflation/labor); FactSet (earnings season);
  Cboe (VIX, implied correlation); NAAIM / AAII (positioning, sentiment).
- **Cross-check the composites.** If `market-structure` reports an extreme
  "cash on the sidelines," sanity-check it against NAAIM exposure / AAII
  bulls-bears and *say so* if they disagree — do not parrot a composite that
  external positioning data contradicts. The same skepticism applies to any
  single-number reading that drives the thesis.
- Verify time-sensitive claims against the source; link it.

## 3. Synthesize — principles, in this order

1. **Lead with a thesis and a causal chain**, not a data dump. State what
   the market is doing and *why* (catalyst → transmission mechanism →
   outcome). Name the one variable that actually drives the others rather
   than treating a downstream signal as the cause.
2. **Regime backdrop** — from `Macro/Rates` + `Macro/market-structure`:
   risk-on or risk-off, and how confident that read is (bull score,
   cash-on-sidelines, credit-spread trend, curve shape, USD trend, breadth
   of trend-violation).
3. **What's actually being bought** — from `equity-rotation`: leadership /
   opportunity ranking and RRG quadrants. Call out disagreement between the
   quadrant read and the leadership score explicitly — that disagreement is
   informative, not noise. Distinguish "what's being bought this week"
   (tactical rotation) from "what owns the cycle" (durable leadership).
4. **Why** — the qualitative grounding from `industry-expertise` for the
   sector that stood out.
5. **Cross-asset confirmation** — from `Commodities`: does commodity
   trend/carry (and its macro-controls features) agree with the regime read,
   or diverge?
6. **Fastest-moving check** — from `Crypto`: has its risk score turned ahead
   of equities/credit? Crypto is usually the earliest of the four to move.
7. **Write the divergences, not just the agreements.** Four reads agreeing
   is higher-conviction but lower-information. Four diverging is the more
   specific, usually more interesting story — name the outlier and
   hypothesize why (a genuine leading-indicator lead/lag gap vs. noise).
8. **Separate observation / forecast / opinion explicitly.** Only
   Commodities' `up_probability` is a calibrated probability; `bull_score`,
   `risk_score`, `leadership`/`opportunity`/`joint` are relative composites,
   not probabilities — never quote them with equivalent confidence. When the
   piece moves from "the data shows X" to "therefore Y" to "therefore you
   should Z," mark the transition in those terms.

## 4. Craft requirements for the article

- **Cite sources** for external figures (link them). Attribute tool figures
  to the tool.
- **Keep price levels internally consistent.** If you quote a stop/target,
  they come from one engine — do not mix a tool's tile levels with different
  narrative levels as if they share one stop-and-target model.
- **Close with a scenario state-vector and a watch-hierarchy.** Give a few
  named regimes with *numeric* triggers (e.g. "spreads widen through X, VIX
  holds above Y") and state what to watch first, second, third — the
  hierarchy of drivers, not a single number.
- End with a one-line data-provenance + not-advice note.

Full methodology, the shared-DNA table between engines, and per-engine data
provenance/limitations live in `$CLAUDE_PLUGIN_ROOT/CLAUDE.md`. Read it if
anything here is ambiguous; don't guess at an engine's methodology or caveats
when that file already states them.
````

- [ ] **Step 2: Verify the frontmatter is well-formed**

Run: `head -6 skills/market-outlook/SKILL.md`
Expected: shows YAML frontmatter with `allowed-tools: Bash, WebSearch, WebFetch`.

- [ ] **Step 3: Verify the orchestration paths still resolve**

Run:
```bash
for p in Macro/Rates Macro/market-structure Equities/equity-rotation Commodities Crypto; do \
  test -d "$p" && echo "OK $p" || echo "MISSING $p"; done
```
Expected: five `OK` lines.

- [ ] **Step 4: Commit**

```bash
git add skills/market-outlook/SKILL.md
git commit -m "feat(market-outlook): article/report tool with web enrichment + article-craft principles"
```

---

## Task 5: Prune the four research skills + scrub references

**Files:**
- Delete: `skills/macro-research/`, `skills/equity-research/`, `skills/commodities-research/`, `skills/crypto-research/`
- Modify: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `README.md`, `CLAUDE.md`

**Interfaces:**
- Consumes: nothing. Produces: a two-skill plugin surface (`market-outlook`, `industry-research`).

- [ ] **Step 1: Delete the four skill directories**

```bash
git rm -r skills/macro-research skills/equity-research skills/commodities-research skills/crypto-research
```

- [ ] **Step 2: Verify only two skills remain**

Run: `ls skills/`
Expected: exactly `industry-research` and `market-outlook`.

- [ ] **Step 3: Scrub removed skill names from the manifests**

In `.claude-plugin/plugin.json`, remove `"macro-research"`, `"equity-research"`, `"commodities-research"`, `"crypto-research"` from the `keywords` array (keep `"industry-research"`, `"market-outlook"`, `"mcp"`, `"investment-research"`). Do the same for the `tags` array in `.claude-plugin/marketplace.json`. Leave `"skills": "./skills/"` and all other fields untouched.

- [ ] **Step 4: Update README.md and CLAUDE.md prose**

In `README.md` and top-level `CLAUDE.md`, update text that lists the plugin's skills so it describes exactly two: `market-outlook` (the compile-everything report/article tool) and `industry-research` (subject-knowledge via the `industry-expertise` MCP server). Note the four research engines (`Macro/`, `Equities/`, `Commodities/`, `Crypto/`) remain and are driven directly by `market-outlook`, but are no longer exposed as standalone skills. Do NOT alter the engine-methodology sections (shared-DNA table, data provenance) or `Equities/CLAUDE.md` (it documents the equity-rotation project, not the removed skill).

Find the references to update:
```bash
grep -rn -e "macro-research" -e "equity-research" -e "commodities-research" -e "crypto-research" README.md CLAUDE.md .claude-plugin/
```
Expected after editing: no matches in `.claude-plugin/`; in `README.md`/`CLAUDE.md`, surviving mentions are engine/project references, not skill listings.

- [ ] **Step 5: Verify the manifest JSON is valid**

Run: `python3 -c "import json; json.load(open('.claude-plugin/plugin.json')); json.load(open('.claude-plugin/marketplace.json')); print('valid json')"`
Expected: `valid json`.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore(plugin): prune to market-outlook + industry-research skills"
```

---

## Task 6: Final local verification

**Files:** none (verification only).

- [ ] **Step 1: Full Commodities suite green**

Run: `cd Commodities && uv run pytest -q`
Expected: all tests pass (57 pre-existing + 4 new).

- [ ] **Step 2: Demonstrate the speedup (timed small-universe build)**

Run:
```bash
cd Commodities && uv run python -c "
import time
from commodities.universe import default_universe
from commodities.report import build_report
u = dict(list(default_universe().items())[:4])
t = time.time(); r = build_report(universe=u); dt = time.time() - t
print(f'4-commodity build_report: {dt:.1f}s, {len(r[\"run\"].rankings)} ranked')
"
```
Expected: completes in seconds and prints a ranking count. (Exercises the once-compute path end-to-end against live data; if the network is unavailable, note it and rely on Step 1's synthetic-data coverage.)

- [ ] **Step 3: Confirm the pruned skill surface + intact orchestration**

Run:
```bash
ls skills/
grep -rn -e "macro-research" -e "equity-research" -e "commodities-research" -e "crypto-research" .claude-plugin/ || echo "no stale skill refs in manifests"
```
Expected: `skills/` shows only `industry-research` and `market-outlook`; no stale references in `.claude-plugin/`.

---

## Task 7: Version-bump and push to GitHub

**Files:**
- Modify: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `package.json` (version fields)

**Interfaces:**
- Consumes: a clean working tree with Tasks 1-6 committed and green.
- Produces: a new plugin version on `origin` (`mkt-research`).

- [ ] **Step 1: Bump the version in all three manifests**

Bump `version` from `0.1.0` to `0.2.0` (new feature surface: report tool + skill prune) in:
- `.claude-plugin/plugin.json` (`"version"`)
- `.claude-plugin/marketplace.json` (both the top-level `"version"` and the entry under `plugins[0].version`)
- `package.json` (`"version"`)

- [ ] **Step 2: Verify the bump is consistent**

Run: `grep -rn "0.2.0" .claude-plugin/plugin.json .claude-plugin/marketplace.json package.json`
Expected: four matches (plugin.json ×1, marketplace.json ×2, package.json ×1).

- [ ] **Step 3: Confirm the working tree is clean apart from the bump**

Run: `git status --short`
Expected: only the three manifest files modified (everything else already committed by prior tasks).

- [ ] **Step 4: Commit the version bump**

```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json package.json
git commit -m "chore(release): v0.2.0 — outlook report tool + commodities speedup + skill prune"
```

- [ ] **Step 5: Tag and push to origin**

```bash
git tag v0.2.0
git push origin main --tags
```
Expected: push succeeds to `https://github.com/elijahksamson-stack/mkt-research.git`; `v0.2.0` tag appears. If the push is rejected (auth or non-fast-forward), stop and report to the user rather than force-pushing.

- [ ] **Step 6: Report the release**

Confirm the pushed commit + tag and summarize what shipped.

---

## Self-Review

**Spec coverage:**
- Part A (prune to two skills + scrub) → Task 5. ✓
- Part B (market-outlook rewrite: hybrid enrichment, article-craft, allowed-tools) → Task 4. ✓
- Part C (build_feature_matrix; build_training_matrix delegates; build_rankings once; equivalence tests) → Tasks 1-3. ✓
- Verification (pytest, timed run, skill-surface check) → Task 6. ✓
- New instruction (version-bump + push) → Task 7. ✓

**Placeholder scan:** No TBD/TODO; every code step shows complete code; commands have expected output. ✓

**Type consistency:** `build_feature_matrix(data, label_panel=None, include_curve=False)` used identically in Tasks 1, 2, 3. `build_training_matrix` signature preserved. Merge keys `["canonical_id","as_of"]` and label columns `["canonical_id","as_of","horizon_days","forward_return","forward_direction"]` consistent across Tasks 2, 3. Version `0.2.0` consistent across Task 7. ✓
