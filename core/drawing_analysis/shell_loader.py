"""Load hand-authored shell annotations into a normalized SHELL_MODEL."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


class ShellLoadError(ValueError):
    """Raised when a manual shell file cannot form a valid SHELL_MODEL."""


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ShellLoadError("Manual shell file must contain a JSON object.")
    return data


def _point(value: Any, *, label: str) -> list[float | int]:
    if not isinstance(value, list) or len(value) != 2:
        raise ShellLoadError(f"{label} must be a 2D point.")
    if not all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value):
        raise ShellLoadError(f"{label} must contain numeric coordinates.")
    return [value[0], value[1]]


def _normalize_bbox(value: Any, *, label: str) -> dict[str, list[float | int]]:
    if not isinstance(value, dict):
        raise ShellLoadError(f"{label} bbox is required.")
    min_point = _point(value.get("min"), label=f"{label}.min")
    max_point = _point(value.get("max"), label=f"{label}.max")
    if min_point[0] >= max_point[0] or min_point[1] >= max_point[1]:
        raise ShellLoadError(f"{label} min must be lower than max.")
    return {"min": min_point, "max": max_point}


def _normalize_boundary(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ShellLoadError("boundary is required.")

    boundary_type = str(value.get("type", "bbox"))
    if boundary_type not in {"bbox", "polygon", "orthogonal_polygon"}:
        raise ShellLoadError("boundary.type must be bbox, polygon or orthogonal_polygon.")

    bbox = _normalize_bbox(value, label="boundary")
    boundary: dict[str, Any] = {"type": boundary_type, **bbox}

    points = value.get("points")
    if points is not None:
        if not isinstance(points, list) or len(points) < 4:
            raise ShellLoadError("boundary.points must contain at least 4 points.")
        boundary["points"] = [_point(point, label="boundary.points[]") for point in points]

    return boundary


def _bbox_inside(inner: dict[str, list[float | int]], outer: dict[str, Any]) -> bool:
    return (
        inner["min"][0] >= outer["min"][0]
        and inner["min"][1] >= outer["min"][1]
        and inner["max"][0] <= outer["max"][0]
        and inner["max"][1] <= outer["max"][1]
    )


def _normalize_opening(value: Any, *, index: int) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ShellLoadError("openings must contain objects.")
    opening_id = value.get("opening_id") or value.get("id")
    if not opening_id:
        raise ShellLoadError(f"openings[{index}].opening_id is required.")
    if "width" not in value:
        raise ShellLoadError(f"openings[{index}].width is required.")
    width = value["width"]
    if not isinstance(width, (int, float)) or isinstance(width, bool) or width <= 0:
        raise ShellLoadError(f"openings[{index}].width must be > 0.")
    center = value.get("center", value.get("point"))
    return {
        "opening_id": str(opening_id),
        "type": str(value.get("type", "entry")),
        "center": _point(center, label=f"openings[{index}].center"),
        "width": width,
    }


def _normalize_zone(value: Any, *, index: int, id_key: str, output_id_key: str, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ShellLoadError(f"{label} must contain objects.")
    zone_id = value.get(output_id_key) or value.get(id_key) or value.get("id")
    if not zone_id:
        raise ShellLoadError(f"{label}[{index}].{output_id_key} is required.")
    return {
        output_id_key: str(zone_id),
        "bbox": _normalize_bbox(value.get("bbox"), label=f"{label}[{index}]"),
    }


def _legacy_space_payload(raw: dict[str, Any]) -> dict[str, Any] | None:
    spaces = raw.get("spaces")
    if not isinstance(spaces, list) or not spaces:
        return None
    first_space = spaces[0]
    if not isinstance(first_space, dict):
        raise ShellLoadError("spaces must contain objects.")

    drawing_id = str(raw.get("drawing_id", "manual-shell"))
    shell_id = drawing_id.replace("drawing-", "shell-", 1) if drawing_id.startswith("drawing-") else f"shell-{drawing_id}"
    avoid_zones = first_space.get("avoid_zones", [])
    if not isinstance(avoid_zones, list):
        raise ShellLoadError("spaces[0].avoid_zones must be a list.")

    return {
        "version": raw.get("version", "0.1"),
        "shell_id": shell_id,
        "units": raw.get("units"),
        "boundary": first_space.get("boundary"),
        "openings": first_space.get("entrances", []),
        "fixed_obstacles": [
            {"obstacle_id": item.get("obstacle_id", item.get("id")), "bbox": item.get("bbox")}
            for item in avoid_zones
            if isinstance(item, dict)
        ],
        "no_place_zones": [
            {"zone_id": item.get("zone_id", item.get("id")), "bbox": item.get("bbox")}
            for item in avoid_zones
            if isinstance(item, dict)
        ],
        "required_connections": [],
        "building_elements": [],
        "uncertainties": raw.get("uncertainties", []),
        "source": {"type": str(raw.get("source", "manual_annotation"))},
    }


def load_manual_shell(path: str | Path) -> dict[str, Any]:
    """Load a manual shell annotation file and return normalized SHELL_MODEL data."""

    shell_path = Path(path)
    raw = _load_json(shell_path)
    payload = _legacy_space_payload(raw) or deepcopy(raw)

    units = payload.get("units")
    if not isinstance(units, str) or not units:
        raise ShellLoadError("units is required.")
    if units not in {"mm", "cm", "m"}:
        raise ShellLoadError("units must be mm, cm or m.")

    boundary = _normalize_boundary(payload.get("boundary"))

    openings = [
        _normalize_opening(opening, index=index)
        for index, opening in enumerate(payload.get("openings", []))
    ]
    fixed_obstacles = [
        _normalize_zone(obstacle, index=index, id_key="obstacle_id", output_id_key="obstacle_id", label="fixed_obstacles")
        for index, obstacle in enumerate(payload.get("fixed_obstacles", []))
    ]
    no_place_zones = [
        _normalize_zone(zone, index=index, id_key="zone_id", output_id_key="zone_id", label="no_place_zones")
        for index, zone in enumerate(payload.get("no_place_zones", []))
    ]

    for obstacle in fixed_obstacles:
        if not _bbox_inside(obstacle["bbox"], boundary):
            raise ShellLoadError(f"fixed_obstacles[{obstacle['obstacle_id']}] bbox is outside boundary.")
    for zone in no_place_zones:
        if not _bbox_inside(zone["bbox"], boundary):
            raise ShellLoadError(f"no_place_zones[{zone['zone_id']}] bbox is outside boundary.")

    uncertainties = list(payload.get("uncertainties", []))
    if boundary["type"] == "polygon":
        uncertainties.append("Arbitrary polygon shell boundaries have finite support until Phase Q geometry is implemented.")

    source = payload.get("source", {})
    if isinstance(source, str):
        source = {"type": source}
    if not isinstance(source, dict):
        source = {"type": "manual_annotation"}
    source.setdefault("type", "manual_annotation")
    source.setdefault("path", str(shell_path))

    return {
        "version": str(payload.get("version", "0.1")),
        "shell_id": str(payload.get("shell_id", "shell-manual")),
        "units": units,
        "boundary": boundary,
        "openings": openings,
        "fixed_obstacles": fixed_obstacles,
        "no_place_zones": no_place_zones,
        "required_connections": list(payload.get("required_connections", [])),
        "building_elements": list(payload.get("building_elements", [])),
        "uncertainties": uncertainties,
        "source": source,
    }
