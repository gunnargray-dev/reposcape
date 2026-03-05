"""Stripe environment configuration helpers.

Reposcape intentionally keeps Stripe integration optional.

This module centralizes reading Stripe-related environment variables so other
modules can stay small and consistently validated.
"""

from __future__ import annotations

import os


def stripe_enabled() -> bool:
    """Return True when Stripe checkout should be enabled.

    This is a safety valve to avoid accidentally presenting a broken payment UX.

    Environment variable:
        REPOSCAPE_BILLING_ENABLED

    Returns:
        Whether Stripe / billing endpoints should be enabled.
    """

    raw = os.getenv("REPOSCAPE_BILLING_ENABLED", "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def stripe_secret_key() -> str | None:
    """Return Stripe secret key, if configured.

    Environment variable:
        REPOSCAPE_STRIPE_SECRET_KEY

    Returns:
        Secret key string, or None.
    """

    key = os.getenv("REPOSCAPE_STRIPE_SECRET_KEY", "").strip()
    return key or None


def stripe_webhook_secret() -> str | None:
    """Return Stripe webhook signing secret, if configured.

    Environment variable:
        REPOSCAPE_STRIPE_WEBHOOK_SECRET

    Returns:
        Webhook secret string, or None.
    """

    secret = os.getenv("REPOSCAPE_STRIPE_WEBHOOK_SECRET", "").strip()
    return secret or None


def stripe_price_id() -> str | None:
    """Return Stripe price ID for the Pro subscription/product.

    Environment variable:
        REPOSCAPE_STRIPE_PRICE_ID

    Returns:
        Stripe price ID, or None.
    """

    price_id = os.getenv("REPOSCAPE_STRIPE_PRICE_ID", "").strip()
    return price_id or None
