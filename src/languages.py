"""Language breakdown analyzer.

Counts lines of code by language and file type across a repository,
building a structured summary suitable for treemap visualizations.
"""

from __future__ import annotations

import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Extension -> language mapping
# ---------------------------------------------------------------------------

_EXTENSION_MAP: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JSX",
    ".tsx": "TSX",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".c": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C/C++ Header",
    ".cs": "C#",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".r": "R",
    ".R": "R",
    ".m": "Objective-C",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "SCSS",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".md": "Markdown",
    ".markdown": "Markdown",
    ".txt": "Text",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".sql": "SQL",
    ".xml": "XML",
    ".toml": "TOML",
    ".ini": "INI",
    ".cfg": "INI",
}

# Directories to always skip when walking a repository
_SKIP_DIRS: frozenset[str] = frozenset(
    [
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
    ]
)


def detect_language(file_path: str) -> str:
    """Map a file path to a human-readable language name.

    Uses the file extension to determine the language. Files without a
    recognised extension are reported as "Other".

    Args:
        file_path: Path or filename to classify (only the extension matters).

    Returns:
        Language name string (e.g. "Python", "JavaScript", "Other").
    """
    ext = Path(file_path).suffix.lower()
    if ext:
        return _EXTENSION_MAP.get(ext) or _EXTENSION_MAP.get(Path(file_path).suffix, "Other")
    return "Other"


def count_lines(file_path: str) -> int:
    """Count the number of non-empty lines in a text file.

    Binary files are skipped gracefully and return 0. Files that cannot
    be decoded as UTF-8 are retried with latin-1; if that also fails the
    file is treated as binary.

    Args:
        file_path: Absolute or relative path to the file to count.

    Returns:
        Number of lines that contain at least one non-whitespace character.
        Returns 0 for binary files or files that cannot be read.
    """
    path = Path(file_path)
    if not path.is_file():
        return 0

    # Quick binary sniff: check for null bytes in the first 8 KB
    try:
        with open(path, "rb") as fh:
            chunk = fh.read(8192)
        if b"\x00" in chunk:
            return 0
    except OSError:
        return 0

    # Try reading as text
    for encoding in ("utf-8", "latin-1"):
        try:
            with open(path, "r", encoding=encoding, errors="strict") as fh:
                return sum(1 for line in fh if line.strip())
        except (UnicodeDecodeError, OSError):
            continue

    return 0


def _should_skip_dir(dir_name: str) -> bool:
    """Return True if a directory should be excluded from analysis.

    Args:
        dir_name: The bare directory name (not a full path).

    Returns:
        True if the directory is in the skip list.
    """
    return dir_name in _SKIP_DIRS


def analyze_languages(repo_path: str) -> dict:
    """Walk a repository and aggregate lines-of-code by language.

    Skips hidden/generated directories (e.g. .git, node_modules, __pycache__).
    Binary files contribute a file count of 1 but 0 lines.

    Args:
        repo_path: Absolute path to the root of the repository to analyze.

    Returns:
        Dict with keys:
            languages (list[dict]): Each entry has:
                name (str): Language name.
                files (int): Number of files in this language.
                lines (int): Total non-empty lines in this language.
                percentage (float): Percentage of total lines (0-100, 2 dp).
            total_files (int): Total number of files processed.
            total_lines (int): Total non-empty lines across all files.

        The languages list is sorted by lines descending.
    """
    root = Path(repo_path)
    lang_stats: dict[str, dict] = {}  # language -> {files, lines}
    total_files = 0

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skip dirs in-place so os.walk doesn't descend into them
        dirnames[:] = [d for d in dirnames if not _should_skip_dir(d)]

        for filename in filenames:
            file_path = Path(dirpath) / filename
            language = detect_language(str(file_path))
            lines = count_lines(str(file_path))
            total_files += 1

            if language not in lang_stats:
                lang_stats[language] = {"files": 0, "lines": 0}
            lang_stats[language]["files"] += 1
            lang_stats[language]["lines"] += lines

    total_lines = sum(v["lines"] for v in lang_stats.values())

    languages = []
    for lang_name, stats in lang_stats.items():
        pct = round((stats["lines"] / total_lines * 100), 2) if total_lines > 0 else 0.0
        languages.append(
            {
                "name": lang_name,
                "files": stats["files"],
                "lines": stats["lines"],
                "percentage": pct,
            }
        )

    languages.sort(key=lambda x: x["lines"], reverse=True)

    return {
        "languages": languages,
        "total_files": total_files,
        "total_lines": total_lines,
    }


def get_file_tree(repo_path: str) -> list[dict]:
    """Return a flat list of all files in a repository with metadata.

    Intended for use in treemap visualizations where each file is a leaf
    node. Skips the same directories as analyze_languages.

    Args:
        repo_path: Absolute path to the root of the repository to analyze.

    Returns:
        List of file dicts, each containing:
            path (str): Relative file path from the repo root.
            size_bytes (int): File size in bytes (0 if unreadable).
            language (str): Language name from detect_language.
            lines (int): Non-empty line count from count_lines.
    """
    root = Path(repo_path)
    file_tree: list[dict] = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not _should_skip_dir(d)]

        for filename in filenames:
            file_path = Path(dirpath) / filename
            try:
                size_bytes = file_path.stat().st_size
            except OSError:
                size_bytes = 0

            relative_path = str(file_path.relative_to(root))
            language = detect_language(str(file_path))
            lines = count_lines(str(file_path))

            file_tree.append(
                {
                    "path": relative_path,
                    "size_bytes": size_bytes,
                    "language": language,
                    "lines": lines,
                }
            )

    return file_tree
