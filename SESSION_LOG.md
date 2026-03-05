# Reposcape Session Log

This file tracks what shipped each autonomous session.

---

## Session 1

**Focus:** repo cloning and core analysis skeleton.

**Shipped:**
- Repo cloner (`src/clone.py`) + git log parser (`src/gitlog.py`)
- Language breakdown analyzer (`src/languages.py`)
- Basic CLI entrypoint (`reposcape_cli.py`)
- Test harness and initial test suite

---

## Session 2

**Focus:** commit frequency heatmap and file tree map.

**Shipped:**
- Commit frequency heatmap generator (`src/heatmap.py`)
- File tree analyzer + treemap data (`src/treemap.py`)

---

## Session 3

**Focus:** contributor stats and commit quality.

**Shipped:**
- Contributor stats engine (`src/contributors.py`)
- Author velocity tracking (`src/velocity.py`)
- Commit message quality analyzer (`src/commit_quality.py`)

---

## Session 4

**Focus:** dependency graph + complexity heatmap.

**Shipped:**
- Dependency graph (Python/JS/TS import parsing) (`src/dependencies.py`)
- Code complexity heatmap (cyclomatic complexity per file) (`src/complexity.py`)

---

## Session 5

**Focus:** timeline + PR velocity + tech debt.

**Shipped:**
- Commit timeline (`src/timeline.py`)
- PR velocity tracker (`src/pr_velocity.py`)
- Tech debt scorer (`src/techdebt.py`)

---

## Session 6 (2026-03-01)

**PR:** #14 (squash merged)

### Focus
Web frontend: landing page + initial dashboard.

### Shipped
- Landing page with repo URL input.
- Visualization dashboard with initial summary and treemap.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 7 (2026-03-01)

**PR:** #15 (squash merged)

### Focus
Dashboard: expand analyze payload and add caching.

### Shipped
- Expanded `/api/analyze` payload with more analyzers.
- Basic caching of analysis results (in-memory).

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 8 (2026-03-01)

**PR:** #16 (squash merged)

### Focus
Dashboard: render all analyzers.

### Shipped
- Dashboard renders timeline, heatmap, tech debt, complexity, PR velocity, commit message quality.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 9 (2026-03-01)

**PR:** #17 (squash merged)

### Focus
Share cards (Open Graph images).

### Shipped
- Open Graph image generator + share card route.

### Tests
- `python -m pytest tests/web/test_og.py -q --tb=short`

---

## Session 10 (2026-03-02)

**PR:** #18 (squash merged)

### Focus
Export system (HTML snapshot download).

### Shipped
- Export endpoint that returns a self-contained HTML dashboard snapshot.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 11 (2026-03-02)

**PR:** #19 (squash merged)

### Focus
Nightshift showcase.

### Shipped
- Showcase page using a pre-generated demo for `nightshift`.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 12 (2026-03-02)

**PR:** #20 (squash merged)

### Focus
Story pages.

### Shipped
- Per-repo story pages with OG meta tags wired to share cards.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 13 (2026-03-02)

**PR:** #21 (squash merged)

### Focus
Docs page and dashboard polish.

### Shipped
- `/docs` route with basic documentation.
- Dashboard: small UI polish improvements.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 14 (2026-03-02)

**PR:** #22 (squash merged)

### Focus
Story pages: GitHub metadata.

### Shipped
- Story pages: populate subtitle/metadata (stars, primary language, last updated) from GitHub metadata.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 15 (2026-03-02)

**PR:** #23 (squash merged)

### Focus
Export: SVG -> PNG and iframe embed.

### Shipped
- Export system: client-side SVG->PNG for shareable assets.
- Export system: optional iframe embed.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 16 (2026-03-02)

**PR:** #24 (squash merged)

### Focus
Share preview polish.

### Shipped
- Share preview page: per-metric chips + metadata.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 17 (2026-03-02)

**PR:** #25 (squash merged)

### Focus
Export: print-to-PDF helper.

### Shipped
- Export system: server-side print-to-PDF helper.

### Tests
- `python -m pytest tests/test_export.py -q --tb=short`

---

## Session 18 (2026-03-02)

**PR:** #26 (squash merged)

### Focus
CLI tool.

### Shipped
- CLI: `reposcape analyze <url>`.

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 19 (2026-03-02)

**PR:** #27 (squash merged)

### Focus
Packaging for `src/` layout.

### Shipped
- Packaging: fix setuptools discovery for `src/` layout.

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 20 (2026-03-03)

**PR:** #28 (squash merged)

### Focus
Metadata caching.

### Shipped
- Cache GitHub metadata lookups (stars, languages, updated) to reduce repeated calls.

### Tests
- `python -m pytest tests/test_github_meta.py -q --tb=short`

---

## Session 21 (2026-03-03)

**PR:** #29 (squash merged)

### Focus
Test suite stability.

### Shipped
- Refactor test suite for stability: module-scoped fixtures, integration markers, shared conftest.

### Tests
- `python -m pytest tests/test_clone.py -q --tb=short`
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 22 (2026-03-03)

**PR:** #30 (squash merged)

### Focus
Comparison mode.

### Shipped
- `/api/compare` endpoint.
- Dashboard: compare mode UI.

### Tests
- `python -m pytest tests/test_compare.py -q --tb=short`

