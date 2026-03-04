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

**Focus:** dependency + complexity graphing.

**Shipped:**
- Dependency graph (`src/dependencies.py`)
- Complexity heatmap (`src/complexity.py`)

---

## Session 5

**Focus:** timeline + PR velocity.

**Shipped:**
- Commit timeline (`src/timeline.py`)
- PR velocity tracker (`src/pr_velocity.py`)
- Tech debt scorer (`src/techdebt.py`)

---

## Session 6

**Focus:** initial web UI.

**Shipped:**
- FastAPI web app skeleton (`src/web/app.py`)
- Dashboard template and basic analyze wiring (`src/web/templates/dashboard.html`)
- Landing page + URL input (`src/web/templates/index.html`)

---

## Session 7

**Focus:** expand analyze payload + basic caching.

**Shipped:**
- Expand analyze payload to include additional analyzers
- Add basic caching layer to avoid repeated analysis
- Dashboard renders more analyzers

---

## Session 8

**Focus:** expand dashboard visualizations.

**Shipped:**
- Dashboard renders timeline, heatmap, tech debt, complexity sections
- Added basic section cards and status labels

---

## Session 9

**Focus:** share cards.

**Shipped:**
- Open Graph image generator (`src/web/og.py`)
- Share preview route + template

---

## Session 10

**Focus:** export system.

**Shipped:**
- HTML snapshot export for analysis payloads
- Printable export workflow

---

## Session 11

**Focus:** showcase.

**Shipped:**
- Nightshift showcase route and pre-generated demo assets

---

## Session 12

**Focus:** story pages.

**Shipped:**
- Story pages wired to share cards and OG meta tags

---

## Session 13

**Focus:** quality and cleanup.

**Shipped:**
- Minor rendering/formatting improvements

---

## Session 14

**Focus:** story metadata.

**Shipped:**
- Story pages: populate metadata (stars, primary language, last updated)

---

## Session 15

**Focus:** export enhancements.

**Shipped:**
- Client-side SVG->PNG export + iframe embed option

---

## Session 16 (2026-03-02)

**PR:** #19 (squash merged)

### Focus
Dashboard snapshots: timeline sparkline + UX polish.

### Shipped
- Dashboard: adds snapshot timeline sparkline (small SVG) for snapshot list.
- Dashboard: makes snapshot list a little more scannable.

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 17 (2026-03-02)

**PR:** #20 (squash merged)

### Focus
Snapshot bundle selection + snapshot ZIP link improvements.

### Shipped
- Dashboard: allow selecting release tag/date for the snapshot bundle download.
- Dashboard: link to `reposcape-snapshots.zip` asset for the selected release.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 18 (2026-03-02)

**PR:** #21 (squash merged)

### Focus
CLI: make `reposcape analyze` work for local clones.

### Shipped
- CLI: `reposcape analyze` can analyze a local folder path.
- CLI: more helpful error message when path is missing.

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 19 (2026-03-02)

**PR:** #22 (squash merged)

### Focus
Fix packaging for `src/` layout.

### Shipped
- Packaging: ensure `pip install -e .` finds `src/` packages.
- CLI entrypoint moved to package.

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 20 (2026-03-02)

**PR:** #23 (squash merged)

### Focus
Dashboard: add “Download snapshots” link.

### Shipped
- Dashboard: when snapshots are present, show a “Download snapshots” link.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 21 (2026-03-03)

**PR:** #24 (squash merged)

### Focus
Stabilize tests and reduce fixture duplication.

### Shipped
- Tests: convert multiple fixtures to module-scoped
- Tests: add shared conftest + integration marker

### Tests
- `python -m pytest tests -q --tb=short` (note: may be slow)

---

## Session 22 (2026-03-03)

**PR:** #25 (squash merged)

### Focus
Comparison mode.

### Shipped
- Web: `/compare` route and template
- API: `/api/compare` endpoint
- UI: side-by-side cards for two repos

### Tests
- `python -m pytest tests/test_clone.py -q --tb=short`

---

## Session 23 (2026-03-03)

**PR:** #26 (squash merged)

### Focus
History: snapshot bucketing + persistence.

### Shipped
- `src/history.py`: bucketing, snapshot IO, and snapshot directory layout

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 24 (2026-03-03)

**PR:** #27 (squash merged)

### Focus
CLI: wire snapshot generation.

### Shipped
- CLI: `--snapshot-dir` option for `reposcape analyze`
- CLI: `--as-of` label for snapshot naming

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 25 (2026-03-03)

**PR:** #28 (squash merged)

### Focus
Web API: list and fetch snapshots.

### Shipped
- API: `/api/snapshots/list` and `/api/snapshots/get`

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 26 (2026-03-03)

**PR:** #29 (squash merged)

### Focus
Dashboard UI: snapshot selector.

### Shipped
- Dashboard: snapshot selector dropdown
- Dashboard: load snapshot payload into dashboard

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 27 (2026-03-03)

**PR:** #30 (squash merged)

### Focus
GitHub Action: auto-generate snapshots on release.

### Shipped
- GitHub Action workflow for snapshot generation

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 28 (2026-03-03)

**PR:** #31 (squash merged)

### Focus
Story/share polish.

### Shipped
- Story: improve metadata layout and OG defaults

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 29 (2026-03-04)

**PR:** #32 (squash merged)

### Focus
Dashboard: link snapshots ZIP asset to latest release.

### Shipped
- Dashboard: show “Download snapshots” link to `reposcape-snapshots.zip` on latest GitHub release.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 30 (2026-03-04)

**PR:** #33 (squash merged)

### Focus
Dashboard: allow selecting snapshot bundle release tag/date.

### Shipped
- Dashboard: add a release selector for snapshot bundle downloads.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 31 (2026-03-04)

**PR:** #34 (squash merged)

### Focus
Snapshot diff: API + delta table.

### Shipped
- API: snapshot diff endpoint
- Dashboard: delta table comparing two snapshots

### Tests
- `python -m pytest tests/test_history_delta.py -q --tb=short`

---

## Session 32 (2026-03-04)

**PR:** #35 (squash merged)

### Focus
Dashboard: snapshot timeline sparkline.

### Shipped
- Dashboard: sparkline shows snapshot density over time.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 33 (2026-03-04)

**PR:** #36 (squash merged)

### Focus
Dashboard: snapshot timeline sparkline polish.

### Shipped
- Dashboard: timeline sparkline uses normalized time axis.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 34 (2026-03-04)

**PR:** #37 (squash merged)

### Focus
Dashboard: snapshot chips.

### Shipped
- Dashboard: show snapshot metric chips (as_of, LOC, files, TODOs, debt, avg cx).

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 35 (2026-03-04)

**PR:** #42 (squash merged)

### Focus
Dashboard: timeline/diff UI.

### Shipped
- Dashboard: timeline/diff view improvements.

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
