"""Controlled block alpha helpers for AutoCAD COM driver."""

from __future__ import annotations

import math
from typing import Any


CONTROLLED_BLOCK_NAME = "CODEX_TEST_BLOCK_001"
CONTROLLED_BLOCK_ID = "controlled-test-block-001"
SECOND_CONTROLLED_BLOCK_NAME = "CODEX_TEST_BLOCK_002"
SECOND_CONTROLLED_BLOCK_ID = "controlled-test-block-002"
CONTROLLED_BLOCK_ALLOWLIST = {
    CONTROLLED_BLOCK_ID: CONTROLLED_BLOCK_NAME,
    SECOND_CONTROLLED_BLOCK_ID: SECOND_CONTROLLED_BLOCK_NAME,
}
CONTROLLED_BLOCK_DEFINITION_LAYER = "0"
CONTROLLED_BLOCK_FOOTPRINT_MM = (900.0, 450.0)
CONTROLLED_BLOCK_MIN_SIZE = CONTROLLED_BLOCK_FOOTPRINT_MM
PREVIEW_LAYER = "CODEX_PREVIEW"


def _controlled_block_footprint_mm(block_id: str = CONTROLLED_BLOCK_ID) -> tuple[float, float]:
    try:
        from core.block_engine.block_library import load_block_library, normalize_block

        for block in load_block_library().get("blocks", []):
            if isinstance(block, dict) and block.get("block_id") == block_id:
                normalized = normalize_block(block)
                footprint = normalized.get("footprint_2d", normalized.get("size", {}))
                if isinstance(footprint, dict):
                    return float(footprint["width"]), float(footprint["depth"])
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return CONTROLLED_BLOCK_FOOTPRINT_MM


def block_definition_failure(
    *,
    block_name: str,
    message: str,
    failure_category: str = "definition_missing",
) -> dict[str, Any]:
    return {
        "status": "definition_missing",
        "failure_category": failure_category,
        "block_name": block_name,
        "message": message,
    }


def block_definition_ready(*, block_name: str, source: str, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": "ready",
        "block_name": block_name,
        "source": source,
    }
    payload.update(extra)
    return payload


def block_insert_failure(
    *,
    block_name: str,
    message: str,
    failure_category: str = "insert_failed",
) -> dict[str, Any]:
    return {
        "status": "insert_failed",
        "failure_category": failure_category,
        "block_name": block_name,
        "message": message,
    }


