"""GitHub metadata helpers tests."""

from __future__ import annotations

from datetime import datetime, timezone

from src.github_meta import _parse_repo_metadata


def test_parse_repo_metadata_parses_updated_at() -> None:
    meta = _parse_repo_metadata(
        "octo",
        "hello",
        {
            "stargazers_count": 123,
            "forks_count": 5,
            "open_issues_count": 2,
            "watchers_count": 10,
            "language": "Python",
            "updated_at": "2020-01-02T03:04:05Z",
            "html_url": "https://github.com/octo/hello",
        },
    )

    assert meta.stargazers_count == 123
    assert meta.primary_language == "Python"
    assert meta.updated_at == datetime(2020, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    assert meta.html_url == "https://github.com/octo/hello"
    assert meta.error is None


def test_parse_repo_metadata_handles_bad_updated_at() -> None:
    meta = _parse_repo_metadata("octo", "hello", {"updated_at": "nope"})
    assert meta.updated_at is None
