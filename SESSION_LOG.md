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
Render the full analyzer set in the dashboard.

### Shipped
- Dashboard: added timeline, heatmap, tech debt, complexity sections.


---

## Session 9 (2026-03-01)

**PR:** #9 (squash merged)

### Focus
Add share cards.

### Shipped
- Open Graph image generator (`src/web/og.py`).
- Share routes + preview page.


---

## Session 10 (2026-03-01)

**PR:** #10 (squash merged)

### Focus
Export system foundations.

### Shipped
- `POST /api/export.html` returns a self-contained HTML export.
- Dashboard: “Export HTML” button.


---

## Session 11 (2026-03-02)

**PR:** #11 (squash merged)

### Focus
Add a demo showcase.

### Shipped
- Pre-generated demo payloads and a showcase route.


---

## Session 12 (2026-03-02)

**PR:** #12 (squash merged)

### Focus
Per-repo story pages + OG metadata.

### Shipped
- Story route and template with OG meta tags.


---

## Session 13 (2026-03-02)

**PR:** #13 (squash merged)

### Focus
Stabilize web tests.

### Shipped
- Cleaned up template wiring and tests for story/og routes.


---

## Session 14 (2026-03-02)

**PR:** #14 (squash merged)

### Focus
Story metadata from GitHub.

### Shipped
- Added GitHub metadata fetch and injected into story subtitle.


---

## Session 15 (2026-03-02)

**PR:** #15 (squash merged)

### Focus
Export enhancements.

### Shipped
- Client-side SVG->PNG helper.
- Optional embed iframe support.


---

## Session 16 (2026-03-02)

**PR:** #16 (squash merged)

### Focus
Monetization scaffolding.

### Shipped
- Initial Phase 4 roadmap and scaffolding for future pro tier.


---

## Session 17 (2026-03-02)

**PR:** #17 (squash merged)

### Focus
Server-side PDF generation helper.

### Shipped
- Print-to-PDF helper route + documentation.


---

## Session 18 (2026-03-02)

**PR:** #18 (squash merged)

### Focus
CLI tool.

### Shipped
- `reposcape analyze <url>` CLI.


---

## Session 19 (2026-03-02)

**PR:** #19 (squash merged)

### Focus
Packaging.

### Shipped
- Fixed setuptools discovery for `src/` layout.


---

## Session 20 (2026-03-02)

**PR:** #20 (squash merged)

### Focus
Test improvements.

### Shipped
- Improved fixtures and reduced flakes.


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
- Compare API + compare page.


---

## Session 23 (2026-03-03)

**PR:** #23 (squash merged)

### Focus
History foundations.

### Shipped
- Snapshot persistence and bucketing (`src/history.py`).


---

## Session 24 (2026-03-03)

**PR:** #24 (squash merged)

### Focus
Wire snapshot generation into CLI.

### Shipped
- `reposcape analyze --snapshot-dir ...` writes dated snapshots.


---

## Session 25 (2026-03-03)

**PR:** #25 (squash merged)

### Focus
Web API snapshot endpoints.

### Shipped
- `POST /api/snapshots/index` and `POST /api/snapshots/get`.


---

## Session 26 (2026-03-03)

**PR:** #26 (squash merged)

### Focus
Dashboard snapshot selector.

### Shipped
- Snapshot selector + load button.


---

## Session 27 (2026-03-03)

**PR:** #33 (squash merged)

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
