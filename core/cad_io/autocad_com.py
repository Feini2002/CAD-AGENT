"""AutoCAD COM driver for low-risk preview drawing.

Keep natural-language understanding out of this layer. It only receives
explicit geometry from execute_plan.py and writes entities to the active CAD
document.
"""

from __future__ import annotations

from typing import Any


ACI_COLORS = {
    "red": 1,
    "yellow": 2,
    "green": 3,
    "cyan": 4,
    "blue": 5,
    "magenta": 6,
    "white": 7,
}


def driver_status() -> str:
    return "autocad_com driver ready"


class AutoCADComDriver:
    def __init__(self, *, connect_existing_only: bool = False) -> None:
        try:
            import win32com.client
        except ImportError as exc:
            raise RuntimeError("pywin32 is required for AutoCAD COM drawing.") from exc

        self._win32com = win32com.client
        try:
            self.app = win32com.client.GetActiveObject("AutoCAD.Application")
        except Exception:
            if connect_existing_only:
                raise RuntimeError("No active AutoCAD.Application instance is available.")
            self.app = win32com.client.Dispatch("AutoCAD.Application")
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
            entity = self.model_space.AddLine(start, end)
            self._apply_common(entity, layer=layer, color=color)
            handle = self._handle(entity)
            if handle:
                handles.append(handle)
        return {"handles": handles}

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
        entity = self.model_space.AddText(text, tuple(position), height)
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
        entity = self.model_space.AddDimAligned(tuple(start_point), tuple(end_point), tuple(text_position))
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
