"""Commit timeline and repository evolution analytics.

Generates data for animated timelines of repo evolution, including commit
groupings by time bucket, milestone detection, cumulative growth curves,
and file churn metrics.
"""

from __future__ import annotations

import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .clone import parse_git_log, _run_git


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_commit_timeline(repo_path: str, bucket: str = "week") -> list[dict]:
    """Group commits by time bucket for timeline visualization.

    Args:
        repo_path: Absolute path to the local git repository.
        bucket: Time granularity — "day", "week", or "month".

    Returns:
        List of dicts ordered by period ascending, each containing:
            period (str): Period label (YYYY-MM-DD, YYYY-WXX, or YYYY-MM).
            commits (int): Number of commits in the period.
            authors (int): Number of unique authors in the period.
            lines_added (int): Total lines inserted.
            lines_deleted (int): Total lines deleted.
            net_lines (int): lines_added - lines_deleted.
            files_changed (int): Total file change events.

    Raises:
        ValueError: If bucket is not "day", "week", or "month".
        RuntimeError: If repo_path is not a valid git repository.
    """
    valid_buckets = ("day", "week", "month")
    if bucket not in valid_buckets:
        raise ValueError(f"bucket must be one of {valid_buckets}, got {bucket!r}")

    try:
        commits = parse_git_log(repo_path)
    except RuntimeError as exc:
        if _is_empty_repo_error(exc):
            return []
        raise
    if not commits:
        return []

    buckets: dict[str, dict] = {}

    for commit in commits:
        date_str = commit.get("date", "")
        if not date_str:
            continue
        try:
            dt = _parse_iso_datetime(date_str)
        except (ValueError, TypeError):
            continue

        period = _format_period(dt, bucket)

        if period not in buckets:
            buckets[period] = {
                "period": period,
                "commits": 0,
                "authors": set(),
                "lines_added": 0,
                "lines_deleted": 0,
                "files_changed": 0,
            }

        b = buckets[period]
        b["commits"] += 1
        b["authors"].add(commit.get("author_email", ""))
        b["lines_added"] += commit.get("insertions", 0)
        b["lines_deleted"] += commit.get("deletions", 0)
        b["files_changed"] += commit.get("files_changed", 0)

    result = []
    for period in sorted(buckets.keys()):
        b = buckets[period]
        result.append({
            "period": b["period"],
            "commits": b["commits"],
            "authors": len(b["authors"]),
            "lines_added": b["lines_added"],
            "lines_deleted": b["lines_deleted"],
            "net_lines": b["lines_added"] - b["lines_deleted"],
            "files_changed": b["files_changed"],
        })

    return result


