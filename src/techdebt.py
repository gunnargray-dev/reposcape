"""Tech debt scanner and scorer.

Scans a repository for technical debt indicators: TODO/FIXME comments,
large files, deeply nested code, long functions, and aggregates them into
a single weighted tech debt score (0-100, lower is better).
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path

from .clone import _run_git


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Directories to skip during scanning
_SKIP_DIRS: frozenset[str] = frozenset({
    ".git", "node_modules", "__pycache__", ".venv", "venv", ".env",
    "dist", "build", ".tox", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "vendor", "third_party",
})

# Comment patterns indicating tech debt
_DEBT_PATTERNS: dict[str, re.Pattern] = {
    "TODO": re.compile(r"#\s*TODO\b", re.IGNORECASE),
    "FIXME": re.compile(r"#\s*FIXME\b", re.IGNORECASE),
    "HACK": re.compile(r"#\s*HACK\b", re.IGNORECASE),
    "XXX": re.compile(r"#\s*XXX\b", re.IGNORECASE),
    "WORKAROUND": re.compile(r"#\s*WORKAROUND\b", re.IGNORECASE),
}

# Source file extensions to scan
_SOURCE_EXTENSIONS: frozenset[str] = frozenset({
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".kt", ".go",
    ".rs", ".cpp", ".cc", ".c", ".h", ".hpp", ".cs", ".rb", ".php",
    ".swift", ".scala", ".sh", ".bash", ".yaml", ".yml", ".toml",
})

# Grade thresholds (lower score = better)
_GRADE_THRESHOLDS: list[tuple[int, str]] = [
    (10, "A"),
    (25, "B"),
    (40, "C"),
    (60, "D"),
    (101, "F"),
]

# Long function threshold (lines)
_LONG_FUNCTION_LINES = 50


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def scan_todos(repo_path: str) -> list[dict]:
    """Find all TODO, FIXME, HACK, XXX, WORKAROUND comments in source files.

    Args:
        repo_path: Absolute path to the local git repository.

    Returns:
        List of dicts sorted by path and line number, each containing:
            path (str): Relative file path from repo root.
            line (int): 1-based line number.
            type (str): Comment type ("TODO", "FIXME", "HACK", "XXX", "WORKAROUND").
            text (str): Full line text (stripped).
            author (str): Author email from git blame if available, else "".

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    if not Path(repo_path).joinpath(".git").exists():
        raise RuntimeError(f"Not a git repository: {repo_path!r}")

    findings: list[dict] = []
    repo = Path(repo_path)

    for filepath in _iter_source_files(repo):
        rel_path = str(filepath.relative_to(repo))
        try:
            lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
        except (OSError, PermissionError):
            continue

        for line_no, line_text in enumerate(lines, start=1):
            for debt_type, pattern in _DEBT_PATTERNS.items():
                if pattern.search(line_text):
                    findings.append({
                        "path": rel_path,
                        "line": line_no,
                        "type": debt_type,
                        "text": line_text.strip(),
                        "author": "",
                    })
                    break  # Only report first matching type per line

    # Enrich with git blame author (limit to first 200 findings)
    for finding in findings[:200]:
        finding["author"] = _get_blame_author(repo_path, finding["path"], finding["line"])

    return sorted(findings, key=lambda f: (f["path"], f["line"]))


