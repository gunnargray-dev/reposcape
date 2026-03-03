"""Comparison utilities.

This module builds on the existing single-repo analysis payload produced by
`src.analyze.analyze_repo_url`.

The initial goal is a lightweight, fully-JSON-serializable comparison payload
that can power a simple UI:
- analyze two repos
- compute a few headline deltas (languages, tech debt, PR velocity, commit quality)

The UI layer is intentionally separate; this module contains no FastAPI or
Pydantic dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.analyze import analyze_repo_url


@dataclass(frozen=True)
class ComparisonMetric:
    """A simple numeric metric comparison between two repos."""

    name: str
    a: float | None
    b: float | None
    delta: float | None


def _as_float(value: Any) -> float | None:
    """Best-effort conversion to float.

    Args:
        value: Any value.

    Returns:
        Float if conversion possible, else None.
    """

    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _delta(a: float | None, b: float | None) -> float | None:
    """Compute b - a if both are present."""

    if a is None or b is None:
        return None
    return b - a


def _pick(payload: dict[str, Any], path: list[str]) -> Any:
    """Safely pick nested values from a dict."""

    cur: Any = payload
    for p in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


def build_comparison_payload(repo_a_url: str, repo_b_url: str) -> dict[str, Any]:
    """Analyze two repos and return a comparison payload.

    Args:
        repo_a_url: Repo A URL.
        repo_b_url: Repo B URL.

    Returns:
        Dict with `repo_a`, `repo_b`, and a small set of comparable metrics.
    """

    repo_a = analyze_repo_url(repo_a_url)
    repo_b = analyze_repo_url(repo_b_url)

    # Remove transport-oriented keys so this payload is stable.
    def _strip_runtime(p: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in p.items() if k not in {"cached", "duration_ms"}}

    a_payload = _strip_runtime(repo_a)
    b_payload = _strip_runtime(repo_b)

    metrics: list[ComparisonMetric] = []

    metrics.append(
        ComparisonMetric(
            name="Commit quality avg score",
            a=_as_float(_pick(a_payload, ["commit_quality", "average_score"])),
            b=_as_float(_pick(b_payload, ["commit_quality", "average_score"])),
            delta=_delta(
                _as_float(_pick(a_payload, ["commit_quality", "average_score"])),
                _as_float(_pick(b_payload, ["commit_quality", "average_score"])),
            ),
        )
    )

    metrics.append(
        ComparisonMetric(
            name="Tech debt score",
            a=_as_float(_pick(a_payload, ["techdebt", "score"])),
            b=_as_float(_pick(b_payload, ["techdebt", "score"])),
            delta=_delta(
                _as_float(_pick(a_payload, ["techdebt", "score"])),
                _as_float(_pick(b_payload, ["techdebt", "score"])),
            ),
        )
    )

    metrics.append(
        ComparisonMetric(
            name="PR velocity median days",
            a=_as_float(_pick(a_payload, ["pr_velocity", "median_days"])),
            b=_as_float(_pick(b_payload, ["pr_velocity", "median_days"])),
            delta=_delta(
                _as_float(_pick(a_payload, ["pr_velocity", "median_days"])),
                _as_float(_pick(b_payload, ["pr_velocity", "median_days"])),
            ),
        )
    )

    # Languages: compare top-language share.
    def _top_lang_share(p: dict[str, Any]) -> float | None:
        langs = p.get("languages")
        if not isinstance(langs, dict) or not langs:
            return None
        total = sum(float(v) for v in langs.values() if isinstance(v, (int, float)))
        if total <= 0:
            return None
        top = max(float(v) for v in langs.values() if isinstance(v, (int, float)))
        return top / total

    metrics.append(
        ComparisonMetric(
            name="Top language share",
            a=_top_lang_share(a_payload),
            b=_top_lang_share(b_payload),
            delta=_delta(_top_lang_share(a_payload), _top_lang_share(b_payload)),
        )
    )

    return {
        "repo_a": a_payload,
        "repo_b": b_payload,
        "metrics": [m.__dict__ for m in metrics],
    }
