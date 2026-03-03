"""Tests for the commit timeline module."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from src.timeline import (
    build_commit_timeline,
    detect_milestones,
    get_file_churn,
    get_growth_curve,
    _format_period,
    _parse_iso_datetime,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git"] + args, cwd=cwd, capture_output=True, check=False)


def _set_author(repo: Path, email: str, name: str) -> None:
    _git(["config", "user.email", email], repo)
    _git(["config", "user.name", name], repo)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def basic_repo(tmp_path: Path) -> str:
    """Simple single-author repo with several commits on different dates."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(["init"], repo)
    _set_author(repo, "alice@example.com", "Alice")

    commits = [
        ("2026-01-05T10:00:00+00:00", "feat: initial commit", "main.py", "x = 1\n"),
        ("2026-01-12T11:00:00+00:00", "feat: add utils", "utils.py", "def f():\n    pass\n"),
        ("2026-01-19T09:00:00+00:00", "fix: bug fix", "main.py", "x = 2\n"),
        ("2026-01-26T14:00:00+00:00", "feat: add tests", "test.py", "# tests\n"),
    ]
    for date, msg, fname, content in commits:
        (repo / fname).write_text(content)
        _git(["add", fname], repo)
        _git(["commit", f"--date={date}", "-m", msg], repo)

    return str(repo)


@pytest.fixture()
def two_author_repo(tmp_path: Path) -> str:
    """Repo with two authors to check author counting per bucket."""
    repo = tmp_path / "repo2"
    repo.mkdir()
    _git(["init"], repo)

    _set_author(repo, "alice@example.com", "Alice")
    (repo / "a.py").write_text("# a\n")
    _git(["add", "."], repo)
    _git(["commit", "--date=2026-02-01T10:00:00+00:00", "-m", "feat: file a"], repo)

    _set_author(repo, "bob@example.com", "Bob")
    (repo / "b.py").write_text("# b\n")
    _git(["add", "."], repo)
    _git(["commit", "--date=2026-02-02T10:00:00+00:00", "-m", "feat: file b"], repo)

    return str(repo)


@pytest.fixture()
def large_commit_repo(tmp_path: Path) -> str:
    """Repo with one very large commit for milestone detection."""
    repo = tmp_path / "bigrepo"
    repo.mkdir()
    _git(["init"], repo)
    _set_author(repo, "dev@example.com", "Dev")

    # First: small commit
    (repo / "small.py").write_text("x = 1\n")
    _git(["add", "."], repo)
    _git(["commit", "--date=2026-01-01T10:00:00+00:00", "-m", "feat: init"], repo)

    # Then: large commit (>500 lines)
    big_content = "\n".join(f"line_{i} = {i}" for i in range(600))
    (repo / "big.py").write_text(big_content + "\n")
    _git(["add", "."], repo)
    _git(["commit", "--date=2026-01-10T10:00:00+00:00", "-m", "feat: add big file"], repo)

    return str(repo)


@pytest.fixture()
def empty_repo(tmp_path: Path) -> str:
    repo = tmp_path / "empty"
    repo.mkdir()
    _git(["init"], repo)
    return str(repo)


@pytest.fixture()
def multi_file_churn_repo(tmp_path: Path) -> str:
    """Repo where one file is modified many times."""
    repo = tmp_path / "churn"
    repo.mkdir()
    _git(["init"], repo)
    _set_author(repo, "dev@example.com", "Dev")

    # Create initial files
    (repo / "hot.py").write_text("x = 0\n")
    (repo / "cold.py").write_text("y = 0\n")
    _git(["add", "."], repo)
    _git(["commit", "--date=2026-01-01T09:00:00+00:00", "-m", "feat: init"], repo)

    # Modify hot.py 5 more times
    for i in range(1, 6):
        (repo / "hot.py").write_text(f"x = {i}\n")
        _git(["add", "hot.py"], repo)
        _git(["commit", f"--date=2026-01-{i+1:02d}T09:00:00+00:00", "-m", f"fix: update hot {i}"], repo)

    return str(repo)


# ---------------------------------------------------------------------------
# build_commit_timeline tests
# ---------------------------------------------------------------------------


def test_build_commit_timeline_returns_list(basic_repo: str) -> None:
    result = build_commit_timeline(basic_repo)
    assert isinstance(result, list)


def test_build_commit_timeline_week_bucket_structure(basic_repo: str) -> None:
    result = build_commit_timeline(basic_repo, bucket="week")
    assert len(result) >= 1
    for entry in result:
        assert "period" in entry
        assert "commits" in entry
        assert "authors" in entry
        assert "lines_added" in entry
        assert "lines_deleted" in entry
        assert "net_lines" in entry
        assert "files_changed" in entry


def test_build_commit_timeline_day_bucket(basic_repo: str) -> None:
    result = build_commit_timeline(basic_repo, bucket="day")
    assert len(result) >= 1
    for entry in result:
        # Day format: YYYY-MM-DD
        assert len(entry["period"]) == 10
        assert entry["period"][4] == "-"


