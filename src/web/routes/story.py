"""Per-repo story page.

This page is primarily used for social sharing. It renders Open Graph meta tags
and a small UX that points users to the interactive dashboard.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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
    title = f"{repo_ref.slug} · Reposcape"
    subtitle = "Visualize code structure, activity, and complexity"
    og_image = share_card_url(base_url=base_url, title=title, subtitle=subtitle)

    context = {
        "request": request,
        "owner": repo_ref.owner,
        "repo": repo_ref.name,
        "repo_slug": repo_ref.slug,
        "og_title": title,
        "og_description": subtitle,
        "og_image": og_image,
    }
    return templates.TemplateResponse(request, "story.html", context)
