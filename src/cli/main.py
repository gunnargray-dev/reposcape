"""Command-line interface for Reposcape.

This module provides a small wrapper around the existing analysis engine.

Usage:
  reposcape analyze <repo_url>

Design goals:
- Keep dependencies to the Python standard library.
- Reuse existing analyzers (no duplicated analysis logic).
- Emit JSON to stdout so users can pipe/redirect to files.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.analyze import analyze_repo_url as analyze_repo


@dataclass(frozen=True)
class CliResult:
    """Represents a CLI execution result."""

    exit_code: int
    stdout: str
    stderr: str = ""


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""

    parser = argparse.ArgumentParser(prog="reposcape")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Analyze a repository")
    analyze.add_argument("repo_url", help="GitHub repository URL")
    analyze.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    analyze.add_argument(
        "--snapshot-dir",
        default=os.environ.get("REPOSCAPE_SNAPSHOT_DIR"),
        help=(
            "Optional base directory where a point-in-time analysis snapshot is written. "
            "Can also be set via REPOSCAPE_SNAPSHOT_DIR."
        ),
    )

    return parser


def _render_json(payload: dict[str, Any], pretty: bool) -> str:
    if pretty:
        return json.dumps(payload, indent=2, sort_keys=True)
    return json.dumps(payload)


def run(argv: list[str]) -> CliResult:
    """Run the CLI.

    Args:
        argv: Raw argv list, excluding the program name.

    Returns:
        CliResult with output and exit code.
    """

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        snapshot_dir: Path | None = None
        if getattr(args, "snapshot_dir", None):
            snapshot_dir = Path(str(args.snapshot_dir))

        payload = analyze_repo(str(args.repo_url), snapshot_base_dir=snapshot_dir)
        return CliResult(exit_code=0, stdout=_render_json(payload, bool(args.pretty)))

    return CliResult(exit_code=2, stdout="", stderr="Unknown command")


def main() -> None:
    """Entrypoint for `reposcape` console script."""

    res = run(sys.argv[1:])
    if res.stderr:
        sys.stderr.write(res.stderr)
        if not res.stderr.endswith("\n"):
            sys.stderr.write("\n")
    if res.stdout:
        sys.stdout.write(res.stdout)
        if not res.stdout.endswith("\n"):
            sys.stdout.write("\n")
    raise SystemExit(res.exit_code)


if __name__ == "__main__":
    main()
