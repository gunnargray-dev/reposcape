"""Billing / checkout routes.

This module intentionally implements a minimal stub of a paid checkout flow.

Design goals:
- Keep the code stdlib-only (no Stripe dependency) until a later session.
- Provide stable URLs that the UI can link to now.
- Allow future Stripe wiring by swapping the checkout URL creation.

Endpoints:
- POST /api/billing/checkout: returns a checkout_url to redirect the user to.
- GET /billing/success: sets a temporary entitlement cookie and redirects.
- GET /billing/cancel: returns a minimal cancel page.

Notes:
- We do NOT persist entitlements yet. That comes with real Stripe webhooks.
"""

from __future__ import annotations

from urllib.parse import urljoin

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from src.web.entitlements.cookies import pro_cookie_name
from src.web.stripe_env import stripe_enabled

router = APIRouter(tags=["billing"])


def _base_url(request: Request) -> str:
    """Return the best-effort base URL for building absolute links.

    Args:
        request: Active request.

    Returns:
        Absolute base URL (scheme + host), ending in '/'.
    """

    # We avoid relying on request.base_url because it can include a path prefix.
    scheme = request.url.scheme
    host = request.headers.get("host") or "localhost"
    return f"{scheme}://{host}/"


@router.post("/api/billing/checkout")
def create_checkout_session(request: Request) -> JSONResponse:
    """Create a checkout session and return a redirect URL.

    Current behavior is a stub: it returns a link to an internal success page.

    Later sessions will:
    - create a Stripe Checkout Session
    - return Stripe's hosted checkout URL

    Args:
        request: Active request.

    Returns:
        JSON payload containing checkout_url.
    """

    if not stripe_enabled():
        return JSONResponse(
            status_code=501,
            content={
                "error": "billing_not_configured",
                "message": "Billing is not configured on this deployment.",
            },
        )

    checkout_url = urljoin(_base_url(request), "billing/success")
    return JSONResponse(content={"checkout_url": checkout_url})


@router.get("/billing/success")
def billing_success(request: Request) -> RedirectResponse:
    """Checkout success redirect.

    This endpoint sets a temporary cookie granting Pro features.

    Returns:
        Redirect response back to the dashboard.
    """

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key=pro_cookie_name(),
        value="1",
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )
    return response


@router.get("/billing/cancel", response_class=HTMLResponse)
def billing_cancel(request: Request) -> HTMLResponse:
    """Checkout cancel page."""

    html = """<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\" />
<title>Reposcape Pro — Canceled</title>
<style>body{font-family:ui-sans-serif,system-ui;max-width:720px;margin:40px auto;padding:0 16px;line-height:1.5}a{color:#2563eb}</style>
</head><body>
<h1>Upgrade canceled</h1>
<p>No changes were made.</p>
<p><a href=\"/dashboard\">Return to dashboard</a></p>
</body></html>"""
    return HTMLResponse(content=html)
