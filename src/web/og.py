"""Open Graph / social metadata helpers.

We keep this tiny and dependency-free so it can be reused across server-rendered
pages.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import quote


_RE_OWNER_REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


@dataclass(frozen=True)
class RepoRef:
    """A GitHub repo reference like "owner/name"."""

    owner: str
    name: str

    @property
    def slug(self) -> str:
        """Return "owner/name"."""

        return f"{self.owner}/{self.name}"


def parse_repo_ref(raw: str) -> RepoRef:
    """Parse a repo ref.

    Args:
        raw: String like "owner/name".

    Returns:
        Parsed RepoRef.

    Raises:
        ValueError: If raw is not a valid repo ref.
    """

    cleaned = (raw or "").strip().strip("/")
    if not _RE_OWNER_REPO.match(cleaned):
        raise ValueError(f"Invalid repo ref: {raw!r}")
    owner, name = cleaned.split("/", 1)
    return RepoRef(owner=owner, name=name)


def share_card_url(
    *,
    base_url: str,
    title: str,
    subtitle: str,
) -> str:
    """Build absolute URL to the share-card endpoint.

    Args:
        base_url: Absolute base URL like "https://example.com".
        title: Share card title.
        subtitle: Share card subtitle.

    Returns:
        Absolute URL to /share/card.png.
    """

    base = base_url.rstrip("/")
    q_title = quote((title or "").strip(), safe="")
    q_sub = quote((subtitle or "").strip(), safe="")
    return f"{base}/share/card.png?title={q_title}&subtitle={q_sub}"
