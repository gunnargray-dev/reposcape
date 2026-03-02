"""JSON API endpoints."""

from __future__ import annotations

import tempfile
import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from src.clone import clone_repo, parse_git_log
from src.commit_quality import analyze_commit_quality
from src.complexity import analyze_repo_complexity
from src.contributors import analyze_contributors
from src.dependencies import build_dependency_graph
from src.heatmap import build_commit_heatmap, to_json as heatmap_to_json
from src.languages import analyze_languages
from src.pr_velocity import estimate_pr_velocity
from src.techdebt import calculate_tech_debt_score
from src.timeline import build_commit_timeline
from src.treemap import build_treemap, treemap_to_dict
from src.web.demo import load_demo_payload
from src.web.export import build_export_html

router = APIRouter(prefix="/api", tags=["api"])

_CACHE_TTL_SECONDS = 300
_analysis_cache: dict[str, tuple[float, dict[str, Any]]] = {}


def _cache_get(key: str) -> dict[str, Any] | None:
    """Return cached value if present and unexpired."""

    item = _analysis_cache.get(key)
    if item is None:
        return None

    expires_at, payload = item
    if time.time() >= expires_at:
        _analysis_cache.pop(key, None)
        return None

    return payload


def _cache_set(key: str, payload: dict[str, Any]) -> None:
    """Store payload with a TTL."""

    _analysis_cache[key] = (time.time() + _CACHE_TTL_SECONDS, payload)


def _load_commit_datetimes(repo_path: str) -> list[datetime]:
    """Load commit datetimes for a repository.

    Args:
        repo_path: Local git repository path.

    Returns:
        List of datetimes (newest first).
    """

    commits = parse_git_log(repo_path)
    dts: list[datetime] = []
    for commit in commits:
        dts.append(datetime.fromisoformat(str(commit.get("date"))))
    return dts


class AnalyzeRequest(BaseModel):
    """Request payload for analyzing a Git repository."""

    repo_url: HttpUrl


@router.post("/analyze")
def analyze_repo(req: AnalyzeRequest) -> dict[str, Any]:
    """Clone a repo and run a set of analyzers.

    Note: this endpoint is intentionally synchronous for now, and uses a simple
    in-memory cache to avoid repeat work during a short window.

    Args:
        req: Analyze request.

    Returns:
        JSON-serializable analysis result.
    """

    cache_key = str(req.repo_url)
    cached = _cache_get(cache_key)
    if cached is not None:
        return {"cached": True, "duration_ms": 0, **cached}

    try:
        start = time.perf_counter()
        with tempfile.TemporaryDirectory(prefix="reposcape-") as tmpdir:
            repo_path = clone_repo(str(req.repo_url), tmpdir)
            commit_datetimes = _load_commit_datetimes(repo_path)

            payload: dict[str, Any] = {
                "repo_url": str(req.repo_url),
                "languages": analyze_languages(repo_path),
                "treemap": treemap_to_dict(build_treemap(repo_path)),
                "contributors": analyze_contributors(repo_path),
                "commit_quality": analyze_commit_quality(repo_path),
                "timeline": build_commit_timeline(repo_path, bucket="week"),
                "complexity": analyze_repo_complexity(repo_path),
                "dependencies": build_dependency_graph(repo_path),
                "pr_velocity": estimate_pr_velocity(repo_path),
                "techdebt": calculate_tech_debt_score(repo_path),
                "heatmap": heatmap_to_json(build_commit_heatmap(commit_datetimes)),
            }

            duration_ms = int((time.perf_counter() - start) * 1000)

            _cache_set(cache_key, payload)
            return {"cached": False, "duration_ms": duration_ms, **payload}
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

    This is a first step toward the broader export system. It reuses the same
    analysis + caching as /api/analyze.

    Args:
        req: Analyze request.

    Returns:
        JSON containing the HTML document string.
    """

    analysis = analyze_repo(req)
    payload = {k: v for k, v in analysis.items() if k not in {"cached", "duration_ms"}}
    return {"repo_url": payload.get("repo_url"), "html": build_export_html(payload)}
