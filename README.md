# Reposcape

**Turn any GitHub repo into a beautiful visual story.**

Architecture diagrams. Commit heatmaps. Contributor timelines. Code complexity maps. Dependency graphs. Tech debt scores.

Paste a repo URL. Get stunning, shareable visualizations.

---

## Stats

| Metric | Value |
|--------|-------|
| Sessions | 17 |
| PRs merged | 23 |
| Source modules | 13 |
| Tests passing | 407 |
| Visualizations | 9 |

---

## How It Works

1. Paste a public GitHub repo URL
2. Reposcape clones and analyzes the codebase
3. Get interactive visualizations: treemaps, heatmaps, timelines, graphs
4. Share on Twitter/LinkedIn with auto-generated Open Graph cards

## Visualizations

- **Language Breakdown** -- LOC by language, file type distribution
- **Commit Heatmap** -- GitHub-style contribution calendar per repo
- **File Treemap** -- Interactive treemap of file sizes and types
- **Contributor Stats** -- Who wrote what, commit velocity, active periods
- **Dependency Graph** -- Module relationships visualized
- **Complexity Heatmap** -- Cyclomatic complexity per file
- **Commit Timeline** -- Animated evolution of the repo
- **PR Velocity** -- Open-to-merge time, throughput metrics
- **Tech Debt Score** -- TODO density, large files, stale branches

## Tech Stack

- Pure Python analysis engine (stdlib only where possible)
- FastAPI web server
- D3.js / Three.js frontend visualizations
- GitHub API integration

## Development

This project is built autonomously by [Perplexity Computer](https://perplexity.ai) in 2-hour sessions. Each session reads the repo state, picks tasks from the roadmap, writes and tests code, pushes PRs, and updates the log.

See [SESSION_LOG.md](SESSION_LOG.md) for the full development history.

## License

MIT

## Web (prototype)

Install web dependencies:

```bash
pip install -e .[web]
```

Run the dev server:

```bash
python -m web
```

Then open:
- `http://127.0.0.1:8000/` (landing)
- `http://127.0.0.1:8000/dashboard` (dashboard)


### Export

From the dashboard, click **Export HTML** to download a standalone HTML snapshot of the current analysis.

In the exported page you can:
- **Download PNG** for individual chart panels (client-side SVG → canvas → PNG)
- **Print / Save PDF** via your browser’s print dialog

For a more guided PDF flow, open:
- `/pdf?repo_url=https://github.com/OWNER/REPO`

Tip: for best PNG results, use Chrome.


### Story URLs

Use `/r/{owner}/{repo}` to get a share-friendly landing page with Open Graph meta tags.
