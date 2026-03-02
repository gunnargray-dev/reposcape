# Reposcape Session Log

A chronological record of all autonomous development sessions.

---

## Session 1

✅ Built core repo cloning + analysis engine (language breakdown, git log parser)
✅ Set up project structure, tests, and CI

## Session 2

✅ Added commit frequency heatmap analyzer
✅ Built file tree treemap analyzer

## Session 3

✅ Built contributor stats analyzer
✅ Built commit message quality analyzer
✅ Built author velocity tracking

## Session 4

✅ Implemented dependency graph analyzer (Python/JS/TS import parsing)
✅ Implemented cyclomatic complexity analyzer

## Session 5

✅ Built commit timeline generator
✅ Built PR velocity tracker
✅ Built tech debt scorer

## Session 6

✅ Built initial web app with landing page and treemap dashboard
✅ Wired repo analysis engine into FastAPI API

## Session 7

✅ Expanded dashboard data payload
✅ Added simple in-memory caching
✅ Added additional dashboard visualizations

## Session 8

✅ Completed dashboard visualizer suite
✅ Added timeline, heatmap, dependency, complexity panels

## Session 9

✅ Built Open Graph share-card generator
✅ Added /share preview route

## Session 10

✅ Built export system: standalone HTML snapshot download
✅ Export page renders treemap/timeline/heatmap
✅ Export includes Print / Save PDF button

## Session 11

✅ Built Nightshift showcase (pre-generated demo)

## Session 12

✅ Built per-repo story pages with OG tags
✅ Added demo payload loading for story page routing

## Session 13

✅ Improved story routing and metadata handling

## Session 14

✅ Story pages now populate subtitle/metadata using GitHub metadata (stars, primary language, last updated)

## Session 15

✅ Added client-side export of dashboard panels to PNG (SVG → canvas)
✅ Added iframe embed option for exports

---

## Session 17 (2026-03-02)

**Focus:** Export enhancement + payload reliability.

### Shipped
- Added a zero-dependency **print-to-PDF helper route**: `/pdf?repo_url=...`.
  - Renders the existing export view inside an iframe with a sticky instruction bar and a one-click "Print / Save PDF" button.
  - Avoids introducing heavy server-side PDF rendering dependencies (Chromium/wkhtmltopdf/etc.).
- Fixed `/api/analyze` **JSON serialization** issues:
  - `treemap` is now converted from `TreemapNode` to a JSON dict (`treemap_to_dict`).
  - `heatmap` is now converted from `HeatmapCell` grid to a JSON dict (`heatmap.to_json`).
- Made `reposcape_cli.py` runnable as a module/script (`python -m reposcape_cli ...`).

### Notes
- Tests: `407 passed`.
- PR: #23 (squash merged).

---

## Session 18 (2026-03-02)

**Focus:** Finish CLI tool + share analysis entrypoint.

### Shipped
- Refactored analysis into a shared module: `src/analyze.py`.
  - Provides `analyze_repo_url(repo_url: str)` for reuse.
  - Keeps the analysis layer free of FastAPI/Pydantic dependencies.
- Fixed the CLI analyze command to call shared analysis logic.
  - `python -m src.cli.main analyze <repo_url>` now produces JSON output (previously crashed due to passing a string into the FastAPI request handler).
- Fixed the web module runner import path.
  - `python -m src.web` now imports the app factory correctly.

### Notes
- Next: comparison mode, historical tracking, GitHub Action.
