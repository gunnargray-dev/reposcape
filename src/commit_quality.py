"""Commit message quality analyzer.

Scores individual commit messages and provides aggregate quality metrics for
an entire repository's commit history.
"""

from __future__ import annotations

import re
from typing import Optional

from .clone import parse_git_log


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONVENTIONAL_PREFIXES: list[str] = [
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "build",
    "ci",
    "chore",
    "revert",
]

# Messages considered generic / low-quality
_GENERIC_MESSAGES: frozenset[str] = frozenset(
    {
        "fix",
        "fixes",
        "fixed",
        "update",
        "updated",
        "updates",
        "wip",
        "work in progress",
        "commit",
        "changes",
        "change",
        "misc",
        "cleanup",
        "minor",
        "stuff",
        "test",
        "testing",
        "temp",
        "tmp",
        "asdf",
        "asd",
        "xxx",
        "todo",
        "initial commit",
        "first commit",
        "init",
    }
)

# Grade thresholds
_GRADE_THRESHOLDS: list[tuple[int, str]] = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0, "F"),
]

# Ideal subject line length range
_MIN_SUBJECT_LEN = 10
_IDEAL_MAX_SUBJECT_LEN = 72
_HARD_MAX_SUBJECT_LEN = 120

# Points breakdown (must sum to 100)
_POINTS_NOT_GENERIC = 30       # Not a generic filler message
_POINTS_LENGTH = 25            # Appropriate length
_POINTS_CONVENTIONAL = 20      # Uses conventional commit prefix
_POINTS_CAPITALIZATION = 15    # Proper capitalization
_POINTS_BODY_BONUS = 10        # Has a body section (bonus)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def score_commit_message(message: str) -> dict:
    """Score a single commit message on quality criteria.

    Scoring breakdown (100 points total):
    - Not a generic filler message: 30 pts
    - Appropriate length (10-72 chars): 25 pts
    - Uses conventional commit prefix: 20 pts
    - Proper capitalization of first word: 15 pts
    - Has body text (multi-line): 10 pts bonus

    Args:
        message: The full commit message (subject + optional body).

    Returns:
        Dict containing:
            score (int): Quality score 0-100.
            grade (str): Letter grade A-F.
            issues (list[str]): Human-readable list of detected problems.
    """
    issues: list[str] = []
    score = 0

    lines = message.strip().splitlines()
    subject = lines[0].strip() if lines else ""
    has_body = len(lines) > 2 and any(l.strip() for l in lines[2:])

    subject_lower = subject.lower().strip()

    # --- Not generic (30 pts) ---
    is_generic = subject_lower in _GENERIC_MESSAGES
    if not is_generic:
        score += _POINTS_NOT_GENERIC
    else:
        issues.append(f"Generic or filler message: {subject!r}")

    # --- Length (25 pts) ---
    length_score, length_issue = _score_length(subject)
    score += length_score
    if length_issue:
        issues.append(length_issue)

    # --- Conventional prefix (20 pts) ---
    has_prefix = _has_conventional_prefix(subject)
    if has_prefix:
        score += _POINTS_CONVENTIONAL
    else:
        issues.append("Missing conventional commit prefix (feat:, fix:, docs:, etc.)")

    # --- Capitalization (15 pts) ---
    cap_score, cap_issue = _score_capitalization(subject)
    score += cap_score
    if cap_issue:
        issues.append(cap_issue)

    # --- Body bonus (10 pts) ---
    if has_body:
        score += _POINTS_BODY_BONUS

    score = max(0, min(100, score))
    grade = _score_to_grade(score)

    return {"score": score, "grade": grade, "issues": issues}