class BlockAlphaInsertionError(RuntimeError):
    """Raised when controlled block insertion cannot proceed."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        super().__init__(str(payload.get("message", "block alpha insertion failed")))


class AutoCADBlockAlphaMixin:
    def _normalize_block_alpha_base_point(self, base_point: list[float | int]) -> list[float]:
        if not isinstance(base_point, list) or len(base_point) not in (2, 3):
            raise ValueError("insert_block_alpha requires base_point as two or three numeric values.")
        if not all(isinstance(value, (int, float)) for value in base_point):
            raise ValueError("insert_block_alpha requires base_point values to be numeric.")
        normalized = [float(value) for value in base_point]
        if len(normalized) == 2:
            normalized.append(0.0)
        return normalized

    def _delete_entity_safely(self, entity: object) -> None:
        try:
            delete = getattr(entity, "Delete")
            delete()
        except Exception:
            pass

    def _point_tuple(self, value: object) -> tuple[float, float, float] | None:
        try:
            items = list(value)  # type: ignore[arg-type]
        except TypeError:
            return None
        if len(items) < 2:
            return None
        try:
            x = float(items[0])
            y = float(items[1])
            z = float(items[2]) if len(items) > 2 else 0.0
        except (TypeError, ValueError):
            return None
        return (round(x, 3), round(y, 3), round(z, 3))

    def _block_record_entities(self, block_record: object) -> list[object] | None:
        try:
            count = int(getattr(block_record, "Count"))
            item = getattr(block_record, "Item")
            return [item(index) for index in range(count)]
        except Exception:
            try:
                return list(block_record)  # type: ignore[arg-type]
            except Exception:
                return None

    def _controlled_block_definition_failure(self, block_record: object, *, block_id: str) -> str:
        entities = self._block_record_entities(block_record)
        if entities is None:
            return "unable to inspect existing controlled block definition"
        if len(entities) != 4:
            return f"expected 4 line entities, got {len(entities)}"

        width, depth = _controlled_block_footprint_mm(block_id)
        expected_edges = {
            ((0.0, 0.0, 0.0), (round(width, 3), 0.0, 0.0)),
            ((round(width, 3), 0.0, 0.0), (round(width, 3), round(depth, 3), 0.0)),
            ((round(width, 3), round(depth, 3), 0.0), (0.0, round(depth, 3), 0.0)),
            ((0.0, round(depth, 3), 0.0), (0.0, 0.0, 0.0)),
        }
        actual_edges: set[tuple[tuple[float, float, float], tuple[float, float, float]]] = set()
        for entity in entities:
            object_name = str(getattr(entity, "ObjectName", "")).lower()
            if "line" not in object_name:
                return f"expected only line entities, got {getattr(entity, 'ObjectName', '')!r}"
            if str(getattr(entity, "Layer", "")) != CONTROLLED_BLOCK_DEFINITION_LAYER:
                return "controlled block definition entities must be on layer 0"
            start = self._point_tuple(getattr(entity, "StartPoint", None))
            end = self._point_tuple(getattr(entity, "EndPoint", None))
            if start is None or end is None:
                return "controlled block definition line endpoints are unreadable"
            actual_edges.add((start, end))
        if actual_edges != expected_edges:
            return f"controlled block definition footprint does not match {width:g}x{depth:g} origin rectangle"
        return ""

    def block_definition_exists(self, block_name: str) -> bool:
        try:
            self.doc.Blocks.Item(block_name)
            return True
        except Exception:
            return False

    def _create_minimal_controlled_block_definition(self, block_name: str, *, block_id: str) -> dict[str, Any]:
        """Create a tiny rectangle inside a new block table record (layer 0 only, no DWG save)."""

        width, depth = _controlled_block_footprint_mm(block_id)
        origin = self._point([0.0, 0.0, 0.0])
        try:
            block_record = self.doc.Blocks.Add(origin, block_name)
        except Exception as exc:
            return block_definition_failure(
                block_name=block_name,
                message=f"unable to create block table record: {exc}",
            )

        corners = [
            (0.0, 0.0, 0.0),
            (width, 0.0, 0.0),
            (width, depth, 0.0),
            (0.0, depth, 0.0),
        ]
        edges = [
            (corners[0], corners[1]),
            (corners[1], corners[2]),
            (corners[2], corners[3]),
            (corners[3], corners[0]),
        ]
        definition_handles: list[str] = []
        try:
            for start, end in edges:
                entity = block_record.AddLine(self._point(list(start)), self._point(list(end)))
                entity.Layer = CONTROLLED_BLOCK_DEFINITION_LAYER
                handle = self._handle(entity)
                if handle:
                    definition_handles.append(handle)
        except Exception as exc:
            self._delete_entity_safely(block_record)
            return block_definition_failure(
                block_name=block_name,
                message=f"unable to add minimal geometry to block definition: {exc}",
            )

        if not definition_handles:
            self._delete_entity_safely(block_record)
            return block_definition_failure(
                block_name=block_name,
                message="block definition was created but no geometry handles were returned",
            )

        return block_definition_ready(
            block_name=block_name,
            source="created",
            definition_handles=definition_handles,
            definition_layer=CONTROLLED_BLOCK_DEFINITION_LAYER,
        )

    def ensure_controlled_block_definition(
        self,
        block_name: str | None = None,
        *,
        allow_create: bool = True,
    ) -> dict[str, Any]:
        """Resolve a controlled test block: reuse existing definition or create minimal geometry."""

        resolved_name = str(block_name or CONTROLLED_BLOCK_NAME).strip()
        if not resolved_name:
            return block_definition_failure(
                block_name=CONTROLLED_BLOCK_NAME,
                message="block_name is required",
            )
        allowed_name_to_id = {name: block_id for block_id, name in CONTROLLED_BLOCK_ALLOWLIST.items()}
        block_id = allowed_name_to_id.get(resolved_name)
        if block_id is None:
            return block_definition_failure(
                block_name=resolved_name,
                message="block alpha only allows controlled block definitions: "
                + ", ".join(sorted(CONTROLLED_BLOCK_ALLOWLIST.values())),
                failure_category="controlled_block_mismatch",
            )

        try:
            existing_record = self.doc.Blocks.Item(resolved_name)
        except Exception:
            existing_record = None

        if existing_record is not None:
            definition_failure = self._controlled_block_definition_failure(existing_record, block_id=block_id)
            if definition_failure:
                return block_definition_failure(
                    block_name=resolved_name,
                    message=definition_failure,
                    failure_category="definition_mismatch",
                )
            return block_definition_ready(block_name=resolved_name, source="existing")

        if not allow_create:
            return block_definition_failure(
                block_name=resolved_name,
                message=f"block definition '{resolved_name}' is not present in the active DWG",
            )

        return self._create_minimal_controlled_block_definition(resolved_name, block_id=block_id)

    def insert_block_alpha(
        self,
        *,
        block_id: str,
        block_name: str,
        base_point: list[float | int],
        rotation: float | int = 0,
        scale: list[float | int] | None = None,
        layer: str | None = None,
        attributes: dict[str, Any] | None = None,
        cad_identity: dict[str, Any] | None = None,
        **_: object,
    ) -> dict[str, Any]:
        """Insert a controlled block reference into ModelSpace on CODEX_PREVIEW only."""

        resolved_block_id = str(block_id or "").strip()
        resolved_name = str(block_name or "").strip()
        if resolved_block_id not in CONTROLLED_BLOCK_ALLOWLIST:
            raise ValueError(
                "insert_block_alpha only allows controlled test block ids: "
                + ", ".join(sorted(CONTROLLED_BLOCK_ALLOWLIST))
            )
        if not resolved_name:
            raise BlockAlphaInsertionError(
                block_insert_failure(block_name=CONTROLLED_BLOCK_NAME, message="block_name is required"),
            )
        expected_block_name = CONTROLLED_BLOCK_ALLOWLIST[resolved_block_id]
        if resolved_name != expected_block_name:
            raise ValueError(
                f"insert_block_alpha block_id={resolved_block_id} requires block_name={expected_block_name}."
            )

        if layer != PREVIEW_LAYER:
            raise ValueError(f"insert_block_alpha only allows layer={PREVIEW_LAYER}.")

        resolved_scale = list(scale or [1, 1, 1])
        if len(resolved_scale) != 3 or not all(isinstance(value, (int, float)) for value in resolved_scale):
            raise ValueError("insert_block_alpha requires scale as three numeric values.")
        if not all(value > 0 for value in resolved_scale):
            raise ValueError("insert_block_alpha requires positive scale values.")
        if not (resolved_scale[0] == resolved_scale[1] == resolved_scale[2]):
            raise ValueError("insert_block_alpha alpha only supports uniform scale.")
        insertion_values = self._normalize_block_alpha_base_point(base_point)

        if not isinstance(rotation, (int, float)):
            raise ValueError("insert_block_alpha requires numeric rotation.")

        if attributes:
            raise BlockAlphaInsertionError(
                block_insert_failure(
                    block_name=resolved_name,
                    message="block attributes are deferred in block alpha",
                    failure_category="attribute_unverified",
                ),
            )

        definition_result = self.ensure_controlled_block_definition(expected_block_name)
        if definition_result.get("status") != "ready":
            raise BlockAlphaInsertionError(
                block_insert_failure(
                    block_name=resolved_name,
                    message=str(definition_result.get("message", "block definition unavailable")),
                    failure_category=str(definition_result.get("failure_category", "definition_missing")),
                ),
            )

        self.ensure_layer(PREVIEW_LAYER)
        insertion_point = self._point(insertion_values)
        xscale = yscale = zscale = float(resolved_scale[0])
        rotation_rad = math.radians(float(rotation))

        try:
            entity = self.model_space.InsertBlock(
                insertion_point,
                resolved_name,
                xscale,
                yscale,
                zscale,
                rotation_rad,
            )
        except Exception as exc:
            raise BlockAlphaInsertionError(
                block_insert_failure(
                    block_name=resolved_name,
                    message=f"InsertBlock failed: {exc}",
                ),
            ) from exc

        try:
            self._apply_common(entity, layer=PREVIEW_LAYER)
            handle = self._handle(entity)
        except Exception as exc:
            self._delete_entity_safely(entity)
            raise BlockAlphaInsertionError(
                block_insert_failure(
                    block_name=resolved_name,
                    message=f"post-insert validation failed: {exc}",
                    failure_category="partial_write_rolled_back",
                ),
            ) from exc
        if not handle:
            self._delete_entity_safely(entity)
            raise BlockAlphaInsertionError(
                block_insert_failure(
                    block_name=resolved_name,
                    message="InsertBlock returned no entity handle",
                    failure_category="partial_write_rolled_back",
                ),
            )

        return {
            "handle": handle,
            "block_id": resolved_block_id,
            "block_name": resolved_name,
            "insertion_point": insertion_values,
            "rotation": float(rotation),
            "scale": resolved_scale,
            "layer": PREVIEW_LAYER,
            "block_definition_source": definition_result.get("source"),
            "geometry_accuracy": "not_verified_without_cad_readback",
        }
