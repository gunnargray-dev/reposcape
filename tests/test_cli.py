"""CLI tests."""

from __future__ import annotations

import json

from src.cli.main import run


def test_cli_analyze_smoke(monkeypatch):
    def fake_analyze_repo(repo_url: str):
        return {"cached": False, "duration_ms": 1, "repo_url": repo_url, "languages": {"Python": 1}}

    monkeypatch.setattr("src.cli.main.analyze_repo", fake_analyze_repo)

    res = run(["analyze", "https://github.com/gunnargray-dev/reposcape", "--pretty"])
    assert res.exit_code == 0

    payload = json.loads(res.stdout)
    assert payload["repo_url"].endswith("/reposcape")
    assert payload["languages"]["Python"] == 1

