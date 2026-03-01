"""Git clone and log parsing utilities.

Handles cloning public repos and extracting structured commit data
with author info, dates, messages, and file change statistics.
"""

from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional


def clone_repo(url: str, target_dir: str) -> str:
    """Clone a public GitHub repository to a local directory.

    Args:
        url: Public git repository URL (https or git protocol).
        target_dir: Local directory path to clone into.

    Returns:
        Absolute path to the cloned repository.

    Raises:
        ValueError: If the URL is empty or clearly invalid.
        RuntimeError: If git clone fails (network error, not found, etc.).
    """
    if not url or not url.strip():
        raise ValueError("Repository URL cannot be empty.")

    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("git@")):
        raise ValueError(f"Invalid repository URL: {url!r}")

    target_path = Path(target_dir).resolve()
    target_path.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        ["git", "clone", "--", url, str(target_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(f"git clone failed for {url!r}: {stderr}")

    return str(target_path)


def _run_git(args: list[str], repo_path: str) -> subprocess.CompletedProcess:
    """Run a git command inside a repository directory.

    Args:
        args: List of git subcommand arguments (e.g. ["log", "--oneline"]).
        repo_path: Absolute path to the local git repository.

    Returns:
        CompletedProcess with stdout/stderr captured.

    Raises:
        RuntimeError: If the path is not a git repository or git fails.
    """
    if not Path(repo_path).joinpath(".git").exists():
        raise RuntimeError(f"Not a git repository: {repo_path!r}")

    return subprocess.run(
        ["git", "-C", repo_path] + args,
        capture_output=True,
        text=True,
    )


def parse_git_log(repo_path: str) -> list[dict]:
    """Parse full commit history from a local git repository.

    Uses a record-separator format to reliably split commits, then
    fetches numstat data to get per-commit file change statistics.

    Args:
        repo_path: Absolute path to the local git repository.

    Returns:
        List of commit dicts, newest first, each containing:
            hash (str): Full 40-char commit SHA.
            author_name (str): Commit author display name.
            author_email (str): Commit author email address.
            date (str): ISO 8601 date string (YYYY-MM-DDTHH:MM:SS+HH:MM).
            message (str): Full commit message subject line.
            files_changed (int): Number of files modified in the commit.
            insertions (int): Total lines added across all files.
            deletions (int): Total lines removed across all files.

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    SEP = "\x1e"  # ASCII record separator - unlikely in commit messages

    log_result = _run_git(
        [
            "log",
            f"--pretty=format:{SEP}%H%x00%an%x00%ae%x00%aI%x00%s",
            "--numstat",
        ],
        repo_path,
    )

    if log_result.returncode != 0:
        raise RuntimeError(f"git log failed: {log_result.stderr.strip()}")

    output = log_result.stdout
    if not output.strip():
        return []

    # Split on record separator to get per-commit blocks
    raw_blocks = output.split(SEP)
    commits: list[dict] = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.splitlines()
        # First line is the header fields joined by null bytes
        header_line = lines[0]
        fields = header_line.split("\x00")
        if len(fields) < 5:
            continue

        commit_hash, author_name, author_email, date_str, message = (
            fields[0].strip(),
            fields[1].strip(),
            fields[2].strip(),
            fields[3].strip(),
            fields[4].strip(),
        )

        # Remaining non-empty lines are numstat rows: added\tdeleted\tfilename
        files_changed = 0
        insertions = 0
        deletions = 0

        for stat_line in lines[1:]:
            stat_line = stat_line.strip()
            if not stat_line:
                continue
            parts = stat_line.split("\t")
            if len(parts) < 3:
                continue
            added_str, deleted_str = parts[0], parts[1]
            files_changed += 1
            # Binary files show "-" instead of a number
            if added_str.isdigit():
                insertions += int(added_str)
            if deleted_str.isdigit():
                deletions += int(deleted_str)

        commits.append(
            {
                "hash": commit_hash,
                "author_name": author_name,
                "author_email": author_email,
                "date": date_str,
                "message": message,
                "files_changed": files_changed,
                "insertions": insertions,
                "deletions": deletions,
            }
        )

    return commits


def get_repo_info(repo_path: str) -> dict:
    """Return high-level summary statistics for a git repository.

    Args:
        repo_path: Absolute path to the local git repository.

    Returns:
        Dict containing:
            name (str): Repository directory name.
            default_branch (str): Current HEAD branch name.
            total_commits (int): Total number of commits on the current branch.
            first_commit_date (str | None): ISO date of the earliest commit.
            latest_commit_date (str | None): ISO date of the most recent commit.
            total_authors (int): Number of unique author emails.

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    name = Path(repo_path).name

    # Current branch
    branch_result = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_path)
    default_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

    commits = parse_git_log(repo_path)
    total_commits = len(commits)

    if commits:
        # parse_git_log returns newest first
        latest_commit_date: Optional[str] = commits[0]["date"]
        first_commit_date: Optional[str] = commits[-1]["date"]
    else:
        latest_commit_date = None
        first_commit_date = None

    unique_authors = {c["author_email"] for c in commits if c["author_email"]}
    total_authors = len(unique_authors)

    return {
        "name": name,
        "default_branch": default_branch,
        "total_commits": total_commits,
        "first_commit_date": first_commit_date,
        "latest_commit_date": latest_commit_date,
        "total_authors": total_authors,
    }
