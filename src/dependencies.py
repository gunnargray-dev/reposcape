"""Dependency graph builder for Python and JavaScript/TypeScript repositories.

Parses import statements across .py, .js, .ts, .jsx, and .tsx files to build
a directed graph of module relationships, detect circular dependencies, and
compute topological layer ordering for architecture visualization.
"""

from __future__ import annotations

import ast
import os
import re
from collections import defaultdict, deque
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PY_EXTENSIONS: frozenset[str] = frozenset({".py"})
_JS_EXTENSIONS: frozenset[str] = frozenset({".js", ".ts", ".jsx", ".tsx"})
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

# Regex patterns for JS/TS import forms
_JS_IMPORT_RE = re.compile(
    r"""
    (?:
        import\s+(?:[\w*{}\s,]+\s+from\s+)?   # import ... from
        |const\s+[\w{}\s,]+\s*=\s*require\s*\(  # const x = require(
    )
    ['"]([^'"]+)['"]                            # module path/name
    """,
    re.VERBOSE,
)
_JS_DYNAMIC_IMPORT_RE = re.compile(
    r"""import\s*\(\s*['"]([^'"]+)['"]\s*\)""",
    re.VERBOSE,
)


# ---------------------------------------------------------------------------
# Python import parser
# ---------------------------------------------------------------------------


def parse_python_imports(file_path: str) -> list[dict]:
    """Parse a Python source file and extract all import statements.

    Uses Python's ``ast`` module for accurate parsing. Both ``import X``
    and ``from X import Y`` forms are handled, including relative imports.

    Args:
        file_path: Absolute or relative path to the ``.py`` file.

    Returns:
        List of import dicts, each containing:
            module (str): The imported module name (e.g. ``"os.path"``).
            names (list[str]): Specific names imported (empty for plain imports).
            is_relative (bool): True if the import uses a relative dot prefix.
            line (int): Line number of the import statement.

        Returns an empty list if the file cannot be parsed or does not exist.
    """
    path = Path(file_path)
    if not path.is_file():
        return []

    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []
    except OSError:
        return []

    imports: list[dict] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(
                    {
                        "module": alias.name,
                        "names": [],
                        "is_relative": False,
                        "line": node.lineno,
                    }
                )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            is_relative = (node.level or 0) > 0
            if is_relative and module:
                module = "." * node.level + module
            elif is_relative:
                module = "." * node.level
            names = [alias.name for alias in node.names]
            imports.append(
                {
                    "module": module,
                    "names": names,
                    "is_relative": is_relative,
                    "line": node.lineno,
                }
            )

    return imports


# ---------------------------------------------------------------------------
# JavaScript / TypeScript import parser
# ---------------------------------------------------------------------------


