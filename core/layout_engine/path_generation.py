"""Generate deterministic circulation path candidates from shell context."""

from __future__ import annotations

from typing import Any

from core.geometry_backends.rect2d import path_to_rect_strips, rect_intersects


def _boundary(project_model: dict[str, Any]) -> dict[str, list[float | int]]:
    spaces = project_model.get("spaces", [])
    if not spaces or not isinstance(spaces[0], dict):
        raise ValueError("project_model.spaces[0] is required.")
    boundary = spaces[0].get("boundary")
    if not isinstance(boundary, dict):
        raise ValueError("project_model.spaces[0].boundary is required.")
    return boundary


def _point(value: Any, *, fallback: list[float]) -> list[float]:
    if isinstance(value, list) and len(value) == 2 and all(isinstance(item, (int, float)) for item in value):
        return [float(value[0]), float(value[1])]
    return list(fallback)


def _main_opening(project_model: dict[str, Any], boundary: dict[str, list[float | int]]) -> dict[str, Any]:
    openings = project_model.get("shell_context", {}).get("openings", [])
    if isinstance(openings, list):
        for opening in openings:
            if isinstance(opening, dict) and opening.get("type") == "entry":
                return opening
        for opening in openings:
            if isinstance(opening, dict):
                return opening
    center_y = (float(boundary["min"][1]) + float(boundary["max"][1])) / 2
    return {"opening_id": "entry-fallback", "center": [float(boundary["min"][0]), center_y], "width": 0}


def _target_connection(project_model: dict[str, Any], boundary: dict[str, list[float | int]], start: list[float]) -> dict[str, Any]:
    required = project_model.get("shell_context", {}).get("required_connections", [])
    if isinstance(required, list):
        for connection in required:
            if isinstance(connection, dict) and isinstance(connection.get("point"), list):
                return connection
    return {
        "connection_id": "deep-shell",
        "target": "deep-shell",
        "point": [float(boundary["max"][0]), start[1]],
    }


def _fixed_obstacles(project_model: dict[str, Any]) -> list[dict[str, Any]]:
    obstacles = project_model.get("shell_context", {}).get("fixed_obstacles", [])
    return [obstacle for obstacle in obstacles if isinstance(obstacle, dict) and isinstance(obstacle.get("bbox"), dict)]


def _blocked_reasons(
    *,
    path_surface: list[dict[str, list[float]]],
    obstacles: list[dict[str, Any]],
    width: float,
    minimum_width: float,
    polyline: list[list[float]],
    required_connection: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    if width < minimum_width:
        reasons.append(f"width {width} below minimum {minimum_width}.")
    for obstacle in obstacles:
        obstacle_id = obstacle.get("obstacle_id", obstacle.get("id", "unknown"))
        if any(rect_intersects(strip, obstacle["bbox"]) for strip in path_surface):
            reasons.append(f"path overlaps fixed_obstacle:{obstacle_id}.")
    target_point = _point(required_connection.get("point"), fallback=polyline[-1])
    if target_point not in polyline:
        connection_id = required_connection.get("connection_id", "required_connection")
        reasons.append(f"required_connection:{connection_id} not connected.")
    return reasons


def _candidate(
    *,
    project_model: dict[str, Any],
    strategy: str,
    polyline: list[list[float]],
    width: float,
    minimum_width: float,
    connects: list[str],
    base_score: float,
    weight: float,
    required_connection: dict[str, Any],
) -> dict[str, Any]:
    shell_id = str(project_model.get("shell_id", project_model.get("project_id", "shell-unknown")))
    path_surface = path_to_rect_strips(polyline, width=width)
    reasons = _blocked_reasons(
        path_surface=path_surface,
        obstacles=_fixed_obstacles(project_model),
        width=width,
        minimum_width=minimum_width,
        polyline=polyline,
        required_connection=required_connection,
    )
    status = "blocked" if reasons else "pass"
    score = round(base_score * weight * (0.4 if reasons else 1.0), 4)
    path = {
        "path_id": f"path-{strategy}-main",
        "type": "main",
        "width_mm": width,
        "start": polyline[0],
        "end": polyline[-1],
        "polyline": polyline,
        "connects": connects,
        "path_surface": path_surface,
        "blocked_reasons": reasons,
        "score": score,
    }
    return {
        "version": "0.1",
        "circulation_id": f"circulation-{shell_id}-{strategy}",
        "shell_id": shell_id,
        "strategy": strategy,
        "status": status,
        "score": score,
        "paths": [path],
    }


def generate_circulation_candidates(
    project_model: dict[str, Any],
    preferences: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Generate straight, L-shaped and along-wall circulation candidates."""

    preferences = preferences or {}
    boundary = _boundary(project_model)
    width = float(preferences.get("main_aisle_width_mm", preferences.get("circulation_width_mm", 1200)))
    minimum_width = float(preferences.get("minimum_circulation_width_mm", 900))
    weights = preferences.get("circulation_strategy_weights", {})
    if not isinstance(weights, dict):
        weights = {}

    opening = _main_opening(project_model, boundary)
    start = _point(opening.get("center"), fallback=[float(boundary["min"][0]), 0.0])
    target = _target_connection(project_model, boundary, start)
    target_point = _point(target.get("point"), fallback=[float(boundary["max"][0]), start[1]])
    opening_id = str(opening.get("opening_id", opening.get("id", "entry-fallback")))
    target_id = str(target.get("target", target.get("connection_id", "deep-shell")))
    min_x = float(boundary["min"][0])
    max_x = float(boundary["max"][0])
    min_y = float(boundary["min"][1])
    offset_y = min_y + width / 2
    offset_x = min_x + width / 2

    straight_end = [max_x, start[1]]
    l_elbow = [target_point[0], start[1]]
    along_wall = [
        start,
        [offset_x, start[1]],
        [offset_x, offset_y],
        [target_point[0], offset_y],
        target_point,
    ]

    candidates = [
        _candidate(
            project_model=project_model,
            strategy="straight_spine",
            polyline=[start, straight_end],
            width=width,
            minimum_width=minimum_width,
            connects=[opening_id, "deep-shell"],
            base_score=0.8,
            weight=float(weights.get("straight_spine", 1.0)),
            required_connection=target,
        ),
        _candidate(
            project_model=project_model,
            strategy="l_spine",
            polyline=[start, l_elbow, target_point],
            width=width,
            minimum_width=minimum_width,
            connects=[opening_id, target_id],
            base_score=0.75,
            weight=float(weights.get("l_spine", 1.0)),
            required_connection=target,
        ),
        _candidate(
            project_model=project_model,
            strategy="along_wall",
            polyline=along_wall,
            width=width,
            minimum_width=minimum_width,
            connects=[opening_id, target_id],
            base_score=0.65,
            weight=float(weights.get("along_wall", 1.0)),
            required_connection=target,
        ),
    ]
    return sorted(candidates, key=lambda candidate: candidate["score"], reverse=True)
