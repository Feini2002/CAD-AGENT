"""End-to-end non-CAD Core pipeline for repeatable verification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.plan_engine.dry_run_report import create_dry_run_report
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


def _layout_preferences(raw_preferences: dict[str, Any]) -> dict[str, Any]:
    circulation = raw_preferences.get("circulation", {}) if isinstance(raw_preferences.get("circulation"), dict) else {}
    return {
        "main_aisle_width_mm": circulation.get("main_aisle_width_mm", 0),
        "minimum_clearance_mm": circulation.get("secondary_aisle_width_mm", 100),
        "object_spacing_mm": circulation.get("secondary_aisle_width_mm", 300),
        "layout_weights": raw_preferences.get("layout_weights", {}),
    }


def run_non_cad_pipeline(workflow_path: Path, *, output_dir: Path) -> dict[str, Any]:
    root = _find_project_root(workflow_path.resolve())
    workflow = load_json(workflow_path)
    inputs = workflow.get("inputs", {})
    brief = load_json(root / inputs["design_brief"])
    drawing = load_json(root / inputs["drawing_model"])
    object_spec = load_json(root / inputs["object_spec"])
    style_profile = load_json(root / inputs["style_profile"]) if inputs.get("style_profile") else {}
    preferences = load_json(root / inputs["preferences"]) if inputs.get("preferences") else {}
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
