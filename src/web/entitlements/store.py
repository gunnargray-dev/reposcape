"""Persistent entitlements.

This module provides a tiny, stdlib-only persistence layer for paid feature
entitlements.

Design goals:
- Avoid introducing a DB dependency (SQLite is stdlib).
- Keep schema tiny and easy to migrate later.
- Provide a seam for a future identity system (GitHub OAuth, email, etc.).

Current model:
- Entitlements are keyed by a stable string "subject".
- For now, the only supported subject type is an email address.

Stripe webhooks:
- `checkout.session.completed` typically includes a customer email.
- We store that email as the subject and mark it Pro.

Limitations:
- This is not meant to be a full billing system.
- Email-based matching is best-effort; a future session can shift to Stripe
  customer IDs and authenticated users.
"""

from __future__ import annotations

import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Entitlement:
    """Stored entitlement for a subject."""

    subject: str
    plan: str
    active: bool
    granted_at: int
    source: str


def _db_path() -> Path:
    """Return path to the SQLite DB file used for entitlement storage."""

    raw = os.environ.get("REPOSCAPE_ENTITLEMENTS_DB")
    if raw:
        return Path(raw)
    return Path(".reposcape") / "entitlements.sqlite3"


def _connect(db_path: Path) -> sqlite3.Connection:
    """Return a sqlite3 connection with best-effort safe defaults."""

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_entitlements_db(db_path: Path | None = None) -> None:
    """Create the entitlements table if it does not exist."""

    path = db_path or _db_path()
    with _connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS entitlements (
              subject TEXT PRIMARY KEY,
              plan TEXT NOT NULL,
              active INTEGER NOT NULL,
              granted_at INTEGER NOT NULL,
              source TEXT NOT NULL
            )
            """
        )
        conn.commit()


def normalize_subject(value: str | None) -> str | None:
    """Normalize an entitlement subject string.

    Args:
        value: Raw subject (email).

    Returns:
        Lowercased stripped subject, or None if empty.
    """

    if not value:
        return None
    s = str(value).strip().lower()
    return s or None


def grant_pro(subject: str, *, source: str) -> None:
    """Grant Pro entitlement to the given subject."""

    norm = normalize_subject(subject)
    if not norm:
        raise ValueError("subject is required")

    init_entitlements_db()
    path = _db_path()
    now = int(time.time())
    with _connect(path) as conn:
        conn.execute(
            """
            INSERT INTO entitlements(subject, plan, active, granted_at, source)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(subject) DO UPDATE SET
              plan=excluded.plan,
              active=excluded.active,
              granted_at=excluded.granted_at,
              source=excluded.source
            """,
            (norm, "pro", 1, now, source),
        )
        conn.commit()


def get_entitlement(subject: str) -> Entitlement | None:
    """Return an entitlement for a subject if stored."""

    norm = normalize_subject(subject)
    if not norm:
        return None

    init_entitlements_db()
    path = _db_path()
    with _connect(path) as conn:
        cur = conn.execute(
            "SELECT subject, plan, active, granted_at, source FROM entitlements WHERE subject=?",
            (norm,),
        )
        row = cur.fetchone()

    if not row:
        return None

    return Entitlement(
        subject=str(row[0]),
        plan=str(row[1]),
        active=bool(int(row[2])),
        granted_at=int(row[3]),
        source=str(row[4]),
    )
