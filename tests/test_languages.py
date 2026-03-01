"""Comprehensive tests for the languages module.

Uses temporary files and directories to exercise all code paths without
depending on any particular external repository state.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from src.languages import analyze_languages, count_lines, detect_language, get_file_tree


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(dir_path: Path, name: str, content: str) -> Path:
    """Write content to a file inside dir_path and return the Path."""
    p = dir_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# detect_language tests  (covers all documented extensions)
# ---------------------------------------------------------------------------


class TestDetectLanguage:
    @pytest.mark.parametrize(
        "filename,expected",
        [
            ("app.py", "Python"),
            ("index.js", "JavaScript"),
            ("component.ts", "TypeScript"),
            ("button.jsx", "JSX"),
            ("widget.tsx", "TSX"),
            ("Main.java", "Java"),
            ("main.go", "Go"),
            ("lib.rs", "Rust"),
            ("util.rb", "Ruby"),
            ("index.php", "PHP"),
            ("main.c", "C"),
            ("core.cpp", "C++"),
            ("header.h", "C/C++ Header"),
            ("service.cs", "C#"),
            ("view.swift", "Swift"),
            ("app.kt", "Kotlin"),
            ("analysis.r", "R"),
            ("bridge.m", "Objective-C"),
            ("page.html", "HTML"),
            ("style.css", "CSS"),
            ("styles.scss", "SCSS"),
            ("config.json", "JSON"),
            ("config.yaml", "YAML"),
            ("config.yml", "YAML"),
            ("README.md", "Markdown"),
            ("notes.txt", "Text"),
            ("build.sh", "Shell"),
            ("query.sql", "SQL"),
            ("data.xml", "XML"),
            ("config.toml", "TOML"),
        ],
    )
    def test_extension_mapping(self, filename, expected):
        """Each documented extension maps to the expected language name."""
        assert detect_language(filename) == expected

    def test_unknown_extension_returns_other(self):
        """Files with unrecognised extensions should return 'Other'."""
        assert detect_language("file.xyz123") == "Other"

    def test_no_extension_returns_other(self):
        """Files with no extension should return 'Other'."""
        assert detect_language("Makefile") == "Other"

    def test_path_with_dirs(self):
        """Full paths should be handled correctly."""
        assert detect_language("/some/deep/path/script.py") == "Python"

    def test_cc_extension(self):
        """The .cc extension should also map to C++."""
        assert detect_language("engine.cc") == "C++"

    def test_htm_extension(self):
        """The .htm extension should map to HTML."""
        assert detect_language("index.htm") == "HTML"

    def test_sass_extension(self):
        """The .sass extension should map to SCSS."""
        assert detect_language("styles.sass") == "SCSS"


# ---------------------------------------------------------------------------
# count_lines tests
# ---------------------------------------------------------------------------


class TestCountLines:
    def test_basic_line_count(self, tmp_path):
        """Should count non-empty lines correctly."""
        f = _write(tmp_path, "test.py", "a = 1\nb = 2\nc = 3\n")
        assert count_lines(str(f)) == 3

    def test_empty_lines_not_counted(self, tmp_path):
        """Blank lines should not be counted."""
        f = _write(tmp_path, "test.py", "a = 1\n\n\nb = 2\n")
        assert count_lines(str(f)) == 2

    def test_whitespace_only_lines_not_counted(self, tmp_path):
        """Lines with only whitespace should not be counted."""
        f = _write(tmp_path, "test.py", "a = 1\n   \n\t\nb = 2\n")
        assert count_lines(str(f)) == 2

    def test_empty_file_returns_zero(self, tmp_path):
        """An empty file should return 0."""
        f = _write(tmp_path, "empty.py", "")
        assert count_lines(str(f)) == 0

    def test_single_line_no_newline(self, tmp_path):
        """A single line without trailing newline should count as 1."""
        f = tmp_path / "single.py"
        f.write_bytes(b"hello world")
        assert count_lines(str(f)) == 1

    def test_binary_file_returns_zero(self, tmp_path):
        """Binary files should return 0 without raising an exception."""
        f = tmp_path / "binary.bin"
        f.write_bytes(bytes(range(256)))  # contains null bytes
        assert count_lines(str(f)) == 0

    def test_nonexistent_file_returns_zero(self, tmp_path):
        """A path that doesn't exist should return 0."""
        assert count_lines(str(tmp_path / "missing.py")) == 0

    def test_multiline_file(self, tmp_path):
        """Should correctly count 100 lines."""
        content = "\n".join(f"line {i}" for i in range(100)) + "\n"
        f = _write(tmp_path, "big.py", content)
        assert count_lines(str(f)) == 100

    def test_latin1_file_readable(self, tmp_path):
        """Files encoded in latin-1 should be readable."""
        f = tmp_path / "latin.py"
        f.write_bytes("caf\xe9 = 1\nbar = 2\n".encode("latin-1"))
        result = count_lines(str(f))
        assert result == 2


