"""Shared analysis entrypoint.

This module contains repo analysis logic that is used by both:
- the web API (`src.web.routes.api`)
- the CLI (`src.cli.main`)

It intentionally contains no FastAPI/Pydantic dependencies.
"""

from __future__ import annotations

import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from src.clone import clone_repo, parse_git_log
from src.commit_quality import analyze_commit_quality
from src.complexity import analyze_repo_complexity
from src.contributors import analyze_contributors
from src.dependencies import build_dependency_graph
from src.heatmap import build_commit_heatmap, to_json as heatmap_to_json
from src.history import get_repo_history_dir, write_snapshot
from src.languages import analyze_languages
from src.pr_velocity import estimate_pr_velocity
from src.techdebt import calculate_tech_debt_score
from src.timeline import build_commit_timeline
from src.treemap import build_treemap, treemap_to_dict

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
        List of commit datetimes (newest first).
    """

    commits = parse_git_log(repo_path)
    dts: list[datetime] = []
    for commit in commits:
        dts.append(datetime.fromisoformat(str(commit.get("date"))))
    return dts


def _parse_github_owner_repo(repo_url: str) -> tuple[str, str]:
    """Parse a GitHub repo URL into (owner, name).

    Args:
        repo_url: Repository URL.

    Returns:
        Tuple of (owner, repo_name).

    Raises:
        ValueError: If the URL does not look like a GitHub repo URL.
    """

    parsed = urlparse(repo_url)
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise ValueError(f"Invalid GitHub repo URL: {repo_url}")
    return parts[0], parts[1]


def analyze_repo_url(
    repo_url: str,
    *,
    snapshot_base_dir: Path | None = None,
) -> dict[str, Any]:
    """Analyze a GitHub repo URL and return a JSON-serializable payload.

    Args:
        repo_url: Public repository URL.
        snapshot_base_dir: Optional directory for storing a point-in-time snapshot
            JSON file (for historical tracking). If provided, a snapshot is
            written for today's UTC date.

    Returns:
        Analysis payload suitable for JSON serialization.

    Raises:
        RuntimeError: If cloning or analysis fails.
    """

    cache_key = str(repo_url)
    cached = _cache_get(cache_key)
    if cached is not None:
        return {"cached": True, "duration_ms": 0, **cached}

    start = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="reposcape-") as tmpdir:
        repo_path = clone_repo(str(repo_url), tmpdir)
        commit_datetimes = _load_commit_datetimes(repo_path)

        payload: dict[str, Any] = {
            "repo_url": str(repo_url),
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

        if snapshot_base_dir is not None:
            owner, name = _parse_github_owner_repo(str(repo_url))
            history_dir = get_repo_history_dir(owner, name, snapshot_base_dir)
            write_snapshot(history_dir, datetime.utcnow().date(), payload)

        duration_ms = int((time.perf_counter() - start) * 1000)

        _cache_set(cache_key, payload)
        return {"cached": False, "duration_ms": duration_ms, **payload}
