"""AutoCAD COM driver for low-risk preview drawing.

Keep natural-language understanding out of this layer. It only receives
explicit geometry from execute_plan.py and writes entities to the active CAD
document.
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path
from typing import Any

from core.cad_io.autocad_block_alpha import (
    CONTROLLED_BLOCK_DEFINITION_LAYER,
    CONTROLLED_BLOCK_ID,
    CONTROLLED_BLOCK_MIN_SIZE,
    CONTROLLED_BLOCK_NAME,
    PREVIEW_LAYER,
    SECOND_CONTROLLED_BLOCK_NAME,
    AutoCADBlockAlphaMixin,
    BlockAlphaInsertionError,
    _controlled_block_footprint_mm,
    block_definition_failure,
    block_definition_ready,
    block_insert_failure,
)
from core.cad_io.preview_write_guard_mixin import PreviewWriteGuardMixin
from core.safety.write_guard import CadWriteGuardViolation


ACI_COLORS = {
    "red": 1,
    "yellow": 2,
    "green": 3,
    "cyan": 4,
    "blue": 5,
    "magenta": 6,
    "white": 7,
}

AUTOCAD_LINEWEIGHTS = (
    0,
    5,
    9,
    13,
    15,
    18,
    20,
    25,
    30,
    35,
    40,
    50,
    53,
    60,
    70,
    80,
    90,
    100,
    106,
    120,
    140,
    158,
    200,
    211,
)


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

AUTOCAD_ROT_MARKERS = ("autocad", "acad", ".dwg")


class AutoCADAttachError(RuntimeError):
    """Raised when an existing AutoCAD instance cannot be attached safely."""

    def __init__(self, message: str, *, diagnostics: dict[str, Any]) -> None:
        super().__init__(message)
        self.diagnostics = diagnostics


def _autocad_process_running() -> bool:
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq acad.exe"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:
        result = None
    if result is not None and "acad.exe" in result.stdout.lower():
        return True
    try:
        fallback = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-Process -Name acad -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty ProcessName",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:
        return False
    return "acad" in fallback.stdout.lower()


def driver_status() -> str:
    return "autocad_com driver ready"


def _stringify_error(exc: Exception) -> str:
    return f"{type(exc).__name__}: {exc}"


def _com_text(value: Any) -> str:
    try:
        return str(value or "")
    except Exception:
        return ""


def _get_attr(value: Any, attr: str) -> Any:
    try:
        return getattr(value, attr)
    except Exception:
        return None


def _object_identity_text(*, display_name: str, candidate: Any, app: Any | None, doc: Any | None) -> str:
    parts = [display_name]
    for obj in (candidate, app, doc):
        if obj is None:
            continue
        for attr in ("Name", "name", "FullName", "fullName", "Caption", "caption"):
            parts.append(_com_text(_get_attr(obj, attr)))
    return " ".join(part for part in parts if part)


def _looks_autocad_identity(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in AUTOCAD_ROT_MARKERS)


def _coerce_autocad_application(candidate: Any, *, display_name: str = "") -> tuple[Any | None, str]:
    doc = _get_attr(candidate, "ActiveDocument")
    if doc is not None:
        identity = _object_identity_text(display_name=display_name, candidate=candidate, app=candidate, doc=doc)
        if _looks_autocad_identity(identity) or display_name in {"__get_active_object__", "__get_object__"}:
            return candidate, "application"
        return None, f"application_like_candidate_identity_not_autocad:{identity[:180]}"

    app = _get_attr(candidate, "Application")
    if app is not None:
        app_doc = _get_attr(app, "ActiveDocument")
        identity = _object_identity_text(display_name=display_name, candidate=candidate, app=app, doc=app_doc)
        if app_doc is not None and _looks_autocad_identity(identity):
            return app, "document_application"
        return None, f"document_like_candidate_identity_not_autocad:{identity[:180]}"

    identity = _object_identity_text(display_name=display_name, candidate=candidate, app=None, doc=None)
    return None, f"candidate_lacks_autocad_application_shape:{identity[:180]}"


def _dispatch_rot_object(win32com_client: Any, pythoncom: Any, raw_object: Any) -> tuple[Any, str]:
    dispatch = _get_attr(win32com_client, "Dispatch")
    if callable(dispatch):
        try:
            return dispatch(raw_object), "Dispatch(raw_rot_object)"
        except Exception:
            pass
    query_interface = _get_attr(raw_object, "QueryInterface")
    iid_dispatch = _get_attr(pythoncom, "IID_IDispatch")
    if callable(query_interface) and iid_dispatch is not None and callable(dispatch):
        return dispatch(query_interface(iid_dispatch)), "Dispatch(QueryInterface(IID_IDispatch))"
    return raw_object, "raw_rot_object"


def _attach_via_running_object_table(
    *,
    win32com_client: Any,
    pythoncom: Any,
    attempts: list[str],
) -> tuple[Any | None, str | None]:
    get_rot = _get_attr(pythoncom, "GetRunningObjectTable")
    create_bind_ctx = _get_attr(pythoncom, "CreateBindCtx")
    if not callable(get_rot) or not callable(create_bind_ctx):
        attempts.append("ROT: pythoncom Running Object Table APIs unavailable")
        return None, None
    try:
        rot = get_rot()
        enum = rot.EnumRunning()
        bind_ctx = create_bind_ctx(0)
    except Exception as exc:
        attempts.append(f"ROT init: {_stringify_error(exc)}")
        return None, None

    inspected = 0
    while True:
        try:
            monikers = enum.Next(1)
        except Exception as exc:
            attempts.append(f"ROT enum: {_stringify_error(exc)}")
            break
        if not monikers:
            break
        moniker = monikers[0]
        inspected += 1
        try:
            display_name = str(moniker.GetDisplayName(bind_ctx, None) or "")
        except Exception as exc:
            display_name = ""
            attempts.append(f"ROT[{inspected}] display_name: {_stringify_error(exc)}")
        try:
            raw_object = rot.GetObject(moniker)
            candidate, dispatch_method = _dispatch_rot_object(win32com_client, pythoncom, raw_object)
            app, role = _coerce_autocad_application(candidate, display_name=display_name)
            if app is not None:
                attempts.append(f"ROT[{inspected}] {display_name or '<unnamed>'}: attached via {dispatch_method}/{role}")
                return app, display_name
            attempts.append(f"ROT[{inspected}] {display_name or '<unnamed>'}: {role}")
        except Exception as exc:
            attempts.append(f"ROT[{inspected}] {display_name or '<unnamed>'}: {_stringify_error(exc)}")
    attempts.append(f"ROT inspected={inspected}; no attachable AutoCAD application found")
    return None, None


def _classify_attach_failure(diagnostics: dict[str, Any]) -> str:
    process_running = bool(diagnostics.get("acadProcessRunning", False))
    attempts = " | ".join(str(item) for item in diagnostics.get("attempts", []))
    if not process_running:
        return "acad_process_not_running"
    if "ROT inspected=0" in attempts:
        return "acad_process_running_without_visible_rot_object"
    if "document_like_candidate_identity_not_autocad" in attempts or "application_like_candidate_identity_not_autocad" in attempts:
        return "acad_rot_candidates_rejected"
    return "autocad_active_object_unavailable"


def _attach_existing_autocad(
    *,
    win32com_client: Any,
    pythoncom: Any,
) -> tuple[Any | None, dict[str, Any]]:
    attempts: list[str] = []
    for prog_id in AUTOCAD_PROG_IDS:
        try:
            candidate = win32com_client.GetActiveObject(prog_id)
            app, role = _coerce_autocad_application(candidate, display_name="__get_active_object__")
            if app is not None:
                return app, {"method": "GetActiveObject", "progId": prog_id, "role": role, "attempts": attempts}
            attempts.append(f"{prog_id}: {role}")
        except Exception as exc:
            attempts.append(f"{prog_id}: {_stringify_error(exc)}")

    get_object = _get_attr(win32com_client, "GetObject")
    if callable(get_object):
        for prog_id in AUTOCAD_PROG_IDS:
            try:
                try:
                    candidate = get_object(Class=prog_id)
                except TypeError:
                    candidate = get_object(None, prog_id)
                app, role = _coerce_autocad_application(candidate, display_name="__get_object__")
                if app is not None:
                    return app, {"method": "GetObject", "progId": prog_id, "role": role, "attempts": attempts}
                attempts.append(f"GetObject {prog_id}: {role}")
            except Exception as exc:
                attempts.append(f"GetObject {prog_id}: {_stringify_error(exc)}")
    else:
        attempts.append("GetObject: win32com.client.GetObject unavailable")

    app, display_name = _attach_via_running_object_table(
        win32com_client=win32com_client,
        pythoncom=pythoncom,
        attempts=attempts,
    )
    if app is not None:
        return app, {"method": "RunningObjectTable", "displayName": display_name or "", "attempts": attempts}

    process_running = _autocad_process_running()
    diagnostics = {"method": "none", "acadProcessRunning": process_running, "attempts": attempts}
    diagnostics["blockerCode"] = _classify_attach_failure(diagnostics)
    return None, diagnostics


class AutoCADComDriver(AutoCADBlockAlphaMixin, PreviewWriteGuardMixin):
    def __init__(self, *, connect_existing_only: bool = False) -> None:
        try:
            import win32com.client
            import pythoncom
        except ImportError as exc:
            raise RuntimeError("pywin32 is required for AutoCAD COM drawing.") from exc

        self._win32com = win32com.client
        self._pythoncom = pythoncom
        try:
            pythoncom.CoInitialize()
        except Exception:
            pass
        self.app = None
        self.attach_diagnostics: dict[str, Any] = {}
        self.app, self.attach_diagnostics = _attach_existing_autocad(
            win32com_client=win32com.client,
            pythoncom=pythoncom,
        )
        if self.app is None:
            if connect_existing_only:
                process_running = bool(self.attach_diagnostics.get("acadProcessRunning", False))
                attempts = [str(item) for item in self.attach_diagnostics.get("attempts", [])]
                detail = " | ".join(attempts)
                detail = (
                    f"{detail} || acadProcessRunning={process_running}; "
                    "Dispatch fallback skipped because connect_existing_only=True; "
                    "ROT fallback attempted=True"
                )
                raise AutoCADAttachError(
                    f"No active AutoCAD.Application instance is available. COM detail: {detail}",
                    diagnostics=self.attach_diagnostics,
                )
            else:
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
        self._ensured_layers: set[str] = set()
        self._ensured_linetypes: set[str] = set()
        self._init_preview_write_guard(preview_layer=PREVIEW_LAYER)

    def ensure_layer(self, layer: str, *, layer_role: str = "preview") -> None:
        self._guard_preview_layer_write(layer, layer_role=layer_role)
        ensured_layers: set[str] = getattr(self, "_ensured_layers", set())
        if layer in ensured_layers:
            return
        try:
            self.doc.Layers.Item(layer)
        except Exception:
            self.doc.Layers.Add(layer)
        ensured_layers.add(layer)
        self._ensured_layers = ensured_layers

    def _apply_common(
        self,
        entity: Any,
        *,
        layer: str | None = None,
        color: str | None = None,
        lineweight: float | int | str | None = None,
        linetype: str | None = None,
        linetype_scale: float | int | None = None,
        layer_role: str = "preview",
    ) -> None:
        if layer:
            self._guard_preview_layer_write(layer, layer_role=layer_role)
            self.ensure_layer(layer, layer_role=layer_role)
            entity.Layer = layer
        if color:
            color_value = ACI_COLORS.get(color.lower())
            if color_value is not None:
                entity.Color = color_value
        if lineweight is not None:
            entity.Lineweight = self._lineweight_value(lineweight)
        if linetype:
            self.ensure_linetype(linetype)
            entity.Linetype = str(linetype)
        if linetype_scale is not None:
            entity.LinetypeScale = float(linetype_scale)

    def ensure_linetype(self, linetype: str) -> None:
        resolved = str(linetype).strip()
        if not resolved or resolved.upper() == "CONTINUOUS":
            return
        key = resolved.upper()
        ensured_linetypes: set[str] = getattr(self, "_ensured_linetypes", set())
        if key in ensured_linetypes:
            return
        try:
            self.doc.Linetypes.Item(resolved)
        except Exception:
            load_errors: list[str] = []
            for library in ("acadiso.lin", "acad.lin"):
                try:
                    self.doc.Linetypes.Load(resolved, library)
                    break
                except Exception as exc:
                    load_errors.append(f"{library}: {exc}")
            else:
                detail = " | ".join(load_errors)
                raise RuntimeError(f"Unable to load AutoCAD linetype {resolved!r}. COM detail: {detail}")
        ensured_linetypes.add(key)
        self._ensured_linetypes = ensured_linetypes

    @staticmethod
    def _lineweight_value(value: float | int | str) -> int:
        if isinstance(value, str):
            stripped = value.strip().lower().replace("mm", "")
            raw = float(stripped)
        else:
            raw = float(value)
        candidate = int(round(raw * 100)) if abs(raw) <= 2.11 else int(round(raw))
        if candidate in AUTOCAD_LINEWEIGHTS:
            return candidate
        return min(AUTOCAD_LINEWEIGHTS, key=lambda allowed: abs(allowed - candidate))

    @staticmethod
    def _handle(entity: Any) -> str:
        return str(getattr(entity, "Handle", getattr(entity, "handle", "")))

    @staticmethod
    def _handles_from_result(result: Any) -> list[str]:
        if not isinstance(result, dict):
            return []
        handles: list[str] = []
        for key in ("created_handles", "handles", "boundary_handles"):
            value = result.get(key)
            if isinstance(value, list):
                handles.extend(str(item) for item in value if item)
        handle = result.get("handle")
        if handle:
            handles.append(str(handle))
        return list(dict.fromkeys(handles))

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

    def _dispatch_array(self, values: list[Any]) -> Any:
        return self._win32com.VARIANT(
            self._pythoncom.VT_ARRAY | self._pythoncom.VT_DISPATCH,
            tuple(values),
        )

    def _execute_batch_operation(self, operation: dict[str, Any]) -> dict[str, Any]:
        method_name = str(operation.get("method") or "")
        if method_name.startswith("_") or not method_name:
            raise ValueError(f"Unsupported batch operation method: {method_name!r}")
        method = getattr(self, method_name)
        kwargs = operation.get("kwargs") or {}
        if not isinstance(kwargs, dict):
            raise ValueError("Batch operation kwargs must be an object.")
        return method(**kwargs)

    def execute_operation_batch(
        self,
        operations: list[dict[str, Any]],
        *,
        layer: str = PREVIEW_LAYER,
        batch_name: str = "",
    ) -> dict[str, Any]:
        self._guard_preview_layer_write(layer)
        self.ensure_layer(layer)
        operation_results: list[dict[str, Any]] = []
        created_handles: list[str] = []
        for index, operation in enumerate(operations):
            result = self._execute_batch_operation(operation)
            handles = self._handles_from_result(result)
            created_handles.extend(handles)
            operation_results.append(
                {
                    "index": index,
                    "operation": str(operation.get("operation") or operation.get("method") or ""),
                    "method": str(operation.get("method") or ""),
                    "handles": handles,
                    "result": result,
                }
            )
        return {
            "status": "pass",
            "batch_name": batch_name,
            "layer": layer,
            "operation_count": len(operations),
            "created_handles": list(dict.fromkeys(created_handles)),
            "operation_results": operation_results,
            "submit_unit": "foundation_item",
        }

    def draw_line(
        self,
        *,
        start_point: list[float | int],
        end_point: list[float | int],
        layer: str | None = None,
        color: str | None = None,
        lineweight: float | int | str | None = None,
        linetype: str | None = None,
        linetype_scale: float | int | None = None,
        layer_role: str = "preview",
        **_: object,
    ) -> dict[str, str]:
        self._guard_preview_layer_write(layer, layer_role=layer_role)
        entity = self.model_space.AddLine(self._point(start_point), self._point(end_point))
        self._apply_common(
            entity,
            layer=layer,
            color=color,
            lineweight=lineweight,
            linetype=linetype,
            linetype_scale=linetype_scale,
            layer_role=layer_role,
        )
        return {"handle": self._handle(entity)}

    def draw_rectangle(
        self,
        *,
        corner1: list[float | int],
        corner2: list[float | int],
        layer: str | None = None,
        color: str | None = None,
        lineweight: float | int | str | None = None,
        linetype: str | None = None,
        linetype_scale: float | int | None = None,
        layer_role: str = "preview",
        **_: object,
    ) -> dict[str, list[str]]:
        self._guard_preview_layer_write(layer, layer_role=layer_role)
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
            self._apply_common(
                entity,
                layer=layer,
                color=color,
                lineweight=lineweight,
                linetype=linetype,
                linetype_scale=linetype_scale,
                layer_role=layer_role,
            )
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
        lineweight: float | int | str | None = None,
        linetype: str | None = None,
        linetype_scale: float | int | None = None,
        layer_role: str = "preview",
        **_: object,
    ) -> dict[str, str]:
        self._guard_preview_layer_write(layer, layer_role=layer_role)
        entity = self.model_space.AddCircle(self._point(center), float(radius))
        self._apply_common(
            entity,
            layer=layer,
            color=color,
            lineweight=lineweight,
            linetype=linetype,
            linetype_scale=linetype_scale,
            layer_role=layer_role,
        )
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
        lineweight: float | int | str | None = None,
        linetype: str | None = None,
        linetype_scale: float | int | None = None,
        layer_role: str = "preview",
        **_: object,
    ) -> dict[str, str]:
        self._guard_preview_layer_write(layer, layer_role=layer_role)
        entity = self.model_space.AddArc(
            self._point(center),
            float(radius),
            math.radians(float(start_angle)),
            math.radians(float(end_angle)),
        )
        self._apply_common(
            entity,
            layer=layer,
            color=color,
            lineweight=lineweight,
            linetype=linetype,
            linetype_scale=linetype_scale,
            layer_role=layer_role,
        )
        return {"handle": self._handle(entity)}

    def draw_polyline(
        self,
        *,
        points: list[list[float | int]],
        closed: bool = False,
        layer: str | None = None,
        color: str | None = None,
        lineweight: float | int | str | None = None,
        linetype: str | None = None,
        linetype_scale: float | int | None = None,
        layer_role: str = "preview",
        **_: object,
    ) -> dict[str, str]:
        self._guard_preview_layer_write(layer, layer_role=layer_role)
        entity = self.model_space.AddLightWeightPolyline(self._point2d_array(points))
        entity.Closed = bool(closed)
        self._apply_common(
            entity,
            layer=layer,
            color=color,
            lineweight=lineweight,
            linetype=linetype,
            linetype_scale=linetype_scale,
            layer_role=layer_role,
        )
        return {"handle": self._handle(entity)}

    def draw_hatch(
        self,
        *,
        boundary_points: list[list[float | int]],
        pattern: str = "ANSI31",
        scale: float | int = 1.0,
        layer: str | None = None,
        layer_role: str = "preview",
        **_: object,
    ) -> dict[str, Any]:
        resolved_layer = layer or PREVIEW_LAYER
        self._guard_preview_layer_write(resolved_layer, layer_role=layer_role)

        if len(boundary_points) < 3:
            raise ValueError("Hatch boundary requires at least three points.")

        boundary = self.model_space.AddLightWeightPolyline(self._point2d_array(boundary_points))
        boundary.Closed = True
        self._apply_common(boundary, layer=resolved_layer, layer_role=layer_role)
        hatch = self.model_space.AddHatch(0, pattern, True)
        hatch.PatternScale = float(scale)
        hatch.AppendOuterLoop(self._dispatch_array([boundary]))
        hatch.Evaluate()
        self._apply_common(hatch, layer=resolved_layer, layer_role=layer_role)
        boundary_handle = self._handle(boundary)
        hatch_handle = self._handle(hatch)
        return {
            "handle": hatch_handle,
            "handles": [hatch_handle],
            "boundary_handles": [boundary_handle] if boundary_handle else [],
            "created_handles": [handle for handle in (boundary_handle, hatch_handle) if handle],
            "pattern": pattern,
            "scale": float(scale),
            "layer": resolved_layer,
        }

    def draw_text(
        self,
        *,
        text: str,
        position: list[float | int],
        height: float | int,
        layer: str | None = None,
        color: str | None = None,
        rotation: float | int = 0,
        layer_role: str = "preview",
        **_: object,
    ) -> dict[str, str]:
        self._guard_preview_layer_write(layer, layer_role=layer_role)
        entity = self.model_space.AddText(text, self._point(position), height)
        entity.Rotation = rotation
        self._apply_common(entity, layer=layer, color=color, layer_role=layer_role)
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
        text_override: str | None = None,
        layer_role: str = "preview",
        **_: object,
    ) -> dict[str, str]:
        self._guard_preview_layer_write(layer, layer_role=layer_role)
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
        if text_override is not None:
            entity.TextOverride = str(text_override)
        self._apply_common(entity, layer=layer, color=color, layer_role=layer_role)
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

    def copy_entities_from_dwg(
        self,
        *,
        source_dwg: str,
        source_spec: dict[str, Any],
        target_layer: str = PREVIEW_LAYER,
        base_point: list[float | int] | None = None,
    ) -> dict[str, object]:
        """Copy a system-library native asset from another DWG into the active DWG."""

        self.ensure_layer(target_layer)
        target_doc = self.doc
        target_path = ""
        try:
            target_path = str(target_doc.FullName)
        except Exception:
            target_path = str(getattr(target_doc, "Name", ""))
        source_path = Path(source_dwg).resolve()
        if not source_path.is_file():
            raise FileNotFoundError(f"system asset native DWG not found: {source_path}")

        source_doc = None
        opened_by_tool = False
        for document in self.app.Documents:
            try:
                if Path(str(document.FullName)).resolve() == source_path:
                    source_doc = document
                    break
            except Exception:
                continue
        if source_doc is None:
            try:
                source_doc = self.app.Documents.Open(str(source_path), True)
            except Exception:
                source_doc = self.app.Documents.Open(str(source_path))
            opened_by_tool = True

        mode = str(source_spec.get("mode", "")).strip().lower()
        copied_entities: list[Any] = []
        copy_method = ""
        before_handles = {self._handle(entity) for entity in target_doc.ModelSpace}
        try:
            if mode == "block":
                copied_entities = self._copy_or_insert_block_from_source(
                    source_doc=source_doc,
                    target_doc=target_doc,
                    block_name=str(source_spec.get("blockName", "")).strip(),
                    target_layer=target_layer,
                    base_point=base_point,
                )
                copy_method = "block_insert"
            else:
                source_entities = self._source_asset_entities(source_doc=source_doc, source_spec=source_spec)
                if not source_entities:
                    raise RuntimeError(f"system asset source selection is empty: {source_spec}")
                source_selected_count = len(source_entities)
                from core.verification.inspect_dwg import normalize_com_entity

                source_snapshots = [normalize_com_entity(entity) for entity in source_entities]
                try:
                    copied = source_doc.CopyObjects(self._dispatch_array(source_entities), target_doc.ModelSpace)
                    copied_entities = list(copied or [])
                except Exception:
                    copied_entities = []
                if copied_entities and not any(self._handle(entity) for entity in copied_entities):
                    copied_entities = []
                if copied_entities:
                    copy_method = "copyobjects_return"
                if not copied_entities:
                    copied_entities = self._new_entities_since(target_doc=target_doc, before_handles=before_handles)
                    if copied_entities:
                        copy_method = "copyobjects_handle_diff"
                if not copied_entities:
                    copied_entities = self._replay_source_entities(
                        target_doc=target_doc,
                        source_entities=source_snapshots,
                        target_layer=target_layer,
                        base_point=base_point,
                    )
                    if copied_entities:
                        copy_method = "readback_replay"
                for entity in copied_entities:
                    try:
                        entity.Layer = target_layer
                        entity.Update()
                    except Exception:
                        continue
                if base_point:
                    self._move_entities_min_to_base(copied_entities, base_point=base_point)
        finally:
            try:
                target_doc.Activate()
            except Exception:
                pass
            if opened_by_tool and source_doc is not None:
                try:
                    source_doc.Close(False)
                except Exception:
                    pass
            self.doc = target_doc
            self.model_space = target_doc.ModelSpace

        handles = [self._handle(entity) for entity in copied_entities if self._handle(entity)]
        try:
            target_doc.Regen(1)
        except Exception:
            pass
        return {
            "status": "copied",
            "sourceDwg": str(source_path),
            "targetDocument": target_path,
            "sourceSpec": source_spec,
            "sourceSelectedCount": locals().get("source_selected_count", 0),
            "copyMethod": copy_method,
            "targetLayer": target_layer,
            "basePoint": list(base_point or []),
            "created_handles": handles,
            "createdHandleCount": len(handles),
            "sourceOpenedByTool": opened_by_tool,
            "savedCurrentDwg": False,
        }

    def _new_entities_since(self, *, target_doc: Any, before_handles: set[str]) -> list[Any]:
        entities: list[Any] = []
        for entity in target_doc.ModelSpace:
            handle = self._handle(entity)
            if handle and handle not in before_handles:
                entities.append(entity)
        return entities

    def _replay_source_entities(
        self,
        *,
        target_doc: Any,
        source_entities: list[dict[str, Any]],
        target_layer: str,
        base_point: list[float | int] | None,
    ) -> list[Any]:
        target_doc.Activate()
        self.doc = target_doc
        self.model_space = target_doc.ModelSpace
        bbox = self._bbox_from_entities(source_entities)
        dx = 0.0
        dy = 0.0
        if base_point and bbox is not None:
            dx = float(base_point[0]) - float(bbox["min"][0])
            dy = float(base_point[1]) - float(bbox["min"][1])
        handles: list[str] = []
        for entity in source_entities:
            result = self._draw_replayed_entity(entity, target_layer=target_layer, dx=dx, dy=dy)
            if isinstance(result, dict):
                for key in ("created_handles", "handles", "boundary_handles"):
                    value = result.get(key)
                    if isinstance(value, list):
                        handles.extend(str(handle) for handle in value if handle)
                if result.get("handle"):
                    handles.append(str(result["handle"]))
        replayed: list[Any] = []
        for handle in dict.fromkeys(handles):
            try:
                replayed.append(target_doc.HandleToObject(handle))
            except Exception:
                continue
        return replayed

    def _draw_replayed_entity(self, entity: dict[str, Any], *, target_layer: str, dx: float, dy: float) -> dict[str, Any]:
        entity_type = str(entity.get("type", ""))
        style = self._style_from_snapshot(entity)
        if entity_type == "line":
            return self.draw_line(
                start_point=self._offset_point(entity.get("start_point"), dx=dx, dy=dy),
                end_point=self._offset_point(entity.get("end_point"), dx=dx, dy=dy),
                layer=target_layer,
                **style,
            )
        if entity_type == "text":
            return self.draw_text(
                text=str(entity.get("text", "")),
                position=self._offset_point(entity.get("position"), dx=dx, dy=dy),
                height=70,
                layer=target_layer,
                color=style.get("color"),
            )
        if entity_type == "circle":
            return self.draw_circle(
                center=self._offset_point(entity.get("center"), dx=dx, dy=dy),
                radius=float(entity.get("radius") or 0),
                layer=target_layer,
                **style,
            )
        if entity_type == "arc":
            return self.draw_arc(
                center=self._offset_point(entity.get("center"), dx=dx, dy=dy),
                radius=float(entity.get("radius") or 0),
                start_angle=float(entity.get("start_angle") or 0),
                end_angle=float(entity.get("end_angle") or 0),
                layer=target_layer,
                **style,
            )
        if entity_type == "polyline":
            points = [
                self._offset_point(point, dx=dx, dy=dy)
                for point in entity.get("points", [])
                if isinstance(point, list) and len(point) >= 2
            ]
            return self.draw_polyline(points=points, closed=bool(entity.get("closed")), layer=target_layer, **style)
        return {}

    @staticmethod
    def _offset_point(point: object, *, dx: float, dy: float) -> list[float]:
        if not isinstance(point, list) or len(point) < 2:
            return [dx, dy, 0.0]
        z = float(point[2]) if len(point) > 2 else 0.0
        return [float(point[0]) + dx, float(point[1]) + dy, z]

    @staticmethod
    def _style_from_snapshot(entity: dict[str, Any]) -> dict[str, Any]:
        style: dict[str, Any] = {}
        reverse_colors = {value: key for key, value in ACI_COLORS.items()}
        color = entity.get("color")
        if isinstance(color, int) and color in reverse_colors:
            style["color"] = reverse_colors[color]
        lineweight = entity.get("lineweight")
        if lineweight is not None:
            style["lineweight"] = lineweight
        linetype = str(entity.get("linetype") or "").strip()
        if linetype:
            style["linetype"] = linetype
        linetype_scale = entity.get("linetype_scale")
        if linetype_scale is not None:
            style["linetype_scale"] = linetype_scale
        return style

    def _source_asset_entities(self, *, source_doc: Any, source_spec: dict[str, Any]) -> list[Any]:
        mode = str(source_spec.get("mode", "")).strip().lower()
        if mode == "handles":
            entities: list[Any] = []
            for handle in source_spec.get("handles", []):
                try:
                    entities.append(source_doc.HandleToObject(str(handle)))
                except Exception:
                    continue
            return entities
        if mode == "layer":
            layer = str(source_spec.get("layer") or PREVIEW_LAYER)
            return [entity for entity in source_doc.ModelSpace if str(getattr(entity, "Layer", "")) == layer]
        raise ValueError(f"unsupported system asset source mode: {mode!r}")

    def _copy_or_insert_block_from_source(
        self,
        *,
        source_doc: Any,
        target_doc: Any,
        block_name: str,
        target_layer: str,
        base_point: list[float | int] | None,
    ) -> list[Any]:
        if not block_name:
            raise ValueError("block source mode requires blockName")
        try:
            target_doc.Blocks.Item(block_name)
        except Exception:
            source_block = source_doc.Blocks.Item(block_name)
            source_doc.CopyObjects(self._dispatch_array([source_block]), target_doc.Blocks)
        insertion = list(base_point or [0, 0, 0])
        while len(insertion) < 3:
            insertion.append(0)
        block = target_doc.ModelSpace.InsertBlock(self._point(insertion[:3]), block_name, 1.0, 1.0, 1.0, 0.0)
        block.Layer = target_layer
        try:
            block.Update()
        except Exception:
            pass
        return [block]

    def _move_entities_min_to_base(self, entities: list[Any], *, base_point: list[float | int]) -> None:
        xs: list[float] = []
        ys: list[float] = []
        for entity in entities:
            try:
                minimum, maximum = entity.GetBoundingBox()
                min_point = list(minimum)
                max_point = list(maximum)
            except Exception:
                continue
            if len(min_point) >= 2 and len(max_point) >= 2:
                xs.extend([float(min_point[0]), float(max_point[0])])
                ys.extend([float(min_point[1]), float(max_point[1])])
        if not xs or not ys:
            return
        target = list(base_point)
        while len(target) < 3:
            target.append(0)
        from_point = [min(xs), min(ys), 0]
        to_point = [float(target[0]), float(target[1]), float(target[2])]
        for entity in entities:
            try:
                entity.Move(self._point(from_point), self._point(to_point))
                entity.Update()
            except Exception:
                continue

    def get_current_viewport_bbox(self) -> dict[str, list[float]]:
        """Return the active model-space view bounds without changing the CAD view."""

        try:
            center = list(self.doc.GetVariable("VIEWCTR"))
            view_height = float(self.doc.GetVariable("VIEWSIZE"))
        except Exception as exc:
            raise RuntimeError(f"Unable to read active AutoCAD viewport variables: {exc}") from exc
        aspect = 16.0 / 9.0
        try:
            screen_size = list(self.doc.GetVariable("SCREENSIZE"))
            if len(screen_size) >= 2 and float(screen_size[1]) > 0:
                aspect = float(screen_size[0]) / float(screen_size[1])
        except Exception:
            pass
        if len(center) < 2 or view_height <= 0:
            raise RuntimeError("Active AutoCAD viewport variables are invalid.")
        view_width = view_height * aspect
        cx, cy = float(center[0]), float(center[1])
        return {
            "min": [cx - view_width / 2.0, cy - view_height / 2.0],
            "max": [cx + view_width / 2.0, cy + view_height / 2.0],
        }

    def get_selected_handles(self) -> list[str]:
        """Best-effort read of currently selected handles; returns [] when unavailable."""

        for attr_name in ("PickfirstSelectionSet", "ActiveSelectionSet"):
            try:
                selection = getattr(self.doc, attr_name)
            except Exception:
                continue
            handles: list[str] = []
            try:
                for entity in selection:
                    handle = self._handle(entity)
                    if handle:
                        handles.append(handle)
            except Exception:
                continue
            if handles:
                return handles
        return []

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

    def refresh_view(self) -> dict[str, object]:
        try:
            self.doc.Regen(1)
        except Exception as exc:
            return {"status": "failed", "method": "doc.Regen", "error": str(exc)}
        return {"status": "pass", "method": "doc.Regen"}

    def zoom_to_handles_extents(
        self,
        *,
        handles: list[str],
        padding_ratio: float = 0.15,
    ) -> dict[str, object]:
        """Zoom using COM GeometricExtents so block references and preview geometry align."""

        xs: list[float] = []
        ys: list[float] = []
        resolved = 0
        for handle in handles:
            try:
                entity = self.doc.HandleToObject(str(handle))
                bbox = entity.GetBoundingBox()
                minimum = list(bbox[0])
                maximum = list(bbox[1])
            except Exception:
                continue
            if len(minimum) < 2 or len(maximum) < 2:
                continue
            xs.extend([float(minimum[0]), float(maximum[0])])
            ys.extend([float(minimum[1]), float(maximum[1])])
            resolved += 1
        if not xs or not ys:
            return {
                "status": "focus_target_unavailable",
                "reason": "handle extents unavailable",
                "handle_count": len(handles),
                "resolved_count": resolved,
            }
        result = self.zoom_to_bbox({"min": [min(xs), min(ys)], "max": [max(xs), max(ys)]}, padding_ratio=padding_ratio)
        result["handle_count"] = len(handles)
        result["resolved_count"] = resolved
        result["method"] = "com_geometric_extents"
        return result

    def set_entity_color_by_handle(self, *, handle: str, color: str) -> None:
        entity = self.doc.HandleToObject(str(handle))
        layer = str(getattr(entity, "Layer", ""))
        self._guard_preview_layer_write(layer, layer_role="preview")
        color_value = ACI_COLORS.get(color.lower())
        if color_value is None:
            raise ValueError(f"Unsupported preview color: {color!r}")
        entity.Color = color_value

    def delete_entity_by_handle(self, handle: str) -> None:
        self.write_guard.assert_delete_allowed()
        try:
            entity = self.doc.HandleToObject(str(handle))
        except Exception as exc:
            raise ValueError(f"Unable to resolve handle for delete: {handle}") from exc
        layer = str(getattr(entity, "Layer", ""))
        if layer != PREVIEW_LAYER:
            message = f"Delete blocked: handle {handle!r} is on layer {layer!r}, not {PREVIEW_LAYER!r}"
            self.write_guard._record_block("delete", message)
            raise CadWriteGuardViolation(message)
        entity.Delete()
