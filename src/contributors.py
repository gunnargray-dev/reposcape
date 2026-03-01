"""Contributor statistics engine.

Analyzes per-author commit activity, file ownership, collaboration patterns,
and temporal activity distributions for repository visualization.
"""

from __future__ import annotations

import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from .clone import parse_git_log, _run_git


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def analyze_contributors(repo_path: str) -> dict:
    """Analyze per-author commit statistics for a repository.

    Parses git log to extract total commits, lines added/deleted, date range,
    active days, and files touched per author. Sorted by total commits descending.

    Args:
        repo_path: Absolute path to the local git repository.

    Returns:
        Dict with key ``authors`` (list of author stat dicts, sorted by
        total_commits descending) and key ``total_commits`` (int). Each author
        dict contains:
            author_name (str): Display name.
            author_email (str): Email address.
            total_commits (int): Commit count.
            insertions (int): Total lines added.
            deletions (int): Total lines removed.
            first_commit_date (str | None): ISO date of earliest commit.
            last_commit_date (str | None): ISO date of most recent commit.
            active_days (int): Number of distinct calendar days with a commit.
            files_touched (int): Number of distinct files modified.

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    try:
        commits = parse_git_log(repo_path)
    except RuntimeError as exc:
        if "does not have any commits" in str(exc) or "no commits" in str(exc).lower():
            return {"authors": [], "total_commits": 0}
        raise
    if not commits:
        return {"authors": [], "total_commits": 0}

    # Aggregate stats keyed by email
    stats: dict[str, dict] = {}
    file_sets: dict[str, set] = defaultdict(set)
    active_days: dict[str, set] = defaultdict(set)

    for commit in commits:
        email = commit["author_email"]
        name = commit["author_name"]
        date_str = commit["date"]

        if email not in stats:
            stats[email] = {
                "author_name": name,
                "author_email": email,
                "total_commits": 0,
                "insertions": 0,
                "deletions": 0,
                "first_commit_date": date_str,
                "last_commit_date": date_str,
                "active_days": 0,
                "files_touched": 0,
            }

        s = stats[email]
        s["total_commits"] += 1
        s["insertions"] += commit.get("insertions", 0)
        s["deletions"] += commit.get("deletions", 0)

        # Track date range (parse_git_log returns newest first)
        if date_str and (s["first_commit_date"] is None or date_str < s["first_commit_date"]):
            s["first_commit_date"] = date_str
        if date_str and (s["last_commit_date"] is None or date_str > s["last_commit_date"]):
            s["last_commit_date"] = date_str

        # Collect active days
        if date_str:
            day = date_str[:10]
            active_days[email].add(day)

    # Gather files touched per author via git log --name-only
    _collect_files_touched(repo_path, stats, file_sets)

    # Finalize counts
    for email, s in stats.items():
        s["active_days"] = len(active_days[email])
        s["files_touched"] = len(file_sets[email])

    authors = sorted(stats.values(), key=lambda x: x["total_commits"], reverse=True)
    return {"authors": authors, "total_commits": len(commits)}


def get_author_timeline(repo_path: str) -> list[dict]:
    """Build per-author commit counts grouped by date.

    Args:
        repo_path: Absolute path to the local git repository.

    Returns:
        List of dicts, one per author, each containing:
            author_name (str): Display name.
            author_email (str): Email address.
            timeline (list[dict]): Sorted list of {date (str YYYY-MM-DD),
                commits (int)} entries.

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    try:
        commits = parse_git_log(repo_path)
    except RuntimeError as exc:
        if "does not have any commits" in str(exc) or "no commits" in str(exc).lower():
            return []
        raise
    if not commits:
        return []

    # {email: {date_str: count}}
    author_days: dict[str, Counter] = defaultdict(Counter)
    author_names: dict[str, str] = {}

    for commit in commits:
        email = commit["author_email"]
        author_names[email] = commit["author_name"]
        if commit["date"]:
            day = commit["date"][:10]
            author_days[email][day] += 1

    result = []
    for email, day_counts in author_days.items():
        timeline = [
            {"date": day, "commits": count}
            for day, count in sorted(day_counts.items())
        ]
        result.append(
            {
                "author_name": author_names[email],
                "author_email": email,
                "timeline": timeline,
            }
        )

    return sorted(result, key=lambda x: sum(e["commits"] for e in x["timeline"]), reverse=True)


