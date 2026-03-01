"""Comprehensive tests for the clone module.

Uses gunnargray-dev/reposcape itself as a real tiny repo fixture.
All network-dependent tests clone the repo once into a session-scoped
temporary directory to avoid repeated clones.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from src.clone import clone_repo, get_repo_info, parse_git_log


# ---------------------------------------------------------------------------
# Session-scoped real clone (used for integration tests)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def cloned_repo(tmp_path_factory) -> str:
    """Clone gunnargray-dev/reposcape once for the whole test session."""
    target = tmp_path_factory.mktemp("reposcape_clone")
    path = clone_repo("https://github.com/gunnargray-dev/reposcape", str(target))
    return path


# ---------------------------------------------------------------------------
# clone_repo tests
# ---------------------------------------------------------------------------


class TestCloneRepo:
    def test_clone_returns_string(self, cloned_repo):
        """clone_repo should return a string path."""
        assert isinstance(cloned_repo, str)

    def test_clone_path_exists(self, cloned_repo):
        """Cloned path should exist on disk."""
        assert Path(cloned_repo).exists()

    def test_clone_path_is_git_repo(self, cloned_repo):
        """Cloned directory must contain a .git folder."""
        assert (Path(cloned_repo) / ".git").exists()

    def test_clone_contains_readme(self, cloned_repo):
        """Cloned repo should contain README.md."""
        assert (Path(cloned_repo) / "README.md").exists()

    def test_clone_empty_url_raises(self, tmp_path):
        """Empty URL should raise ValueError."""
        with pytest.raises(ValueError):
            clone_repo("", str(tmp_path / "out"))

    def test_clone_whitespace_url_raises(self, tmp_path):
        """Whitespace-only URL should raise ValueError."""
        with pytest.raises(ValueError):
            clone_repo("   ", str(tmp_path / "out"))

    def test_clone_invalid_scheme_raises(self, tmp_path):
        """URL without http(s) or git@ prefix should raise ValueError."""
        with pytest.raises(ValueError):
            clone_repo("ftp://github.com/owner/repo", str(tmp_path / "out"))

    def test_clone_nonexistent_repo_raises(self, tmp_path):
        """Cloning a repo that doesn't exist should raise RuntimeError."""
        with pytest.raises(RuntimeError):
            clone_repo(
                "https://github.com/gunnargray-dev/nonexistent-repo-xyz123",
                str(tmp_path / "out"),
            )

    def test_clone_creates_target_dir(self, tmp_path):
        """clone_repo should create nested target directories if needed."""
        nested = tmp_path / "a" / "b" / "c"
        path = clone_repo(
            "https://github.com/gunnargray-dev/reposcape", str(nested)
        )
        assert Path(path).exists()

    def test_clone_returns_absolute_path(self, tmp_path):
        """Returned path should be absolute."""
        path = clone_repo(
            "https://github.com/gunnargray-dev/reposcape",
            str(tmp_path / "abs_test"),
        )
        assert Path(path).is_absolute()


# ---------------------------------------------------------------------------
# parse_git_log tests
# ---------------------------------------------------------------------------


class TestParseGitLog:
    def test_returns_list(self, cloned_repo):
        """parse_git_log should return a list."""
        result = parse_git_log(cloned_repo)
        assert isinstance(result, list)

    def test_list_not_empty(self, cloned_repo):
        """At least one commit should be present."""
        result = parse_git_log(cloned_repo)
        assert len(result) > 0

    def test_commit_has_required_keys(self, cloned_repo):
        """Each commit dict must have all required keys."""
        required = {
            "hash",
            "author_name",
            "author_email",
            "date",
            "message",
            "files_changed",
            "insertions",
            "deletions",
        }
        for commit in parse_git_log(cloned_repo):
            assert required.issubset(commit.keys()), f"Missing keys in: {commit}"

    def test_hash_is_40_chars(self, cloned_repo):
        """Git commit hashes should be 40 hex characters."""
        for commit in parse_git_log(cloned_repo):
            assert len(commit["hash"]) == 40
            assert all(c in "0123456789abcdef" for c in commit["hash"])

    def test_date_is_iso_format(self, cloned_repo):
        """Commit dates should contain a 'T' separator (ISO 8601)."""
        for commit in parse_git_log(cloned_repo):
            assert "T" in commit["date"], f"Not ISO date: {commit['date']}"

    def test_numeric_stats_are_ints(self, cloned_repo):
        """files_changed, insertions, deletions must be integers."""
        for commit in parse_git_log(cloned_repo):
            assert isinstance(commit["files_changed"], int)
            assert isinstance(commit["insertions"], int)
            assert isinstance(commit["deletions"], int)

    def test_numeric_stats_non_negative(self, cloned_repo):
        """Numeric stats must be non-negative."""
        for commit in parse_git_log(cloned_repo):
            assert commit["files_changed"] >= 0
            assert commit["insertions"] >= 0
            assert commit["deletions"] >= 0

    def test_invalid_repo_raises(self, tmp_path):
        """parse_git_log on a non-git directory should raise RuntimeError."""
        with pytest.raises(RuntimeError):
            parse_git_log(str(tmp_path))

    def test_message_is_string(self, cloned_repo):
        """Commit messages should be non-empty strings."""
        for commit in parse_git_log(cloned_repo):
            assert isinstance(commit["message"], str)
            assert len(commit["message"]) > 0

    def test_author_email_contains_at(self, cloned_repo):
        """Author emails should contain '@'."""
        for commit in parse_git_log(cloned_repo):
            if commit["author_email"]:
                assert "@" in commit["author_email"]


# ---------------------------------------------------------------------------
# get_repo_info tests
# ---------------------------------------------------------------------------


class TestGetRepoInfo:
    def test_returns_dict(self, cloned_repo):
        """get_repo_info should return a dict."""
        assert isinstance(get_repo_info(cloned_repo), dict)

    def test_has_required_keys(self, cloned_repo):
        """Returned dict must contain all required keys."""
        required = {
            "name",
            "default_branch",
            "total_commits",
            "first_commit_date",
            "latest_commit_date",
            "total_authors",
        }
        info = get_repo_info(cloned_repo)
        assert required.issubset(info.keys())

    def test_name_matches_dir(self, cloned_repo):
        """name field should match the repository directory name."""
        info = get_repo_info(cloned_repo)
        assert info["name"] == Path(cloned_repo).name

    def test_total_commits_positive(self, cloned_repo):
        """total_commits should be a positive integer."""
        info = get_repo_info(cloned_repo)
        assert isinstance(info["total_commits"], int)
        assert info["total_commits"] > 0

    def test_total_authors_positive(self, cloned_repo):
        """total_authors should be at least 1."""
        info = get_repo_info(cloned_repo)
        assert info["total_authors"] >= 1

    def test_first_and_latest_dates_set(self, cloned_repo):
        """first_commit_date and latest_commit_date should not be None."""
        info = get_repo_info(cloned_repo)
        assert info["first_commit_date"] is not None
        assert info["latest_commit_date"] is not None

    def test_invalid_repo_raises(self, tmp_path):
        """get_repo_info on a non-git directory should raise RuntimeError."""
        with pytest.raises(RuntimeError):
            get_repo_info(str(tmp_path))
