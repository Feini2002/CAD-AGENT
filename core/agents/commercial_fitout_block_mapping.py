"""Commercial fitout block mapping: controlled block ids, no arbitrary block names."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.agents.commercial_fitout_catalog import catalog_index, load_commercial_fitout_object_catalog
from core.block_engine.block_library import load_block_library, object_spec_to_block_reference
from core.schemas.validator import validate_value

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAPPING_PATH = PROJECT_ROOT / "agents" / "commercial_fitout" / "capabilities" / "block_mapping.json"
MAPPING_SCHEMA_PATH = PROJECT_ROOT / "core" / "schemas" / "commercial_fitout_block_mapping.schema.json"


def load_commercial_fitout_block_mapping(path: Path | None = None) -> dict[str, Any]:
    mapping_path = path or DEFAULT_MAPPING_PATH
    return json.loads(mapping_path.read_text(encoding="utf-8"))


def validate_commercial_fitout_block_mapping(mapping: dict[str, Any]) -> list[str]:
    schema = json.loads(MAPPING_SCHEMA_PATH.read_text(encoding="utf-8"))
    return validate_value(mapping, schema)


def resolve_block_library_path(mapping: dict[str, Any]) -> Path:
    rel = str(mapping.get("block_library_path", ""))
    if not rel:
        raise ValueError("block_library_path is required")
    return PROJECT_ROOT / Path(rel)


def load_fitout_block_library(mapping: dict[str, Any] | None = None) -> dict[str, Any]:
    data = mapping or load_commercial_fitout_block_mapping()
    return load_block_library(resolve_block_library_path(data))


def allowed_block_ids(library: dict[str, Any]) -> frozenset[str]:
    return frozenset(
        str(block.get("block_id"))
        for block in library.get("blocks", [])
        if isinstance(block, dict) and block.get("block_id")
    )


def allowed_cad_block_names(library: dict[str, Any]) -> frozenset[str]:
    names: set[str] = set()
    for block in library.get("blocks", []):
        if not isinstance(block, dict):
            continue
        cad = block.get("cad_identity", {})
        if isinstance(cad, dict):
            for key in ("block_name", "definition_name"):
                value = cad.get(key)
                if isinstance(value, str) and value.strip():
                    names.add(value.strip())
    return frozenset(names)


def assert_block_name_allowed(
    block_name: str,
    *,
    library: dict[str, Any] | None = None,
    mapping: dict[str, Any] | None = None,
) -> None:
    """Reject CAD block names outside the fitout-controlled library."""

    data = mapping or load_commercial_fitout_block_mapping()
    if data.get("policy", {}).get("allow_arbitrary_block_names"):
        raise AssertionError("commercial_fitout policy must not allow arbitrary block names")
    lib = library or load_fitout_block_library(data)
    allowed = allowed_cad_block_names(lib)
    normalized = str(block_name).strip()
    if normalized not in allowed:
        raise ValueError(f"arbitrary_block_name: {normalized!r} is not in fitout allowlist")


def mapping_index(mapping: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    data = mapping or load_commercial_fitout_block_mapping()
    return {
        str(entry["catalog_object_id"]): entry
        for entry in data.get("entries", [])
        if isinstance(entry, dict) and entry.get("catalog_object_id")
    }


def _resolve_single(
    *,
    object_spec: dict[str, Any],
    entry: dict[str, Any],
    library: dict[str, Any],
    mapping: dict[str, Any],
) -> dict[str, Any]:
    primary_block_id = entry.get("primary_block_id")
    if not isinstance(primary_block_id, str) or not primary_block_id:
        return {
            "render_tier": "deferred",
            "status": "blocked",
            "reason": "mapping entry missing primary_block_id",
            "block_reference": None,
            "object_spec": object_spec,
        }

    allowlist = allowed_block_ids(library)
    if primary_block_id not in allowlist:
        fallback_mode = str(entry.get("fallback_mode", mapping.get("policy", {}).get("fallback_when_block_missing")))
        if fallback_mode == "object_spec":
            selection = object_spec_to_block_reference(object_spec, library, preferred_block_refs=[])
            return {
                "render_tier": "object_spec",
                "status": "fallback",
                "reason": f"block_not_in_allowlist: {primary_block_id}",
                "block_reference": None,
                "object_spec": selection.get("fallback_object_spec") or object_spec,
                "warnings": ["block_id not in fitout library; used OBJECT_SPEC fallback"],
            }
        return {
            "render_tier": "deferred",
            "status": "blocked",
            "reason": f"block_not_in_allowlist: {primary_block_id}",
            "block_reference": None,
            "object_spec": object_spec,
        }

    selection = object_spec_to_block_reference(
        object_spec,
        library,
        domain="commercial_fitout",
        preferred_block_refs=[primary_block_id],
    )
    if selection.get("status") == "selected" and selection.get("block_reference"):
        cad_name = str(selection["block_reference"].get("cad_identity", {}).get("block_name", ""))
        assert_block_name_allowed(cad_name, library=library, mapping=mapping)
        return {
            "render_tier": "block",
            "status": "selected",
            "reason": f"mapped block_id={primary_block_id}",
            "block_reference": selection["block_reference"],
            "object_spec": None,
            "warnings": selection.get("warnings", []),
        }

    fallback_mode = str(entry.get("fallback_mode", "object_spec"))
    if fallback_mode == "object_spec":
        return {
            "render_tier": "object_spec",
            "status": "fallback",
            "reason": "block mapping present but selector fell back",
            "block_reference": None,
            "object_spec": selection.get("fallback_object_spec") or object_spec,
            "warnings": selection.get("warnings", []),
        }
    return {
        "render_tier": "deferred",
        "status": "blocked",
        "reason": "block unavailable and fallback_mode is not object_spec",
        "block_reference": None,
        "object_spec": object_spec,
    }


def resolve_catalog_object_render(
    catalog_object_id: str,
    object_spec: dict[str, Any],
    *,
    mapping: dict[str, Any] | None = None,
    library: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve render path for one catalog object: controlled block or OBJECT_SPEC fallback."""

    data = mapping or load_commercial_fitout_block_mapping()
    lib = library or load_fitout_block_library(data)
    entry = mapping_index(data).get(catalog_object_id)
    if entry is None:
        if data.get("policy", {}).get("require_mapping_entry"):
            return {
                "render_tier": "deferred",
                "status": "blocked",
                "reason": "mapping_entry_missing",
                "catalog_object_id": catalog_object_id,
                "block_reference": None,
                "object_spec": object_spec,
            }
        return _resolve_single(object_spec=object_spec, entry={}, library=lib, mapping=data)

    members = entry.get("member_mappings")
    if isinstance(members, list) and members:
        member_results = []
        for member in members:
            if not isinstance(member, dict):
                continue
            role = str(member.get("member_role", ""))
            member_spec = object_spec
            if role and f"-{role}" in str(object_spec.get("object_id", "")):
                member_spec = object_spec
            member_results.append(
                {
                    "member_role": role,
                    **_resolve_single(
                        object_spec=member_spec,
                        entry=member,
                        library=lib,
                        mapping=data,
                    ),
                }
            )
        tiers = {item.get("render_tier") for item in member_results}
        return {
            "catalog_object_id": catalog_object_id,
            "render_tier": "block" if tiers == {"block"} else "object_spec",
            "status": "bundle",
            "member_results": member_results,
        }

    result = _resolve_single(object_spec=object_spec, entry=entry, library=lib, mapping=data)
    result["catalog_object_id"] = catalog_object_id
    return result


