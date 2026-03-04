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

**Focus:** dependency graph + complexity analysis.

**Shipped:**
- Dependency graph analyzer (`src/dependencies.py`)
- Complexity analyzer (`src/complexity.py`)

---

## Session 5

**Focus:** timeline + PR velocity + tech debt.

**Shipped:**
- Commit timeline analyzer (`src/timeline.py`)
- PR velocity tracker (`src/pr_velocity.py`)
- Tech debt scorer (`src/techdebt.py`)

---

## Session 6

**Focus:** web frontend initial landing page + dashboard.

**Shipped:**
- FastAPI web app skeleton (`src/web/app.py`)
- Landing page with repo URL input (`src/web/templates/index.html`)
- Visualization dashboard initial view (`src/web/templates/dashboard.html`)
- Simple CSS (`src/web/static/styles.css`)

---

## Session 7

**Focus:** richer analyze payload + caching.

**Shipped:**
- Expanded analyze payload to include all analyzers
- Added basic caching to avoid repeated analyses
- Dashboard updated with additional sections

---

## Session 8

**Focus:** dashboard visualizations.

**Shipped:**
- Dashboard now renders additional analysis views (timeline, heatmap, tech debt, complexity)

---

## Session 9

**Focus:** share cards.

**Shipped:**
- Open Graph share card generator (`/og/...` endpoints)

---

## Session 10

**Focus:** export system.

**Shipped:**
- Added HTML export (printable to PDF)
- Added a dashboard export view

---

## Session 11

**Focus:** Nightshift showcase.

**Shipped:**
- Added a "showcase" route with pre-generated demo for nightshift repo

---

## Session 12

**Focus:** story pages.

**Shipped:**
- Per-repo story pages + OG meta tags wired to share cards

---

## Session 13 (2026-03-02)

**PR:** #23 (squash merged)

### Focus
Improve README + packaging experience.

### Shipped
- Refreshed README for clear install/run directions.
- Ensured `reposcape` is the entrypoint module, not `reposcape_cli`.

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 14 (2026-03-02)

**PR:** #24 (squash merged)

### Focus
Story page metadata improvements.

### Shipped
- Story page subtitle now populates stars, primary language, and last updated timestamp from GitHub.
- Added an "as of" timestamp to the story page.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 15 (2026-03-02)

**PR:** #25 (squash merged)

### Focus
SVG -> PNG export helpers.

### Shipped
- Client-side SVG -> PNG export for shareable assets.
- Export page: added optional iframe embed code.

### Tests
- `python -m pytest tests/test_timeline.py -q --tb=short`

---

## Session 16 (2026-03-02)

**PR:** #26 (squash merged)

### Focus
Ensure story pages are SEO-friendly.

### Shipped
- Story pages now include a canonical link to the public story URL.
- Story pages add robots tags to discourage indexing local development URLs.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 17 (2026-03-02)

**PR:** #27 (squash merged)

### Focus
PDF export support.

### Shipped
- Added server-side PDF export generation via Playwright (optional dependency).
- Documented print-to-PDF fallback flow.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 18 (2026-03-02)

**PR:** #28 (squash merged)

### Focus
CLI analysis + artifacts.

### Shipped
- Added `reposcape analyze <repo_url>` command.
- Optionally writes `analysis.json` to a directory.
- Optionally writes snapshot JSON to a snapshot directory.

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 19 (2026-03-02)

**PR:** #29 (squash merged)

### Focus
Fix packaging for src/ layout.

### Shipped
- Fixed setuptools package discovery for `src/` layout.
- Added a smoke test for `pip install -e .` flows.

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 20 (2026-03-03)

**PR:** #30 (squash merged)

### Focus
Render analysis JSON in dashboard (smoke / dev UX).

### Shipped
- Dashboard: added a collapsible raw JSON panel for analysis payload.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 21 (2026-03-03)

**PR:** #31 (squash merged)

### Focus
Stabilize test suite and avoid long-running flakes.

### Shipped
- Added module-scoped fixtures + integration marker.
- Avoids running network clones during most unit tests.

### Tests
- `python -m pytest tests/test_clone.py -q --tb=short`

---

## Session 22 (2026-03-03)

**PR:** #32 (squash merged)

