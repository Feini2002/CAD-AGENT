"""Commercial fitout Scene Product Alpha boundary rollup (C-CFIT-07)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.agents.commercial_fitout_scope import (
    PRIMARY_SUBSCENE_IDS,
    load_commercial_fitout_scope,
    validate_commercial_fitout_scope,
)
from core.agents.fitout_sample_specs import FITOUT_SAMPLE_SPECS, fitout_subscene_to_sample_id
from core.project_samples.project_sample_cad_rollup import load_project_sample_cad_manifest
from core.schemas.validator import validate_value

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BOUNDARY_PATH = (
    PROJECT_ROOT / "agents" / "commercial_fitout" / "capabilities" / "product_alpha_boundary.json"
)
BOUNDARY_SCHEMA_PATH = (
    PROJECT_ROOT / "core" / "schemas" / "commercial_fitout_product_alpha_boundary.schema.json"
)

FITOUT_DEIDENTIFIED_SAMPLE_IDS = frozenset(FITOUT_SAMPLE_SPECS)

REQUIRED_PACKAGES = frozenset(
    {
        "C-CFIT-01-SCOPE-AND-SUBSCENES",
        "C-CFIT-02-OBJECT-CATALOG",
        "C-CFIT-03-BLOCK-MAPPING",
        "C-CFIT-04-MICRO-SCENE-BENCHMARK",
        "C-CFIT-05-SAMPLE-PROJECT-CONFIRMATION",
        "C-CFIT-06-REAL-CAD-SMOKE",
    }
)


def load_product_alpha_boundary(path: Path | None = None) -> dict[str, Any]:
    boundary_path = path or DEFAULT_BOUNDARY_PATH
    return json.loads(boundary_path.read_text(encoding="utf-8"))


def validate_product_alpha_boundary(boundary: dict[str, Any]) -> list[str]:
    schema = json.loads(BOUNDARY_SCHEMA_PATH.read_text(encoding="utf-8"))
    return validate_value(boundary, schema)


def assert_product_boundary_contract(boundary: dict[str, Any] | None = None) -> None:
    """Raise when rollup violates conservative Scene Product Alpha claims."""

    data = boundary or load_product_alpha_boundary()
    errors = validate_product_alpha_boundary(data)
    if errors:
        raise AssertionError("product_alpha_boundary invalid: " + "; ".join(errors))

    maturity = data.get("maturity", {})
    if maturity.get("declares_scene_product_complete") is not False:
        raise AssertionError("must not declare scene product complete")
    if maturity.get("level") != "scene_product_alpha":
        raise AssertionError("maturity.level must be scene_product_alpha")

    package_ids = {item.get("package_id") for item in data.get("completed_packages", []) if isinstance(item, dict)}
    missing = REQUIRED_PACKAGES - package_ids
    if missing:
        raise AssertionError(f"completed_packages missing: {sorted(missing)!r}")

    if set(data.get("primary_subscenes", [])) != PRIMARY_SUBSCENE_IDS:
        raise AssertionError("primary_subscenes must match scope fixture")

    scope = load_commercial_fitout_scope()
    scope_errors = validate_commercial_fitout_scope(scope)
    if scope_errors:
        raise AssertionError("subscenes.json out of sync with scope schema: " + "; ".join(scope_errors))

    if scope.get("product_alpha_status") != "product_boundary":
        raise AssertionError(
            "subscenes.json product_alpha_status must be product_boundary after C-CFIT-07"
        )

    geometry_claims = [
        item
        for item in data.get("declarable_capabilities", [])
        if isinstance(item, dict) and item.get("geometry_verified") is True
    ]
    for item in geometry_claims:
        if not item.get("geometry_verified_note"):
            raise AssertionError(
                f"declarable_capabilities[{item.get('id')}] requires geometry_verified_note when geometry_verified=true"
            )

    assert_fitout_three_sample_rollup_sync(boundary=data, project_root=PROJECT_ROOT)


def assert_fitout_three_sample_rollup_sync(
    *,
    boundary: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> None:
    """Raise when product boundary, fitout specs, and LCAD-08 rollup manifest disagree."""

    data = boundary or load_product_alpha_boundary()
    root = project_root or PROJECT_ROOT

    entries = data.get("deidentified_project_samples")
    if not isinstance(entries, list) or len(entries) != len(PRIMARY_SUBSCENE_IDS):
        raise AssertionError("deidentified_project_samples must list three primary subscene samples")

    subscene_ids = {str(item.get("subscene_id")) for item in entries if isinstance(item, dict)}
    if subscene_ids != PRIMARY_SUBSCENE_IDS:
        raise AssertionError(
            f"deidentified_project_samples subscene_id set must be {sorted(PRIMARY_SUBSCENE_IDS)!r}, got {sorted(subscene_ids)!r}"
        )

    spec_by_subscene = {spec.subscene_id: spec for spec in FITOUT_SAMPLE_SPECS.values()}
    if set(spec_by_subscene) != PRIMARY_SUBSCENE_IDS:
        raise AssertionError("fitout_sample_specs must cover all primary subscenes")

    if fitout_subscene_to_sample_id() != {spec.subscene_id: spec.sample_id for spec in FITOUT_SAMPLE_SPECS.values()}:
        raise AssertionError("fitout_subscene_to_sample_id out of sync with FITOUT_SAMPLE_SPECS")

    for entry in entries:
        if not isinstance(entry, dict):
            raise AssertionError("deidentified_project_samples entries must be objects")
        subscene_id = str(entry.get("subscene_id", ""))
        sample_id = str(entry.get("sample_id", ""))
        spec = spec_by_subscene.get(subscene_id)
        if spec is None:
            raise AssertionError(f"unknown subscene in boundary fixture: {subscene_id!r}")
        if sample_id != spec.sample_id:
            raise AssertionError(
                f"boundary sample_id {sample_id!r} != fitout_sample_specs {spec.sample_id!r} for {subscene_id!r}"
            )
        if Path(str(entry.get("project_rel", ""))) != spec.project_rel:
            raise AssertionError(f"boundary project_rel mismatch for {subscene_id!r}")
        if Path(str(entry.get("workflow_rel", ""))) != spec.workflow_rel:
            raise AssertionError(f"boundary workflow_rel mismatch for {subscene_id!r}")
        project_dir = root / spec.project_rel
        if not project_dir.is_dir():
            raise AssertionError(f"missing de-identified project directory: {project_dir}")

    manifest = load_project_sample_cad_manifest(project_root=root)
    manifest_ids = {str(item.get("sample_id")) for item in manifest.get("samples", []) if isinstance(item, dict)}
    missing_manifest = FITOUT_DEIDENTIFIED_SAMPLE_IDS - manifest_ids
    if missing_manifest:
        raise AssertionError(f"project_sample_cad_rollup manifest missing fitout samples: {sorted(missing_manifest)!r}")

    for entry in entries:
        sample_id = str(entry.get("sample_id", ""))
        if not entry.get("rollup_manifest_registered"):
            raise AssertionError(f"rollup_manifest_registered must be true for {sample_id!r}")


def summarize_for_status_pages(boundary: dict[str, Any] | None = None) -> dict[str, str]:
    """Return short lines for CORE_STATUS / CAD_AGENT_STATUS sync."""

    data = boundary or load_product_alpha_boundary()
    sync = data.get("status_page_sync", {})
    if not isinstance(sync, dict):
        return {}
    return {
        "core_status_scene_line": str(sync.get("core_status_scene_line", "")),
        "cad_agent_status_scene_line": str(sync.get("cad_agent_status_scene_line", "")),
        "agent_multi_scene_progress_note": str(sync.get("agent_multi_scene_progress_note", "")),
    }