def get_author_file_ownership(repo_path: str) -> dict:
    """Map each file to its primary author and ownership percentage.

    For each file, the primary author is the one with the most commits
    touching that file.

    Args:
        repo_path: Absolute path to the local git repository.

    Returns:
        Dict mapping relative file path (str) to:
            primary_author (str): Email of author with most commits to file.
            primary_author_name (str): Display name of primary author.
            ownership_pct (float): Percentage of commits attributed to primary author.
            total_commits (int): Total commits that touched this file.

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    if not Path(repo_path).joinpath(".git").exists():
        raise RuntimeError(f"Not a git repository: {repo_path!r}")

    result = _run_git(
        ["log", "--pretty=format:%ae%x00%an", "--name-only", "--diff-filter=ACDMR"],
        repo_path,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return {}

    file_author_counts: dict[str, Counter] = defaultdict(Counter)
    file_author_names: dict[str, dict] = defaultdict(dict)

    current_email = ""
    current_name = ""

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if "\x00" in line:
            parts = line.split("\x00", 1)
            current_email = parts[0]
            current_name = parts[1] if len(parts) > 1 else ""
        else:
            if current_email:
                file_author_counts[line][current_email] += 1
                file_author_names[line][current_email] = current_name

    ownership: dict = {}
    for filepath, counter in file_author_counts.items():
        total = sum(counter.values())
        primary_email, primary_count = counter.most_common(1)[0]
        ownership[filepath] = {
            "primary_author": primary_email,
            "primary_author_name": file_author_names[filepath].get(primary_email, ""),
            "ownership_pct": round(primary_count / total * 100, 1) if total > 0 else 0.0,
            "total_commits": total,
        }

    return ownership


def get_collaboration_pairs(repo_path: str) -> list[dict]:
    """Find pairs of authors who co-edit the same files.

    Args:
        repo_path: Absolute path to the local git repository.

    Returns:
        List of dicts, sorted by overlap_count descending, each containing:
            author_a (str): Email of first author.
            author_b (str): Email of second author.
            overlap_count (int): Number of files both authors have touched.
            shared_files (list[str]): File paths both authors edited.

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    ownership = get_author_file_ownership(repo_path)

    # Build {author_email: set of files touched}
    author_files: dict[str, set] = defaultdict(set)
    for filepath, info in ownership.items():
        author_files[info["primary_author"]].add(filepath)

    # Also gather all files per author from git log
    result = _run_git(
        ["log", "--pretty=format:%ae", "--name-only", "--diff-filter=ACDMR"],
        repo_path,
    )
    if result.returncode == 0 and result.stdout.strip():
        current_email = ""
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            if "@" in line and "\t" not in line and "/" not in line and "." in line.split("@")[-1]:
                # Looks like an email line
                current_email = line
            elif current_email:
                author_files[current_email].add(line)

    authors = list(author_files.keys())
    pairs: list[dict] = []

    for i in range(len(authors)):
        for j in range(i + 1, len(authors)):
            a, b = authors[i], authors[j]
            shared = author_files[a] & author_files[b]
            if shared:
                pairs.append(
                    {
                        "author_a": a,
                        "author_b": b,
                        "overlap_count": len(shared),
                        "shared_files": sorted(shared),
                    }
                )

    return sorted(pairs, key=lambda x: x["overlap_count"], reverse=True)


def get_activity_periods(repo_path: str) -> dict:
    """Identify each author's most active hour of day and day of week.

    Args:
        repo_path: Absolute path to the local git repository.

    Returns:
        Dict mapping author email to:
            author_name (str): Display name.
            peak_hour (int): Hour of day (0-23) with most commits.
            peak_day (int): Day of week (0=Monday ... 6=Sunday) with most commits.
            hour_distribution (list[int]): Commit counts indexed by hour 0-23.
            day_distribution (list[int]): Commit counts indexed by weekday 0-6.

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    try:
        commits = parse_git_log(repo_path)
    except RuntimeError as exc:
        if "does not have any commits" in str(exc) or "no commits" in str(exc).lower():
            return {}
        raise
    if not commits:
        return {}

    # {email: {hour: count}}, {email: {weekday: count}}
    hour_counts: dict[str, Counter] = defaultdict(Counter)
    day_counts: dict[str, Counter] = defaultdict(Counter)
    author_names: dict[str, str] = {}

    for commit in commits:
        email = commit["author_email"]
        author_names[email] = commit["author_name"]
        date_str = commit.get("date", "")
        if not date_str:
            continue
        try:
            dt = _parse_iso_datetime(date_str)
            hour_counts[email][dt.hour] += 1
            day_counts[email][dt.weekday()] += 1
        except (ValueError, TypeError):
            continue

    result: dict = {}
    for email in author_names:
        h_counter = hour_counts[email]
        d_counter = day_counts[email]

        hour_dist = [h_counter.get(h, 0) for h in range(24)]
        day_dist = [d_counter.get(d, 0) for d in range(7)]

        peak_hour = max(range(24), key=lambda h: hour_dist[h]) if any(hour_dist) else 0
        peak_day = max(range(7), key=lambda d: day_dist[d]) if any(day_dist) else 0

        result[email] = {
            "author_name": author_names[email],
            "peak_hour": peak_hour,
            "peak_day": peak_day,
            "hour_distribution": hour_dist,
            "day_distribution": day_dist,
        }

    return result


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _parse_iso_datetime(date_str: str) -> datetime:
    """Parse ISO 8601 datetime string to datetime object.

    Args:
        date_str: ISO 8601 date string, possibly with timezone offset.

    Returns:
        datetime object (timezone-naive, in commit's local time).
    """
    # Strip timezone offset for simple parsing
    clean = re.sub(r"[+-]\d{2}:\d{2}$", "", date_str.strip())
    clean = clean.replace("T", " ").rstrip("Z")
    try:
        return datetime.strptime(clean, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.strptime(clean[:10], "%Y-%m-%d")


def _collect_files_touched(
    repo_path: str,
    stats: dict,
    file_sets: dict,
) -> None:
    """Populate file_sets per author by reading git log with --name-only.

    Args:
        repo_path: Path to git repository.
        stats: Author stats dict keyed by email.
        file_sets: Dict of email -> set of file paths, modified in-place.
    """
    result = _run_git(
        ["log", "--pretty=format:%ae", "--name-only", "--diff-filter=ACDMR"],
        repo_path,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return

    current_email = ""
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if line in stats:
            current_email = line
        elif current_email:
            file_sets[current_email].add(line)
