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

**Focus:** render more analyzers.

**Shipped:**
- Dashboard renders timeline, heatmap, tech debt, complexity, and treemap in basic forms

---

## Session 9

**Focus:** social share cards.

**Shipped:**
- Open Graph share images (`src/web/og.py`)
- Share routes (`src/web/routes/share.py`)

---

## Session 10

**Focus:** export system.

**Shipped:**
- HTML export generator (`src/web/export.py`)
- Dashboard "Export" link

---

## Session 11

**Focus:** Nightshift showcase demo.

**Shipped:**
- Demo payloads in `src/web/demo.py`
- Showcase routes

---

## Session 12

**Focus:** story pages.

**Shipped:**
- Story routes + templates + OG tag wiring

---

## Session 13

**Focus:** misc polish.

**Shipped:**
- Small UI fixes and test improvements

---

## Session 14

**Focus:** GitHub metadata for stories.

**Shipped:**
- Story subtitle/metadata populated from GitHub (stars, language, last updated)

---

## Session 15

**Focus:** export enhancements.

**Shipped:**
- Client-side SVG->PNG export helper
- Optional iframe embed support

---

## Session 16

**Focus:** growth and docs.

**Shipped:**
- Docs updates

---

## Session 17

**Focus:** PDF export helper.

**Shipped:**
- Server-side PDF generation helper or print-to-PDF notes

---

## Session 18

**Focus:** CLI tool improvements.

**Shipped:**
- `reposcape analyze <url>` CLI command

---

## Session 19

**Focus:** packaging fixes.

**Shipped:**
- setuptools discovery fixes for src layout

---

## Session 20 (2026-03-02)

**PR:** #34 (squash merged)

### Focus
Reduce flaky network test behavior.

### Shipped
- Web API: added `Cache-Control: no-store` headers for GitHub API calls.

### Tests
- `python -m pytest tests/test_github_meta.py -q --tb=short`

---

## Session 21 (2026-03-03)

**PR:** #35 (squash merged)

### Focus
Stabilize the test suite.

### Shipped
- Test suite: module-scoped tmp_path factory to reduce fixture overhead.
- Pytest: marker + addopts to skip integration tests by default.
- Cache: avoid global state leaking between tests.

### Notes
- CI still runs all tests; local defaults to unit-only.

---

## Session 22 (2026-03-03)

**PR:** #36 (squash merged)

### Focus
Ship comparison mode.

### Shipped
- API: added `POST /api/compare`.
- UI: comparison page renders two payloads side by side.

### Tests
- `python -m pytest tests/test_compare.py -q --tb=short`

---

## Session 23 (2026-03-03)

**PR:** #37 (squash merged)

### Focus
Lay the foundation for historical tracking.

### Shipped
- New `src/history.py` module for snapshot bucketing + persistence.
- CLI: optional `--snapshot-dir` support.
- API: endpoints for listing snapshots + fetching a snapshot payload.

### Notes
- This is intentionally minimal; follow-ups add timeline views and baseline selection.

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 24 (2026-03-03)

**PR:** #38 (squash merged)

### Focus
Wire snapshot generation into CLI.

### Shipped
- `reposcape analyze --snapshot-dir ...` now writes daily snapshots.

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 25 (2026-03-03)

**PR:** #39 (squash merged)

### Focus
Web API: list snapshots and fetch snapshot payload.

### Shipped
- API: added endpoints to list snapshots (`POST /api/snapshots/index`) and fetch a snapshot (`POST /api/snapshots/get`).

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 26 (2026-03-03)

**PR:** #40 (squash merged)

### Focus
Dashboard UI: snapshot selector.

### Shipped
- UI: dashboard now includes snapshot selector and loads snapshot payloads.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 31 (2026-03-04)

**PR:** #37 (squash merged)

### Focus
Add a first snapshot-to-snapshot diff primitive to support a historical timeline view.

### Shipped
- New `src/history_delta.py` module for computing lightweight snapshot deltas (tech debt score, TODO count, total source lines/files, avg complexity).
- API: added `POST /api/snapshots/diff` (requires `REPOSCAPE_SNAPSHOT_DIR`).
- Dashboard: snapshot card now supports selecting snapshot A + snapshot B and rendering a delta table.
- Tests: added `tests/test_history_delta.py`.

### Notes
- This is intentionally small: the next step is a real timeline view across many snapshots.
- Tests: `python -m pytest tests/test_history_delta.py -q --tb=short` and `python -m pytest tests/web/ -q --tb=short`.


---

## Session 32 (2026-03-04)

**PR:** #38 (squash merged)

### Focus
Fix dashboard snapshot index loading.

### Shipped
- Dashboard: fixed missing `resp.json()` call so the snapshot index loads correctly.


---

## Session 33 (2026-03-04)

**PR:** #39 (squash merged)

### Focus
Make historical tracking visible at a glance.

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

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`
- `python -m pytest tests/web/test_og.py -q --tb=short`
- `python -m pytest tests/test_history_delta.py -q --tb=short`
