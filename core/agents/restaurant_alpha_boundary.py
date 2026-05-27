"""P3 restaurant scene productization: restaurant alpha boundary (REST-PROD-01)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.agents.scene_alpha import (
    SCENE_ALPHA_SCENARIOS,
    load_scene_preferences,
    validate_scene_alpha_preferences,
)

DEFAULT_MANIFEST_REL = "examples/capability_proof/restaurant_prod_alpha_manifest.json"
REST_PROD_01_PACKAGE_ID = "REST-PROD-01-RESTAURANT-ALPHA-BOUNDARY"
REST_PROD_01_BOUNDARY_DOC = "docs/verification/restaurant_prod_01_restaurant_alpha_boundary.md"
SCENE_ALPHA_BENCHMARK_PATH = "examples/benchmarks/scene_alpha_benchmark.json"
SCENE_ALPHA_SUITE_ID = "scene-alpha-benchmark"
RESTAURANT_ALPHA_CASE_ID = "scene_alpha_restaurant_blank_shell"
EXPECTED_RESTAURANT_ALPHA_CASE_COUNT = 1

REST_PROD_01_ARTIFACTS = (
    "agents/restaurant/agent.json",
    "agents/restaurant/preferences.json",
    "agents/restaurant/rules.md",
    SCENE_ALPHA_BENCHMARK_PATH,
)


def default_manifest_path(root: Path) -> Path:
    return root / DEFAULT_MANIFEST_REL


def load_restaurant_prod_alpha_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError(f"{path} must be a JSON object")
    if manifest.get("manifest_id") != "restaurant-prod-alpha-01":
        raise ValueError(f"unexpected manifest_id: {manifest.get('manifest_id')!r}")
    return manifest


def assert_restaurant_alpha_boundary_contract(*, project_root: Path) -> None:
    """Raise when REST-PROD-01 restaurant alpha artifacts or invariants are missing."""

    root = project_root.resolve()

    if not (root / REST_PROD_01_BOUNDARY_DOC).is_file():
        raise AssertionError(f"missing REST-PROD-01 boundary doc: {REST_PROD_01_BOUNDARY_DOC}")

    manifest_path = default_manifest_path(root)
    if not manifest_path.is_file():
        raise AssertionError(f"missing manifest: {DEFAULT_MANIFEST_REL}")

    manifest = load_restaurant_prod_alpha_manifest(manifest_path)

    for rel in REST_PROD_01_ARTIFACTS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing REST-PROD-01 artifact: {rel}")

    if "restaurant" not in SCENE_ALPHA_SCENARIOS:
        raise AssertionError("restaurant must be in SCENE_ALPHA_SCENARIOS")

    preferences = load_scene_preferences("restaurant", root=root)
    pref_errors = validate_scene_alpha_preferences(preferences, scenario="restaurant")
    if pref_errors:
        raise AssertionError("restaurant preferences invalid: " + "; ".join(pref_errors[:3]))

    agent = json.loads((root / "agents/restaurant/agent.json").read_text(encoding="utf-8"))
    if str(agent.get("id", "")) != "restaurant":
        raise AssertionError("agents/restaurant/agent.json id must be restaurant")
    if agent.get("type") != "scene_agent":
        raise AssertionError("restaurant agent must be scene_agent type")

    suite_path = root / str(manifest.get("benchmark_suite_path", SCENE_ALPHA_BENCHMARK_PATH))
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    if suite.get("suite_id") != SCENE_ALPHA_SUITE_ID:
        raise AssertionError(f"unexpected suite_id: {suite.get('suite_id')!r}")
    cases = suite.get("cases", [])
    restaurant_cases = [
        case
        for case in cases
        if isinstance(case, dict) and str(case.get("case_id", "")) == RESTAURANT_ALPHA_CASE_ID
    ]
    if len(restaurant_cases) != EXPECTED_RESTAURANT_ALPHA_CASE_COUNT:
        raise AssertionError(
            f"expected {EXPECTED_RESTAURANT_ALPHA_CASE_COUNT} restaurant alpha case, got {len(restaurant_cases)}"
        )


def restaurant_alpha_boundary_status_summary(*, project_root: Path) -> dict[str, Any]:
    manifest = load_restaurant_prod_alpha_manifest(default_manifest_path(project_root))
    return {
        "package_id": REST_PROD_01_PACKAGE_ID,
        "manifest_id": manifest.get("manifest_id"),
        "scenario": manifest.get("scenario"),
        "expected_case_count": EXPECTED_RESTAURANT_ALPHA_CASE_COUNT,
        "benchmark_suite_id": SCENE_ALPHA_SUITE_ID,
        "benchmark_case_id": RESTAURANT_ALPHA_CASE_ID,
    }
