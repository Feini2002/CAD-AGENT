"""P3 restaurant scene productization: restaurant beta boundary (REST-PROD-02)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.agents.restaurant_scene_beta import (
    run_restaurant_scene_beta_benchmark,
    validate_restaurant_scene_beta_suite,
)
from core.agents.scene_beta import (
    default_restaurant_scene_beta_benchmark_path,
    load_scene_beta_restaurant_preferences,
    validate_scene_beta_restaurant_preferences,
)
from core.verification.capability_registry import index_capability_rows, load_capability_registry

DEFAULT_MANIFEST_REL = "examples/capability_proof/restaurant_prod_beta_manifest.json"
REST_PROD_02_PACKAGE_ID = "REST-PROD-02-RESTAURANT-BETA-BOUNDARY"
REST_PROD_02_BOUNDARY_DOC = "docs/verification/restaurant_prod_02_restaurant_beta_boundary.md"
RESTAURANT_BETA_SUITE_ID = "restaurant-scene-beta-benchmark"
EXPECTED_RESTAURANT_BETA_CASE_COUNT = 8
RESTAURANT_BETA_REGISTRY_PREFIX = "benchmark.restaurant_scene_beta_benchmark."

REST_PROD_02_ARTIFACTS = (
    "core/agents/restaurant_scene_beta.py",
    "core/agents/scene_beta.py",
    "examples/benchmarks/restaurant_scene_beta_benchmark.json",
    "scripts/run_restaurant_scene_beta_benchmark.py",
    "agents/scene_beta_manifest.json",
)


def default_manifest_path(root: Path) -> Path:
    return root / DEFAULT_MANIFEST_REL


def load_restaurant_prod_beta_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError(f"{path} must be a JSON object")
    if manifest.get("manifest_id") != "restaurant-prod-beta-01":
        raise ValueError(f"unexpected manifest_id: {manifest.get('manifest_id')!r}")
    return manifest


def _registry_beta_case_rows(registry: dict[str, Any]) -> list[dict[str, Any]]:
    index = index_capability_rows(registry)
    return [
        row
        for cap_id, row in index.items()
        if cap_id.startswith(RESTAURANT_BETA_REGISTRY_PREFIX)
    ]


def assert_restaurant_beta_boundary_contract(*, project_root: Path) -> None:
    """Raise when REST-PROD-02 restaurant beta artifacts or invariants are missing."""

    root = project_root.resolve()

    from core.agents.restaurant_alpha_boundary import assert_restaurant_alpha_boundary_contract

    assert_restaurant_alpha_boundary_contract(project_root=root)

    if not (root / REST_PROD_02_BOUNDARY_DOC).is_file():
        raise AssertionError(f"missing REST-PROD-02 boundary doc: {REST_PROD_02_BOUNDARY_DOC}")

    manifest_path = default_manifest_path(root)
    if not manifest_path.is_file():
        raise AssertionError(f"missing manifest: {DEFAULT_MANIFEST_REL}")

    load_restaurant_prod_beta_manifest(manifest_path)

    for rel in REST_PROD_02_ARTIFACTS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing REST-PROD-02 artifact: {rel}")

    preferences = load_scene_beta_restaurant_preferences(root=root)
    pref_errors = validate_scene_beta_restaurant_preferences(preferences)
    if pref_errors:
        raise AssertionError("restaurant scene_beta preferences invalid: " + "; ".join(pref_errors[:3]))

    suite_path = default_restaurant_scene_beta_benchmark_path(root)
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    if suite.get("suite_id") != RESTAURANT_BETA_SUITE_ID:
        raise AssertionError(f"unexpected suite_id: {suite.get('suite_id')!r}")

    suite_errors = validate_restaurant_scene_beta_suite(suite)
    if suite_errors:
        raise AssertionError("restaurant scene beta suite invalid: " + "; ".join(suite_errors))

    cases = suite.get("cases", [])
    if not isinstance(cases, list) or len(cases) != EXPECTED_RESTAURANT_BETA_CASE_COUNT:
        raise AssertionError(f"expected {EXPECTED_RESTAURANT_BETA_CASE_COUNT} beta cases, got {len(cases)}")

    registry = load_capability_registry(
        root / "examples/capability_proof/cad_capability_registry.json",
        project_root=root,
    )
    beta_rows = _registry_beta_case_rows(registry)
    if len(beta_rows) != EXPECTED_RESTAURANT_BETA_CASE_COUNT:
        raise AssertionError(
            f"expected {EXPECTED_RESTAURANT_BETA_CASE_COUNT} registry rows for restaurant scene beta, got {len(beta_rows)}"
        )


def run_restaurant_beta_boundary_smoke(*, project_root: Path, output_root: Path) -> dict[str, Any]:
    """Run restaurant scene beta benchmark as REST-PROD-02 no-CAD smoke."""

    return run_restaurant_scene_beta_benchmark(
        project_root=project_root,
        output_root=output_root,
    )


def restaurant_beta_boundary_status_summary(*, project_root: Path) -> dict[str, Any]:
    manifest = load_restaurant_prod_beta_manifest(default_manifest_path(project_root))
    return {
        "package_id": REST_PROD_02_PACKAGE_ID,
        "manifest_id": manifest.get("manifest_id"),
        "scenario": manifest.get("scenario"),
        "expected_case_count": EXPECTED_RESTAURANT_BETA_CASE_COUNT,
        "benchmark_suite_id": RESTAURANT_BETA_SUITE_ID,
        "required_case_tiers": list(manifest.get("required_case_tiers", [])),
    }
