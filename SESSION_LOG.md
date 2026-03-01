# Reposcape Session Log

Autonomous development sessions by Perplexity Computer.

---

## Session 1 — 2026-03-01

**PR:** https://github.com/gunnargray-dev/reposcape/pull/1  
**Tests passing:** 91

### Built

- **`src/clone.py`** — Git repository cloner and log parser
  - `clone_repo(url, target_dir)` — clones any public repo via subprocess git
  - `parse_git_log(repo_path)` — full commit history with hash, author, date, message, files_changed, insertions, deletions (numstat)
  - `get_repo_info(repo_path)` — repo summary: name, branch, commits, dates, author count

- **`src/languages.py`** — Language breakdown analyzer
  - `detect_language(file_path)` — maps 40+ extensions to language names
  - `count_lines(file_path)` — non-empty LOC counter with binary-file handling
  - `analyze_languages(repo_path)` — LOC by language with percentages; excludes .git, node_modules, __pycache__, etc.
  - `get_file_tree(repo_path)` — flat file list for treemap visualization

- **Test framework**
  - `tests/test_clone.py` — 27 tests
  - `tests/test_languages.py` — 64 tests
  - **91 total, all passing**

---

## Session 2 — 2026-03-01

**PR:** https://github.com/gunnargray-dev/reposcape/pull/2  
**Tests passing:** 104

### Built

- **`src/heatmap.py`** — Commit frequency heatmap grid generator
  - `build_commit_heatmap(commit_datetimes, start=None, end=None, week_start=0)` — weeks x days grid with per-day counts

- **`src/treemap.py`** — File tree analyzer + treemap data generator
  - `build_treemap(repo_path, file_paths=None, ignore=None)` — hierarchical tree with LOC-based sizing

- **Tests**
  - `tests/test_heatmap.py`
  - `tests/test_treemap.py`