def test_build_commit_timeline_month_bucket(basic_repo: str) -> None:
    result = build_commit_timeline(basic_repo, bucket="month")
    assert len(result) >= 1
    for entry in result:
        # Month format: YYYY-MM
        assert len(entry["period"]) == 7


def test_build_commit_timeline_week_bucket_label(basic_repo: str) -> None:
    result = build_commit_timeline(basic_repo, bucket="week")
    for entry in result:
        assert "-W" in entry["period"]


def test_build_commit_timeline_sorted_ascending(basic_repo: str) -> None:
    result = build_commit_timeline(basic_repo, bucket="week")
    periods = [e["period"] for e in result]
    assert periods == sorted(periods)


def test_build_commit_timeline_commit_counts_positive(basic_repo: str) -> None:
    result = build_commit_timeline(basic_repo, bucket="week")
    for entry in result:
        assert entry["commits"] >= 1


def test_build_commit_timeline_authors_positive(two_author_repo: str) -> None:
    result = build_commit_timeline(two_author_repo, bucket="week")
    total_authors_seen = sum(e["authors"] for e in result)
    assert total_authors_seen >= 1


def test_build_commit_timeline_net_lines_computed(basic_repo: str) -> None:
    result = build_commit_timeline(basic_repo, bucket="week")
    for entry in result:
        assert entry["net_lines"] == entry["lines_added"] - entry["lines_deleted"]


def test_build_commit_timeline_invalid_bucket(basic_repo: str) -> None:
    with pytest.raises(ValueError):
        build_commit_timeline(basic_repo, bucket="year")


def test_build_commit_timeline_empty_repo(empty_repo: str) -> None:
    result = build_commit_timeline(empty_repo)
    assert result == []


def test_build_commit_timeline_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        build_commit_timeline(str(tmp_path))


def test_build_commit_timeline_total_commits_match(basic_repo: str) -> None:
    result = build_commit_timeline(basic_repo, bucket="day")
    total = sum(e["commits"] for e in result)
    assert total == 4  # We created 4 commits in basic_repo


# ---------------------------------------------------------------------------
# detect_milestones tests
# ---------------------------------------------------------------------------


def test_detect_milestones_returns_list(basic_repo: str) -> None:
    result = detect_milestones(basic_repo)
    assert isinstance(result, list)


def test_detect_milestones_finds_first_commit(basic_repo: str) -> None:
    result = detect_milestones(basic_repo)
    types = [m["type"] for m in result]
    assert "first_commit" in types


def test_detect_milestones_first_commit_keys(basic_repo: str) -> None:
    result = detect_milestones(basic_repo)
    fc = next(m for m in result if m["type"] == "first_commit")
    assert "date" in fc
    assert "description" in fc
    assert "details" in fc
    assert "hash" in fc["details"]


def test_detect_milestones_sorted_by_date(large_commit_repo: str) -> None:
    result = detect_milestones(large_commit_repo)
    dates = [m["date"] for m in result]
    assert dates == sorted(dates)


def test_detect_milestones_large_commit_detected(large_commit_repo: str) -> None:
    result = detect_milestones(large_commit_repo)
    types = [m["type"] for m in result]
    assert "large_commit" in types


def test_detect_milestones_large_commit_details(large_commit_repo: str) -> None:
    result = detect_milestones(large_commit_repo)
    lc = next(m for m in result if m["type"] == "large_commit")
    assert lc["details"]["lines_changed"] > 500


def test_detect_milestones_empty_repo(empty_repo: str) -> None:
    result = detect_milestones(empty_repo)
    assert result == []


def test_detect_milestones_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        detect_milestones(str(tmp_path))


def test_detect_milestones_milestone_structure(basic_repo: str) -> None:
    result = detect_milestones(basic_repo)
    for m in result:
        assert "date" in m
        assert "type" in m
        assert "description" in m
        assert "details" in m
        assert isinstance(m["details"], dict)


# ---------------------------------------------------------------------------
# get_growth_curve tests
# ---------------------------------------------------------------------------


def test_get_growth_curve_returns_list(basic_repo: str) -> None:
    result = get_growth_curve(basic_repo)
    assert isinstance(result, list)


def test_get_growth_curve_non_empty(basic_repo: str) -> None:
    result = get_growth_curve(basic_repo)
    assert len(result) >= 1


def test_get_growth_curve_structure(basic_repo: str) -> None:
    result = get_growth_curve(basic_repo)
    for entry in result:
        assert "date" in entry
        assert "total_lines" in entry
        assert "total_files" in entry
        assert "total_authors" in entry


def test_get_growth_curve_authors_increase(basic_repo: str) -> None:
    result = get_growth_curve(basic_repo)
    # Authors never decrease over time
    for i in range(1, len(result)):
        assert result[i]["total_authors"] >= result[i - 1]["total_authors"]


def test_get_growth_curve_lines_non_negative(basic_repo: str) -> None:
    result = get_growth_curve(basic_repo)
    for entry in result:
        assert entry["total_lines"] >= 0


