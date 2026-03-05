"""Signed auth session cookie helpers."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request

from src.web.auth.github_oauth import verify_cookie_value
from src.web.auth.token_store import get_token

_COOKIE_GH = "reposcape_gh"
_MAX_AGE_SECONDS = 60 * 60 * 24 * 30


@dataclass(frozen=True)
class UserSession:
    """Authenticated user session."""

    login: str
    access_token: str


def get_user_session(request: Request) -> UserSession | None:
    """Return the authenticated user session if present."""

    raw = request.cookies.get(_COOKIE_GH)
    if not raw:
        return None

    data = verify_cookie_value(raw, max_age_seconds=_MAX_AGE_SECONDS)
    if not data:
        return None

    login = str(data.get("login") or "").strip()
    token = get_token(login)
    if not token:
        return None

    return UserSession(login=login, access_token=token.token)
