"""Load commercial_fitout object catalog and materialize Core OBJECT_SPEC entries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.agents.commercial_fitout_scope import load_commercial_fitout_scope
from core.object_engine.parametric_objects import create_object_spec
from core.schemas.validator import validate_value

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = PROJECT_ROOT / "agents" / "commercial_fitout" / "capabilities" / "object_catalog.json"
CATALOG_SCHEMA_PATH = PROJECT_ROOT / "core" / "schemas" / "commercial_fitout_object_catalog.schema.json"
OBJECT_SPEC_SCHEMA_PATH = PROJECT_ROOT / "core" / "schemas" / "object_spec.schema.json"

CORE_OBJECT_TYPES = frozenset(
    {"cabinet", "shelf", "table", "desk", "chair", "sofa", "counter", "display_unit"}
)


def load_commercial_fitout_object_catalog(path: Path | None = None) -> dict[str, Any]:
    catalog_path = path or DEFAULT_CATALOG_PATH
    return json.loads(catalog_path.read_text(encoding="utf-8"))


def validate_commercial_fitout_object_catalog(catalog: dict[str, Any]) -> list[str]:
    schema = json.loads(CATALOG_SCHEMA_PATH.read_text(encoding="utf-8"))
    return validate_value(catalog, schema)


def _size_tuple(size: dict[str, Any]) -> tuple[float | int, float | int, float | int]:
    return size["width"], size["depth"], size["height"]


def _materialize_member_spec(
    *,
    catalog_object_id: str,
    member: dict[str, Any],
    display_name: str,
) -> dict[str, Any]:
    width, depth, height = _size_tuple(member["default_size"])
    core_type = str(member["core_object_type"])
    if core_type not in CORE_OBJECT_TYPES:
        raise ValueError(f"Unsupported core_object_type: {core_type}")
    spec = create_object_spec(
        core_type,
        name=f"{display_name} ({member['member_role']})",
        width=width,
        depth=depth,
        height=height,
    )
    spec["object_id"] = f"catalog-{catalog_object_id}-{member['member_role']}"
    return spec


def catalog_entry_to_object_specs(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand one catalog row to one or more OBJECT_SPEC dicts for Core layout / plan pipelines."""

    catalog_object_id = str(entry["catalog_object_id"])
    display_name = str(entry.get("display_name", catalog_object_id))
    bundle = entry.get("bundle_members")
    if isinstance(bundle, list) and bundle:
        return [
            _materialize_member_spec(
                catalog_object_id=catalog_object_id,
                member=member,
                display_name=display_name,
            )
            for member in bundle
            if isinstance(member, dict)
        ]

    width, depth, height = _size_tuple(entry["default_size"])
    core_type = str(entry["core_object_type"])
    spec = create_object_spec(
        core_type,
        name=display_name,
        width=width,
        depth=depth,
        height=height,
    )
    spec["object_id"] = f"catalog-{catalog_object_id}"
    return [spec]


def object_specs_for_subscene(
    subscene_id: str,
    *,
    catalog: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    data = catalog or load_commercial_fitout_object_catalog()
    specs: list[dict[str, Any]] = []
    for entry in data.get("objects", []):
        if not isinstance(entry, dict):
            continue
        if subscene_id not in entry.get("subscenes", []):
            continue
        specs.extend(catalog_entry_to_object_specs(entry))
    return specs


def catalog_index(catalog: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    data = catalog or load_commercial_fitout_object_catalog()
    return {
        str(entry["catalog_object_id"]): entry
        for entry in data.get("objects", [])
        if isinstance(entry, dict) and entry.get("catalog_object_id")
    }


def assert_catalog_contract(catalog: dict[str, Any] | None = None) -> None:
    """Raise AssertionError when catalog does not satisfy C-CFIT-02 contract."""

    data = catalog or load_commercial_fitout_object_catalog()
    errors = validate_commercial_fitout_object_catalog(data)
    if errors:
        raise AssertionError("commercial_fitout object catalog invalid: " + "; ".join(errors))

    object_schema = json.loads(OBJECT_SPEC_SCHEMA_PATH.read_text(encoding="utf-8"))
    for entry in data.get("objects", []):
        if not isinstance(entry, dict):
            continue
        for spec in catalog_entry_to_object_specs(entry):
            spec_errors = validate_value(spec, object_schema)
            if spec_errors:
                raise AssertionError(f"{spec.get('object_id')}: " + "; ".join(spec_errors))

    scope = load_commercial_fitout_scope()
    index = catalog_index(data)
    for subscene in scope.get("subscenes", []):
        if not isinstance(subscene, dict):
            continue
        for object_id in subscene.get("typical_objects", []):
            if object_id not in index:
                raise AssertionError(f"scope typical_object {object_id!r} missing from object catalog")