---

## Session 23 (2026-03-03)

**PR:** #31 (squash merged)

### Focus
Historical tracking foundation.

### Shipped
- Snapshot bucketing + persistence utilities (`src/history.py`).

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 24 (2026-03-03)

**PR:** #32 (squash merged)

### Focus
Snapshots in CLI.

### Shipped
- Wire snapshot generation into CLI (`reposcape analyze --snapshot-dir ...`).

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 25 (2026-03-03)

**PR:** #33 (squash merged)

### Focus
Web API: snapshots.

### Shipped
- Web API: add endpoints to list snapshots + fetch a snapshot payload.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 26 (2026-03-03)

**PR:** #34 (squash merged)

### Focus
Dashboard snapshot selector.

### Shipped
- Dashboard: add snapshot selector and load snapshot payload.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 27 (2026-03-03)

**PR:** #35 (squash merged)

### Focus
GitHub Action for snapshots bundle.

### Shipped
- GitHub Action (auto-generate snapshots on release).

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 28 (2026-03-03)

**PR:** #36 (squash merged)

### Focus
Docs: snapshots UX.

### Shipped
- Docs: document how to generate and use snapshots.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 29 (2026-03-03)

**PR:** #37 (squash merged)

### Focus
Dashboard: snapshots download link.

### Shipped
- Dashboard: add "Download snapshots" link to latest release asset.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 30 (2026-03-03)

**PR:** #38 (squash merged)

### Focus
Dashboard: choose release tag/date.

### Shipped
- Dashboard: allow selecting a release tag/date for snapshot bundle.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 31 (2026-03-03)

**PR:** #39 (squash merged)

### Focus
Snapshot diff API + delta table.

### Shipped
- API: snapshot diff endpoint.
- Dashboard: delta table for snapshot diffs.

### Tests
- `python -m pytest tests/test_history_diff.py -q --tb=short`

---

## Session 32 (2026-03-04)

**PR:** #40 (squash merged)

### Focus
Fix baseline selection bug.

### Shipped
- History chart: fix baseline selection edge case when baseline snapshot missing.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 33 (2026-03-04)

**PR:** #41 (squash merged)

### Focus
Add snapshot timeline sparkline.

### Shipped
- Dashboard: add snapshot timeline sparkline.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 34 (2026-03-04)

**PR:** #42 (squash merged)

### Focus
Snapshot B metric chips.

### Shipped
- Dashboard: show snapshot metric chips (as_of, LOC, files, TODOs, debt, avg cx) when loading snapshot B.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 35 (2026-03-04)

**PR:** #43 (squash merged)

### Focus
Timeline/diff view (UI).

### Shipped
- Dashboard: adds a Timeline tab for snapshot diffs.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 36 (2026-03-04)

**PR:** #43 (squash merged)

### Focus
History: interactive chart.

### Shipped
- Dashboard: interactive History chart (SVG) using `/api/snapshots/series`.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 37 (2026-03-04)

**PR:** #44 (squash merged)

### Focus
Baseline-relative deltas on the history chart.

### Shipped
- Dashboard: when a baseline snapshot is selected for the History chart, plot and label values as deltas vs baseline (value - baselineValue).
- UI: y-axis labels now show signed deltas; `debt` deltas are formatted as percent.
- Chart: adds a dashed zero reference line when baseline is active.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 38 (2026-03-04)

**PR:** #45 (squash merged)

### Focus
Optional trendline overlay for the History chart.

### Shipped
- Dashboard History (SVG): adds an optional linear trendline overlay (least-squares fit) over the currently selected metric series.
- UI: new "Trendline" checkbox alongside Metric/Baseline selectors.
- Works for both raw series and baseline-relative delta series.

### Tests
- `python -m pytest tests/web -q --tb=short`

---

## Session 40 (2026-03-05)

**PR:** #47 (squash merged)

### Focus
History chart UX: clarify overlay normalization.

### Shipped
- Dashboard History: clarify overlay note (each selected metric is normalized to its own min..max range for comparability).

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 39 (2026-03-04)

**PR:** #46 (squash merged)

### Focus
History chart: multi-metric toggles/overlays (dashboard).

### Shipped
- Dashboard History: add checkbox toggles to overlay multiple metrics at once (each series normalized for overlay).
- Chart: adds a legend with per-metric colors; retains baseline and optional trendline controls.
- Single-series view: improves y-axis tick formatting (signed deltas and percent handling).

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 38 (2026-03-04)

**PR:** #45 (squash merged)

### Focus
Optional trendline overlay for the History chart.

### Shipped
- Dashboard History (SVG): adds an optional linear trendline overlay (least-squares fit) over the currently selected metric series.
- UI: new "Trendline" checkbox alongside Metric/Baseline selectors.
- Works for both raw series and baseline-relative delta series.

### Tests
- `python -m pytest tests/web -q --tb=short`


---

## Session 37 (2026-03-04)

**PR:** #44 (squash merged)

### Focus
Baseline-relative deltas on the history chart.

### Shipped
- Dashboard: when a baseline snapshot is selected for the History chart, plot and label values as deltas vs baseline (value - baselineValue).
- UI: y-axis labels now show signed deltas; `debt` deltas are formatted as percent.
- Chart: adds a dashed zero reference line when baseline is active.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`
