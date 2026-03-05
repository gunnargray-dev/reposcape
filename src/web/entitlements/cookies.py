"""Cookie-based entitlements.

Design goals:
- Keep dependencies to stdlib + FastAPI only.
- Provide a consistent way for routes/templates to ask "is this request Pro?".
- Make it easy to swap for a real (webhook-backed) entitlement store later.

Current approach:
- On successful checkout, we set an HttpOnly cookie with a short value.
- Pro is true when the cookie is present AND matches the expected value.

Security note:
This is NOT secure enough for real paid features. It's a placeholder that
unblocks UI gating and allows iterative development without storing users.
"""

from __future__ import annotations

import os

from fastapi import Request

_COOKIE_NAME = "reposcape_pro"
_COOKIE_VALUE = "1"


def pro_cookie_name() -> str:
    """Return the cookie name used for the Pro entitlement."""

    return _COOKIE_NAME


def is_pro(request: Request) -> bool:
    """Return True if the request has access to Pro features.

    Today:
    - Pro access is granted if either:
      - a server-level env var enables Pro globally (REPOSCAPE_PRO)
      - the request includes a Pro cookie set by the billing success redirect

    Args:
        request: Active HTTP request.

    Returns:
        True when the request is entitled to Pro.
    """

    raw = os.getenv("REPOSCAPE_PRO", "").strip().lower()
    env_enabled = raw in {"1", "true", "yes", "on"}
    return env_enabled or request.cookies.get(_COOKIE_NAME) == _COOKIE_VALUE
