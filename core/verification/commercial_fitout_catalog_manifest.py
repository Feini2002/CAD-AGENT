"""Validate commercial_fitout catalog inventory vs capability registry (V-PROOF-20)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.plan_engine.validate_plan import load_json

DEFAULT_COMMERCIAL_FITOUT_CATALOG_MANIFEST = (
    Path("examples") / "capability_proof" / "commercial_fitout_catalog_manifest.json"
)
DEFAULT_OBJECT_CATALOG_PATH = Path("agents") / "commercial_fitout" / "capabilities" / "object_catalog.json"


def load_commercial_fitout_catalog_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    if manifest.get("version") != "0.1":
        raise ValueError("commercial_fitout_catalog_manifest version must be '0.1'.")
    if manifest.get("manifest_id") != "commercial_fitout_catalog":
        raise ValueError("manifest_id must be 'commercial_fitout_catalog'.")
    entries = manifest.get("catalog_entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("catalog_entries must be a non-empty array.")
    return manifest


def validate_commercial_fitout_catalog_manifest(
    manifest: dict[str, Any],
    *,
    object_catalog_path: Path,
) -> list[str]:
    errors: list[str] = []
    catalog = load_json(object_catalog_path)
    catalog_ids = {
        str(row["catalog_object_id"])
        for row in catalog.get("objects", [])
        if isinstance(row, dict) and row.get("catalog_object_id")
    }
    manifest_ids: set[str] = set()
    for index, entry in enumerate(manifest.get("catalog_entries", [])):
        if not isinstance(entry, dict):
            errors.append(f"catalog_entries[{index}] must be an object.")
            continue
        catalog_object_id = str(entry.get("catalog_object_id", ""))
        capability_id = str(entry.get("registry_capability_id", ""))
        expected_capability = f"catalog.commercial_fitout.{catalog_object_id}"
        if capability_id != expected_capability:
            errors.append(f"catalog_entries[{index}] registry_capability_id must be {expected_capability}.")
        if catalog_object_id not in catalog_ids:
            errors.append(f"catalog_entries[{index}] unknown catalog_object_id: {catalog_object_id}")
        elif catalog_object_id in manifest_ids:
            errors.append(f"Duplicate catalog_object_id: {catalog_object_id}")
        else:
            manifest_ids.add(catalog_object_id)
    missing = sorted(catalog_ids - manifest_ids)
    if missing:
        errors.append(f"manifest missing catalog_object_id rows: {', '.join(missing)}")
    return errors


def run_commercial_fitout_catalog_inventory(
    *,
    root: Path,
    manifest_path: Path | None = None,
    object_catalog_path: Path | None = None,
) -> dict[str, Any]:
    manifest_path = manifest_path or (root / DEFAULT_COMMERCIAL_FITOUT_CATALOG_MANIFEST)
    object_catalog_path = object_catalog_path or (root / DEFAULT_OBJECT_CATALOG_PATH)
    manifest = load_commercial_fitout_catalog_manifest(manifest_path)
    errors = validate_commercial_fitout_catalog_manifest(manifest, object_catalog_path=object_catalog_path)
    return {
        "status": "pass" if not errors else "fail",
        "manifest_path": str(manifest_path.relative_to(root)).replace("\\", "/"),
        "catalog_entry_count": len(manifest["catalog_entries"]),
        "errors": errors,
        "catalog_entries": manifest["catalog_entries"],
    }
