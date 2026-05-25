"""Collision checks for layout placements."""

from __future__ import annotations

from typing import Any

from core.layout_engine.basic_layout import bboxes_overlap


def check_collisions(placements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for left_index, left in enumerate(placements):
        for right in placements[left_index + 1 :]:
            overlap = bboxes_overlap(left["bbox"], right["bbox"])
            checks.append(
                {
                    "name": "collision",
                    "status": "fail" if overlap else "pass",
                    "objects": [left["object_id"], right["object_id"]],
                    "message": "placements overlap" if overlap else "placements do not overlap",
                }
            )
    return checks or [{"name": "collision", "status": "pass", "message": "single placement"}]
