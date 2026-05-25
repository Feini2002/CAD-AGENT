"""Blank-shell layout pipeline from SHELL_MODEL to non-CAD verification artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.block_engine.block_library import load_block_library
from core.drawing_analysis.shell_loader import load_manual_shell
from core.layout_engine.path_generation import generate_circulation_candidates
from core.layout_engine.placement import create_zone_placements
from core.layout_engine.zone_splitter import split_zones
from core.object_engine.parametric_objects import create_object_spec
from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.model_to_plan import model_to_plans
from core.project_model.project_builder import build_project_model
from core.proposal_engine.design_proposal import create_design_proposal
from core.schemas.validator import load_json
from core.verification.verification_report import build_verification_report


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _find_project_root(path: Path) -> Path:
    for parent in [path.parent, *path.parents]:
        if (parent / "CORE_RESTRUCTURE_PLAN.md").exists():
            return parent
    return PROJECT_ROOT


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _resolve_under_root(root: Path, value: str, label: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    if not _is_relative_to(resolved, root.resolve()):
        raise ValueError(f"{label} must stay under project root")
    return resolved


def _resolve_output_dir(root: Path, output_dir: Path) -> Path:
    candidate = output_dir if output_dir.is_absolute() else root / output_dir
    resolved = candidate.resolve()
    if not _is_relative_to(resolved, (root / "output").resolve()):
        raise ValueError("output_dir must stay under project output directory")
    return resolved


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _validate_workflow_inputs(workflow: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    inputs = workflow.get("inputs")
    if not isinstance(inputs, dict):
        return ["inputs must be an object"]
    for key in ["design_brief", "drawing_model", "shell_model"]:
        value = inputs.get(key)
        if value is None or value == "":
            errors.append(f"inputs.{key} is required")
        elif not isinstance(value, str):
            errors.append(f"inputs.{key} must be a non-empty string path")
    for key in ["preferences", "block_library"]:
        if key in inputs:
            value = inputs[key]
            if not isinstance(value, str) or not value:
                errors.append(f"inputs.{key} must be a non-empty string path when provided")
    object_types = workflow.get("object_types", ["display_unit", "counter", "shelf", "desk", "chair"])
    if (
        not isinstance(object_types, list)
        or not object_types
        or not all(isinstance(item, str) and item for item in object_types)
    ):
        errors.append("object_types must be a non-empty list")
    return errors


def _resolve_workflow_input_paths(root: Path, inputs: dict[str, Any]) -> tuple[dict[str, Path], list[str]]:
    paths: dict[str, Path] = {}
    errors: list[str] = []
    for key in ["design_brief", "drawing_model", "shell_model", "preferences", "block_library"]:
        value = inputs.get(key)
        if not isinstance(value, str) or not value:
            continue
        try:
            path = _resolve_under_root(root, value, f"inputs.{key}")
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not path.exists():
            errors.append(f"inputs.{key} file does not exist")
            continue
        paths[key] = path
    return paths, errors


def _object_spec_from_placement(placement: dict[str, Any]) -> dict[str, Any]:
    object_type = str(placement["object_type"])
    source = placement.get("source", {})
    if source.get("type") == "object_spec_fallback" and isinstance(source.get("object_spec"), dict):
        return source["object_spec"]
    if source.get("type") == "block" and isinstance(source.get("block"), dict):
        size = source["block"].get("size", {})
        if isinstance(size, dict) and "width" in size and "depth" in size:
            return create_object_spec(object_type, width=size["width"], depth=size["depth"])
    return create_object_spec(object_type)


def _layout_from_placements(
    *,
    project_model: dict[str, Any],
    object_specs: list[dict[str, Any]],
    placements: list[dict[str, Any]],
) -> dict[str, Any]:
    mapped_placements: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    for spec, placement in zip(object_specs, placements):
        mapped_placements.append(
            {
                "object_id": spec["object_id"],
                "base_point": placement["base_point"],
                "rotation": placement["rotation"],
                "bbox": placement["bbox"],
            }
        )
        checks.append(
            {
                "name": f"placement:{spec['type']}",
                "status": "pass" if placement["status"] == "placed" else "fail",
                "message": "; ".join(placement.get("failure_reasons", [])) or "placed",
            }
        )
    score = sum(1 for check in checks if check["status"] == "pass") / max(len(checks), 1)
    return {
        "version": "0.1",
        "layout_id": f"layout-{project_model['project_id']}-blank-shell",
        "project_id": project_model["project_id"],
        "candidates": [
            {
                "candidate_id": "candidate-blank-shell-zone-placement",
                "score": round(score, 4),
                "placements": mapped_placements,
                "checks": checks,
            }
        ],
        "uncertainties": [] if score == 1 else ["One or more placements were blocked."],
    }


def _choose_zone_placements(
    *,
    zones: list[dict[str, Any]],
    shell: dict[str, Any],
    object_types: list[str],
    block_library: dict[str, Any],
    preferences: dict[str, Any],
    path_surfaces: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    candidate_zones = zones or [
        {
            "zone_id": "zone-fallback",
            "geometry": shell["boundary"],
            "boundary": shell["boundary"],
            "score": 0,
        }
    ]
    best_zone = candidate_zones[0]
    best_placements: list[dict[str, Any]] = []
    best_key: tuple[bool, int, int, float] | None = None
    for zone in candidate_zones:
        placements = create_zone_placements(
            [zone],
            object_types=object_types,
            block_library=block_library,
            preferences=preferences,
            path_surfaces=path_surfaces,
            fixed_obstacles=shell.get("fixed_obstacles", []),
        )
        placed_count = sum(1 for placement in placements if placement.get("status") == "placed")
        failed_count = len(placements) - placed_count
        key = (
            failed_count == 0,
            placed_count,
            -failed_count,
            float(zone.get("score", 0)),
        )
        if best_key is None or key > best_key:
            best_key = key
            best_zone = zone
            best_placements = placements
    return best_zone, best_placements


def run_blank_shell_pipeline(workflow_path: Path, *, output_dir: Path) -> dict[str, Any]:
    workflow_path = workflow_path.resolve()
    root = _find_project_root(workflow_path)
    try:
        output_dir = _resolve_output_dir(root, output_dir)
    except ValueError as exc:
        return {"status": "invalid", "errors": [str(exc)], "artifacts": {}, "metrics": {}}
    if not _is_relative_to(workflow_path, root.resolve()):
        return {"status": "invalid", "errors": ["workflow_path must stay under project root"], "artifacts": {}, "metrics": {}}
    if not workflow_path.exists():
        return {"status": "invalid", "errors": ["workflow file does not exist"], "artifacts": {}, "metrics": {}}
    try:
        workflow = load_json(workflow_path)
    except json.JSONDecodeError as exc:
        return {"status": "invalid", "errors": [f"workflow JSON is invalid: {exc}"], "artifacts": {}, "metrics": {}}
    except OSError as exc:
        return {"status": "invalid", "errors": [f"workflow file cannot be read: {exc}"], "artifacts": {}, "metrics": {}}
    if not isinstance(workflow, dict):
        return {"status": "invalid", "errors": ["workflow must be a JSON object"], "artifacts": {}, "metrics": {}}
    validation_errors = _validate_workflow_inputs(workflow)
    raw_inputs = workflow.get("inputs", {})
    resolved_inputs, path_errors = _resolve_workflow_input_paths(root, raw_inputs) if isinstance(raw_inputs, dict) else ({}, [])
    validation_errors.extend(path_errors)
    if validation_errors:
        return {"status": "invalid", "errors": validation_errors, "artifacts": {}, "metrics": {}}
    inputs = raw_inputs
    try:
        brief = load_json(resolved_inputs["design_brief"])
        drawing = load_json(resolved_inputs["drawing_model"])
        shell = load_manual_shell(resolved_inputs["shell_model"])
        preferences = load_json(resolved_inputs["preferences"]) if inputs.get("preferences") else {}
    except (OSError, json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
        return {"status": "invalid", "errors": [f"workflow input is invalid: {type(exc).__name__}: {exc}"], "artifacts": {}, "metrics": {}}
    object_types = workflow.get("object_types", ["display_unit", "counter", "shelf", "desk", "chair"])

    project_model = build_project_model(brief, drawing, shell_model=shell).project_model
    circulation_candidates = generate_circulation_candidates(project_model, preferences.get("circulation", preferences))
    circulation_for_zones = next(
        (candidate for candidate in circulation_candidates if candidate.get("strategy") == "straight_spine"),
        circulation_candidates[0],
    )
    zones = split_zones(shell, circulation_for_zones, constraints={})
    try:
        block_library = load_block_library(resolved_inputs["block_library"]) if inputs.get("block_library") else load_block_library()
    except (OSError, json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
        return {"status": "invalid", "errors": [f"block library is invalid: {type(exc).__name__}: {exc}"], "artifacts": {}, "metrics": {}}
    target_zone, placements = _choose_zone_placements(
        zones=zones,
        shell=shell,
        object_types=[str(item) for item in object_types],
        block_library=block_library,
        preferences=preferences.get("placement", {}),
        path_surfaces=circulation_for_zones["paths"][0].get("path_surface", []),
    )
    object_specs = [_object_spec_from_placement(placement) for placement in placements]
    layout = _layout_from_placements(project_model=project_model, object_specs=object_specs, placements=placements)
    proposal = create_design_proposal(
        brief=brief,
        project_model=project_model,
        object_spec=object_specs[0],
        layout_proposal=layout,
    )
    plan_result = model_to_plans(
        object_specs=object_specs,
        layout_proposal=layout,
        design_proposal=proposal,
        confirmed=not proposal.get("needs_confirmation", False),
    )
    if plan_result["status"] != "ok":
        return {"status": "blocked", "errors": plan_result["errors"], "artifacts": {}, "metrics": {}}
    cad_plans = [item["cad_plan"] for item in plan_result["plans"]]
    dry_run_report = create_dry_run_report(cad_plans[0])

    paths = {
        "shell_model": output_dir / "shell_model.json",
        "project_model": output_dir / "project_model.json",
        "circulation_candidates": output_dir / "circulation_candidates.json",
        "function_zones": output_dir / "function_zones.json",
        "placements": output_dir / "placements.json",
        "layout_proposal": output_dir / "layout_proposal.json",
        "design_proposal": output_dir / "design_proposal.json",
        "cad_plan": output_dir / "cad_plan.json",
        "cad_plans": output_dir / "cad_plans.json",
        "dry_run_report": output_dir / "dry_run_report.json",
        "verification_report": output_dir / "verification_report.json",
    }
    _write_json(paths["shell_model"], shell)
    _write_json(paths["project_model"], project_model)
    _write_json(paths["circulation_candidates"], circulation_candidates)
    _write_json(paths["function_zones"], zones)
    _write_json(paths["placements"], placements)
    _write_json(paths["layout_proposal"], layout)
    _write_json(paths["design_proposal"], proposal)
    _write_json(paths["cad_plan"], cad_plans[0])
    _write_json(paths["cad_plans"], cad_plans)
    _write_json(paths["dry_run_report"], dry_run_report)
    verification_report = build_verification_report(plan_path=paths["cad_plan"])
    _write_json(paths["verification_report"], verification_report)

    metrics = {
        "circulation_candidates": len(circulation_candidates),
        "zones": len(zones),
        "placements": len(placements),
        "cad_plans": len(cad_plans),
        "failed_checks": sum(1 for check in layout["candidates"][0]["checks"] if check["status"] == "fail"),
    }
    return {
        "status": "ok",
        "artifacts": {key: str(path) for key, path in paths.items()},
        "metrics": metrics,
        "dry_run_report": dry_run_report,
        "verification_report": verification_report,
    }
