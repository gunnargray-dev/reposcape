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
Full dashboard visualization rollout.

### Shipped
- Dashboard renders additional analyzers (timeline, heatmap, tech debt, complexity).
- Added dashboard UI sections for each analyzer.
- Improved layout and section styling.


---

## Session 9 (2026-03-01)

**PR:** #9 (squash merged)

### Focus
Share cards (Open Graph images) for social sharing.

### Shipped
- Server-generated OG images for story pages.
- Share card templates for consistent rendering.


---

## Session 10 (2026-03-01)

**PR:** #10 (squash merged)

### Focus
Export system: HTML snapshots.

### Shipped
- Added export endpoint that returns a standalone HTML doc.
- Dashboard: added Export button that downloads an HTML snapshot.


---

## Session 11 (2026-03-01)

**PR:** #11 (squash merged)

### Focus
Demo showcase pipeline.

### Shipped
- Packaged a "nightshift" demo payload.
- Added showcase route for demo content.


---

## Session 12 (2026-03-01)

**PR:** #12 (squash merged)

### Focus
Story pages + per-repo share.

### Shipped
- Added story routes for repos.
- Wired OG meta tags to share cards.


---

## Session 13 (2026-03-01)

**PR:** #13 (squash merged)

### Focus
Story and export UI polish.

### Shipped
- Polished story page layout.
- Improved export HTML styles.


---

## Session 14 (2026-03-02)

**PR:** #14 (squash merged)

### Focus
Story metadata from GitHub.

### Shipped
- Story pages now pull GitHub metadata for subtitle/metadata.


---

## Session 15 (2026-03-02)

**PR:** #15 (squash merged)

### Focus
Export assets.

### Shipped
- Added client-side SVG->PNG export for shareable assets.


---

## Session 16 (2026-03-02)

**PR:** #16 (squash merged)

### Focus
Start Growth & Monetization phase.

### Shipped
- Added more “product” UI and a stable landing page.


---

## Session 17 (2026-03-02)

**PR:** #17 (squash merged)

### Focus
Server-side PDF export helper.

### Shipped
- Added a PDF render helper for exports.


---

## Session 18 (2026-03-02)

**PR:** #18 (squash merged)

### Focus
CLI tool (reposcape analyze).

### Shipped
- Added `src/cli/main.py` and `reposcape analyze <url>`.


---

## Session 19 (2026-03-02)

**PR:** #19 (squash merged)

### Focus
Packaging fixes.

### Shipped
- Fixed packaging for `src/` layout and `pip install -e .`.


---

## Session 20 (2026-03-02)

**PR:** #20 (squash merged)

### Focus
Stabilize tests and CI.

### Shipped
- Improved fixtures and integration markers.


---

## Session 21 (2026-03-02)

**PR:** #21 (squash merged)

### Focus
Test suite stability.

### Shipped
- Refactored fixtures for stability and speed.


---

## Session 22 (2026-03-02)

**PR:** #22 (squash merged)

### Focus
Comparison mode.

### Shipped
- Side-by-side comparison for two repos.


---

## Session 23 (2026-03-02)

**PR:** #23 (squash merged)

### Focus
Historical tracking: foundation.

### Shipped
- Added snapshot bucketing + persistence utilities (`src/history.py`).


---

## Session 24 (2026-03-03)

**PR:** #28 (squash merged)

### Focus
Historical tracking: wire snapshots into CLI.

### Shipped
- Added `--snapshot-dir` to CLI; snapshots are written to disk.


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
