# Reposcape Session Log

This file tracks what each scheduled session shipped.

---

## Session 46 (2026-03-04)

**PR:** #46 (squash merged)

### Focus
History chart: multi-metric toggles/overlays (dashboard).

### Shipped
- Dashboard History: add checkbox toggles to overlay multiple metrics at once (each series normalized for overlay).
- Chart: adds a legend with per-metric colors; retains baseline and optional trendline controls.
- Single-series view: improves y-axis tick formatting (signed deltas and percent handling).

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 45 (2026-03-04)

**PR:** #45 (squash merged)

### Focus
Optional trendline overlay for the History chart.

### Shipped
- Dashboard History (SVG): adds an optional linear trendline overlay (least-squares fit) over the currently selected metric series.
- UI: new "Trendline" checkbox alongside Metric/Baseline selectors.
- Works for both raw series and baseline-relative delta series.

### Tests
- `python -m pytest tests/web -q --tb=short`

---

## Session 44 (2026-03-04)

**PR:** #44 (squash merged)

### Focus
Baseline-relative deltas on the history chart.

### Shipped
- Dashboard: when a baseline snapshot is selected for the History chart, plot and label values as deltas vs baseline (value - baselineValue).
- UI: y-axis labels now show signed deltas; `debt` deltas are formatted as percent.
- Chart: adds a dashed zero reference line when baseline is active.

### Tests
- `python -m pytest tests/web -q --tb=short`

---

## Session 43 (2026-03-04)

**PR:** #43 (squash merged)

### Focus
Interactive History chart (SVG) using /api/snapshots/series.

### Shipped
- Dashboard: adds a new History section under Snapshots.
- Web API: add `GET /api/snapshots/{owner}/{repo}/series` returning time series metrics.
- Dashboard: renders an SVG line chart for total_source_lines with a tooltip.

### Tests
- `python -m pytest tests/web -q --tb=short`

---

## Session 42 (2026-03-05)

**PR:** #50 (squash merged)

### Focus
Start wiring the Pro upgrade flow: stable billing endpoints and a real dashboard Upgrade action.

### Shipped
- Add `src/web/routes/billing.py` with a minimal billing stub:
  - `POST /api/billing/checkout` returns a `checkout_url` redirect target when billing is enabled.
  - `GET /billing/success` + `GET /billing/cancel` minimal pages.
- App: wire `billing.router` into the FastAPI app.
- Dashboard: Upgrade link now calls `/api/billing/checkout` and redirects to the returned `checkout_url` (instead of a placeholder alert).

