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

**Focus:** Story pages.

**PR:** #9 (squash merged)

### Shipped
- Per-repo story pages with OG meta tags

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 13

**Focus:** Fix demo mode URL / caching edge cases.

**PR:** #10 (squash merged)

### Shipped
- Demo mode now supports navigating directly to `/?demo=1`.
- Demo mode now disables dashboard inputs and auto-loads demo payload.
- Added basic runtime config: `DEMO_MODE` and `DEMO_REPO_URL`.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 14 (2026-03-01)

**PR:** #11 (squash merged)

### Focus
Add GitHub metadata to story pages.

### Shipped
- Story route fetches GitHub repo metadata (stars, language, updated_at) and renders it in the story subtitle.

### Tests
- `python -m pytest tests/test_github_meta.py -q --tb=short`
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 15 (2026-03-01)

**PR:** #12 (squash merged)

### Focus
Export enhancements.

### Shipped
- Export HTML includes a client-side “Save as PNG” helper that renders embedded SVG and downloads a PNG.
- Export HTML includes an optional iframe embed helper.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 16 (2026-03-02)

**PR:** #13 (squash merged)

### Focus
Add PDF export.

### Shipped
- Added `/api/export.pdf` which renders PDF using Playwright.
- Added a `/export.pdf` route page for download.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 17 (2026-03-02)

**PR:** #14 (squash merged)

### Focus
PDF export helper.

### Shipped
- Added `PdfHelper` abstraction.
- Server-side PDF export now falls back to a “print-to-PDF” helper if Playwright is unavailable.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 18 (2026-03-02)

**PR:** #15 (squash merged)

### Focus
CLI tool.

### Shipped
- Added `reposcape` CLI (`reposcape analyze <repo_url>`) for generating analysis JSON.

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 19 (2026-03-02)

**PR:** #16 (squash merged)

### Focus
Packaging fixes.

### Shipped
- Fixed setuptools discovery for `src/` layout (`pyproject.toml`).
- Restored `pip install -e .` support.

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 20 (2026-03-02)

**PR:** #17 (squash merged)

### Focus
Stabilize CI.

### Shipped
- Updated test suite to remove module-global tmp paths.
- Added module-scoped fixtures for expensive operations.

### Tests
- `python -m pytest tests/test_clone.py -q --tb=short`

---

## Session 21 (2026-03-03)

**PR:** #18 (squash merged)

### Focus
Stabilize full test suite.

### Shipped
- Improved shared conftest configuration and caching.
- Marked integration tests and improved fixture scopes.

### Tests
- `python -m pytest tests/test_clone.py -q --tb=short`

---

## Session 22 (2026-03-03)

**PR:** #19 (squash merged)

### Focus
Comparison mode.

### Shipped
- Added `/compare` page + API to analyze two repos.
- New compare template and minimal compare UI.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 23 (2026-03-03)

**PR:** #20 (squash merged)

### Focus
Snapshot persistence foundation.

### Shipped
- Added snapshot persistence to `src/history.py`.
- Added snapshot bucketing logic.

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 24 (2026-03-03)

**PR:** #21 (squash merged)

### Focus
Wire snapshots into CLI.

### Shipped
- CLI: `reposcape analyze --snapshot-dir ...` writes time-bucketed snapshot JSON.

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 25 (2026-03-03)

**PR:** #22 (squash merged)

### Focus
Expose snapshots in web API.

### Shipped
- Added `POST /api/snapshots/index` + `POST /api/snapshots/get`.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 26 (2026-03-03)

**PR:** #23 (squash merged)

### Focus
Snapshot selector UI.

### Shipped
- Dashboard: snapshot selector A/B + “Load B” + “Diff A→B”.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 27 (2026-03-03)

**PR:** #24 (squash merged)

### Focus
Auto-generate snapshots on release.

### Shipped
- Added GitHub Action to generate snapshots bundle on release.

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 28 (2026-03-04)

**PR:** #25 (squash merged)

### Focus
Snapshot diff endpoint.

### Shipped
- Added `POST /api/snapshots/diff`.

### Tests
- `python -m pytest tests/test_history_delta.py -q --tb=short`

---

## Session 29 (2026-03-04)

**PR:** #26 (squash merged)

### Focus
Snapshots bundle download.

### Shipped
- Dashboard: adds “Download snapshots” button when snapshots exist.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 30 (2026-03-04)

**PR:** #27 (squash merged)

### Focus
Select release for snapshots bundle.

### Shipped
- Dashboard: added a release selector dropdown for choosing which release’s snapshots bundle to download.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 31 (2026-03-04)

**PR:** #28 (squash merged)

### Focus
Snapshot delta table.

### Shipped
- Dashboard: added a delta table for key metrics for snapshot A→B.

### Tests
- `python -m pytest tests/test_history_delta.py -q --tb=short`

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