def parse_js_imports(file_path: str) -> list[dict]:
    """Parse a JS/TS source file and extract import/require statements.

    Uses regex to handle ES module ``import`` syntax and CommonJS
    ``require()`` calls. Dynamic ``import()`` expressions are also captured.

    Args:
        file_path: Absolute or relative path to the JS/TS file.

    Returns:
        List of import dicts, each containing:
            module (str): The module specifier (e.g. ``"./utils"``).
            names (list[str]): Named imports extracted from the statement.
            is_relative (bool): True if the specifier starts with ``.`` or ``..``.
            line (int): Approximate line number of the import statement.

        Returns an empty list if the file cannot be read or does not exist.
    """
    path = Path(file_path)
    if not path.is_file():
        return []

    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    lines = source.splitlines()
    imports: list[dict] = []

    # Build a char-offset -> line map for approximate line numbers
    offset_map: list[int] = []
    for lineno, line in enumerate(lines, start=1):
        for _ in line:
            offset_map.append(lineno)
        offset_map.append(lineno)  # newline char

    def _offset_to_line(offset: int) -> int:
        if offset < len(offset_map):
            return offset_map[offset]
        return len(lines)

    # Named imports pattern: import { A, B } from '...'
    _named_re = re.compile(r"import\s*\{([^}]*)\}\s*from\s*['\"]([^'\"]+)['\"]")
    seen_offsets: set[int] = set()

    for m in _named_re.finditer(source):
        names_raw = [n.strip().split(" as ")[0].strip() for n in m.group(1).split(",")]
        names = [n for n in names_raw if n]
        module = m.group(2)
        lineno = _offset_to_line(m.start())
        imports.append(
            {
                "module": module,
                "names": names,
                "is_relative": module.startswith("."),
                "line": lineno,
            }
        )
        seen_offsets.add(m.start())

    # General import/require regex (avoids duplicates from named imports)
    for m in _JS_IMPORT_RE.finditer(source):
        if m.start() in seen_offsets:
            continue
        module = m.group(1)
        lineno = _offset_to_line(m.start())
        imports.append(
            {
                "module": module,
                "names": [],
                "is_relative": module.startswith("."),
                "line": lineno,
            }
        )

    # Dynamic import()
    for m in _JS_DYNAMIC_IMPORT_RE.finditer(source):
        module = m.group(1)
        lineno = _offset_to_line(m.start())
        imports.append(
            {
                "module": module,
                "names": [],
                "is_relative": module.startswith("."),
                "line": lineno,
            }
        )

    imports.sort(key=lambda x: x["line"])
    return imports


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_python_import(
    module: str,
    is_relative: bool,
    source_file: str,
    repo_root: Path,
    py_files: set[str],
) -> Optional[str]:
    """Attempt to resolve a Python import to a repo-relative module path.

    Args:
        module: Module name from the import statement.
        is_relative: True for relative imports (starts with dots).
        source_file: Repo-relative path of the file containing the import.
        repo_root: Absolute path to the repository root.
        py_files: Set of all known repo-relative .py paths.

    Returns:
        Repo-relative path string if resolved, else None.
    """
    if is_relative:
        # Strip leading dots and resolve relative to parent package
        dots = len(module) - len(module.lstrip("."))
        rel_module = module.lstrip(".")
        source_parts = Path(source_file).parent.parts
        base_parts = list(source_parts[: max(0, len(source_parts) - (dots - 1))])
        if rel_module:
            candidate_parts = base_parts + rel_module.split(".")
        else:
            candidate_parts = base_parts
        candidate = Path(*candidate_parts).with_suffix(".py") if candidate_parts else None
        if candidate:
            candidate_str = str(candidate)
            if candidate_str in py_files:
                return candidate_str
        # Try as package __init__.py
        if candidate_parts:
            init_candidate = str(Path(*candidate_parts) / "__init__.py")
            if init_candidate in py_files:
                return init_candidate
        return None

    # Absolute import: try module as path
    parts = module.split(".")
    candidate = Path(*parts).with_suffix(".py")
    candidate_str = str(candidate)
    if candidate_str in py_files:
        return candidate_str
    # Try as package
    init_candidate = str(Path(*parts) / "__init__.py")
    if init_candidate in py_files:
        return init_candidate
    return None


def _resolve_js_import(
    module: str,
    source_file: str,
    repo_root: Path,
    js_files: set[str],
) -> Optional[str]:
    """Resolve a JS/TS import specifier to a repo-relative file path.

    Only resolves relative imports (starting with . or ..). Third-party
    package imports are not resolved.

    Args:
        module: The import specifier string.
        source_file: Repo-relative path of the importing file.
        repo_root: Absolute path to the repository root.
        js_files: Set of all known repo-relative JS/TS paths.

    Returns:
        Repo-relative path string if resolved, else None.
    """
    if not module.startswith("."):
        return None

    source_dir = Path(source_file).parent
    raw = source_dir / module

    # Try exact match first (module may already have extension)
    raw_str = str(raw)
    if raw_str in js_files:
        return raw_str

    # Try appending extensions
    for ext in (".js", ".ts", ".jsx", ".tsx"):
        candidate = str(raw.with_suffix(ext) if raw.suffix == "" else Path(raw_str + ext))
        # Normalise path
        candidate_norm = str(Path(raw_str + ext))
        if candidate_norm in js_files:
            return candidate_norm

    # Try index file in directory
    for ext in (".js", ".ts", ".jsx", ".tsx"):
        index_candidate = str(raw / f"index{ext}")
        if index_candidate in js_files:
            return index_candidate

    return None


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------


