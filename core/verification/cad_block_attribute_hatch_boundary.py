"""LCAD-07: machine-readable boundary for block / attribute / hatch CAD capabilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.schemas.validator import validate_value

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BOUNDARY_PATH = (
    PROJECT_ROOT / "examples" / "cad_regression" / "cad_block_attribute_hatch_boundary.json"
)
BOUNDARY_SCHEMA_PATH = PROJECT_ROOT / "core" / "schemas" / "cad_block_attribute_hatch_boundary.schema.json"

REQUIRED_CAPABILITY_IDS = frozenset(
    {
        "insert_block_alpha_controlled",
        "block_attribute_tags_probe",
        "hatch_write_readback",
    }
)


def load_cad_block_attribute_hatch_boundary(path: Path | None = None) -> dict[str, Any]:
    boundary_path = path or DEFAULT_BOUNDARY_PATH
    return json.loads(boundary_path.read_text(encoding="utf-8"))


def validate_cad_block_attribute_hatch_boundary(boundary: dict[str, Any]) -> list[str]:
    schema = json.loads(BOUNDARY_SCHEMA_PATH.read_text(encoding="utf-8"))
    return validate_value(boundary, schema)


def _capability_by_id(boundary: dict[str, Any], capability_id: str) -> dict[str, Any] | None:
    for item in boundary.get("capabilities", []):
        if isinstance(item, dict) and item.get("id") == capability_id:
            return item
    return None


def assert_cad_block_attribute_hatch_boundary_contract(boundary: dict[str, Any] | None = None) -> None:
    """Raise when boundary misstates verified vs deferred capabilities."""

    data = boundary or load_cad_block_attribute_hatch_boundary()
    errors = validate_cad_block_attribute_hatch_boundary(data)
    if errors:
        raise AssertionError("cad_block_attribute_hatch_boundary invalid: " + "; ".join(errors))

    capability_ids = {
        str(item.get("id"))
        for item in data.get("capabilities", [])
        if isinstance(item, dict) and item.get("id")
    }
    missing = REQUIRED_CAPABILITY_IDS - capability_ids
    if missing:
        raise AssertionError(f"capabilities missing ids: {sorted(missing)!r}")

    block = _capability_by_id(data, "insert_block_alpha_controlled")
    assert block is not None
    if block.get("status") != "verified" or block.get("geometry_verified") is not True:
        raise AssertionError("insert_block_alpha_controlled must be verified with geometry_verified=true")

    attributes = _capability_by_id(data, "block_attribute_tags_probe")
    assert attributes is not None
    if attributes.get("status") != "verified":
        raise AssertionError("block_attribute_tags_probe must be verified when tags match")

    hatch = _capability_by_id(data, "hatch_write_readback")
    assert hatch is not None
    if hatch.get("status") != "deferred" or hatch.get("geometry_verified") is not False:
        raise AssertionError("hatch_write_readback must be deferred with geometry_verified=false")

    for item in data.get("capabilities", []):
        if not isinstance(item, dict):
            continue
        if item.get("status") == "deferred" and item.get("geometry_verified") is True:
            raise AssertionError(f"deferred capability must not claim geometry_verified: {item.get('id')}")
        if item.get("status") == "verified" and item.get("geometry_verified") is False:
            raise AssertionError(f"verified capability must claim geometry_verified: {item.get('id')}")

    for path_str in block.get("evidence", []):
        if not (PROJECT_ROOT / str(path_str)).exists():
            raise AssertionError(f"missing block evidence path: {path_str}")


def summarize_capability_matrix(boundary: dict[str, Any] | None = None) -> list[dict[str, str]]:
    data = boundary or load_cad_block_attribute_hatch_boundary()
    rows: list[dict[str, str]] = []
    for item in data.get("capabilities", []):
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "id": str(item.get("id", "")),
                "primitive": str(item.get("primitive", "")),
                "status": str(item.get("status", "")),
                "geometry_verified": "yes" if item.get("geometry_verified") else "no",
            }
        )
    return rows
