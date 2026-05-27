"""Load and validate composition template catalogs from versioned JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.schemas.validator import validate_json


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = PROJECT_ROOT / "libraries" / "composition_templates" / "catalog.json"
CATALOG_SCHEMA_PATH = PROJECT_ROOT / "core" / "schemas" / "composition_template_catalog.schema.json"


def load_composition_template_catalog(path: Path = DEFAULT_CATALOG_PATH) -> dict[str, dict[str, Any]]:
    catalog_path = Path(path)
    errors = validate_json(CATALOG_SCHEMA_PATH, catalog_path)
    if errors:
        joined = "; ".join(errors[:5])
        suffix = " ..." if len(errors) > 5 else ""
        raise ValueError(f"Invalid composition template catalog: {joined}{suffix}")

    with catalog_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    templates = payload.get("templates")
    if not isinstance(templates, dict):
        raise ValueError("composition template catalog must contain a templates object.")

    normalized: dict[str, dict[str, Any]] = {}
    for composition_id, template in templates.items():
        if not isinstance(template, dict):
            raise ValueError(f"composition template {composition_id} must be an object.")
        objects = template.get("objects")
        if not isinstance(objects, list):
            raise ValueError(f"composition template {composition_id} must contain objects.")
        for item in objects:
            if not isinstance(item, dict):
                continue
            if item.get("include_label") or item.get("include_dimensions"):
                instance_id = item.get("instance_id", "<unknown>")
                raise ValueError(
                    f"composition template {composition_id}/{instance_id} must not enable preview labels or dimensions."
                )
        normalized[str(composition_id)] = dict(template)

    return normalized
