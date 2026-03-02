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
from typing import Any

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


def analyze_repo_url(repo_url: str) -> dict[str, Any]:
    """Analyze a GitHub repo URL and return a JSON-serializable payload.

    Args:
        repo_url: Public repository URL.

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

        duration_ms = int((time.perf_counter() - start) * 1000)

        _cache_set(cache_key, payload)
        return {"cached": False, "duration_ms": duration_ms, **payload}
