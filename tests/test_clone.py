"""Tests for the clone module.

Uses the shared local_git_repo fixture (no network required).
Integration tests that clone from GitHub are marked with @pytest.mark.integration.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.clone import clone_repo, get_repo_info, parse_git_log


# ---------------------------------------------------------------------------
# clone_repo tests (validation only — no network)
# ---------------------------------------------------------------------------


class TestCloneRepoValidation:
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


# ---------------------------------------------------------------------------
# parse_git_log tests (using local_git_repo fixture)
# ---------------------------------------------------------------------------


class TestParseGitLog:
    def test_returns_list(self, local_git_repo):
        """parse_git_log should return a list."""
        result = parse_git_log(local_git_repo)
        assert isinstance(result, list)

    def test_list_not_empty(self, local_git_repo):
        """At least one commit should be present."""
        result = parse_git_log(local_git_repo)
        assert len(result) > 0

    def test_expected_commit_count(self, local_git_repo):
        """Local repo has 5 commits."""
        result = parse_git_log(local_git_repo)
        assert len(result) == 5

    def test_commit_has_required_keys(self, local_git_repo):
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
        for commit in parse_git_log(local_git_repo):
            assert required.issubset(commit.keys()), f"Missing keys in: {commit}"

    def test_hash_is_40_chars(self, local_git_repo):
        """Git commit hashes should be 40 hex characters."""
        for commit in parse_git_log(local_git_repo):
            assert len(commit["hash"]) == 40
            assert all(c in "0123456789abcdef" for c in commit["hash"])

    def test_date_is_iso_format(self, local_git_repo):
        """Commit dates should contain a 'T' separator (ISO 8601)."""
        for commit in parse_git_log(local_git_repo):
            assert "T" in commit["date"], f"Not ISO date: {commit['date']}"

    def test_numeric_stats_are_ints(self, local_git_repo):
        """files_changed, insertions, deletions must be integers."""
        for commit in parse_git_log(local_git_repo):
            assert isinstance(commit["files_changed"], int)
            assert isinstance(commit["insertions"], int)
            assert isinstance(commit["deletions"], int)

    def test_numeric_stats_non_negative(self, local_git_repo):
        """Numeric stats must be non-negative."""
        for commit in parse_git_log(local_git_repo):
            assert commit["files_changed"] >= 0
            assert commit["insertions"] >= 0
            assert commit["deletions"] >= 0

    def test_message_is_string(self, local_git_repo):
        """Commit messages should be non-empty strings."""
        for commit in parse_git_log(local_git_repo):
            assert isinstance(commit["message"], str)
            assert len(commit["message"]) > 0

    def test_author_email_contains_at(self, local_git_repo):
        """Author emails should contain '@'."""
        for commit in parse_git_log(local_git_repo):
            if commit["author_email"]:
                assert "@" in commit["author_email"]

    def test_invalid_repo_raises(self, tmp_path):
        """parse_git_log on a non-git directory should raise RuntimeError."""
        with pytest.raises(RuntimeError):
            parse_git_log(str(tmp_path))

    def test_multiple_authors(self, local_git_repo):
        """Local repo has commits from both Alice and Bob."""
        authors = {c["author_name"] for c in parse_git_log(local_git_repo)}
        assert "Alice" in authors
        assert "Bob" in authors


# ---------------------------------------------------------------------------
# get_repo_info tests
# ---------------------------------------------------------------------------


class TestGetRepoInfo:
    def test_returns_dict(self, local_git_repo):
        """get_repo_info should return a dict."""
        assert isinstance(get_repo_info(local_git_repo), dict)

    def test_has_required_keys(self, local_git_repo):
        """Returned dict must contain all required keys."""
        required = {
            "name",
            "default_branch",
            "total_commits",
            "first_commit_date",
            "latest_commit_date",
            "total_authors",
        }
        info = get_repo_info(local_git_repo)
        assert required.issubset(info.keys())

    def test_total_commits_positive(self, local_git_repo):
        """total_commits should be a positive integer."""
        info = get_repo_info(local_git_repo)
        assert isinstance(info["total_commits"], int)
        assert info["total_commits"] == 5

    def test_total_authors_correct(self, local_git_repo):
        """total_authors should be 2 (Alice and Bob)."""
        info = get_repo_info(local_git_repo)
        assert info["total_authors"] == 2

    def test_first_and_latest_dates_set(self, local_git_repo):
        """first_commit_date and latest_commit_date should not be None."""
        info = get_repo_info(local_git_repo)
        assert info["first_commit_date"] is not None
        assert info["latest_commit_date"] is not None

    def test_invalid_repo_raises(self, tmp_path):
        """get_repo_info on a non-git directory should raise RuntimeError."""
        with pytest.raises(RuntimeError):
            get_repo_info(str(tmp_path))


# ---------------------------------------------------------------------------
# Integration tests (require network — skipped by default)
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestCloneIntegration:
    @pytest.fixture(scope="class")
    def cloned_repo(self, tmp_path_factory) -> str:
        target = tmp_path_factory.mktemp("reposcape_clone")
        path = clone_repo(
            "https://github.com/gunnargray-dev/reposcape", str(target)
        )
        return path

    def test_clone_returns_string(self, cloned_repo):
        assert isinstance(cloned_repo, str)

    def test_clone_path_exists(self, cloned_repo):
        assert Path(cloned_repo).exists()

    def test_clone_path_is_git_repo(self, cloned_repo):
        assert (Path(cloned_repo) / ".git").exists()

    def test_parse_log_on_real_repo(self, cloned_repo):
        result = parse_git_log(cloned_repo)
        assert len(result) > 5
