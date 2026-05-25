"""Circulation checks for simple shell layout candidates."""

from __future__ import annotations

from typing import Any


def check_main_aisle_width(
    *,
    placements: list[dict[str, Any]],
    boundary: dict[str, list[float | int]],
    minimum_width: float | int,
) -> list[dict[str, Any]]:
    if not placements:
        return [
            {
                "name": "main_aisle_width",
                "status": "not_run",
                "message": "No placements to compare with shell depth.",
            }
        ]

    max_occupied_y = max(float(placement["bbox"]["max"][1]) for placement in placements)
    available_width = float(boundary["max"][1]) - max_occupied_y
    status = "pass" if available_width >= float(minimum_width) else "fail"
    return [
        {
            "name": "main_aisle_width",
            "status": status,
            "message": f"available main aisle {available_width} mm, required {minimum_width} mm",
        }
    ]
