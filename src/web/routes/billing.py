"""Billing / checkout routes.

This module wires a minimal paid checkout flow using Stripe Hosted Checkout.

Design goals:
- Keep the code stdlib-only (no Stripe dependency).
- Provide stable URLs that the UI can link to.
- Keep endpoints small and easy to replace with a fuller billing subsystem.

Endpoints:
- POST /api/billing/checkout: returns a Stripe-hosted checkout_url.
- POST /api/billing/webhook: verifies webhook signature and grants Pro cookie.
- GET /billing/success: fallback success page (and manual entitlement cookie).
- GET /billing/cancel: minimal cancel page.

Notes:
- Cookie-based entitlements are still a placeholder; webhooks are the bridge to
  future persistent entitlements.
"""

from __future__ import annotations

import json
from urllib.parse import urljoin

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from src.web.entitlements.cookies import pro_cookie_name
from src.web.stripe_client import StripeAPIError, create_checkout_session
from src.web.stripe_env import (
    stripe_enabled,
    stripe_price_id,
    stripe_secret_key,
    stripe_webhook_secret,
)
from src.web.stripe_webhook import StripeWebhookError, verify_stripe_webhook

router = APIRouter(tags=["billing"])


def _base_url(request: Request) -> str:
    """Return a best-effort base URL for building absolute links."""

    scheme = request.url.scheme
    host = request.headers.get("host") or "localhost"
    return f"{scheme}://{host}/"


def _set_pro_cookie(response: RedirectResponse, request: Request) -> None:
    """Set the Pro entitlement cookie on the response."""

    response.set_cookie(
        key=pro_cookie_name(),
        value="1",
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )


@router.post("/api/billing/checkout")
def api_checkout(request: Request) -> JSONResponse:
    """Create a Stripe Checkout Session and return a redirect URL."""

    if not stripe_enabled():
        return JSONResponse(
            status_code=501,
            content={
                "error": "billing_not_configured",
                "message": "Billing is not configured on this deployment.",
            },
        )

    secret = stripe_secret_key()
    price_id = stripe_price_id()
    if not secret or not price_id:
        return JSONResponse(
            status_code=500,
            content={
                "error": "billing_missing_env",
                "message": "Billing is enabled but missing Stripe keys.",
            },
        )

    success_url = urljoin(_base_url(request), "billing/success")
    cancel_url = urljoin(_base_url(request), "billing/cancel")

    try:
        checkout_url, _session_id = create_checkout_session(
            secret_key=secret,
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )
    except StripeAPIError as e:
        return JSONResponse(
            status_code=502,
            content={"error": "stripe_error", "message": str(e)},
        )

    return JSONResponse(content={"checkout_url": checkout_url})


@router.post("/api/billing/webhook")
async def stripe_webhook(request: Request) -> JSONResponse:
    """Stripe webhook endpoint.

    Today this endpoint sets a Pro cookie when it receives a valid
    `checkout.session.completed` event.

    Returns:
        Minimal JSON response for Stripe.
    """

    secret = stripe_webhook_secret()
    if not secret:
        return JSONResponse(
            status_code=501,
            content={
                "error": "webhook_not_configured",
                "message": "Webhook secret is not configured.",
            },
        )

    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    try:
        verify_stripe_webhook(payload=payload, signature_header=sig, webhook_secret=secret)
    except StripeWebhookError as e:
        return JSONResponse(status_code=400, content={"error": "invalid_signature", "message": str(e)})

    try:
        event = json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "invalid_json"})

    event_type = str(event.get("type") or "")
    if event_type != "checkout.session.completed":
        return JSONResponse(content={"received": True})

    response = JSONResponse(content={"received": True})
    response.set_cookie(
        key=pro_cookie_name(),
        value="1",
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )
    return response


@router.get("/billing/success")
def billing_success(request: Request) -> RedirectResponse:
    """Checkout success redirect.

    This endpoint is used as Stripe success_url and provides a fallback that
    grants the Pro cookie even if webhooks are not configured.
    """

    response = RedirectResponse(url="/dashboard", status_code=303)
    _set_pro_cookie(response, request)
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
