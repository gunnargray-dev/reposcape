"""Tests for treemap generation."""

from __future__ import annotations

from pathlib import Path

from src.treemap import TreemapNode, build_treemap


def _names(node: TreemapNode) -> set[str]:
    return {c.name for c in node.children}


def test_build_treemap_from_explicit_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "a").mkdir()
    (repo / "a" / "x.py").write_text("print('x')\n\n")

    (repo / "b").mkdir()
    (repo / "b" / "y.py").write_text("print('y')\nprint('yy')\n")

    root = build_treemap(repo, file_paths=[repo / "a" / "x.py", repo / "b" / "y.py"])

    assert root.name == "repo"
    assert _names(root) == {"a", "b"}

    a = [c for c in root.children if c.name == "a"][0]
    b = [c for c in root.children if c.name == "b"][0]

    assert a.value == 1
    assert b.value == 2
    assert root.value == 3


def test_build_treemap_ignores_dot_git(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / ".git").mkdir()
    (repo / ".git" / "ignore.txt").write_text("no\n")

    (repo / "ok.py").write_text("x=1\n")

    root = build_treemap(repo)
    assert _names(root) == {"ok.py"}
    assert root.value == 1


def test_build_treemap_relative_file_paths_ok(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "src").mkdir()
    (repo / "src" / "main.py").write_text("x=1\n")

    root = build_treemap(repo, file_paths=[Path("src/main.py")])
    assert root.value == 1


def test_build_treemap_outside_repo_ignored(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "ok.py").write_text("x=1\n")

    outside = tmp_path / "outside.py"
    outside.write_text("x=1\n")

    root = build_treemap(repo, file_paths=[repo / "ok.py", outside])
    assert root.value == 1


def test_build_treemap_children_sorted(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "b.py").write_text("x=1\n")
    (repo / "a.py").write_text("x=1\n")

    root = build_treemap(repo)
    assert [c.name for c in root.children] == ["a.py", "b.py"]
