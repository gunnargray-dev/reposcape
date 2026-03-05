"""Restore Pro access from persisted entitlements.

This is a temporary bridge until Reposcape has an authenticated user identity
(GitHub OAuth).

Flow:
- Users enter their email on a restore form.
- If the email has an active Pro entitlement stored by Stripe webhooks, the
  server sets the Pro cookie and redirects to /dashboard.

Security note:
This is not secure enough for real monetization. It's a development aid to
validate the end-to-end webhook -> persistence -> gating pipeline.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.web.entitlements.cookies import pro_cookie_name
from src.web.entitlements.store import get_entitlement, normalize_subject

router = APIRouter(tags=["billing"])


def _base_html(body: str) -> str:
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\" />"
        "<title>Reposcape Pro — Restore</title>"
        "<style>body{font-family:ui-sans-serif,system-ui;max-width:720px;margin:40px auto;"
        "padding:0 16px;line-height:1.5}a{color:#2563eb}input{padding:10px 12px;"
        "border-radius:10px;border:1px solid #ddd;width:min(420px,100%)}"
        "button{padding:10px 14px;border-radius:10px;border:0;background:#2563eb;"
        "color:white;font-weight:700;cursor:pointer}</style></head><body>"
        + body
        + "</body></html>"
    )


@router.get("/billing/restore", response_class=HTMLResponse)
def restore_form(request: Request) -> HTMLResponse:
    """Render a minimal restore form."""

    html = _base_html(
        "<h1>Restore Pro</h1>"
        "<p>Enter the email used during checkout.</p>"
        "<form method=\"post\" action=\"/billing/restore\">"
        "<p><input name=\"email\" type=\"email\" placeholder=\"you@example.com\" required /></p>"
        "<p><button type=\"submit\">Restore</button></p>"
        "</form>"
        "<p class=\"muted\"><a href=\"/dashboard\">Back to dashboard</a></p>"
    )
    return HTMLResponse(content=html)


@router.post("/billing/restore")
async def restore_submit(request: Request):
    """Attempt to restore Pro cookie for a known entitled email."""

    form = await request.form()
    email = normalize_subject(str(form.get("email") or ""))
    if not email:
        return HTMLResponse(content=_base_html("<h1>Missing email</h1><p>Please try again.</p>"), status_code=400)

    ent = get_entitlement(email)
    if not ent or not ent.active or ent.plan != "pro":
        return HTMLResponse(
            content=_base_html(
                "<h1>No Pro entitlement found</h1>"
                "<p>We couldn't find an active Pro entitlement for that email.</p>"
                "<p><a href=\"/billing/restore\">Try again</a></p>"
            ),
            status_code=404,
        )

    response = RedirectResponse(url=f"/dashboard?email={email}", status_code=303)
    response.set_cookie(
        key=pro_cookie_name(),
        value="1",
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )
    return response
