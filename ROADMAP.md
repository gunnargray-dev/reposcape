# Reposcape Roadmap

## Phase 1 -- Core Analysis Engine (Sessions 1-5)

### Active Sprint

- [x] Commit frequency heatmap data generator (Session 2 -- completed Session 2)
- [x] File tree analyzer + treemap data (Session 2 -- completed Session 2)
- [x] Contributor stats engine (Session 3 -- completed Session 3)
- [x] Author velocity tracking (Session 3 -- completed Session 3)
- [x] Commit message quality analyzer (Session 3 -- completed Session 3)

**Phase 1 complete!** All core analysis engine modules are built and tested.

### Backlog

_Phase 1 items all done._

## Phase 2 -- Advanced Visualizations (Sessions 6-10)

- [x] Dependency graph (Python/JS/TS import parsing) (Session 4)
- [x] Code complexity heatmap (cyclomatic complexity per file) (Session 4)
- [x] Commit timeline (animated repo evolution) (Session 5)
- [x] PR velocity tracker (open-to-merge time, throughput) (Session 5)
- [x] Tech debt scorer (TODO density, large files, deep nesting) (Session 5)

**Phase 2 complete!**

## Phase 3 -- Web Frontend (Sessions 6-10)

- [x] Landing page with repo URL input (Session 6)
- [x] Visualization dashboard (initial dashboard + treemap) (Session 6)
- [x] Expand analyze payload + add basic caching + extra dashboard sections (Session 7)
- [x] Expand dashboard to render additional analyzers (timeline, heatmap, tech debt, complexity) (Session 8)
- [x] Share cards (Open Graph images for social) (Session 9)
- [x] Per-repo story pages with OG meta tags wired to share cards (Session 12)
- [x] Export system (HTML snapshot download; printable to PDF) (Session 10)
- [x] Nightshift showcase (pre-generated demo using nightshift repo) (Session 11)

## Phase 3.1 -- Story + Export Enhancements (Sessions 11-15)

- [x] Story pages: populate subtitle/metadata (stars, primary language, last updated) from GitHub metadata (Session 14)
- [x] Export system: client-side SVG->PNG for shareable assets; optional iframe embed (Session 15)
- [x] Export system: server-side PDF generation or print-to-PDF helper (Session 17)

## Phase 4 -- Growth & Monetization (Sessions 16-20)

- [x] CLI tool (`reposcape analyze <url>`) (Session 18)
- [x] Packaging: fix `pip install -e .` / setuptools discovery for `src/` layout (Session 19)
- [x] Test suite stability: module-scoped fixtures, integration markers, shared conftest (Session 21)
- [ ] Comparison mode (two repos side by side)
- [ ] Historical tracking (repo evolution over time)
- [ ] GitHub Action (auto-generate on release)
- [ ] Pro tier + Stripe (payments, private repos, watermark removal)

## Completed

- [x] Repo cloner + git log parser (Session 1)
- [x] Language breakdown analyzer (Session 1)
- [x] Test framework + CI pipeline (Session 1)
- [x] Commit frequency heatmap data generator (Session 2)
- [x] File tree analyzer + treemap data (Session 2)
- [x] Contributor stats engine (Session 3)
- [x] Author velocity tracking (Session 3)
- [x] Commit message quality analyzer (Session 3)
- [x] Dependency graph (Session 4)
- [x] Code complexity heatmap (Session 4)
- [x] Commit timeline (Session 5)
- [x] PR velocity tracker (Session 5)
- [x] Tech debt scorer (Session 5)
