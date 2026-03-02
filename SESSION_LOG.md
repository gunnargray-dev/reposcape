# Reposcape Session Log

This file records what was built each session.

## Session 1 (2026-03-01)

- Built core repo cloning + git log parser (`src/clone.py`)
- Added language breakdown analyzer (`src/languages.py`)
- Set up pytest + GitHub Actions CI

## Session 2 (2026-03-01)

- Added commit frequency heatmap generator (`src/heatmap.py`)
- Added file tree analyzer + treemap data generator (`src/treemap.py`)

## Session 3 (2026-03-01)

- Built contributor stats engine (`src/contributors.py`)
- Built author velocity tracker (`src/velocity.py`)
- Built commit message quality analyzer (`src/commit_quality.py`)

## Session 4 (2026-03-01)

- Added dependency graph analyzer (`src/dependencies.py`)
- Added code complexity heatmap analyzer (`src/complexity.py`)

## Session 5 (2026-03-01)

- Added commit timeline analyzer (`src/timeline.py`)
- Added PR velocity analyzer (`src/pr_velocity.py`)
- Added tech debt scorer (`src/techdebt.py`)

## Session 6 (2026-03-01)

- Built FastAPI app scaffold (`src/web/app.py`)
- Added landing page + dashboard skeleton

## Session 7 (2026-03-01)

- Expanded `/api/analyze` payload
- Added in-memory caching to avoid repeated clone/analysis
- Improved dashboard sections and chart rendering

## Session 8 (2026-03-01)

- Added timeline / heatmap / tech debt / complexity dashboard charts
- Added “analysis duration” status indicator

## Session 9 (2026-03-01)

- Added share card generator (`/share/card.png`) using Pillow
- Added share preview page (`/share/preview`)

## Session 10 (2026-03-01)

- Added export system: `/api/export.html` returns standalone HTML snapshot
- Added export HTML view builder (`src/web/export.py`) and a simple shareable export layout

## Session 11 (2026-03-01)

- Added a “showcase” demo using a pre-generated payload (nightshift)
- Added routes + template for `/showcase/nightshift`

## Session 12 (2026-03-02)

- Added per-repo story pages: `/r/{owner}/{repo}` with OG meta tags
- Wired OG image to share card route (`/share/card.png`) with repo-specific title

## Session 13 (2026-03-02)

- Fixed Starlette template deprecation warnings by updating TemplateResponse call signatures.

**Notes:**
- URL encoding uses `quote(..., safe='')` so repo slugs and separators are encoded correctly.

## Session 14 (2026-03-02)

- PR #18 (squash merge, commit e4cb1a5)
- Story pages now use GitHub repo metadata (stars/language/updated) for OG description + on-page metadata pills.
- Added `src/github_meta.py` (stdlib, best-effort) + parsing tests.
