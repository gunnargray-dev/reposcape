"""Commit frequency heatmap data generator.

The output format is designed to be directly consumable by a frontend heatmap
component (e.g., D3). The core representation is a list of weeks, each containing
seven day cells.

All logic uses the standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable, Optional


@dataclass(frozen=True)
class HeatmapCell:
    """Single day in the heatmap grid."""

    day: date
    count: int


def _start_of_week(d: date, week_start: int) -> date:
    """Return the week-start date for `d`.

    Args:
        d: Any date.
        week_start: Weekday integer where 0=Monday ... 6=Sunday.

    Returns:
        The date of the week start.
    """ 

    delta = (d.weekday() - week_start) % 7
    return d - timedelta(days=delta)


def build_commit_heatmap(
    commit_datetimes: Iterable[datetime],
    *,
    start: Optional[date] = None,
    end: Optional[date] = None,
    week_start: int = 0,
) -> list[list[HeatmapCell]]:
    """Build a commit frequency heatmap grid.

    Args:
        commit_datetimes: Commit timestamps.
        start: Optional inclusive start date. Defaults to the earliest commit date.
        end: Optional inclusive end date. Defaults to the latest commit date.
        week_start: Week start weekday, 0=Monday ... 6=Sunday.

    Returns:
        A list of weeks. Each week is a list of seven HeatmapCell objects ordered
        from week_start to week_start+6.

    Raises:
        ValueError: If week_start is not between 0 and 6.
    """

    if week_start < 0 or week_start > 6:
        raise ValueError("week_start must be between 0 and 6")

    commits = [dt.date() for dt in commit_datetimes]
    if not commits:
        return []

    min_day = min(commits)
    max_day = max(commits)

    start_day = start or min_day
    end_day = end or max_day
    if start_day > end_day:
        return []

    counts: dict[date, int] = {}
    for d in commits:
        if d < start_day or d > end_day:
            continue
        counts[d] = counts.get(d, 0) + 1

    grid_start = _start_of_week(start_day, week_start)
    grid_end = _start_of_week(end_day, week_start) + timedelta(days=6)

    weeks: list[list[HeatmapCell]] = []
    current = grid_start
    while current <= grid_end:
        week: list[HeatmapCell] = []
        for offset in range(7):
            day = current + timedelta(days=offset)
            week.append(HeatmapCell(day=day, count=counts.get(day, 0)))
        weeks.append(week)
        current += timedelta(days=7)

    return weeks


def to_json(grid: list[list[HeatmapCell]]) -> dict:
    """Convert HeatmapCell grid to JSON-serializable dict.

    Args:
        grid: Heatmap output.

    Returns:
        Dict with a list of weeks and date ranges.
    """

    if not grid:
        return {"weeks": [], "start": None, "end": None}

    flat = [c for week in grid for c in week]
    start = min(c.day for c in flat)
    end = max(c.day for c in flat)

    weeks: list[dict] = []
    for week in grid:
        if not week:
            continue
        weeks.append(
            {
                "start": week[0].day.isoformat(),
                "days": [{"date": c.day.isoformat(), "count": c.count} for c in week],
            }
        )

    return {"weeks": weeks, "start": start.isoformat(), "end": end.isoformat()}
