"""Web JSON API endpoints.

Note: core analysis logic lives in `src.analyze.analyze_repo_url` so the web API
and CLI can share implementation.
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from src.analyze import analyze_repo_url
from src.compare import build_comparison_payload
from src.history import build_snapshot_index, get_repo_history_dir, load_snapshot
from src.web.demo import load_demo_payload
from src.web.export import build_export_html

_GITHUB_API = "https://api.github.com"

router = APIRouter(prefix="/api", tags=["api"])


class AnalyzeRequest(BaseModel):
    """Request payload for analyzing a Git repository."""

    repo_url: HttpUrl


class CompareRequest(BaseModel):
    """Request payload for comparing two Git repositories."""

    repo_a_url: HttpUrl
    repo_b_url: HttpUrl


class SnapshotIndexRequest(BaseModel):
    """Request payload for listing available snapshots."""

    repo_url: HttpUrl


class SnapshotGetRequest(BaseModel):
    """Request payload for retrieving a snapshot payload."""

    repo_url: HttpUrl
    as_of: date


def _parse_github_owner_repo(repo_url: str) -> tuple[str, str]:
    """Parse a GitHub repo URL into (owner, name)."""

    parts = [p for p in str(repo_url).split("/") if p]
    # expected: https://github.com/<owner>/<repo>
    if "github.com" in parts:
        idx = parts.index("github.com")
        parts = parts[idx + 1 :]
    if len(parts) < 2:
        raise ValueError(f"Invalid GitHub repo URL: {repo_url}")
    return parts[0], parts[1]


def _get_snapshot_base_dir() -> Path | None:
    """Return configured snapshot base dir for the web server."""

    raw = os.environ.get("REPOSCAPE_SNAPSHOT_DIR")
    if not raw:
        return None
    return Path(raw)

def _best_effort_get_latest_release_asset_url(
    owner: str, repo: str, asset_name: str
) -> str | None:
    """Return a browser_download_url for an asset on the latest GitHub release.

    This is a best-effort helper for wiring the UI to release-produced assets.
    It intentionally avoids adding new dependencies.

    Args:
        owner: GitHub repo owner.
        repo: GitHub repo name.
        asset_name: Exact asset filename to search for.

    Returns:
        Direct browser download URL, if found.
    """

    try:
        import json
        import urllib.request

        req = urllib.request.Request(
            f"{_GITHUB_API}/repos/{owner}/{repo}/releases/latest",
            headers={"Accept": "application/vnd.github+json", "User-Agent": "reposcape"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            payload = json.loads(resp.read().decode("utf-8"))

        for asset in payload.get("assets", []):
            if asset.get("name") == asset_name:
                return asset.get("browser_download_url")
        return None
    except Exception:
        return None



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


@router.post("/snapshots/index")
def snapshots_index(req: SnapshotIndexRequest) -> dict[str, Any]:
    """List available snapshot files for a repo.

    Requires REPOSCAPE_SNAPSHOT_DIR to be configured.

    Args:
        req: Snapshot index request.

    Returns:
        Dict containing repo_url and an index list.
    """

    base = _get_snapshot_base_dir()
    if base is None:
        raise HTTPException(
            status_code=422,
            detail="Snapshots not configured (set REPOSCAPE_SNAPSHOT_DIR)",
        )

    try:
        owner, name = _parse_github_owner_repo(str(req.repo_url))
        history_dir = get_repo_history_dir(owner, name, base)
        paths = list(history_dir.glob("*.json")) if history_dir.exists() else []
        return {"repo_url": str(req.repo_url), "snapshots": build_snapshot_index(paths)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/snapshots/get")
def snapshots_get(req: SnapshotGetRequest) -> dict[str, Any]:
    """Load a single snapshot JSON payload.

    Requires REPOSCAPE_SNAPSHOT_DIR to be configured.

    Args:
        req: Snapshot payload request.

    Returns:
        Snapshot JSON.
    """

    base = _get_snapshot_base_dir()
    if base is None:
        raise HTTPException(
            status_code=422,
            detail="Snapshots not configured (set REPOSCAPE_SNAPSHOT_DIR)",
        )

    try:
        owner, name = _parse_github_owner_repo(str(req.repo_url))
        history_dir = get_repo_history_dir(owner, name, base)
        path = history_dir / f"{req.as_of.isoformat()}.json"
        if not path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Snapshot not found: {req.as_of.isoformat()}",
            )
        return load_snapshot(path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/releases/latest")
def latest_release_info(owner: str, repo: str) -> dict[str, Any]:
    """Return best-effort info about the latest GitHub release assets.

    This endpoint exists to support UI features like "Download snapshots".

    Args:
        owner: GitHub owner.
        repo: GitHub repo name.

    Returns:
        Dict containing owner/repo and known asset download URLs.
    """

    if not owner or not repo:
        raise HTTPException(status_code=422, detail="owner and repo are required")

    snapshots_url = _best_effort_get_latest_release_asset_url(
        owner,
        repo,
        "reposcape-snapshots.zip",
    )

    return {
        "owner": owner,
        "repo": repo,
        "assets": {"reposcape-snapshots.zip": snapshots_url},
    }
