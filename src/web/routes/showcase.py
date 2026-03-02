"""Showcase pages with pre-generated results.

These routes provide a fast way to explore the UI without waiting for analysis.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory=str((Path(__file__).resolve().parents[1] / "templates")))


@router.get("/showcase/nightshift", response_class=HTMLResponse)
def nightshift(request: Request) -> HTMLResponse:
    """Render a pre-generated demo dashboard.

    The demo is intentionally lightweight: it uses the normal dashboard template,
    but passes `demo_mode=True` and a fixed repo URL.
    """

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "repo_url": "https://github.com/gunnargray-dev/nightshift",
            "demo_mode": True,
        },
    )
