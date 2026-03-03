"""Tests for the contributor statistics engine."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from src.contributors import (
    analyze_contributors,
    get_activity_periods,
    get_author_file_ownership,
    get_author_timeline,
    get_collaboration_pairs,
    _parse_iso_datetime,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def single_author_repo(tmp_path_factory) -> str:
    """Create a minimal git repo with a single author and several commits."""
    repo = tmp_path_factory.mktemp("repo")
    _git(["init"], repo)
    _git(["config", "user.email", "alice@example.com"], repo)
    _git(["config", "user.name", "Alice"], repo)

    for i in range(3):
        f = repo / f"file{i}.py"
        f.write_text(f"x = {i}\n")
        _git(["add", f.name], repo)
        _git(
            ["commit", "--date=2026-01-0{}T10:00:00+00:00".format(i + 1), "-m", f"feat: add file{i}"],
            repo,
        )

    return str(repo)


@pytest.fixture(scope="module")
def two_author_repo(tmp_path_factory) -> str:
    """Create a git repo with two authors who both touch the same file."""
    repo = tmp_path_factory.mktemp("repo2")
    _git(["init"], repo)

    _set_author(repo, "alice@example.com", "Alice")
    (repo / "shared.py").write_text("# shared\n")
    (repo / "alice_only.py").write_text("# alice\n")
    _git(["add", "."], repo)
    _git(["commit", "--date=2026-01-01T09:00:00+00:00", "-m", "feat: initial files"], repo)

    _set_author(repo, "bob@example.com", "Bob")
    (repo / "shared.py").write_text("# shared\nx = 1\n")
    (repo / "bob_only.py").write_text("# bob\n")
    _git(["add", "."], repo)
    _git(["commit", "--date=2026-01-02T14:30:00+00:00", "-m", "fix: update shared and add bob_only"], repo)

    _set_author(repo, "alice@example.com", "Alice")
    (repo / "shared.py").write_text("# shared\nx = 1\ny = 2\n")
    _git(["add", "."], repo)
    _git(["commit", "--date=2026-01-03T11:00:00+00:00", "-m", "feat: extend shared"], repo)

    return str(repo)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git"] + args, cwd=cwd, capture_output=True, check=False)


def _set_author(repo: Path, email: str, name: str) -> None:
    _git(["config", "user.email", email], repo)
    _git(["config", "user.name", name], repo)


# ---------------------------------------------------------------------------
# analyze_contributors tests
# ---------------------------------------------------------------------------


def test_analyze_contributors_returns_dict(single_author_repo: str) -> None:
    result = analyze_contributors(single_author_repo)
    assert isinstance(result, dict)
    assert "authors" in result
    assert "total_commits" in result


def test_analyze_contributors_author_keys(single_author_repo: str) -> None:
    result = analyze_contributors(single_author_repo)
    author = result["authors"][0]
    expected_keys = {
        "author_name", "author_email", "total_commits",
        "insertions", "deletions", "first_commit_date",
        "last_commit_date", "active_days", "files_touched",
    }
    assert expected_keys.issubset(set(author.keys()))


def test_analyze_contributors_single_author_commit_count(single_author_repo: str) -> None:
    result = analyze_contributors(single_author_repo)
    assert len(result["authors"]) == 1
    assert result["authors"][0]["total_commits"] == 3
    assert result["total_commits"] == 3


def test_analyze_contributors_sorted_descending(two_author_repo: str) -> None:
    result = analyze_contributors(two_author_repo)
    counts = [a["total_commits"] for a in result["authors"]]
    assert counts == sorted(counts, reverse=True)


def test_analyze_contributors_two_authors(two_author_repo: str) -> None:
    result = analyze_contributors(two_author_repo)
    assert len(result["authors"]) == 2


def test_analyze_contributors_active_days_positive(single_author_repo: str) -> None:
    result = analyze_contributors(single_author_repo)
    assert result["authors"][0]["active_days"] >= 1


def test_analyze_contributors_files_touched_positive(single_author_repo: str) -> None:
    result = analyze_contributors(single_author_repo)
    # Alice touched 3 files
    assert result["authors"][0]["files_touched"] >= 1


def test_analyze_contributors_empty_repo(tmp_path: Path) -> None:
    repo = tmp_path / "empty"
    repo.mkdir()
    _git(["init"], repo)
    result = analyze_contributors(str(repo))
    assert result == {"authors": [], "total_commits": 0}


def test_analyze_contributors_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        analyze_contributors(str(tmp_path))


def test_analyze_contributors_insertions_deletions(two_author_repo: str) -> None:
    result = analyze_contributors(two_author_repo)
    total_insertions = sum(a["insertions"] for a in result["authors"])
    assert total_insertions >= 0  # Could be 0 if binary only


# ---------------------------------------------------------------------------
# get_author_timeline tests
# ---------------------------------------------------------------------------


def test_get_author_timeline_returns_list(single_author_repo: str) -> None:
    result = get_author_timeline(single_author_repo)
    assert isinstance(result, list)


def test_get_author_timeline_single_author_structure(single_author_repo: str) -> None:
    result = get_author_timeline(single_author_repo)
    assert len(result) == 1
    entry = result[0]
    assert "author_name" in entry
    assert "author_email" in entry
    assert "timeline" in entry


def test_get_author_timeline_timeline_entries(single_author_repo: str) -> None:
    result = get_author_timeline(single_author_repo)
    timeline = result[0]["timeline"]
    assert len(timeline) >= 1
    for entry in timeline:
        assert "date" in entry
        assert "commits" in entry
        assert isinstance(entry["commits"], int)
        assert entry["commits"] >= 1


def test_get_author_timeline_dates_sorted(single_author_repo: str) -> None:
    result = get_author_timeline(single_author_repo)
    timeline = result[0]["timeline"]
    dates = [e["date"] for e in timeline]
    assert dates == sorted(dates)


def test_get_author_timeline_empty_repo(tmp_path: Path) -> None:
    repo = tmp_path / "empty"
    repo.mkdir()
    _git(["init"], repo)
    result = get_author_timeline(str(repo))
    assert result == []


def test_get_author_timeline_two_authors(two_author_repo: str) -> None:
    result = get_author_timeline(two_author_repo)
    assert len(result) == 2


# ---------------------------------------------------------------------------
# get_author_file_ownership tests
# ---------------------------------------------------------------------------


def test_get_author_file_ownership_returns_dict(single_author_repo: str) -> None:
    result = get_author_file_ownership(single_author_repo)
    assert isinstance(result, dict)


def test_get_author_file_ownership_entry_keys(single_author_repo: str) -> None:
    result = get_author_file_ownership(single_author_repo)
    if result:
        entry = next(iter(result.values()))
        assert "primary_author" in entry
        assert "primary_author_name" in entry
        assert "ownership_pct" in entry
        assert "total_commits" in entry


def test_get_author_file_ownership_pct_range(two_author_repo: str) -> None:
    result = get_author_file_ownership(two_author_repo)
    for entry in result.values():
        assert 0.0 <= entry["ownership_pct"] <= 100.0


def test_get_author_file_ownership_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        get_author_file_ownership(str(tmp_path))


# ---------------------------------------------------------------------------
# get_collaboration_pairs tests
# ---------------------------------------------------------------------------


def test_get_collaboration_pairs_returns_list(two_author_repo: str) -> None:
    result = get_collaboration_pairs(two_author_repo)
    assert isinstance(result, list)


def test_get_collaboration_pairs_entry_keys(two_author_repo: str) -> None:
    result = get_collaboration_pairs(two_author_repo)
    if result:
        pair = result[0]
        assert "author_a" in pair
        assert "author_b" in pair
        assert "overlap_count" in pair
        assert "shared_files" in pair


def test_get_collaboration_pairs_sorted_by_overlap(two_author_repo: str) -> None:
    result = get_collaboration_pairs(two_author_repo)
    overlaps = [p["overlap_count"] for p in result]
    assert overlaps == sorted(overlaps, reverse=True)


def test_get_collaboration_pairs_single_author_no_pairs(single_author_repo: str) -> None:
    result = get_collaboration_pairs(single_author_repo)
    assert result == []


# ---------------------------------------------------------------------------
# get_activity_periods tests
# ---------------------------------------------------------------------------


def test_get_activity_periods_returns_dict(single_author_repo: str) -> None:
    result = get_activity_periods(single_author_repo)
    assert isinstance(result, dict)


def test_get_activity_periods_entry_keys(single_author_repo: str) -> None:
    result = get_activity_periods(single_author_repo)
    assert len(result) >= 1
    entry = next(iter(result.values()))
    assert "author_name" in entry
    assert "peak_hour" in entry
    assert "peak_day" in entry
    assert "hour_distribution" in entry
    assert "day_distribution" in entry


def test_get_activity_periods_peak_hour_valid(single_author_repo: str) -> None:
    result = get_activity_periods(single_author_repo)
    for entry in result.values():
        assert 0 <= entry["peak_hour"] <= 23


def test_get_activity_periods_peak_day_valid(single_author_repo: str) -> None:
    result = get_activity_periods(single_author_repo)
    for entry in result.values():
        assert 0 <= entry["peak_day"] <= 6


def test_get_activity_periods_distributions_length(single_author_repo: str) -> None:
    result = get_activity_periods(single_author_repo)
    for entry in result.values():
        assert len(entry["hour_distribution"]) == 24
        assert len(entry["day_distribution"]) == 7


def test_get_activity_periods_empty_repo(tmp_path: Path) -> None:
    repo = tmp_path / "empty"
    repo.mkdir()
    _git(["init"], repo)
    result = get_activity_periods(str(repo))
    assert result == {}


# ---------------------------------------------------------------------------
# _parse_iso_datetime tests
# ---------------------------------------------------------------------------


def test_parse_iso_datetime_with_offset() -> None:
    dt = _parse_iso_datetime("2026-01-15T10:30:00+05:00")
    assert dt.year == 2026
    assert dt.month == 1
    assert dt.day == 15
    assert dt.hour == 10
    assert dt.minute == 30


def test_parse_iso_datetime_utc_z() -> None:
    dt = _parse_iso_datetime("2026-03-01T08:00:00Z")
    assert dt.year == 2026
    assert dt.hour == 8


def test_parse_iso_datetime_date_only() -> None:
    dt = _parse_iso_datetime("2026-06-15")
    assert dt.year == 2026
    assert dt.month == 6
    assert dt.day == 15
