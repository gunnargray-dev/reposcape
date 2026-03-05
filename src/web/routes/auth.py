"""Authentication routes (GitHub OAuth)."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from src.web.auth.github_oauth import (
    authorize_url,
    exchange_code_for_token,
    fetch_viewer_login,
    make_state,
    sign_cookie_value,
)
from src.web.auth.token_store import store_token

router = APIRouter(tags=["auth"])

_COOKIE_STATE = "reposcape_oauth_state"
_COOKIE_GH = "reposcape_gh"


@router.get("/auth/github/login")
def github_login(request: Request) -> RedirectResponse:
    """Start GitHub OAuth login."""

    state = make_state()
    resp = RedirectResponse(authorize_url(state), status_code=302)
    resp.set_cookie(
        _COOKIE_STATE,
        state,
        max_age=600,
        httponly=True,
        samesite="lax",
    )
    return resp


@router.get("/auth/github/callback")
def github_callback(request: Request, code: str | None = None, state: str | None = None) -> RedirectResponse:
    """Complete GitHub OAuth flow and store a signed cookie."""

    stored_state = request.cookies.get(_COOKIE_STATE)
    if not code or not state or not stored_state or stored_state != state:
        return RedirectResponse("/dashboard?auth=error", status_code=302)

    token = exchange_code_for_token(code, state=state)
    if not token.access_token:
        return RedirectResponse("/dashboard?auth=error", status_code=302)

    login = fetch_viewer_login(token.access_token)
    cookie_payload = {
        "v": 2,
        "iat": int(__import__("time").time()),
        "login": login,
    }

    store_token(login, token.access_token, source="github_oauth")

    resp = RedirectResponse("/dashboard?auth=ok", status_code=302)
    resp.delete_cookie(_COOKIE_STATE)
    resp.set_cookie(
        _COOKIE_GH,
        sign_cookie_value(cookie_payload),
        max_age=60 * 60 * 24 * 30,
        httponly=True,
        samesite="lax",
    )
    return resp


@router.post("/auth/logout")
def logout() -> RedirectResponse:
    """Clear auth cookies."""

    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie(_COOKIE_GH)
    resp.delete_cookie(_COOKIE_STATE)
    return resp
