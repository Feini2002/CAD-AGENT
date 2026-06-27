from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import Field

from cad_agent.domain.common import StrictModel
from cad_agent.domain.scene import Dimensions2D


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OBJECT_CATALOG_PATH = Path(__file__).resolve().parents[1] / "resources" / "object_catalog.json"


class ObjectCatalogError(ValueError):
    pass


class CatalogEntry(StrictModel):
    kind: str
    default_dimensions: Dimensions2D
    min_dimensions: Dimensions2D | None = None
    max_dimensions: Dimensions2D | None = None
    generator: str


class CatalogLookup(StrictModel):
    status: Literal["supported", "unsupported"]
    kind: str
    entry: CatalogEntry | None = None
    reason: str | None = None


class ObjectCatalog(StrictModel):
    schema_version: Literal["object-catalog/v1"]
    objects: dict[str, CatalogEntry] = Field(default_factory=dict)

    def lookup(self, kind: str) -> CatalogLookup:
        resolved = str(kind).strip()
        entry = self.objects.get(resolved)
        if entry is None:
            return CatalogLookup(status="unsupported", kind=resolved, entry=None, reason="unsupported_object_kind")
        return CatalogLookup(status="supported", kind=resolved, entry=entry)

    def require_entry(self, kind: str) -> CatalogEntry:
        lookup = self.lookup(kind)
        if lookup.entry is None:
            raise ObjectCatalogError(f"unsupported_object_kind:{lookup.kind}")
        return lookup.entry

    def resolve_dimensions(self, kind: str, requested: Dimensions2D | None = None) -> Dimensions2D:
        entry = self.require_entry(kind)
        dimensions = requested or entry.default_dimensions
        _check_min(kind, dimensions, entry.min_dimensions)
        _check_max(kind, dimensions, entry.max_dimensions)
        return dimensions


def load_object_catalog(path: str | Path = DEFAULT_OBJECT_CATALOG_PATH) -> ObjectCatalog:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    raw_objects = payload.get("objects")
    if not isinstance(raw_objects, dict):
        raise ObjectCatalogError("object_catalog_missing_objects")

    entries: dict[str, CatalogEntry] = {}
    for kind, item in raw_objects.items():
        if not isinstance(item, dict):
            raise ObjectCatalogError(f"object_catalog_entry_invalid:{kind}")
        entry = CatalogEntry(
            kind=str(kind),
            default_dimensions=_dimensions(item, "defaultDimensions"),
            min_dimensions=_optional_dimensions(item, "minDimensions"),
            max_dimensions=_optional_dimensions(item, "maxDimensions"),
            generator=str(item.get("generator") or ""),
        )
        if not entry.generator:
            raise ObjectCatalogError(f"object_catalog_generator_missing:{kind}")
        entries[str(kind)] = entry

    return ObjectCatalog(schema_version=payload.get("schemaVersion"), objects=entries)


def _dimensions(item: dict[str, object], key: str) -> Dimensions2D:
    raw = item.get(key)
    if not isinstance(raw, dict):
        raise ObjectCatalogError(f"object_catalog_dimension_missing:{key}")
    return Dimensions2D(width=float(raw["width"]), depth=float(raw["depth"]))


def _optional_dimensions(item: dict[str, object], key: str) -> Dimensions2D | None:
    if key not in item:
        return None
    return _dimensions(item, key)


def _check_min(kind: str, dimensions: Dimensions2D, minimum: Dimensions2D | None) -> None:
    if minimum is None:
        return
    if dimensions.width < minimum.width or dimensions.depth < minimum.depth:
        raise ObjectCatalogError(f"dimension_below_min:{kind}")


def _check_max(kind: str, dimensions: Dimensions2D, maximum: Dimensions2D | None) -> None:
    if maximum is None:
        return
    if dimensions.width > maximum.width or dimensions.depth > maximum.depth:
        raise ObjectCatalogError(f"dimension_above_max:{kind}")
