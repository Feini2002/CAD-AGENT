"""P5 block wave parent contract (RBLOCK-03..07 rollup)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.block_engine.block_alpha_boundary import RBLOCK_03_BOUNDARY_DOC
from core.block_engine.block_attribute_boundary import RBLOCK_06_BOUNDARY_DOC
from core.block_engine.block_matrix_manifest import (
    default_manifest_path as matrix_manifest_path,
    run_block_insert_matrix_manifest,
)
from core.block_engine.block_matrix_registry import RBLOCK_07_BOUNDARY_DOC
from core.block_engine.second_controlled_block_boundary import RBLOCK_05_BOUNDARY_DOC
from core.verification.block_alpha_beta_suite import default_suite_path, run_block_alpha_beta_suite

P5_WAVE_PACKAGE_IDS = (
    "RBLOCK-03-BLOCK-ALPHA-BOUNDARY",
    "RBLOCK-04-BLOCK-MATRIX-MANIFEST",
    "RBLOCK-05-SECOND-CONTROLLED-BLOCK",
    "RBLOCK-06-BLOCK-ATTRIBUTE-BOUNDARY",
    "RBLOCK-07-BLOCK-MATRIX-REGISTRY-ROWS",
)

P5_BOUNDARY_DOCS = (
    RBLOCK_03_BOUNDARY_DOC,
    "docs/verification/rblock_04_block_matrix_manifest.md",
    RBLOCK_05_BOUNDARY_DOC,
    RBLOCK_06_BOUNDARY_DOC,
    RBLOCK_07_BOUNDARY_DOC,
)

P5_ACCEPTANCE_DOC = "docs/verification/block_p5_wave_acceptance.md"

P5_MANIFESTS = (
    "examples/capability_proof/block_insert_matrix_manifest.json",
    "examples/capability_proof/second_controlled_block_manifest.json",
    "examples/capability_proof/block_attribute_probe_manifest.json",
)


def assert_block_p5_wave_contract(*, project_root: Path) -> None:
    """Raise when RBLOCK-03..07 artifacts or cross-links are missing."""

    root = project_root.resolve()

    acceptance = root / P5_ACCEPTANCE_DOC
    if not acceptance.is_file():
        raise AssertionError(f"missing P5 acceptance doc: {P5_ACCEPTANCE_DOC}")

    for rel in P5_BOUNDARY_DOCS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing P5 boundary doc: {rel}")

    for rel in P5_MANIFESTS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing P5 manifest: {rel}")

    from core.block_engine.block_matrix_registry import assert_block_matrix_registry_contract

    assert_block_matrix_registry_contract(project_root=root)

    beta = run_block_alpha_beta_suite(default_suite_path(root), output_root=None)
    if beta.get("status") != "pass":
        raise AssertionError(f"block alpha beta suite must pass: {beta.get('summary')}")

    matrix = run_block_insert_matrix_manifest(matrix_manifest_path(root), output_root=None)
    if matrix.get("status") != "pass":
        raise AssertionError(f"block insert matrix must pass: {matrix.get('summary')}")

    if len(beta.get("cases", [])) != 8:
        raise AssertionError(f"expected 8 beta cases, got {len(beta.get('cases', []))}")
    if matrix.get("summary", {}).get("passed") != matrix.get("summary", {}).get("total"):
        raise AssertionError(f"matrix cases incomplete: {matrix.get('summary')}")


def block_p5_wave_status_summary(*, project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    return {
        "package_ids": list(P5_WAVE_PACKAGE_IDS),
        "boundary_docs": list(P5_BOUNDARY_DOCS),
        "acceptance_doc": P5_ACCEPTANCE_DOC,
        "docs_present": all((root / rel).is_file() for rel in (*P5_BOUNDARY_DOCS, P5_ACCEPTANCE_DOC)),
        "child_package_count": len(P5_WAVE_PACKAGE_IDS),
        "manifest_count": len(P5_MANIFESTS),
    }
