"""P3 residential scene productization parent contract (RESIDENTIAL-PROD-01/02 rollup)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.agents.residential_alpha_boundary import (
    EXPECTED_RESIDENTIAL_ALPHA_CASE_COUNT,
    RESIDENTIAL_ALPHA_CASE_ID,
    RESIDENTIAL_PROD_01_BOUNDARY_DOC,
    RESIDENTIAL_PROD_01_PACKAGE_ID,
    assert_residential_alpha_boundary_contract,
)
from core.agents.residential_beta_boundary import (
    EXPECTED_RESIDENTIAL_BETA_CASE_COUNT,
    RESIDENTIAL_PROD_02_BOUNDARY_DOC,
    RESIDENTIAL_PROD_02_PACKAGE_ID,
    assert_residential_beta_boundary_contract,
    run_residential_beta_boundary_smoke,
)
from core.benchmarks.runner import run_benchmark_suite

RESIDENTIAL_P3_WAVE_PACKAGE_ID = "RESIDENTIAL-PROD-03-RESIDENTIAL-P3-WAVE-ROLLUP"
RESIDENTIAL_P3_ACCEPTANCE_DOC = "docs/verification/residential_prod_03_p3_wave_acceptance.md"
RESIDENTIAL_P3_WAVE_PACKAGE_IDS = (
    RESIDENTIAL_PROD_01_PACKAGE_ID,
    RESIDENTIAL_PROD_02_PACKAGE_ID,
)
RESIDENTIAL_P3_BOUNDARY_DOCS = (
    RESIDENTIAL_PROD_01_BOUNDARY_DOC,
    RESIDENTIAL_PROD_02_BOUNDARY_DOC,
)
RESIDENTIAL_P3_MANIFESTS = (
    "examples/capability_proof/residential_prod_alpha_manifest.json",
    "examples/capability_proof/residential_prod_beta_manifest.json",
)
SCENE_ALPHA_BENCHMARK_PATH = "examples/benchmarks/scene_alpha_benchmark.json"
RESIDENTIAL_P3_DEFAULT_OUTPUT_ROOT = "output/validation_runs/res-prod-03-p3-rollup-contract"


def assert_residential_p3_wave_contract(*, project_root: Path) -> None:
    """Raise when the residential P3 rollup artifacts or child contracts are missing."""

    root = project_root.resolve()

    if not (root / RESIDENTIAL_P3_ACCEPTANCE_DOC).is_file():
        raise AssertionError(f"missing RESIDENTIAL-PROD-03 acceptance doc: {RESIDENTIAL_P3_ACCEPTANCE_DOC}")

    for rel in RESIDENTIAL_P3_BOUNDARY_DOCS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing residential P3 boundary doc: {rel}")

    for rel in RESIDENTIAL_P3_MANIFESTS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing residential P3 manifest: {rel}")

    assert_residential_alpha_boundary_contract(project_root=root)
    assert_residential_beta_boundary_contract(project_root=root)

    output_root = root / RESIDENTIAL_P3_DEFAULT_OUTPUT_ROOT

    alpha = run_benchmark_suite(root / SCENE_ALPHA_BENCHMARK_PATH, output_root=output_root / "alpha")
    if alpha.get("status") != "pass":
        raise AssertionError(f"scene alpha benchmark must pass: {alpha.get('summary')}")
    residential_cases = [
        case
        for case in alpha.get("cases", [])
        if isinstance(case, dict) and str(case.get("case_id", "")) == RESIDENTIAL_ALPHA_CASE_ID
    ]
    if len(residential_cases) != EXPECTED_RESIDENTIAL_ALPHA_CASE_COUNT:
        raise AssertionError(
            f"expected {EXPECTED_RESIDENTIAL_ALPHA_CASE_COUNT} residential alpha case, "
            f"got {len(residential_cases)}"
        )
    actual = residential_cases[0].get("actual", {})
    if actual.get("evidence_state") != "benchmark_pass_non_cad":
        raise AssertionError(f"residential alpha case must remain no-CAD benchmark evidence: {actual}")

    beta = run_residential_beta_boundary_smoke(project_root=root, output_root=output_root / "beta")
    if beta.get("status") != "pass":
        raise AssertionError(f"residential beta benchmark must pass: {beta.get('summary')}")
    if beta.get("summary", {}).get("passed") != EXPECTED_RESIDENTIAL_BETA_CASE_COUNT:
        raise AssertionError(
            f"expected {EXPECTED_RESIDENTIAL_BETA_CASE_COUNT} beta cases, got {beta.get('summary')}"
        )

    evidence = beta.get("evidence_summary", {})
    if evidence.get("readback_geometry_verified_count") != 0:
        raise AssertionError("residential P3 no-CAD rollup must not report geometry_verified")


def residential_p3_wave_status_summary(*, project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    return {
        "package_id": RESIDENTIAL_P3_WAVE_PACKAGE_ID,
        "package_ids": list(RESIDENTIAL_P3_WAVE_PACKAGE_IDS),
        "boundary_docs": list(RESIDENTIAL_P3_BOUNDARY_DOCS),
        "acceptance_doc": RESIDENTIAL_P3_ACCEPTANCE_DOC,
        "docs_present": all(
            (root / rel).is_file() for rel in (*RESIDENTIAL_P3_BOUNDARY_DOCS, RESIDENTIAL_P3_ACCEPTANCE_DOC)
        ),
        "child_package_count": len(RESIDENTIAL_P3_WAVE_PACKAGE_IDS),
        "alpha_case_count": EXPECTED_RESIDENTIAL_ALPHA_CASE_COUNT,
        "beta_case_count": EXPECTED_RESIDENTIAL_BETA_CASE_COUNT,
    }