def test_get_growth_curve_dates_sorted(basic_repo: str) -> None:
    result = get_growth_curve(basic_repo)
    dates = [e["date"] for e in result]
    assert dates == sorted(dates)


def test_get_growth_curve_empty_repo(empty_repo: str) -> None:
    result = get_growth_curve(empty_repo)
    assert result == []


def test_get_growth_curve_single_author(basic_repo: str) -> None:
    result = get_growth_curve(basic_repo)
    last = result[-1]
    assert last["total_authors"] == 1


# ---------------------------------------------------------------------------
# get_file_churn tests
# ---------------------------------------------------------------------------


def test_get_file_churn_returns_list(multi_file_churn_repo: str) -> None:
    result = get_file_churn(multi_file_churn_repo)
    assert isinstance(result, list)


def test_get_file_churn_structure(multi_file_churn_repo: str) -> None:
    result = get_file_churn(multi_file_churn_repo)
    for entry in result:
        assert "path" in entry
        assert "changes" in entry
        assert "authors" in entry
        assert "last_changed" in entry


def test_get_file_churn_sorted_by_changes_desc(multi_file_churn_repo: str) -> None:
    result = get_file_churn(multi_file_churn_repo)
    changes = [e["changes"] for e in result]
    assert changes == sorted(changes, reverse=True)


def test_get_file_churn_hot_file_first(multi_file_churn_repo: str) -> None:
    result = get_file_churn(multi_file_churn_repo)
    assert len(result) >= 1
    assert result[0]["path"] == "hot.py"


def test_get_file_churn_top_n_limit(multi_file_churn_repo: str) -> None:
    result = get_file_churn(multi_file_churn_repo, top_n=1)
    assert len(result) <= 1


def test_get_file_churn_authors_positive(multi_file_churn_repo: str) -> None:
    result = get_file_churn(multi_file_churn_repo)
    for entry in result:
        assert entry["authors"] >= 1


def test_get_file_churn_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        get_file_churn(str(tmp_path))


def test_get_file_churn_last_changed_format(multi_file_churn_repo: str) -> None:
    result = get_file_churn(multi_file_churn_repo)
    for entry in result:
        if entry["last_changed"]:
            assert len(entry["last_changed"]) == 10  # YYYY-MM-DD


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------


def test_format_period_day() -> None:
    from datetime import datetime
    dt = datetime(2026, 3, 15, 10, 0, 0)
    assert _format_period(dt, "day") == "2026-03-15"


def test_format_period_month() -> None:
    from datetime import datetime
    dt = datetime(2026, 3, 15, 10, 0, 0)
    assert _format_period(dt, "month") == "2026-03"


def test_format_period_week() -> None:
    from datetime import datetime
    dt = datetime(2026, 3, 15, 10, 0, 0)
    result = _format_period(dt, "week")
    assert "W" in result
    assert result.startswith("2026")


def test_parse_iso_datetime_with_offset() -> None:
    dt = _parse_iso_datetime("2026-01-15T10:30:00+05:00")
    assert dt.year == 2026
    assert dt.month == 1
    assert dt.day == 15


def test_parse_iso_datetime_utc_z() -> None:
    dt = _parse_iso_datetime("2026-03-01T08:00:00Z")
    assert dt.year == 2026
    assert dt.hour == 8


def test_parse_iso_datetime_date_only() -> None:
    dt = _parse_iso_datetime("2026-06-15")
    assert dt.year == 2026
    assert dt.month == 6
    assert dt.day == 15


# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Integration tests using shared local_git_repo fixture (no network)
# ---------------------------------------------------------------------------


def test_build_commit_timeline_on_local_repo(local_git_repo: str) -> None:
    result = build_commit_timeline(local_git_repo, bucket="week")
    assert len(result) >= 1
    assert all(e["commits"] >= 1 for e in result)


def test_detect_milestones_on_local_repo(local_git_repo: str) -> None:
    result = detect_milestones(local_git_repo)
    assert isinstance(result, list)
    assert len(result) >= 1
    types = {m["type"] for m in result}
    assert "first_commit" in types


def test_get_file_churn_on_local_repo(local_git_repo: str) -> None:
    result = get_file_churn(local_git_repo)
    assert isinstance(result, list)
    assert len(result) >= 1


# ---------------------------------------------------------------------------
# Network integration tests (skipped by default)
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestTimelineNetworkIntegration:
    @pytest.fixture(scope="class")
    def reposcape_clone(self, tmp_path_factory) -> str:
        import subprocess
        target = tmp_path_factory.mktemp("reposcape")
        result = subprocess.run(
            ["git", "clone", "https://github.com/gunnargray-dev/reposcape.git", str(target)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            pytest.skip("Could not clone reposcape repo (network unavailable)")
        return str(target)

    def test_timeline_on_reposcape(self, reposcape_clone):
        result = build_commit_timeline(reposcape_clone, bucket="week")
        assert len(result) >= 1
