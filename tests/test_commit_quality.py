"""Tests for commit message quality analyzer."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from src.commit_quality import (
    CONVENTIONAL_PREFIXES,
    analyze_commit_quality,
    score_commit_message,
    _has_conventional_prefix,
    _score_length,
    _score_to_grade,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git"] + args, cwd=cwd, capture_output=True, check=False)


@pytest.fixture()
def quality_repo(tmp_path: Path) -> str:
    """Git repo with a mix of good and bad commit messages."""
    repo = tmp_path / "qrepo"
    repo.mkdir()
    _git(["init"], repo)
    _git(["config", "user.email", "dev@example.com"], repo)
    _git(["config", "user.name", "Dev"], repo)

    messages_and_files = [
        ("feat: add user authentication system with JWT tokens", "auth.py"),
        ("fix: resolve null pointer exception in login flow", "login.py"),
        ("docs: update README with installation instructions", "README.md"),
        ("wip", "wip.py"),
        ("fix", "bad1.py"),
        ("update", "bad2.py"),
    ]

    for msg, filename in messages_and_files:
        f = repo / filename
        f.write_text(f"# {filename}\n")
        _git(["add", filename], repo)
        _git(["commit", "-m", msg], repo)

    return str(repo)


# ---------------------------------------------------------------------------
# CONVENTIONAL_PREFIXES tests
# ---------------------------------------------------------------------------


def test_conventional_prefixes_is_list() -> None:
    assert isinstance(CONVENTIONAL_PREFIXES, list)


def test_conventional_prefixes_contains_common() -> None:
    assert "feat" in CONVENTIONAL_PREFIXES
    assert "fix" in CONVENTIONAL_PREFIXES
    assert "docs" in CONVENTIONAL_PREFIXES
    assert "chore" in CONVENTIONAL_PREFIXES
    assert "refactor" in CONVENTIONAL_PREFIXES


def test_conventional_prefixes_minimum_count() -> None:
    assert len(CONVENTIONAL_PREFIXES) >= 10


# ---------------------------------------------------------------------------
# score_commit_message - good messages
# ---------------------------------------------------------------------------


def test_score_good_feat_message() -> None:
    result = score_commit_message("feat: add user authentication system")
    assert result["score"] >= 70
    assert result["grade"] in ("A", "B", "C")


def test_score_good_fix_message() -> None:
    result = score_commit_message("fix: resolve null pointer exception in login")
    assert result["score"] >= 70


def test_score_good_docs_message() -> None:
    result = score_commit_message("docs: update API reference for v2 endpoints")
    assert result["score"] >= 70


def test_score_message_with_body_gets_bonus() -> None:
    msg_no_body = "feat: add search feature"
    msg_with_body = "feat: add search feature\n\nThis adds full-text search using Elasticsearch."
    score_no_body = score_commit_message(msg_no_body)["score"]
    score_with_body = score_commit_message(msg_with_body)["score"]
    assert score_with_body > score_no_body


def test_score_high_result_structure() -> None:
    result = score_commit_message("feat: add user authentication")
    assert "score" in result
    assert "grade" in result
    assert "issues" in result
    assert isinstance(result["score"], int)
    assert isinstance(result["grade"], str)
    assert isinstance(result["issues"], list)


# ---------------------------------------------------------------------------
# score_commit_message - bad messages
# ---------------------------------------------------------------------------


def test_score_generic_fix() -> None:
    result = score_commit_message("fix")
    assert result["score"] < 50
    assert result["grade"] in ("D", "F")


def test_score_generic_update() -> None:
    result = score_commit_message("update")
    assert result["score"] < 50


def test_score_generic_wip() -> None:
    result = score_commit_message("wip")
    assert result["score"] < 50


def test_score_generic_asdf() -> None:
    result = score_commit_message("asdf")
    assert result["score"] < 50


def test_score_too_short_message() -> None:
    result = score_commit_message("bug")
    assert result["score"] < 60
    # Should have a length issue
    has_length_issue = any("short" in issue.lower() or "length" in issue.lower()
                           for issue in result["issues"])
    assert has_length_issue or result["score"] < 40


def test_score_too_long_message() -> None:
    long_msg = "a" * 130
    result = score_commit_message(long_msg)
    assert result["score"] < 70
    has_length_issue = any("long" in issue.lower() for issue in result["issues"])
    assert has_length_issue


def test_score_no_conventional_prefix_has_issue() -> None:
    result = score_commit_message("Added new user authentication feature")
    issues_lower = [i.lower() for i in result["issues"]]
    assert any("conventional" in i or "prefix" in i for i in issues_lower)


def test_score_lowercase_no_prefix_has_cap_issue() -> None:
    result = score_commit_message("added a new file without prefix")
    issues_lower = [i.lower() for i in result["issues"]]
    assert any("capital" in i or "prefix" in i for i in issues_lower)


def test_score_empty_message() -> None:
    result = score_commit_message("")
    assert result["score"] < 40


# ---------------------------------------------------------------------------
# score_commit_message - grade range
# ---------------------------------------------------------------------------


def test_score_range_0_to_100() -> None:
    messages = [
        "feat: add comprehensive user authentication with JWT",
        "fix",
        "wip",
        "docs: add getting started guide",
        "x",
    ]
    for msg in messages:
        result = score_commit_message(msg)
        assert 0 <= result["score"] <= 100


def test_grade_a_for_excellent_message() -> None:
    result = score_commit_message(
        "feat: add OAuth2 integration\n\nSupports GitHub and Google providers."
    )
    assert result["grade"] == "A"


def test_grade_f_for_generic_message() -> None:
    result = score_commit_message("fix")
    assert result["grade"] == "F"


# ---------------------------------------------------------------------------
# _has_conventional_prefix
# ---------------------------------------------------------------------------


def test_has_conventional_prefix_feat() -> None:
    assert _has_conventional_prefix("feat: add feature") is True


def test_has_conventional_prefix_with_scope() -> None:
    assert _has_conventional_prefix("fix(auth): resolve token refresh") is True


def test_has_conventional_prefix_breaking() -> None:
    assert _has_conventional_prefix("feat!: remove deprecated API") is True


def test_has_conventional_prefix_false() -> None:
    assert _has_conventional_prefix("Added some changes") is False


def test_has_conventional_prefix_unknown_prefix() -> None:
    assert _has_conventional_prefix("magic: do something") is False


# ---------------------------------------------------------------------------
# _score_to_grade
# ---------------------------------------------------------------------------


def test_grade_thresholds() -> None:
    assert _score_to_grade(95) == "A"
    assert _score_to_grade(85) == "B"
    assert _score_to_grade(75) == "C"
    assert _score_to_grade(65) == "D"
    assert _score_to_grade(50) == "F"
    assert _score_to_grade(0) == "F"


# ---------------------------------------------------------------------------
# analyze_commit_quality tests
# ---------------------------------------------------------------------------


def test_analyze_commit_quality_structure(quality_repo: str) -> None:
    result = analyze_commit_quality(quality_repo)
    expected_keys = {
        "total_analyzed", "average_score", "average_grade",
        "grade_distribution", "best_commits", "worst_commits",
    }
    assert expected_keys.issubset(set(result.keys()))


def test_analyze_commit_quality_total_analyzed(quality_repo: str) -> None:
    result = analyze_commit_quality(quality_repo)
    assert result["total_analyzed"] == 6


def test_analyze_commit_quality_average_score_range(quality_repo: str) -> None:
    result = analyze_commit_quality(quality_repo)
    assert 0 <= result["average_score"] <= 100


def test_analyze_commit_quality_grade_distribution_keys(quality_repo: str) -> None:
    result = analyze_commit_quality(quality_repo)
    dist = result["grade_distribution"]
    assert set(dist.keys()) == {"A", "B", "C", "D", "F"}


def test_analyze_commit_quality_grade_distribution_sums(quality_repo: str) -> None:
    result = analyze_commit_quality(quality_repo)
    dist = result["grade_distribution"]
    assert sum(dist.values()) == result["total_analyzed"]


def test_analyze_commit_quality_best_commits(quality_repo: str) -> None:
    result = analyze_commit_quality(quality_repo)
    best = result["best_commits"]
    assert len(best) <= 5
    for entry in best:
        assert "hash" in entry
        assert "message" in entry
        assert "score" in entry
        assert "grade" in entry


def test_analyze_commit_quality_worst_commits(quality_repo: str) -> None:
    result = analyze_commit_quality(quality_repo)
    worst = result["worst_commits"]
    assert len(worst) <= 5
    # Worst should have lower scores than best
    if worst and result["best_commits"]:
        avg_worst = sum(e["score"] for e in worst) / len(worst)
        avg_best = sum(e["score"] for e in result["best_commits"]) / len(result["best_commits"])
        assert avg_worst <= avg_best


def test_analyze_commit_quality_best_scores_descending(quality_repo: str) -> None:
    result = analyze_commit_quality(quality_repo)
    best_scores = [e["score"] for e in result["best_commits"]]
    assert best_scores == sorted(best_scores, reverse=True)


def test_analyze_commit_quality_empty_repo(tmp_path: Path) -> None:
    repo = tmp_path / "empty"
    repo.mkdir()
    _git(["init"], repo)
    result = analyze_commit_quality(str(repo))
    assert result["total_analyzed"] == 0
    assert result["average_score"] == 0.0
    assert result["average_grade"] == "F"


def test_analyze_commit_quality_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        analyze_commit_quality(str(tmp_path))


def test_analyze_commit_quality_generic_messages_score_low(quality_repo: str) -> None:
    result = analyze_commit_quality(quality_repo)
    # "wip", "fix", "update" messages should appear in worst commits
    worst_messages = [e["message"] for e in result["worst_commits"]]
    generic = {"fix", "wip", "update"}
    assert any(m.lower() in generic for m in worst_messages)
