"""CLI tests."""

from __future__ import annotations

import json
from pathlib import Path

from src.cli.main import run


def test_cli_analyze_smoke(monkeypatch):
    def fake_analyze_repo(repo_url: str, snapshot_base_dir=None):
        return {"cached": False, "duration_ms": 1, "repo_url": repo_url, "languages": {"Python": 1}}

    monkeypatch.setattr("src.cli.main.analyze_repo", fake_analyze_repo)

    res = run(["analyze", "https://github.com/gunnargray-dev/reposcape", "--pretty"])
    assert res.exit_code == 0

    payload = json.loads(res.stdout)
    assert payload["repo_url"].endswith("/reposcape")
    assert payload["languages"]["Python"] == 1


def test_cli_analyze_snapshot_dir_passed(monkeypatch, tmp_path: Path):
    captured = {}

    def fake_analyze_repo(repo_url: str, snapshot_base_dir=None):
        captured["repo_url"] = repo_url
        captured["snapshot_base_dir"] = snapshot_base_dir
        return {"cached": False, "duration_ms": 1, "repo_url": repo_url, "languages": {"Python": 1}}

    monkeypatch.setattr("src.cli.main.analyze_repo", fake_analyze_repo)

    res = run(
        [
            "analyze",
            "https://github.com/gunnargray-dev/reposcape",
            "--snapshot-dir",
            str(tmp_path),
        ]
    )
    assert res.exit_code == 0
    assert captured["repo_url"].endswith("/reposcape")
    assert captured["snapshot_base_dir"] == tmp_path
