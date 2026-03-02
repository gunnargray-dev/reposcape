"""Export helpers for the web dashboard.

This module intentionally uses only the Python standard library.

Phase 3 roadmap calls for PNG/PDF/SVG exports. Since the project currently
restricts dependencies to stdlib + FastAPI/Jinja2/D3 (and Pillow is used only
for share-card images), this first step implements an **SVG export** endpoint.

The endpoint serves a minimal, self-contained HTML page that renders the key
charts and can be printed to PDF by the browser.

Future sessions can add:
- front-end SVG->PNG (canvas) for chart panels
- optional server-side PNG/PDF rendering once a dependency strategy is chosen
"""

from __future__ import annotations

import json
from html import escape
from typing import Any


def build_export_html(payload: dict[str, Any]) -> str:
    """Build a standalone HTML export view.

    Args:
        payload: Analysis payload returned by /api/analyze.

    Returns:
        HTML document string.
    """

    repo_url = escape(str(payload.get("repo_url", "")))
    data_json = json.dumps(payload)

    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
    <title>Reposcape Export</title>
    <style>
      body {{ font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; margin: 24px; color: #0B1220; }}
      h1 {{ margin: 0 0 6px 0; font-size: 20px; }}
      .meta {{ color: #667085; margin-bottom: 18px; }}
      .grid {{ display: grid; grid-template-columns: 1fr; gap: 18px; }}
      .card {{ border: 1px solid #E4E7EC; border-radius: 10px; padding: 14px; }}
      .card h2 {{ margin: 0 0 10px 0; font-size: 14px; color: #344054; }}
      .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; font-size: 11px; }}
      pre {{ white-space: pre-wrap; word-break: break-word; }}
      @media print {{ body {{ margin: 0.5in; }} .card {{ break-inside: avoid; }} }}
    </style>
    <script src=\"https://d3js.org/d3.v7.min.js\"></script>
    <script defer src=\"/static/export.js\"></script>
  </head>
  <body>
    <h1>Reposcape export</h1>
    <div class=\"meta\">{repo_url}</div>

    <div class=\"controls card\" style=\"margin-bottom: 18px;\">
      <h2>Exports</h2>
      <div style=\"display:flex; gap:12px; align-items:center; flex-wrap:wrap;\">
        <label>Panel
          <select id=\"panel-select\">
            <option value=\"treemap\">Treemap</option>
            <option value=\"timeline\">Timeline</option>
            <option value=\"heatmap\">Heatmap</option>
          </select>
        </label>
        <label>Scale
          <select id=\"scale-select\">
            <option value=\"1\">1x</option>
            <option value=\"2\" selected>2x</option>
            <option value=\"3\">3x</option>
          </select>
        </label>
        <button id=\"download-panel\" type=\"button\" style=\"padding:8px 10px; border-radius:8px; border:1px solid #E4E7EC; background:#FFFFFF;\">Download PNG</button>
        <button type=\"button\" onclick=\"window.print()\" style=\"padding:8px 10px; border-radius:8px; border:1px solid #E4E7EC; background:#FFFFFF;\">Print / Save PDF</button>
      </div>
      <div style=\"margin-top:8px; color:#667085; font-size:12px;\">PNG export is client-side (SVG → canvas). For best results, use Chrome.</div>
    </div>

    <div class=\"grid\">
      <section class=\"card\">
        <h2>Treemap (LOC by file)</h2>
        <div id=\"treemap\"></div>
      </section>

      <section class=\"card\">
        <h2>Commit timeline</h2>
        <div id=\"timeline\"></div>
      </section>

      <section class=\"card\">
        <h2>Commit heatmap</h2>
        <div id=\"heatmap\"></div>
      </section>

      <section class=\"card\">
        <h2>Key JSON (languages, contributors, techdebt)</h2>
        <pre id=\"json\" class=\"mono\"></pre>
      </section>
    </div>

    <script>
      const payload = {data_json};

      function safeJson(obj) {{
        return JSON.stringify(obj || null, null, 2);
      }}

      function el(id) {{
        return document.getElementById(id);
      }}

      function renderTreemap(treeData) {{
        const container = el('treemap');
        container.innerHTML = '';

        if (!treeData) {{
          container.textContent = 'No treemap data available.';
          return;
        }}

        const width = 960;
        const height = 520;

        const root = d3.hierarchy(treeData)
          .sum(d => d.value || 0)
          .sort((a,b) => (b.value||0) - (a.value||0));

        d3.treemap()
          .size([width, height])
          .padding(2)(root);

        const svg = d3.select(container).append('svg')
          .attr('width', width)
          .attr('height', height)
          .attr('viewBox', `0 0 ${{width}} ${{height}}`);

        const nodes = svg.selectAll('g')
          .data(root.leaves())
          .enter().append('g')
          .attr('transform', d => `translate(${{d.x0}},${{d.y0}})`);

        nodes.append('rect')
          .attr('width', d => d.x1 - d.x0)
          .attr('height', d => d.y1 - d.y0)
          .attr('fill', '#2E90FA')
          .attr('fill-opacity', 0.25)
          .attr('stroke', '#2E90FA');

        nodes.append('title')
          .text(d => `${{d.data.name}}\n${{d.value}} LOC`);

        nodes.append('text')
          .attr('x', 4)
          .attr('y', 14)
          .attr('font-size', '12px')
          .attr('fill', '#0B1220')
          .text(d => d.data.name)
          .each(function(d) {{
            const rectWidth = d.x1 - d.x0;
            const self = d3.select(this);
            if (self.node().getComputedTextLength() > rectWidth - 6) {{
              const name = d.data.name;
              self.text(name.length > 16 ? name.slice(0, 15) + '…' : name);
            }}
          }});
      }}

      function renderTimeline(tl) {{
        const container = el('timeline');
        container.innerHTML = '';

        if (!tl || !Array.isArray(tl.buckets)) {{
          container.textContent = 'No timeline data available.';
          return;
        }}

        const width = 960;
        const height = 240;
        const margin = {{ top: 10, right: 20, bottom: 30, left: 40 }};

        const buckets = tl.buckets.map(b => ({{
          date: new Date(b.start),
          commits: b.count || 0
        }}));

        const x = d3.scaleTime()
          .domain(d3.extent(buckets, d => d.date))
          .range([margin.left, width - margin.right]);

        const y = d3.scaleLinear()
          .domain([0, d3.max(buckets, d => d.commits) || 1]).nice()
          .range([height - margin.bottom, margin.top]);

        const svg = d3.select(container).append('svg')
          .attr('width', width)
          .attr('height', height)
          .attr('viewBox', `0 0 ${{width}} ${{height}}`);

        svg.append('path')
          .datum(buckets)
          .attr('fill', 'none')
          .attr('stroke', '#2E90FA')
          .attr('stroke-width', 2)
          .attr('d', d3.line()
            .x(d => x(d.date))
            .y(d => y(d.commits))
          );

        svg.append('g')
          .attr('transform', `translate(0,${{height - margin.bottom}})`)
          .call(d3.axisBottom(x).ticks(6));

        svg.append('g')
          .attr('transform', `translate(${{margin.left}},0)`)
          .call(d3.axisLeft(y).ticks(4));
      }}

      function renderHeatmap(hm) {{
        const container = el('heatmap');
        container.innerHTML = '';

        if (!hm || !Array.isArray(hm.weeks)) {{
          container.textContent = 'No heatmap data available.';
          return;
        }}

        const cell = 14;
        const gap = 2;
        const weeks = hm.weeks;
        const width = (weeks.length * (cell + gap)) + 60;
        const height = (7 * (cell + gap)) + 40;

        const maxVal = d3.max(weeks.flatMap(w => w.days.map(d => d.count || 0))) || 1;
        const color = d3.scaleLinear()
          .domain([0, maxVal])
          .range(['#EEF2FF', '#2E90FA']);

        const svg = d3.select(container).append('svg')
          .attr('width', width)
          .attr('height', height)
          .attr('viewBox', `0 0 ${{width}} ${{height}}`);

        svg.append('text')
          .attr('x', 0)
          .attr('y', 12)
          .attr('class', 'mono')
          .text(`${{hm.start || ''}} → ${{hm.end || ''}}`);

        const g = svg.append('g').attr('transform', 'translate(40,20)');

        weeks.forEach((w, wi) => {{
          w.days.forEach((d, di) => {{
            g.append('rect')
              .attr('x', wi * (cell + gap))
              .attr('y', di * (cell + gap))
              .attr('width', cell)
              .attr('height', cell)
              .attr('fill', color(d.count || 0))
              .append('title')
              .text(`${{d.date}}: ${{d.count}} commits`);
          }});
        }});
      }}

      el('json').textContent = safeJson({{
        languages: payload.languages,
        contributors: payload.contributors,
        techdebt: payload.techdebt
      }});

      renderTreemap(payload.treemap);
      renderTimeline(payload.timeline);
      renderHeatmap(payload.heatmap);
    </script>
  </body>
</html>
"""
