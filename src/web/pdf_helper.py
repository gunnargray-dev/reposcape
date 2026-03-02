"""Print-to-PDF helper HTML.

Reposcape intentionally keeps its dependency footprint small (stdlib + FastAPI/
Jinja2/D3 for web). True server-side PDF generation typically requires
non-trivial third-party dependencies (e.g., headless Chromium, wkhtmltopdf,
WeasyPrint, or a SaaS renderer).

This module implements the next-best, zero-dependency step: a helper HTML page
with print-specific CSS and lightweight UX to nudge users into a consistent,
high-quality "Save as PDF" flow.

The helper is meant to be used in conjunction with the existing /api/export.html
endpoint:

  1) The browser requests /api/export.html to get a standalone export HTML.
  2) The browser opens that export HTML in a new tab.
  3) The export HTML includes a Print / Save PDF button.

This module provides a dedicated endpoint that renders that export HTML directly
(server-side) so it can be linked to and printed without additional JS wiring.

Future work:
- Introduce optional server-side rendering behind an extra dependency flag.
- Generate PDFs in CI for demos/releases.
"""

from __future__ import annotations

from html import escape


def build_pdf_helper_html(export_html: str, *, repo_url: str) -> str:
    """Wrap the export HTML with a small instructions banner.

    Args:
        export_html: Full export HTML document.
        repo_url: Repository URL used for the analysis.

    Returns:
        HTML document that embeds the export view in an iframe and adds a small
        print guidance banner.
    """

    safe_repo = escape(repo_url)

    # Note: embedding the export view in an iframe avoids duplicating markup.
    # The user can still use the in-frame Print button or the browser's print
    # dialog.
    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
    <title>Reposcape PDF Helper</title>
    <style>
      body {{
        margin: 0;
        font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
        color: #0B1220;
      }}
      .bar {{
        position: sticky;
        top: 0;
        z-index: 10;
        background: #FFFFFF;
        border-bottom: 1px solid #E4E7EC;
        padding: 12px 14px;
        display: flex;
        gap: 12px;
        align-items: center;
        flex-wrap: wrap;
      }}
      .title {{ font-weight: 600; }}
      .muted {{ color: #667085; font-size: 13px; }}
      .btn {{
        padding: 8px 10px;
        border-radius: 8px;
        border: 1px solid #E4E7EC;
        background: #FFFFFF;
        cursor: pointer;
      }}
      iframe {{ width: 100%; height: calc(100vh - 58px); border: 0; }}
      @media print {{
        .bar {{ display: none; }}
        iframe {{ height: 100vh; }}
      }}
    </style>
  </head>
  <body>
    <div class=\"bar\">
      <div>
        <div class=\"title\">Save as PDF</div>
        <div class=\"muted\">Repo: <span style=\"font-family: ui-monospace;\">{safe_repo}</span></div>
      </div>
      <button class=\"btn\" type=\"button\" onclick=\"window.print()\">Print / Save PDF</button>
      <div class=\"muted\">Tip: Use Chrome → Destination: Save as PDF → Background graphics: on.</div>
    </div>

    <iframe title=\"Reposcape export\" srcdoc=\"{escape(export_html)}\"></iframe>
  </body>
</html>
"""
