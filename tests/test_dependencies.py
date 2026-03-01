"""Tests for src/dependencies.py -- dependency graph builder."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from src.dependencies import (
    build_dependency_graph,
    find_circular_dependencies,
    get_dependency_layers,
    parse_js_imports,
    parse_python_imports,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(tmp: Path, rel: str, content: str) -> Path:
    """Write *content* to *tmp/rel*, creating parent dirs."""
    p = tmp / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


# ===========================================================================
# parse_python_imports
# ===========================================================================


class TestParsePythonImports:
    def test_plain_import(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "import os\n")
        result = parse_python_imports(str(f))
        assert any(r["module"] == "os" for r in result)

    def test_from_import(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "from pathlib import Path\n")
        result = parse_python_imports(str(f))
        assert result[0]["module"] == "pathlib"
        assert "Path" in result[0]["names"]

    def test_from_import_multiple_names(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "from os import path, getcwd\n")
        result = parse_python_imports(str(f))
        assert "path" in result[0]["names"]
        assert "getcwd" in result[0]["names"]

    def test_relative_import(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "pkg/a.py", "from .utils import helper\n")
        result = parse_python_imports(str(f))
        assert result[0]["is_relative"] is True
        assert "helper" in result[0]["names"]

    def test_relative_import_double_dot(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "pkg/sub/a.py", "from ..models import User\n")
        result = parse_python_imports(str(f))
        assert result[0]["is_relative"] is True

    def test_multi_import_statement(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "import os, sys\n")
        result = parse_python_imports(str(f))
        modules = [r["module"] for r in result]
        assert "os" in modules
        assert "sys" in modules

    def test_line_numbers(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "import os\nimport sys\n")
        result = parse_python_imports(str(f))
        lines = [r["line"] for r in result]
        assert 1 in lines
        assert 2 in lines

    def test_empty_file(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "")
        assert parse_python_imports(str(f)) == []

    def test_file_no_imports(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "x = 1\n")
        assert parse_python_imports(str(f)) == []

    def test_syntax_error_returns_empty(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "def broken(\n")
        assert parse_python_imports(str(f)) == []

    def test_nonexistent_file_returns_empty(self) -> None:
        assert parse_python_imports("/nonexistent/path/file.py") == []

    def test_is_relative_false_for_stdlib(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "import json\n")
        result = parse_python_imports(str(f))
        assert result[0]["is_relative"] is False

    def test_dotted_module(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "import os.path\n")
        result = parse_python_imports(str(f))
        assert result[0]["module"] == "os.path"

    def test_from_future_import(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.py", "from __future__ import annotations\n")
        result = parse_python_imports(str(f))
        assert result[0]["module"] == "__future__"
        assert "annotations" in result[0]["names"]


# ===========================================================================
# parse_js_imports
# ===========================================================================


class TestParseJsImports:
    def test_import_from(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.js", "import React from 'react';\n")
        result = parse_js_imports(str(f))
        assert any(r["module"] == "react" for r in result)

    def test_require(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.js", "const fs = require('fs');\n")
        result = parse_js_imports(str(f))
        assert any(r["module"] == "fs" for r in result)

    def test_destructured_import(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.ts", "import { useState, useEffect } from 'react';\n")
        result = parse_js_imports(str(f))
        assert any(r["module"] == "react" for r in result)
        react_imp = next(r for r in result if r["module"] == "react")
        assert "useState" in react_imp["names"]
        assert "useEffect" in react_imp["names"]

    def test_relative_import_is_relative(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.js", "import utils from './utils';\n")
        result = parse_js_imports(str(f))
        assert any(r["is_relative"] is True for r in result)

    def test_package_import_not_relative(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.js", "import lodash from 'lodash';\n")
        result = parse_js_imports(str(f))
        assert any(r["is_relative"] is False for r in result)

    def test_empty_file_returns_empty(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.js", "")
        assert parse_js_imports(str(f)) == []

    def test_file_no_imports_returns_empty(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.js", "const x = 1;\n")
        assert parse_js_imports(str(f)) == []

    def test_nonexistent_file_returns_empty(self) -> None:
        assert parse_js_imports("/nonexistent/file.js") == []

    def test_tsx_file(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "App.tsx", "import React from 'react';\nimport { Button } from './Button';\n")
        result = parse_js_imports(str(f))
        modules = [r["module"] for r in result]
        assert "react" in modules

    def test_line_numbers_populated(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.js", "import A from 'a';\nimport B from 'b';\n")
        result = parse_js_imports(str(f))
        assert all(r["line"] >= 1 for r in result)


# ===========================================================================
# build_dependency_graph
# ===========================================================================


class TestBuildDependencyGraph:
    def _make_simple_repo(self, tmp: Path) -> None:
        _write(tmp, "src/main.py", "from src.utils import helper\n")
        _write(tmp, "src/utils.py", "def helper(): pass\n")

    def test_nodes_present(self, tmp_path: Path) -> None:
        self._make_simple_repo(tmp_path)
        graph = build_dependency_graph(str(tmp_path))
        node_ids = {n["id"] for n in graph["nodes"]}
        assert "src/main.py" in node_ids
        assert "src/utils.py" in node_ids

    def test_stats_keys_present(self, tmp_path: Path) -> None:
        _write(tmp_path, "a.py", "import os\n")
        graph = build_dependency_graph(str(tmp_path))
        for key in ("total_modules", "total_edges", "avg_imports", "most_imported", "most_dependent"):
            assert key in graph["stats"]

    def test_empty_repo_returns_empty_graph(self, tmp_path: Path) -> None:
        graph = build_dependency_graph(str(tmp_path))
        assert graph["nodes"] == []
        assert graph["edges"] == []

    def test_internal_edge_resolved(self, tmp_path: Path) -> None:
        _write(tmp_path, "pkg/__init__.py", "")
        _write(tmp_path, "pkg/a.py", "from pkg.b import something\n")
        _write(tmp_path, "pkg/b.py", "something = 1\n")
        graph = build_dependency_graph(str(tmp_path))
        edges = [(e["source"], e["target"]) for e in graph["edges"]]
        assert ("pkg/a.py", "pkg/b.py") in edges

    def test_external_imports_not_in_edges(self, tmp_path: Path) -> None:
        _write(tmp_path, "a.py", "import os\nimport sys\n")
        graph = build_dependency_graph(str(tmp_path))
        # os and sys are external, so no edges should appear
        assert graph["edges"] == []

    def test_node_language_python(self, tmp_path: Path) -> None:
        _write(tmp_path, "a.py", "x = 1\n")
        graph = build_dependency_graph(str(tmp_path))
        node = next(n for n in graph["nodes"] if n["id"] == "a.py")
        assert node["language"] == "Python"

    def test_node_language_typescript(self, tmp_path: Path) -> None:
        _write(tmp_path, "a.ts", "export const x = 1;\n")
        graph = build_dependency_graph(str(tmp_path))
        node = next(n for n in graph["nodes"] if n["id"] == "a.ts")
        assert node["language"] == "TypeScript"

    def test_node_imports_count(self, tmp_path: Path) -> None:
        _write(tmp_path, "a.py", "import os\nimport sys\n")
        graph = build_dependency_graph(str(tmp_path))
        node = next(n for n in graph["nodes"] if n["id"] == "a.py")
        assert node["imports_count"] == 2

    def test_skip_dirs_excluded(self, tmp_path: Path) -> None:
        _write(tmp_path, "__pycache__/cached.py", "x = 1\n")
        _write(tmp_path, "real.py", "x = 1\n")
        graph = build_dependency_graph(str(tmp_path))
        node_ids = {n["id"] for n in graph["nodes"]}
        assert not any("__pycache__" in nid for nid in node_ids)

    def test_syntax_error_file_handled(self, tmp_path: Path) -> None:
        _write(tmp_path, "bad.py", "def broken(\n")
        _write(tmp_path, "good.py", "x = 1\n")
        # Should not raise
        graph = build_dependency_graph(str(tmp_path))
        node_ids = {n["id"] for n in graph["nodes"]}
        assert "good.py" in node_ids


# ===========================================================================
# find_circular_dependencies
# ===========================================================================


class TestFindCircularDependencies:
    def _make_graph(self, nodes: list[str], edges: list[tuple[str, str]]) -> dict:
        return {
            "nodes": [{"id": n} for n in nodes],
            "edges": [{"source": s, "target": t, "imports": []} for s, t in edges],
        }

    def test_no_cycles_returns_empty(self) -> None:
        graph = self._make_graph(["a", "b", "c"], [("a", "b"), ("b", "c")])
        assert find_circular_dependencies(graph) == []

    def test_simple_cycle_detected(self) -> None:
        graph = self._make_graph(["a", "b"], [("a", "b"), ("b", "a")])
        cycles = find_circular_dependencies(graph)
        assert len(cycles) >= 1

    def test_three_node_cycle(self) -> None:
        graph = self._make_graph(["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")])
        cycles = find_circular_dependencies(graph)
        assert len(cycles) >= 1
        # All nodes should appear in a cycle
        all_nodes_in_cycles = {n for cycle in cycles for n in cycle}
        assert {"a", "b", "c"}.issubset(all_nodes_in_cycles)

    def test_self_loop(self) -> None:
        graph = self._make_graph(["a"], [("a", "a")])
        # Self-loop should not crash; may or may not be reported as cycle
        result = find_circular_dependencies(graph)
        assert isinstance(result, list)

    def test_empty_graph(self) -> None:
        assert find_circular_dependencies({"nodes": [], "edges": []}) == []

    def test_cycle_nodes_are_lists(self) -> None:
        graph = self._make_graph(["a", "b"], [("a", "b"), ("b", "a")])
        cycles = find_circular_dependencies(graph)
        for cycle in cycles:
            assert isinstance(cycle, list)


# ===========================================================================
# get_dependency_layers
# ===========================================================================


class TestGetDependencyLayers:
    def _make_graph(self, nodes: list[str], edges: list[tuple[str, str]]) -> dict:
        return {
            "nodes": [{"id": n} for n in nodes],
            "edges": [{"source": s, "target": t, "imports": []} for s, t in edges],
        }

    def test_linear_chain_order(self) -> None:
        # a -> b -> c (a imports b, b imports c)
        # Kahn's algorithm: in-degree 0 nodes go first.
        # a has in-degree 0 (nothing imports a) -> layer 0
        # b has in-degree 1 (a imports b) -> layer 1
        # c has in-degree 1 (b imports c) -> layer 2
        graph = self._make_graph(["a", "b", "c"], [("a", "b"), ("b", "c")])
        layers = get_dependency_layers(graph)
        assert len(layers) >= 2
        flat = [n for layer in layers for n in layer]
        assert flat.index("a") < flat.index("b") < flat.index("c")

    def test_all_nodes_present(self) -> None:
        graph = self._make_graph(["a", "b", "c"], [("a", "b")])
        layers = get_dependency_layers(graph)
        flat = {n for layer in layers for n in layer}
        assert flat == {"a", "b", "c"}

    def test_empty_graph(self) -> None:
        assert get_dependency_layers({"nodes": [], "edges": []}) == []

    def test_no_edges_single_layer(self) -> None:
        graph = self._make_graph(["a", "b", "c"], [])
        layers = get_dependency_layers(graph)
        # All nodes are independent, should be in one layer
        assert len(layers) == 1
        assert set(layers[0]) == {"a", "b", "c"}

    def test_cycle_nodes_in_last_layer(self) -> None:
        graph = self._make_graph(["a", "b", "c"], [("a", "b"), ("b", "a"), ("c", "a")])
        layers = get_dependency_layers(graph)
        # a and b form a cycle; c depends on a (which is in a cycle)
        # All cycle nodes should appear somewhere in layers
        flat = {n for layer in layers for n in layer}
        assert "a" in flat
        assert "b" in flat