def detect_milestones(repo_path: str) -> list[dict]:
    """Identify significant events in repository history.

    Detects: first commit, large commits (>500 lines), merge commits,
    tagged releases, and days with unusually high activity (>2 std devs
    above mean).

    Args:
        repo_path: Absolute path to the local git repository.

    Returns:
        List of milestone dicts sorted by date ascending, each containing:
            date (str): ISO date string of the event.
            type (str): "first_commit", "large_commit", "merge_commit",
                "release_tag", or "high_activity_day".
            description (str): Human-readable description.
            details (dict): Type-specific metadata.

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    try:
        commits = parse_git_log(repo_path)
    except RuntimeError as exc:
        if _is_empty_repo_error(exc):
            return []
        raise
    if not commits:
        return []

    milestones: list[dict] = []
    commit_map = {c["hash"]: c for c in commits}

    # First commit
    first = commits[-1]
    milestones.append({
        "date": first["date"][:10],
        "type": "first_commit",
        "description": "Repository created",
        "details": {
            "hash": first["hash"],
            "author": first["author_name"],
            "message": first["message"],
        },
    })

    # Large commits (>500 lines changed)
    for commit in commits:
        total_lines = commit.get("insertions", 0) + commit.get("deletions", 0)
        if total_lines > 500:
            milestones.append({
                "date": commit["date"][:10],
                "type": "large_commit",
                "description": f"Large commit: {total_lines} lines changed",
                "details": {
                    "hash": commit["hash"],
                    "author": commit["author_name"],
                    "message": commit["message"],
                    "lines_changed": total_lines,
                },
            })

    # Merge commits
    merge_hashes = _get_merge_commit_hashes(repo_path)
    for h in merge_hashes:
        if h in commit_map:
            c = commit_map[h]
            milestones.append({
                "date": c["date"][:10],
                "type": "merge_commit",
                "description": f"Merge: {c['message'][:60]}",
                "details": {
                    "hash": h,
                    "author": c["author_name"],
                    "message": c["message"],
                },
            })

    # Release tags
    tags = _get_tags(repo_path)
    for tag_name, tag_date, tag_hash in tags:
        milestones.append({
            "date": tag_date[:10],
            "type": "release_tag",
            "description": f"Release: {tag_name}",
            "details": {
                "tag": tag_name,
                "hash": tag_hash,
            },
        })

    # High activity days (>2 std devs above mean)
    day_counts: Counter = Counter()
    for commit in commits:
        if commit.get("date"):
            day_counts[commit["date"][:10]] += 1

    if len(day_counts) >= 3:
        counts = list(day_counts.values())
        mean = statistics.mean(counts)
        stdev = statistics.stdev(counts) if len(counts) > 1 else 0
        threshold = mean + 2 * stdev
        for day, count in day_counts.items():
            if stdev > 0 and count > threshold:
                milestones.append({
                    "date": day,
                    "type": "high_activity_day",
                    "description": f"High activity: {count} commits in one day",
                    "details": {
                        "commits": count,
                        "mean_daily_commits": round(mean, 2),
                        "threshold": round(threshold, 2),
                    },
                })

    return sorted(milestones, key=lambda m: m["date"])


def get_growth_curve(repo_path: str) -> list[dict]:
    """Return cumulative LOC, file count, and author count over time.

    Samples at weekly intervals by replaying the commit history.

    Args:
        repo_path: Absolute path to the local git repository.

    Returns:
        List of dicts ordered by date ascending, each containing:
            date (str): ISO date string (YYYY-MM-DD) of sample point.
            total_lines (int): Cumulative net lines at this point.
            total_files (int): Approximate distinct files touched up to this date.
            total_authors (int): Cumulative unique authors up to this date.

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    try:
        commits = parse_git_log(repo_path)
    except RuntimeError as exc:
        if _is_empty_repo_error(exc):
            return []
        raise
    if not commits:
        return []

    ordered = list(reversed(commits))
    first_date = _parse_iso_datetime(ordered[0]["date"])
    last_date = _parse_iso_datetime(ordered[-1]["date"])

    sample_dates = _get_weekly_dates(first_date, last_date)
    if not sample_dates:
        sample_dates = [first_date.date()]

    cumulative_lines = 0
    cumulative_files: set = set()
    cumulative_authors: set = set()
    commit_idx = 0

    result = []
    for sample_date in sample_dates:
        while commit_idx < len(ordered):
            try:
                commit_date = _parse_iso_datetime(ordered[commit_idx]["date"]).date()
            except (ValueError, TypeError):
                commit_idx += 1
                continue
            if commit_date <= sample_date:
                c = ordered[commit_idx]
                cumulative_lines += c.get("insertions", 0) - c.get("deletions", 0)
                cumulative_authors.add(c.get("author_email", ""))
                commit_idx += 1
            else:
                break

        result.append({
            "date": sample_date.isoformat(),
            "total_lines": max(0, cumulative_lines),
            "total_files": len(cumulative_files) if cumulative_files else commit_idx,
            "total_authors": len(cumulative_authors),
        })

    return result


