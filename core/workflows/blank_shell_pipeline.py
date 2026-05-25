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


def _find_project_root(path: Path) -> Path:
    for parent in [path.parent, *path.parents]:
        if (parent / "CORE_RESTRUCTURE_PLAN.md").exists():
            return parent
    return path.parent


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    root = _find_project_root(workflow_path.resolve())
    workflow = load_json(workflow_path)
    inputs = workflow.get("inputs", {})
    brief = load_json(root / inputs["design_brief"])
    drawing = load_json(root / inputs["drawing_model"])
    shell = load_manual_shell(root / inputs["shell_model"])
    preferences = load_json(root / inputs["preferences"]) if inputs.get("preferences") else {}
    object_types = workflow.get("object_types", ["display_unit", "counter", "shelf", "desk", "chair"])
    if not isinstance(object_types, list) or not object_types:
        object_types = ["display_unit", "counter", "shelf", "desk", "chair"]

    project_model = build_project_model(brief, drawing, shell_model=shell).project_model
    circulation_candidates = generate_circulation_candidates(project_model, preferences.get("circulation", preferences))
    circulation_for_zones = next(
        (candidate for candidate in circulation_candidates if candidate.get("strategy") == "straight_spine"),
        circulation_candidates[0],
    )
    zones = split_zones(shell, circulation_for_zones, constraints={})
    block_library = load_block_library(root / inputs["block_library"]) if inputs.get("block_library") else load_block_library()
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
