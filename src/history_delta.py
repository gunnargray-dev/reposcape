"""Snapshot-to-snapshot diff helpers for historical tracking.

This module intentionally stays stdlib-only and provides a small API for
computing lightweight deltas between two snapshot payloads.

The goal is to support a timeline view in the web UI without requiring the
server to re-analyze repositories.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class SnapshotDelta:
    """Computed delta between two snapshots."""

    a_as_of: date
    b_as_of: date
    metrics: dict[str, Any]


def _as_int(value: Any) -> int | None:
    """Best-effort parse to int."""

    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_float(value: Any) -> float | None:
    """Best-effort parse to float."""

    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _get(d: dict[str, Any], *path: str) -> Any:
    """Get a nested key path from a dict, returning None on missing."""

    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def compute_snapshot_delta(
    a: dict[str, Any],
    b: dict[str, Any],
    a_as_of: date,
    b_as_of: date,
) -> SnapshotDelta:
    """Compute a stable set of numeric deltas between two snapshots.

    Metrics are chosen to be:
    - stable across schema evolution
    - cheap to compute
    - useful in a mini timeline UI (tables/mini charts)

    Args:
        a: Snapshot payload (older).
        b: Snapshot payload (newer).
        a_as_of: Date for snapshot a.
        b_as_of: Date for snapshot b.

    Returns:
        SnapshotDelta including absolute and delta values.
    """

    a_score = _as_int(_get(a, "techdebt", "score"))
    b_score = _as_int(_get(b, "techdebt", "score"))

    a_todo = _as_int(_get(a, "techdebt", "breakdown", "todo_count"))
    b_todo = _as_int(_get(b, "techdebt", "breakdown", "todo_count"))

    a_lines = _as_int(_get(a, "techdebt", "breakdown", "total_source_lines"))
    b_lines = _as_int(_get(b, "techdebt", "breakdown", "total_source_lines"))

    a_files = _as_int(_get(a, "techdebt", "breakdown", "total_source_files"))
    b_files = _as_int(_get(b, "techdebt", "breakdown", "total_source_files"))

    a_avg_complex = _as_float(_get(a, "complexity", "summary", "avg_complexity"))
    b_avg_complex = _as_float(_get(b, "complexity", "summary", "avg_complexity"))

    metrics: dict[str, Any] = {
        "a": {
            "as_of": a_as_of.isoformat(),
            "techdebt_score": a_score,
            "todo_count": a_todo,
            "total_source_lines": a_lines,
            "total_source_files": a_files,
            "avg_complexity": a_avg_complex,
        },
        "b": {
            "as_of": b_as_of.isoformat(),
            "techdebt_score": b_score,
            "todo_count": b_todo,
            "total_source_lines": b_lines,
            "total_source_files": b_files,
            "avg_complexity": b_avg_complex,
        },
        "delta": {
            "techdebt_score": (b_score - a_score) if a_score is not None and b_score is not None else None,
            "todo_count": (b_todo - a_todo) if a_todo is not None and b_todo is not None else None,
            "total_source_lines": (b_lines - a_lines) if a_lines is not None and b_lines is not None else None,
            "total_source_files": (b_files - a_files) if a_files is not None and b_files is not None else None,
            "avg_complexity": (
                round(b_avg_complex - a_avg_complex, 2)
                if a_avg_complex is not None and b_avg_complex is not None
                else None
            ),
        },
    }

    return SnapshotDelta(a_as_of=a_as_of, b_as_of=b_as_of, metrics=metrics)
