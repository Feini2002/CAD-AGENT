"""P4 block-first tier boundary contract (SYMBOL-09)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.symbol_engine.block_first_tier import (
    default_manifest_path,
    load_block_first_tier_manifest,
    run_block_first_tier_smoke,
)
from core.symbol_engine.fallback_policy import TIER_TO_CAD_INTENT
from core.verification.capability_registry import index_capability_rows, load_capability_registry, validate_capability_registry
from core.verification.capability_registry_seed_common import PREVIEW_SAFETY, _slug
from core.drawing_standard.drawing_standard_registry import (
    SmokeEvidenceWritebackRequest,
    apply_smoke_registry_evidence_writeback,
)

SYMBOL_09_PACKAGE_ID = "SYMBOL-09-BLOCK-FIRST-TIER"
SYMBOL_09_BOUNDARY_DOC = "docs/verification/symbol_09_block_first_tier_boundary.md"
SYMBOL_BLOCK_FIRST_MANIFEST = "examples/capability_proof/symbol_block_first_tier_manifest.json"
BLOCK_FIRST_RUNNER = "scripts/run_block_first_tier_smoke.py"
SYMBOL_09_DEFAULT_OUTPUT = "output/validation_runs/symbol-09-block-first-no-cad"

SYMBOL_09_SUITE_CAPABILITY_ID = "symbol.block_first.symbol_block_first_tier_01"


def capability_id_for_block_first_case(case_id: str) -> str:
    return f"symbol.block_first.{_slug(case_id)}"


def expected_block_first_case_ids(*, project_root: Path) -> list[str]:
    manifest = load_block_first_tier_manifest(default_manifest_path(project_root))
    return [str(case["case_id"]) for case in manifest["cases"]]


def build_block_first_registry_row(
    *,
    case_id: str | None,
    output_root: str = SYMBOL_09_DEFAULT_OUTPUT,
) -> dict[str, Any]:
    if case_id is None:
        capability_id = SYMBOL_09_SUITE_CAPABILITY_ID
        display_name = "Symbol block-first tier smoke suite"
        source_key = "symbol-block-first-tier-01"
        report_rel = f"{output_root}/block_first_tier_summary.json"
    else:
        capability_id = capability_id_for_block_first_case(case_id)
        display_name = f"Symbol block-first / {case_id}"
        source_key = case_id
        report_rel = f"{output_root}/{case_id}/case_result.json"

    return {
        "capability_id": capability_id,
        "display_name": display_name,
        "category": "symbol",
        "claim_level": "smoke",
        "ladder_level": "L1",
        "domain": "generic",
        "tags": ["block_first", "V-PROOF-34", "SYMBOL-09"],
        "notes": [
            "SYMBOL-09 block-first tier smoke row; block tier requires cad_insertion_verified controlled block.",
            "Does not imply real CAD geometry_verified until RCAD-25.",
        ],
        "source_refs": [
            {
                "source_kind": "documentation",
                "source_path": SYMBOL_BLOCK_FIRST_MANIFEST,
                "source_key": source_key,
            }
        ],
        "cad_case": {
            "case_kind": "script",
            "requires_real_cad": False,
            "entrypoint": BLOCK_FIRST_RUNNER,
            "output_path": report_rel,
            "safety": dict(PREVIEW_SAFETY),
        },
    }


def build_block_first_registry_rows(*, project_root: Path, output_root: str = SYMBOL_09_DEFAULT_OUTPUT) -> list[dict[str, Any]]:
    rows = [build_block_first_registry_row(case_id=None, output_root=output_root)]
    for case_id in expected_block_first_case_ids(project_root=project_root):
        rows.append(build_block_first_registry_row(case_id=case_id, output_root=output_root))
    return rows


def assert_block_first_tier_boundary_contract(*, project_root: Path) -> None:
    """Raise when SYMBOL-09 block-first artifacts or invariants are missing."""

    root = project_root.resolve()

    for rel in (
        SYMBOL_09_BOUNDARY_DOC,
        SYMBOL_BLOCK_FIRST_MANIFEST,
        BLOCK_FIRST_RUNNER,
        "core/symbol_engine/block_first_tier.py",
        "core/symbol_engine/fallback_policy.py",
    ):
        if not (root / rel).is_file():
            raise AssertionError(f"missing SYMBOL-09 artifact: {rel}")

    if TIER_TO_CAD_INTENT.get("block") != "insert_block_alpha":
        raise AssertionError("block tier must map to insert_block_alpha")

    registry = load_capability_registry(
        root / "examples/capability_proof/cad_capability_registry.json",
        project_root=root,
    )
    index = index_capability_rows(registry)
    if SYMBOL_09_SUITE_CAPABILITY_ID not in index:
        raise AssertionError(f"missing registry suite row: {SYMBOL_09_SUITE_CAPABILITY_ID}")
    for case_id in expected_block_first_case_ids(project_root=root):
        capability_id = capability_id_for_block_first_case(case_id)
        if capability_id not in index:
            raise AssertionError(f"missing registry row: {capability_id}")

    schema_errors = validate_capability_registry(registry)
    if schema_errors:
        raise AssertionError(f"registry validation failed: {schema_errors[:3]}")

    manifest = load_block_first_tier_manifest(default_manifest_path(root))
    if manifest.get("manifest_id") != "symbol-block-first-tier-01":
        raise AssertionError(f"unexpected manifest_id: {manifest.get('manifest_id')!r}")

    smoke = run_block_first_tier_smoke(default_manifest_path(root), output_root=None)
    if smoke.get("status") != "pass":
        raise AssertionError(f"block-first smoke must pass in contract: {smoke.get('summary')}")


def build_smoke_writeback_requests_from_block_first_output(
    smoke_result: dict[str, Any],
    *,
    output_root: Path,
    project_root: Path,
) -> list[SmokeEvidenceWritebackRequest]:
    summary_rel = str(output_root.relative_to(project_root)).replace("\\", "/")
    requests = [
        SmokeEvidenceWritebackRequest(
            capability_id=SYMBOL_09_SUITE_CAPABILITY_ID,
            report_path=f"{summary_rel}/block_first_tier_summary.json",
        )
    ]
    for case in smoke_result.get("cases", []):
        if not isinstance(case, dict):
            continue
        case_id = str(case.get("case_id", ""))
        if case_id:
            requests.append(
                SmokeEvidenceWritebackRequest(
                    capability_id=capability_id_for_block_first_case(case_id),
                    report_path=f"{summary_rel}/{case_id}/case_result.json",
                )
            )
    return requests


def sync_block_first_registry_from_smoke(
    registry: dict[str, Any],
    smoke_result: dict[str, Any],
    *,
    output_root: Path,
    project_root: Path,
    dry_run: bool = False,
) -> list[Any]:
    if str(smoke_result.get("status", "")) != "pass":
        raise ValueError("smoke_result.status must be pass before registry sync")

    index = index_capability_rows(registry)
    requests = build_smoke_writeback_requests_from_block_first_output(
        smoke_result,
        output_root=output_root,
        project_root=project_root,
    )
    return [
        apply_smoke_registry_evidence_writeback(
            registry,
            request,
            project_root=project_root,
            row_index=index,
            dry_run=dry_run,
        )
        for request in requests
    ]


def block_first_boundary_status_summary(*, project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    manifest = load_block_first_tier_manifest(default_manifest_path(root))
    return {
        "package_id": SYMBOL_09_PACKAGE_ID,
        "docs_present": (root / SYMBOL_09_BOUNDARY_DOC).is_file(),
        "case_count": len(manifest.get("cases", [])),
        "block_cad_intent": TIER_TO_CAD_INTENT.get("block"),
    }
