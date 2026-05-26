"""Block library metadata loading, normalization, and OBJECT_SPEC mapping."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.schemas.validator import load_json, validate_value


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LIBRARY = PROJECT_ROOT / "libraries" / "blocks" / "block_library.example.json"
BLOCK_LIBRARY_SCHEMA = PROJECT_ROOT / "core" / "schemas" / "block_library.schema.json"

SELECTABLE_VALIDATION_STATUSES = frozenset(
    {"metadata_only", "symbol_fallback", "cad_insertion_verified"}
)


def _point3(value: Any, *, default: list[float]) -> list[float]:
    if isinstance(value, list) and len(value) >= 2:
        z = float(value[2]) if len(value) > 2 else 0.0
        return [float(value[0]), float(value[1]), z]
    return list(default)


def normalize_block(block: dict[str, Any]) -> dict[str, Any]:
    """Normalize legacy 0.1 blocks and fill derived v0.2 fields."""

    normalized = dict(block)
    size = block.get("size", {})
    width = float(size.get("width", 0))
    depth = float(size.get("depth", 0))
    insertion = _point3(block.get("insertion_point"), default=[0.0, 0.0, 0.0])

    anchors = block.get("anchor_points")
    if not isinstance(anchors, dict):
        normalized["anchor_points"] = {
            "insert": insertion,
            "center": [width / 2, depth / 2, insertion[2]],
        }
    else:
        normalized["anchor_points"] = {
            "insert": _point3(anchors.get("insert"), default=insertion),
            "center": _point3(anchors.get("center"), default=[width / 2, depth / 2, insertion[2]]),
        }
        if "back_left" in anchors:
            normalized["anchor_points"]["back_left"] = _point3(anchors["back_left"], default=insertion)

    if "footprint_2d" not in block:
        normalized["footprint_2d"] = {"width": width, "depth": depth}

    clearance_mm = float(block.get("clearance_mm", 0))
    if "clearance_zones" not in block:
        normalized["clearance_zones"] = [{"role": "default_clearance", "offset_mm": clearance_mm, "side": "front"}]
    normalized.setdefault("clearance_mm", clearance_mm)

    if "cad_identity" not in block:
        block_name = str(block.get("block_id", "BLOCK")).replace("-", "_").upper()
        normalized["cad_identity"] = {
            "block_name": block_name,
            "definition_name": block_name,
            "expected_entity_type": "block_reference",
        }

    if "source" not in block:
        normalized["source"] = {
            "type": "symbol_fallback",
            "path": "",
            "status": "symbol_fallback",
        }

    if "symbol_2d" not in block:
        normalized["symbol_2d"] = {
            "type": "rectangle",
            "width": width,
            "depth": depth,
        }

    if "layer_bindings" not in block:
        normalized["layer_bindings"] = {
            "insert_layer_role": "preview",
            "block_internal_layer_role": "furniture",
        }

    if "validation" not in block:
        normalized["validation"] = {
            "status": "symbol_fallback",
            "readback_fields": ["handle", "block_name", "insertion_point", "rotation", "scale", "layer", "bbox"],
            "tolerance_mm": 2.0,
        }

    normalized.setdefault("insertion_point", normalized["anchor_points"]["insert"])
    normalized.setdefault("rotation_allowed", False)
    normalized.setdefault("tags", [])
    return normalized


def validate_block_library(library: dict[str, Any]) -> list[str]:
    """Validate a block library payload and return structured error messages."""

    schema = load_json(BLOCK_LIBRARY_SCHEMA)
    errors = validate_value(library, schema)
    if errors:
        return [f"schema: {message}" for message in errors]

    version = str(library.get("version", ""))
    blocks = library.get("blocks", [])
    if not isinstance(blocks, list):
        return ["blocks must be an array"]

    if version == "0.2":
        if library.get("units") != "mm":
            errors.append("units must be 'mm' for BLOCK_LIBRARY 0.2")
        for index, block in enumerate(blocks):
            if not isinstance(block, dict):
                errors.append(f"blocks[{index}] must be an object")
                continue
            for field in ("source", "cad_identity", "anchor_points", "footprint_2d", "validation"):
                if field not in block:
                    errors.append(f"blocks[{index}] missing required field: {field}")
    return errors


def load_block_library(path: Path = DEFAULT_LIBRARY) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        library = json.load(file)
    if not isinstance(library, dict):
        raise ValueError("Block library must be a JSON object.")

    errors = validate_block_library(library)
    if errors:
        raise ValueError("Invalid block library: " + "; ".join(errors))

    blocks = library.get("blocks", [])
    if isinstance(blocks, list):
        library = dict(library)
        library["blocks"] = [normalize_block(block) for block in blocks if isinstance(block, dict)]
    return library


def select_blocks(
    library: dict[str, Any],
    *,
    category: str | None = None,
    domain: str | None = None,
    tags: list[str] | None = None,
    max_width: float | int | None = None,
    max_depth: float | int | None = None,
    validation_status: str | None = None,
    selectable_only: bool = True,
) -> list[dict[str, Any]]:
    blocks = library.get("blocks", [])
    if not isinstance(blocks, list):
        return []

    tag_set = set(tags or [])
    result: list[dict[str, Any]] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        normalized = normalize_block(block)
        status = str(normalized.get("validation", {}).get("status", "symbol_fallback"))
        if selectable_only and status not in SELECTABLE_VALIDATION_STATUSES:
            continue
        if validation_status and status != validation_status:
            continue
        if category and normalized.get("category") != category:
            continue
        if domain and normalized.get("domain") not in {domain, "generic"}:
            continue
        block_tags = set(normalized.get("tags", []))
        if tag_set and not block_tags.intersection(tag_set):
            continue
        size = normalized.get("size", {})
        if max_width is not None and size.get("width", 0) > max_width:
            continue
        if max_depth is not None and size.get("depth", 0) > max_depth:
            continue
        result.append(normalized)
    return result


def fallback_object_spec(category: str, *, width: float | int, depth: float | int) -> dict[str, Any]:
    from core.object_engine.parametric_objects import create_object_spec

    return create_object_spec(category, width=width, depth=depth)


def object_spec_to_block_reference(
    object_spec: dict[str, Any],
    library: dict[str, Any],
    *,
    domain: str | None = None,
    tags: list[str] | None = None,
    preferred_block_refs: list[str] | None = None,
) -> dict[str, Any]:
    """Map OBJECT_SPEC semantics to a block reference candidate or parametric fallback."""

    category = str(object_spec.get("type") or object_spec.get("category") or "")
    size = object_spec.get("size", {}) if isinstance(object_spec.get("size"), dict) else {}
    max_width = size.get("width")
    max_depth = size.get("depth")
    refs = preferred_block_refs or list(object_spec.get("preferred_block_refs") or [])
    blocks_by_id = {
        str(block.get("block_id")): normalize_block(block)
        for block in library.get("blocks", [])
        if isinstance(block, dict) and block.get("block_id")
    }

    for ref in refs:
        block = blocks_by_id.get(ref)
        if block is None:
            continue
        status = str(block.get("validation", {}).get("status", ""))
        if status not in SELECTABLE_VALIDATION_STATUSES:
            continue
        return {
            "status": "selected",
            "block_reference": _block_reference_payload(block, object_spec=object_spec),
            "fallback_object_spec": None,
            "geometry_accuracy": "not_verified_without_cad_readback",
            "warnings": [],
        }

    from core.block_engine.block_selector import select_block_candidate

    selection = select_block_candidate(
        library,
        category=category,
        domain=domain or object_spec.get("domain"),
        tags=tags,
        max_width=max_width,
        max_depth=max_depth,
    )
    if selection["status"] == "selected" and selection["selected_block"]:
        block = normalize_block(selection["selected_block"])
        return {
            "status": "selected",
            "block_reference": _block_reference_payload(block, object_spec=object_spec),
            "fallback_object_spec": None,
            "geometry_accuracy": "not_verified_without_cad_readback",
            "warnings": selection.get("warnings", []),
        }

    return {
        "status": "fallback",
        "block_reference": None,
        "fallback_object_spec": selection.get("fallback_object_spec")
        or fallback_object_spec(
            category,
            width=float(max_width or 1000),
            depth=float(max_depth or 500),
        ),
        "geometry_accuracy": "not_verified_without_cad_readback",
        "warnings": selection.get("warnings", []),
    }


def _block_reference_payload(block: dict[str, Any], *, object_spec: dict[str, Any]) -> dict[str, Any]:
    anchors = block.get("anchor_points", {})
    return {
        "block_id": block["block_id"],
        "block_version": block.get("block_version", "1"),
        "name": block["name"],
        "category": block["category"],
        "domain": block.get("domain", "generic"),
        "cad_identity": block["cad_identity"],
        "anchor_points": anchors,
        "footprint_2d": block["footprint_2d"],
        "clearance_zones": block.get("clearance_zones", []),
        "layer_bindings": block.get("layer_bindings", {}),
        "symbol_2d": block.get("symbol_2d", {}),
        "validation": block.get("validation", {}),
        "object_spec_id": object_spec.get("object_id"),
        "preferred_layer_role": block.get("layer_bindings", {}).get("insert_layer_role", "preview"),
    }
