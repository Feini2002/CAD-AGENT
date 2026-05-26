"""Block alpha beta suite runner (BETA-CAD-BLOCK-01)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.path_safety import resolve_under_project_output, validate_safe_path_segment
from core.plan_engine.block_alpha_plan import CONTROLLED_BLOCK_ID, CONTROLLED_BLOCK_NAME, PREVIEW_LAYER
from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import validate_plan
from core.verification.evidence_contract import (
    EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
    NON_CAD_GEOMETRY_ACCURACY,
)


DEFAULT_SUITE_REL = "examples/plans/block_alpha_beta_suite.json"


def default_suite_path(root: Path) -> Path:
    return root / DEFAULT_SUITE_REL


def load_block_alpha_beta_suite(path: Path) -> dict[str, Any]:
    suite = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(suite, dict):
        raise ValueError(f"{path} must be a JSON object")
    cases = suite.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"{path} must contain a non-empty cases array")
    return suite


def materialize_block_alpha_plan(case: dict[str, Any]) -> dict[str, Any]:
    placement = case.get("placement", {})
    if not isinstance(placement, dict):
        raise ValueError(f"case {case.get('case_id')}: placement must be an object")
    base_point = placement.get("base_point")
    if not isinstance(base_point, list):
        raise ValueError(f"case {case.get('case_id')}: placement.base_point is required")
    rotation = placement.get("rotation", 0)
    scale = placement.get("scale", [1, 1, 1])
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
            "rotation": rotation,
            "scale": scale,
        },
        "drawing": {"layer": PREVIEW_LAYER},
        "confidence": 1.0,
        "needs_confirmation": False,
    }


def run_block_alpha_beta_case(*, case: dict[str, Any]) -> dict[str, Any]:
    case_id = str(case.get("case_id", "unknown"))
    validate_safe_path_segment(case_id, label="case_id")
    plan = materialize_block_alpha_plan(case)
    validation_errors = validate_plan(plan)
    dry_run = create_dry_run_report(plan) if not validation_errors else None
    expected = case.get("expected", {})
    if not isinstance(expected, dict):
        expected = {}

    actual: dict[str, Any] = {
        "case_id": case_id,
        "validation_errors": validation_errors,
        "dry_run_status": dry_run.get("status") if isinstance(dry_run, dict) else "skipped",
        "evidence_state": dry_run.get("evidence_state") if isinstance(dry_run, dict) else "",
        "geometry_accuracy": dry_run.get("geometry_accuracy") if isinstance(dry_run, dict) else "",
        "rotation": plan["placement"].get("rotation"),
        "scale": plan["placement"].get("scale"),
        "base_point": plan["placement"].get("base_point"),
    }
    if isinstance(dry_run, dict) and dry_run.get("bbox"):
        actual["bbox"] = dry_run["bbox"]

    errors: list[str] = []
    if validation_errors:
        errors.append(f"validation failed: {validation_errors}")
    if dry_run is None or dry_run.get("status") != "valid":
        errors.append(f"dry_run_status expected valid, got {actual['dry_run_status']!r}")
    if expected.get("dry_run_status") == "valid" and actual["dry_run_status"] != "valid":
        errors.append("dry_run_status mismatch")
    if expected.get("evidence_state") and actual["evidence_state"] != expected["evidence_state"]:
        errors.append(
            f"evidence_state expected {expected['evidence_state']!r}, got {actual['evidence_state']!r}"
        )
    if "rotation" in expected and actual["rotation"] != expected["rotation"]:
        errors.append(f"rotation expected {expected['rotation']}, got {actual['rotation']}")
    if "scale_uniform" in expected:
        scale = actual.get("scale", [])
        if not scale or float(scale[0]) != float(expected["scale_uniform"]):
            errors.append(f"scale_uniform expected {expected['scale_uniform']}, got {scale}")

    status = "pass" if not errors else "fail"
    return {
        "case_id": case_id,
        "status": status,
        "errors": errors,
        "expected": expected,
        "actual": actual,
        "plan": plan,
        "dry_run": dry_run,
    }


def _project_root_from_suite(suite_path: Path) -> Path:
    resolved = suite_path.resolve()
    for parent in [resolved.parent, *resolved.parents]:
        if (parent / "examples").is_dir() and (parent / "core").is_dir():
            return parent
    raise ValueError(f"could not locate project root from suite path {suite_path}")


def run_block_alpha_beta_suite(
    suite_path: Path,
    *,
    output_root: Path | None = None,
) -> dict[str, Any]:
    project_root = _project_root_from_suite(suite_path)
    if output_root is not None:
        output_root = resolve_under_project_output(project_root, output_root, label="output_root")
    suite = load_block_alpha_beta_suite(suite_path)
    case_results = [run_block_alpha_beta_case(case=case) for case in suite["cases"]]
    passed = sum(1 for case in case_results if case["status"] == "pass")
    failed = len(case_results) - passed

    summary = {
        "version": "0.1",
        "suite_id": str(suite.get("suite_id", "")),
        "status": "pass" if failed == 0 else "fail",
        "summary": {"total": len(case_results), "passed": passed, "failed": failed},
        "evidence_summary": {
            "case_count": len(case_results),
            "dry_run_valid_count": passed,
            "geometry_verified_count": 0,
            "non_cad_only": True,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "evidence_state": EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
        },
        "cases": case_results,
    }

    if output_root is not None:
        output_root = Path(output_root)
        output_root.mkdir(parents=True, exist_ok=True)
        summary_path = output_root / "block_alpha_beta_summary.json"
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        for case in case_results:
            case_dir = output_root / str(case["case_id"])
            case_dir.mkdir(parents=True, exist_ok=True)
            (case_dir / "cad_plan.json").write_text(
                json.dumps(case["plan"], indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            if case.get("dry_run"):
                (case_dir / "dry_run_report.json").write_text(
                    json.dumps(case["dry_run"], indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )

    return summary