def build_dependency_graph(repo_path: str) -> dict:
    """Walk a repository and build a directed module dependency graph.

    Parses all ``.py``, ``.js``, ``.ts``, ``.jsx``, and ``.tsx`` files,
    resolves relative imports within the repo, and returns a graph suitable
    for dependency visualization.

    Args:
        repo_path: Absolute path to the root of the repository.

    Returns:
        Dict with keys:
            nodes (list[dict]): Each node has ``id`` (repo-relative path),
                ``path`` (same), ``language`` (str), ``imports_count`` (int).
            edges (list[dict]): Each edge has ``source`` (str), ``target``
                (str), ``imports`` (list[str] of imported names).
            stats (dict): ``total_modules`` (int), ``total_edges`` (int),
                ``avg_imports`` (float), ``most_imported`` (str),
                ``most_dependent`` (str).
    """
    root = Path(repo_path).resolve()

    # Collect all source files
    py_files: set[str] = set()
    js_files: set[str] = set()

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            rel = str(fpath.relative_to(root))
            ext = fpath.suffix.lower()
            if ext in _PY_EXTENSIONS:
                py_files.add(rel)
            elif ext in _JS_EXTENSIONS:
                js_files.add(rel)

    all_files = py_files | js_files

    # Parse imports per file
    raw_edges: list[tuple[str, str, list[str]]] = []
    imports_per_file: dict[str, int] = {}
    imported_by: dict[str, int] = defaultdict(int)

    for rel_path in sorted(all_files):
        abs_path = str(root / rel_path)
        ext = Path(rel_path).suffix.lower()

        if ext in _PY_EXTENSIONS:
            parsed = parse_python_imports(abs_path)
            imports_per_file[rel_path] = len(parsed)
            for imp in parsed:
                target = _resolve_python_import(
                    imp["module"], imp["is_relative"], rel_path, root, py_files
                )
                if target and target != rel_path:
                    raw_edges.append((rel_path, target, imp["names"]))
                    imported_by[target] += 1
        else:
            parsed = parse_js_imports(abs_path)
            imports_per_file[rel_path] = len(parsed)
            for imp in parsed:
                target = _resolve_js_import(imp["module"], rel_path, root, js_files)
                if target and target != rel_path:
                    raw_edges.append((rel_path, target, imp["names"]))
                    imported_by[target] += 1

    # Build nodes
    nodes: list[dict] = []
    for rel_path in sorted(all_files):
        ext = Path(rel_path).suffix.lower()
        if ext in _PY_EXTENSIONS:
            lang = "Python"
        elif ext in {".ts", ".tsx"}:
            lang = "TypeScript"
        else:
            lang = "JavaScript"
        nodes.append(
            {
                "id": rel_path,
                "path": rel_path,
                "language": lang,
                "imports_count": imports_per_file.get(rel_path, 0),
            }
        )

    # Deduplicate edges (merge imports for same source->target pair)
    edge_map: dict[tuple[str, str], list[str]] = {}
    for source, target, names in raw_edges:
        key = (source, target)
        if key not in edge_map:
            edge_map[key] = []
        edge_map[key].extend(names)

    edges: list[dict] = [
        {"source": src, "target": tgt, "imports": list(dict.fromkeys(names))}
        for (src, tgt), names in sorted(edge_map.items())
    ]

    # Stats
    total_modules = len(nodes)
    total_edges = len(edges)
    avg_imports = (
        round(sum(imports_per_file.values()) / total_modules, 2) if total_modules else 0.0
    )
    most_imported = max(imported_by, key=imported_by.get) if imported_by else ""
    dependent_counts: dict[str, int] = defaultdict(int)
    for src, _ in edge_map:
        dependent_counts[src] += 1
    most_dependent = max(dependent_counts, key=dependent_counts.get) if dependent_counts else ""

    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "total_modules": total_modules,
            "total_edges": total_edges,
            "avg_imports": avg_imports,
            "most_imported": most_imported,
            "most_dependent": most_dependent,
        },
    }


