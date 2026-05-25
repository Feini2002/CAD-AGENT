"""Build PROJECT_MODEL artifacts from a structured brief and drawing model."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any


DEFAULT_PREVIEW_BOUNDARY = {"min": [0, 0], "max": [3000, 1800]}


class ProjectModelError(ValueError):
    """Raised when brief and drawing data cannot form a project model."""


@dataclass(frozen=True)
class ProjectBuildResult:
    project_model: dict[str, Any]
    provenance: list[dict[str, str]]
    warnings: list[str]
    pending_questions: list[str]


def _validate_boundary(boundary: dict[str, Any], *, label: str) -> None:
    try:
        min_point = boundary["min"]
        max_point = boundary["max"]
    except KeyError as exc:
        raise ProjectModelError(f"{label} boundary is missing {exc.args[0]}.") from exc
    if not isinstance(min_point, list) or not isinstance(max_point, list) or len(min_point) != 2 or len(max_point) != 2:
        raise ProjectModelError(f"{label} boundary must use 2D min/max points.")
    if min_point[0] >= max_point[0] or min_point[1] >= max_point[1]:
        raise ProjectModelError(f"{label} boundary min must be lower than max.")


def _space_from_drawing(space: dict[str, Any]) -> dict[str, Any]:
    boundary = space.get("boundary")
    if not isinstance(boundary, dict):
        raise ProjectModelError(f"{space.get('space_id', 'space')} boundary is required.")
    _validate_boundary(boundary, label=str(space.get("space_id", "space")))
    return {
        "space_id": str(space.get("space_id", "space-1")),
        "name": str(space.get("name", "Space")),
        "boundary": boundary,
    }


def _constraint_ids(shell_model: dict[str, Any]) -> list[str]:
    constraints: list[str] = []
    for obstacle in shell_model.get("fixed_obstacles", []):
        if isinstance(obstacle, dict) and obstacle.get("obstacle_id"):
            constraints.append(f"fixed_obstacle:{obstacle['obstacle_id']}")
    for zone in shell_model.get("no_place_zones", []):
        if isinstance(zone, dict) and zone.get("zone_id"):
            constraints.append(f"no_place_zone:{zone['zone_id']}")
    for opening in shell_model.get("openings", []):
        if isinstance(opening, dict) and opening.get("opening_id"):
            constraints.append(f"opening:{opening['opening_id']}")
    return constraints


def _spaces_from_shell(shell_model: dict[str, Any]) -> list[dict[str, Any]]:
    boundary = shell_model.get("boundary")
    if not isinstance(boundary, dict):
        raise ProjectModelError("shell_model.boundary is required.")
    _validate_boundary(boundary, label="shell_model.boundary")
    shell_id = str(shell_model.get("shell_id", "shell-main"))
    return [
        {
            "space_id": f"space-{shell_id.replace('shell-', '', 1)}",
            "name": "Shell Area",
            "boundary": {"min": boundary["min"], "max": boundary["max"]},
            "shell_id": shell_id,
            "source": "shell_model.boundary",
        }
    ]


def _shell_context(shell_model: dict[str, Any]) -> dict[str, Any]:
    return {
        "openings": deepcopy(shell_model.get("openings", [])),
        "fixed_obstacles": deepcopy(shell_model.get("fixed_obstacles", [])),
        "no_place_zones": deepcopy(shell_model.get("no_place_zones", [])),
        "required_connections": deepcopy(shell_model.get("required_connections", [])),
        "building_elements": deepcopy(shell_model.get("building_elements", [])),
    }


def build_project_model(
    brief: dict[str, Any],
    drawing_model: dict[str, Any],
    *,
    defaults: dict[str, Any] | None = None,
    shell_model: dict[str, Any] | None = None,
) -> ProjectBuildResult:
    defaults = defaults or {}
    units = (shell_model or {}).get("units") or drawing_model.get("units") or defaults.get("units")
    if not isinstance(units, str):
        raise ProjectModelError("drawing_model.units or defaults.units is required.")

    if shell_model is not None:
        spaces = _spaces_from_shell(shell_model)
        shell_id = str(shell_model.get("shell_id", "shell-main"))
        provenance = [{"target": "spaces", "source": "shell_model.boundary"}]
        warnings = []
        pending_questions = list(shell_model.get("uncertainties", []))
        shell_constraints = _constraint_ids(shell_model)
    else:
        shell_id = ""
        shell_constraints = []
        drawing_spaces = drawing_model.get("spaces", [])
        if drawing_spaces:
            if not isinstance(drawing_spaces, list):
                raise ProjectModelError("drawing_model.spaces must be a list.")
            invalid_items = [space for space in drawing_spaces if not isinstance(space, dict)]
            if invalid_items:
                raise ProjectModelError("drawing_model.spaces must contain only space objects.")
            spaces = [_space_from_drawing(space) for space in drawing_spaces if isinstance(space, dict)]
            if not spaces:
                raise ProjectModelError("drawing_model.spaces did not contain any valid space.")
            provenance = [{"target": "spaces", "source": "drawing_model.spaces"}]
            pending_questions = []
            warnings = []
        else:
            boundary = dict(defaults.get("preview_boundary", DEFAULT_PREVIEW_BOUNDARY))
            _validate_boundary(boundary, label="default_preview_space")
            spaces = [{"space_id": "space-preview", "name": "Preview Area", "boundary": boundary}]
            provenance = [{"target": "spaces", "source": "default_preview_space"}]
            pending_questions = ["No drawing spaces were provided; using a default preview area."]
            warnings = ["project_model uses default preview space"]

    project_model = {
        "version": "0.1",
        "project_id": f"project-{brief['brief_id'].replace('brief-', '')}",
        "domain": brief.get("domain", "generic"),
        "units": units,
        "brief_id": brief["brief_id"],
        "drawing_model_id": drawing_model["drawing_id"],
        "spaces": spaces,
        "requirements": [brief.get("user_request", "")],
        "constraints": list(brief.get("constraints", [])) + shell_constraints,
        "uncertainties": list(shell_model.get("uncertainties", [])) if shell_model is not None else [],
        "pending_questions": pending_questions,
    }
    if shell_model is not None:
        project_model["shell_id"] = shell_id
        project_model["source"] = {"type": "shell_model", "shell_id": shell_id}
        project_model["shell_context"] = _shell_context(shell_model)
    return ProjectBuildResult(
        project_model=project_model,
        provenance=provenance,
        warnings=warnings,
        pending_questions=pending_questions,
    )
