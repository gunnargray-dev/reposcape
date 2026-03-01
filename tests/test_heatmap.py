"""Tests for commit frequency heatmap generation."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from src.heatmap import HeatmapCell, build_commit_heatmap


def _d(y: int, m: int, d: int) -> datetime:
    return datetime(y, m, d, 12, 0, 0)


def test_build_commit_heatmap_empty() -> None:
    assert build_commit_heatmap([]) == []


def test_build_commit_heatmap_invalid_week_start() -> None:
    with pytest.raises(ValueError):
        build_commit_heatmap([_d(2026, 1, 1)], week_start=7)


def test_build_commit_heatmap_single_day_counts() -> None:
    grid = build_commit_heatmap([_d(2026, 1, 1), _d(2026, 1, 1), _d(2026, 1, 2)])
    flat = [c for week in grid for c in week]
    by_day = {c.day: c.count for c in flat}

    assert by_day[date(2026, 1, 1)] == 2
    assert by_day[date(2026, 1, 2)] == 1


def test_build_commit_heatmap_start_end_filtering() -> None:
    grid = build_commit_heatmap(
        [_d(2026, 1, 1), _d(2026, 1, 2), _d(2026, 1, 3)],
        start=date(2026, 1, 2),
        end=date(2026, 1, 2),
    )
    flat = [c for week in grid for c in week]
    assert {c.day: c.count for c in flat}[date(2026, 1, 2)] == 1
    assert sum(c.count for c in flat) == 1


def test_build_commit_heatmap_start_after_end_returns_empty() -> None:
    grid = build_commit_heatmap(
        [_d(2026, 1, 1)],
        start=date(2026, 1, 3),
        end=date(2026, 1, 2),
    )
    assert grid == []


def test_build_commit_heatmap_grid_is_full_weeks() -> None:
    # 2026-01-01 is Thursday.
    grid = build_commit_heatmap([_d(2026, 1, 1)], week_start=0)
    assert len(grid) == 1
    assert len(grid[0]) == 7
    assert grid[0][0].day.weekday() == 0
    assert grid[0][-1].day.weekday() == 6


def test_build_commit_heatmap_week_start_sunday() -> None:
    grid = build_commit_heatmap([_d(2026, 1, 1)], week_start=6)
    assert grid[0][0].day.weekday() == 6
    assert grid[0][1].day.weekday() == 0


def test_cells_are_heatmapcell() -> None:
    grid = build_commit_heatmap([_d(2026, 1, 1)])
    assert isinstance(grid[0][0], HeatmapCell)
