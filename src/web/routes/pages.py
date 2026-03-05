"""Server-rendered pages."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.web.entitlements.identity import is_pro

router = APIRouter(tags=["pages"])

_templates_dir = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(_templates_dir))


@router.get("/", response_class=HTMLResponse)
def landing(request: Request) -> HTMLResponse:
    """Landing page with repo URL input."""
    return templates.TemplateResponse(request, "index.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    """Dashboard placeholder; JS triggers analysis and renders a treemap."""

    context = {
        "request": request,
        "snapshots_enabled": bool(request.app.state.get("snapshots_enabled", False)),
        "pro_enabled": is_pro(request),
    }
    return templates.TemplateResponse(request, "dashboard.html", context)


@router.get("/compare", response_class=HTMLResponse)
def compare(request: Request) -> HTMLResponse:
    """Comparison mode page (two repos side by side)."""
    return templates.TemplateResponse(request, "compare.html", {"request": request})


@router.get("/share", response_class=HTMLResponse)
def share_preview(request: Request) -> HTMLResponse:
    """Preview the default share card image."""
    return templates.TemplateResponse(request, "share_preview.html", {"request": request})
