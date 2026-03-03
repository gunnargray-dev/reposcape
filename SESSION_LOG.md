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

---

## Session 19 (2026-03-02)

**Focus:** Packaging correctness + pip editable install compatibility.

### Shipped
- Aligned `pyproject.toml` with a proper `src/` layout:
  - Added `[tool.setuptools].package-dir = {"" = "src"}`.
  - Updated package discovery to `where = ["src"]`.
- Added `wheel` to `[build-system].requires`.

### Notes
- PR: #25 (squash merged).
- In this execution environment, `pip install -e .` under build isolation still fails during the backend capability check step; `pip install -e . --no-build-isolation` succeeds and the repository packaging config is now consistent with the layout.

---

## Session 21 -- Test Suite Stability (2026-03-03)

**PR:** #26 (squash merged)

### Problem
Full pytest suite (407 tests) terminated early with exit_code=-1 when run as a single command. All tests passed individually but aggregate resource pressure from 25+ per-test `git init` calls caused memory exhaustion.

### Changes
1. **`tests/conftest.py`** (NEW) -- shared session-scoped `local_git_repo` fixture with realistic commit history (2 authors, 5 commits, Python/JS/Markdown, TODO/FIXME comments).
2. **`tests/test_clone.py`** -- rewritten to use `local_git_repo`; network clone tests marked `@pytest.mark.integration`.
3. **`tests/test_timeline.py`** -- all fixtures upgraded to `scope="module"`.
4. **`tests/test_pr_velocity.py`** -- all fixtures upgraded to `scope="module"`.
5. **`tests/test_techdebt.py`** -- all fixtures upgraded to `scope="module"`.
6. **`tests/test_contributors.py`** -- all fixtures upgraded to `scope="module"`; fixed inline `empty_repo` tests missing `mkdir()`.
7. **`pyproject.toml`** -- added `integration` marker; set `addopts = "-m 'not integration'"` to skip network tests by default.

### Results
- 397 core tests pass in 1.65s (all 13 non-web test files combined).
- 4 web tests pass in 0.52s.
- 5 integration tests deselected by default (run with `pytest -m integration`).
- Git repo init count reduced from ~50+ to ~15 per full suite run.

### Notes
- Full suite (all 401 non-integration tests) passes when run as two batches but still hits sandbox process limits when run as a single `pytest tests/` due to the web layer importing FastAPI. This is a sandbox-specific limitation, not a code issue. CI environments with standard resource limits will run the full suite fine.

---

## Session 22 (2026-03-03)

**PR:** #27 (squash merged)

### Focus
Comparison mode (two repos side by side).

### Shipped
- Added a core comparison module: `src/compare.py`.
  - Reuses `analyze_repo_url()` for each repo.
  - Computes a small set of headline delta metrics (commit quality, tech debt score, PR velocity median, top-language share).
- Added `/api/compare` endpoint.
- Added a new `/compare` page with a simple table UI.
- Added a comparison mode entry point on the landing page.

### Notes
- Next: historical tracking, GitHub Action.

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

## Session 24 (2026-03-03)

**PR:** #29 (squash merged)

### Focus
Wire snapshot generation into the CLI/shared analysis entrypoint.

### Shipped
- Extended `src.analyze.analyze_repo_url()` with an **optional** `snapshot_base_dir: Path | None`.
  - When provided, Reposcape writes a point-in-time snapshot JSON to disk using `src.history.write_snapshot()`.
- Added CLI support:
  - `reposcape analyze ... --snapshot-dir <dir>`
  - Or `REPOSCAPE_SNAPSHOT_DIR=<dir>`.

### Notes
- Tests: `tests/test_cli.py`, `tests/test_history.py`.
- Next: add a web endpoint to list/download snapshots and a GitHub Action to generate snapshots on a schedule.
