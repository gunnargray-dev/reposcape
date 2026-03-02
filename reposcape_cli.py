"""Console-script wrapper.

This module exists because the project's import root is the `src/` directory
(which is importable as the `src` package). Installing a console script pointing
at `src.*` can be fragile depending on environment.

By placing a thin wrapper module at the repository root, we can reliably expose
`reposcape` as a command without changing the internal package layout.
"""

from __future__ import annotations

from src.cli.main import main

__all__ = ["main"]
