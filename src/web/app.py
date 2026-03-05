"""FastAPI application factory and configuration."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.web.routes import api, billing, billing_restore, pages, pdf, share, showcase, story
from src.web.pro import pro_enabled


def create_app() -> FastAPI:
    """Create and configure the FastAPI app.

    Returns:
        Configured FastAPI app.
    """

    app = FastAPI(title="Reposcape", version="0.1.0")

    app.state["snapshots_enabled"] = bool(os.environ.get("REPOSCAPE_SNAPSHOT_DIR"))
    app.state["pro_enabled"] = pro_enabled()

    app.include_router(api.router)
    app.include_router(billing.router)
    app.include_router(billing_restore.router)
    app.include_router(pages.router)
    app.include_router(pdf.router)
    app.include_router(share.router)
    app.include_router(showcase.router)
    app.include_router(story.router)

    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app
