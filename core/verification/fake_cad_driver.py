"""In-memory AutoCAD driver for non-CAD capability probe tests and beta rollups."""

from __future__ import annotations

from typing import Any

from core.cad_io.autocad_block_alpha import (
    CONTROLLED_BLOCK_ALLOWLIST,
    CONTROLLED_BLOCK_ID,
    CONTROLLED_BLOCK_NAME,
    PREVIEW_LAYER,
)
from core.cad_io.preview_write_guard_mixin import PreviewWriteGuardMixin
from core.safety.write_guard import CadWriteGuardViolation


class FakeCadEntity:
    def __init__(self, *, handle: str, object_name: str, layer: str, **attrs: object) -> None:
        self.Handle = handle
        self.ObjectName = object_name
        self.Layer = layer
        for name, value in attrs.items():
            setattr(self, name, value)


class _FakeDocuments:
    def __init__(self, count: int) -> None:
        self.Count = count


class _FakeApplication:
    def __init__(self, open_document_count: int) -> None:
        self.Documents = _FakeDocuments(open_document_count)


class FakeCadDriver(PreviewWriteGuardMixin):
    def __init__(
        self,
        *,
        missing_readback_handle: str | None = None,
        open_document_count: int = 1,
    ) -> None:
        self.doc = type("Doc", (), {"Name": "sample-active.dwg", "FullName": r"C:\sample-active.dwg"})()
        self.app = _FakeApplication(open_document_count)
        self.missing_readback_handle = missing_readback_handle
        self.entities: dict[str, FakeCadEntity] = {}
        self.layers: list[str] = []
        self.next_handle = 100
        self._init_preview_write_guard(preview_layer=PREVIEW_LAYER)
        self._block_definitions: set[str] = set()

    def _assert_layer(self, layer: str, *, layer_role: str = "preview") -> None:
        self._guard_preview_layer_write(layer, layer_role=layer_role)

    def _handle(self) -> str:
        self.next_handle += 1
        return f"H{self.next_handle}"

    def ensure_layer(self, layer: str, *, layer_role: str = "preview") -> None:
        self._assert_layer(layer, layer_role=layer_role)
        self.layers.append(layer)

    def ensure_controlled_block_definition(
        self,
        block_name: str | None = None,
        *,
        allow_create: bool = True,
    ) -> dict[str, Any]:
        resolved_name = str(block_name or CONTROLLED_BLOCK_NAME).strip()
        if resolved_name not in CONTROLLED_BLOCK_ALLOWLIST.values():
            return {
                "status": "failed",
                "block_name": resolved_name,
                "message": "block alpha only allows controlled block definitions",
                "failure_category": "controlled_block_mismatch",
            }
        if resolved_name in self._block_definitions:
            return {"status": "ready", "block_name": resolved_name, "source": "existing"}
        if not allow_create:
            return {
                "status": "failed",
                "block_name": resolved_name,
                "message": f"block definition '{resolved_name}' is not present in the active DWG",
                "failure_category": "definition_missing",
            }
        self._block_definitions.add(resolved_name)
        return {"status": "ready", "block_name": resolved_name, "source": "created"}

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
        resolved_layer = str(layer or PREVIEW_LAYER)
        self._assert_layer(resolved_layer)
        resolved_block_id = str(block_id).strip()
        if resolved_block_id not in CONTROLLED_BLOCK_ALLOWLIST:
            raise ValueError(
                "insert_block_alpha only allows controlled test block ids: "
                + ", ".join(sorted(CONTROLLED_BLOCK_ALLOWLIST))
            )
        expected_block_name = CONTROLLED_BLOCK_ALLOWLIST[resolved_block_id]
        if str(block_name).strip() != expected_block_name:
            raise ValueError(
                f"insert_block_alpha block_id={resolved_block_id} requires block_name={expected_block_name}."
            )
        if attributes:
            raise ValueError("block attributes are deferred in block alpha")

        definition_result = self.ensure_controlled_block_definition(expected_block_name)
        if definition_result.get("status") != "ready":
            return definition_result

        resolved_scale = list(scale or [1, 1, 1])
        uniform = float(resolved_scale[0])
        x0, y0 = float(base_point[0]), float(base_point[1])
        z0 = float(base_point[2]) if len(base_point) > 2 else 0.0
        width = 900.0 * uniform
        depth = 450.0 * uniform
        if resolved_block_id != CONTROLLED_BLOCK_ID:
            try:
                from core.block_engine.block_library import load_block_library, normalize_block

                for block in load_block_library().get("blocks", []):
                    if isinstance(block, dict) and block.get("block_id") == resolved_block_id:
                        normalized = normalize_block(block)
                        footprint = normalized.get("footprint_2d", {})
                        width = float(footprint["width"]) * uniform
                        depth = float(footprint["depth"]) * uniform
                        break
            except (OSError, ValueError, KeyError, TypeError):
                pass
        handle = self._handle()
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbBlockReference",
            layer=resolved_layer,
            block_name=expected_block_name,
            InsertionPoint=[x0, y0, z0],
            Rotation=float(rotation),
            Scale=[uniform, uniform, uniform],
            bbox={"min": [x0, y0], "max": [x0 + width, y0 + depth]},
        )
        return {"handle": handle, "handles": [handle]}

    def draw_rectangle(
        self,
        *,
        corner1: list[float | int],
        corner2: list[float | int],
        layer: str,
        layer_role: str = "preview",
        **_: object,
    ) -> dict[str, list[str]]:
        self._assert_layer(layer, layer_role=layer_role)
        x1, y1, z1 = corner1
        x2, y2, _z2 = corner2
        segments = [
            ([x1, y1, z1], [x2, y1, z1]),
            ([x2, y1, z1], [x2, y2, z1]),
            ([x2, y2, z1], [x1, y2, z1]),
            ([x1, y2, z1], [x1, y1, z1]),
        ]
        handles: list[str] = []
        for start, end in segments:
            handle = self._handle()
            self.entities[handle] = FakeCadEntity(
                handle=handle,
                object_name="AcDbLine",
                layer=layer,
                StartPoint=start,
                EndPoint=end,
            )
            handles.append(handle)
        return {"handles": handles}

    def draw_line(
        self,
        *,
        start_point: list[float | int],
        end_point: list[float | int],
        layer: str,
        layer_role: str = "preview",
        **_: object,
    ) -> dict[str, str]:
        self._assert_layer(layer, layer_role=layer_role)
        handle = self._handle()
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbLine",
            layer=layer,
            StartPoint=start_point,
            EndPoint=end_point,
        )
        return {"handle": handle}

    def draw_circle(
        self,
        *,
        center: list[float | int],
        radius: float | int,
        layer: str,
        layer_role: str = "preview",
        **_: object,
    ) -> dict[str, str]:
        self._assert_layer(layer, layer_role=layer_role)
        handle = self._handle()
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbCircle",
            layer=layer,
            Center=center,
            Radius=radius,
        )
        return {"handle": handle}

    def draw_arc(
        self,
        *,
        center: list[float | int],
        radius: float | int,
        start_angle: float | int,
        end_angle: float | int,
        layer: str,
        layer_role: str = "preview",
        **_: object,
    ) -> dict[str, str]:
        self._assert_layer(layer, layer_role=layer_role)
        handle = self._handle()
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbArc",
            layer=layer,
            Center=center,
            Radius=radius,
            StartAngle=start_angle,
            EndAngle=end_angle,
        )
        return {"handle": handle}

    def draw_polyline(
        self,
        *,
        points: list[list[float | int]],
        closed: bool,
        layer: str,
        layer_role: str = "preview",
        **_: object,
    ) -> dict[str, str]:
        self._assert_layer(layer, layer_role=layer_role)
        handle = self._handle()
        coordinates = [coordinate for point in points for coordinate in point[:2]]
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbPolyline",
            layer=layer,
            Coordinates=coordinates,
            Closed=closed,
        )
        return {"handle": handle}

    def draw_hatch(
        self,
        *,
        boundary_points: list[list[float | int]],
        pattern: str = "ANSI31",
        layer: str | None = None,
        layer_role: str = "preview",
        **_: object,
    ) -> dict[str, Any]:
        resolved_layer = layer or PREVIEW_LAYER
        self._assert_layer(resolved_layer, layer_role=layer_role)

        from core.verification.entity_level_evidence import build_hatch_deferred_entry

        write = {
            "boundary_points": [[float(point[0]), float(point[1])] for point in boundary_points],
            "pattern": pattern,
            "layer": resolved_layer,
            "layer_role": layer_role,
        }
        entry = build_hatch_deferred_entry(write)
        entry["created_handles"] = []
        entry["geometry_verified"] = False
        return entry

    def draw_text(
        self,
        *,
        text: str,
        position: list[float | int],
        layer: str,
        layer_role: str = "preview",
        **_: object,
    ) -> dict[str, str]:
        self._assert_layer(layer, layer_role=layer_role)
        handle = self._handle()
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbText",
            layer=layer,
            TextString=text,
            InsertionPoint=position,
        )
        return {"handle": handle}

    def add_dimension(self, *, layer: str, layer_role: str = "preview", **_: object) -> dict[str, str]:
        self._assert_layer(layer, layer_role=layer_role)
        handle = self._handle()
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbAlignedDimension",
            layer=layer,
        )
        return {"handle": handle}

    def set_entity_color_by_handle(self, *, handle: str, color: str) -> None:
        entity = self.entities.get(str(handle))
        if entity is None:
            raise ValueError(f"Unknown handle: {handle}")
        self._assert_layer(str(entity.Layer))
        entity.Color = color

    def delete_entity_by_handle(self, handle: str) -> None:
        self.write_guard.assert_delete_allowed()
        entity = self.entities.get(str(handle))
        if entity is None:
            raise ValueError(f"Unknown handle: {handle}")
        if str(entity.Layer) != PREVIEW_LAYER:
            message = f"Delete blocked: handle {handle!r} is not on {PREVIEW_LAYER!r}"
            self.write_guard._record_block("delete", message)
            raise CadWriteGuardViolation(message)
        del self.entities[str(handle)]

    def snapshot_modelspace(self, *, layer: str | None = None) -> list[dict[str, Any]]:
        from core.verification.inspect_dwg import normalize_com_entity

        entities = [normalize_com_entity(entity) for entity in self.entities.values()]
        if layer is not None:
            entities = [entity for entity in entities if entity.get("layer") == layer]
        return entities

    def snapshot_handles(self, *, handles: list[str], layer: str | None = None) -> list[dict[str, Any]]:
        from core.verification.inspect_dwg import normalize_com_entity

        entities = []
        for handle in handles:
            if handle == self.missing_readback_handle:
                continue
            entity = self.entities.get(handle)
            if entity is None:
                continue
            normalized = normalize_com_entity(entity)
            if layer is None or normalized["layer"] == layer:
                entities.append(normalized)
        return entities
