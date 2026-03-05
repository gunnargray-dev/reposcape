"""GitHub OAuth helpers (stdlib-only).

This module implements the minimal pieces needed to support a GitHub OAuth login
flow for Reposcape's web app.

Notes:
- Uses only the Python standard library for HTTP.
- Stores the resulting GitHub access token in a signed cookie (HMAC) so we can
  call GitHub's API on behalf of the user.

Security model:
- Cookie integrity: HMAC-signed to prevent tampering.
- Cookie confidentiality: NOT encrypted. Treat this as a pragmatic interim step
  for development/self-hosting; a future version should store tokens server-side.

Env vars:
- REPOSCAPE_GITHUB_CLIENT_ID
- REPOSCAPE_GITHUB_CLIENT_SECRET
- REPOSCAPE_WEB_SECRET (required for cookie signing)

Optional:
- REPOSCAPE_GITHUB_OAUTH_REDIRECT_URL (defaults to
  http://localhost:8000/auth/github/callback)
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class GitHubToken:
    """OAuth access token response."""

    access_token: str
    token_type: str
    scope: str


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def github_client_id() -> str:
    return _required_env("REPOSCAPE_GITHUB_CLIENT_ID")


def github_client_secret() -> str:
    return _required_env("REPOSCAPE_GITHUB_CLIENT_SECRET")


def oauth_redirect_url() -> str:
    return os.environ.get(
        "REPOSCAPE_GITHUB_OAUTH_REDIRECT_URL",
        "http://localhost:8000/auth/github/callback",
    )


def make_state() -> str:
    """Return a random OAuth state value."""

    return secrets.token_urlsafe(32)


def authorize_url(state: str, *, scope: str = "read:user") -> str:
    """Return the GitHub OAuth authorize URL."""

    q = {
        "client_id": github_client_id(),
        "redirect_uri": oauth_redirect_url(),
        "scope": scope,
        "state": state,
        "allow_signup": "true",
    }
    return "https://github.com/login/oauth/authorize?" + urllib.parse.urlencode(q)


def exchange_code_for_token(code: str, *, state: str | None = None) -> GitHubToken:
    """Exchange authorization code for a GitHub access token."""

    data = {
        "client_id": github_client_id(),
        "client_secret": github_client_secret(),
        "code": code,
        "redirect_uri": oauth_redirect_url(),
    }
    if state:
        data["state"] = state

    req = urllib.request.Request(
        "https://github.com/login/oauth/access_token",
        data=urllib.parse.urlencode(data).encode("utf-8"),
        headers={"Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    if "error" in payload:
        desc = payload.get("error_description") or payload.get("error")
        raise RuntimeError(f"GitHub OAuth token exchange failed: {desc}")

    return GitHubToken(
        access_token=str(payload.get("access_token") or ""),
        token_type=str(payload.get("token_type") or ""),
        scope=str(payload.get("scope") or ""),
    )


def fetch_viewer_login(access_token: str) -> str:
    """Return the GitHub login for the token owner."""

    req = urllib.request.Request(
        "https://api.github.com/user",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "reposcape",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    login = payload.get("login")
    if not login:
        raise RuntimeError("GitHub /user response missing login")
    return str(login)


def _secret_key() -> bytes:
    return _required_env("REPOSCAPE_WEB_SECRET").encode("utf-8")


def sign_cookie_value(data: dict) -> str:
    """Return a signed, urlsafe cookie value for the given JSON payload."""

    raw = json.dumps(data, separators=(",", ":")).encode("utf-8")
    msg = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    sig = hmac.new(_secret_key(), msg.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{msg}.{sig}"


def verify_cookie_value(value: str, *, max_age_seconds: int) -> dict | None:
    """Verify and decode a signed cookie value."""

    if not value or "." not in value:
        return None

    msg, sig = value.rsplit(".", 1)
    expected = hmac.new(_secret_key(), msg.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        return None

    padded = msg + "=" * (-len(msg) % 4)
    raw = base64.urlsafe_b64decode(padded.encode("ascii"))
    data = json.loads(raw.decode("utf-8"))

    issued_at = int(data.get("iat") or 0)
    if issued_at <= 0:
        return None

    if int(time.time()) - issued_at > max_age_seconds:
        return None

    return data
