"""Split shell space around circulation paths into function zone candidates."""

from __future__ import annotations

from typing import Any

from core.geometry_backends.rect2d import rect_area, rect_center, subtract_no_place_zones


GENERIC_FUNCTIONS = {
    "left": ["display", "storage", "desk_area", "service", "living"],
    "right": ["display", "storage", "desk_area", "service", "living"],
    "end": ["service", "storage", "display"],
}

PREFERRED_OBJECTS = {
    "display": ["display_unit", "shelf", "cabinet"],
    "storage": ["cabinet", "shelf"],
    "desk_area": ["desk", "chair"],
    "service": ["counter", "cabinet"],
    "living": ["sofa", "table"],
}


def _bbox(value: dict[str, Any], *, label: str) -> dict[str, list[float]]:
    min_point = value.get("min")
    max_point = value.get("max")
    if not isinstance(min_point, list) or not isinstance(max_point, list):
        raise ValueError(f"{label} must contain min/max.")
    return {"min": [float(min_point[0]), float(min_point[1])], "max": [float(max_point[0]), float(max_point[1])]}


def _no_place_zones(shell_model: dict[str, Any], constraints: Any) -> list[dict[str, Any]]:
    zones = list(shell_model.get("no_place_zones", []))
    if isinstance(constraints, dict):
        zones.extend(constraints.get("no_place_zones", []))
    return [zone for zone in zones if isinstance(zone, dict) and isinstance(zone.get("bbox"), dict)]


def _constraint_labels(constraints: Any) -> list[str]:
    if isinstance(constraints, list):
        return [str(item) for item in constraints]
    if isinstance(constraints, dict):
        return [str(item) for item in constraints.get("labels", [])]
    return []


def _candidate_functions(side: str) -> list[str]:
    return list(GENERIC_FUNCTIONS.get(side, GENERIC_FUNCTIONS["left"]))


def _preferred_objects(functions: list[str]) -> list[str]:
    objects: list[str] = []
    for function in functions:
        for object_type in PREFERRED_OBJECTS.get(function, []):
            if object_type not in objects:
                objects.append(object_type)
    return objects


def _score_zone(
    *,
    geometry: dict[str, list[float]],
    frontage: float,
    depth: float,
    uncertainties: list[str],
    shell_model: dict[str, Any],
) -> float:
    area = rect_area(geometry)
    area_score = min(area / 5_000_000, 1.0)
    depth_score = min(depth / 1200, 1.0)
    frontage_score = min(frontage / 3000, 1.0)
    entry_distance_score = 1.0
    openings = shell_model.get("openings", [])
    if openings:
        center = rect_center(geometry)
        opening = openings[0] if isinstance(openings[0], dict) else {}
        opening_center = opening.get("center", center)
        if isinstance(opening_center, list) and len(opening_center) == 2:
            distance = ((center[0] - float(opening_center[0])) ** 2 + (center[1] - float(opening_center[1])) ** 2) ** 0.5
            entry_distance_score = max(0.25, 1.0 - distance / 12000)
    score = (area_score * 0.35) + (depth_score * 0.25) + (frontage_score * 0.25) + (entry_distance_score * 0.15)
    if uncertainties:
        score *= 0.75
    return round(score, 4)


def _apply_no_place_zones(
    geometry: dict[str, list[float]],
    zones: list[dict[str, Any]],
) -> tuple[dict[str, list[float]], list[str]]:
    if not zones:
        return geometry, []
    result = subtract_no_place_zones({"type": "bbox", **geometry}, zones)
    if result["status"] == "pass":
        return geometry, []
    if result["rects"]:
        largest = max(result["rects"], key=rect_area)
        return largest, [f"no_place_zone subtraction returned {result['status']}; using largest conservative fragment."]
    return geometry, ["no_place_zone subtraction blocked reliable zone splitting."]


