"""Server-rendered pages."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["pages"])

_templates_dir = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(_templates_dir))


@router.get("/", response_class=HTMLResponse)
def landing(request: Request) -> HTMLResponse:
    """Landing page with repo URL input."""

    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    """Dashboard placeholder; JS triggers analysis and renders a treemap."""

    return templates.TemplateResponse("dashboard.html", {"request": request})
