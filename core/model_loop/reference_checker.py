"""Validate workflow artifact schemas and cross-model references."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.schemas.registry import get_schema_path, infer_model_type
from core.schemas.validator import load_json, validate_value


@dataclass
class WorkflowArtifact:
    model_type: str
    path: Path
    data: dict[str, Any]
    role: str = "input"


@dataclass
class WorkflowIndex:
    path: Path
    root: Path
    artifacts: dict[str, WorkflowArtifact]


def _find_project_root(path: Path) -> Path:
    for parent in [path.parent, *path.parents]:
        if (parent / "CORE_RESTRUCTURE_PLAN.md").exists():
            return parent
    return path.parent


def _artifact_from_step(step: str | dict[str, Any], *, root: Path) -> WorkflowArtifact:
    if isinstance(step, str):
        path = root / step
        data = load_json(path)
        return WorkflowArtifact(model_type=infer_model_type(data), path=path, data=data)
    model_type = str(step["model_type"])
    path = root / str(step["path"])
    data = load_json(path)
    return WorkflowArtifact(model_type=model_type, path=path, data=data, role=str(step.get("role", "input")))


def load_workflow_index(path: Path) -> WorkflowIndex:
    root = _find_project_root(path.resolve())
    data = json.loads(path.read_text(encoding="utf-8"))
    steps = data.get("artifacts", data.get("steps", []))
    artifacts: dict[str, WorkflowArtifact] = {}
    for step in steps:
        artifact = _artifact_from_step(step, root=root)
        artifacts[artifact.model_type] = artifact
    return WorkflowIndex(path=path, root=root, artifacts=artifacts)


def validate_workflow_schemas(index: WorkflowIndex) -> list[str]:
    errors: list[str] = []
    for model_type, artifact in index.artifacts.items():
        try:
            schema = load_json(get_schema_path(model_type))
        except ValueError as exc:
            errors.append(str(exc))
            continue
        for error in validate_value(artifact.data, schema):
            errors.append(f"{model_type}: {error}")
    return errors


def validate_references(index: WorkflowIndex) -> list[str]:
    artifacts = index.artifacts
    errors: list[str] = []

    brief = artifacts.get("design_brief")
    drawing = artifacts.get("drawing_model")
    project = artifacts.get("project_model")
    object_spec = artifacts.get("object_spec")
    style = artifacts.get("style_profile")
    layout = artifacts.get("layout_proposal")
    proposal = artifacts.get("design_proposal")
    cad_plan = artifacts.get("cad_plan")

    if brief and project and project.data.get("brief_id") != brief.data.get("brief_id"):
        errors.append("project brief_id does not match design_brief.brief_id.")
    if drawing and project and project.data.get("drawing_model_id") != drawing.data.get("drawing_id"):
        errors.append("project drawing_model_id does not match drawing_model.drawing_id.")
    if project and layout and layout.data.get("project_id") != project.data.get("project_id"):
        errors.append("layout project_id does not match project_model.project_id.")
    if brief and proposal and proposal.data.get("brief_id") != brief.data.get("brief_id"):
        errors.append("proposal brief_id does not match design_brief.brief_id.")
    if project and proposal and proposal.data.get("project_id") != project.data.get("project_id"):
        errors.append("proposal project_id does not match project_model.project_id.")
    if object_spec and style and object_spec.data.get("style_profile_id") != style.data.get("style_id"):
        errors.append("object style_profile_id does not match style_profile.style_id.")
    if object_spec and layout:
        object_id = object_spec.data.get("object_id")
        for candidate in layout.data.get("candidates", []):
            for placement in candidate.get("placements", []):
                if placement.get("object_id") != object_id:
                    errors.append("layout placement object_id does not match object_spec.object_id.")
    if object_spec and cad_plan:
        plan_object = cad_plan.data.get("object", {})
        ref = plan_object.get("object_spec_id")
        if ref and ref != object_spec.data.get("object_id"):
            errors.append("cad_plan object_spec_id does not match object_spec.object_id.")

    return errors
