"""PDF helper routes.

These endpoints provide a zero-dependency path to "Save as PDF" for Reposcape
reports.

- /pdf?repo_url=... renders a print-optimized page.

This intentionally does *not* attempt server-side PDF generation.
"""

from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

from src.web.export import build_export_html
from src.web.pdf_helper import build_pdf_helper_html
from src.web.routes.api import AnalyzeRequest, analyze_repo

router = APIRouter(tags=["pdf"])


@router.get("/pdf", response_class=HTMLResponse)
def pdf_helper(repo_url: str = Query(..., description="GitHub repository URL")) -> HTMLResponse:
    """Render a helper page for printing an analysis to PDF.

    Args:
        repo_url: GitHub repository URL.

    Returns:
        HTML response.
    """

    analysis = analyze_repo(AnalyzeRequest(repo_url=repo_url))
    payload = {k: v for k, v in analysis.items() if k not in {"cached", "duration_ms"}}
    export_html = build_export_html(payload)
    html = build_pdf_helper_html(export_html, repo_url=repo_url)
    return HTMLResponse(content=html)
