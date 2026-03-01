"""Code complexity analyzer for Python and JavaScript/TypeScript files.

Calculates cyclomatic complexity per function using Python's ``ast`` module
and provides a regex-based estimator for JS/TS files. Produces color-coded
data suitable for complexity heatmap visualizations.
"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SKIP_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "vendor",
        "dist",
        "build",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        "site-packages",
        "coverage",
        ".coverage",
    }
)

# AST node types that each add 1 to cyclomatic complexity
_DECISION_NODES: tuple[type, ...] = (
    ast.If,
    ast.For,
    ast.While,
    ast.ExceptHandler,
    ast.With,
    ast.Assert,
    ast.comprehension,  # list/set/dict/generator comprehension
)

# Grade thresholds: A (1-5), B (6-10), C (11-15), D (16-20), F (21+)
_GRADE_THRESHOLDS: list[tuple[int, str]] = [
    (5, "A"),
    (10, "B"),
    (15, "C"),
    (20, "D"),
]

# JS/TS keywords and operators that indicate decision points
_JS_DECISION_RE = re.compile(
    r"""
    \bif\b | \belse\b | \bfor\b | \bwhile\b | \bswitch\b |
    \bcase\b | \bcatch\b | \?\?? |
    &&|\|\|
    """,
    re.VERBOSE,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _complexity_grade(complexity: int) -> str:
    """Convert a cyclomatic complexity integer to a letter grade.

    Args:
        complexity: Cyclomatic complexity value (>= 1).

    Returns:
        Grade string: ``"A"`` (1-5), ``"B"`` (6-10), ``"C"`` (11-15),
        ``"D"`` (16-20), or ``"F"`` (21+).
    """
    for threshold, grade in _GRADE_THRESHOLDS:
        if complexity <= threshold:
            return grade
    return "F"


def _count_body_lines(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Return the number of lines in a function body.

    Args:
        node: An ``ast.FunctionDef`` or ``ast.AsyncFunctionDef`` node.

    Returns:
        Line count from the function's first body statement to its last.
    """
    try:
        start = node.lineno
        end = node.end_lineno or node.lineno
        return max(1, end - start + 1)
    except AttributeError:
        return 1


class _ComplexityVisitor(ast.NodeVisitor):
    """AST visitor that counts decision points in a function body."""

    def __init__(self) -> None:
        self.count: int = 0

    # Each of these node types adds 1 to complexity
    def visit_If(self, node: ast.If) -> None:  # noqa: N802
        self.count += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:  # noqa: N802
        self.count += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:  # noqa: N802
        self.count += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:  # noqa: N802
        self.count += 1
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:  # noqa: N802
        self.count += 1
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:  # noqa: N802
        self.count += 1
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:  # noqa: N802
        self.count += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:  # noqa: N802
        # Each extra operand in ``and``/``or`` is a branch point
        self.count += len(node.values) - 1
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:  # noqa: N802
        # Ternary expression (x if cond else y)
        self.count += 1
        self.generic_visit(node)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def calculate_cyclomatic_complexity(source: str) -> int:
    """Calculate the cyclomatic complexity of a Python source string.

    Complexity = 1 + number of decision points (if, elif, for, while,
    except, with, assert, boolean operators, comprehensions, ternary
    expressions).

    Args:
        source: Python source code as a string.

    Returns:
        Integer complexity value >= 1. Returns 1 for empty or
        unparseable source.
    """
    if not source or not source.strip():
        return 1

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 1

    visitor = _ComplexityVisitor()
    visitor.visit(tree)
    return 1 + visitor.count


def analyze_function_complexity(file_path: str) -> list[dict]:
    """Analyze the cyclomatic complexity of every function in a Python file.

    Processes both top-level functions and class methods. Nested functions
    are included as separate entries with qualified names.

    Args:
        file_path: Absolute or relative path to the ``.py`` file.

    Returns:
        List of function dicts, each containing:
            name (str): Qualified function name (e.g. ``"MyClass.method"``).
            line (int): Line number of the ``def`` statement.
            complexity (int): Cyclomatic complexity value.
            grade (str): Letter grade A through F.
            lines (int): Number of lines in the function body.

        Returns an empty list if the file cannot be parsed.
    """
    path = Path(file_path)
    if not path.is_file():
        return []

    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, OSError):
        return []

    results: list[dict] = []

    def _visit_function(
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        prefix: str,
    ) -> None:
        qualified_name = f"{prefix}.{node.name}" if prefix else node.name
        visitor = _ComplexityVisitor()
        visitor.visit(node)
        complexity = 1 + visitor.count
        body_lines = _count_body_lines(node)
        results.append(
            {
                "name": qualified_name,
                "line": node.lineno,
                "complexity": complexity,
                "grade": _complexity_grade(complexity),
                "lines": body_lines,
            }
        )
        # Recurse into nested functions and methods
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _visit_function(child, qualified_name)

    def _walk_top(node: ast.AST, prefix: str = "") -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _visit_function(child, prefix)
            elif isinstance(child, ast.ClassDef):
                class_prefix = f"{prefix}.{child.name}" if prefix else child.name
                for item in ast.iter_child_nodes(child):
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        _visit_function(item, class_prefix)
                    elif isinstance(item, ast.ClassDef):
                        _walk_top(item, class_prefix)

    _walk_top(tree)
    results.sort(key=lambda x: x["line"])
    return results


