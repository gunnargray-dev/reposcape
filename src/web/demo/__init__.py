"""Demo payload loaders for showcase pages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_demo_payload(name: str) -> dict[str, Any]:
    """Load a demo analysis payload from the packaged demo directory."""

    demo_dir = Path(__file__).resolve().parent
    path = demo_dir / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))
