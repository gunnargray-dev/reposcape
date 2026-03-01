"""Tests for src/complexity.py -- code complexity analyzer."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from src.complexity import (
    analyze_file_complexity,
    analyze_function_complexity,
    analyze_repo_complexity,
    calculate_cyclomatic_complexity,
    estimate_js_complexity,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(tmp: Path, rel: str, content: str) -> Path:
    p = tmp / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


# ===========================================================================
# calculate_cyclomatic_complexity
# ===========================================================================


class TestCalculateCyclomaticComplexity:
    def test_simple_function_is_one(self) -> None:
        src = "def f():\n    return 1\n"
        assert calculate_cyclomatic_complexity(src) == 1

    def test_one_if_adds_one(self) -> None:
        src = "def f(x):\n    if x:\n        return 1\n    return 0\n"
        assert calculate_cyclomatic_complexity(src) == 2

    def test_if_elif_adds_two(self) -> None:
        src = "def f(x):\n    if x > 0:\n        pass\n    elif x < 0:\n        pass\n"
        # if + elif (nested If in orelse) = 2 decision points
        result = calculate_cyclomatic_complexity(src)
        assert result >= 2

    def test_for_loop_adds_one(self) -> None:
        src = "for i in range(10):\n    pass\n"
        assert calculate_cyclomatic_complexity(src) == 2

    def test_while_loop_adds_one(self) -> None:
        src = "while True:\n    break\n"
        assert calculate_cyclomatic_complexity(src) == 2

    def test_try_except_adds_one(self) -> None:
        src = "try:\n    pass\nexcept Exception:\n    pass\n"
        assert calculate_cyclomatic_complexity(src) == 2

    def test_with_statement_adds_one(self) -> None:
        src = "with open('f') as fh:\n    pass\n"
        assert calculate_cyclomatic_complexity(src) == 2

    def test_boolean_and_adds_one(self) -> None:
        src = "x = a and b\n"
        assert calculate_cyclomatic_complexity(src) == 2

    def test_boolean_or_adds_one(self) -> None:
        src = "x = a or b\n"
        assert calculate_cyclomatic_complexity(src) == 2

    def test_list_comprehension_adds_one(self) -> None:
        src = "x = [i for i in range(10)]\n"
        assert calculate_cyclomatic_complexity(src) == 2

    def test_empty_string_returns_one(self) -> None:
        assert calculate_cyclomatic_complexity("") == 1

    def test_whitespace_only_returns_one(self) -> None:
        assert calculate_cyclomatic_complexity("   \n  \n") == 1

    def test_syntax_error_returns_one(self) -> None:
        assert calculate_cyclomatic_complexity("def broken(") == 1

    def test_nested_ifs_accumulate(self) -> None:
        src = (
            "def f(a, b):\n"
            "    if a:\n"
            "        if b:\n"
            "            return 1\n"
            "    return 0\n"
        )
        assert calculate_cyclomatic_complexity(src) >= 3

    def test_assert_adds_one(self) -> None:
        src = "assert x > 0\n"
        assert calculate_cyclomatic_complexity(src) == 2

    def test_ternary_expression_adds_one(self) -> None:
        src = "x = 1 if flag else 0\n"
        assert calculate_cyclomatic_complexity(src) == 2

    def test_complex_function_high_complexity(self) -> None:
        src = textwrap.dedent("""\
            def f(a, b, c, d, e):
                if a:
                    if b:
                        pass
                    elif c:
                        pass
                for i in range(10):
                    if d:
                        pass
                while e:
                    break
                try:
                    pass
                except ValueError:
                    pass
                return 1
        """)
        result = calculate_cyclomatic_complexity(src)
        assert result >= 7


# ===========================================================================
# analyze_function_complexity
# ===========================================================================


class TestAnalyzeFunctionComplexity:
    def test_single_function_returned(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "def foo():\n    return 1\n")
        result = analyze_function_complexity(str(f))
        assert len(result) == 1
        assert result[0]["name"] == "foo"

    def test_complexity_value_set(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "def foo(x):\n    if x:\n        return 1\n    return 0\n")
        result = analyze_function_complexity(str(f))
        assert result[0]["complexity"] == 2

    def test_grade_a_for_simple(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "def foo():\n    return 1\n")
        result = analyze_function_complexity(str(f))
        assert result[0]["grade"] == "A"

    def test_grade_b_for_moderate(self, tmp_path: Path) -> None:
        src = "def foo():\n" + "    if True:\n        pass\n" * 7
        f = _write(tmp_path, "a.py", src)
        result = analyze_function_complexity(str(f))
        assert result[0]["grade"] in {"B", "C"}

    def test_grade_f_for_very_complex(self, tmp_path: Path) -> None:
        src = "def foo():\n" + "    if True:\n        pass\n" * 25
        f = _write(tmp_path, "a.py", src)
        result = analyze_function_complexity(str(f))
        assert result[0]["grade"] == "F"

    def test_multiple_functions(self, tmp_path: Path) -> None:
        src = "def a():\n    return 1\ndef b():\n    if True: pass\n"
        f = _write(tmp_path, "a.py", src)
        result = analyze_function_complexity(str(f))
        assert len(result) == 2
        names = {r["name"] for r in result}
        assert names == {"a", "b"}

    def test_class_methods_included(self, tmp_path: Path) -> None:
        src = "class Foo:\n    def bar(self):\n        return 1\n"
        f = _write(tmp_path, "a.py", src)
        result = analyze_function_complexity(str(f))
        assert any("bar" in r["name"] for r in result)

    def test_method_name_qualified(self, tmp_path: Path) -> None:
        src = "class MyClass:\n    def my_method(self):\n        return 1\n"
        f = _write(tmp_path, "a.py", src)
        result = analyze_function_complexity(str(f))
        assert result[0]["name"] == "MyClass.my_method"

    def test_async_function_included(self, tmp_path: Path) -> None:
        src = "async def fetch():\n    return await something()\n"
        f = _write(tmp_path, "a.py", src)
        result = analyze_function_complexity(str(f))
        assert any(r["name"] == "fetch" for r in result)

    def test_line_number_set(self, tmp_path: Path) -> None:
        src = "\n\ndef foo():\n    return 1\n"
        f = _write(tmp_path, "a.py", src)
        result = analyze_function_complexity(str(f))
        assert result[0]["line"] == 3

    def test_lines_field_positive(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "def foo():\n    return 1\n")
        result = analyze_function_complexity(str(f))
        assert result[0]["lines"] >= 1

    def test_empty_file_returns_empty(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "")
        assert analyze_function_complexity(str(f)) == []

    def test_file_no_functions_returns_empty(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "x = 1\n")
        assert analyze_function_complexity(str(f)) == []

    def test_syntax_error_returns_empty(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "def broken(")
        assert analyze_function_complexity(str(f)) == []

    def test_nonexistent_file_returns_empty(self) -> None:
        assert analyze_function_complexity("/nonexistent/file.py") == []


# ===========================================================================
# analyze_file_complexity
# ===========================================================================


class TestAnalyzeFileComplexity:
    def test_result_keys_present(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "def foo():\n    return 1\n")
        result = analyze_file_complexity(str(f))
        for key in ("path", "total_complexity", "avg_complexity", "max_complexity", "functions", "grade", "hotspots"):
            assert key in result

    def test_empty_file_defaults(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "")
        result = analyze_file_complexity(str(f))
        assert result["functions"] == 0
        assert result["total_complexity"] == 0
        assert result["grade"] == "A"

    def test_single_simple_function(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "def foo():\n    return 1\n")
        result = analyze_file_complexity(str(f))
        assert result["functions"] == 1
        assert result["max_complexity"] == 1

    def test_hotspots_empty_for_simple_file(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "def foo():\n    return 1\ndef bar():\n    return 2\n")
        result = analyze_file_complexity(str(f))
        assert result["hotspots"] == []

    def test_hotspot_detected_for_complex_function(self, tmp_path: Path) -> None:
        src = "def complex_fn():\n" + "    if True:\n        pass\n" * 12
        f = _write(tmp_path, "a.py", src)
        result = analyze_file_complexity(str(f))
        assert len(result["hotspots"]) >= 1

    def test_avg_complexity_calculated(self, tmp_path: Path) -> None:
        src = "def a():\n    return 1\ndef b(x):\n    if x: return 1\n    return 0\n"
        f = _write(tmp_path, "a.py", src)
        result = analyze_file_complexity(str(f))
        # a=1, b=2, avg=1.5
        assert result["avg_complexity"] == 1.5


# ===========================================================================
# analyze_repo_complexity
# ===========================================================================


class TestAnalyzeRepoComplexity:
    def test_summary_keys_present(self, tmp_path: Path) -> None:
        _write(tmp_path, "a.py", "def foo():\n    return 1\n")
        result = analyze_repo_complexity(str(tmp_path))
        for key in ("total_files", "total_functions", "avg_complexity", "grade", "hotspot_files", "complexity_distribution"):
            assert key in result["summary"]

    def test_files_list_contains_file(self, tmp_path: Path) -> None:
        _write(tmp_path, "a.py", "def foo():\n    return 1\n")
        result = analyze_repo_complexity(str(tmp_path))
        assert any("a.py" in f["path"] for f in result["files"])

    def test_pycache_excluded(self, tmp_path: Path) -> None:
        _write(tmp_path, "__pycache__/cached.py", "def foo(): pass\n")
        _write(tmp_path, "real.py", "def bar(): pass\n")
        result = analyze_repo_complexity(str(tmp_path))
        paths = [f["path"] for f in result["files"]]
        assert not any("__pycache__" in p for p in paths)

    def test_complexity_distribution_keys(self, tmp_path: Path) -> None:
        _write(tmp_path, "a.py", "def foo():\n    return 1\n")
        result = analyze_repo_complexity(str(tmp_path))
        dist = result["summary"]["complexity_distribution"]
        assert set(dist.keys()) == {"A", "B", "C", "D", "F"}

    def test_hotspot_files_grade_c_or_worse(self, tmp_path: Path) -> None:
        src = "def complex_fn():\n" + "    if True:\n        pass\n" * 15
        _write(tmp_path, "complex.py", src)
        _write(tmp_path, "simple.py", "def foo():\n    return 1\n")
        result = analyze_repo_complexity(str(tmp_path))
        hotspots = result["summary"]["hotspot_files"]
        # complex.py should be in hotspots
        hotspot_names = [Path(h["path"]).name for h in hotspots]
        assert "complex.py" in hotspot_names

    def test_empty_repo_returns_empty(self, tmp_path: Path) -> None:
        result = analyze_repo_complexity(str(tmp_path))
        assert result["summary"]["total_files"] == 0
        assert result["summary"]["total_functions"] == 0


# ===========================================================================
# estimate_js_complexity
# ===========================================================================


class TestEstimateJsComplexity:
    def test_result_keys_present(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.js", "const x = 1;\n")
        result = estimate_js_complexity(str(f))
        for key in ("path", "estimated_complexity", "decision_points", "grade", "lines"):
            assert key in result

    def test_simple_file_low_complexity(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.js", "const x = 1;\nexport default x;\n")
        result = estimate_js_complexity(str(f))
        assert result["estimated_complexity"] == 1
        assert result["grade"] == "A"

    def test_if_statement_increases_complexity(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.js", "if (x > 0) { return 1; } else { return 0; }\n")
        result = estimate_js_complexity(str(f))
        assert result["estimated_complexity"] > 1

    def test_for_loop_increases_complexity(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.js", "for (let i = 0; i < 10; i++) {}\n")
        result = estimate_js_complexity(str(f))
        assert result["decision_points"] >= 1

    def test_nonexistent_file_defaults(self) -> None:
        result = estimate_js_complexity("/nonexistent/file.js")
        assert result["estimated_complexity"] == 1
        assert result["grade"] == "A"
        assert result["lines"] == 0

    def test_empty_file_returns_one(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.js", "")
        result = estimate_js_complexity(str(f))
        assert result["estimated_complexity"] == 1

    def test_logical_operators_counted(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.js", "const ok = a && b || c;\n")
        result = estimate_js_complexity(str(f))
        assert result["decision_points"] >= 2

    def test_lines_count_set(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.js", "const a = 1;\nconst b = 2;\nconst c = 3;\n")
        result = estimate_js_complexity(str(f))
        assert result["lines"] == 3

    def test_grade_grading_applied(self, tmp_path: Path) -> None:
        # Build a file with many decision keywords
        src = ("if (x) {}\n" * 25)
        f = _write(tmp_path, "a.js", src)
        result = estimate_js_complexity(str(f))
        assert result["grade"] in {"C", "D", "F"}
