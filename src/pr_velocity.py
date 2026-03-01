"""PR velocity and merge pattern analyzer.

Analyzes pull request activity from git history using merge commits and
branch data. Works entirely from the local git clone without any GitHub API
calls, making it suitable for any public repository.
"""

from __future__ import annotations

import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from .clone import _run_git, parse_git_log


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def analyze_merge_commits(repo_path: str) -> list[dict]:
    """Find and parse all merge commits in the repository.

    Uses ``git log --merges`` to identify merge commits, then extracts
    branch name hints from the commit message (e.g. "Merge branch 'feature/x'").

    Args:
        repo_path: Absolute path to the local git repository.

    Returns:
        List of merge commit dicts sorted by date descending, each containing:
            hash (str): Full commit SHA.
            date (str): ISO date string of the merge.
            author_name (str): Name of the person who merged.
            author_email (str): Email of the person who merged.
            message (str): Full commit message.
            branch_name (str | None): Extracted branch name if parseable.
            commits_in_merge (int): 0 (estimated from merge structure).

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    if not Path(repo_path).joinpath(".git").exists():
        raise RuntimeError(f"Not a git repository: {repo_path!r}")

    SEP = "\x1e"
    result = _run_git(
        [
            "log", "--merges",
            f"--pretty=format:{SEP}%H%x00%an%x00%ae%x00%aI%x00%s%x00%b",
        ],
        repo_path,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []

    merges = []
    for block in result.stdout.split(SEP):
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        if not lines:
            continue
        fields = lines[0].split("\x00")
        if len(fields) < 5:
            continue

        commit_hash = fields[0].strip()
        author_name = fields[1].strip()
        author_email = fields[2].strip()
        date_str = fields[3].strip()
        subject = fields[4].strip()
        body = fields[5].strip() if len(fields) > 5 else ""

        full_message = subject + ("\n\n" + body if body else "")
        branch_name = _extract_branch_from_merge_message(subject)

        merges.append({
            "hash": commit_hash,
            "date": date_str,
            "author_name": author_name,
            "author_email": author_email,
            "message": full_message,
            "branch_name": branch_name,
            "commits_in_merge": 0,
        })

    return merges


def estimate_pr_velocity(repo_path: str) -> dict:
    """Estimate PR/merge velocity metrics from git history.

    Uses merge commits as a proxy for pull requests.

    Args:
        repo_path: Absolute path to the local git repository.

    Returns:
        Dict containing:
            total_merges (int): Total number of merge commits.
            avg_commits_per_merge (float): Mean commits between merges.
            merges_per_week (float): Average weekly merge rate.
            busiest_week (str | None): ISO week label with most merges.
            merge_frequency_trend (str): "increasing", "decreasing", or "stable".
            weekly_counts (list[dict]): Per-week merge counts [{week, merges}].

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    merges = analyze_merge_commits(repo_path)
    all_commits = parse_git_log(repo_path)

    total_merges = len(merges)
    total_commits = len(all_commits)

    if total_merges == 0:
        return {
            "total_merges": 0,
            "avg_commits_per_merge": 0.0,
            "merges_per_week": 0.0,
            "busiest_week": None,
            "merge_frequency_trend": "stable",
            "weekly_counts": [],
        }

    avg_commits_per_merge = round(total_commits / total_merges, 2) if total_merges > 0 else 0.0

    week_counts: Counter = Counter()
    for merge in merges:
        try:
            dt = _parse_iso_datetime(merge["date"])
            week_label = f"{dt.year}-W{dt.strftime('%W').zfill(2)}"
            week_counts[week_label] += 1
        except (ValueError, TypeError):
            continue

    weekly_counts = [
        {"week": w, "merges": c}
        for w, c in sorted(week_counts.items())
    ]

    total_weeks = len(week_counts) if week_counts else 1
    merges_per_week = round(total_merges / total_weeks, 2)
    busiest_week = week_counts.most_common(1)[0][0] if week_counts else None
    merge_frequency_trend = _calculate_trend([e["merges"] for e in weekly_counts])

    return {
        "total_merges": total_merges,
        "avg_commits_per_merge": avg_commits_per_merge,
        "merges_per_week": merges_per_week,
        "busiest_week": busiest_week,
        "merge_frequency_trend": merge_frequency_trend,
        "weekly_counts": weekly_counts,
    }


