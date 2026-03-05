"""Minimal Stripe HTTP client.

Reposcape keeps Stripe optional and avoids a dependency on the official Stripe
SDK. This module implements the narrow subset we need for a hosted checkout
flow: creating a Checkout Session.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


class StripeAPIError(RuntimeError):
    """Raised when Stripe API calls fail."""


def create_checkout_session(
    *,
    secret_key: str,
    price_id: str,
    success_url: str,
    cancel_url: str,
    client_reference_id: str | None = None,
    metadata: dict[str, str] | None = None,
) -> tuple[str, str]:
    """Create a Stripe Checkout Session and return its URL and ID.

    Args:
        secret_key: Stripe secret key.
        price_id: Stripe price ID.
        success_url: URL Stripe redirects to after successful purchase.
        cancel_url: URL Stripe redirects to if user cancels.
        client_reference_id: Optional stable reference ID (e.g., gh:<login>).
        metadata: Optional key/value metadata stored on the session.

    Returns:
        Tuple of (checkout_url, session_id).

    Raises:
        StripeAPIError: If Stripe responds with an error or we fail to decode.
    """

    if not secret_key:
        raise StripeAPIError("missing_secret_key")
    if not price_id:
        raise StripeAPIError("missing_price_id")

    form: dict[str, str] = {
        "mode": "payment",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": "1",
        "allow_promotion_codes": "true",
    }

    if client_reference_id:
        form["client_reference_id"] = client_reference_id

    if metadata:
        for key, value in metadata.items():
            if not key or value is None:
                continue
            form[f"metadata[{key}]"] = str(value)

    body = urllib.parse.urlencode(form).encode("utf-8")
    req = urllib.request.Request(
        url="https://api.stripe.com/v1/checkout/sessions",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise StripeAPIError(f"stripe_http_error: {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise StripeAPIError(f"stripe_network_error: {e.reason}") from e

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        raise StripeAPIError("stripe_invalid_json") from e

    session_id = str(data.get("id") or "")
    url = str(data.get("url") or "")
    if not session_id or not url:
        raise StripeAPIError("stripe_missing_fields")
    return url, session_id
