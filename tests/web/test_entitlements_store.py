from __future__ import annotations

from pathlib import Path

from src.web.entitlements import store


def test_normalize_subject() -> None:
    assert store.normalize_subject(None) is None
    assert store.normalize_subject("") is None
    assert store.normalize_subject("  ") is None
    assert store.normalize_subject("Test@Example.com ") == "test@example.com"


def test_grant_and_get_entitlement(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "entitlements.sqlite3"
    monkeypatch.setenv("REPOSCAPE_ENTITLEMENTS_DB", str(db_path))

    assert store.get_entitlement("a@example.com") is None

    store.grant_pro("A@Example.com", source="test")

    ent = store.get_entitlement("a@example.com")
    assert ent is not None
    assert ent.subject == "a@example.com"
    assert ent.plan == "pro"
    assert ent.active is True
    assert ent.source == "test"
