"""Email-based entitlement checks.

This module extends the placeholder cookie entitlement mechanism by persisting
Stripe webhook grants keyed by email.

How it works:
- The billing success redirect sets a cookie so the current browser session
  immediately becomes Pro.
- The Stripe webhook endpoint (when configured) stores a Pro entitlement for
  the checkout customer's email.
- Users can later restore Pro in a new browser by visiting:

    /billing/restore?email=<email>

This is a deliberate interim step before a real identity system (GitHub OAuth).
"""

from __future__ import annotations

from fastapi import Request

from src.web.entitlements.cookies import is_pro as is_pro_cookie
from src.web.entitlements.store import get_entitlement, normalize_subject


def is_pro(request: Request) -> bool:
    """Return True if the request is entitled to Pro.

    Priority:
    1) Server env override (handled inside cookie helper).
    2) Browser Pro cookie.
    3) Best-effort email entitlement lookup via `?email=` query parameter.

    Args:
        request: Active HTTP request.

    Returns:
        True when the request is entitled to Pro.
    """

    if is_pro_cookie(request):
        return True

    email = normalize_subject(request.query_params.get("email"))
    if not email:
        return False

    ent = get_entitlement(email)
    return bool(ent and ent.active and ent.plan == "pro")
