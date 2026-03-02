"""GitHub metadata helpers.

Reposcape core analysis is intentionally lightweight and primarily operates on a
cloned repository. Some UI elements benefit from GitHub-level metadata
(stargazers, updated timestamps, etc.).

This module provides a small, standard-library-only helper to fetch that
metadata from the public GitHub REST API.

The helper is best-effort:
- If rate-limited or offline, it returns a minimal payload with an error.
- Callers should treat all returned fields as optional.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RepoMetadata:
    """Selected GitHub repository metadata."""

    owner: str
    name: str
    stargazers_count: int | None = None
    forks_count: int | None = None
    open_issues_count: int | None = None
    watchers_count: int | None = None
    primary_language: str | None = None
    updated_at: datetime | None = None
    html_url: str | None = None

    error: str | None = None


def fetch_repo_metadata(owner: str, repo: str, *, token: str | None = None) -> RepoMetadata:
    """Fetch basic metadata for a GitHub repository.

    Args:
        owner: Repository owner.
        repo: Repository name.
        token: Optional GitHub token to increase rate limits. If not provided,
            this checks the `GITHUB_TOKEN` environment variable.

    Returns:
        RepoMetadata. If a network/auth error happens, `error` is populated and
        other fields may be None.
    """

    token = (token or os.environ.get("GITHUB_TOKEN") or "").strip() or None

    url = f"https://api.github.com/repos/{owner}/{repo}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return _parse_repo_metadata(owner, repo, payload)
    except urllib.error.HTTPError as e:
        msg = f"HTTP {e.code} {getattr(e, 'reason', '')}".strip()
        return RepoMetadata(owner=owner, name=repo, error=msg)
    except urllib.error.URLError as e:
        return RepoMetadata(owner=owner, name=repo, error=str(e.reason))
    except Exception as e:  # pragma: no cover
        return RepoMetadata(owner=owner, name=repo, error=str(e))


def _parse_repo_metadata(owner: str, repo: str, payload: dict[str, Any]) -> RepoMetadata:
    """Parse GitHub repo JSON into RepoMetadata."""

    updated_at = None
    raw_updated = (payload.get("updated_at") or "").strip()
    if raw_updated:
        try:
            updated_at = datetime.fromisoformat(raw_updated.replace("Z", "+00:00"))
        except ValueError:
            updated_at = None

    return RepoMetadata(
        owner=owner,
        name=repo,
        stargazers_count=_as_int(payload.get("stargazers_count")),
        forks_count=_as_int(payload.get("forks_count")),
        open_issues_count=_as_int(payload.get("open_issues_count")),
        watchers_count=_as_int(payload.get("watchers_count")),
        primary_language=_as_str(payload.get("language")),
        updated_at=updated_at,
        html_url=_as_str(payload.get("html_url")),
        error=None,
    )


def _as_int(value: Any) -> int | None:
    """Return value as int, or None."""

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_str(value: Any) -> str | None:
    """Return value as string, or None."""

    if value is None:
        return None

    s = str(value).strip()
    return s or None
