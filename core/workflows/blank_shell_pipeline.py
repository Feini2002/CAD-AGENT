"""Blank-shell layout pipeline from SHELL_MODEL to non-CAD verification artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.block_engine.block_library import load_block_library
from core.drawing_analysis.shell_loader import load_manual_shell
from core.layout_engine.path_generation import generate_circulation_candidates
from core.object_engine.parametric_objects import create_object_spec
from core.path_safety import (
    is_relative_to,
    resolve_under_project_output,
    resolve_under_project_root,
)
from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.model_to_plan import model_to_plans
from core.project_model.project_builder import build_project_model
from core.proposal_engine.design_proposal import create_design_proposal
from core.schemas.validator import load_json
from core.layout_engine.office_layout_failure import evaluate_blank_shell_layout_expectation
from core.verification.verification_report import build_verification_report, summarize_verification_reports
from core.workflows.blank_shell_candidates import build_blank_shell_candidate_sets


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _find_project_root(path: Path) -> Path:
    for parent in [path.parent, *path.parents]:
        if (parent / "CORE_RESTRUCTURE_PLAN.md").exists():
            return parent
    return PROJECT_ROOT


def _resolve_under_root(root: Path, value: str, label: str) -> Path:
    return resolve_under_project_root(root, Path(value), label=label)


def _resolve_output_dir(root: Path, output_dir: Path) -> Path:
    return resolve_under_project_output(root, output_dir, label="output_dir")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _summarize_dry_run_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for report in reports:
        status = str(report.get("status", "unknown"))
        status_counts[status] = status_counts.get(status, 0) + 1
    valid_count = status_counts.get("valid", 0)
    return {
        "version": "0.1",
        "status": "valid" if reports and valid_count == len(reports) else "invalid",
        "plan_count": len(reports),
        "valid_count": valid_count,
        "invalid_count": len(reports) - valid_count,
        "status_counts": status_counts,
    }


def _summarize_plan_verification_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    summary = summarize_verification_reports(reports)
    status_counts = summary["status_counts"]
    if summary["all_geometry_verified"]:
        status = "geometry_verified"
    elif reports and status_counts.get("unverified", 0) == len(reports):
        status = "unverified"
    elif status_counts.get("failed", 0) > 0:
        status = "failed"
    else:
        status = "mixed"
    return {**summary, "status": status}


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


def run_blank_shell_pipeline(workflow_path: Path, *, output_dir: Path) -> dict[str, Any]:
    workflow_path = workflow_path.resolve()
    root = _find_project_root(workflow_path)
    try:
        output_dir = _resolve_output_dir(root, output_dir)
    except ValueError as exc:
        return {"status": "invalid", "errors": [str(exc)], "artifacts": {}, "metrics": {}}
    if not is_relative_to(workflow_path, root.resolve()):
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
    try:
        block_library = load_block_library(resolved_inputs["block_library"]) if inputs.get("block_library") else load_block_library()
    except (OSError, json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
        return {"status": "invalid", "errors": [f"block library is invalid: {type(exc).__name__}: {exc}"], "artifacts": {}, "metrics": {}}
    candidate_sets, circulation_for_zones, zones, target_zone, placements = build_blank_shell_candidate_sets(
        shell=shell,
        circulation_candidates=circulation_candidates,
        object_types=[str(item) for item in object_types],
        block_library=block_library,
        placement_preferences=preferences.get("placement", {}),
        scene_preferences=preferences,
        constraints={},
    )
    layout_failure = evaluate_blank_shell_layout_expectation(workflow, placements=placements)
    if layout_failure is not None:
        return {
            "status": layout_failure["status"],
            "errors": layout_failure["blocked_reasons"],
            "artifacts": {},
            "metrics": {
                "failure_category": layout_failure["failure_category"],
                "blocked_reasons": layout_failure["blocked_reasons"],
                "placements": len(placements),
                "shell_id": str(shell.get("shell_id", "")),
                "fixed_obstacle_count": len(shell.get("fixed_obstacles", [])),
                "no_place_zone_count": len(shell.get("no_place_zones", [])),
                "circulation_candidates": len(circulation_candidates),
            },
        }

    object_specs = [_object_spec_from_placement(placement) for placement in placements]
    layout = _layout_from_placements(project_model=project_model, object_specs=object_specs, placements=placements)
    proposal = create_design_proposal(
        brief=brief,
        project_model=project_model,
        object_spec=object_specs[0],
        layout_proposal=layout,
        candidate_sets=candidate_sets,
        object_types=[str(item) for item in object_types],
        preferences=preferences,
    )
    proposal_summary = proposal.get("proposal_comparison_summary")
    plan_result = model_to_plans(
        object_specs=object_specs,
        layout_proposal=layout,
        design_proposal=proposal,
        confirmed=not proposal.get("needs_confirmation", False),
    )
    if plan_result["status"] != "ok":
        confirmation_only = bool(proposal.get("needs_confirmation")) and plan_result.get("errors") == [
            "DESIGN_PROPOSAL needs confirmation before CAD_PLAN generation."
        ]
        if confirmation_only:
            pre_paths = {
                "shell_model": output_dir / "shell_model.json",
                "project_model": output_dir / "project_model.json",
                "circulation_candidates": output_dir / "circulation_candidates.json",
                "candidate_sets": output_dir / "candidate_sets.json",
                "function_zones": output_dir / "function_zones.json",
                "placements": output_dir / "placements.json",
                "layout_proposal": output_dir / "layout_proposal.json",
                "design_proposal": output_dir / "design_proposal.json",
                "proposal_comparison_summary": output_dir / "proposal_comparison_summary.json",
            }
            _write_json(pre_paths["shell_model"], shell)
            _write_json(pre_paths["project_model"], project_model)
            _write_json(pre_paths["circulation_candidates"], circulation_candidates)
            _write_json(pre_paths["candidate_sets"], candidate_sets)
            _write_json(pre_paths["function_zones"], zones)
            _write_json(pre_paths["placements"], placements)
            _write_json(pre_paths["layout_proposal"], layout)
            _write_json(pre_paths["design_proposal"], proposal)
            pre_artifacts = {key: str(path) for key, path in pre_paths.items() if key != "proposal_comparison_summary"}
            if isinstance(proposal_summary, dict):
                _write_json(pre_paths["proposal_comparison_summary"], proposal_summary)
                pre_artifacts["proposal_comparison_summary"] = str(pre_paths["proposal_comparison_summary"])
            pre_metrics: dict[str, Any] = {
                "circulation_candidates": len(circulation_candidates),
                "placements": len(placements),
                "shell_id": str(shell.get("shell_id", "")),
                "needs_confirmation": True,
            }
            return {
                "status": "confirmation_pending",
                "confirmation_gate": {
                    "cad_plan_generation": "blocked",
                    "needs_confirmation": True,
                },
                "artifacts": pre_artifacts,
                "metrics": pre_metrics,
            }
        return {"status": "blocked", "errors": plan_result["errors"], "artifacts": {}, "metrics": {}}
    cad_plans = [item["cad_plan"] for item in plan_result["plans"]]
    dry_run_reports = [create_dry_run_report(cad_plan) for cad_plan in cad_plans]
    dry_run_report = dry_run_reports[0]
    dry_run_summary = _summarize_dry_run_reports(dry_run_reports)

    paths = {
        "shell_model": output_dir / "shell_model.json",
        "project_model": output_dir / "project_model.json",
        "circulation_candidates": output_dir / "circulation_candidates.json",
        "candidate_sets": output_dir / "candidate_sets.json",
        "function_zones": output_dir / "function_zones.json",
        "placements": output_dir / "placements.json",
        "layout_proposal": output_dir / "layout_proposal.json",
        "design_proposal": output_dir / "design_proposal.json",
        "proposal_comparison_summary": output_dir / "proposal_comparison_summary.json",
        "cad_plan": output_dir / "cad_plan.json",
        "cad_plans": output_dir / "cad_plans.json",
        "dry_run_report": output_dir / "dry_run_report.json",
        "dry_run_reports": output_dir / "dry_run_reports.json",
        "verification_report": output_dir / "verification_report.json",
        "verification_reports": output_dir / "verification_reports.json",
    }
    cad_plan_paths = [output_dir / "cad_plan_items" / f"cad_plan_{index + 1:03d}.json" for index in range(len(cad_plans))]
    _write_json(paths["shell_model"], shell)
    _write_json(paths["project_model"], project_model)
    _write_json(paths["circulation_candidates"], circulation_candidates)
    _write_json(paths["candidate_sets"], candidate_sets)
    _write_json(paths["function_zones"], zones)
    _write_json(paths["placements"], placements)
    _write_json(paths["layout_proposal"], layout)
    _write_json(paths["design_proposal"], proposal)
    if isinstance(proposal_summary, dict):
        _write_json(paths["proposal_comparison_summary"], proposal_summary)
    _write_json(paths["cad_plan"], cad_plans[0])
    _write_json(paths["cad_plans"], cad_plans)
    for plan_path, cad_plan in zip(cad_plan_paths, cad_plans):
        _write_json(plan_path, cad_plan)
    _write_json(paths["dry_run_report"], dry_run_report)
    _write_json(paths["dry_run_reports"], dry_run_reports)
    verification_reports = [build_verification_report(plan_path=plan_path) for plan_path in cad_plan_paths]
    verification_report = verification_reports[0]
    verification_summary = _summarize_plan_verification_reports(verification_reports)
    _write_json(paths["verification_report"], verification_report)
    _write_json(paths["verification_reports"], verification_reports)

    metrics: dict[str, Any] = {
        "circulation_candidates": len(circulation_candidates),
        "zone_placement_candidates": candidate_sets["counts"]["zone_placement_candidates"],
        "candidate_sets": candidate_sets["counts"],
        "zones": len(zones),
        "placements": len(placements),
        "selected_zone_id": str(target_zone.get("zone_id", "")),
        "selected_circulation_strategy": str(circulation_for_zones.get("strategy", "")),
        "preferences_scenario": str(preferences.get("scenario", "")),
        "preferences_path": str(inputs.get("preferences", "")),
        "object_types": sorted({str(placement.get("object_type")) for placement in placements if placement.get("object_type")}),
        "cad_plans": len(cad_plans),
        "failed_checks": sum(1 for check in layout["candidates"][0]["checks"] if check["status"] == "fail"),
        "no_place_zone_count": len(shell.get("no_place_zones", [])),
        "fixed_obstacle_count": len(shell.get("fixed_obstacles", [])),
        "shell_id": str(shell.get("shell_id", "")),
    }
    comparison_detail = proposal.get("comparison_detail")
    if isinstance(comparison_detail, dict):
        comparison_metrics = comparison_detail.get("metrics", {})
        continuity = comparison_detail.get("circulation_continuity", {})
        metrics.update(
            {
                "has_comparison_detail": True,
                "circulation_branch_count": int(comparison_metrics.get("circulation_branch_count", 0)),
                "object_coverage_rate": float(comparison_metrics.get("object_coverage_rate", 0)),
                "selected_placement_failed_count": int(comparison_metrics.get("selected_placement_failed_count", 0)),
                "failed_reason_distribution": comparison_metrics.get("failed_reason_distribution", {}),
                "selected_failed_reason_distribution": comparison_metrics.get("selected_failed_reason_distribution", {}),
                "circulation_continuity": str(continuity.get("continuity", "")),
            }
        )
    else:
        metrics["has_comparison_detail"] = False
    if isinstance(proposal_summary, dict):
        from core.proposal_engine.comparison_summary import flatten_proposal_comparison_summary_metrics

        metrics.update(flatten_proposal_comparison_summary_metrics(proposal_summary))
    else:
        metrics["has_proposal_comparison_summary"] = False
    return {
        "status": "ok",
        "artifacts": {key: str(path) for key, path in paths.items()},
        "metrics": metrics,
        "dry_run_report": dry_run_report,
        "dry_run_reports": dry_run_reports,
        "dry_run_summary": dry_run_summary,
        "verification_report": verification_report,
        "verification_reports": verification_reports,
        "verification_summary": verification_summary,
    }
