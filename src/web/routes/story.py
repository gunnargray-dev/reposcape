"""Per-repo story page.

This page is primarily used for social sharing. It renders Open Graph meta tags
and a small UX that points users to the interactive dashboard.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.github_meta import fetch_repo_metadata
from src.web.og import parse_repo_ref, share_card_url

router = APIRouter(tags=["story"])

_templates_dir = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(_templates_dir))


@router.get("/r/{owner}/{repo}", response_class=HTMLResponse)
def story(request: Request, owner: str, repo: str) -> HTMLResponse:
    """Render a repo story landing page with Open Graph metadata."""

    repo_ref = parse_repo_ref(f"{owner}/{repo}")

    # request.base_url already includes scheme/host.
    base_url = str(request.base_url).rstrip("/")

    meta = fetch_repo_metadata(repo_ref.owner, repo_ref.name)

    title = f"{repo_ref.slug} · Reposcape"
    subtitle_parts: list[str] = []
    if meta.stargazers_count is not None:
        subtitle_parts.append(f"{meta.stargazers_count:,} stars")
    if meta.primary_language:
        subtitle_parts.append(meta.primary_language)
    if meta.updated_at is not None:
        subtitle_parts.append(f"Updated {meta.updated_at.date().isoformat()}")

    subtitle = " · ".join(subtitle_parts) or "Visualize code structure, activity, and complexity"
    og_image = share_card_url(base_url=base_url, title=title, subtitle=subtitle)

    context = {
        "request": request,
        "owner": repo_ref.owner,
        "repo": repo_ref.name,
        "repo_slug": repo_ref.slug,
        "og_title": title,
        "og_description": subtitle,
        "og_image": og_image,
        "stars": meta.stargazers_count,
        "language": meta.primary_language,
        "updated_at": meta.updated_at,
        "github_url": meta.html_url,
        "meta_error": meta.error,
    }
    return templates.TemplateResponse(request, "story.html", context)
