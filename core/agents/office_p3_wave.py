"""P3 office scene productization parent contract (OFFICE-PROD-01/02 rollup)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.agents.office_alpha_boundary import (
    EXPECTED_OFFICE_ALPHA_CASE_COUNT,
    OFFICE_PROD_01_BOUNDARY_DOC,
    OFFICE_PROD_01_PACKAGE_ID,
    assert_office_alpha_boundary_contract,
)
from core.agents.office_beta_boundary import (
    EXPECTED_OFFICE_BETA_CASE_COUNT,
    OFFICE_PROD_02_BOUNDARY_DOC,
    OFFICE_PROD_02_PACKAGE_ID,
    assert_office_beta_boundary_contract,
    run_office_beta_boundary_smoke,
)
from core.benchmarks.runner import run_benchmark_suite

OFFICE_P3_WAVE_PACKAGE_ID = "OFFICE-PROD-03-OFFICE-P3-WAVE-ROLLUP"
OFFICE_P3_ACCEPTANCE_DOC = "docs/verification/office_prod_03_p3_wave_acceptance.md"
OFFICE_P3_WAVE_PACKAGE_IDS = (
    OFFICE_PROD_01_PACKAGE_ID,
    OFFICE_PROD_02_PACKAGE_ID,
)
OFFICE_P3_BOUNDARY_DOCS = (
    OFFICE_PROD_01_BOUNDARY_DOC,
    OFFICE_PROD_02_BOUNDARY_DOC,
)
OFFICE_P3_MANIFESTS = (
    "examples/capability_proof/office_prod_alpha_manifest.json",
    "examples/capability_proof/office_prod_beta_manifest.json",
)
OFFICE_ALPHA_BENCHMARK_PATH = "examples/benchmarks/office_alpha_benchmark.json"
OFFICE_P3_DEFAULT_OUTPUT_ROOT = "output/validation_runs/office-prod-03-p3-rollup-contract"


def assert_office_p3_wave_contract(*, project_root: Path) -> None:
    """Raise when the office P3 rollup artifacts or child contracts are missing."""

    root = project_root.resolve()

    if not (root / OFFICE_P3_ACCEPTANCE_DOC).is_file():
        raise AssertionError(f"missing OFFICE-PROD-03 acceptance doc: {OFFICE_P3_ACCEPTANCE_DOC}")

    for rel in OFFICE_P3_BOUNDARY_DOCS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing office P3 boundary doc: {rel}")

    for rel in OFFICE_P3_MANIFESTS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing office P3 manifest: {rel}")

    assert_office_alpha_boundary_contract(project_root=root)
    assert_office_beta_boundary_contract(project_root=root)

    output_root = root / OFFICE_P3_DEFAULT_OUTPUT_ROOT

    alpha = run_benchmark_suite(root / OFFICE_ALPHA_BENCHMARK_PATH, output_root=output_root / "alpha")
    if alpha.get("status") != "pass":
        raise AssertionError(f"office alpha benchmark must pass: {alpha.get('summary')}")
    if alpha.get("summary", {}).get("passed") != EXPECTED_OFFICE_ALPHA_CASE_COUNT:
        raise AssertionError(f"expected {EXPECTED_OFFICE_ALPHA_CASE_COUNT} alpha cases, got {alpha.get('summary')}")

    beta = run_office_beta_boundary_smoke(project_root=root, output_root=output_root / "beta")
    if beta.get("status") != "pass":
        raise AssertionError(f"office beta benchmark must pass: {beta.get('summary')}")
    if beta.get("summary", {}).get("passed") != EXPECTED_OFFICE_BETA_CASE_COUNT:
        raise AssertionError(f"expected {EXPECTED_OFFICE_BETA_CASE_COUNT} beta cases, got {beta.get('summary')}")

    evidence = beta.get("evidence_summary", {})
    if evidence.get("readback_geometry_verified_count") != 0:
        raise AssertionError("office P3 no-CAD rollup must not report geometry_verified")


def office_p3_wave_status_summary(*, project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    return {
        "package_id": OFFICE_P3_WAVE_PACKAGE_ID,
        "package_ids": list(OFFICE_P3_WAVE_PACKAGE_IDS),
        "boundary_docs": list(OFFICE_P3_BOUNDARY_DOCS),
        "acceptance_doc": OFFICE_P3_ACCEPTANCE_DOC,
        "docs_present": all((root / rel).is_file() for rel in (*OFFICE_P3_BOUNDARY_DOCS, OFFICE_P3_ACCEPTANCE_DOC)),
        "child_package_count": len(OFFICE_P3_WAVE_PACKAGE_IDS),
        "alpha_case_count": EXPECTED_OFFICE_ALPHA_CASE_COUNT,
        "beta_case_count": EXPECTED_OFFICE_BETA_CASE_COUNT,
    }
