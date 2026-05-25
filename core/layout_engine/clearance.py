"""Clearance checks for simple rectangular placements."""

from __future__ import annotations

from typing import Any

from core.geometry_backends.rect2d import rect_gap


def _gap(first: dict[str, list[float | int]], second: dict[str, list[float | int]]) -> float:
    return rect_gap(first, second)


def check_clearance(placements: list[dict[str, Any]], *, minimum_clearance: float | int) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for index, first in enumerate(placements):
        for second in placements[index + 1 :]:
            gap = _gap(first["bbox"], second["bbox"])
            checks.append(
                {
                    "name": "clearance",
                    "status": "pass" if gap >= minimum_clearance else "fail",
                    "objects": [first["object_id"], second["object_id"]],
                    "message": f"clearance {gap} mm, required {minimum_clearance} mm",
                }
            )
    return checks or [{"name": "clearance", "status": "pass", "message": "single placement"}]
