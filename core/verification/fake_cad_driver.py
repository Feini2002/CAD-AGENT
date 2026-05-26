"""In-memory AutoCAD driver for non-CAD capability probe tests and beta rollups."""

from __future__ import annotations

from typing import Any


class FakeCadEntity:
    def __init__(self, *, handle: str, object_name: str, layer: str, **attrs: object) -> None:
        self.Handle = handle
        self.ObjectName = object_name
        self.Layer = layer
        for name, value in attrs.items():
            setattr(self, name, value)


class FakeCadDriver:
    def __init__(self, *, missing_readback_handle: str | None = None) -> None:
        self.doc = type("Doc", (), {"Name": "sample-active.dwg"})()
        self.missing_readback_handle = missing_readback_handle
        self.entities: dict[str, FakeCadEntity] = {}
        self.layers: list[str] = []
        self.next_handle = 100

    def ensure_layer(self, layer: str) -> None:
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
        handle = self._handle()
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbAlignedDimension",
            layer=layer,
        )
        return {"handle": handle}

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
