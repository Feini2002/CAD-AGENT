"""P3 residential scene productization: residential beta boundary (RESIDENTIAL-PROD-02)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.agents.residential_scene_beta import (
    run_residential_scene_beta_benchmark,
    validate_residential_scene_beta_suite,
)
from core.agents.scene_beta import (
    default_residential_scene_beta_benchmark_path,
    load_scene_beta_residential_preferences,
    validate_scene_beta_residential_preferences,
)
from core.verification.capability_registry import index_capability_rows, load_capability_registry

DEFAULT_MANIFEST_REL = "examples/capability_proof/residential_prod_beta_manifest.json"
RESIDENTIAL_PROD_02_PACKAGE_ID = "RESIDENTIAL-PROD-02-RESIDENTIAL-BETA-BOUNDARY"
RESIDENTIAL_PROD_02_BOUNDARY_DOC = (
    "docs/verification/residential_prod_02_residential_beta_boundary.md"
)
RESIDENTIAL_BETA_SUITE_ID = "residential-scene-beta-benchmark"
EXPECTED_RESIDENTIAL_BETA_CASE_COUNT = 8
RESIDENTIAL_BETA_REGISTRY_PREFIX = "benchmark.residential_scene_beta_benchmark."

RESIDENTIAL_PROD_02_ARTIFACTS = (
    "core/agents/residential_scene_beta.py",
    "core/agents/scene_beta.py",
    "examples/benchmarks/residential_scene_beta_benchmark.json",
    "scripts/run_residential_scene_beta_benchmark.py",
    "agents/scene_beta_manifest.json",
)


def default_manifest_path(root: Path) -> Path:
    return root / DEFAULT_MANIFEST_REL


def load_residential_prod_beta_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError(f"{path} must be a JSON object")
    if manifest.get("manifest_id") != "residential-prod-beta-01":
        raise ValueError(f"unexpected manifest_id: {manifest.get('manifest_id')!r}")
    return manifest


def _registry_beta_case_rows(registry: dict[str, Any]) -> list[dict[str, Any]]:
    index = index_capability_rows(registry)
    return [
        row
        for cap_id, row in index.items()
        if cap_id.startswith(RESIDENTIAL_BETA_REGISTRY_PREFIX)
    ]


def assert_residential_beta_boundary_contract(*, project_root: Path) -> None:
    """Raise when RESIDENTIAL-PROD-02 residential beta artifacts or invariants are missing."""

    root = project_root.resolve()

    from core.agents.residential_alpha_boundary import assert_residential_alpha_boundary_contract

    assert_residential_alpha_boundary_contract(project_root=root)

    if not (root / RESIDENTIAL_PROD_02_BOUNDARY_DOC).is_file():
        raise AssertionError(
            f"missing RESIDENTIAL-PROD-02 boundary doc: {RESIDENTIAL_PROD_02_BOUNDARY_DOC}"
        )

    manifest_path = default_manifest_path(root)
    if not manifest_path.is_file():
        raise AssertionError(f"missing manifest: {DEFAULT_MANIFEST_REL}")

    load_residential_prod_beta_manifest(manifest_path)

    for rel in RESIDENTIAL_PROD_02_ARTIFACTS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing RESIDENTIAL-PROD-02 artifact: {rel}")

    preferences = load_scene_beta_residential_preferences(root=root)
    pref_errors = validate_scene_beta_residential_preferences(preferences)
    if pref_errors:
        raise AssertionError(
            "residential scene_beta preferences invalid: " + "; ".join(pref_errors[:3])
        )

    suite_path = default_residential_scene_beta_benchmark_path(root)
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    if suite.get("suite_id") != RESIDENTIAL_BETA_SUITE_ID:
        raise AssertionError(f"unexpected suite_id: {suite.get('suite_id')!r}")

    suite_errors = validate_residential_scene_beta_suite(suite)
    if suite_errors:
        raise AssertionError("residential scene beta suite invalid: " + "; ".join(suite_errors))

    cases = suite.get("cases", [])
    if not isinstance(cases, list) or len(cases) != EXPECTED_RESIDENTIAL_BETA_CASE_COUNT:
        raise AssertionError(
            f"expected {EXPECTED_RESIDENTIAL_BETA_CASE_COUNT} beta cases, got {len(cases)}"
        )

    registry = load_capability_registry(
        root / "examples/capability_proof/cad_capability_registry.json",
        project_root=root,
    )
    beta_rows = _registry_beta_case_rows(registry)
    if len(beta_rows) != EXPECTED_RESIDENTIAL_BETA_CASE_COUNT:
        raise AssertionError(
            f"expected {EXPECTED_RESIDENTIAL_BETA_CASE_COUNT} registry rows for residential scene beta, "
            f"got {len(beta_rows)}"
        )


def run_residential_beta_boundary_smoke(*, project_root: Path, output_root: Path) -> dict[str, Any]:
    """Run residential scene beta benchmark as RESIDENTIAL-PROD-02 no-CAD smoke."""

    return run_residential_scene_beta_benchmark(
        project_root=project_root,
        output_root=output_root,
    )


def residential_beta_boundary_status_summary(*, project_root: Path) -> dict[str, Any]:
    manifest = load_residential_prod_beta_manifest(default_manifest_path(project_root))
    return {
        "package_id": RESIDENTIAL_PROD_02_PACKAGE_ID,
        "manifest_id": manifest.get("manifest_id"),
        "scenario": manifest.get("scenario"),
        "expected_case_count": EXPECTED_RESIDENTIAL_BETA_CASE_COUNT,
        "benchmark_suite_id": RESIDENTIAL_BETA_SUITE_ID,
        "required_case_tiers": list(manifest.get("required_case_tiers", [])),
    }