def find_large_files(repo_path: str, threshold_lines: int = 500) -> list[dict]:
    """Find source files exceeding the given line count threshold.

    Args:
        repo_path: Absolute path to the local git repository.
        threshold_lines: Files with at least this many lines are flagged.

    Returns:
        List of dicts sorted by lines descending, each containing:
            path (str): Relative file path from repo root.
            lines (int): Total line count.
            language (str): Detected language from extension.

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    if not Path(repo_path).joinpath(".git").exists():
        raise RuntimeError(f"Not a git repository: {repo_path!r}")

    repo = Path(repo_path)
    large_files = []

    for filepath in _iter_source_files(repo):
        try:
            line_count = sum(1 for _ in filepath.open(encoding="utf-8", errors="replace"))
        except (OSError, PermissionError):
            continue

        if line_count >= threshold_lines:
            rel_path = str(filepath.relative_to(repo))
            large_files.append({
                "path": rel_path,
                "lines": line_count,
                "language": _ext_to_language(filepath.suffix),
            })

    return sorted(large_files, key=lambda f: f["lines"], reverse=True)


def find_deep_nesting(repo_path: str, max_depth: int = 4) -> list[dict]:
    """Find code constructs with excessive nesting depth.

    For Python files, uses AST analysis. For other files, uses an
    indentation-based heuristic (4 spaces or 1 tab = 1 level).

    Args:
        repo_path: Absolute path to the local git repository.
        max_depth: Constructs nested deeper than this are flagged.

    Returns:
        List of dicts sorted by depth descending, each containing:
            path (str): Relative file path from repo root.
            function (str): Function/scope name if determinable.
            line (int): 1-based line number where deep nesting occurs.
            depth (int): Detected nesting depth.

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    if not Path(repo_path).joinpath(".git").exists():
        raise RuntimeError(f"Not a git repository: {repo_path!r}")

    repo = Path(repo_path)
    findings: list[dict] = []

    for filepath in _iter_source_files(repo):
        rel_path = str(filepath.relative_to(repo))
        if filepath.suffix == ".py":
            findings.extend(_analyze_python_nesting(filepath, rel_path, max_depth))
        else:
            findings.extend(_analyze_indent_nesting(filepath, rel_path, max_depth))

    return sorted(findings, key=lambda f: f["depth"], reverse=True)


def calculate_tech_debt_score(repo_path: str) -> dict:
    """Aggregate all tech debt signals into a single composite score.

    Scoring weights (lower total = less debt):
    - TODO density (25%): todos per 1000 source lines
    - Large files (20%): proportion of files above threshold
    - Deep nesting (20%): proportion of files with excessive nesting
    - Long functions (20%): proportion of Python functions above line limit
    - Code duplication hints (15%): repeated boilerplate patterns

    Score range: 0-100 (lower is better).
    Grade: A<=10, B<=25, C<=40, D<=60, F>60.

    Args:
        repo_path: Absolute path to the local git repository.

    Returns:
        Dict containing:
            score (int): Composite tech debt score 0-100.
            grade (str): Letter grade A-F.
            breakdown (dict): Per-signal raw stats and sub-scores.
            top_issues (list[str]): Up to 5 human-readable issue descriptions.

    Raises:
        RuntimeError: If repo_path is not a valid git repository.
    """
    if not Path(repo_path).joinpath(".git").exists():
        raise RuntimeError(f"Not a git repository: {repo_path!r}")

    repo = Path(repo_path)

    todos = scan_todos(repo_path)
    large_files = find_large_files(repo_path)
    deep_nesting = find_deep_nesting(repo_path)

    total_lines = 0
    total_files = 0
    long_functions = 0
    total_functions = 0
    duplication_hints = 0

    for filepath in _iter_source_files(repo):
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except (OSError, PermissionError):
            continue
        lines = content.splitlines()
        total_lines += len(lines)
        total_files += 1

        if filepath.suffix == ".py":
            lf, tf = _count_long_functions(content)
            long_functions += lf
            total_functions += tf
            duplication_hints += _count_duplication_hints(lines)

    # Sub-scores (0-100, higher = more debt)
    todo_density = (len(todos) / max(total_lines, 1)) * 1000
    todo_sub = min(100, todo_density * 10)

    large_pct = (len(large_files) / max(total_files, 1)) * 100
    large_sub = min(100, large_pct * 2)

    nest_files = len({f["path"] for f in deep_nesting})
    nest_pct = (nest_files / max(total_files, 1)) * 100
    nesting_sub = min(100, nest_pct * 2)

    long_fn_pct = (long_functions / total_functions * 100) if total_functions > 0 else 0.0
    long_fn_sub = min(100, long_fn_pct * 2)

    dup_density = (duplication_hints / max(total_lines, 1)) * 1000
    dup_sub = min(100, dup_density * 5)

    score = int(round(
        todo_sub * 0.25
        + large_sub * 0.20
        + nesting_sub * 0.20
        + long_fn_sub * 0.20
        + dup_sub * 0.15
    ))
    score = max(0, min(100, score))
    grade = _score_to_grade(score)
    top_issues = _build_top_issues(todos, large_files, deep_nesting, long_functions, total_functions)

    return {
        "score": score,
        "grade": grade,
        "breakdown": {
            "todo_count": len(todos),
            "todo_density_per_1k_lines": round(todo_density, 2),
            "todo_sub_score": round(todo_sub, 1),
            "large_file_count": len(large_files),
            "large_file_sub_score": round(large_sub, 1),
            "nesting_violation_files": nest_files,
            "nesting_sub_score": round(nesting_sub, 1),
            "long_function_count": long_functions,
            "total_function_count": total_functions,
            "long_function_sub_score": round(long_fn_sub, 1),
            "duplication_hints": duplication_hints,
            "duplication_sub_score": round(dup_sub, 1),
            "total_source_lines": total_lines,
            "total_source_files": total_files,
        },
        "top_issues": top_issues,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _iter_source_files(repo: Path):
    """Yield source file Paths, skipping excluded directories.

    Args:
        repo: Root path of the repository.

    Yields:
        Path objects for each qualifying source file.
    """
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS and not d.startswith(".")]
        for filename in files:
            filepath = Path(root) / filename
            if filepath.suffix in _SOURCE_EXTENSIONS:
                yield filepath


