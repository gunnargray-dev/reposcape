"""Pro / paid feature gating utilities.

This module centralizes the definition of "Pro" behavior.

For now, Pro is a stub: the server reads an env var to decide whether Pro
features should be enabled.

Later sessions will integrate Stripe and real entitlements.
"""

from __future__ import annotations

import os


def pro_enabled() -> bool:
    """Return True if Pro features are enabled.

    Pro is toggled via the `REPOSCAPE_PRO` environment variable.

    Accepted truthy values: 1, true, yes, on (case-insensitive).

    Returns:
        Whether Pro features should be enabled.
    """

    raw = os.getenv("REPOSCAPE_PRO", "").strip().lower()
    return raw in {"1", "true", "yes", "on"}