# ---------------------------------------------------------------------------
# analyze_languages tests
# ---------------------------------------------------------------------------


class TestAnalyzeLanguages:
    def test_returns_dict_with_expected_keys(self, tmp_path):
        """analyze_languages should return dict with required top-level keys."""
        result = analyze_languages(str(tmp_path))
        assert "languages" in result
        assert "total_files" in result
        assert "total_lines" in result

    def test_empty_repo_returns_zeros(self, tmp_path):
        """An empty directory should report 0 files and 0 lines."""
        result = analyze_languages(str(tmp_path))
        assert result["total_files"] == 0
        assert result["total_lines"] == 0
        assert result["languages"] == []

    def test_single_python_file(self, tmp_path):
        """A single Python file should appear as 'Python' with correct counts."""
        _write(tmp_path, "main.py", "x = 1\ny = 2\nz = 3\n")
        result = analyze_languages(str(tmp_path))
        assert result["total_files"] == 1
        assert result["total_lines"] == 3
        langs = {l["name"]: l for l in result["languages"]}
        assert "Python" in langs
        assert langs["Python"]["files"] == 1
        assert langs["Python"]["lines"] == 3
        assert langs["Python"]["percentage"] == 100.0

    def test_mixed_languages(self, tmp_path):
        """Multiple file types should each appear as distinct languages."""
        _write(tmp_path, "app.py", "a = 1\nb = 2\n")
        _write(tmp_path, "index.js", "const x = 1;\nconst y = 2;\n")
        _write(tmp_path, "style.css", "body { }\n")
        result = analyze_languages(str(tmp_path))
        assert result["total_files"] == 3
        langs = {l["name"] for l in result["languages"]}
        assert "Python" in langs
        assert "JavaScript" in langs
        assert "CSS" in langs

    def test_git_dir_excluded(self, tmp_path):
        """Files inside .git should not be counted."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        _write(git_dir, "HEAD", "ref: refs/heads/main\n")
        _write(tmp_path, "main.py", "x = 1\n")
        result = analyze_languages(str(tmp_path))
        assert result["total_files"] == 1  # only main.py

    def test_node_modules_excluded(self, tmp_path):
        """Files inside node_modules should not be counted."""
        nm = tmp_path / "node_modules"
        nm.mkdir()
        _write(nm, "index.js", "console.log('hi');\n")
        _write(tmp_path, "app.py", "x = 1\n")
        result = analyze_languages(str(tmp_path))
        assert result["total_files"] == 1

    def test_pycache_excluded(self, tmp_path):
        """Files inside __pycache__ should not be counted."""
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        _write(cache, "module.cpython-312.pyc", "binary stuff\n")
        _write(tmp_path, "module.py", "x = 1\n")
        result = analyze_languages(str(tmp_path))
        assert result["total_files"] == 1

    def test_languages_sorted_by_lines_descending(self, tmp_path):
        """Languages list should be sorted from most to fewest lines."""
        _write(tmp_path, "big.py", "\n".join(f"x = {i}" for i in range(10)))
        _write(tmp_path, "small.js", "const a = 1;\nconst b = 2;\n")
        result = analyze_languages(str(tmp_path))
        lines_seq = [l["lines"] for l in result["languages"]]
        assert lines_seq == sorted(lines_seq, reverse=True)

    def test_percentages_sum_to_100(self, tmp_path):
        """Percentages should sum to approximately 100%."""
        _write(tmp_path, "a.py", "x = 1\ny = 2\n")
        _write(tmp_path, "b.js", "const a = 1;\n")
        result = analyze_languages(str(tmp_path))
        total_pct = sum(l["percentage"] for l in result["languages"])
        assert abs(total_pct - 100.0) < 0.1

    def test_total_files_counts_all(self, tmp_path):
        """total_files should match the number of files created."""
        for i in range(5):
            _write(tmp_path, f"file{i}.py", f"x = {i}\n")
        result = analyze_languages(str(tmp_path))
        assert result["total_files"] == 5

    def test_language_entry_structure(self, tmp_path):
        """Each language entry must have the four required fields."""
        _write(tmp_path, "app.py", "x = 1\n")
        result = analyze_languages(str(tmp_path))
        for lang in result["languages"]:
            assert "name" in lang
            assert "files" in lang
            assert "lines" in lang
            assert "percentage" in lang


# ---------------------------------------------------------------------------
# get_file_tree tests
# ---------------------------------------------------------------------------


class TestGetFileTree:
    def test_returns_list(self, tmp_path):
        """get_file_tree should return a list."""
        assert isinstance(get_file_tree(str(tmp_path)), list)

    def test_empty_dir_returns_empty_list(self, tmp_path):
        """An empty directory should return an empty list."""
        assert get_file_tree(str(tmp_path)) == []

    def test_file_entry_has_required_keys(self, tmp_path):
        """Each file entry must have path, size_bytes, language, lines."""
        _write(tmp_path, "app.py", "x = 1\n")
        tree = get_file_tree(str(tmp_path))
        assert len(tree) == 1
        entry = tree[0]
        assert "path" in entry
        assert "size_bytes" in entry
        assert "language" in entry
        assert "lines" in entry

    def test_relative_path_used(self, tmp_path):
        """Paths in the tree should be relative to the repo root."""
        _write(tmp_path, "app.py", "x = 1\n")
        tree = get_file_tree(str(tmp_path))
        assert not Path(tree[0]["path"]).is_absolute()
        assert tree[0]["path"] == "app.py"

    def test_size_bytes_positive(self, tmp_path):
        """size_bytes should be a positive integer for non-empty files."""
        _write(tmp_path, "app.py", "x = 1\n")
        tree = get_file_tree(str(tmp_path))
        assert tree[0]["size_bytes"] > 0

    def test_git_excluded_from_tree(self, tmp_path):
        """get_file_tree should exclude .git directory contents."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        _write(git_dir, "HEAD", "ref: refs/heads/main\n")
        _write(tmp_path, "app.py", "x = 1\n")
        tree = get_file_tree(str(tmp_path))
        paths = [e["path"] for e in tree]
        assert all(".git" not in p for p in paths)

    def test_nested_files_included(self, tmp_path):
        """Files in subdirectories should be included in the tree."""
        subdir = tmp_path / "src"
        subdir.mkdir()
        _write(subdir, "main.py", "x = 1\n")
        _write(tmp_path, "README.md", "# Hello\n")
        tree = get_file_tree(str(tmp_path))
        assert len(tree) == 2

    def test_node_modules_excluded_from_tree(self, tmp_path):
        """node_modules should be excluded from the file tree."""
        nm = tmp_path / "node_modules"
        nm.mkdir()
        _write(nm, "package.js", "module.exports = {};\n")
        _write(tmp_path, "app.py", "x = 1\n")
        tree = get_file_tree(str(tmp_path))
        assert len(tree) == 1
        assert "node_modules" not in tree[0]["path"]