def _get_blame_author(repo_path: str, rel_path: str, line_no: int) -> str:
    """Get the git blame author email for a specific line.

    Args:
        repo_path: Path to git repository.
        rel_path: Relative path to the file.
        line_no: 1-based line number.

    Returns:
        Author email string, or empty string on failure.
    """
    result = _run_git(
        ["blame", "-p", f"-L{line_no},{line_no}", "--", rel_path],
        repo_path,
    )
    if result.returncode != 0:
        return ""
    for line in result.stdout.splitlines():
        if line.startswith("author-mail "):
            return line.split("author-mail ")[1].strip().strip("<>")
    return ""


def _ext_to_language(suffix: str) -> str:
    """Map a file extension to a language name.

    Args:
        suffix: File extension including the dot (e.g. ".py").

    Returns:
        Language name string.
    """
    mapping = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".jsx": "JavaScript", ".tsx": "TypeScript", ".java": "Java",
        ".kt": "Kotlin", ".go": "Go", ".rs": "Rust", ".cpp": "C++",
        ".cc": "C++", ".c": "C", ".h": "C/C++", ".hpp": "C++",
        ".cs": "C#", ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
        ".scala": "Scala", ".sh": "Shell", ".bash": "Shell",
    }
    return mapping.get(suffix, "Unknown")


def _analyze_python_nesting(filepath: Path, rel_path: str, max_depth: int) -> list[dict]:
    """Analyze Python AST for deeply nested constructs.

    Args:
        filepath: Absolute path to the Python file.
        rel_path: Relative path for reporting.
        max_depth: Minimum depth to flag.

    Returns:
        List of nesting violation dicts.
    """
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return []

    findings = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            depth = _max_nesting_depth(node)
            if depth > max_depth:
                findings.append({
                    "path": rel_path,
                    "function": node.name,
                    "line": node.lineno,
                    "depth": depth,
                })
    return findings


def _max_nesting_depth(func_node: ast.AST, current: int = 0) -> int:
    """Recursively compute maximum nesting depth inside a function node.

    Args:
        func_node: AST node to analyze.
        current: Current depth accumulator.

    Returns:
        Maximum depth integer.
    """
    nesting_nodes = (
        ast.If, ast.For, ast.While, ast.With, ast.Try,
        ast.FunctionDef, ast.AsyncFunctionDef, ast.AsyncFor, ast.AsyncWith,
    )
    max_d = current
    for child in ast.iter_child_nodes(func_node):
        if isinstance(child, nesting_nodes):
            child_depth = _max_nesting_depth(child, current + 1)
        else:
            child_depth = _max_nesting_depth(child, current)
        max_d = max(max_d, child_depth)
    return max_d