def analyze_commit_quality(repo_path: str) -> dict:
    """Analyze commit message quality across an entire repository.

    Runs score_commit_message on every commit and aggregates results.

    Args:
        repo_path: Absolute path to the local git repository.

    Returns:
        Dict containing:
            total_analyzed (int): Number of commits scored.
            average_score (float): Mean score across all commits.
            average_grade (str): Letter grade for the average score.
            grade_distribution (dict): Counts of A/B/C/D/F grades.
            best_commits (list[dict]): Top 5 commits by score.
            worst_commits (list[dict]): Bottom 5 commits by score.

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    try:
        commits = parse_git_log(repo_path)
    except RuntimeError as exc:
        if "does not have any commits" in str(exc) or "no commits" in str(exc).lower():
            return {
                "total_analyzed": 0,
                "average_score": 0.0,
                "average_grade": "F",
                "grade_distribution": {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0},
                "best_commits": [],
                "worst_commits": [],
            }
        raise
    if not commits:
        return {
            "total_analyzed": 0,
            "average_score": 0.0,
            "average_grade": "F",
            "grade_distribution": {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0},
            "best_commits": [],
            "worst_commits": [],
        }

    scored: list[dict] = []
    grade_distribution: dict[str, int] = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}

    for commit in commits:
        result = score_commit_message(commit["message"])
        entry = {
            "hash": commit["hash"],
            "message": commit["message"],
            "score": result["score"],
            "grade": result["grade"],
            "issues": result["issues"],
            "date": commit["date"],
            "author_name": commit["author_name"],
        }
        scored.append(entry)
        grade_distribution[result["grade"]] = grade_distribution.get(result["grade"], 0) + 1

    total = len(scored)
    avg_score = sum(e["score"] for e in scored) / total if total > 0 else 0.0
    avg_grade = _score_to_grade(int(avg_score))

    sorted_by_score = sorted(scored, key=lambda x: x["score"])
    worst = sorted_by_score[:5]
    best = sorted_by_score[-5:][::-1]

    return {
        "total_analyzed": total,
        "average_score": round(avg_score, 1),
        "average_grade": avg_grade,
        "grade_distribution": grade_distribution,
        "best_commits": best,
        "worst_commits": worst,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _has_conventional_prefix(subject: str) -> bool:
    """Return True if subject starts with a recognized conventional prefix.

    Args:
        subject: The commit subject line.

    Returns:
        True if a conventional prefix (e.g. ``feat:``, ``fix(scope):``) is found.
    """
    pattern = r"^(" + "|".join(re.escape(p) for p in CONVENTIONAL_PREFIXES) + r")(\([^)]*\))?!?:"
    return bool(re.match(pattern, subject.lower()))


def _score_length(subject: str) -> tuple[int, Optional[str]]:
    """Score subject line length.

    Args:
        subject: The commit subject line.

    Returns:
        Tuple of (points_awarded, issue_message_or_None).
    """
    length = len(subject)

    if length == 0:
        return 0, "Subject line is empty"
    if length < _MIN_SUBJECT_LEN:
        return 0, f"Subject too short ({length} chars, minimum {_MIN_SUBJECT_LEN})"
    if length <= _IDEAL_MAX_SUBJECT_LEN:
        return _POINTS_LENGTH, None
    if length <= _HARD_MAX_SUBJECT_LEN:
        return _POINTS_LENGTH // 2, f"Subject line is long ({length} chars, ideal max {_IDEAL_MAX_SUBJECT_LEN})"
    return 0, f"Subject line is too long ({length} chars, hard max {_HARD_MAX_SUBJECT_LEN})"


def _score_capitalization(subject: str) -> tuple[int, Optional[str]]:
    """Score subject line capitalization.

    Accepts: starts with uppercase OR starts with a lowercase conventional prefix.

    Args:
        subject: The commit subject line.

    Returns:
        Tuple of (points_awarded, issue_message_or_None).
    """
    if not subject:
        return 0, None

    # Conventional commits start lowercase (feat: ...) - that's acceptable
    if _has_conventional_prefix(subject):
        return _POINTS_CAPITALIZATION, None

    first_char = subject[0]
    if first_char.isupper():
        return _POINTS_CAPITALIZATION, None

    if first_char.islower():
        return 0, "Subject line should start with a capital letter or conventional prefix"

    # Starts with non-letter (e.g. number, emoji) - neutral
    return _POINTS_CAPITALIZATION, None


def _score_to_grade(score: int) -> str:
    """Convert numeric score to letter grade.

    Args:
        score: Integer score 0-100.

    Returns:
        Letter grade string: A, B, C, D, or F.
    """
    for threshold, grade in _GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "F"
