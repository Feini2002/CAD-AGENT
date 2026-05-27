"""RBLOCK-06: block attribute / tag readback probe boundary (BETA-CAD-BLOCK-02 rollup)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.plan_engine.validate_plan import validate_plan
from core.verification.block_attribute_probe import (
    FAILURE_ATTRIBUTE_UNVERIFIED,
    check_block_attribute_readback,
    merge_block_readback_checks,
    plan_expects_attribute_readback,
)
from core.verification.evidence_contract import EVIDENCE_DEFERRED_CAD_READBACK
from core.verification.geometry_checks import check_block_reference_readback, expected_block_reference_from_plan

DEFAULT_MANIFEST_REL = "examples/capability_proof/block_attribute_probe_manifest.json"
RBLOCK_06_PACKAGE_ID = "RBLOCK-06-BLOCK-ATTRIBUTE-BOUNDARY"
RBLOCK_06_BOUNDARY_DOC = "docs/verification/rblock_06_block_attribute_boundary.md"
LEGACY_BOUNDARY_DOC = "docs/verification/beta_cad_block_02_boundaries.md"

RBLOCK_06_ARTIFACTS = (
    "core/verification/block_attribute_probe.py",
    "examples/plans/insert_block_alpha_attribute_probe.json",
    "tests/core/test_block_attribute_probe.py",
)


def default_manifest_path(root: Path) -> Path:
    return root / DEFAULT_MANIFEST_REL


def load_block_attribute_probe_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError(f"{path} must be a JSON object")
    if manifest.get("manifest_id") != "block-attribute-probe-01":
        raise ValueError(f"unexpected manifest_id: {manifest.get('manifest_id')!r}")
    return manifest


def run_block_attribute_probe_smoke(*, project_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """No-CAD smoke: probe plan validates; missing tags defer; baseline skips attribute check."""

    root = project_root.resolve()
    probe_path = root / str(manifest["probe_plan_path"])
    baseline_path = root / str(manifest["baseline_plan_path"])
    probe_plan = json.loads(probe_path.read_text(encoding="utf-8"))
    baseline_plan = json.loads(baseline_path.read_text(encoding="utf-8"))

    probe_errors = validate_plan(probe_plan)
    if probe_errors:
        raise AssertionError(f"probe plan must validate: {probe_errors[:2]}")
    if not plan_expects_attribute_readback(probe_plan):
        raise AssertionError("probe plan must set attribute_readback_probe")

    expected_tags = list(manifest.get("expected_probe_tags", []))
    plan_tags = sorted(probe_plan.get("object", {}).get("attributes", {}).keys())
    if sorted(str(tag) for tag in expected_tags) != sorted(str(tag) for tag in plan_tags):
        raise AssertionError(f"probe plan tags mismatch: expected {expected_tags}, got {plan_tags}")

    expected = expected_block_reference_from_plan(probe_plan)
    entity_no_attrs = {"handle": "BR-PROBE", "type": "block_reference", **expected}
    deferred = check_block_attribute_readback(probe_plan, entity_no_attrs)
    if deferred.get("status") != "deferred":
        raise AssertionError(f"missing attributes must defer, got {deferred.get('status')!r}")

    geometry_checks = check_block_reference_readback(probe_plan, entity_no_attrs)
    _, geometry_verified, evidence_state = merge_block_readback_checks(geometry_checks, deferred)
    if geometry_verified:
        raise AssertionError("missing attribute tags must block geometry_verified")
    if evidence_state != EVIDENCE_DEFERRED_CAD_READBACK:
        raise AssertionError(f"expected deferred evidence_state, got {evidence_state!r}")

    baseline_assessment = check_block_attribute_readback(baseline_plan, entity_no_attrs)
    if baseline_assessment.get("status") != "not_run":
        raise AssertionError("baseline plan must not run attribute readback")

    entity_with_attrs = {
        **entity_no_attrs,
        "attributes": {str(tag): str(probe_plan["object"]["attributes"][tag]) for tag in plan_tags},
    }
    passed = check_block_attribute_readback(probe_plan, entity_with_attrs)
    if passed.get("status") != "pass":
        raise AssertionError(f"matching tags must pass attribute readback, got {passed.get('status')!r}")

    checks, geometry_verified_match, _ = merge_block_readback_checks(
        check_block_reference_readback(probe_plan, entity_with_attrs),
        passed,
    )
    if not geometry_verified_match:
        raise AssertionError("matching tags with geometry pass must allow geometry_verified")

    return {
        "status": "pass",
        "probe_plan_path": str(probe_path.relative_to(root)).replace("\\", "/"),
        "deferred_failure_category": FAILURE_ATTRIBUTE_UNVERIFIED,
        "checks_run": len(checks),
    }


def assert_block_attribute_boundary_contract(*, project_root: Path) -> None:
    """Raise when RBLOCK-06 attribute probe artifacts or invariants are missing."""

    root = project_root.resolve()
    from core.block_engine.block_matrix_manifest import assert_block_matrix_manifest_contract

    assert_block_matrix_manifest_contract(project_root=root)

    if not (root / RBLOCK_06_BOUNDARY_DOC).is_file():
        raise AssertionError(f"missing RBLOCK-06 boundary doc: {RBLOCK_06_BOUNDARY_DOC}")
    if not (root / LEGACY_BOUNDARY_DOC).is_file():
        raise AssertionError(f"missing legacy boundary doc: {LEGACY_BOUNDARY_DOC}")

    manifest_path = default_manifest_path(root)
    if not manifest_path.is_file():
        raise AssertionError(f"missing manifest: {DEFAULT_MANIFEST_REL}")

    manifest = load_block_attribute_probe_manifest(manifest_path)
    for rel in RBLOCK_06_ARTIFACTS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing RBLOCK-06 artifact: {rel}")

    from core.verification.capability_registry import index_capability_rows, load_capability_registry

    registry = load_capability_registry(
        root / "examples/capability_proof/cad_capability_registry.json",
        project_root=root,
    )
    cap_id = str(manifest.get("registry_capability_id", ""))
    if cap_id and cap_id not in index_capability_rows(registry):
        raise AssertionError(f"missing registry row: {cap_id}")

    smoke = run_block_attribute_probe_smoke(project_root=root, manifest=manifest)
    if smoke.get("status") != "pass":
        raise AssertionError(f"attribute probe smoke failed: {smoke}")


def block_attribute_boundary_status_summary(*, project_root: Path) -> dict[str, Any]:
    manifest = load_block_attribute_probe_manifest(default_manifest_path(project_root))
    return {
        "package_id": RBLOCK_06_PACKAGE_ID,
        "manifest_id": manifest.get("manifest_id"),
        "probe_plan_path": manifest.get("probe_plan_path"),
        "expected_probe_tags": list(manifest.get("expected_probe_tags", [])),
        "legacy_boundary_doc": manifest.get("legacy_boundary_doc"),
    }
