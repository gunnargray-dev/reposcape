"""Tests for src.history_delta."""

from __future__ import annotations

from datetime import date

from src.history_delta import compute_snapshot_delta


def test_compute_snapshot_delta_happy_path() -> None:
    a = {
        "techdebt": {
            "score": 10,
            "breakdown": {"todo_count": 3, "total_source_lines": 100, "total_source_files": 5},
        },
        "complexity": {"summary": {"avg_complexity": 1.5}},
    }
    b = {
        "techdebt": {
            "score": 12,
            "breakdown": {"todo_count": 5, "total_source_lines": 110, "total_source_files": 6},
        },
        "complexity": {"summary": {"avg_complexity": 2.0}},
    }

    out = compute_snapshot_delta(a, b, date(2020, 1, 1), date(2020, 1, 8)).metrics
    assert out["delta"]["techdebt_score"] == 2
    assert out["delta"]["todo_count"] == 2
    assert out["delta"]["total_source_lines"] == 10
    assert out["delta"]["total_source_files"] == 1
    assert out["delta"]["avg_complexity"] == 0.5


def test_compute_snapshot_delta_missing_fields() -> None:
    out = compute_snapshot_delta({}, {}, date(2020, 1, 1), date(2020, 1, 8)).metrics
    assert out["a"]["techdebt_score"] is None
    assert out["delta"]["todo_count"] is None
