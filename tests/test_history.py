"""Tests for src.history."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from src.history import (
    DEFAULT_SNAPSHOT_BUCKET_DAYS,
    build_snapshot_index,
    infer_snapshot_window,
    iter_snapshot_dates,
)


def test_iter_snapshot_dates_weekly_alignment() -> None:
    # 1970-01-01 is the anchor; with 7-day buckets, 1970-01-08 is the next bucket.
    start = date(1970, 1, 2)
    end = date(1970, 1, 9)
    out = iter_snapshot_dates(start, end, bucket_days=7)
    assert out == [date(1970, 1, 1), date(1970, 1, 8)]


def test_iter_snapshot_dates_invalid_range() -> None:
    with pytest.raises(ValueError):
        iter_snapshot_dates(date(2024, 1, 2), date(2024, 1, 1))


def test_infer_snapshot_window_empty() -> None:
    assert infer_snapshot_window([]) is None


def test_infer_snapshot_window_floors_to_bucket() -> None:
    commits = [
        datetime(2024, 1, 3, 12, tzinfo=timezone.utc),
        datetime(2024, 1, 16, 9, tzinfo=timezone.utc),
    ]
    start, end = infer_snapshot_window(commits, bucket_days=DEFAULT_SNAPSHOT_BUCKET_DAYS)  # type: ignore[misc]
    assert start <= date(2024, 1, 3)
    assert end <= date(2024, 1, 16)


def test_build_snapshot_index_sorts_and_filters(tmp_path) -> None:
    (tmp_path / "2024-01-08.json").write_text("{}")
    (tmp_path / "2024-01-01.json").write_text("{}")
    (tmp_path / "not-a-date.json").write_text("{}")

    paths = list(tmp_path.iterdir())
    idx = build_snapshot_index(paths)
    assert idx == [
        {"as_of": "2024-01-01", "filename": "2024-01-01.json"},
        {"as_of": "2024-01-08", "filename": "2024-01-08.json"},
    ]
