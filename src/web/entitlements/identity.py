"""Identity-aware entitlement checks.

This module bridges Reposcape's entitlement system to an authenticated identity.

Current identity sources:
- GitHub OAuth cookie (preferred when present).
- Email query parameter fallback (legacy; best-effort).

Entitlement store:
- Uses `src.web.entitlements.store` where the subject is a string key.
- For GitHub sessions we store entitlements under subject `gh:<login>`.
- For email fallback, subject is the normalized email.

This design intentionally keeps the persistence layer unchanged while we evolve
identity.
"""

from __future__ import annotations

from fastapi import Request

from src.web.auth.session import get_user_session
from src.web.entitlements.cookies import is_pro as is_pro_cookie
from src.web.entitlements.store import get_entitlement, normalize_subject


def subject_for_request(request: Request) -> str | None:
    """Return the entitlement subject key for the current request."""

    sess = get_user_session(request)
    if sess:
        return f"gh:{sess.login.lower()}"

    email = normalize_subject(request.query_params.get("email"))
    return email


def is_pro(request: Request) -> bool:
    """Return True if request is entitled to Pro."""

    if is_pro_cookie(request):
        return True

    subject = subject_for_request(request)
    if not subject:
        return False

    ent = get_entitlement(subject)
    return bool(ent and ent.active and ent.plan == "pro")
