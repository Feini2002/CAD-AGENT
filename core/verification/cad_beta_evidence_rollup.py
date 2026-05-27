"""Roll up BETA-CAD-BLOCK 01–05 non-CAD evidence into one machine-readable report (BETA-CAD-BLOCK-05)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from core.path_safety import resolve_under_project_output
from core.plan_engine.validate_plan import validate_plan
from core.verification.block_alpha_beta_suite import default_suite_path as block_alpha_suite_path
from core.verification.block_alpha_beta_suite import run_block_alpha_beta_suite
from core.verification.block_attribute_probe import check_block_attribute_readback, plan_expects_attribute_readback
from core.verification.cad_capability_probe import run_cad_capability_probe
from core.verification.drawing_standard_beta_suite import default_suite_path as drawing_standard_suite_path
from core.verification.drawing_standard_beta_suite import run_drawing_standard_beta_suite
from core.verification.entity_level_evidence import entity_level_evidence_allows_probe_pass
from core.verification.evidence_contract import (
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
    GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE,
    NON_CAD_GEOMETRY_ACCURACY,
    validate_capability_probe_evidence,
)
from core.verification.evidence_trend import (
    build_evidence_trend_report,
    build_evidence_trend_snapshot,
    validate_evidence_trend_report,
)
from core.verification.evidence_vocabulary import SCREENSHOT_NOT_APPLICABLE
from core.verification.fake_cad_driver import FakeCadDriver
from core.verification.geometry_checks import check_block_reference_readback, expected_block_reference_from_plan


PARENT_PACKAGE_ID = "BETA-CAD-BLOCK"
ROLLUP_VERSION = "0.1"
CAD_BETA_EVIDENCE_TREND_FILENAME = "cad_beta_evidence_rollup_trend.json"

VERIFICATION_DOC_NAMES = (
    "beta_cad_block_01_boundaries.md",
    "beta_cad_block_02_boundaries.md",
    "beta_cad_block_03_boundaries.md",
    "beta_cad_block_04_boundaries.md",
    "beta_cad_block_05_boundaries.md",
    "beta_cad_block_acceptance.md",
    "beta_cad_block_evidence_rollup.md",
)

ALLOWED_CLAIMS = [
    "受控 insert_block_alpha 多锚点/旋转/统一缩放 CAD_PLAN 可 validate + dry-run valid（non-CAD）",
    "属性块 readback 探针：无 probe 不误报；缺 tag 时 structured deferred",
    "Capability probe（Fake driver）可输出 cad_capability_verified + entity_evidence（hatch deferred）",
    "drawing_standard_profile 可把 object_role / layer_role 解析到 CODEX_PREVIEW（preview_only）",
    "本 rollup 汇总 01–05 子包 non-CAD 证据；geometry_verified_count 保持 0",
]

FORBIDDEN_CLAIMS = [
    "不得将本 rollup 或任一 beta suite pass 等同于 geometry_verified",
    "不得声称任意公司块库、正式图层或 hatch 已在真实 CAD 全面验证",
    "不得声称 capability probe Fake driver 等于用户 AutoCAD 会话实跑",
    "不得跳过 R-BLOCK-CAD / CAD validation runner 的 created-handle readback 门槛",
]


def _subpackage(
    *,
    subpackage_id: str,
    status: str,
    evidence_type: str,
    machine_entry: str,
    summary: dict[str, Any],
    errors: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "subpackage_id": subpackage_id,
        "status": status,
        "evidence_type": evidence_type,
        "machine_entry": machine_entry,
        "summary": summary,
        "errors": errors or [],
    }


def evaluate_beta_cad_block_01(root: Path, output_root: Path | None) -> dict[str, Any]:
    suite_path = block_alpha_suite_path(root)
    case_output = output_root / "beta_cad_block_01" if output_root else None
    result = run_block_alpha_beta_suite(suite_path, output_root=case_output)
    status = str(result.get("status", "fail"))
    return _subpackage(
        subpackage_id="BETA-CAD-BLOCK-01",
        status=status,
        evidence_type="dry_run_suite",
        machine_entry=str(suite_path.relative_to(root)).replace("\\", "/"),
        summary={
            "suite_id": result.get("suite_id"),
            "case_count": result.get("summary", {}).get("total", 0),
            "passed": result.get("summary", {}).get("passed", 0),
            "evidence_state": EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        },
        errors=[] if status == "pass" else ["block_alpha_beta_suite failed"],
    )


def evaluate_beta_cad_block_02(root: Path) -> dict[str, Any]:
    probe_plan_path = root / "examples/plans/insert_block_alpha_attribute_probe.json"
    base_plan_path = root / "examples/plans/insert_block_alpha_test.json"
    errors: list[str] = []
    try:
        probe_plan = json.loads(probe_plan_path.read_text(encoding="utf-8"))
        base_plan = json.loads(base_plan_path.read_text(encoding="utf-8"))
        if validate_plan(probe_plan):
            errors.append("probe plan validation failed")
        if not plan_expects_attribute_readback(probe_plan):
            errors.append("probe plan missing attribute_readback_probe")
        expected = expected_block_reference_from_plan(probe_plan)
        entity = {"handle": "BR1", "type": "block_reference", **expected}
        missing = check_block_attribute_readback(probe_plan, entity)
        if missing.get("status") != "deferred":
            errors.append(f"expected deferred for missing tags, got {missing.get('status')}")
        base_entity = {"handle": "BR1", "type": "block_reference", **expected_block_reference_from_plan(base_plan)}
        not_run = check_block_attribute_readback(base_plan, base_entity)
        if not_run.get("status") != "not_run":
            errors.append("base plan should not_run attribute check")
        geometry = check_block_reference_readback(base_plan, base_entity)
        if not all(check.get("status") == "pass" for check in geometry):
            errors.append("base plan geometry checks failed")
    except Exception as exc:
        errors.append(str(exc))

    status = "pass" if not errors else "fail"
    return _subpackage(
        subpackage_id="BETA-CAD-BLOCK-02",
        status=status,
        evidence_type="attribute_probe_synthetic",
        machine_entry="core/verification/block_attribute_probe.py",
        summary={
            "probe_plan": str(probe_plan_path.relative_to(root)).replace("\\", "/"),
            "attribute_missing_status": "deferred",
            "geometry_verified_count": 0,
        },
        errors=errors,
    )


def evaluate_beta_cad_block_03(output_root: Path | None) -> dict[str, Any]:
    case_output = output_root / "beta_cad_block_03" if output_root else None
    report = run_cad_capability_probe(driver_factory=FakeCadDriver, output_dir=case_output)
    errors: list[str] = []
    if report.get("status") != "cad_capability_verified":
        errors.append(f"probe status {report.get('status')!r}")
    if report.get("evidence_state") != EVIDENCE_CAD_CAPABILITY_VERIFIED:
        errors.append("evidence_state mismatch")
    if report.get("geometry_accuracy") != GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE:
        errors.append("geometry_accuracy must be capability-probe scoped, not full geometry_verified")
    gate = validate_capability_probe_evidence(report)
    if gate:
        errors.append(gate)
    entity_evidence = report.get("entity_evidence", [])
    if not entity_level_evidence_allows_probe_pass(entity_evidence):
        errors.append("entity_evidence incomplete")

    status = "pass" if not errors else "fail"
    return _subpackage(
        subpackage_id="BETA-CAD-BLOCK-03",
        status=status,
        evidence_type="capability_probe_fake_driver",
        machine_entry="core/verification/cad_capability_probe.py",
        summary={
            "probe_status": report.get("status"),
            "evidence_state": report.get("evidence_state"),
            "geometry_accuracy": report.get("geometry_accuracy"),
            "entity_evidence_count": len(entity_evidence) if isinstance(entity_evidence, list) else 0,
            "hatch_deferred": any(
                entry.get("primitive") == "hatch" and entry.get("status") == "deferred"
                for entry in entity_evidence
                if isinstance(entry, dict)
            ),
            "non_cad_driver": True,
        },
        errors=errors,
    )


def evaluate_beta_cad_block_04(root: Path, output_root: Path | None) -> dict[str, Any]:
    suite_path = drawing_standard_suite_path(root)
    case_output = output_root / "beta_cad_block_04" if output_root else None
    result = run_drawing_standard_beta_suite(suite_path, output_root=case_output)
    status = str(result.get("status", "fail"))
    return _subpackage(
        subpackage_id="BETA-CAD-BLOCK-04",
        status=status,
        evidence_type="drawing_standard_suite",
        machine_entry=str(suite_path.relative_to(root)).replace("\\", "/"),
        summary={
            "suite_id": result.get("suite_id"),
            "profile_id": result.get("profile_id"),
            "case_count": result.get("summary", {}).get("total", 0),
            "passed": result.get("summary", {}).get("passed", 0),
            "evidence_state": EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
        },
        errors=[] if status == "pass" else ["drawing_standard_beta_suite failed"],
    )


def evaluate_beta_cad_block_05(root: Path) -> dict[str, Any]:
    verification_root = root / "docs" / "verification"
    missing = [name for name in VERIFICATION_DOC_NAMES if not (verification_root / name).is_file()]
    status = "pass" if not missing else "fail"
    return _subpackage(
        subpackage_id="BETA-CAD-BLOCK-05",
        status=status,
        evidence_type="documentation_bundle",
        machine_entry="docs/verification/beta_cad_block_acceptance.md",
        summary={
            "verification_docs_expected": len(VERIFICATION_DOC_NAMES),
            "verification_docs_present": len(VERIFICATION_DOC_NAMES) - len(missing),
        },
        errors=[f"missing doc: {name}" for name in missing],
    )


def run_cad_beta_evidence_rollup(
    root: Path,
    *,
    output_root: Path | None = None,
) -> dict[str, Any]:
    """Execute non-CAD beta checks for BETA-CAD-BLOCK-01..05 and write rollup JSON."""

    root = root.resolve()
    if output_root is not None:
        output_root = resolve_under_project_output(root, output_root, label="output_root")

    subpackages = [
        evaluate_beta_cad_block_01(root, output_root),
        evaluate_beta_cad_block_02(root),
        evaluate_beta_cad_block_03(output_root),
        evaluate_beta_cad_block_04(root, output_root),
        evaluate_beta_cad_block_05(root),
    ]
    passed = sum(1 for item in subpackages if item["status"] == "pass")
    failed = len(subpackages) - passed

    real_cad_reference = {
        "note": "Real CAD block alpha evidence is not re-run by this rollup.",
        "reference_paths": [
            "output/validation_runs/r-block-alpha-cad/report.json",
            "output/validation_runs/codex-second-gate-block-alpha-cad-final/report.json",
        ],
        "claim_scope": "reference_only_not_part_of_rollup_pass",
    }

    generated_at = datetime.now().isoformat(timespec="seconds")
    report: dict[str, Any] = {
        "version": ROLLUP_VERSION,
        "parent_package_id": PARENT_PACKAGE_ID,
        "generated_at": generated_at,
        "status": "pass" if failed == 0 else "fail",
        "summary": {
            "subpackage_total": len(subpackages),
            "subpackage_passed": passed,
            "subpackage_failed": failed,
        },
        "evidence_summary": {
            "geometry_verified_count": 0,
            "readback_geometry_verified_count": 0,
            "non_cad_only": True,
            "rollup_evidence_state": EVIDENCE_DRY_RUN_VALID_PLAN_ONLY
            if failed == 0
            else EVIDENCE_DEFERRED_CAD_READBACK,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        },
        "claims": {
            "allowed": list(ALLOWED_CLAIMS),
            "forbidden": list(FORBIDDEN_CLAIMS),
        },
        "real_cad_reference": real_cad_reference,
        "verification_docs": list(VERIFICATION_DOC_NAMES),
        "subpackages": subpackages,
    }

    if output_root is not None:
        output_root = Path(output_root)
        output_root.mkdir(parents=True, exist_ok=True)
        rollup_path = output_root / "cad_beta_evidence_rollup.json"
        source_path = str(rollup_path.relative_to(root)).replace("\\", "/")
        trend = build_evidence_trend_report(
            report_id="cad-beta-evidence-rollup-trend",
            generated_at=generated_at,
            snapshots=[
                build_evidence_trend_snapshot(
                    snapshot_id="beta-cad-block-05",
                    series_id="cad_beta_evidence_rollup",
                    source_kind="benchmark_suite",
                    source_path=source_path,
                    snapshot_at=generated_at,
                    evidence_state_counts={EVIDENCE_DRY_RUN_VALID_PLAN_ONLY: passed},
                    geometry_accuracy_counts={NON_CAD_GEOMETRY_ACCURACY: len(subpackages)},
                    screenshot_role_counts={SCREENSHOT_NOT_APPLICABLE: len(subpackages)},
                    metrics={
                        "subpackage_total": len(subpackages),
                        "subpackage_passed": passed,
                        "subpackage_failed": failed,
                        "geometry_verified_count": 0,
                        "readback_geometry_verified_count": 0,
                    },
                )
            ],
            status=report["status"],
            notes=[
                "BETA-CAD-BLOCK rollup is non-CAD only; it must not be counted as real CAD geometry_verified.",
                "Real CAD references in the rollup are reference_only_not_part_of_rollup_pass.",
            ],
        )
        trend_errors = validate_evidence_trend_report(trend)
        if trend_errors:
            raise ValueError(f"cad beta evidence trend validation failed: {trend_errors}")
        trend_dir = output_root / "evidence_trend"
        trend_dir.mkdir(parents=True, exist_ok=True)
        trend_path = trend_dir / CAD_BETA_EVIDENCE_TREND_FILENAME
        trend_path.write_text(json.dumps(trend, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report["trend_output_path"] = str(trend_path.relative_to(root)).replace("\\", "/")
        rollup_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return report
