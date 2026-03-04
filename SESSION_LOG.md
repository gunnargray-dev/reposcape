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
- Dashboard now renders more analyzers (languages, contributors).


---

## Session 8 (2026-03-01)

**PR:** #8 (squash merged)

### Focus
Expand dashboard rendering.

### Shipped
- Dashboard now renders commit quality, timeline, heatmap, tech debt, complexity.


---

## Session 9 (2026-03-01)

**PR:** #9 (squash merged)

### Focus
Add share cards (Open Graph images).

### Shipped
- Server-side Open Graph image generation (`src/web/og.py`).
- Share route + OG meta tags.


---

## Session 10 (2026-03-01)

**PR:** #10 (squash merged)

### Focus
Export system foundation.

### Shipped
- Export HTML endpoint + client download.


---

## Session 11 (2026-03-02)

**PR:** #11 (squash merged)

### Focus
Nightshift showcase.

### Shipped
- Demo payload + showcase route.


---

## Session 12 (2026-03-02)

**PR:** #12 (squash merged)

### Focus
Story pages + OG meta integration.

### Shipped
- Story pages using GitHub metadata.


---

## Session 13 (2026-03-02)

**PR:** #13 (squash merged)

### Focus
Minor web improvements.

### Shipped
- Small improvements across routes/templates.


---

## Session 14 (2026-03-02)

**PR:** #14 (squash merged)

### Focus
Story pages: enrich with repo metadata.

### Shipped
- GitHub metadata fetch for stars/language/updated.


---

## Session 15 (2026-03-02)

**PR:** #15 (squash merged)

### Focus
Export system enhancements.

### Shipped
- Client-side SVG→PNG.


---

## Session 16 (2026-03-02)

**PR:** #16 (squash merged)

### Focus
Docs + project hygiene.

### Shipped
- README/ROADMAP/SESSION_LOG updates.


---

## Session 17 (2026-03-02)

**PR:** #17 (squash merged)

### Focus
PDF export helper.

### Shipped
- Server-side print helper.


---

## Session 18 (2026-03-03)

**PR:** #18 (squash merged)

### Focus
CLI tool.

### Shipped
- `reposcape analyze <url>`.


---

## Session 19 (2026-03-03)

**PR:** #19 (squash merged)

### Focus
Packaging fixes.

### Shipped
- setuptools discovery for `src/` layout.


---

## Session 20 (2026-03-03)

**PR:** #20 (squash merged)

### Focus
Release pipeline improvements.

### Shipped
- docs/notes improvements.


---

## Session 21 (2026-03-03)

**PR:** #21 (squash merged)

### Focus
Test suite stability.

### Shipped
- Module-scoped fixtures, integration markers, shared conftest.


---

## Session 22 (2026-03-03)

**PR:** #22 (squash merged)

### Focus
Comparison mode.

### Shipped
- Compare payload + compare page.


---

## Session 23 (2026-03-03)

**PR:** #29 (squash merged)

### Focus
Historical tracking foundation.

### Shipped
- Snapshot bucketing + persistence utilities (`src/history.py`).


---

## Session 24 (2026-03-03)

**PR:** #30 (squash merged)

### Focus
Wire snapshot generation into CLI.

### Shipped
- `reposcape analyze --snapshot-dir ...`.


---

## Session 25 (2026-03-04)

**PR:** #31 (squash merged)

### Focus
Web API: list snapshots + fetch snapshot payload.

### Shipped
- `/api/snapshots/index` + `/api/snapshots/get`.


---

## Session 26 (2026-03-04)

**PR:** #32 (squash merged)

### Focus
Dashboard UI: snapshot selector.

### Shipped
- Snapshot selector + load snapshot payload.


---

## Session 27 (2026-03-04)

**PR:** #33 (squash merged)

### Focus
GitHub Action to generate snapshots on release.

### Shipped
- Release workflow generates `reposcape-snapshots.zip`.


---

## Session 28 (2026-03-04)

**PR:** #34 (squash merged)

### Focus
Snapshot pipeline fixes.

### Shipped
- Stability improvements.


---

## Session 29 (2026-03-04)

**PR:** #35 (squash merged)

### Focus
UI: add a "Download snapshots" link to the latest release asset.

### Shipped
- Dashboard button for `reposcape-snapshots.zip` (latest release).


---

## Session 30 (2026-03-04)

**PR:** #36 (squash merged)

### Focus
Support selecting a release tag/date (not only latest) when downloading the snapshots bundle.

### Shipped
- API: added `GET /api/releases?owner=...&repo=...&limit=...` to list recent releases (tag, name, published date).
- API: added `GET /api/releases/by_tag?owner=...&repo=...&tag=...` to discover `reposcape-snapshots.zip` on a specific release tag.
- Dashboard: added a Release selector (default: Latest) that refreshes the snapshots download URL when changed.

### Notes
- This is best-effort, unauthenticated GitHub API access; private repos and rate limits are out of scope for now.
- Tests: `python -m pytest tests/test_history.py tests/web/test_story_route.py -q --tb=short`.


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
