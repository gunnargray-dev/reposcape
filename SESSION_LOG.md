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
Contributor and commit quality metrics.

### Shipped
- Contributor stats engine (`src/contributors.py`).
- Author velocity tracking (`src/velocity.py`).
- Commit message quality analyzer (`src/commit_quality.py`).
- Tests for new modules.


---

## Session 4 (2026-03-01)

**PR:** #4 (squash merged)

### Focus
Advanced code graph/complexity signals.

### Shipped
- Dependency graph analyzer (Python/JS/TS import parsing) (`src/dependencies.py`).
- Cyclomatic complexity hotspots (`src/complexity.py`).
- Tests for new modules.


---

## Session 5 (2026-03-01)

**PR:** #5 (squash merged)

### Focus
More activity/engineering health signals.

### Shipped
- Commit timeline analyzer (`src/timeline.py`).
- PR velocity tracker (`src/pr_velocity.py`).
- Tech debt scoring (`src/techdebt.py`).
- Tests for new modules.


---

## Session 6 (2026-03-01)

**PR:** #6 (squash merged)

### Focus
First web UX: landing + dashboard.

### Shipped
- FastAPI app with landing page and dashboard skeleton.
- Dashboard renders treemap + languages.
- Basic frontend styling.


---

## Session 7 (2026-03-01)

**PR:** #7 (squash merged)

### Focus
Expand web analysis payload + caching.

### Shipped
- Expand `/api/analyze` payload with additional analyzers.
- Add in-memory cache for repeated requests.
- Dashboard renders more sections.


---

## Session 8 (2026-03-01)

**PR:** #8 (squash merged)

### Focus
Full dashboard: render all analyzers.

### Shipped
- Dashboard: added timeline, heatmap, tech debt, complexity.
- Added minimal charts rendering logic.


---

## Session 9 (2026-03-01)

**PR:** #9 (squash merged)

### Focus
Share cards (Open Graph images).

### Shipped
- Added OG image generator for sharing a repo analysis.
- Wired into story pages.


---

## Session 10 (2026-03-01)

**PR:** #10 (squash merged)

### Focus
Export system: standalone HTML snapshot.

### Shipped
- Added `build_export_html()` and an `/api/export.html` endpoint.
- Added client-side export helpers.


---

## Session 11 (2026-03-01)

**PR:** #11 (squash merged)

### Focus
Nightshift showcase.

### Shipped
- Added demo payload packaging.
- Added `/showcase/nightshift` page.


---

## Session 12 (2026-03-02)

**PR:** #12 (squash merged)

### Focus
Story pages + OG meta tags.

### Shipped
- Added per-repo story pages.
- Wired OG meta tags and share card URLs.


---

## Session 13 (2026-03-02)

**PR:** #13 (squash merged)

### Focus
Share cards: improvements.

### Shipped
- Improved OG card layout.
- Fixed share preview template.


---

## Session 14 (2026-03-02)

**PR:** #14 (squash merged)

### Focus
Story metadata enrichment.

### Shipped
- Story pages: populate stars/language/last updated.


---

## Session 15 (2026-03-02)

**PR:** #15 (squash merged)

### Focus
Export enhancements.

### Shipped
- Client-side SVG->PNG export.
- Optional iframe embed.


---

## Session 16 (2026-03-02)

**PR:** #16 (squash merged)

### Focus
Growth baseline cleanup.

### Shipped
- TODO placeholders for monetization phase.


---

## Session 17 (2026-03-02)

**PR:** #17 (squash merged)

### Focus
Export system: PDF helper.

### Shipped
- Added server-side PDF helper route.


---

## Session 18 (2026-03-02)

**PR:** #18 (squash merged)

### Focus
CLI tooling.

### Shipped
- Added `reposcape analyze <url>` command.


---

## Session 19 (2026-03-02)

**PR:** #19 (squash merged)

### Focus
Packaging fixes.

### Shipped
- Fixed setuptools discovery for `src/` layout.


---

## Session 20 (2026-03-02)

**PR:** #20 (squash merged)

### Focus
Prepping for reliable test runs.

### Shipped
- Minor test infra improvements.


---

## Session 21 (2026-03-03)

**PR:** #23 (squash merged)

### Focus
Test suite stability.

### Shipped
- Module-scoped fixtures.
- Shared conftest.


---

## Session 22 (2026-03-03)

**PR:** #24 (squash merged)

### Focus
Comparison mode.

### Shipped
- Added comparison payload builder.
- Added compare page.


---

## Session 23 (2026-03-03)

**PR:** #25 (squash merged)

### Focus
Historical tracking foundation.

### Shipped
- Snapshot bucketing + persistence utilities (`src/history.py`).


---

## Session 24 (2026-03-03)

**PR:** #26 (squash merged)

### Focus
Wire snapshot generation into CLI.

### Shipped
- `reposcape analyze --snapshot-dir ...` writes snapshot JSON.


---

## Session 25 (2026-03-03)

**PR:** #30 (squash merged)

### Focus
Historical tracking: web API endpoints.

### Shipped
- Added endpoints to list snapshots and retrieve a snapshot payload.


---

## Session 26 (2026-03-03)

**PR:** #31 (squash merged)

### Focus
Wire snapshot browsing into the dashboard UI.

### Shipped
- Dashboard: added a Snapshots selector (dropdown + Load button) that calls the existing snapshot endpoints.
- Snapshots card auto-hides when snapshots are not configured (based on `REPOSCAPE_SNAPSHOT_DIR`) or in demo mode.

### Notes
- Tests: `tests/web/test_story_route.py`, `tests/test_history.py`.
- Next: ship a GitHub Action to auto-generate snapshots (nightly or on release) and consider a timeline diff view.


---

## Session 27 (2026-03-03)

**PR:** #32 (squash merged)

### Focus
GitHub Action to auto-generate and publish snapshots.

### Shipped
- Added release-triggered GitHub Action (`.github/workflows/snapshots.yml`) that generates an analysis snapshot for the repository and uploads it as an artifact.

### Notes
- Current implementation uploads snapshots as an artifact; future work could publish to GitHub Pages or attach to the release assets.

---

## Session 28 (2026-03-03)

**PR:** #34 (squash merged)

### Focus
Make release snapshots easier to discover and download.

### Shipped
- Updated the release-triggered snapshot workflow to zip the generated `snapshots/` directory and upload it to the GitHub Release assets as `reposcape-snapshots.zip`.
- Kept the existing Actions artifact upload in place.

### Notes
- This is a stepping stone toward a “download snapshots” link in the UI and/or a published snapshot timeline view.

---

## Session 29 (2026-03-03)

**PR:** #35 (squash merged)

### Focus
Add a dashboard link to download the snapshots bundle from the latest GitHub release.

### Shipped
- Dashboard: added a "Download snapshots" button that appears when the latest release includes `reposcape-snapshots.zip`.
- API: added a lightweight `GET /api/releases/latest?owner=...&repo=...` endpoint that returns best-effort download URLs for known assets.

### Notes
- Tests: `python -m pytest tests/test_history.py tests/web/test_story_route.py -q --tb=short`.
