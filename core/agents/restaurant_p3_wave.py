"""P3 restaurant scene productization parent contract (REST-PROD-01/02 rollup)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.agents.restaurant_alpha_boundary import (
    EXPECTED_RESTAURANT_ALPHA_CASE_COUNT,
    REST_PROD_01_BOUNDARY_DOC,
    REST_PROD_01_PACKAGE_ID,
    assert_restaurant_alpha_boundary_contract,
)
from core.agents.restaurant_beta_boundary import (
    EXPECTED_RESTAURANT_BETA_CASE_COUNT,
    REST_PROD_02_BOUNDARY_DOC,
    REST_PROD_02_PACKAGE_ID,
    assert_restaurant_beta_boundary_contract,
    run_restaurant_beta_boundary_smoke,
)
from core.benchmarks.runner import run_benchmark_suite

RESTAURANT_P3_WAVE_PACKAGE_ID = "REST-PROD-03-RESTAURANT-P3-WAVE-ROLLUP"
RESTAURANT_P3_ACCEPTANCE_DOC = "docs/verification/restaurant_prod_03_p3_wave_acceptance.md"
RESTAURANT_P3_WAVE_PACKAGE_IDS = (
    REST_PROD_01_PACKAGE_ID,
    REST_PROD_02_PACKAGE_ID,
)
RESTAURANT_P3_BOUNDARY_DOCS = (
    REST_PROD_01_BOUNDARY_DOC,
    REST_PROD_02_BOUNDARY_DOC,
)
RESTAURANT_P3_MANIFESTS = (
    "examples/capability_proof/restaurant_prod_alpha_manifest.json",
    "examples/capability_proof/restaurant_prod_beta_manifest.json",
)
SCENE_ALPHA_BENCHMARK_PATH = "examples/benchmarks/scene_alpha_benchmark.json"
RESTAURANT_ALPHA_CASE_ID = "scene_alpha_restaurant_blank_shell"
RESTAURANT_P3_DEFAULT_OUTPUT_ROOT = "output/validation_runs/rest-prod-03-p3-rollup-contract"


def assert_restaurant_p3_wave_contract(*, project_root: Path) -> None:
    """Raise when the restaurant P3 rollup artifacts or child contracts are missing."""

    root = project_root.resolve()

    if not (root / RESTAURANT_P3_ACCEPTANCE_DOC).is_file():
        raise AssertionError(f"missing REST-PROD-03 acceptance doc: {RESTAURANT_P3_ACCEPTANCE_DOC}")

    for rel in RESTAURANT_P3_BOUNDARY_DOCS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing restaurant P3 boundary doc: {rel}")

    for rel in RESTAURANT_P3_MANIFESTS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing restaurant P3 manifest: {rel}")

    assert_restaurant_alpha_boundary_contract(project_root=root)
    assert_restaurant_beta_boundary_contract(project_root=root)

    output_root = root / RESTAURANT_P3_DEFAULT_OUTPUT_ROOT

    alpha = run_benchmark_suite(root / SCENE_ALPHA_BENCHMARK_PATH, output_root=output_root / "alpha")
    if alpha.get("status") != "pass":
        raise AssertionError(f"scene alpha benchmark must pass: {alpha.get('summary')}")
    restaurant_cases = [
        case
        for case in alpha.get("cases", [])
        if isinstance(case, dict) and str(case.get("case_id", "")) == RESTAURANT_ALPHA_CASE_ID
    ]
    if len(restaurant_cases) != EXPECTED_RESTAURANT_ALPHA_CASE_COUNT:
        raise AssertionError(
            f"expected {EXPECTED_RESTAURANT_ALPHA_CASE_COUNT} restaurant alpha case, got {len(restaurant_cases)}"
        )
    actual = restaurant_cases[0].get("actual", {})
    if actual.get("evidence_state") != "benchmark_pass_non_cad":
        raise AssertionError(f"restaurant alpha case must remain no-CAD benchmark evidence: {actual}")

    beta = run_restaurant_beta_boundary_smoke(project_root=root, output_root=output_root / "beta")
    if beta.get("status") != "pass":
        raise AssertionError(f"restaurant beta benchmark must pass: {beta.get('summary')}")
    if beta.get("summary", {}).get("passed") != EXPECTED_RESTAURANT_BETA_CASE_COUNT:
        raise AssertionError(f"expected {EXPECTED_RESTAURANT_BETA_CASE_COUNT} beta cases, got {beta.get('summary')}")

    evidence = beta.get("evidence_summary", {})
    if evidence.get("readback_geometry_verified_count") != 0:
        raise AssertionError("restaurant P3 no-CAD rollup must not report geometry_verified")


def restaurant_p3_wave_status_summary(*, project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    return {
        "package_id": RESTAURANT_P3_WAVE_PACKAGE_ID,
        "package_ids": list(RESTAURANT_P3_WAVE_PACKAGE_IDS),
        "boundary_docs": list(RESTAURANT_P3_BOUNDARY_DOCS),
        "acceptance_doc": RESTAURANT_P3_ACCEPTANCE_DOC,
        "docs_present": all((root / rel).is_file() for rel in (*RESTAURANT_P3_BOUNDARY_DOCS, RESTAURANT_P3_ACCEPTANCE_DOC)),
        "child_package_count": len(RESTAURANT_P3_WAVE_PACKAGE_IDS),
        "alpha_case_count": EXPECTED_RESTAURANT_ALPHA_CASE_COUNT,
        "beta_case_count": EXPECTED_RESTAURANT_BETA_CASE_COUNT,
    }
