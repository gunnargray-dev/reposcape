"""Shared test fixtures for Reposcape.

Provides a local git repository fixture that doesn't require network access.
Network-dependent integration tests are marked with @pytest.mark.integration
and skipped by default (run with: pytest -m integration).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


def _run_git(repo_dir: str, *args: str) -> None:
    """Run a git command in the given directory."""
    subprocess.run(
        ["git", *args],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=True,
    )


@pytest.fixture(scope="session")
def local_git_repo(tmp_path_factory) -> str:
    """Create a local git repo with realistic commit history.

    This avoids all network calls while providing a repo with:
    - Multiple commits by different authors
    - Multiple languages (Python, JavaScript, Markdown)
    - Merge commits
    - TODO/FIXME comments
    - Varying file sizes and complexity
    """
    repo_dir = str(tmp_path_factory.mktemp("local_repo"))

    # Init repo
    _run_git(repo_dir, "init")
    _run_git(repo_dir, "config", "user.email", "alice@example.com")
    _run_git(repo_dir, "config", "user.name", "Alice")

    # Commit 1: initial Python files
    src_dir = Path(repo_dir) / "src"
    src_dir.mkdir()
    (src_dir / "__init__.py").write_text('"""Package init."""\n__version__ = "0.1.0"\n')
    (src_dir / "main.py").write_text(
        '"""Main module."""\n\n\ndef greet(name: str) -> str:\n'
        '    """Greet someone."""\n'
        '    # TODO: add greeting styles\n'
        '    if not name:\n'
        '        raise ValueError("empty name")\n'
        '    return f"Hello, {name}!"\n\n\n'
        'def add(a: int, b: int) -> int:\n'
        '    """Add two numbers."""\n'
        '    return a + b\n\n\n'
        'def complex_func(x: int) -> str:\n'
        '    """A function with branches."""\n'
        '    if x < 0:\n'
        '        return "negative"\n'
        '    elif x == 0:\n'
        '        return "zero"\n'
        '    elif x < 10:\n'
        '        for i in range(x):\n'
        '            if i % 2 == 0:\n'
        '                continue\n'
        '        return "small"\n'
        '    else:\n'
        '        return "large"\n'
    )
    (src_dir / "utils.py").write_text(
        '"""Utility helpers."""\n\n'
        'import os\n'
        'from src.main import greet\n\n\n'
        'def get_home() -> str:\n'
        '    """Return home directory."""\n'
        '    # FIXME: handle Windows\n'
        '    return os.path.expanduser("~")\n'
    )
    _run_git(repo_dir, "add", ".")
    _run_git(repo_dir, "commit", "-m", "feat: initial Python modules")

    # Commit 2: add JS files (different author)
    _run_git(repo_dir, "config", "user.email", "bob@example.com")
    _run_git(repo_dir, "config", "user.name", "Bob")

    js_dir = Path(repo_dir) / "frontend"
    js_dir.mkdir()
    (js_dir / "index.js").write_text(
        'import { render } from "./render.js";\n'
        'const app = require("./app");\n\n'
        'function main() {\n'
        '  if (window.ready) {\n'
        '    render();\n'
        '  } else {\n'
        '    console.log("waiting");\n'
        '  }\n'
        '}\n\n'
        'export default main;\n'
    )
    (js_dir / "render.js").write_text(
        'export function render() {\n'
        '  // HACK: temporary workaround\n'
        '  document.body.innerHTML = "<h1>Hello</h1>";\n'
        '}\n'
    )
    (js_dir / "app.js").write_text(
        'const { render } = require("./render");\n'
        'module.exports = { start: render };\n'
    )
    _run_git(repo_dir, "add", ".")
    _run_git(repo_dir, "commit", "-m", "feat: add frontend JavaScript")

    # Commit 3: add docs (back to Alice)
    _run_git(repo_dir, "config", "user.email", "alice@example.com")
    _run_git(repo_dir, "config", "user.name", "Alice")

    (Path(repo_dir) / "README.md").write_text(
        "# Test Project\n\nA test project for Reposcape.\n\n"
        "## Usage\n\n```python\nfrom src.main import greet\nprint(greet('world'))\n```\n"
    )
    (Path(repo_dir) / "setup.py").write_text(
        '"""Setup script."""\nfrom setuptools import setup\nsetup(name="testproject")\n'
    )
    _run_git(repo_dir, "add", ".")
    _run_git(repo_dir, "commit", "-m", "docs: add README and setup")

    # Commit 4: a fix (Bob)
    _run_git(repo_dir, "config", "user.email", "bob@example.com")
    _run_git(repo_dir, "config", "user.name", "Bob")

    (src_dir / "main.py").write_text(
        (src_dir / "main.py").read_text() +
        '\ndef subtract(a: int, b: int) -> int:\n'
        '    """Subtract b from a."""\n'
        '    return a - b\n'
    )
    _run_git(repo_dir, "add", ".")
    _run_git(repo_dir, "commit", "-m", "fix: add subtract function")

    # Commit 5: WIP commit (bad quality, for commit_quality tests)
    (Path(repo_dir) / ".gitignore").write_text("__pycache__/\n*.pyc\n.env\n")
    _run_git(repo_dir, "add", ".")
    _run_git(repo_dir, "commit", "-m", "wip")

    # Reset author for consistency
    _run_git(repo_dir, "config", "user.email", "alice@example.com")
    _run_git(repo_dir, "config", "user.name", "Alice")

    return repo_dir