def assert_block_mapping_contract(
    mapping: dict[str, Any] | None = None,
    *,
    catalog: dict[str, Any] | None = None,
) -> None:
    data = mapping or load_commercial_fitout_block_mapping()
    errors = validate_commercial_fitout_block_mapping(data)
    if errors:
        raise AssertionError("block mapping invalid: " + "; ".join(errors))

    if data.get("policy", {}).get("allow_arbitrary_block_names") is not False:
        raise AssertionError("allow_arbitrary_block_names must be false")

    lib = load_fitout_block_library(data)
    allowlist = allowed_block_ids(lib)
    for entry in data.get("entries", []):
        if not isinstance(entry, dict):
            continue
        block_id = entry.get("primary_block_id")
        if isinstance(block_id, str) and block_id not in allowlist:
            raise AssertionError(f"primary_block_id {block_id!r} not in fitout block library")
        for member in entry.get("member_mappings", []) or []:
            if isinstance(member, dict):
                mid = member.get("primary_block_id")
                if isinstance(mid, str) and mid not in allowlist:
                    raise AssertionError(f"member primary_block_id {mid!r} not in fitout block library")

    cat = catalog or load_commercial_fitout_object_catalog()
    cat_ids = set(catalog_index(cat))
    mapped_ids = set(mapping_index(data))
    missing = cat_ids - mapped_ids
    if missing:
        raise AssertionError(f"catalog objects missing block mapping: {sorted(missing)}")

    assert_block_name_allowed("FITOUT_DESK_1400", library=lib, mapping=data)
    try:
        assert_block_name_allowed("RANDOM_COMPANY_BLOCK", library=lib, mapping=data)
        raise AssertionError("expected arbitrary block name to be rejected")
    except ValueError as exc:
        if "arbitrary_block_name" not in str(exc):
            raise
