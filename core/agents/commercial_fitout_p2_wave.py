"""P2 commercial fitout wave parent contract (CFIT-09..12 rollup)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.agents.commercial_fitout_product_boundary import (
    assert_fitout_three_sample_rollup_sync,
    load_product_alpha_boundary,
)
from core.agents.commercial_fitout_scope import PRIMARY_SUBSCENE_IDS
from core.agents.fitout_sample_specs import FITOUT_SAMPLE_SPECS, fitout_subscene_to_sample_id
from core.project_samples.project_sample_cad_rollup import load_project_sample_cad_manifest
from core.verification.fitout_subscene_object_cad_smoke import (
    assert_fitout_subscene_object_manifest_contract,
    load_fitout_subscene_object_cad_smoke_manifest,
)

P2_WAVE_PACKAGE_IDS = (
    "CFIT-09-SECOND-PROJECT-SAMPLE",
    "CFIT-10-RECEPTION-PROJECT-SAMPLE",
    "CFIT-11-THREE-SAMPLE-BOUNDARY-SYNC",
    "CFIT-12-FITOUT-SUBSCENE-OBJECT-CAD-SMOKE",
)

P2_BOUNDARY_DOCS = (
    "docs/verification/cfit_09_second_project_sample_boundary.md",
    "docs/verification/cfit_10_reception_project_sample_boundary.md",
    "docs/verification/cfit_11_three_sample_product_boundary_sync.md",
    "docs/verification/cfit_12_fitout_subscene_object_cad_smoke_boundary.md",
)

P2_ACCEPTANCE_DOC = "docs/verification/commercial_fitout_p2_wave_acceptance.md"

FITOUT_COMPOSITION_MANIFEST = Path(
    "examples/capability_proof/fitout_composition_cad_registry_manifest.json"
)
FITOUT_SUBSCENE_SMOKE_MANIFEST = Path(
    "examples/capability_proof/fitout_subscene_object_cad_smoke_manifest.json"
)
PROJECT_SAMPLE_ROLLUP_MANIFEST = Path("examples/cad_regression/project_sample_cad_rollup.json")


def assert_commercial_fitout_p2_wave_contract(*, project_root: Path) -> None:
    """Raise when CFIT-09..12 artifacts or cross-links are missing."""

    root = project_root.resolve()

    acceptance = root / P2_ACCEPTANCE_DOC
    if not acceptance.is_file():
        raise AssertionError(f"missing P2 acceptance doc: {P2_ACCEPTANCE_DOC}")

    for rel in P2_BOUNDARY_DOCS:
        path = root / rel
        if not path.is_file():
            raise AssertionError(f"missing P2 boundary doc: {rel}")

    mapping = fitout_subscene_to_sample_id()
    if set(mapping) != PRIMARY_SUBSCENE_IDS:
        raise AssertionError(f"fitout subscene mapping mismatch: {sorted(mapping)!r}")

    if len(FITOUT_SAMPLE_SPECS) != 3:
        raise AssertionError(f"expected 3 fitout sample specs, got {len(FITOUT_SAMPLE_SPECS)}")

    boundary = load_product_alpha_boundary()
    assert_fitout_three_sample_rollup_sync(boundary=boundary, project_root=root)

    rollup = load_project_sample_cad_manifest(project_root=root)
    rollup_ids = {str(row["sample_id"]) for row in rollup.get("samples", []) if isinstance(row, dict)}
    for spec in FITOUT_SAMPLE_SPECS.values():
        if spec.sample_id not in rollup_ids:
            raise AssertionError(f"rollup manifest missing sample_id={spec.sample_id!r}")

    composition_manifest = root / FITOUT_COMPOSITION_MANIFEST
    if not composition_manifest.is_file():
        raise AssertionError(f"missing fitout composition manifest: {FITOUT_COMPOSITION_MANIFEST}")

    subscene_manifest = load_fitout_subscene_object_cad_smoke_manifest(
        root / FITOUT_SUBSCENE_SMOKE_MANIFEST
    )
    assert_fitout_subscene_object_manifest_contract(subscene_manifest)

    for spec in FITOUT_SAMPLE_SPECS.values():
        project_dir = root / spec.project_rel
        if not project_dir.is_dir():
            raise AssertionError(f"missing project sample directory: {spec.project_rel}")
        workflow = root / spec.workflow_rel
        if not workflow.is_file():
            raise AssertionError(f"missing workflow: {spec.workflow_rel}")


def p2_wave_status_summary(*, project_root: Path) -> dict[str, Any]:
    """Non-throwing summary for acceptance reports (no CAD execution)."""

    root = project_root.resolve()
    return {
        "package_ids": list(P2_WAVE_PACKAGE_IDS),
        "boundary_docs": list(P2_BOUNDARY_DOCS),
        "acceptance_doc": P2_ACCEPTANCE_DOC,
        "fitout_sample_count": len(FITOUT_SAMPLE_SPECS),
        "primary_subscenes": sorted(PRIMARY_SUBSCENE_IDS),
        "rollup_manifest": str(PROJECT_SAMPLE_ROLLUP_MANIFEST),
        "composition_manifest": str(FITOUT_COMPOSITION_MANIFEST),
        "subscene_smoke_manifest": str(FITOUT_SUBSCENE_SMOKE_MANIFEST),
        "docs_present": all((root / rel).is_file() for rel in (*P2_BOUNDARY_DOCS, P2_ACCEPTANCE_DOC)),
    }
