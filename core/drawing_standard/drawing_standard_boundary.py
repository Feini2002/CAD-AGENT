"""P4 drawing standard boundary contract (DRAW-01)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.drawing_standard.drawing_standard_profile import (
    DEFAULT_DRAWING_STANDARD_PROFILE_ID,
    load_drawing_standard_profile,
    resolve_layer_role,
)
from core.schemas.registry import get_schema_path
from core.verification.drawing_standard_beta_suite import (
    default_suite_path,
    load_drawing_standard_beta_suite,
)

DRAW_01_PACKAGE_ID = "DRAW-01-DRAWING-STANDARD-BOUNDARY"

DRAW_01_BOUNDARY_DOC = "docs/verification/draw_01_drawing_standard_boundary.md"
LEGACY_BOUNDARY_DOC = "docs/verification/beta_cad_block_04_boundaries.md"

DRAW_01_ARTIFACTS = (
    "libraries/drawing_standards/codex_preview_beta.json",
    "libraries/layer_presets/codex_preview_beta.json",
    "examples/plans/drawing_standard_beta_suite.json",
    "core/schemas/drawing_standard_profile.schema.json",
    "scripts/run_drawing_standard_beta_suite.py",
)


def assert_drawing_standard_boundary_contract(*, project_root: Path) -> None:
    """Raise when DRAW-01 drawing-standard artifacts or policy invariants are missing."""

    root = project_root.resolve()

    boundary = root / DRAW_01_BOUNDARY_DOC
    if not boundary.is_file():
        raise AssertionError(f"missing DRAW-01 boundary doc: {DRAW_01_BOUNDARY_DOC}")

    legacy = root / LEGACY_BOUNDARY_DOC
    if not legacy.is_file():
        raise AssertionError(f"missing legacy boundary doc: {LEGACY_BOUNDARY_DOC}")

    for rel in DRAW_01_ARTIFACTS:
        path = root / rel
        if not path.is_file():
            raise AssertionError(f"missing DRAW-01 artifact: {rel}")

    schema_path = get_schema_path("drawing_standard_profile")
    if not schema_path.is_file():
        raise AssertionError(f"missing drawing_standard_profile schema: {schema_path}")

    profile = load_drawing_standard_profile(DEFAULT_DRAWING_STANDARD_PROFILE_ID)
    policy = profile.get("block_layer_policy", {})
    if str(policy.get("cad_execution_mode", "")) != "preview_only":
        raise AssertionError("codex_preview_beta must use cad_execution_mode=preview_only")
    if str(policy.get("preview_layer", "")) != "CODEX_PREVIEW":
        raise AssertionError("codex_preview_beta preview_layer must be CODEX_PREVIEW")

    furniture_layer = resolve_layer_role(profile, "furniture", for_cad_execution=True)
    if furniture_layer != "CODEX_PREVIEW":
        raise AssertionError(
            f"furniture layer_role must resolve to CODEX_PREVIEW for CAD execution, got {furniture_layer!r}"
        )

    suite_path = default_suite_path(root)
    suite = load_drawing_standard_beta_suite(suite_path)
    if suite.get("suite_id") != "drawing-standard-beta-04":
        raise AssertionError(f"unexpected drawing standard suite_id: {suite.get('suite_id')!r}")
    cases = suite.get("cases", [])
    if len(cases) != 6:
        raise AssertionError(f"expected 6 drawing standard beta cases, got {len(cases)}")


def drawing_standard_boundary_status_summary(*, project_root: Path) -> dict[str, Any]:
    """Machine-readable DRAW-01 status for tests and handoffs."""

    root = project_root.resolve()
    suite = load_drawing_standard_beta_suite(default_suite_path(root))
    return {
        "package_id": DRAW_01_PACKAGE_ID,
        "docs_present": (root / DRAW_01_BOUNDARY_DOC).is_file()
        and (root / LEGACY_BOUNDARY_DOC).is_file(),
        "artifact_count": len(DRAW_01_ARTIFACTS),
        "profile_id": DEFAULT_DRAWING_STANDARD_PROFILE_ID,
        "suite_id": suite.get("suite_id"),
        "case_count": len(suite.get("cases", [])),
    }
