"""Web JSON API endpoints.

Note: core analysis logic lives in `src.analyze.analyze_repo_url` so the web API
and CLI can share implementation.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from src.analyze import analyze_repo_url
from src.compare import build_comparison_payload
from src.web.demo import load_demo_payload
from src.web.export import build_export_html

router = APIRouter(prefix="/api", tags=["api"])


class AnalyzeRequest(BaseModel):
    """Request payload for analyzing a Git repository."""

    repo_url: HttpUrl


class CompareRequest(BaseModel):
    """Request payload for comparing two Git repositories."""

    repo_a_url: HttpUrl
    repo_b_url: HttpUrl


@router.post("/analyze")
def analyze_repo(req: AnalyzeRequest) -> dict[str, Any]:
    """Clone a repo and run a set of analyzers.

    Note: this endpoint is intentionally synchronous for now.

    Args:
        req: Analyze request.

    Returns:
        JSON-serializable analysis result.
    """

    try:
        return analyze_repo_url(str(req.repo_url))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/compare")
def compare_repos(req: CompareRequest) -> dict[str, Any]:
    """Compare two GitHub repo URLs.

    Args:
        req: Compare request.

    Returns:
        JSON-serializable comparison payload.
    """

    try:
        return build_comparison_payload(str(req.repo_a_url), str(req.repo_b_url))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/demo/{name}")
def demo_payload(name: str) -> dict[str, Any]:
    """Return a packaged demo payload by name.

    Args:
        name: Demo payload name (without extension).

    Returns:
        Demo analysis payload as JSON.
    """

    try:
        return load_demo_payload(name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Unknown demo: {name}") from e


@router.post("/export.html")
def export_html(req: AnalyzeRequest) -> dict[str, Any]:
    """Create a standalone HTML export view.

    This is a first step toward the broader export system.

    Args:
        req: Analyze request.

    Returns:
        JSON containing the HTML document string.
    """

    analysis = analyze_repo(req)
    payload = {k: v for k, v in analysis.items() if k not in {"cached", "duration_ms"}}
    return {"repo_url": payload.get("repo_url"), "html": build_export_html(payload)}
