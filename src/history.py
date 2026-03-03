"""Historical tracking (repo snapshots over time).

This module is intentionally stdlib-only and provides a small, testable API for:
- deciding which snapshot dates should exist
- writing/reading snapshot JSON
- building a lightweight index for consumers (CLI/web)

A "snapshot" is a JSON blob representing analysis results at a specific point
in time (typically weekly). Consumers can use this to show historical trends
without re-analyzing every intermediate point.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


DEFAULT_SNAPSHOT_BUCKET_DAYS = 7


@dataclass(frozen=True)
class SnapshotRef:
    """Reference to a historical snapshot on disk."""

    as_of: date
    path: Path


def _as_utc_date(dt: datetime) -> date:
    """Normalize a datetime into a UTC date."""

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).date()


def _floor_to_bucket(d: date, bucket_days: int) -> date:
    """Floor a date to the start of its N-day bucket."""

    if bucket_days <= 0:
        raise ValueError("bucket_days must be > 0")

    # Treat 1970-01-01 as an epoch anchor.
    anchor = date(1970, 1, 1)
    delta_days = (d - anchor).days
    bucket_index = delta_days // bucket_days
    return anchor + timedelta(days=bucket_index * bucket_days)


def iter_snapshot_dates(
    start: date,
    end: date,
    bucket_days: int = DEFAULT_SNAPSHOT_BUCKET_DAYS,
) -> list[date]:
    """Return snapshot dates from start..end inclusive, aligned to buckets.

    Args:
        start: First date (inclusive).
        end: Last date (inclusive).
        bucket_days: Size of bucket in days (default weekly).

    Returns:
        List of bucket-aligned dates (ascending).

    Raises:
        ValueError: If start > end or bucket_days <= 0.
    """

    if start > end:
        raise ValueError("start must be <= end")
    if bucket_days <= 0:
        raise ValueError("bucket_days must be > 0")

    cursor = _floor_to_bucket(start, bucket_days)
    end_bucket = _floor_to_bucket(end, bucket_days)

    dates: list[date] = []
    while cursor <= end_bucket:
        dates.append(cursor)
        cursor = cursor + timedelta(days=bucket_days)

    return dates


def get_repo_history_dir(repo_owner: str, repo_name: str, base_dir: Path) -> Path:
    """Return the base directory for a repository's snapshot history."""

    safe = f"{repo_owner}__{repo_name}".replace("/", "_")
    return base_dir / safe


def snapshot_path(history_dir: Path, as_of: date) -> Path:
    """Return the expected JSON path for a snapshot date."""

    return history_dir / f"{as_of.isoformat()}.json"


def write_snapshot(history_dir: Path, as_of: date, payload: dict[str, Any]) -> Path:
    """Write a snapshot JSON file to disk.

    Args:
        history_dir: Directory for this repo's history.
        as_of: Snapshot date (bucket start).
        payload: JSON-serializable dict.

    Returns:
        Path written.
    """

    history_dir.mkdir(parents=True, exist_ok=True)
    out_path = snapshot_path(history_dir, as_of)

    to_write = {"as_of": as_of.isoformat(), **payload}
    out_path.write_text(json.dumps(to_write, sort_keys=True, indent=2) + "\n")
    return out_path


def load_snapshot(path: Path) -> dict[str, Any]:
    """Load snapshot JSON from disk."""

    return json.loads(path.read_text())


def build_snapshot_index(paths: Iterable[Path]) -> list[dict[str, str]]:
    """Build a stable index payload from a set of snapshot files.

    Args:
        paths: Iterable of snapshot JSON paths.

    Returns:
        List of dicts sorted by date ascending, each containing:
            as_of: ISO date string
            filename: base filename (no directory)
    """

    refs: list[SnapshotRef] = []
    for p in paths:
        try:
            as_of = date.fromisoformat(p.stem)
        except ValueError:
            continue
        refs.append(SnapshotRef(as_of=as_of, path=p))

    refs.sort(key=lambda r: r.as_of)
    return [{"as_of": r.as_of.isoformat(), "filename": r.path.name} for r in refs]


def infer_snapshot_window(
    commit_datetimes: list[datetime],
    bucket_days: int = DEFAULT_SNAPSHOT_BUCKET_DAYS,
) -> tuple[date, date] | None:
    """Infer the snapshot window for a repo from commit datetimes.

    Args:
        commit_datetimes: Commit datetimes (any order).
        bucket_days: Snapshot bucket size.

    Returns:
        (start_date, end_date) aligned to bucket boundaries, or None if no commits.
    """

    if not commit_datetimes:
        return None

    dates = [_as_utc_date(dt) for dt in commit_datetimes]
    start = min(dates)
    end = max(dates)
    return (_floor_to_bucket(start, bucket_days), _floor_to_bucket(end, bucket_days))
