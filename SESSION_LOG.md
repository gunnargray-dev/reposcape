# Reposcape Session Log

## Session 1 (2026-02-28)

**PR:** #1 (squash merged)

### Focus
Get a minimal working analysis engine with a test harness.

### Shipped
- Repo cloning + git log parsing (`src/clone.py`, `src/gitlog.py`).
- Language breakdown analyzer (`src/languages.py`).
- Basic CLI entry point (`reposcape_cli.py`).
- Test suite + CI pipeline (`tests/`, `.github/workflows/ci.yml`).

### Notes
- This session intentionally prioritized correctness and a stable test baseline.


---

## Session 2 (2026-02-28)

**PR:** #2 (squash merged)

### Focus
Add core “structure + activity” analyzers.

### Shipped
- Commit frequency heatmap data generator (`src/heatmap.py`).
- File tree analyzer + treemap data (`src/treemap.py`).
- Tests: `tests/test_heatmap.py`, `tests/test_treemap.py`.

### Notes
- Added deterministic fixtures for git log parsing.


---

## Session 3 (2026-02-28)

**PR:** #3 (squash merged)

### Focus
Add author-level activity analyzers.

### Shipped
- Contributor stats engine (`src/contributors.py`).
- Author velocity tracking (`src/velocity.py`).
- Tests: `tests/test_contributors.py`, `tests/test_velocity.py`.


---

## Session 4 (2026-02-28)

**PR:** #4 (squash merged)

### Focus
Add dependency + complexity analyzers.

### Shipped
- Dependency graph analyzer (`src/dependencies.py`).
- Code complexity heatmap (`src/complexity.py`).
- Tests: `tests/test_dependencies.py`, `tests/test_complexity.py`.


---

## Session 5 (2026-02-28)

**PR:** #5 (squash merged)

### Focus
Add repo health + velocity analyzers.

### Shipped
- Commit timeline analyzer (`src/timeline.py`).
- PR velocity tracker (`src/pr_velocity.py`).
- Tech debt scorer (`src/techdebt.py`).
- Tests: `tests/test_timeline.py`, `tests/test_pr_velocity.py`, `tests/test_techdebt.py`.


---

## Session 6 (2026-03-01)

**PR:** #6 (squash merged)

### Focus
Introduce the web frontend.

### Shipped
- FastAPI app + landing page with repo URL input (`src/web/app.py`, templates).
- Initial dashboard rendering treemap (`src/web/templates/dashboard.html`).

### Notes
- Early UI intentionally kept minimal; data binding is all client-side for now.


---

## Session 7 (2026-03-01)

**PR:** #7 (squash merged)

### Focus
Expand dashboard payload + caching.

### Shipped
- Added basic caching to avoid re-running analysis for identical URLs.
- Dashboard now renders more analyzers (timeline, heatmap, tech debt, complexity).


---

## Session 8 (2026-03-01)

**PR:** #8 (squash merged)

### Focus
Add more visualization rendering to the dashboard.

### Shipped
- Dashboard now renders additional analyzers (timeline, heatmap, tech debt, complexity).


---

## Session 9 (2026-03-01)

**PR:** #9 (squash merged)

### Focus
Add share cards (Open Graph images) for social sharing.

### Shipped
- Open Graph image generator (`src/web/og.py`).
- Share endpoints + templates.


---

## Session 10 (2026-03-01)

**PR:** #10 (squash merged)

### Focus
Add export system (standalone HTML snapshot download).

### Shipped
- Export HTML builder (`src/web/export.py`) + dashboard wiring.


---

## Session 11 (2026-03-02)

**PR:** #11 (squash merged)

### Focus
Ship a showcase demo and polish landing.

### Shipped
- Nightshift showcase with pre-generated demo payloads.


---

## Session 12 (2026-03-02)

**PR:** #12 (squash merged)

### Focus
Add per-repo story pages with proper OG meta tags.

### Shipped
- Story route `/r/{owner}/{repo}` and OG meta tags.


---

## Session 13 (2026-03-02)

**PR:** #13 (squash merged)

### Focus
Make the analysis payload more robust and support more repo structures.

### Shipped
- Improved analyzer robustness and error handling.


---

## Session 14 (2026-03-02)

**PR:** #14 (squash merged)

### Focus
Enrich story pages with GitHub metadata.

### Shipped
- Story pages now show stars, language, and last-updated.


---

## Session 15 (2026-03-02)

**PR:** #15 (squash merged)

### Focus
Export enhancements: client-side SVG→PNG + embed.

### Shipped
- Client-side export helpers (`src/web/static/export.js`).


---

## Session 16 (2026-03-02)

**PR:** #16 (squash merged)

### Focus
Begin growth/monetization phase with infra improvements.

### Shipped
- Roadmap + docs updates.


---

## Session 17 (2026-03-02)

**PR:** #17 (squash merged)

### Focus
Export system: add a more guided PDF flow.

### Shipped
- `/pdf` helper route for print-to-PDF.


---

## Session 18 (2026-03-02)

**PR:** #18 (squash merged)

### Focus
Add CLI tool for analyzing repos.

### Shipped
- `reposcape analyze <url>` CLI command.


---

## Session 19 (2026-03-02)

**PR:** #19 (squash merged)

### Focus
Packaging fixes for `src/` layout.

### Shipped
- setuptools discovery fixes; `pip install -e .` works.


---

## Session 20 (2026-03-03)

**PR:** #20 (squash merged)

### Focus
Expand test suite stability and speed.

### Shipped
- fixture improvements and test markers.


---

## Session 21 (2026-03-03)

**PR:** #21 (squash merged)

### Focus
Stabilize integration tests.

### Shipped
- module-scoped fixtures and shared conftest.


---

## Session 22 (2026-03-03)

**PR:** #22 (squash merged)

### Focus
Add comparison mode.

### Shipped
- Side-by-side comparison payload + UI.


---

## Session 23 (2026-03-03)

**PR:** #23 (squash merged)

### Focus
Historical tracking foundation.

### Shipped
- Snapshot bucketing + persistence utilities (`src/history.py`).


---

## Session 24 (2026-03-03)

**PR:** #24 (squash merged)

### Focus
Wire snapshot generation into CLI.

### Shipped
- CLI now supports `--snapshot-dir`.


---

## Session 25 (2026-03-03)

**PR:** #25 (squash merged)

### Focus
Web API endpoints for snapshots.

### Shipped
- `/api/snapshots/index` + `/api/snapshots/get`.


---

## Session 26 (2026-03-03)

**PR:** #26 (squash merged)

### Focus
Dashboard snapshot selector UI.

### Shipped
- Snapshot A/B selectors and load snapshot wiring.


---

## Session 27 (2026-03-03)

**PR:** #27 (squash merged)

### Focus
Automate snapshot bundles on release.

### Shipped
- GitHub Action to generate `reposcape-snapshots.zip`.


---

## Session 28 (2026-03-03)

**PR:** #28 (squash merged)

### Focus
General polish and bug fixes.

### Shipped
- Minor fixes.


---

## Session 29 (2026-03-03)

**PR:** #29 (squash merged)

### Focus
Wire "Download snapshots" to release assets.

### Shipped
- Dashboard shows download button if `reposcape-snapshots.zip` exists.


---

## Session 30 (2026-03-03)

**PR:** #30 (squash merged)

### Focus
Allow selecting a release tag for snapshot bundles.

### Shipped
- Release selector controlling snapshot bundle download.


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
