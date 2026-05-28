"""P3 residential scene productization: residential alpha boundary (RESIDENTIAL-PROD-01)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.agents.scene_alpha import (
    SCENE_ALPHA_SCENARIOS,
    load_scene_preferences,
    validate_scene_alpha_preferences,
)

DEFAULT_MANIFEST_REL = "examples/capability_proof/residential_prod_alpha_manifest.json"
RESIDENTIAL_PROD_01_PACKAGE_ID = "RESIDENTIAL-PROD-01-RESIDENTIAL-ALPHA-BOUNDARY"
RESIDENTIAL_PROD_01_BOUNDARY_DOC = (
    "docs/verification/residential_prod_01_residential_alpha_boundary.md"
)
SCENE_ALPHA_BENCHMARK_PATH = "examples/benchmarks/scene_alpha_benchmark.json"
SCENE_ALPHA_SUITE_ID = "scene-alpha-benchmark"
RESIDENTIAL_ALPHA_CASE_ID = "scene_alpha_residential_blank_shell"
EXPECTED_RESIDENTIAL_ALPHA_CASE_COUNT = 1

RESIDENTIAL_PROD_01_ARTIFACTS = (
    "agents/residential/agent.json",
    "agents/residential/preferences.json",
    "agents/residential/rules.md",
    SCENE_ALPHA_BENCHMARK_PATH,
)


def default_manifest_path(root: Path) -> Path:
    return root / DEFAULT_MANIFEST_REL


def load_residential_prod_alpha_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError(f"{path} must be a JSON object")
    if manifest.get("manifest_id") != "residential-prod-alpha-01":
        raise ValueError(f"unexpected manifest_id: {manifest.get('manifest_id')!r}")
    return manifest


def assert_residential_alpha_boundary_contract(*, project_root: Path) -> None:
    """Raise when RESIDENTIAL-PROD-01 residential alpha artifacts or invariants are missing."""

    root = project_root.resolve()

    if not (root / RESIDENTIAL_PROD_01_BOUNDARY_DOC).is_file():
        raise AssertionError(
            f"missing RESIDENTIAL-PROD-01 boundary doc: {RESIDENTIAL_PROD_01_BOUNDARY_DOC}"
        )

    manifest_path = default_manifest_path(root)
    if not manifest_path.is_file():
        raise AssertionError(f"missing manifest: {DEFAULT_MANIFEST_REL}")

    manifest = load_residential_prod_alpha_manifest(manifest_path)

    for rel in RESIDENTIAL_PROD_01_ARTIFACTS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing RESIDENTIAL-PROD-01 artifact: {rel}")

    if "residential" not in SCENE_ALPHA_SCENARIOS:
        raise AssertionError("residential must be in SCENE_ALPHA_SCENARIOS")

    preferences = load_scene_preferences("residential", root=root)
    pref_errors = validate_scene_alpha_preferences(preferences, scenario="residential")
    if pref_errors:
        raise AssertionError("residential preferences invalid: " + "; ".join(pref_errors[:3]))

    agent = json.loads((root / "agents/residential/agent.json").read_text(encoding="utf-8"))
    if str(agent.get("id", "")) != "residential":
        raise AssertionError("agents/residential/agent.json id must be residential")
    if agent.get("type") != "scene_agent":
        raise AssertionError("residential agent must be scene_agent type")

    suite_path = root / str(manifest.get("benchmark_suite_path", SCENE_ALPHA_BENCHMARK_PATH))
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    if suite.get("suite_id") != SCENE_ALPHA_SUITE_ID:
        raise AssertionError(f"unexpected suite_id: {suite.get('suite_id')!r}")
    cases = suite.get("cases", [])
    residential_cases = [
        case
        for case in cases
        if isinstance(case, dict) and str(case.get("case_id", "")) == RESIDENTIAL_ALPHA_CASE_ID
    ]
    if len(residential_cases) != EXPECTED_RESIDENTIAL_ALPHA_CASE_COUNT:
        raise AssertionError(
            f"expected {EXPECTED_RESIDENTIAL_ALPHA_CASE_COUNT} residential alpha case, "
            f"got {len(residential_cases)}"
        )


def residential_alpha_boundary_status_summary(*, project_root: Path) -> dict[str, Any]:
    manifest = load_residential_prod_alpha_manifest(default_manifest_path(project_root))
    return {
        "package_id": RESIDENTIAL_PROD_01_PACKAGE_ID,
        "manifest_id": manifest.get("manifest_id"),
        "scenario": manifest.get("scenario"),
        "expected_case_count": EXPECTED_RESIDENTIAL_ALPHA_CASE_COUNT,
        "benchmark_suite_id": SCENE_ALPHA_SUITE_ID,
        "benchmark_case_id": RESIDENTIAL_ALPHA_CASE_ID,
    }
