"""AutoCAD COM driver for low-risk preview drawing.

Keep natural-language understanding out of this layer. It only receives
explicit geometry from execute_plan.py and writes entities to the active CAD
document.
"""

from __future__ import annotations

import math
from typing import Any

from core.cad_io.autocad_block_alpha import (
    CONTROLLED_BLOCK_DEFINITION_LAYER,
    CONTROLLED_BLOCK_ID,
    CONTROLLED_BLOCK_MIN_SIZE,
    CONTROLLED_BLOCK_NAME,
    PREVIEW_LAYER,
    AutoCADBlockAlphaMixin,
    BlockAlphaInsertionError,
    _controlled_block_footprint_mm,
    block_definition_failure,
    block_definition_ready,
    block_insert_failure,
)


ACI_COLORS = {
    "red": 1,
    "yellow": 2,
    "green": 3,
    "cyan": 4,
    "blue": 5,
    "magenta": 6,
    "white": 7,
}


AUTOCAD_PROG_IDS = (
    "AutoCAD.Application",
    "AutoCAD.Application.25.1",
    "AutoCAD.Application.25",
    "AutoCAD.Application.24.3",
    "AutoCAD.Application.24.2",
    "AutoCAD.Application.24.1",
    "AutoCAD.Application.24",
    "AutoCAD.Application.23.1",
    "AutoCAD.Application.23",
)


def driver_status() -> str:
    return "autocad_com driver ready"


