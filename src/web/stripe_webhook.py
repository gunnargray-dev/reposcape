"""Stripe webhook verification helpers.

This module implements Stripe's webhook signing verification using stdlib only.

We intentionally keep this separate from route handlers so it can be unit tested
in isolation.

Signature format (Stripe-Signature header):
    t=timestamp,v1=hex_signature[,v0=...]

The signature is:
    HMAC_SHA256(secret, f"{t}.{payload}")
"""

from __future__ import annotations

import hmac
import time
from dataclasses import dataclass
from hashlib import sha256


class StripeWebhookError(RuntimeError):
    """Raised when webhook verification fails."""


@dataclass(frozen=True)
class StripeSignature:
    """Parsed Stripe-Signature header."""

    timestamp: int
    v1_signatures: tuple[str, ...]


def parse_stripe_signature_header(header: str) -> StripeSignature:
    """Parse a Stripe-Signature header value.

    Args:
        header: Raw header value.

    Returns:
        Parsed signature data.

    Raises:
        StripeWebhookError: If the header is missing required fields.
    """

    parts: dict[str, list[str]] = {}
    for item in (header or "").split(","):
        if "=" not in item:
            continue
        k, v = item.split("=", 1)
        parts.setdefault(k.strip(), []).append(v.strip())

    if "t" not in parts:
        raise StripeWebhookError("missing_timestamp")
    if "v1" not in parts:
        raise StripeWebhookError("missing_v1_signature")

    try:
        ts = int(parts["t"][0])
    except ValueError as e:
        raise StripeWebhookError("invalid_timestamp") from e

    v1 = tuple(s for s in parts["v1"] if s)
    if not v1:
        raise StripeWebhookError("missing_v1_signature")
    return StripeSignature(timestamp=ts, v1_signatures=v1)


def verify_stripe_webhook(
    *,
    payload: bytes,
    signature_header: str,
    webhook_secret: str,
    tolerance_seconds: int = 300,
    now: int | None = None,
) -> StripeSignature:
    """Verify a Stripe webhook signature.

    Args:
        payload: Raw request body bytes.
        signature_header: Stripe-Signature header value.
        webhook_secret: Stripe webhook signing secret.
        tolerance_seconds: Allowed timestamp drift.
        now: Current unix timestamp (override for tests).

    Returns:
        Parsed signature.

    Raises:
        StripeWebhookError: If signature invalid or timestamp too old.
    """

    if not webhook_secret:
        raise StripeWebhookError("missing_webhook_secret")

    parsed = parse_stripe_signature_header(signature_header)

    current = int(time.time()) if now is None else int(now)
    if abs(current - parsed.timestamp) > tolerance_seconds:
        raise StripeWebhookError("timestamp_out_of_tolerance")

    signed_payload = str(parsed.timestamp).encode("utf-8") + b"." + payload
    expected = hmac.new(
        webhook_secret.encode("utf-8"),
        msg=signed_payload,
        digestmod=sha256,
    ).hexdigest()

    if not any(hmac.compare_digest(expected, sig) for sig in parsed.v1_signatures):
        raise StripeWebhookError("signature_mismatch")

    return parsed
