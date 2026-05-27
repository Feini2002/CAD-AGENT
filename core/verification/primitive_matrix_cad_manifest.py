"""Load and validate primitive_matrix_cad manifest (V-PROOF-12)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.plan_engine.validate_plan import load_json
from core.verification.primitive_matrix import PRIMITIVE_TYPES

DEFAULT_PRIMITIVE_MATRIX_CAD_MANIFEST = (
    Path("examples") / "capability_proof" / "primitive_matrix_cad_manifest.json"
)


def load_primitive_matrix_cad_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    if manifest.get("version") != "0.1":
        raise ValueError("primitive_matrix_cad_manifest version must be '0.1'.")
    if manifest.get("manifest_id") != "primitive_matrix_cad":
        raise ValueError("primitive_matrix_cad_manifest manifest_id must be 'primitive_matrix_cad'.")
    primitives = manifest.get("primitives")
    if not isinstance(primitives, list) or not primitives:
        raise ValueError("primitive_matrix_cad_manifest requires a non-empty primitives array.")
    return manifest


def validate_primitive_matrix_cad_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, row in enumerate(manifest.get("primitives", [])):
        if not isinstance(row, dict):
            errors.append(f"primitives[{index}] must be an object.")
            continue
        primitive = row.get("primitive")
        capability_id = row.get("capability_id")
        if primitive not in PRIMITIVE_TYPES and row.get("expected_in_probe", True):
            errors.append(f"primitives[{index}].primitive is not in PRIMITIVE_TYPES.")
        if not capability_id:
            errors.append(f"primitives[{index}].capability_id is required.")
        elif capability_id in seen_ids:
            errors.append(f"Duplicate capability_id: {capability_id}")
        else:
            seen_ids.add(str(capability_id))
        if capability_id and primitive and capability_id != f"primitive.{primitive}":
            errors.append(f"primitives[{index}] capability_id must be primitive.{primitive}.")
    regression = manifest.get("regression_case")
    if not isinstance(regression, dict) or regression.get("id") != "primitive_matrix_cad":
        errors.append("regression_case.id must be 'primitive_matrix_cad'.")
    return errors


def primitive_inventory_from_manifest(manifest: dict[str, Any]) -> list[str]:
    return sorted(str(row["primitive"]) for row in manifest["primitives"] if isinstance(row, dict))
