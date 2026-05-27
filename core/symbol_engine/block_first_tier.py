"""SYMBOL-09: block-first tier smoke runner and deferred boundaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.path_safety import find_project_root, resolve_under_project_output, validate_safe_path_segment
from core.symbol_engine.fallback_policy import (
    detect_silent_degradation,
    resolve_symbol_render_resolution,
)
from core.verification.evidence_contract import (
    EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)

DEFAULT_MANIFEST_REL = "examples/capability_proof/symbol_block_first_tier_manifest.json"


def default_manifest_path(root: Path) -> Path:
    return root / DEFAULT_MANIFEST_REL


def load_block_first_tier_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError(f"{path} must be a JSON object")
    cases = manifest.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"{path} must contain a non-empty cases array")
    return manifest


def _load_library(root: Path, manifest: dict[str, Any], case: dict[str, Any]) -> dict[str, Any] | None:
    if case.get("use_library") is False:
        return None
    overrides = case.get("block_library_overrides")
    if isinstance(overrides, dict):
        base = {"version": "0.2", "library_id": "test-block-first", "units": "mm", "blocks": []}
        base.update({k: v for k, v in overrides.items() if k != "blocks"})
        base["blocks"] = list(overrides.get("blocks", []))
        return base
    library_path = root / str(manifest.get("library_path", ""))
    if not library_path.is_file():
        raise FileNotFoundError(f"block library not found: {library_path}")
    return json.loads(library_path.read_text(encoding="utf-8"))


def _load_object_spec(root: Path, case: dict[str, Any]) -> dict[str, Any]:
    spec_path = case.get("object_spec_path")
    if not spec_path:
        raise ValueError(f"case {case.get('case_id')}: object_spec_path required")
    spec = json.loads((root / str(spec_path)).read_text(encoding="utf-8"))
    overrides = case.get("object_spec_overrides")
    if isinstance(overrides, dict):
        spec = {**spec, **overrides}
    return spec


def run_block_first_tier_case(
    *,
    case: dict[str, Any],
    manifest: dict[str, Any],
    project_root: Path,
) -> dict[str, Any]:
    case_id = str(case.get("case_id", "unknown"))
    validate_safe_path_segment(case_id, label="case_id")
    spec = _load_object_spec(project_root, case)
    library = _load_library(project_root, manifest, case)
    report = resolve_symbol_render_resolution(spec, block_library=library, base_point=[1000.0, 1000.0, 0.0])

    expected = case.get("expected", {})
    if not isinstance(expected, dict):
        expected = {}

    errors: list[str] = []
    for key in ("selected_render_path", "selected_cad_intent", "silent_degradation"):
        if key in expected and report.get(key) != expected[key]:
            errors.append(f"{key} expected {expected[key]!r}, got {report.get(key)!r}")

    block_tier = next(
        (item for item in report.get("tier_assessments", []) if item.get("tier") == "block"),
        {},
    )
    if "block_tier_available" in expected:
        actual_available = bool(block_tier.get("available"))
        if actual_available != bool(expected["block_tier_available"]):
            errors.append(
                f"block_tier_available expected {expected['block_tier_available']!r}, got {actual_available!r}"
            )

    silent_errors = detect_silent_degradation(report)
    if silent_errors:
        errors.extend(silent_errors)

    plan = report.get("cad_plan")
    dry_run_status = None
    if plan is not None:
        from core.plan_engine.dry_run_report import create_dry_run_report
        from core.plan_engine.validate_plan import validate_plan

        validation_errors = validate_plan(plan)
        if validation_errors:
            errors.append("cad_plan validation failed: " + "; ".join(validation_errors[:2]))
        else:
            dry_run_status = create_dry_run_report(plan).get("status")

    return {
        "case_id": case_id,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "expected": expected,
        "selected_render_path": report.get("selected_render_path"),
        "selected_cad_intent": report.get("selected_cad_intent"),
        "block_tier_available": block_tier.get("available"),
        "block_tier_reason": block_tier.get("reason"),
        "dry_run_status": dry_run_status,
        "silent_degradation": report.get("silent_degradation"),
        "report": {
            "selected_render_path": report.get("selected_render_path"),
            "selected_evidence_state": report.get("selected_evidence_state"),
            "declared_fallback_mode": report.get("declared_fallback_mode"),
            "tier_assessments": report.get("tier_assessments"),
        },
    }


def run_block_first_tier_smoke(
    manifest_path: Path,
    *,
    output_root: Path | None = None,
) -> dict[str, Any]:
    project_root = find_project_root(manifest_path)
    if output_root is not None:
        output_root = resolve_under_project_output(project_root, output_root, label="output_root")
    manifest = load_block_first_tier_manifest(manifest_path)
    case_results = [
        run_block_first_tier_case(case=case, manifest=manifest, project_root=project_root)
        for case in manifest["cases"]
    ]
    passed = sum(1 for case in case_results if case["status"] == "pass")
    failed = len(case_results) - passed
    result: dict[str, Any] = {
        "manifest_id": manifest.get("manifest_id", "symbol-block-first-tier"),
        "status": "pass" if failed == 0 else "fail",
        "summary": {"total": len(case_results), "passed": passed, "failed": failed},
        "evidence_summary": {
            "block_first_count": sum(
                1 for case in case_results if case.get("selected_render_path") == "block"
            ),
            "glyph_fallback_count": sum(
                1 for case in case_results if case.get("selected_render_path") == "symbol_glyph"
            ),
            "geometry_verified_count": 0,
            "non_cad_only": True,
            "evidence_state": EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
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
        (output_root / "block_first_tier_summary.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return result