### Focus
Comparison mode (two repos side-by-side).

### Shipped
- Added `src/compare.py` analyzer.
- Added `/api/compare` endpoint.
- New compare dashboard UI + template.

### Tests
- `python -m pytest tests/test_clone.py tests/test_languages.py -q --tb=short`

---

## Session 23 (2026-03-03)

**PR:** #33 (squash merged)

### Focus
Snapshot bucketing + persistence.

### Shipped
- Added `src/history.py` foundation (save/load snapshots, bucket by day).
- Added tests for snapshot storage.

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 24 (2026-03-03)

**PR:** #34 (squash merged)

### Focus
Wire snapshots into CLI.

### Shipped
- `reposcape analyze --snapshot-dir ...` writes snapshot JSON to the specified directory.
- Added CLI tests.

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 25 (2026-03-03)

**PR:** #35 (squash merged)

### Focus
Snapshot API support.

### Shipped
- Added `/api/snapshots/list` endpoint.
- Added `/api/snapshots/get` endpoint.

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 26 (2026-03-03)

**PR:** #36 (squash merged)

### Focus
Dashboard snapshot selector UI.

### Shipped
- Dashboard: added snapshot A/B selector.
- Dashboard: snapshot B triggers a delta table vs snapshot A.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 27 (2026-03-03)

**PR:** #37 (squash merged)

### Focus
Automate snapshot bundle generation.

### Shipped
- GitHub Action generates `reposcape-snapshots.zip` on release.

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 28 (2026-03-03)

**PR:** #38 (squash merged)

### Focus
Release assets: select snapshots bundle by tag.

### Shipped
- Dashboard: can pick a release tag for downloading `reposcape-snapshots.zip`.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 29 (2026-03-04)

**PR:** #39 (squash merged)

### Focus
Snapshot download link.

### Shipped
- Dashboard: added "Download snapshots" link to latest release assets.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 30 (2026-03-04)

**PR:** #39 (squash merged)

### Focus
Snapshot release selector improvements.

### Shipped
- Dashboard: supports selecting release tag/date for snapshots bundle.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 31 (2026-03-04)

**PR:** #38 (squash merged)

### Focus
Snapshot diff API + dashboard diff table.

### Shipped
- API: `GET /api/snapshots/diff` endpoint.
- Dashboard: shows a delta table of key metrics comparing snapshot A vs B.

### Tests
- `python -m pytest tests/test_history.py tests/test_history_delta.py -q --tb=short`

---

## Session 32 (2026-03-04)

**PR:** #29 (squash merged)

### Focus
Snapshot index ordering + UX.

### Shipped
- Snapshot index is now returned in chronological order.
- Dashboard: improved default selection for snapshot A/B.

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 33 (2026-03-04)

**PR:** #40 (squash merged)

### Focus
Timeline sparkline.

### Shipped
- Dashboard: added an SVG sparkline timeline in the snapshots card based on snapshot index metrics (currently `total_source_lines`).
- UI: shows a helpful placeholder message until at least 2 snapshots exist.

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 34 (2026-03-04)

**PR:** #41 (squash merged)

### Focus
Improve snapshot selection ergonomics.

### Shipped
- Dashboard: when loading snapshot B, show key snapshot metrics as compact chips (as_of, LOC, files, TODOs, tech debt score, avg complexity).

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`


---

## Session 35 (2026-03-04)

**PR:** #42 (squash merged)

### Focus
Add a minimal multi-snapshot timeline view.

### Shipped
- API: added `POST /api/snapshots/series` to return a time-ordered metric series across snapshots (reads `history.metrics` from snapshot JSON files).
- Dashboard: snapshot card now renders a lightweight “History” table (last 12 points) for key metrics when loading Snapshot B.



---

## Session 36 (2026-03-04)

**PR:** #43 (squash merged)

### Focus
Render an interactive chart for snapshot history.

### Shipped
- Dashboard: renders `/api/snapshots/series` as an SVG line chart (uses last 120 points).
- UI: added a metric selector + baseline snapshot selector for the chart.
- Dashboard: keeps the existing “History” table (last 12 points) below the chart.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`
- `python -m pytest tests/test_history.py tests/test_history_delta.py -q --tb=short`


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
