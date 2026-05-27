"""P4 Core wave parent contract (DRAW-01/02 + SYMBOL-08/09 rollup)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.drawing_standard.drawing_standard_boundary import DRAW_01_BOUNDARY_DOC
from core.drawing_standard.drawing_standard_registry import DRAW_02_BOUNDARY_DOC
from core.symbol_engine.block_first_boundary import SYMBOL_09_BOUNDARY_DOC
from core.symbol_engine.block_first_tier import default_manifest_path as block_first_manifest_path
from core.symbol_engine.block_first_tier import run_block_first_tier_smoke
from core.symbol_engine.symbol_fallback_boundary import SYMBOL_08_BOUNDARY_DOC
from core.verification.drawing_standard_beta_suite import default_suite_path, run_drawing_standard_beta_suite

P4_WAVE_PACKAGE_IDS = (
    "DRAW-01-DRAWING-STANDARD-BOUNDARY",
    "DRAW-02-DRAWING-STANDARD-REGISTRY-ROWS",
    "SYMBOL-08-GLYPH-FALLBACK-BOUNDARY",
    "SYMBOL-09-BLOCK-FIRST-TIER",
)

P4_BOUNDARY_DOCS = (
    DRAW_01_BOUNDARY_DOC,
    DRAW_02_BOUNDARY_DOC,
    SYMBOL_08_BOUNDARY_DOC,
    SYMBOL_09_BOUNDARY_DOC,
)

P4_ACCEPTANCE_DOC = "docs/verification/p4_core_wave_acceptance.md"

P4_MANIFESTS = (
    "examples/capability_proof/symbol_block_first_tier_manifest.json",
    "examples/plans/drawing_standard_beta_suite.json",
    "examples/benchmarks/symbol_fallback_policy_benchmark.json",
)


def assert_p4_core_wave_contract(*, project_root: Path) -> None:
    """Raise when P4 Core wave (DRAW/SYMBOL) artifacts or cross-links are missing."""

    root = project_root.resolve()

    if not (root / P4_ACCEPTANCE_DOC).is_file():
        raise AssertionError(f"missing P4 acceptance doc: {P4_ACCEPTANCE_DOC}")

    for rel in P4_BOUNDARY_DOCS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing P4 boundary doc: {rel}")

    for rel in P4_MANIFESTS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing P4 manifest/benchmark: {rel}")

    from core.drawing_standard.drawing_standard_boundary import assert_drawing_standard_boundary_contract
    from core.drawing_standard.drawing_standard_registry import assert_drawing_standard_registry_contract
    from core.symbol_engine.block_first_boundary import assert_block_first_tier_boundary_contract
    from core.symbol_engine.symbol_fallback_boundary import assert_symbol_glyph_fallback_boundary_contract

    assert_drawing_standard_boundary_contract(project_root=root)
    assert_drawing_standard_registry_contract(project_root=root)
    assert_symbol_glyph_fallback_boundary_contract(project_root=root)
    assert_block_first_tier_boundary_contract(project_root=root)

    draw_suite = run_drawing_standard_beta_suite(default_suite_path(root), output_root=None)
    if draw_suite.get("status") != "pass":
        raise AssertionError(f"drawing standard beta must pass: {draw_suite.get('summary')}")
    if len(draw_suite.get("cases", [])) != 6:
        raise AssertionError(f"expected 6 drawing standard cases, got {len(draw_suite.get('cases', []))}")

    block_first = run_block_first_tier_smoke(block_first_manifest_path(root), output_root=None)
    if block_first.get("status") != "pass":
        raise AssertionError(f"block-first tier smoke must pass: {block_first.get('summary')}")
    if block_first.get("summary", {}).get("passed") != 3:
        raise AssertionError(f"expected 3 block-first cases, got {block_first.get('summary')}")


def p4_core_wave_status_summary(*, project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    return {
        "package_id": "CORE-P4-WAVE-PARENT-ROLLUP",
        "package_ids": list(P4_WAVE_PACKAGE_IDS),
        "boundary_docs": list(P4_BOUNDARY_DOCS),
        "acceptance_doc": P4_ACCEPTANCE_DOC,
        "docs_present": all((root / rel).is_file() for rel in (*P4_BOUNDARY_DOCS, P4_ACCEPTANCE_DOC)),
        "child_package_count": len(P4_WAVE_PACKAGE_IDS),
    }
