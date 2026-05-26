"""In-memory AutoCAD driver for non-CAD capability probe tests and beta rollups."""

from __future__ import annotations

from typing import Any

from core.cad_io.autocad_block_alpha import CONTROLLED_BLOCK_ID, CONTROLLED_BLOCK_NAME, PREVIEW_LAYER
from core.safety.write_guard import CadWriteGuard


class FakeCadEntity:
    def __init__(self, *, handle: str, object_name: str, layer: str, **attrs: object) -> None:
        self.Handle = handle
        self.ObjectName = object_name
        self.Layer = layer
        for name, value in attrs.items():
            setattr(self, name, value)


class FakeCadDriver:
    def __init__(
        self,
        *,
        missing_readback_handle: str | None = None,
        open_document_count: int = 1,
        write_guard: CadWriteGuard | None = None,
        preview_only: bool = True,
    ) -> None:
        self.doc = type(
            "Doc",
            (),
            {
                "Name": "sample-active.dwg",
                "FullName": r"C:\temp\sample-active.dwg",
            },
        )()
        self.app = type(
            "App",
            (),
            {
                "Documents": type("Documents", (), {"Count": open_document_count})(),
            },
        )()
        self.missing_readback_handle = missing_readback_handle
        self.entities: dict[str, FakeCadEntity] = {}
        self.layers: list[str] = []
        self.next_handle = 100
        self.write_guard = write_guard or CadWriteGuard(enabled=preview_only, preview_layer=PREVIEW_LAYER)

    def _guard_layer(self, layer: str) -> None:
        self.write_guard.assert_preview_layer_write(layer)

    def save_document(self) -> None:
        self.write_guard.assert_save_allowed()
        self.doc.Saved = True  # pragma: no cover - only reachable with explicit approval

    def overwrite_document(self) -> None:
        self.write_guard.assert_overwrite_allowed()

    def delete_entity_by_handle(self, handle: str) -> None:
        self.write_guard.assert_delete_allowed()
        self.entities.pop(handle, None)

    def ensure_layer(self, layer: str) -> None:
        self._guard_layer(layer)
        self.layers.append(layer)

    def _handle(self) -> str:
        self.next_handle += 1
        return f"H{self.next_handle}"

    def draw_rectangle(
        self,
        *,
        corner1: list[float | int],
        corner2: list[float | int],
        layer: str,
        **_: object,
    ) -> dict[str, list[str]]:
        self._guard_layer(layer)
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
        **_: object,
    ) -> dict[str, str]:
        self._guard_layer(layer)
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
        **_: object,
    ) -> dict[str, str]:
        self._guard_layer(layer)
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
        **_: object,
    ) -> dict[str, str]:
        self._guard_layer(layer)
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
        **_: object,
    ) -> dict[str, str]:
        self._guard_layer(layer)
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

    def draw_text(
        self,
        *,
        text: str,
        position: list[float | int],
        layer: str,
        **_: object,
    ) -> dict[str, str]:
        self._guard_layer(layer)
        handle = self._handle()
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbText",
            layer=layer,
            TextString=text,
            InsertionPoint=position,
        )
        return {"handle": handle}

    def add_dimension(self, *, layer: str, **_: object) -> dict[str, str]:
        self._guard_layer(layer)
        handle = self._handle()
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbAlignedDimension",
            layer=layer,
        )
        return {"handle": handle}

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
        **_: object,
    ) -> dict[str, Any]:
        if str(block_id).strip() != CONTROLLED_BLOCK_ID:
            raise ValueError(f"insert_block_alpha only allows block_id={CONTROLLED_BLOCK_ID}.")
        if str(block_name).strip() != CONTROLLED_BLOCK_NAME:
            raise ValueError(f"insert_block_alpha only allows block_name={CONTROLLED_BLOCK_NAME}.")
        if layer != PREVIEW_LAYER:
            raise ValueError(f"insert_block_alpha only allows layer={PREVIEW_LAYER}.")
        if attributes:
            raise ValueError("block attributes are deferred in block alpha")
        resolved_scale = list(scale or [1, 1, 1])
        if len(resolved_scale) != 3 or not all(isinstance(value, (int, float)) for value in resolved_scale):
            raise ValueError("insert_block_alpha requires scale as three numeric values.")
        if not all(value > 0 for value in resolved_scale):
            raise ValueError("insert_block_alpha requires positive scale values.")
        if not (resolved_scale[0] == resolved_scale[1] == resolved_scale[2]):
            raise ValueError("insert_block_alpha alpha only supports uniform scale.")

        self.ensure_layer(PREVIEW_LAYER)
        handle = self._handle()
        insertion_point = [float(value) for value in base_point[:3]]
        if len(insertion_point) == 2:
            insertion_point.append(0.0)
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbBlockReference",
            layer=PREVIEW_LAYER,
            Name=CONTROLLED_BLOCK_NAME,
            InsertionPoint=insertion_point,
            Rotation=float(rotation),
            ScaleFactor=resolved_scale[0],
        )
        return {
            "handle": handle,
            "block_id": CONTROLLED_BLOCK_ID,
            "block_name": CONTROLLED_BLOCK_NAME,
            "insertion_point": insertion_point,
            "rotation": float(rotation),
            "scale": resolved_scale,
            "layer": PREVIEW_LAYER,
            "block_definition_source": "fake",
            "geometry_accuracy": "not_verified_without_cad_readback",
        }

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
            entity = self.entities[handle]
            normalized = normalize_com_entity(entity)
            if layer is None or normalized["layer"] == layer:
                entities.append(normalized)
        return entities
