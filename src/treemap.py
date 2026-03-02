"""File tree analyzer and treemap data generator.

Treemap visualization typically requires a hierarchical tree with values at
leaves and aggregated values at internal nodes.

This module builds a tree based on relative paths under a repository root, and
assigns each file a numeric "size" based on lines-of-code (non-empty lines).

The core analyzer returns a TreemapNode dataclass (convenient for tests and
internal computation). The web layer should convert it to a JSON-serializable
form via `treemap_to_dict`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from .languages import count_lines


@dataclass(frozen=True)
class TreemapNode:
    """Single node in a treemap hierarchy."""

    name: str
    path: str
    value: int
    children: tuple["TreemapNode", ...] = ()


def treemap_to_dict(node: TreemapNode) -> dict:
    """Convert a TreemapNode hierarchy into a JSON-serializable dict."""

    return {
        "name": node.name,
        "path": node.path,
        "value": node.value,
        "children": [treemap_to_dict(c) for c in node.children],
    }


def _is_ignored_path(rel_path: Path, ignore: set[str]) -> bool:
    parts = set(rel_path.parts)
    return any(p in ignore for p in parts)


def _add_file(
    root: dict,
    parts: list[str],
    *,
    value: int,
    rel_path: str,
) -> None:
    node = root
    for part in parts[:-1]:
        node = node.setdefault(part, {"__files__": []})
    node.setdefault("__files__", []).append((parts[-1], value, rel_path))


def _to_node(name: str, rel_path: str, tree: dict) -> TreemapNode:
    children: list[TreemapNode] = []
    value = 0

    for file_name, file_value, file_path in tree.get("__files__", []):
        children.append(
            TreemapNode(
                name=file_name,
                path=file_path,
                value=file_value,
                children=(),
            )
        )
        value += file_value

    for child_dir_name, child_tree in tree.items():
        if child_dir_name == "__files__":
            continue
        child_rel = f"{rel_path}/{child_dir_name}" if rel_path else child_dir_name
        child = _to_node(child_dir_name, child_rel, child_tree)
        children.append(child)
        value += child.value

    children_sorted = tuple(sorted(children, key=lambda n: n.name))
    return TreemapNode(name=name, path=rel_path, value=value, children=children_sorted)


def build_treemap(
    repo_path: str | Path,
    *,
    file_paths: Optional[Iterable[str | Path]] = None,
    ignore: Optional[set[str]] = None,
) -> TreemapNode:
    """Build treemap hierarchy with LOC values.

    Args:
        repo_path: Repository root.
        file_paths: Optional explicit iterable of file paths. Defaults to all files
            under repo_path (recursive).
        ignore: Directory/file names to ignore anywhere in the path.

    Returns:
        TreemapNode rooted at the repo directory name.
    """

    root_path = Path(repo_path)
    root_name = root_path.name

    ignored = ignore or {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
        ".mypy_cache",
        ".pytest_cache",
    }

    files: Iterable[Path]
    if file_paths is None:
        files = (p for p in root_path.rglob("*") if p.is_file())
    else:
        files = (Path(p) for p in file_paths)

    tree: dict = {"__files__": []}

    for p in files:
        if not p.is_absolute():
            p = root_path / p
        try:
            rel = p.relative_to(root_path)
        except ValueError:
            continue

        if _is_ignored_path(rel, ignored):
            continue

        loc = count_lines(p)
        rel_str = str(rel).replace("\\", "/")
        _add_file(tree, rel_str.split("/"), value=loc, rel_path=rel_str)

    return _to_node(root_name, "", tree)