### Notes
- Billing is disabled by default; enable with `REPOSCAPE_BILLING_ENABLED=1`.
- No entitlement persistence yet (future session will add Stripe checkout + webhooks).

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`
- `python -m pytest tests/web/test_og.py -q --tb=short`

---

## Session 40 (2026-03-05)

**PR:** #47 (squash merged)

### Focus
History chart UX: clarify overlay normalization.

### Shipped
- Dashboard History: clarify overlay note (each selected metric is normalized to its own min..max range for comparability).

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 41 (2026-03-05)

**PR:** #49 (squash merged)

### Focus
Pro tier groundwork: feature flag + watermark/upgrade CTA.

### Shipped
- Add `REPOSCAPE_PRO` env-var-backed Pro feature flag stub (`src/web/pro.py`).
- Dashboard: show a watermark/upgrade CTA when Pro is disabled (hidden when enabled).

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 39 (2026-03-04)

**PR:** #46 (squash merged)

### Focus
History chart: multi-metric toggles/overlays (dashboard).

### Shipped
- Dashboard History: add checkbox toggles to overlay multiple metrics at once (each series normalized for overlay).
- Chart: adds a legend with per-metric colors; retains baseline and optional trendline controls.
- Single-series view: improves y-axis tick formatting (signed deltas and percent handling).

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 38 (2026-03-04)

**PR:** #45 (squash merged)

### Focus
Optional trendline overlay for the History chart.

### Shipped
- Dashboard History (SVG): adds an optional linear trendline overlay (least-squares fit) over the currently selected metric series.
- UI: new "Trendline" checkbox alongside Metric/Baseline selectors.
- Works for both raw series and baseline-relative delta series.

### Tests
- `python -m pytest tests/web -q --tb=short`


---

## Session 37 (2026-03-04)

**PR:** #44 (squash merged)

### Focus
Baseline-relative deltas on the history chart.

### Shipped
- Dashboard: when a baseline snapshot is selected for the History chart, plot and label values as deltas vs baseline (value - baselineValue).
- UI: y-axis labels now show signed deltas; `debt` deltas are formatted as percent.
- Chart: adds a dashed zero reference line when baseline is active.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 36 (2026-03-04)

**PR:** #42 (squash merged)

### Focus
History series endpoint: baseline selection.

### Shipped
- Web API: extend `/api/snapshots/{owner}/{repo}/series` to accept optional `baseline_as_of`.
- Response includes baseline snapshot metadata and baseline-relative delta metrics.

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 35 (2026-03-04)

**PR:** #41 (squash merged)

### Focus
Timeline/diff view (UI).

### Shipped
- Dashboard: add timeline view for snapshot diffs in addition to raw delta JSON.

### Tests
- `python -m pytest tests/test_history_delta.py -q --tb=short`

---

## Session 34 (2026-03-04)

**PR:** #40 (squash merged)

### Focus
Snapshot diff chips.

### Shipped
- Dashboard Diff: show Snapshot B chips (as_of, LOC, files, TODOs, debt, avg cx) when loading a diff.

### Tests
- `python -m pytest tests/test_history_delta.py -q --tb=short`

---

## Session 33 (2026-03-04)

**PR:** #39 (squash merged)

### Focus
Snapshot timeline sparkline.

### Shipped
- Dashboard: show a tiny sparkline under snapshots to visualize snapshot cadence.

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 32 (2026-03-04)

**PR:** #38 (squash merged)

### Focus
Fix diff endpoint for missing snapshot.

### Shipped
- Snapshot diff endpoint: return 404 when snapshot missing instead of 500.

### Tests
- `python -m pytest tests/test_history_delta.py -q --tb=short`

---

## Session 31 (2026-03-04)

**PR:** #37 (squash merged)

### Focus
Snapshot diff endpoint + dashboard delta table.

### Shipped
- Web API: add `GET /api/snapshots/{owner}/{repo}/diff?a=...&b=...`.
- Dashboard: adds a delta table under the snapshots section.

### Tests
- `python -m pytest tests/test_history_delta.py -q --tb=short`

---

## Session 30 (2026-03-04)

**PR:** #36 (squash merged)

### Focus
Snapshots release selector.

### Shipped
- Dashboard: add a release selector to pick a tagged snapshots bundle.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 29 (2026-03-04)

**PR:** #35 (squash merged)

### Focus
Dashboard: snapshots release download link.

### Shipped
- Dashboard: add a "Download snapshots" link pointing to the latest release asset.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 28 (2026-03-04)

**PR:** #34 (squash merged)

### Focus
Improve unit test runner durations.

### Shipped
- Test runner: add per-file pytest scripts and capture durations.

### Tests
- (none)

---

## Session 27 (2026-03-04)

**PR:** #33 (squash merged)

### Focus
GitHub Action to auto-generate snapshots bundle on release.

### Shipped
- Add a GitHub Actions workflow to generate and upload snapshot bundle on release.

### Tests
- (none)

---

## Session 26 (2026-03-04)

**PR:** #32 (squash merged)

### Focus
Dashboard snapshot selector.

### Shipped
- Dashboard: add a snapshot selector and load snapshot payload.

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 25 (2026-03-04)

**PR:** #31 (squash merged)

### Focus
Snapshot list + payload API.

### Shipped
- Web API: list snapshots and fetch snapshot payload.

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 24 (2026-03-04)

**PR:** #30 (squash merged)

### Focus
Wire snapshot generation into CLI.

### Shipped
- CLI: add snapshot-dir support and snapshot generation.

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 23 (2026-03-04)

**PR:** #29 (squash merged)

### Focus
Snapshot persistence utilities.

### Shipped
- Add snapshot bucketing + persistence utilities in `src/history.py`.

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 22 (2026-03-04)

**PR:** #28 (squash merged)

### Focus
Comparison mode.

### Shipped
- Add compare endpoint + UI.

### Tests
- `python -m pytest tests/test_cli.py -q --tb=short`

---

## Session 21 (2026-03-04)

**PR:** #27 (squash merged)

### Focus
Test suite stability.

### Shipped
- Add test suite improvements.

### Tests
- (see PR)

---

## Session 20 (2026-03-04)

**PR:** #26 (squash merged)

### Focus
Packaging.

### Shipped
- Fix setuptools discovery.

### Tests
- (see PR)

---

## Session 19 (2026-03-04)

**PR:** #25 (squash merged)

### Focus
CLI tool.

### Shipped
- Add CLI.

### Tests
- (see PR)

---

## Session 18 (2026-03-04)

**PR:** #24 (squash merged)

### Focus
Server-side PDF generation.

### Shipped
- Add PDF endpoints.

### Tests
- (see PR)

---

## Session 17 (2026-03-04)

**PR:** #23 (squash merged)

### Focus
Client-side SVG->PNG export + embeds.

### Shipped
- Add export enhancements.

### Tests
- (see PR)

---

## Session 16 (2026-03-04)

**PR:** #22 (squash merged)

### Focus
Story pages: GitHub metadata.

### Shipped
- Add GitHub metadata to story pages.

### Tests
- (see PR)

---

## Session 15 (2026-03-04)

**PR:** #21 (squash merged)

### Focus
Share cards: OG meta tags.

### Shipped
- Wire OG meta tags to share cards.

### Tests
- (see PR)

---

## Session 14 (2026-03-04)

**PR:** #20 (squash merged)

### Focus
Export system: HTML snapshot download.

### Shipped
- Add export system.

### Tests
- (see PR)

---

## Session 13 (2026-03-04)

**PR:** #19 (squash merged)

### Focus
Nightshift showcase.

### Shipped
- Add showcase.

### Tests
- (see PR)

---

## Session 12 (2026-03-04)

**PR:** #18 (squash merged)

### Focus
Per-repo story pages.

### Shipped
- Add story pages.

### Tests
- (see PR)

---

## Session 11 (2026-03-04)

**PR:** #17 (squash merged)

### Focus
Export system enhancements.

### Shipped
- Add export enhancements.

### Tests
- (see PR)

---

## Session 10 (2026-03-04)

**PR:** #16 (squash merged)

### Focus
Export system.

### Shipped
- Add export system.

### Tests
- (see PR)

---

## Session 9 (2026-03-04)

**PR:** #15 (squash merged)

### Focus
Share cards.

### Shipped
- Add share cards.

### Tests
- (see PR)

---

## Session 8 (2026-03-04)

**PR:** #14 (squash merged)

### Focus
Dashboard expansions.

### Shipped
- Expand dashboard.

### Tests
- (see PR)

---

## Session 7 (2026-03-04)

**PR:** #13 (squash merged)

### Focus
Add caching.

### Shipped
- Add caching.

### Tests
- (see PR)

---

## Session 6 (2026-03-04)

**PR:** #12 (squash merged)

### Focus
Landing + dashboard.

### Shipped
- Add landing + dashboard.

### Tests
- (see PR)

---

## Session 5 (2026-03-04)

**PR:** #11 (squash merged)

### Focus
Advanced analyzers.

### Shipped
- Add PR velocity + tech debt.

### Tests
- (see PR)

---

## Session 4 (2026-03-04)

**PR:** #10 (squash merged)

### Focus
Advanced analyzers.

### Shipped
- Add dependency graph + complexity.

### Tests
- (see PR)

---

## Session 3 (2026-03-04)

**PR:** #9 (squash merged)

### Focus
Core analyzers.

### Shipped
- Add contributors + velocity + commit quality.

### Tests
- (see PR)

---

## Session 2 (2026-03-04)

**PR:** #8 (squash merged)

### Focus
Heatmap + treemap.

### Shipped
- Add heatmap + treemap.

### Tests
- (see PR)

---

## Session 1 (2026-03-04)

**PR:** #7 (squash merged)

### Focus
Repo cloner + analyzers.

### Shipped
- Initial release.

### Tests
- (see PR)
