"""Clearance checks for simple rectangular placements."""

from __future__ import annotations

from typing import Any


def _gap(first: dict[str, list[float | int]], second: dict[str, list[float | int]]) -> float:
    x_gap = max(0, max(second["min"][0] - first["max"][0], first["min"][0] - second["max"][0]))
    y_gap = max(0, max(second["min"][1] - first["max"][1], first["min"][1] - second["max"][1]))
    if x_gap == 0:
        return float(y_gap)
    if y_gap == 0:
        return float(x_gap)
    return float((x_gap**2 + y_gap**2) ** 0.5)


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