def analyze_file_complexity(file_path: str) -> dict:
    """Aggregate cyclomatic complexity statistics for a single Python file.

    Args:
        file_path: Absolute or relative path to the ``.py`` file.

    Returns:
        Dict containing:
            path (str): File path as provided.
            total_complexity (int): Sum of all function complexities.
            avg_complexity (float): Average complexity across all functions.
            max_complexity (int): Highest single-function complexity.
            functions (int): Total number of functions analyzed.
            grade (str): Grade based on average complexity.
            hotspots (list[dict]): Functions with grade C or worse (sorted
                by complexity descending).
    """
    functions = analyze_function_complexity(file_path)

    if not functions:
        return {
            "path": file_path,
            "total_complexity": 0,
            "avg_complexity": 0.0,
            "max_complexity": 0,
            "functions": 0,
            "grade": "A",
            "hotspots": [],
        }

    total = sum(f["complexity"] for f in functions)
    avg = round(total / len(functions), 2)
    max_c = max(f["complexity"] for f in functions)
    hotspots = sorted(
        [f for f in functions if f["grade"] not in {"A", "B"}],
        key=lambda x: x["complexity"],
        reverse=True,
    )

    return {
        "path": file_path,
        "total_complexity": total,
        "avg_complexity": avg,
        "max_complexity": max_c,
        "functions": len(functions),
        "grade": _complexity_grade(round(avg)),
        "hotspots": hotspots,
    }


def analyze_repo_complexity(repo_path: str) -> dict:
    """Analyze cyclomatic complexity for all Python files in a repository.

    Walks the repository, skipping hidden and generated directories, and
    analyzes each ``.py`` file. Produces a summary suitable for complexity
    heatmap and overview visualizations.

    Args:
        repo_path: Absolute path to the root of the repository.

    Returns:
        Dict with keys:
            files (list[dict]): Per-file results from
                :func:`analyze_file_complexity`.
            summary (dict):
                total_files (int): Number of Python files analyzed.
                total_functions (int): Total functions across all files.
                avg_complexity (float): Global average complexity.
                grade (str): Overall repo grade.
                hotspot_files (list[dict]): Files with grade C or worse,
                    sorted by avg_complexity descending.
                complexity_distribution (dict): Counts of functions in
                    each grade bucket (A, B, C, D, F).
    """
    root = Path(repo_path).resolve()
    file_results: list[dict] = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for fname in sorted(filenames):
            if Path(fname).suffix == ".py":
                abs_path = str(Path(dirpath) / fname)
                result = analyze_file_complexity(abs_path)
                # Store relative path for cleaner output
                try:
                    result["path"] = str(Path(abs_path).relative_to(root))
                except ValueError:
                    pass
                file_results.append(result)

    # Aggregate distribution across all function grades
    distribution: dict[str, int] = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    all_complexities: list[float] = []
    total_functions = 0

    for fr in file_results:
        total_functions += fr["functions"]
        all_complexities.extend(
            [f["complexity"] for f in analyze_function_complexity(
                str(root / fr["path"])
            )]
        )

    # Re-walk for distribution (grade per function)
    for fr in file_results:
        abs_path = str(root / fr["path"])
        for func in analyze_function_complexity(abs_path):
            distribution[func["grade"]] = distribution.get(func["grade"], 0) + 1

    total_files = len(file_results)
    avg_complexity = (
        round(sum(all_complexities) / len(all_complexities), 2)
        if all_complexities
        else 0.0
    )
    overall_grade = _complexity_grade(round(avg_complexity)) if avg_complexity else "A"

    hotspot_files = sorted(
        [f for f in file_results if f["grade"] not in {"A", "B"}],
        key=lambda x: x["avg_complexity"],
        reverse=True,
    )

    return {
        "files": file_results,
        "summary": {
            "total_files": total_files,
            "total_functions": total_functions,
            "avg_complexity": avg_complexity,
            "grade": overall_grade,
            "hotspot_files": hotspot_files,
            "complexity_distribution": distribution,
        },
    }


def estimate_js_complexity(file_path: str) -> dict:
    """Estimate cyclomatic complexity for a JS/TS file using regex heuristics.

    Counts decision-point keywords and operators (if, else, for, while,
    switch, case, catch, &&, ||, ?) to approximate complexity. Less accurate
    than AST-based analysis but works for any JS/TS dialect.

    Args:
        file_path: Absolute or relative path to the JS/TS file.

    Returns:
        Dict containing:
            path (str): File path as provided.
            estimated_complexity (int): 1 + count of decision keywords found.
            decision_points (int): Raw count of matched decision keywords.
            grade (str): Letter grade based on estimated complexity.
            lines (int): Total line count of the file.

        Returns a complexity of 1 with grade ``"A"`` if the file cannot be read.
    """
    path = Path(file_path)
    if not path.is_file():
        return {
            "path": file_path,
            "estimated_complexity": 1,
            "decision_points": 0,
            "grade": "A",
            "lines": 0,
        }

    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {
            "path": file_path,
            "estimated_complexity": 1,
            "decision_points": 0,
            "grade": "A",
            "lines": 0,
        }

    # Strip single-line and multi-line comments to reduce false positives
    source_no_comments = re.sub(r"//.*", "", source)
    source_no_comments = re.sub(r"/\*.*?\*/", "", source_no_comments, flags=re.DOTALL)

    matches = _JS_DECISION_RE.findall(source_no_comments)
    decision_points = len(matches)
    estimated = 1 + decision_points
    lines = len(source.splitlines())

    return {
        "path": file_path,
        "estimated_complexity": estimated,
        "decision_points": decision_points,
        "grade": _complexity_grade(estimated),
        "lines": lines,
    }