def get_branch_stats(repo_path: str) -> dict:
    """Analyze branch activity in the local clone.

    A branch is considered "stale" if its last commit was more than 30 days ago.

    Args:
        repo_path: Absolute path to the local git repository.

    Returns:
        Dict containing:
            total (int): Total number of branches.
            active (int): Branches with commits in the last 30 days.
            stale (int): Branches with no commits in 30+ days.
            branches (list[dict]): Per-branch details with name, last_commit_date,
                author, is_stale, commits_ahead.

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    if not Path(repo_path).joinpath(".git").exists():
        raise RuntimeError(f"Not a git repository: {repo_path!r}")

    SEP = "|||RSEP|||"
    result = _run_git(
        [
            "for-each-ref",
            "--sort=-committerdate",
            "refs/heads",
            f"--format=%(refname:short){SEP}%(committerdate:iso8601){SEP}%(authorname){SEP}%(ahead-behind:HEAD)",
        ],
        repo_path,
    )

    branches = []
    cutoff = datetime.now() - timedelta(days=30)

    if result.returncode == 0 and result.stdout.strip():
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(SEP)
            name = parts[0].strip() if parts else ""
            date_str = parts[1].strip() if len(parts) > 1 else ""
            author = parts[2].strip() if len(parts) > 2 else ""
            ahead_behind = parts[3].strip() if len(parts) > 3 else ""

            is_stale = True
            if date_str:
                try:
                    dt = _parse_iso_datetime(date_str)
                    is_stale = dt < cutoff
                except (ValueError, TypeError):
                    pass

            commits_ahead = 0
            if ahead_behind:
                ab_parts = ahead_behind.split()
                if ab_parts and ab_parts[0].isdigit():
                    commits_ahead = int(ab_parts[0])

            branches.append({
                "name": name,
                "last_commit_date": date_str[:10] if date_str else "",
                "author": author,
                "is_stale": is_stale,
                "commits_ahead": commits_ahead,
            })

    active = sum(1 for b in branches if not b["is_stale"])
    stale = sum(1 for b in branches if b["is_stale"])

    return {
        "total": len(branches),
        "active": active,
        "stale": stale,
        "branches": branches,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _parse_iso_datetime(date_str: str) -> datetime:
    """Parse ISO 8601 datetime string to a datetime object.

    Args:
        date_str: ISO 8601 date string, possibly with timezone offset.

    Returns:
        datetime object (timezone-naive).
    """
    import re as _re
    clean = _re.sub(r"[+-]\d{2}:\d{2}$", "", date_str.strip())
    clean = clean.replace("T", " ").rstrip("Z").strip()
    clean = _re.sub(r"\s+[+-]\d{4}$", "", clean)
    try:
        return datetime.strptime(clean, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(clean[:10], "%Y-%m-%d")
        except ValueError:
            return datetime.now()


def _extract_branch_from_merge_message(message: str) -> str | None:
    """Extract the merged branch name from a merge commit subject line.

    Args:
        message: The merge commit subject line.

    Returns:
        Extracted branch name string, or None if not parseable.
    """
    m = re.search(r"Merge branch '([^']+)'", message)
    if m:
        return m.group(1)
    m = re.search(r"Merge pull request #\d+ from \S+/(\S+)", message)
    if m:
        return m.group(1)
    m = re.search(r"Merge remote-tracking branch '(?:origin/)?([^']+)'", message)
    if m:
        return m.group(1)
    return None


def _calculate_trend(values: list[int | float]) -> str:
    """Determine if a sequence is increasing, decreasing, or stable.

    Args:
        values: Ordered list of numeric values.

    Returns:
        "increasing", "decreasing", or "stable".
    """
    if len(values) < 4:
        return "stable"

    mid = len(values) // 2
    first_mean = statistics.mean(values[:mid]) if values[:mid] else 0
    second_mean = statistics.mean(values[mid:]) if values[mid:] else 0

    if first_mean == 0:
        return "stable"

    change_pct = (second_mean - first_mean) / first_mean
    if change_pct > 0.15:
        return "increasing"
    if change_pct < -0.15:
        return "decreasing"
    return "stable"
