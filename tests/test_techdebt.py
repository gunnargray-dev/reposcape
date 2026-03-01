"""Tests for the tech debt scorer module."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from src.techdebt import (
    calculate_tech_debt_score,
    find_deep_nesting,
    find_large_files,
    scan_todos,
    _ext_to_language,
    _score_to_grade,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git"] + args, cwd=cwd, capture_output=True, check=False)


def _make_repo(path: Path) -> None:
    """Initialize a minimal git repo at path."""
    _git(["init"], path)
    _git(["config", "user.email", "dev@example.com"], path)
    _git(["config", "user.name", "Dev"], path)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo_with_todos(tmp_path: Path) -> str:
    """Repo containing TODO and FIXME comments across several files."""
    repo = tmp_path / "todo_repo"
    repo.mkdir()
    _make_repo(repo)

    (repo / "main.py").write_text(
        "# TODO: refactor this function\n"
        "def run():\n"
        "    # FIXME: this is broken\n"
        "    pass\n"
        "# HACK: temporary workaround\n"
        "x = 1\n"
        "# XXX: review this logic\n"
    )
    (repo / "utils.py").write_text(
        "def helper():\n"
        "    # WORKAROUND: library bug\n"
        "    return None\n"
    )
    (repo / "clean.py").write_text("def clean():\n    return True\n")

    _git(["add", "."], repo)
    _git(["commit", "-m", "feat: initial"], repo)
    return str(repo)


@pytest.fixture()
def large_file_repo(tmp_path: Path) -> str:
    """Repo containing files above and below the large-file threshold."""
    repo = tmp_path / "large_repo"
    repo.mkdir()
    _make_repo(repo)

    big_content = "\n".join(f"x_{i} = {i}" for i in range(600))
    (repo / "big.py").write_text(big_content + "\n")
    (repo / "small.py").write_text("x = 1\n")

    _git(["add", "."], repo)
    _git(["commit", "-m", "feat: initial"], repo)
    return str(repo)


@pytest.fixture()
def deep_nesting_repo(tmp_path: Path) -> str:
    """Repo with a Python function that has 6 levels of nesting."""
    repo = tmp_path / "nesting_repo"
    repo.mkdir()
    _make_repo(repo)

    deep_code = (
        "def deeply_nested(items):\n"
        "    for item in items:\n"
        "        if item:\n"
        "            for sub in item:\n"
        "                if sub:\n"
        "                    while True:\n"
        "                        if sub > 0:\n"
        "                            return sub\n"
        "                        break\n"
        "    return None\n"
    )
    (repo / "nested.py").write_text(deep_code)
    (repo / "clean.py").write_text("def simple(x):\n    return x + 1\n")

    _git(["add", "."], repo)
    _git(["commit", "-m", "feat: initial"], repo)
    return str(repo)


@pytest.fixture()
def excluded_dirs_repo(tmp_path: Path) -> str:
    """Repo with TODOs inside node_modules (should be excluded)."""
    repo = tmp_path / "excluded_repo"
    repo.mkdir()
    _make_repo(repo)

    (repo / "main.py").write_text("x = 1\n")
    node_modules = repo / "node_modules"
    node_modules.mkdir()
    (node_modules / "lib.js").write_text("// TODO: upstream bug\nconst x = 1;\n")

    _git(["add", "main.py"], repo)
    _git(["commit", "-m", "feat: initial"], repo)
    return str(repo)


@pytest.fixture()
def clean_repo(tmp_path: Path) -> str:
    """Repo with clean, well-structured code and no debt."""
    repo = tmp_path / "clean_repo"
    repo.mkdir()
    _make_repo(repo)

    (repo / "main.py").write_text(
        "def main() -> int:\n"
        "    return 0\n\n"
        "if __name__ == '__main__':\n"
        "    main()\n"
    )
    (repo / "utils.py").write_text(
        "def add(a: int, b: int) -> int:\n"
        "    return a + b\n"
    )

    _git(["add", "."], repo)
    _git(["commit", "-m", "feat: initial"], repo)
    return str(repo)


@pytest.fixture()
def empty_repo(tmp_path: Path) -> str:
    repo = tmp_path / "empty"
    repo.mkdir()
    _make_repo(repo)
    return str(repo)


# ---------------------------------------------------------------------------
# scan_todos tests
# ---------------------------------------------------------------------------


def test_scan_todos_returns_list(repo_with_todos: str) -> None:
    result = scan_todos(repo_with_todos)
    assert isinstance(result, list)


def test_scan_todos_finds_todos(repo_with_todos: str) -> None:
    result = scan_todos(repo_with_todos)
    types = {f["type"] for f in result}
    assert "TODO" in types


def test_scan_todos_finds_fixme(repo_with_todos: str) -> None:
    result = scan_todos(repo_with_todos)
    types = {f["type"] for f in result}
    assert "FIXME" in types


def test_scan_todos_finds_hack(repo_with_todos: str) -> None:
    result = scan_todos(repo_with_todos)
    types = {f["type"] for f in result}
    assert "HACK" in types


def test_scan_todos_finds_xxx(repo_with_todos: str) -> None:
    result = scan_todos(repo_with_todos)
    types = {f["type"] for f in result}
    assert "XXX" in types


def test_scan_todos_finds_workaround(repo_with_todos: str) -> None:
    result = scan_todos(repo_with_todos)
    types = {f["type"] for f in result}
    assert "WORKAROUND" in types


def test_scan_todos_structure(repo_with_todos: str) -> None:
    result = scan_todos(repo_with_todos)
    for f in result:
        assert "path" in f
        assert "line" in f
        assert "type" in f
        assert "text" in f
        assert "author" in f
        assert isinstance(f["line"], int)
        assert f["line"] >= 1


def test_scan_todos_sorted_by_path_and_line(repo_with_todos: str) -> None:
    result = scan_todos(repo_with_todos)
    keys = [(f["path"], f["line"]) for f in result]
    assert keys == sorted(keys)


def test_scan_todos_excludes_node_modules(excluded_dirs_repo: str) -> None:
    result = scan_todos(excluded_dirs_repo)
    for f in result:
        assert "node_modules" not in f["path"]


def test_scan_todos_empty_repo(empty_repo: str) -> None:
    result = scan_todos(empty_repo)
    assert result == []


def test_scan_todos_clean_repo(clean_repo: str) -> None:
    result = scan_todos(clean_repo)
    assert result == []


def test_scan_todos_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        scan_todos(str(tmp_path))


def test_scan_todos_correct_line_numbers(repo_with_todos: str) -> None:
    result = scan_todos(repo_with_todos)
    for f in result:
        if f["path"] == "main.py" and f["type"] == "TODO":
            assert f["line"] == 1
            break


# ---------------------------------------------------------------------------
# find_large_files tests
# ---------------------------------------------------------------------------


def test_find_large_files_returns_list(large_file_repo: str) -> None:
    result = find_large_files(large_file_repo)
    assert isinstance(result, list)


def test_find_large_files_finds_large_file(large_file_repo: str) -> None:
    result = find_large_files(large_file_repo, threshold_lines=500)
    paths = [f["path"] for f in result]
    assert "big.py" in paths


def test_find_large_files_excludes_small_file(large_file_repo: str) -> None:
    result = find_large_files(large_file_repo, threshold_lines=500)
    paths = [f["path"] for f in result]
    assert "small.py" not in paths


def test_find_large_files_structure(large_file_repo: str) -> None:
    result = find_large_files(large_file_repo)
    for f in result:
        assert "path" in f
        assert "lines" in f
        assert "language" in f


def test_find_large_files_sorted_descending(large_file_repo: str) -> None:
    result = find_large_files(large_file_repo, threshold_lines=1)
    lines = [f["lines"] for f in result]
    assert lines == sorted(lines, reverse=True)


def test_find_large_files_language_detected(large_file_repo: str) -> None:
    result = find_large_files(large_file_repo, threshold_lines=500)
    big = next(f for f in result if f["path"] == "big.py")
    assert big["language"] == "Python"


def test_find_large_files_custom_threshold(large_file_repo: str) -> None:
    result_all = find_large_files(large_file_repo, threshold_lines=1)
    result_none = find_large_files(large_file_repo, threshold_lines=10000)
    assert len(result_all) >= len(result_none)


def test_find_large_files_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        find_large_files(str(tmp_path))


def test_find_large_files_empty_repo(empty_repo: str) -> None:
    result = find_large_files(empty_repo)
    assert result == []


# ---------------------------------------------------------------------------
# find_deep_nesting tests
# ---------------------------------------------------------------------------


def test_find_deep_nesting_returns_list(deep_nesting_repo: str) -> None:
    result = find_deep_nesting(deep_nesting_repo)
    assert isinstance(result, list)


def test_find_deep_nesting_finds_violation(deep_nesting_repo: str) -> None:
    result = find_deep_nesting(deep_nesting_repo, max_depth=4)
    assert len(result) >= 1


def test_find_deep_nesting_structure(deep_nesting_repo: str) -> None:
    result = find_deep_nesting(deep_nesting_repo, max_depth=4)
    for f in result:
        assert "path" in f
        assert "function" in f
        assert "line" in f
        assert "depth" in f
        assert isinstance(f["depth"], int)
        assert f["depth"] >= 1


def test_find_deep_nesting_sorted_by_depth_descending(deep_nesting_repo: str) -> None:
    result = find_deep_nesting(deep_nesting_repo, max_depth=1)
    depths = [f["depth"] for f in result]
    assert depths == sorted(depths, reverse=True)


def test_find_deep_nesting_depth_above_threshold(deep_nesting_repo: str) -> None:
    max_depth = 4
    result = find_deep_nesting(deep_nesting_repo, max_depth=max_depth)
    for f in result:
        assert f["depth"] > max_depth


def test_find_deep_nesting_python_function_name(deep_nesting_repo: str) -> None:
    result = find_deep_nesting(deep_nesting_repo, max_depth=4)
    py_findings = [f for f in result if f["path"].endswith(".py")]
    if py_findings:
        assert py_findings[0]["function"] != ""


def test_find_deep_nesting_clean_code(clean_repo: str) -> None:
    result = find_deep_nesting(clean_repo, max_depth=4)
    assert result == []


def test_find_deep_nesting_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        find_deep_nesting(str(tmp_path))


def test_find_deep_nesting_empty_repo(empty_repo: str) -> None:
    result = find_deep_nesting(empty_repo)
    assert result == []


# ---------------------------------------------------------------------------
# calculate_tech_debt_score tests
# ---------------------------------------------------------------------------


def test_calculate_tech_debt_score_returns_dict(clean_repo: str) -> None:
    result = calculate_tech_debt_score(clean_repo)
    assert isinstance(result, dict)


def test_calculate_tech_debt_score_structure(clean_repo: str) -> None:
    result = calculate_tech_debt_score(clean_repo)
    assert "score" in result
    assert "grade" in result
    assert "breakdown" in result
    assert "top_issues" in result


def test_calculate_tech_debt_score_range(clean_repo: str) -> None:
    result = calculate_tech_debt_score(clean_repo)
    assert 0 <= result["score"] <= 100


def test_calculate_tech_debt_grade_valid(clean_repo: str) -> None:
    result = calculate_tech_debt_score(clean_repo)
    assert result["grade"] in ("A", "B", "C", "D", "F")


def test_calculate_tech_debt_clean_repo_grade(clean_repo: str) -> None:
    result = calculate_tech_debt_score(clean_repo)
    assert result["grade"] in ("A", "B")


def test_calculate_tech_debt_top_issues_list(clean_repo: str) -> None:
    result = calculate_tech_debt_score(clean_repo)
    assert isinstance(result["top_issues"], list)


def test_calculate_tech_debt_breakdown_keys(clean_repo: str) -> None:
    result = calculate_tech_debt_score(clean_repo)
    breakdown = result["breakdown"]
    assert "todo_count" in breakdown
    assert "large_file_count" in breakdown
    assert "total_source_lines" in breakdown
    assert "total_source_files" in breakdown


def test_calculate_tech_debt_higher_score_for_debt(
    clean_repo: str, repo_with_todos: str
) -> None:
    clean_score = calculate_tech_debt_score(clean_repo)["score"]
    debt_score = calculate_tech_debt_score(repo_with_todos)["score"]
    assert debt_score >= clean_score


def test_calculate_tech_debt_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        calculate_tech_debt_score(str(tmp_path))


def test_calculate_tech_debt_todo_count_in_breakdown(repo_with_todos: str) -> None:
    result = calculate_tech_debt_score(repo_with_todos)
    assert result["breakdown"]["todo_count"] >= 5


def test_calculate_tech_debt_large_file_flagged(large_file_repo: str) -> None:
    result = calculate_tech_debt_score(large_file_repo)
    assert result["breakdown"]["large_file_count"] >= 1


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------


def test_ext_to_language_python() -> None:
    assert _ext_to_language(".py") == "Python"


def test_ext_to_language_javascript() -> None:
    assert _ext_to_language(".js") == "JavaScript"


def test_ext_to_language_typescript() -> None:
    assert _ext_to_language(".ts") == "TypeScript"


def test_ext_to_language_unknown() -> None:
    assert _ext_to_language(".xyz") == "Unknown"


def test_score_to_grade_a() -> None:
    assert _score_to_grade(5) == "A"


def test_score_to_grade_b() -> None:
    assert _score_to_grade(20) == "B"


def test_score_to_grade_c() -> None:
    assert _score_to_grade(35) == "C"


def test_score_to_grade_d() -> None:
    assert _score_to_grade(55) == "D"


def test_score_to_grade_f() -> None:
    assert _score_to_grade(75) == "F"
