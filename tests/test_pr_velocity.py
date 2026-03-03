"""Tests for the PR velocity module."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from src.pr_velocity import (
    analyze_merge_commits,
    estimate_pr_velocity,
    get_branch_stats,
    _extract_branch_from_merge_message,
    _calculate_trend,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _git(args: list[str], cwd: Path, env: dict | None = None) -> None:
    import os
    run_env = None
    if env:
        run_env = os.environ.copy()
        run_env.update(env)
    subprocess.run(["git"] + args, cwd=cwd, capture_output=True, check=False, env=run_env)


def _set_author(repo: Path, email: str, name: str) -> None:
    _git(["config", "user.email", email], repo)
    _git(["config", "user.name", name], repo)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def no_merge_repo(tmp_path_factory) -> str:
    """Simple linear repo with no merge commits."""
    repo = tmp_path_factory.mktemp("linear")
    _git(["init"], repo)
    _set_author(repo, "dev@example.com", "Dev")

    for i in range(4):
        (repo / f"file{i}.py").write_text(f"# {i}\n")
        _git(["add", "."], repo)
        _git(["commit", "--date=2026-01-{:02d}T10:00:00+00:00".format(i + 1), "-m", f"feat: add file{i}"], repo)

    return str(repo)


@pytest.fixture(scope="module")
def merge_repo(tmp_path_factory) -> str:
    """Repo with a real merge commit via branch + merge."""
    repo = tmp_path_factory.mktemp("merged")
    _git(["init"], repo)
    _set_author(repo, "dev@example.com", "Dev")

    # Initial commit on default branch (master or main depending on git config)
    (repo / "main.py").write_text("# main\n")
    _git(["add", "."], repo)
    _git(["commit", "--date=2026-01-01T10:00:00+00:00", "-m", "feat: initial"], repo)

    # Detect default branch name
    r = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo, capture_output=True, text=True,
    )
    default_branch = r.stdout.strip() or "master"

    # Create and work on a feature branch
    _git(["checkout", "-b", "feature/my-feature"], repo)
    (repo / "feature.py").write_text("# feature\n")
    _git(["add", "."], repo)
    _git(["commit", "--date=2026-01-02T10:00:00+00:00", "-m", "feat: add feature"], repo)

    # Go back to default branch and merge
    _git(["checkout", default_branch], repo)
    _git(["merge", "--no-ff", "feature/my-feature", "-m", "Merge branch 'feature/my-feature'"], repo)

    return str(repo)


@pytest.fixture(scope="module")
def empty_repo(tmp_path_factory) -> str:
    repo = tmp_path_factory.mktemp("empty")
    _git(["init"], repo)
    return str(repo)


@pytest.fixture(scope="module")
def multi_branch_repo(tmp_path_factory) -> str:
    """Repo with multiple branches including stale ones."""
    repo = tmp_path_factory.mktemp("branches")
    _git(["init"], repo)
    _set_author(repo, "dev@example.com", "Dev")

    (repo / "main.py").write_text("# main\n")
    _git(["add", "."], repo)
    _git(["commit", "--date=2026-01-01T10:00:00+00:00", "-m", "feat: initial"], repo)

    # Detect default branch
    r = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo, capture_output=True, text=True,
    )
    default_branch = r.stdout.strip() or "master"

    # Create active branch (recent commit)
    _git(["checkout", "-b", "feature/active"], repo)
    (repo / "active.py").write_text("# active\n")
    _git(["add", "."], repo)
    _git(["commit", "-m", "feat: active branch"], repo)

    _git(["checkout", default_branch], repo)

    # Create stale branch with old committer date
    _git(["checkout", "-b", "feature/stale"], repo)
    (repo / "stale.py").write_text("# stale\n")
    _git(["add", "."], repo)
    old_date = "2024-01-01T10:00:00+00:00"
    _git(
        ["commit", f"--date={old_date}", "-m", "feat: stale branch"],
        repo,
        env={"GIT_COMMITTER_DATE": old_date},
    )

    _git(["checkout", default_branch], repo)

    return str(repo)


# ---------------------------------------------------------------------------
# analyze_merge_commits tests
# ---------------------------------------------------------------------------


def test_analyze_merge_commits_returns_list(merge_repo: str) -> None:
    result = analyze_merge_commits(merge_repo)
    assert isinstance(result, list)


def test_analyze_merge_commits_finds_merge(merge_repo: str) -> None:
    result = analyze_merge_commits(merge_repo)
    assert len(result) >= 1


def test_analyze_merge_commits_structure(merge_repo: str) -> None:
    result = analyze_merge_commits(merge_repo)
    assert len(result) >= 1
    m = result[0]
    assert "hash" in m
    assert "date" in m
    assert "author_name" in m
    assert "author_email" in m
    assert "message" in m
    assert "branch_name" in m
    assert "commits_in_merge" in m


def test_analyze_merge_commits_branch_name_extracted(merge_repo: str) -> None:
    result = analyze_merge_commits(merge_repo)
    assert len(result) >= 1
    assert result[0]["branch_name"] == "feature/my-feature"


def test_analyze_merge_commits_no_merges_in_linear_repo(no_merge_repo: str) -> None:
    result = analyze_merge_commits(no_merge_repo)
    assert result == []


def test_analyze_merge_commits_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        analyze_merge_commits(str(tmp_path))


def test_analyze_merge_commits_hash_length(merge_repo: str) -> None:
    result = analyze_merge_commits(merge_repo)
    for m in result:
        assert len(m["hash"]) == 40


# ---------------------------------------------------------------------------
# estimate_pr_velocity tests
# ---------------------------------------------------------------------------


def test_estimate_pr_velocity_returns_dict(no_merge_repo: str) -> None:
    result = estimate_pr_velocity(no_merge_repo)
    assert isinstance(result, dict)


def test_estimate_pr_velocity_structure(no_merge_repo: str) -> None:
    result = estimate_pr_velocity(no_merge_repo)
    expected_keys = {
        "total_merges", "avg_commits_per_merge", "merges_per_week",
        "busiest_week", "merge_frequency_trend", "weekly_counts",
    }
    assert expected_keys.issubset(set(result.keys()))


def test_estimate_pr_velocity_no_merges(no_merge_repo: str) -> None:
    result = estimate_pr_velocity(no_merge_repo)
    assert result["total_merges"] == 0
    assert result["merges_per_week"] == 0.0
    assert result["busiest_week"] is None


def test_estimate_pr_velocity_with_merges(merge_repo: str) -> None:
    result = estimate_pr_velocity(merge_repo)
    assert result["total_merges"] >= 1


def test_estimate_pr_velocity_trend_valid(no_merge_repo: str) -> None:
    result = estimate_pr_velocity(no_merge_repo)
    assert result["merge_frequency_trend"] in ("increasing", "decreasing", "stable")


def test_estimate_pr_velocity_weekly_counts_list(merge_repo: str) -> None:
    result = estimate_pr_velocity(merge_repo)
    assert isinstance(result["weekly_counts"], list)


def test_estimate_pr_velocity_weekly_counts_structure(merge_repo: str) -> None:
    result = estimate_pr_velocity(merge_repo)
    for entry in result["weekly_counts"]:
        assert "week" in entry
        assert "merges" in entry
        assert entry["merges"] >= 1


# ---------------------------------------------------------------------------
# get_branch_stats tests
# ---------------------------------------------------------------------------


def test_get_branch_stats_returns_dict(multi_branch_repo: str) -> None:
    result = get_branch_stats(multi_branch_repo)
    assert isinstance(result, dict)


def test_get_branch_stats_structure(multi_branch_repo: str) -> None:
    result = get_branch_stats(multi_branch_repo)
    assert "total" in result
    assert "active" in result
    assert "stale" in result
    assert "branches" in result


def test_get_branch_stats_total_equals_active_plus_stale(multi_branch_repo: str) -> None:
    result = get_branch_stats(multi_branch_repo)
    assert result["total"] == result["active"] + result["stale"]


def test_get_branch_stats_branch_structure(multi_branch_repo: str) -> None:
    result = get_branch_stats(multi_branch_repo)
    for branch in result["branches"]:
        assert "name" in branch
        assert "last_commit_date" in branch
        assert "author" in branch
        assert "is_stale" in branch
        assert "commits_ahead" in branch


def test_get_branch_stats_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        get_branch_stats(str(tmp_path))


def test_get_branch_stats_stale_branch_detected(multi_branch_repo: str) -> None:
    result = get_branch_stats(multi_branch_repo)
    stale_names = [b["name"] for b in result["branches"] if b["is_stale"]]
    assert "feature/stale" in stale_names


def test_get_branch_stats_has_multiple_branches(multi_branch_repo: str) -> None:
    result = get_branch_stats(multi_branch_repo)
    assert result["total"] >= 2


# ---------------------------------------------------------------------------
# _extract_branch_from_merge_message tests
# ---------------------------------------------------------------------------


def test_extract_branch_simple_branch() -> None:
    result = _extract_branch_from_merge_message("Merge branch 'feature/my-feature'")
    assert result == "feature/my-feature"


def test_extract_branch_into_syntax() -> None:
    result = _extract_branch_from_merge_message("Merge branch 'hotfix/bug' into main")
    assert result == "hotfix/bug"


def test_extract_branch_pr_syntax() -> None:
    result = _extract_branch_from_merge_message("Merge pull request #42 from user/feature-branch")
    assert result == "feature-branch"


def test_extract_branch_remote_tracking() -> None:
    result = _extract_branch_from_merge_message("Merge remote-tracking branch 'origin/develop'")
    assert result == "develop"


def test_extract_branch_no_match() -> None:
    result = _extract_branch_from_merge_message("Random merge message")
    assert result is None


# ---------------------------------------------------------------------------
# _calculate_trend tests
# ---------------------------------------------------------------------------


def test_calculate_trend_increasing() -> None:
    values = [1, 1, 1, 1, 5, 5, 5, 5]
    assert _calculate_trend(values) == "increasing"


def test_calculate_trend_decreasing() -> None:
    values = [5, 5, 5, 5, 1, 1, 1, 1]
    assert _calculate_trend(values) == "decreasing"


def test_calculate_trend_stable() -> None:
    values = [3, 3, 3, 3, 3, 3, 3, 3]
    assert _calculate_trend(values) == "stable"


def test_calculate_trend_too_short() -> None:
    assert _calculate_trend([1, 2, 3]) == "stable"
