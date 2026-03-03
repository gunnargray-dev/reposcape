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
Complete the dashboard’s initial visualization coverage.

### Shipped
- Dashboard renders timeline, heatmap, tech debt, complexity.
- Small UI improvements.


---

## Session 9 (2026-03-01)

**PR:** #9 (squash merged)

### Focus
Share cards (Open Graph images for social).

### Shipped
- Dynamic OG image route and generation utilities.
- Share preview page.
- Tests: `tests/web/test_og.py`.


---

## Session 10 (2026-03-01)

**PR:** #10 (squash merged)

### Focus
Export system (downloadable HTML snapshot).

### Shipped
- `POST /api/export.html` to generate standalone HTML.
- Export HTML template and bundling logic.
- Dashboard “Export HTML” button.


---

## Session 11 (2026-03-02)

**PR:** #11 (squash merged)

### Focus
Nightshift showcase.

### Shipped
- Packaged demo payload and “demo mode” entry point.
- Showcase route and page.


---

## Session 12 (2026-03-02)

**PR:** #12 (squash merged)

### Focus
Story pages with OG meta tags.

### Shipped
- `/r/{owner}/{repo}` story route.
- Story template with OG and Twitter meta tags.


---

## Session 14 (2026-03-02)

**PR:** #14 (squash merged)

### Focus
Improve story page metadata.

### Shipped
- GitHub metadata fetcher for stars/language/updated.
- Story template enhancements.

### Notes
- If GitHub API rate limits become an issue, consider caching or server-side token support.


---

## Session 16 (2026-03-02)

**PR:** #17 (squash merged)

### Focus
Server-side PDF generation helper.

### Shipped
- `/api/export.pdf` server-side endpoint (best-effort) using Playwright.
- Docs updates.


---

## Session 17 (2026-03-02)

**PR:** #18 (squash merged)

### Focus
Export enhancements (image generation + embed).

### Shipped
- Client-side SVG->PNG export helpers.
- Optional iframe embed.


---

## Session 18 (2026-03-02)

**PR:** #19 (squash merged)

### Focus
CLI tool (`reposcape analyze <url>`).

### Shipped
- CLI entry point with `analyze` subcommand.
- Shared analysis code paths.


---

## Session 19 (2026-03-02)

**PR:** #20 (squash merged)

### Focus
Packaging and `src/` discovery.

### Shipped
- Updated `pyproject.toml` / packaging config for editable installs.


---

## Session 20 (2026-03-03)

**PR:** #23 (squash merged)

### Focus
Enforce function size limits and type hints across analyzers.

### Shipped
- Refactors in several modules to keep functions <50 lines.
- More consistent typing.


---

## Session 21 (2026-03-03)

**PR:** #24 (squash merged)

### Focus
Test suite stability.

### Shipped
- Module-scoped fixtures and shared conftest.
- Integration markers.


---

## Session 22 (2026-03-03)

**PR:** #25 (squash merged)

### Focus
Comparison mode (two repos side by side).

### Shipped
- `POST /api/compare` endpoint.
- Compare page + template.
- Comparison payload builder.


---

## Session 23 (2026-03-03)

**PR:** #28 (squash merged)

### Focus
Historical tracking foundation (snapshot storage + index utilities).

### Shipped
- Added stdlib-only historical helpers: `src/history.py`.
  - Snapshot date bucketing (weekly by default).
  - Helpers for stable snapshot filenames and per-repo history directories.
  - JSON persistence helpers (write/load).
  - Index builder for consumers (web/CLI).
- Added unit tests: `tests/test_history.py`.

### Notes
- Tests: history unit tests pass (`5 passed`).
- Next: wire snapshots into CLI/web and add a GitHub Action to publish/update history artifacts.


---

## Session 25 (2026-03-03)

**PR:** #30 (squash merged)

### Focus
Expose persisted analysis snapshots via the web JSON API.

### Shipped
- Added snapshot endpoints to `src/web/routes/api.py`:
  - `POST /api/snapshots/index` to list available snapshot files.
  - `POST /api/snapshots/get` to fetch a single snapshot payload by `as_of` date.
- Snapshot directory is configured via `REPOSCAPE_SNAPSHOT_DIR` (server-side).

### Notes
- Tests: `tests/web/*`, `tests/test_history.py`.
- Next: wire snapshot browsing into the dashboard/story UI and add a GitHub Action to generate snapshots.


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