def _zone_from_rect(
    *,
    shell_model: dict[str, Any],
    circulation_model: dict[str, Any],
    path: dict[str, Any],
    side: str,
    geometry: dict[str, list[float]],
    frontage: float,
    depth: float,
    constraints: Any,
) -> dict[str, Any]:
    adjusted_geometry, uncertainties = _apply_no_place_zones(geometry, _no_place_zones(shell_model, constraints))
    functions = _candidate_functions(side)
    base_constraints = _constraint_labels(constraints)
    base_constraints.extend(
        [
            f"derived_from_circulation:{circulation_model['circulation_id']}",
            f"adjacent_to_path:{path['path_id']}",
        ]
    )
    area = rect_area(adjusted_geometry)
    score = _score_zone(
        geometry=adjusted_geometry,
        frontage=frontage,
        depth=depth,
        uncertainties=uncertainties,
        shell_model=shell_model,
    )
    zone_id = f"zone-{shell_model['shell_id']}-{circulation_model.get('strategy', 'path')}-{side}"
    return {
        "version": "0.1",
        "zone_id": zone_id,
        "shell_id": shell_model["shell_id"],
        "name": f"{side.title()} Function Zone",
        "purpose": functions[0],
        "boundary": adjusted_geometry,
        "geometry": adjusted_geometry,
        "area": area,
        "depth": depth,
        "frontage": frontage,
        "side_of_path": side,
        "candidate_functions": functions,
        "preferred_objects": _preferred_objects(functions),
        "constraints": base_constraints,
        "score": score,
        "uncertainties": uncertainties,
    }


def _union_path_surface_bbox(path: dict[str, Any]) -> dict[str, list[float]]:
    """Bounding box covering every circulation strip (L-shaped paths need the union, not segment[0])."""

    surfaces = path.get("path_surface", [])
    if not surfaces:
        raise ValueError("path.path_surface must not be empty")
    mins_x: list[float] = []
    mins_y: list[float] = []
    maxs_x: list[float] = []
    maxs_y: list[float] = []
    for surface in surfaces:
        if not isinstance(surface, dict):
            continue
        bbox = _bbox(surface, label="path_surface")
        mins_x.append(bbox["min"][0])
        mins_y.append(bbox["min"][1])
        maxs_x.append(bbox["max"][0])
        maxs_y.append(bbox["max"][1])
    if not mins_x:
        raise ValueError("path.path_surface must contain at least one bbox surface")
    return {
        "min": [min(mins_x), min(mins_y)],
        "max": [max(maxs_x), max(maxs_y)],
    }


def split_zones(
    shell_model: dict[str, Any],
    circulation_model: dict[str, Any],
    constraints: Any,
) -> list[dict[str, Any]]:
    """Split a bbox shell around the circulation path envelope."""

    boundary = shell_model.get("boundary", {})
    if not isinstance(boundary, dict) or boundary.get("type", "bbox") != "bbox":
        return []
    paths = circulation_model.get("paths", [])
    if not paths or not isinstance(paths[0], dict):
        return []
    path = paths[0]
    surfaces = path.get("path_surface", [])
    if not surfaces:
        return []

    shell_bbox = _bbox(boundary, label="shell.boundary")
    strip = _union_path_surface_bbox(path)
    strip_width = strip["max"][0] - strip["min"][0]
    strip_depth = strip["max"][1] - strip["min"][1]
    zones: list[dict[str, Any]] = []

    if strip_width >= strip_depth:
        candidates = [
            ("right", {"min": [shell_bbox["min"][0], shell_bbox["min"][1]], "max": [shell_bbox["max"][0], strip["min"][1]]}),
            ("left", {"min": [shell_bbox["min"][0], strip["max"][1]], "max": [shell_bbox["max"][0], shell_bbox["max"][1]]}),
        ]
        for side, geometry in candidates:
            if geometry["min"][1] >= geometry["max"][1]:
                continue
            depth = geometry["max"][1] - geometry["min"][1]
            frontage = geometry["max"][0] - geometry["min"][0]
            zones.append(
                _zone_from_rect(
                    shell_model=shell_model,
                    circulation_model=circulation_model,
                    path=path,
                    side=side,
                    geometry=geometry,
                    frontage=frontage,
                    depth=depth,
                    constraints=constraints,
                )
            )
    else:
        candidates = [
            ("left", {"min": [shell_bbox["min"][0], shell_bbox["min"][1]], "max": [strip["min"][0], shell_bbox["max"][1]]}),
            ("right", {"min": [strip["max"][0], shell_bbox["min"][1]], "max": [shell_bbox["max"][0], shell_bbox["max"][1]]}),
        ]
        for side, geometry in candidates:
            if geometry["min"][0] >= geometry["max"][0]:
                continue
            depth = geometry["max"][0] - geometry["min"][0]
            frontage = geometry["max"][1] - geometry["min"][1]
            zones.append(
                _zone_from_rect(
                    shell_model=shell_model,
                    circulation_model=circulation_model,
                    path=path,
                    side=side,
                    geometry=geometry,
                    frontage=frontage,
                    depth=depth,
                    constraints=constraints,
                )
            )

    return sorted(zones, key=lambda zone: zone["score"], reverse=True)
