"""GitHub OAuth token persistence (server-side).

This module stores OAuth access tokens in a small SQLite database so the token
is not embedded in a client-side cookie.

Design goals:
- stdlib only (sqlite3)
- keyed by GitHub login (lowercased)
- minimal surface area

This is intentionally simple and can be replaced by a proper identity system
later.
"""

from __future__ import annotations

import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StoredToken:
    """Stored GitHub access token."""

    login: str
    token: str
    stored_at: int
    source: str


def _db_path() -> Path:
    """Return path to SQLite DB used for GitHub token storage."""

    raw = os.environ.get("REPOSCAPE_TOKENS_DB")
    if raw:
        return Path(raw)
    return Path(".reposcape") / "tokens.sqlite3"


def _connect(db_path: Path) -> sqlite3.Connection:
    """Return sqlite3 connection with best-effort safe defaults."""

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_tokens_db(db_path: Path | None = None) -> None:
    """Create the tokens table if it does not exist."""

    path = db_path or _db_path()
    with _connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tokens (
              login TEXT PRIMARY KEY,
              token TEXT NOT NULL,
              stored_at INTEGER NOT NULL,
              source TEXT NOT NULL
            )
            """
        )
        conn.commit()


def normalize_login(login: str | None) -> str | None:
    """Normalize a GitHub login string."""

    if not login:
        return None
    s = str(login).strip().lower()
    return s or None


def store_token(login: str, token: str, *, source: str) -> None:
    """Persist an access token for a GitHub login."""

    norm = normalize_login(login)
    tok = str(token or "").strip()
    if not norm or not tok:
        raise ValueError("login and token are required")

    init_tokens_db()
    path = _db_path()
    now = int(time.time())
    with _connect(path) as conn:
        conn.execute(
            """
            INSERT INTO tokens(login, token, stored_at, source)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(login) DO UPDATE SET
              token=excluded.token,
              stored_at=excluded.stored_at,
              source=excluded.source
            """,
            (norm, tok, now, source),
        )
        conn.commit()


def get_token(login: str) -> StoredToken | None:
    """Return stored token for a GitHub login if present."""

    norm = normalize_login(login)
    if not norm:
        return None

    init_tokens_db()
    path = _db_path()
    with _connect(path) as conn:
        cur = conn.execute(
            "SELECT login, token, stored_at, source FROM tokens WHERE login=?",
            (norm,),
        )
        row = cur.fetchone()

    if not row:
        return None

    return StoredToken(
        login=str(row[0]),
        token=str(row[1]),
        stored_at=int(row[2]),
        source=str(row[3]),
    )
