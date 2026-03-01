"""JSON API endpoints."""

from __future__ import annotations

import tempfile
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from src.clone import clone_repo
from src.languages import analyze_languages
from src.treemap import build_treemap

router = APIRouter(prefix="/api", tags=["api"])


class AnalyzeRequest(BaseModel):
    """Request payload for analyzing a Git repository."""

    repo_url: HttpUrl


@router.post("/analyze")
def analyze_repo(req: AnalyzeRequest) -> dict[str, Any]:
    """Clone a repo and run a small set of analyzers.

    Note: This is the minimal Phase 3 starting point.

    Args:
        req: Analyze request.

    Returns:
        JSON-serializable analysis result.
    """

    try:
        with tempfile.TemporaryDirectory(prefix="reposcape-") as tmpdir:
            repo_path = clone_repo(str(req.repo_url), tmpdir)

            languages = analyze_languages(repo_path)
            treemap = build_treemap(repo_path)

            return {
                "repo_url": str(req.repo_url),
                "languages": languages,
                "treemap": treemap,
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