class AutoCADComDriver(AutoCADBlockAlphaMixin):
    def __init__(self, *, connect_existing_only: bool = False) -> None:
        try:
            import win32com.client
            import pythoncom
        except ImportError as exc:
            raise RuntimeError("pywin32 is required for AutoCAD COM drawing.") from exc

        self._win32com = win32com.client
        self._pythoncom = pythoncom
        self.app = None
        active_errors: list[str] = []
        for prog_id in AUTOCAD_PROG_IDS:
            try:
                self.app = win32com.client.GetActiveObject(prog_id)
                break
            except Exception as exc:
                active_errors.append(f"{prog_id}: {exc}")
        if self.app is None:
            if connect_existing_only:
                detail = " | ".join(active_errors)
                raise RuntimeError(f"No active AutoCAD.Application instance is available. COM detail: {detail}")
            dispatch_errors: list[str] = []
            for prog_id in AUTOCAD_PROG_IDS:
                try:
                    self.app = win32com.client.Dispatch(prog_id)
                    break
                except Exception as exc:
                    dispatch_errors.append(f"{prog_id}: {exc}")
            if self.app is None:
                detail = " | ".join(dispatch_errors)
                raise RuntimeError(f"Unable to dispatch AutoCAD.Application. COM detail: {detail}")
        self.doc = self.app.ActiveDocument
        self.model_space = self.doc.ModelSpace

    def ensure_layer(self, layer: str) -> None:
        try:
            self.doc.Layers.Item(layer)
        except Exception:
            self.doc.Layers.Add(layer)

    def _apply_common(self, entity: Any, *, layer: str | None = None, color: str | None = None) -> None:
        if layer:
            self.ensure_layer(layer)
            entity.Layer = layer
        if color:
            color_value = ACI_COLORS.get(color.lower())
            if color_value is not None:
                entity.Color = color_value

    @staticmethod
    def _handle(entity: Any) -> str:
        return str(getattr(entity, "Handle", getattr(entity, "handle", "")))

    def _point(self, values: list[float | int]) -> Any:
        if len(values) != 3:
            raise ValueError("AutoCAD COM points must contain exactly three coordinates.")
        point = tuple(float(value) for value in values)
        return self._win32com.VARIANT(self._pythoncom.VT_ARRAY | self._pythoncom.VT_R8, point)

    def _point2d_array(self, points: list[list[float | int]]) -> Any:
        if len(points) < 2:
            raise ValueError("AutoCAD COM polylines require at least two points.")
        coordinates: list[float] = []
        for point in points:
            if len(point) < 2:
                raise ValueError("Polyline points must contain at least x and y coordinates.")
            coordinates.extend([float(point[0]), float(point[1])])
        return self._win32com.VARIANT(self._pythoncom.VT_ARRAY | self._pythoncom.VT_R8, tuple(coordinates))

    def draw_line(
        self,
        *,
        start_point: list[float | int],
        end_point: list[float | int],
        layer: str | None = None,
        color: str | None = None,
        **_: object,
    ) -> dict[str, str]:
        entity = self.model_space.AddLine(self._point(start_point), self._point(end_point))
        self._apply_common(entity, layer=layer, color=color)
        return {"handle": self._handle(entity)}

    def draw_rectangle(
        self,
        *,
        corner1: list[float | int],
        corner2: list[float | int],
        layer: str | None = None,
        color: str | None = None,
        **_: object,
    ) -> dict[str, list[str]]:
        x1, y1, z1 = corner1
        x2, y2, _z2 = corner2
        points = [
            ((x1, y1, z1), (x2, y1, z1)),
            ((x2, y1, z1), (x2, y2, z1)),
            ((x2, y2, z1), (x1, y2, z1)),
            ((x1, y2, z1), (x1, y1, z1)),
        ]
        handles: list[str] = []
        for start, end in points:
            entity = self.model_space.AddLine(self._point(list(start)), self._point(list(end)))
            self._apply_common(entity, layer=layer, color=color)
            handle = self._handle(entity)
            if handle:
                handles.append(handle)
        return {"handles": handles}

    def draw_circle(
        self,
        *,
        center: list[float | int],
        radius: float | int,
        layer: str | None = None,
        color: str | None = None,
        **_: object,
    ) -> dict[str, str]:
        entity = self.model_space.AddCircle(self._point(center), float(radius))
        self._apply_common(entity, layer=layer, color=color)
        return {"handle": self._handle(entity)}

    def draw_arc(
        self,
        *,
        center: list[float | int],
        radius: float | int,
        start_angle: float | int,
        end_angle: float | int,
        layer: str | None = None,
        color: str | None = None,
        **_: object,
    ) -> dict[str, str]:
        entity = self.model_space.AddArc(
            self._point(center),
            float(radius),
            math.radians(float(start_angle)),
            math.radians(float(end_angle)),
        )
        self._apply_common(entity, layer=layer, color=color)
        return {"handle": self._handle(entity)}

    def draw_polyline(
        self,
        *,
        points: list[list[float | int]],
        closed: bool = False,
        layer: str | None = None,
        color: str | None = None,
        **_: object,
    ) -> dict[str, str]:
        entity = self.model_space.AddLightWeightPolyline(self._point2d_array(points))
        entity.Closed = bool(closed)
        self._apply_common(entity, layer=layer, color=color)
        return {"handle": self._handle(entity)}

    def draw_text(
        self,
        *,
        text: str,
        position: list[float | int],
        height: float | int,
        layer: str | None = None,
        color: str | None = None,
        rotation: float | int = 0,
        **_: object,
    ) -> dict[str, str]:
        entity = self.model_space.AddText(text, self._point(position), height)
        entity.Rotation = rotation
        self._apply_common(entity, layer=layer, color=color)
        return {"handle": self._handle(entity)}

    def add_dimension(
        self,
        *,
        start_point: list[float | int],
        end_point: list[float | int],
        text_position: list[float | int] | None = None,
        layer: str | None = None,
        color: str | None = None,
        textheight: float | int | None = None,
        **_: object,
    ) -> dict[str, str]:
        if text_position is None:
            text_position = [
                (start_point[0] + end_point[0]) / 2,
                (start_point[1] + end_point[1]) / 2,
                start_point[2],
            ]
        entity = self.model_space.AddDimAligned(
            self._point(start_point),
            self._point(end_point),
            self._point(text_position),
        )
        if textheight is not None:
            entity.TextHeight = textheight
        self._apply_common(entity, layer=layer, color=color)
        return {"handle": self._handle(entity)}

    def snapshot_modelspace(self, *, layer: str | None = None) -> list[dict[str, object]]:
        from core.verification.inspect_dwg import normalize_com_entity

        entities: list[dict[str, object]] = []
        for entity in self.model_space:
            normalized = normalize_com_entity(entity)
            if layer and normalized.get("layer") != layer:
                continue
            entities.append(normalized)
        return entities

    def snapshot_handles(self, *, handles: list[str], layer: str | None = None) -> list[dict[str, object]]:
        from core.verification.inspect_dwg import normalize_com_entity

        entities: list[dict[str, object]] = []
        for handle in handles:
            try:
                entity = self.doc.HandleToObject(str(handle))
            except Exception:
                continue
            normalized = normalize_com_entity(entity)
            if layer and normalized.get("layer") != layer:
                continue
            entities.append(normalized)
        return entities

    @staticmethod
    def _bbox_from_entities(entities: list[dict[str, object]]) -> dict[str, list[float]] | None:
        xs: list[float] = []
        ys: list[float] = []
        for entity in entities:
            bbox = entity.get("bbox")
            if isinstance(bbox, dict):
                minimum = bbox.get("min")
                maximum = bbox.get("max")
                if isinstance(minimum, list) and isinstance(maximum, list) and len(minimum) >= 2 and len(maximum) >= 2:
                    xs.extend([float(minimum[0]), float(maximum[0])])
                    ys.extend([float(minimum[1]), float(maximum[1])])
                    continue
            for key in ("start_point", "end_point", "position", "center"):
                point = entity.get(key)
                if isinstance(point, list) and len(point) >= 2:
                    xs.append(float(point[0]))
                    ys.append(float(point[1]))
            points = entity.get("points")
            if isinstance(points, list):
                for point in points:
                    if isinstance(point, list) and len(point) >= 2:
                        xs.append(float(point[0]))
                        ys.append(float(point[1]))
        if not xs or not ys:
            return None
        return {"min": [min(xs), min(ys)], "max": [max(xs), max(ys)]}

    def zoom_to_bbox(self, bbox: dict[str, list[float]], *, padding_ratio: float = 0.15) -> dict[str, object]:
        minimum = bbox.get("min", [])
        maximum = bbox.get("max", [])
        if len(minimum) < 2 or len(maximum) < 2:
            raise ValueError("bbox must contain min and max xy coordinates.")
        min_x, min_y = float(minimum[0]), float(minimum[1])
        max_x, max_y = float(maximum[0]), float(maximum[1])
        width = max(max_x - min_x, 1.0)
        height = max(max_y - min_y, 1.0)
        pad_x = width * padding_ratio
        pad_y = height * padding_ratio
        p1 = [min_x - pad_x, min_y - pad_y, 0]
        p2 = [max_x + pad_x, max_y + pad_y, 0]
        self.app.ZoomWindow(self._point(p1), self._point(p2))
        return {"status": "zoomed_to_bbox", "bbox": {"min": p1[:2], "max": p2[:2]}}

    def zoom_to_handles(self, *, handles: list[str], layer: str | None = None, padding_ratio: float = 0.15) -> dict[str, object]:
        entities = self.snapshot_handles(handles=handles, layer=layer)
        bbox = self._bbox_from_entities(entities)
        if bbox is None:
            self.app.ZoomExtents()
            return {"status": "zoom_extents", "reason": "created handle bbox unavailable", "handle_count": len(handles)}
        result = self.zoom_to_bbox(bbox, padding_ratio=padding_ratio)
        result["handle_count"] = len(handles)
        return result
