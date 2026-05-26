"""Drawing standard profile beta suite (BETA-CAD-BLOCK-04)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.drawing_standard.drawing_standard_profile import (
    DEFAULT_DRAWING_STANDARD_PROFILE_ID,
    apply_drawing_standard_to_plan,
    load_drawing_standard_profile,
    resolve_layer_role,
    resolve_object_role,
    resolve_primitive_style,
    semantic_layer_name,
)
from core.path_safety import find_project_root, resolve_under_project_output, validate_safe_path_segment
from core.plan_engine.block_alpha_plan import CONTROLLED_BLOCK_ID, CONTROLLED_BLOCK_NAME
from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import validate_plan
from core.verification.evidence_contract import EVIDENCE_DRY_RUN_VALID_PLAN_ONLY


DEFAULT_SUITE_REL = "examples/plans/drawing_standard_beta_suite.json"


def default_suite_path(root: Path) -> Path:
    return root / DEFAULT_SUITE_REL


def load_drawing_standard_beta_suite(path: Path) -> dict[str, Any]:
    suite = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(suite, dict):
        raise ValueError(f"{path} must be a JSON object")
    cases = suite.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"{path} must contain a non-empty cases array")
    return suite


def _materialize_block_plan(case: dict[str, Any]) -> dict[str, Any]:
    placement = case.get("placement", {})
    if not isinstance(placement, dict):
        raise ValueError("placement must be an object")
    base_point = placement.get("base_point", [0, 0, 0])
    return {
        "version": "0.1",
        "domain": "generic",
        "intent": "insert_block_alpha",
        "object": {
            "type": "block_reference",
            "name": "Controlled Test Block",
            "block_id": CONTROLLED_BLOCK_ID,
            "cad_identity": {"block_name": CONTROLLED_BLOCK_NAME},
        },
        "placement": {
            "mode": "absolute",
            "base_point": base_point,
            "rotation": placement.get("rotation", 0),
            "scale": placement.get("scale", [1, 1, 1]),
        },
        "drawing": {},
        "confidence": 1.0,
        "needs_confirmation": False,
        "drawing_standard_profile_id": DEFAULT_DRAWING_STANDARD_PROFILE_ID,
    }


def run_drawing_standard_beta_case(*, case: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    case_id = str(case.get("case_id", "unknown"))
    validate_safe_path_segment(case_id, label="case_id")
    expected = case.get("expected", {})
    if not isinstance(expected, dict):
        expected = {}

    actual: dict[str, Any] = {"case_id": case_id}
    errors: list[str] = []

    if case.get("plan_kind") == "insert_block_alpha":
        plan = _materialize_block_plan(case)
        object_role = str(case.get("object_role", "block_insert"))
        apply_drawing_standard_to_plan(plan, profile=profile, object_role=object_role)
        validation_errors = validate_plan(plan)
        dry_run = create_dry_run_report(plan) if not validation_errors else None
        actual["validation_errors"] = validation_errors
        actual["resolved_layer"] = plan["drawing"].get("layer")
        actual["layer_role"] = plan["drawing"].get("layer_role")
        actual["semantic_layer"] = plan["drawing"].get("semantic_layer")
        actual["dry_run_status"] = dry_run.get("status") if isinstance(dry_run, dict) else "skipped"
        if validation_errors:
            errors.append(f"validation: {validation_errors}")
        if actual["dry_run_status"] != expected.get("dry_run_status", "valid"):
            errors.append(f"dry_run_status {actual['dry_run_status']!r}")
    elif "primitive" in case:
        resolution = resolve_primitive_style(
            profile,
            primitive=str(case["primitive"]),
            layer_role=str(case.get("layer_role", "preview")),
        )
        actual.update(resolution)
    elif "object_role" in case:
        resolution = resolve_object_role(profile, str(case["object_role"]))
        actual.update(resolution)
    elif "layer_role" in case:
        layer_role = str(case["layer_role"])
        actual["layer_role"] = layer_role
        actual["semantic_layer"] = semantic_layer_name(profile, layer_role)
        actual["resolved_layer"] = resolve_layer_role(profile, layer_role, for_cad_execution=True)
    else:
        errors.append("case must specify object_role, layer_role, primitive, or plan_kind")

    for key, value in expected.items():
        if actual.get(key) != value:
            errors.append(f"{key} expected {value!r}, got {actual.get(key)!r}")

    return {
        "case_id": case_id,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "expected": expected,
        "actual": actual,
    }


def run_drawing_standard_beta_suite(
    suite_path: Path,
    *,
    output_root: Path | None = None,
) -> dict[str, Any]:
    project_root = find_project_root(suite_path)
    if output_root is not None:
        output_root = resolve_under_project_output(project_root, output_root, label="output_root")
    suite = load_drawing_standard_beta_suite(suite_path)
    profile_id = str(suite.get("profile_id", DEFAULT_DRAWING_STANDARD_PROFILE_ID))
    profile = load_drawing_standard_profile(profile_id)
    case_results = [
        run_drawing_standard_beta_case(case=case, profile=profile) for case in suite["cases"]
    ]
    passed = sum(1 for case in case_results if case["status"] == "pass")
    failed = len(case_results) - passed
    result: dict[str, Any] = {
        "suite_id": suite.get("suite_id", "drawing-standard-beta"),
        "profile_id": profile_id,
        "status": "pass" if failed == 0 else "fail",
        "summary": {"total": len(case_results), "passed": passed, "failed": failed},
        "evidence_summary": {
            "dry_run_valid_count": sum(
                1
                for case in case_results
                if case.get("actual", {}).get("dry_run_status") == "valid"
            ),
            "geometry_verified_count": 0,
            "non_cad_only": True,
            "evidence_state": EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
        },
        "cases": case_results,
    }
    if output_root is not None:
        output_root.mkdir(parents=True, exist_ok=True)
        for case in case_results:
            case_dir = output_root / str(case["case_id"])
            case_dir.mkdir(parents=True, exist_ok=True)
            (case_dir / "case_result.json").write_text(
                json.dumps(case, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        (output_root / "drawing_standard_beta_summary.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return result
