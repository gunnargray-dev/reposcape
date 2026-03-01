"""Command-line entrypoint for running the Reposcape web server."""

from __future__ import annotations

import uvicorn

from web.app import create_app


def main() -> None:
    """Run a local dev server."""

    uvicorn.run(create_app(), host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