def get_file_churn(repo_path: str, top_n: int = 20) -> list[dict]:
    """Find the most frequently changed files in the repository.

    High churn indicates potential instability or hot spots.

    Args:
        repo_path: Absolute path to the local git repository.
        top_n: Maximum number of files to return.

    Returns:
        List of dicts sorted by changes descending, each containing:
            path (str): Relative file path.
            changes (int): Total commit count touching this file.
            authors (int): Number of unique authors who changed this file.
            last_changed (str): ISO date string of most recent change.

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    if not Path(repo_path).joinpath(".git").exists():
        raise RuntimeError(f"Not a git repository: {repo_path!r}")

    result = _run_git(
        ["log", "--pretty=format:%ae%x00%aI", "--name-only", "--diff-filter=ACDMR"],
        repo_path,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []

    file_changes: Counter = Counter()
    file_authors: dict[str, set] = defaultdict(set)
    file_last_changed: dict[str, str] = {}

    current_email = ""
    current_date = ""

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if "\x00" in line:
            parts = line.split("\x00", 1)
            current_email = parts[0]
            current_date = parts[1][:10] if len(parts) > 1 else ""
        else:
            file_changes[line] += 1
            if current_email:
                file_authors[line].add(current_email)
            if current_date:
                if line not in file_last_changed:
                    file_last_changed[line] = current_date

    top_files = file_changes.most_common(top_n)
    return [
        {
            "path": path,
            "changes": count,
            "authors": len(file_authors.get(path, set())),
            "last_changed": file_last_changed.get(path, ""),
        }
        for path, count in top_files
    ]


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _parse_iso_datetime(date_str: str) -> datetime:
    """Parse ISO 8601 datetime string to a datetime object.

    Args:
        date_str: ISO 8601 date string, possibly with timezone offset.

    Returns:
        datetime object (timezone-naive, in commit's local time).
    """
    clean = re.sub(r"[+-]\d{2}:\d{2}$", "", date_str.strip())
    clean = clean.replace("T", " ").rstrip("Z")
    try:
        return datetime.strptime(clean, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.strptime(clean[:10], "%Y-%m-%d")


def _format_period(dt: datetime, bucket: str) -> str:
    """Format a datetime into a period label string.

    Args:
        dt: The datetime to format.
        bucket: "day", "week", or "month".

    Returns:
        Period label string.
    """
    if bucket == "day":
        return dt.strftime("%Y-%m-%d")
    if bucket == "week":
        return f"{dt.year}-W{dt.strftime('%W').zfill(2)}"
    if bucket == "month":
        return dt.strftime("%Y-%m")
    return dt.strftime("%Y-%m-%d")


def _get_weekly_dates(start: datetime, end: datetime) -> list:
    """Return a list of date objects spaced weekly from start to end.

    Args:
        start: Start datetime.
        end: End datetime.

    Returns:
        List of date objects at weekly intervals, always including end.date().
    """
    from datetime import date
    dates = []
    current = start.date()
    end_date = end.date()
    while current <= end_date:
        dates.append(current)
        current += timedelta(weeks=1)
    if not dates or dates[-1] < end_date:
        dates.append(end_date)
    return dates


def _get_merge_commit_hashes(repo_path: str) -> list[str]:
    """Return list of merge commit hashes from git log.

    Args:
        repo_path: Path to git repository.

    Returns:
        List of commit SHA strings for merge commits.
    """
    result = _run_git(
        ["log", "--merges", "--pretty=format:%H"],
        repo_path,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    return [h.strip() for h in result.stdout.splitlines() if h.strip()]


def _get_tags(repo_path: str) -> list[tuple[str, str, str]]:
    """Return list of (tag_name, date, hash) tuples for tags.

    Args:
        repo_path: Path to git repository.

    Returns:
        List of (tag_name, date_str, hash_str) tuples.
    """
    result = _run_git(
        ["log", "--tags", "--simplify-by-decoration",
         "--pretty=format:%D%x00%aI%x00%H"],
        repo_path,
    )
    tags = []
    if result.returncode != 0 or not result.stdout.strip():
        return tags

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or "\x00" not in line:
            continue
        parts = line.split("\x00")
        if len(parts) < 3:
            continue
        decorations, date_str, commit_hash = parts[0], parts[1], parts[2]
        for token in decorations.split(","):
            token = token.strip()
            if token.startswith("tag: "):
                tag_name = token[5:].strip()
                tags.append((tag_name, date_str, commit_hash))
    return tags


def _is_empty_repo_error(exc: Exception) -> bool:
    """Return True if the exception indicates an empty repository.

    Args:
        exc: The exception to check.

    Returns:
        True if it looks like an empty-repo error.
    """
    msg = str(exc).lower()
    return "does not have any commits" in msg or "no commits" in msg
