"""Build PROJECT_MODEL artifacts from a structured brief and drawing model."""

from __future__ import annotations

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


def build_project_model(
    brief: dict[str, Any],
    drawing_model: dict[str, Any],
    *,
    defaults: dict[str, Any] | None = None,
) -> ProjectBuildResult:
    defaults = defaults or {}
    units = drawing_model.get("units") or defaults.get("units")
    if not isinstance(units, str):
        raise ProjectModelError("drawing_model.units or defaults.units is required.")

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
        pending_questions: list[str] = []
        warnings: list[str] = []
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
        "constraints": list(brief.get("constraints", [])),
        "pending_questions": pending_questions,
    }
    return ProjectBuildResult(
        project_model=project_model,
        provenance=provenance,
        warnings=warnings,
        pending_questions=pending_questions,
    )
