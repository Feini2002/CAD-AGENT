"""P5 block alpha boundary contract (RBLOCK-03)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.plan_engine.block_alpha_plan import CONTROLLED_BLOCK_ID, CONTROLLED_BLOCK_NAME
from core.schemas.registry import get_schema_path
from core.verification.block_alpha_beta_suite import (
    default_suite_path,
    load_block_alpha_beta_suite,
    run_block_alpha_beta_suite,
)

RBLOCK_03_PACKAGE_ID = "RBLOCK-03-BLOCK-ALPHA-BOUNDARY"

RBLOCK_03_BOUNDARY_DOC = "docs/verification/rblock_03_block_alpha_boundary.md"
LEGACY_ACCEPTANCE_DOC = "docs/verification/beta_cad_block_acceptance.md"

RBLOCK_03_ARTIFACTS = (
    "libraries/blocks/block_library.example.json",
    "examples/plans/block_alpha_beta_suite.json",
    "examples/plans/insert_block_alpha_test.json",
    "core/schemas/block_library.schema.json",
    "scripts/run_block_alpha_beta_suite.py",
    "scripts/run_block_alpha_validation.py",
)


def assert_block_alpha_boundary_contract(*, project_root: Path) -> None:
    """Raise when RBLOCK-03 controlled block-alpha artifacts or invariants are missing."""

    root = project_root.resolve()

    if not (root / RBLOCK_03_BOUNDARY_DOC).is_file():
        raise AssertionError(f"missing RBLOCK-03 boundary doc: {RBLOCK_03_BOUNDARY_DOC}")

    if not (root / LEGACY_ACCEPTANCE_DOC).is_file():
        raise AssertionError(f"missing legacy acceptance doc: {LEGACY_ACCEPTANCE_DOC}")

    for rel in RBLOCK_03_ARTIFACTS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing RBLOCK-03 artifact: {rel}")

    if not get_schema_path("block_library").is_file():
        raise AssertionError("missing block_library schema")

    library = json.loads(
        (root / "libraries/blocks/block_library.example.json").read_text(encoding="utf-8")
    )
    block_ids = {str(item.get("block_id", "")) for item in library.get("blocks", []) if isinstance(item, dict)}
    if CONTROLLED_BLOCK_ID not in block_ids:
        raise AssertionError(f"block library must include {CONTROLLED_BLOCK_ID}")

    controlled = next(
        item for item in library["blocks"] if item.get("block_id") == CONTROLLED_BLOCK_ID
    )
    cad_name = str(controlled.get("cad_identity", {}).get("block_name", ""))
    if cad_name != CONTROLLED_BLOCK_NAME:
        raise AssertionError(f"controlled block cad_identity.block_name must be {CONTROLLED_BLOCK_NAME!r}")

    suite_path = default_suite_path(root)
    suite = load_block_alpha_beta_suite(suite_path)
    if suite.get("suite_id") != "block-alpha-beta-01":
        raise AssertionError(f"unexpected block alpha suite_id: {suite.get('suite_id')!r}")
    if len(suite.get("cases", [])) != 8:
        raise AssertionError(f"expected 8 block alpha beta cases, got {len(suite.get('cases', []))}")

    smoke = run_block_alpha_beta_suite(suite_path, output_root=None)
    if smoke.get("status") != "pass":
        raise AssertionError(f"block alpha beta suite must pass in contract: {smoke.get('summary')}")


def block_alpha_boundary_status_summary(*, project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    suite = load_block_alpha_beta_suite(default_suite_path(root))
    return {
        "package_id": RBLOCK_03_PACKAGE_ID,
        "docs_present": (root / RBLOCK_03_BOUNDARY_DOC).is_file()
        and (root / LEGACY_ACCEPTANCE_DOC).is_file(),
        "artifact_count": len(RBLOCK_03_ARTIFACTS),
        "controlled_block_id": CONTROLLED_BLOCK_ID,
        "suite_id": suite.get("suite_id"),
        "case_count": len(suite.get("cases", [])),
    }
