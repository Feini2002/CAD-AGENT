"""P3 office scene productization: office alpha boundary (OFFICE-PROD-01)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.agents.scene_alpha import (
    SCENE_ALPHA_SCENARIOS,
    load_scene_preferences,
    validate_scene_alpha_preferences,
)

DEFAULT_MANIFEST_REL = "examples/capability_proof/office_prod_alpha_manifest.json"
OFFICE_PROD_01_PACKAGE_ID = "OFFICE-PROD-01-OFFICE-ALPHA-BOUNDARY"
OFFICE_PROD_01_BOUNDARY_DOC = "docs/verification/office_prod_01_office_alpha_boundary.md"
LEGACY_OFFICE_EVIDENCE_DOC = "docs/verification/office_alpha_benchmark_evidence.md"
OFFICE_ALPHA_BENCHMARK_PATH = "examples/benchmarks/office_alpha_benchmark.json"
OFFICE_ALPHA_SUITE_ID = "office-alpha-benchmark"
EXPECTED_OFFICE_ALPHA_CASE_COUNT = 18

OFFICE_PROD_01_ARTIFACTS = (
    "agents/office/agent.json",
    "agents/office/preferences.json",
    "agents/office/rules.md",
    OFFICE_ALPHA_BENCHMARK_PATH,
    LEGACY_OFFICE_EVIDENCE_DOC,
)


def default_manifest_path(root: Path) -> Path:
    return root / DEFAULT_MANIFEST_REL


def load_office_prod_alpha_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError(f"{path} must be a JSON object")
    if manifest.get("manifest_id") != "office-prod-alpha-01":
        raise ValueError(f"unexpected manifest_id: {manifest.get('manifest_id')!r}")
    return manifest


def assert_office_alpha_boundary_contract(*, project_root: Path) -> None:
    """Raise when OFFICE-PROD-01 office alpha artifacts or invariants are missing."""

    root = project_root.resolve()

    if not (root / OFFICE_PROD_01_BOUNDARY_DOC).is_file():
        raise AssertionError(f"missing OFFICE-PROD-01 boundary doc: {OFFICE_PROD_01_BOUNDARY_DOC}")

    if not (root / LEGACY_OFFICE_EVIDENCE_DOC).is_file():
        raise AssertionError(f"missing legacy office evidence doc: {LEGACY_OFFICE_EVIDENCE_DOC}")

    manifest_path = default_manifest_path(root)
    if not manifest_path.is_file():
        raise AssertionError(f"missing manifest: {DEFAULT_MANIFEST_REL}")

    manifest = load_office_prod_alpha_manifest(manifest_path)

    for rel in OFFICE_PROD_01_ARTIFACTS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing OFFICE-PROD-01 artifact: {rel}")

    if "office" not in SCENE_ALPHA_SCENARIOS:
        raise AssertionError("office must be in SCENE_ALPHA_SCENARIOS")

    preferences = load_scene_preferences("office", root=root)
    pref_errors = validate_scene_alpha_preferences(preferences, scenario="office")
    if pref_errors:
        raise AssertionError("office preferences invalid: " + "; ".join(pref_errors[:3]))

    agent = json.loads((root / "agents/office/agent.json").read_text(encoding="utf-8"))
    if str(agent.get("id", "")) != "office":
        raise AssertionError("agents/office/agent.json id must be office")
    if agent.get("type") != "scene_agent":
        raise AssertionError("office agent must be scene_agent type")

    suite_path = root / str(manifest.get("benchmark_suite_path", OFFICE_ALPHA_BENCHMARK_PATH))
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    if suite.get("suite_id") != OFFICE_ALPHA_SUITE_ID:
        raise AssertionError(f"unexpected suite_id: {suite.get('suite_id')!r}")
    cases = suite.get("cases", [])
    if not isinstance(cases, list) or len(cases) != EXPECTED_OFFICE_ALPHA_CASE_COUNT:
        raise AssertionError(f"expected {EXPECTED_OFFICE_ALPHA_CASE_COUNT} office alpha cases, got {len(cases)}")


def office_alpha_boundary_status_summary(*, project_root: Path) -> dict[str, Any]:
    manifest = load_office_prod_alpha_manifest(default_manifest_path(project_root))
    return {
        "package_id": OFFICE_PROD_01_PACKAGE_ID,
        "manifest_id": manifest.get("manifest_id"),
        "scenario": manifest.get("scenario"),
        "expected_case_count": EXPECTED_OFFICE_ALPHA_CASE_COUNT,
        "benchmark_suite_id": OFFICE_ALPHA_SUITE_ID,
    }