# ---------------------------------------------------------------------------
# Circular dependency detection
# ---------------------------------------------------------------------------


def find_circular_dependencies(graph: dict) -> list[list[str]]:
    """Find all circular dependency chains in a dependency graph.

    Uses iterative DFS (depth-first search) with a recursion stack to detect
    back-edges, which indicate cycles. Each cycle is returned as an ordered
    list of node IDs representing one complete cycle path.

    Args:
        graph: Dict returned by :func:`build_dependency_graph`, containing
            ``nodes`` and ``edges`` keys.

    Returns:
        List of cycles. Each cycle is a list of node ID strings forming a
        closed loop (the first and last element are the same node).
        Returns an empty list if no cycles are found.
    """
    # Build adjacency list
    adj: dict[str, list[str]] = defaultdict(list)
    node_ids: set[str] = {n["id"] for n in graph.get("nodes", [])}
    for edge in graph.get("edges", []):
        adj[edge["source"]].append(edge["target"])

    visited: set[str] = set()
    rec_stack: set[str] = set()
    cycles: list[list[str]] = []

    def _dfs(node: str, path: list[str]) -> None:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbour in adj.get(node, []):
            if neighbour not in node_ids:
                continue
            if neighbour not in visited:
                _dfs(neighbour, path)
            elif neighbour in rec_stack:
                # Found a cycle -- extract the loop portion
                cycle_start = path.index(neighbour)
                cycle = path[cycle_start:] + [neighbour]
                # Avoid duplicate cycles (same set of nodes)
                cycle_set = frozenset(cycle[:-1])
                if not any(frozenset(c[:-1]) == cycle_set for c in cycles):
                    cycles.append(cycle)

        path.pop()
        rec_stack.discard(node)

    for node in sorted(node_ids):
        if node not in visited:
            _dfs(node, [])

    return cycles


# ---------------------------------------------------------------------------
# Topological layer ordering
# ---------------------------------------------------------------------------


def get_dependency_layers(graph: dict) -> list[list[str]]:
    """Topologically sort modules into dependency layers (Kahn's algorithm).

    Leaf modules (no dependencies on other repo modules) appear in the first
    layer. Modules that depend only on layer-0 modules appear in layer 1, and
    so on. Modules involved in cycles are placed in the final layer.

    Args:
        graph: Dict returned by :func:`build_dependency_graph`.

    Returns:
        List of layers. Each layer is a sorted list of node ID strings.
        Layer 0 contains leaf/standalone modules; higher layers contain
        modules that depend on earlier layers.
    """
    node_ids: set[str] = {n["id"] for n in graph.get("nodes", [])}
    in_degree: dict[str, int] = {n: 0 for n in node_ids}
    adj: dict[str, list[str]] = defaultdict(list)

    for edge in graph.get("edges", []):
        src, tgt = edge["source"], edge["target"]
        if src in node_ids and tgt in node_ids:
            adj[src].append(tgt)
            in_degree[tgt] = in_degree.get(tgt, 0) + 1

    # BFS (Kahn's algorithm)
    queue: deque[str] = deque(
        sorted(node for node, deg in in_degree.items() if deg == 0)
    )
    layers: list[list[str]] = []
    processed: set[str] = set()

    while queue:
        layer_size = len(queue)
        current_layer: list[str] = []
        for _ in range(layer_size):
            node = queue.popleft()
            current_layer.append(node)
            processed.add(node)
            for neighbour in adj.get(node, []):
                in_degree[neighbour] -= 1
                if in_degree[neighbour] == 0:
                    queue.append(neighbour)
        layers.append(sorted(current_layer))

    # Any remaining nodes are part of a cycle
    cycle_nodes = sorted(node_ids - processed)
    if cycle_nodes:
        layers.append(cycle_nodes)

    return layers
