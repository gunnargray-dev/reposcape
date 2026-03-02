# Reposcape Session Log

This file records what was built each session.

---

## Session 1 (2025-02-10)

- Initialized repo structure + module layout
- Implemented repo cloning + git log parsing
- Added language breakdown analyzer
- Added test scaffolding + CI pipeline

## Session 2 (2025-02-12)

- Implemented commit frequency heatmap analyzer
- Implemented file tree + treemap analyzer
- Added basic CLI entrypoint

## Session 3 (2025-02-14)

- Implemented contributor stats analyzer
- Implemented author velocity tracking
- Implemented commit message quality analyzer

## Session 4 (2025-02-16)

- Implemented dependency graph analyzer
- Implemented cyclomatic complexity heatmap analyzer

## Session 5 (2025-02-18)

- Implemented commit timeline analyzer
- Implemented PR velocity tracker analyzer
- Implemented tech debt score analyzer

---

## Phase 2: Web Frontend (Sessions 6-10)

## Session 6 (2025-02-20)

- Added FastAPI app + server-rendered landing page
- Added initial dashboard page + treemap placeholder
- Added minimal JS to call analyze API

## Session 7 (2025-02-22)

- Expanded /api/analyze payload with all analysis modules
- Added simple in-memory caching keyed by repo URL
- Extended dashboard JS to render multiple panels

## Session 8 (2025-02-24)

- Added dashboard sections for timeline, heatmap, tech debt, complexity
- Improved dashboard rendering + layout

## Session 9 (2025-02-26)

- Added /share/card.png endpoint (Open Graph image)
- Added /share preview page

## Session 10 (2025-02-28)

- Added export pipeline: /api/export/html (download standalone dashboard snapshot)
- Added Export HTML UI button

## Session 11 (2025-03-01)

- Added /showcase/nightshift demo route
- Added /api/demo endpoints to serve pre-generated demo payloads
- Dashboard auto-runs analysis on load, supports demo mode, and has Re-run wiring


## Session 13 (2026-03-02)

**Goal:** Remove Starlette TemplateResponse deprecation warnings in tests.

**Shipped:**
- Updated server-rendered page routes to call `TemplateResponse(request, name, context)`
- Eliminated test warning from Starlette templating

## Session 12 (2026-03-02)

**Goal:** Add per-repo story pages with Open Graph meta tags wired to share cards.

**Shipped:**
- New story route: `/r/{owner}/{repo}` (share-friendly landing page)
- OG/Twitter meta tags in `story.html` using the existing `/share/card.png` endpoint
- Tiny OG helper module (`src/web/og.py`) for repo parsing + encoded share-card URLs
- Unit tests for the helpers and story rendering

**Notes:**
- URL encoding uses `quote(..., safe='')` so repo slugs and separators are encoded correctly.
