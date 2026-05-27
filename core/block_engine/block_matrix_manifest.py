"""RBLOCK-04: block insert matrix manifest (anchor / rotation / scale / attribute)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.path_safety import find_project_root, resolve_under_project_output
from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import validate_plan
from core.verification.block_alpha_beta_suite import (
    load_block_alpha_beta_suite,
    run_block_alpha_beta_case,
    run_block_alpha_beta_suite,
)
from core.verification.evidence_contract import (
    EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)

DEFAULT_MANIFEST_REL = "examples/capability_proof/block_insert_matrix_manifest.json"
BLOCK_MATRIX_DIMENSIONS = ("anchor", "rotation", "scale", "attribute")

RBLOCK_04_REGISTRY_CAPABILITY_IDS = (
    "block.insert_block_alpha.anchor",
    "block.insert_block_alpha.rotation",
    "block.insert_block_alpha.scale",
    "block.insert_block_alpha.attributes",
)


def default_manifest_path(root: Path) -> Path:
    return root / DEFAULT_MANIFEST_REL


def load_block_insert_matrix_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError(f"{path} must be a JSON object")
    dimensions = manifest.get("dimensions")
    if not isinstance(dimensions, dict):
        raise ValueError(f"{path} must define dimensions object")
    for key in BLOCK_MATRIX_DIMENSIONS:
        if key not in dimensions:
            raise ValueError(f"{path} missing dimension {key!r}")
    return manifest


def _beta_cases_by_id(suite: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(case["case_id"]): case for case in suite.get("cases", []) if isinstance(case, dict)}


def run_attribute_probe_case(*, project_root: Path, case_id: str) -> dict[str, Any]:
    plan_path = project_root / "examples/plans/insert_block_alpha_attribute_probe.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    errors = validate_plan(plan)
    dry_run = create_dry_run_report(plan) if not errors else None
    status = "pass" if not errors and dry_run and dry_run.get("status") == "valid" else "fail"
    case_errors: list[str] = []
    if errors:
        case_errors.append("validation: " + "; ".join(errors[:2]))
    if dry_run is None or dry_run.get("status") != "valid":
        case_errors.append(f"dry_run expected valid, got {(dry_run or {}).get('status')!r}")
    return {
        "case_id": case_id,
        "dimension": "attribute",
        "status": status,
        "errors": case_errors,
        "plan_path": str(plan_path.relative_to(project_root)).replace("\\", "/"),
        "dry_run_status": dry_run.get("status") if isinstance(dry_run, dict) else None,
    }


def run_block_insert_matrix_manifest(
    manifest_path: Path,
    *,
    output_root: Path | None = None,
) -> dict[str, Any]:
    project_root = find_project_root(manifest_path)
    if output_root is not None:
        output_root = resolve_under_project_output(project_root, output_root, label="output_root")
    manifest = load_block_insert_matrix_manifest(manifest_path)
    suite_path = project_root / str(manifest["beta_suite_path"])
    suite = load_block_alpha_beta_suite(suite_path)
    beta_index = _beta_cases_by_id(suite)

    dimension_results: dict[str, Any] = {}
    case_results: list[dict[str, Any]] = []

    for dimension in BLOCK_MATRIX_DIMENSIONS:
        spec = manifest["dimensions"][dimension]
        dim_cases: list[dict[str, Any]] = []
        if dimension == "attribute":
            case_id = str(spec.get("plan_case_id", "attribute_probe_codex"))
            result = run_attribute_probe_case(project_root=project_root, case_id=case_id)
            dim_cases.append(result)
            case_results.append(result)
        else:
            for case_id in spec.get("beta_case_ids", []):
                beta_case = beta_index.get(str(case_id))
                if beta_case is None:
                    dim_cases.append(
                        {
                            "case_id": case_id,
                            "dimension": dimension,
                            "status": "fail",
                            "errors": [f"missing beta case {case_id!r}"],
                        }
                    )
                    continue
                run = run_block_alpha_beta_case(case=beta_case)
                run["dimension"] = dimension
                run["registry_capability_id"] = spec.get("registry_capability_id")
                dim_cases.append(run)
                case_results.append(run)

        passed = sum(1 for item in dim_cases if item.get("status") == "pass")
        dimension_results[dimension] = {
            "registry_capability_id": spec.get("registry_capability_id"),
            "case_count": len(dim_cases),
            "passed": passed,
            "failed": len(dim_cases) - passed,
            "cases": dim_cases,
        }

    combined_id = str(manifest.get("combined_case", {}).get("beta_case_id", ""))
    combined_result = None
    if combined_id and combined_id in beta_index:
        combined_result = run_block_alpha_beta_case(case=beta_index[combined_id])
        combined_result["dimension"] = "combined"
        case_results.append(combined_result)

    total = len(case_results)
    passed_total = sum(1 for item in case_results if item.get("status") == "pass")
    result: dict[str, Any] = {
        "manifest_id": manifest.get("manifest_id"),
        "status": "pass" if passed_total == total else "fail",
        "summary": {"total": total, "passed": passed_total, "failed": total - passed_total},
        "dimension_summary": {
            key: {
                "passed": value["passed"],
                "failed": value["failed"],
                "registry_capability_id": value.get("registry_capability_id"),
            }
            for key, value in dimension_results.items()
        },
        "evidence_summary": {
            "geometry_verified_count": 0,
            "non_cad_only": True,
            "evidence_state": EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        },
        "dimensions": dimension_results,
        "combined_case": combined_result,
    }

    if output_root is not None:
        output_root.mkdir(parents=True, exist_ok=True)
        (output_root / "block_insert_matrix_summary.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        for dim, payload in dimension_results.items():
            (output_root / f"dimension_{dim}.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    return result


def assert_block_matrix_manifest_contract(*, project_root: Path) -> None:
    """Raise when RBLOCK-04 matrix manifest bindings are missing or inconsistent."""

    root = project_root.resolve()
    from core.block_engine.block_alpha_boundary import assert_block_alpha_boundary_contract

    assert_block_alpha_boundary_contract(project_root=root)

    manifest_path = default_manifest_path(root)
    if not manifest_path.is_file():
        raise AssertionError(f"missing matrix manifest: {DEFAULT_MANIFEST_REL}")

    manifest = load_block_insert_matrix_manifest(manifest_path)
    if manifest.get("manifest_id") != "block-insert-matrix-01":
        raise AssertionError(f"unexpected manifest_id: {manifest.get('manifest_id')!r}")

    from core.verification.capability_registry import index_capability_rows, load_capability_registry

    registry = load_capability_registry(
        root / "examples/capability_proof/cad_capability_registry.json",
        project_root=root,
    )
    index = index_capability_rows(registry)
    for capability_id in RBLOCK_04_REGISTRY_CAPABILITY_IDS:
        if capability_id not in index:
            raise AssertionError(f"missing registry row: {capability_id}")

    suite = load_block_alpha_beta_suite(root / str(manifest["beta_suite_path"]))
    beta_ids = {str(c["case_id"]) for c in suite.get("cases", [])}
    for dimension in ("anchor", "rotation", "scale"):
        spec = manifest["dimensions"][dimension]
        for case_id in spec.get("beta_case_ids", []):
            if str(case_id) not in beta_ids:
                raise AssertionError(f"beta suite missing case {case_id!r} for dimension {dimension}")

    attr_plan = root / str(manifest["attribute_probe_plan_path"])
    if not attr_plan.is_file():
        raise AssertionError(f"missing attribute probe plan: {manifest['attribute_probe_plan_path']}")

    smoke = run_block_insert_matrix_manifest(manifest_path, output_root=None)
    if smoke.get("status") != "pass":
        raise AssertionError(f"block insert matrix smoke must pass: {smoke.get('summary')}")


def block_matrix_manifest_status_summary(*, project_root: Path) -> dict[str, Any]:
    manifest = load_block_insert_matrix_manifest(default_manifest_path(project_root))
    return {
        "package_id": "RBLOCK-04-BLOCK-MATRIX-MANIFEST",
        "manifest_id": manifest.get("manifest_id"),
        "dimension_count": len(BLOCK_MATRIX_DIMENSIONS),
        "registry_binding_count": len(RBLOCK_04_REGISTRY_CAPABILITY_IDS),
    }
