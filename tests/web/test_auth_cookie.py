from __future__ import annotations

import os
import time

import pytest

from src.web.auth.github_oauth import sign_cookie_value, verify_cookie_value


def test_signed_cookie_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REPOSCAPE_WEB_SECRET", "test-secret")

    now = int(time.time())
    value = sign_cookie_value({"iat": now, "login": "octocat", "token": "t"})
    data = verify_cookie_value(value, max_age_seconds=60)

    assert data
    assert data["login"] == "octocat"


def test_signed_cookie_rejects_tamper(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REPOSCAPE_WEB_SECRET", "test-secret")

    now = int(time.time())
    value = sign_cookie_value({"iat": now, "login": "octocat", "token": "t"})

    msg, sig = value.rsplit(".", 1)
    # flip one hex char
    bad = f"{msg}.{('0' if sig[0] != '0' else '1')}{sig[1:]}"

    assert verify_cookie_value(bad, max_age_seconds=60) is None


def test_signed_cookie_rejects_expired(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REPOSCAPE_WEB_SECRET", "test-secret")

    past = int(time.time()) - 120
    value = sign_cookie_value({"iat": past, "login": "octocat", "token": "t"})

    assert verify_cookie_value(value, max_age_seconds=60) is None
