"""End-to-end non-CAD Core pipeline for repeatable verification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.plan_engine.dry_run_report import create_dry_run_report
from core.path_safety import resolve_under_project_output, resolve_under_project_root
from core.plan_engine.model_to_plan import model_to_plans
from core.project_model.project_builder import build_project_model
from core.proposal_engine.design_proposal import create_design_proposal
from core.schemas.validator import load_json
from core.verification.verification_report import build_verification_report
from core.layout_engine.basic_layout import create_layout_candidates
from core.object_engine.parametric_objects import apply_style_to_object_spec


def _find_project_root(path: Path) -> Path:
    for parent in [path.parent, *path.parents]:
        if (parent / "CORE_RESTRUCTURE_PLAN.md").exists():
            return parent
    return path.parent


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _invalid(errors: list[str]) -> dict[str, Any]:
    return {"status": "invalid", "errors": errors, "artifacts": {}}


def _resolve_input(root: Path, inputs: dict[str, Any], key: str, *, required: bool = True) -> Path | None:
    value = inputs.get(key)
    if value in {None, ""} and not required:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"inputs.{key} must be a non-empty string")
    path = resolve_under_project_root(root, Path(value), label=f"inputs.{key}")
    if not path.is_file():
        raise ValueError(f"inputs.{key} does not exist: {path}")
    return path


def _layout_preferences(raw_preferences: dict[str, Any]) -> dict[str, Any]:
    circulation = raw_preferences.get("circulation", {}) if isinstance(raw_preferences.get("circulation"), dict) else {}
    return {
        "main_aisle_width_mm": circulation.get("main_aisle_width_mm", 0),
        "minimum_clearance_mm": circulation.get("secondary_aisle_width_mm", 100),
        "object_spacing_mm": circulation.get("secondary_aisle_width_mm", 300),
        "layout_weights": raw_preferences.get("layout_weights", {}),
    }


def run_non_cad_pipeline(workflow_path: Path, *, output_dir: Path) -> dict[str, Any]:
    try:
        root = _find_project_root(workflow_path.resolve())
        workflow_path = resolve_under_project_root(root, workflow_path, label="workflow_path")
        output_dir = resolve_under_project_output(root, output_dir, label="output_dir")
        workflow = load_json(workflow_path)
        inputs = workflow.get("inputs", {})
        if not isinstance(inputs, dict):
            raise ValueError("inputs must be an object")
        brief_path = _resolve_input(root, inputs, "design_brief")
        drawing_path = _resolve_input(root, inputs, "drawing_model")
        object_spec_path = _resolve_input(root, inputs, "object_spec")
        style_profile_path = _resolve_input(root, inputs, "style_profile", required=False)
        preferences_path = _resolve_input(root, inputs, "preferences", required=False)
        brief = load_json(brief_path)
        drawing = load_json(drawing_path)
        object_spec = load_json(object_spec_path)
        style_profile = load_json(style_profile_path) if style_profile_path else {}
        preferences = load_json(preferences_path) if preferences_path else {}
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _invalid([str(exc)])
    if style_profile:
        object_spec = apply_style_to_object_spec(object_spec, style_profile)

    project_result = build_project_model(brief, drawing)
    project_model = project_result.project_model
    layout = create_layout_candidates(
        project_model=project_model,
        object_specs=[object_spec],
        preferences=_layout_preferences(preferences),
    )
    proposal = create_design_proposal(
        brief=brief,
        project_model=project_model,
        object_spec=object_spec,
        layout_proposal=layout,
    )
    plan_result = model_to_plans(object_spec=object_spec, layout_proposal=layout, design_proposal=proposal)
    if plan_result["status"] != "ok":
        return {"status": "blocked", "errors": plan_result["errors"], "artifacts": {}}
    cad_plan = plan_result["plans"][0]["cad_plan"]
    dry_run_report = create_dry_run_report(cad_plan)

    paths = {
        "project_model": output_dir / "project_model.json",
        "object_spec": output_dir / "object_spec.json",
        "layout_proposal": output_dir / "layout_proposal.json",
        "design_proposal": output_dir / "design_proposal.json",
        "cad_plan": output_dir / "cad_plan.json",
        "dry_run_report": output_dir / "dry_run_report.json",
        "verification_report": output_dir / "verification_report.json",
    }
    _write_json(paths["project_model"], project_model)
    _write_json(paths["object_spec"], object_spec)
    _write_json(paths["layout_proposal"], layout)
    _write_json(paths["design_proposal"], proposal)
    _write_json(paths["cad_plan"], cad_plan)
    _write_json(paths["dry_run_report"], dry_run_report)
    verification_report = build_verification_report(plan_path=paths["cad_plan"])
    _write_json(paths["verification_report"], verification_report)

    return {
        "status": "ok",
        "artifacts": {key: str(path) for key, path in paths.items()},
        "dry_run_report": dry_run_report,
        "verification_report": verification_report,
        "preferences": preferences,
        "warnings": project_result.warnings,
    }
