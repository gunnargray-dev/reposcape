# Session Log

This file records what was built in each autonomous development session.

## Session 1 -- Repo cloning + baseline analyzers

- Built repo cloner with temp directory support.
- Implemented language breakdown analyzer.
- Added initial test harness and CI pipeline.

## Session 2 -- Treemap + commit heatmap

- Implemented file tree analyzer and treemap data model.
- Added commit heatmap generator with week/day bucket output.
- Expanded test coverage.

## Session 3 -- Contributor stats + commit quality

- Added contributor stats analyzer (commits, LOC estimates, active periods).
- Built author velocity tracking (commits over time per author).
- Implemented commit message quality analyzer (length, keywords, conventions).

## Session 4 -- Dependencies + complexity

- Implemented dependency graph parser for Python and JS/TS imports.
- Added cyclomatic complexity estimator per file.

## Session 5 -- Timeline + PR velocity + tech debt

- Added commit timeline builder with daily/weekly buckets.
- Implemented PR velocity estimator from merge commits.
- Added tech debt score model (TODO density, deep nesting, large files).

## Session 6 -- Web app skeleton

- Built FastAPI server with landing page.
- Added initial dashboard with treemap visualization.

## Session 7 -- Expanded dashboard + caching

- Expanded /api/analyze payload.
- Added basic in-memory caching (TTL).
- Added dashboard sections for languages, contributors, and tech debt.

## Session 8 -- Dashboard visualization expansion

- Rendered timeline and heatmap charts.
- Added sections for complexity, dependencies, and PR velocity.

## Session 9 -- Share cards

- Implemented Open Graph share card image generation.
- Added /share/{owner}/{repo} endpoint.

## Session 10 -- Export HTML snapshot

- Added /api/export.html endpoint.
- Implemented standalone export HTML generator.

## Session 11 -- Nightshift showcase

- Added /showcase route with a demo story.
- Packaged a demo payload JSON.

## Session 12 -- Story pages

- Added /r/{owner}/{repo} story pages.
- Wired OG meta tags to share cards.

## Session 13 -- Story page polish

- Improved story layout, added more sections.
- Fixed minor bugs across story/share routes.

## Session 14 -- GitHub metadata in story subtitles

- Added lightweight GitHub API helper (stdlib) to fetch repo metadata.
- Populated story subtitle with stars, primary language, last updated.

## Session 15 -- Export: client-side PNG + print/PDF helper

- Added an export controls panel to the HTML snapshot view (panel selector, scale selector, Download PNG, and Print/Save PDF via window.print()).
- Implemented a dependency-free client-side SVG → PNG pipeline using canvas in `src/web/static/export.js` and wired it into the export HTML.
- Tests: 406 passed.
