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
from core.schemas.validator import validate_value

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BOUNDARY_PATH = (
    PROJECT_ROOT / "agents" / "commercial_fitout" / "capabilities" / "product_alpha_boundary.json"
)
BOUNDARY_SCHEMA_PATH = (
    PROJECT_ROOT / "core" / "schemas" / "commercial_fitout_product_alpha_boundary.schema.json"
)

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