def _analyze_indent_nesting(filepath: Path, rel_path: str, max_depth: int) -> list[dict]:
    """Detect deep nesting via indentation heuristic for non-Python files.

    Each 4-space indent (or 1 tab) counts as one level.

    Args:
        filepath: Absolute path to the file.
        rel_path: Relative path for reporting.
        max_depth: Minimum depth to flag.

    Returns:
        List of nesting violation dicts.
    """
    try:
        lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
    except (OSError, PermissionError):
        return []

    findings = []
    for line_no, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        stripped = line.lstrip()
        leading = len(line) - len(stripped)
        if "\t" in line[:leading]:
            depth = leading
        else:
            depth = leading // 4

        if depth > max_depth:
            findings.append({
                "path": rel_path,
                "function": "",
                "line": line_no,
                "depth": depth,
            })

    if len(findings) > 50:
        findings = sorted(findings, key=lambda f: f["depth"], reverse=True)[:50]
    return findings


def _count_long_functions(source: str) -> tuple[int, int]:
    """Count long (>50 line) and total functions in Python source.

    Args:
        source: Python source code string.

    Returns:
        Tuple of (long_function_count, total_function_count).
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0, 0

    long_count = 0
    total_count = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            total_count += 1
            start = node.lineno
            end = getattr(node, "end_lineno", start)
            if end - start + 1 > _LONG_FUNCTION_LINES:
                long_count += 1

    return long_count, total_count


def _count_duplication_hints(lines: list[str]) -> int:
    """Count crude duplication hints: repeated boilerplate lines.

    Args:
        lines: Source file lines.

    Returns:
        Integer count of potential duplication hints.
    """
    from collections import Counter
    stripped = [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]
    counts = Counter(stripped)
    common = {"pass", "return", "break", "continue", "...", "return None",
              "return {}", "return []", "return ''", 'return ""'}
    return sum(
        v - 1 for line, v in counts.items()
        if v >= 3 and line not in common and len(line) > 5
    )


def _build_top_issues(
    todos: list[dict],
    large_files: list[dict],
    deep_nesting: list[dict],
    long_fn_count: int,
    total_fn_count: int,
) -> list[str]:
    """Build a concise list of the most impactful tech debt issues.

    Args:
        todos: List of TODO/FIXME findings.
        large_files: List of large file findings.
        deep_nesting: List of deep nesting findings.
        long_fn_count: Count of long functions.
        total_fn_count: Total function count.

    Returns:
        List of up to 5 issue description strings.
    """
    issues = []
    if todos:
        fixme_count = sum(1 for t in todos if t["type"] == "FIXME")
        todo_count = sum(1 for t in todos if t["type"] == "TODO")
        issues.append(f"{len(todos)} debt markers ({todo_count} TODOs, {fixme_count} FIXMEs)")
    if large_files:
        worst = large_files[0]
        issues.append(
            f"{len(large_files)} large file(s) — worst: {worst['path']} ({worst['lines']} lines)"
        )
    if deep_nesting:
        worst = deep_nesting[0]
        issues.append(
            f"{len(deep_nesting)} deep nesting violation(s) — worst: "
            f"{worst['path']}:{worst['line']} (depth {worst['depth']})"
        )
    if long_fn_count > 0 and total_fn_count > 0:
        pct = round(long_fn_count / total_fn_count * 100)
        issues.append(f"{long_fn_count} long function(s) ({pct}% of all functions)")
    if not issues:
        issues.append("No significant tech debt detected")
    return issues[:5]


def _score_to_grade(score: int) -> str:
    """Convert a tech debt score to a letter grade (lower = better).

    Args:
        score: Integer score 0-100.

    Returns:
        Letter grade string: A, B, C, D, or F.
    """
    for threshold, grade in _GRADE_THRESHOLDS:
        if score < threshold:
            return grade
    return "F"
