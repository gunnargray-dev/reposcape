"""FastAPI application factory and configuration."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from web.routes import api, pages, share


def create_app() -> FastAPI:
    """Create and configure the FastAPI app.

    Returns:
        Configured FastAPI app.
    """

    app = FastAPI(title="Reposcape", version="0.1.0")

    app.include_router(api.router)
    app.include_router(pages.router)
    app.include_router(share.router)

    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app
