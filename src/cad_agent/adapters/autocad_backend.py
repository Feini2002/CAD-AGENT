from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal

from cad_agent.adapters.autocad_primitives import PREVIEW_LAYER, primitive_to_autocad_call
from cad_agent.domain.drawing import DrawingEntitySnapshot, DrawingSnapshot
from cad_agent.domain.patch import CadPatch, PatchOperation
from cad_agent.domain.receipt import EntityReadback, ExecutionReceipt


DriverFactory = Callable[[], Any]


@dataclass(frozen=True)
class _TransactionState:
    run_id: str
    transaction_id: str
    rollback_token: str
    created_handles: list[str]
    semantic_to_handles: dict[str, list[str]]


class AutoCadBackend:
    """Preview-only backend for an already-open AutoCAD document."""

    def __init__(
        self,
        *,
        driver: Any | None = None,
        driver_factory: DriverFactory | None = None,
        backend_name: str = "autocad-existing",
    ) -> None:
        if driver is not None and driver_factory is not None:
            raise ValueError("Pass either driver or driver_factory, not both.")
        self._driver = driver
        self._driver_factory = driver_factory
        self.backend_name = backend_name
        self._transactions: dict[str, _TransactionState] = {}

    @classmethod
    def from_existing_autocad(cls) -> "AutoCadBackend":
        return cls(driver_factory=_ExistingAutoCadDriver.connect)

    def inspect_document(self, *, run_id: str) -> DrawingSnapshot:
        driver = self._driver_instance()
        snapshots = _snapshot_modelspace(driver)
        return DrawingSnapshot(
            schema_version="drawing-snapshot/v1",
            run_id=run_id,
            document_id=_document_id(driver),
            units="mm",
            current_space="model",
            active_layer=PREVIEW_LAYER,
            saved=None,
            target_region=None,
            nearby_entities=[_drawing_entity_from_snapshot(item) for item in snapshots],
            snapshot_hash=f"autocad-existing:{len(snapshots)}:{_document_id(driver)}",
        )

    def apply_patch(self, patch: CadPatch) -> ExecutionReceipt:
        if patch.transaction_id in self._transactions:
            return self._receipt(
                patch=patch,
                status="blocked",
                semantic_to_handles={},
                created_handles=[],
                entities=[],
                rollback_token=None,
                errors=["duplicate_transaction_id"],
            )
        if patch.target_layer != PREVIEW_LAYER or patch.save_current_dwg is not False:
            return self._receipt(
                patch=patch,
                status="blocked",
                semantic_to_handles={},
                created_handles=[],
                entities=[],
                rollback_token=None,
                errors=["preview_only_contract_violation"],
            )

        driver = self._driver_instance()
        _ensure_preview_layer(driver)
        created_handles: list[str] = []
        semantic_to_handles: dict[str, list[str]] = {}
        errors: list[str] = []
        status: Literal["succeeded", "blocked", "failed"] = "succeeded"

        for operation in patch.operations:
            if operation.action != "create":
                status = "blocked"
                errors.append(f"unsupported_operation:{operation.action}")
                break
            operation_status = self._apply_create_operation(driver, operation)
            created_handles.extend(operation_status["handles"])
            if operation_status["handles"]:
                semantic_to_handles.setdefault(operation.semantic_object_id, []).extend(operation_status["handles"])
            errors.extend(operation_status["errors"])
            if operation_status["errors"]:
                status = "failed"
                break

        entities = _readback_handles(driver, created_handles)
        readback_handles = {entity.handle for entity in entities}
        missing_handles = [handle for handle in created_handles if handle not in readback_handles]
        if missing_handles:
            status = "failed"
            errors.append(f"missing_readback_handles:{','.join(missing_handles)}")
        if any(entity.layer != PREVIEW_LAYER for entity in entities):
            status = "failed"
            errors.append("wrong_layer_readback")

        rollback_token = f"autocad-rollback:{patch.transaction_id}" if created_handles else None
        receipt = self._receipt(
            patch=patch,
            status=status,
            semantic_to_handles=semantic_to_handles,
            created_handles=created_handles,
            entities=entities,
            rollback_token=rollback_token,
            errors=errors,
        )
        if rollback_token:
            self._transactions[patch.transaction_id] = _TransactionState(
                run_id=patch.run_id,
                transaction_id=patch.transaction_id,
                rollback_token=rollback_token,
                created_handles=list(created_handles),
                semantic_to_handles={key: list(value) for key, value in semantic_to_handles.items()},
            )
        return receipt

    def readback(self, *, transaction_id: str) -> ExecutionReceipt:
        state = self._transactions.get(transaction_id)
        if state is None:
            return ExecutionReceipt(
                schema_version="execution-receipt/v1",
                run_id="readback",
                transaction_id=transaction_id,
                backend=self.backend_name,
                status="blocked",
                semantic_to_handles={},
                entities=[],
                created_handles=[],
                updated_handles=[],
                deleted_handles=[],
                saved_current_dwg=False,
                rollback_token=None,
                errors=["unknown_transaction_id"],
                warnings=[],
            )
        return ExecutionReceipt(
            schema_version="execution-receipt/v1",
            run_id=state.run_id,
            transaction_id=state.transaction_id,
            backend=self.backend_name,
            status="succeeded",
            semantic_to_handles={key: list(value) for key, value in state.semantic_to_handles.items()},
            entities=_readback_handles(self._driver_instance(), state.created_handles),
            created_handles=list(state.created_handles),
            updated_handles=[],
            deleted_handles=[],
            saved_current_dwg=False,
            rollback_token=state.rollback_token,
            errors=[],
            warnings=[],
        )

    def capture_view(self, *, transaction_id: str, output_path: str) -> str:
        state = self._transactions.get(transaction_id)
        if state is None:
            raise ValueError(f"Unknown transaction_id: {transaction_id}")
        driver = self._driver_instance()
        zoom_result = _call_optional(
            driver,
            "zoom_to_handles",
            handles=list(state.created_handles),
            layer=PREVIEW_LAYER,
            padding_ratio=0.15,
        )
        refresh_result = _call_optional(driver, "refresh_view")
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schemaVersion": "autocad-visual-aid/v1",
            "transactionId": transaction_id,
            "backend": self.backend_name,
            "visualAidOnly": True,
            "handles": list(state.created_handles),
            "zoomResult": zoom_result,
            "refreshResult": refresh_result,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path)

    def rollback(self, *, rollback_token: str) -> ExecutionReceipt:
        state = next((item for item in self._transactions.values() if item.rollback_token == rollback_token), None)
        if state is None:
            return ExecutionReceipt(
                schema_version="execution-receipt/v1",
                run_id="rollback",
                transaction_id=rollback_token,
                backend=self.backend_name,
                status="blocked",
                semantic_to_handles={},
                entities=[],
                created_handles=[],
                updated_handles=[],
                deleted_handles=[],
                saved_current_dwg=False,
                rollback_token=None,
                errors=["unknown_rollback_token"],
                warnings=[],
            )

        driver = self._driver_instance()
        deleted: list[str] = []
        errors: list[str] = []
        previous_delete_flag = _set_preview_delete_guard(driver, allowed=True)
        try:
            for handle in state.created_handles:
                try:
                    driver.delete_entity_by_handle(handle)
                    deleted.append(handle)
                except Exception as exc:  # pragma: no cover - depends on live driver failure mode
                    errors.append(f"delete_failed:{handle}:{type(exc).__name__}:{exc}")
                    break
        finally:
            _restore_preview_delete_guard(driver, previous_delete_flag)

        status: Literal["succeeded", "blocked", "failed"] = "failed" if errors else "succeeded"
        if status == "succeeded":
            self._transactions.pop(state.transaction_id, None)
        return ExecutionReceipt(
            schema_version="execution-receipt/v1",
            run_id=state.run_id,
            transaction_id=state.transaction_id,
            backend=self.backend_name,
            status=status,
            semantic_to_handles={key: list(value) for key, value in state.semantic_to_handles.items()},
            entities=_readback_handles(driver, state.created_handles),
            created_handles=[],
            updated_handles=[],
            deleted_handles=deleted,
            saved_current_dwg=False,
            rollback_token=rollback_token,
            errors=errors,
            warnings=[],
        )

    def _driver_instance(self) -> Any:
        if self._driver is None:
            if self._driver_factory is None:
                raise RuntimeError("AutoCadBackend requires a driver or driver_factory.")
            self._driver = self._driver_factory()
        return self._driver

    def _apply_create_operation(self, driver: Any, operation: PatchOperation) -> dict[str, list[str]]:
        handles: list[str] = []
        errors: list[str] = []
        for primitive in operation.primitives:
            try:
                call = primitive_to_autocad_call(primitive)
                method = getattr(driver, call.method)
                result = method(**call.kwargs)
                result_handles = _collect_handles(result)
                if not result_handles:
                    errors.append(f"no_handle_returned:{primitive.primitive_id}")
                    break
                handles.extend(result_handles)
            except Exception as exc:
                errors.append(f"create_failed:{primitive.primitive_id}:{type(exc).__name__}:{exc}")
                break
        return {"handles": handles, "errors": errors}

    def _receipt(
        self,
        *,
        patch: CadPatch,
        status: Literal["succeeded", "blocked", "failed"],
        semantic_to_handles: dict[str, list[str]],
        created_handles: list[str],
        entities: list[EntityReadback],
        rollback_token: str | None,
        errors: list[str],
    ) -> ExecutionReceipt:
        return ExecutionReceipt(
            schema_version="execution-receipt/v1",
            run_id=patch.run_id,
            transaction_id=patch.transaction_id,
            backend=self.backend_name,
            status=status,
            semantic_to_handles={key: list(value) for key, value in semantic_to_handles.items()},
            entities=list(entities),
            created_handles=list(created_handles),
            updated_handles=[],
            deleted_handles=[],
            saved_current_dwg=False,
            rollback_token=rollback_token,
            errors=list(errors),
            warnings=[],
        )


class _ExistingAutoCadDriver:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.doc = app.ActiveDocument
        self.modelspace = self.doc.ModelSpace

    @classmethod
    def connect(cls) -> "_ExistingAutoCadDriver":
        try:
            import pythoncom  # type: ignore
            import win32com.client  # type: ignore
        except ImportError as exc:  # pragma: no cover - Windows optional dependency
            raise RuntimeError("pywin32 is required for AutoCAD backend.") from exc

        pythoncom.CoInitialize()
        errors: list[str] = []
        for prog_id in ("AutoCAD.Application", "AutoCAD.Application.25", "AutoCAD.Application.25.1"):
            try:
                return cls(win32com.client.GetActiveObject(prog_id))
            except Exception as exc:  # pragma: no cover - depends on installed AutoCAD
                errors.append(f"{prog_id}:{type(exc).__name__}:{exc}")
        raise RuntimeError("No already-open AutoCAD application found. " + " | ".join(errors))

    def ensure_layer(self, layer: str, *, layer_role: str = "preview") -> dict[str, str]:
        try:
            self.doc.Layers.Item(layer)
        except Exception:
            self.doc.Layers.Add(layer)
        self.doc.ActiveLayer = self.doc.Layers.Item(layer)
        return {"status": "ok", "layer": layer, "layerRole": layer_role}

    def draw_line(self, *, start_point: list[float], end_point: list[float], layer: str, layer_role: str = "preview") -> dict[str, str]:
        entity = self.modelspace.AddLine(_variant_point(start_point), _variant_point(end_point))
        return self._finalize(entity, layer)

    def draw_polyline(self, *, points: list[list[float]], closed: bool, layer: str, layer_role: str = "preview") -> dict[str, str]:
        entity = self.modelspace.AddLightWeightPolyline(_variant_double_array(_flatten_xy(points)))
        entity.Closed = bool(closed)
        return self._finalize(entity, layer)

    def draw_circle(self, *, center: list[float], radius: float, layer: str, layer_role: str = "preview") -> dict[str, str]:
        entity = self.modelspace.AddCircle(_variant_point(center), float(radius))
        return self._finalize(entity, layer)

    def draw_arc(
        self,
        *,
        center: list[float],
        radius: float,
        start_angle: float,
        end_angle: float,
        layer: str,
        layer_role: str = "preview",
    ) -> dict[str, str]:
        entity = self.modelspace.AddArc(_variant_point(center), float(radius), float(start_angle), float(end_angle))
        return self._finalize(entity, layer)

    def draw_text(self, *, text: str, position: list[float], height: float, layer: str, layer_role: str = "preview") -> dict[str, str]:
        entity = self.modelspace.AddText(str(text), _variant_point(position), float(height))
        return self._finalize(entity, layer)

    def snapshot_handles(self, *, handles: list[str], layer: str | None = None) -> list[dict[str, Any]]:
        wanted = {str(handle).upper() for handle in handles}
        snapshots: list[dict[str, Any]] = []
        for entity in self.modelspace:
            handle = str(getattr(entity, "Handle", "")).upper()
            if handle not in wanted:
                continue
            if layer and str(getattr(entity, "Layer", "")) != layer:
                continue
            snapshots.append(_snapshot_entity(entity))
        return snapshots

    def snapshot_modelspace(self, *, layer: str | None = None) -> list[dict[str, Any]]:
        snapshots: list[dict[str, Any]] = []
        for entity in self.modelspace:
            if layer and str(getattr(entity, "Layer", "")) != layer:
                continue
            snapshots.append(_snapshot_entity(entity))
        return snapshots

    def delete_entity_by_handle(self, handle: str) -> None:
        matches = self.snapshot_handles(handles=[handle])
        if not matches:
            raise ValueError(f"created_handle_not_found:{handle}")
        wanted = str(handle).upper()
        for entity in self.modelspace:
            if str(getattr(entity, "Handle", "")).upper() == wanted:
                entity.Delete()
                return
        raise ValueError(f"created_handle_not_found:{handle}")

    def zoom_to_handles(self, *, handles: list[str], layer: str | None = None, padding_ratio: float = 0.15) -> dict[str, Any]:
        return {"status": "not_required", "handles": list(handles), "layer": layer, "paddingRatio": padding_ratio}

    def refresh_view(self) -> dict[str, str]:
        try:
            self.doc.Regen(1)
        except Exception:
            pass
        return {"status": "refreshed"}

    def _finalize(self, entity: Any, layer: str) -> dict[str, str]:
        entity.Layer = layer
        try:
            entity.Update()
        except Exception:
            pass
        return {"handle": str(entity.Handle)}


def _ensure_preview_layer(driver: Any) -> None:
    ensure_layer = getattr(driver, "ensure_layer", None)
    if callable(ensure_layer):
        ensure_layer(PREVIEW_LAYER, layer_role="preview")


def _set_preview_delete_guard(driver: Any, *, allowed: bool) -> bool | None:
    write_guard = getattr(driver, "write_guard", None)
    if write_guard is None or not hasattr(write_guard, "allow_delete"):
        return None
    previous = bool(getattr(write_guard, "allow_delete"))
    setattr(write_guard, "allow_delete", allowed)
    return previous


def _restore_preview_delete_guard(driver: Any, previous: bool | None) -> None:
    if previous is None:
        return
    write_guard = getattr(driver, "write_guard", None)
    if write_guard is not None and hasattr(write_guard, "allow_delete"):
        setattr(write_guard, "allow_delete", previous)


def _collect_handles(result: object) -> list[str]:
    if result is None:
        return []
    if isinstance(result, str):
        return [result]
    if isinstance(result, dict):
        handles: list[str] = []
        for key in ("handles", "created_handles", "boundary_handles"):
            value = result.get(key)
            if isinstance(value, list):
                handles.extend(str(item) for item in value if item)
        if result.get("handle"):
            handles.append(str(result["handle"]))
        return list(dict.fromkeys(handles))
    if isinstance(result, list):
        return [str(item) for item in result if item]
    return []


def _readback_handles(driver: Any, handles: list[str]) -> list[EntityReadback]:
    snapshot_handles = getattr(driver, "snapshot_handles", None)
    if not callable(snapshot_handles):
        return []
    snapshots = snapshot_handles(handles=list(dict.fromkeys(handles)), layer=PREVIEW_LAYER)
    if not isinstance(snapshots, list):
        return []
    return [_entity_readback_from_snapshot(item) for item in snapshots if isinstance(item, dict)]


def _snapshot_modelspace(driver: Any) -> list[dict[str, Any]]:
    snapshot_modelspace = getattr(driver, "snapshot_modelspace", None)
    if not callable(snapshot_modelspace):
        return []
    snapshots = snapshot_modelspace(layer=PREVIEW_LAYER)
    return [dict(item) for item in snapshots if isinstance(item, dict)] if isinstance(snapshots, list) else []


def _entity_readback_from_snapshot(snapshot: dict[str, Any]) -> EntityReadback:
    return EntityReadback(
        handle=str(snapshot.get("handle") or ""),
        entity_type=_entity_type(snapshot),
        layer=str(snapshot.get("layer") or ""),
        bbox=_bbox(snapshot),
    )


def _drawing_entity_from_snapshot(snapshot: dict[str, Any]) -> DrawingEntitySnapshot:
    return DrawingEntitySnapshot(
        handle=str(snapshot.get("handle") or ""),
        entity_type=_entity_type(snapshot),
        layer=str(snapshot.get("layer") or ""),
        bbox=_bbox(snapshot),
    )


def _snapshot_entity(entity: Any) -> dict[str, Any]:
    return {
        "handle": str(getattr(entity, "Handle", "")),
        "entity_type": _entity_name(entity),
        "object_name": str(getattr(entity, "ObjectName", "")),
        "layer": str(getattr(entity, "Layer", "")),
        "bbox": _entity_bbox(entity),
    }


def _entity_name(entity: Any) -> str:
    object_name = str(getattr(entity, "ObjectName", "")).lower()
    if "polyline" in object_name:
        return "LWPOLYLINE"
    if "circle" in object_name:
        return "CIRCLE"
    if "arc" in object_name:
        return "ARC"
    if "text" in object_name:
        return "TEXT"
    if "line" in object_name:
        return "LINE"
    return object_name.upper() or "UNKNOWN"


def _entity_bbox(entity: Any) -> dict[str, list[float]] | None:
    try:
        minimum, maximum = entity.GetBoundingBox()
        return {"min": [float(minimum[0]), float(minimum[1])], "max": [float(maximum[0]), float(maximum[1])]}
    except Exception:
        return None


def _entity_type(snapshot: dict[str, Any]) -> str:
    raw = str(snapshot.get("entity_type") or snapshot.get("expected_entity_type") or "").strip().upper()
    if raw:
        return raw
    type_value = str(snapshot.get("type") or "").strip().lower()
    if type_value == "polyline":
        return "LWPOLYLINE"
    if type_value:
        return type_value.upper()
    object_name = str(snapshot.get("object_name") or "").strip().lower()
    if "polyline" in object_name:
        return "LWPOLYLINE"
    if "circle" in object_name:
        return "CIRCLE"
    if "arc" in object_name:
        return "ARC"
    if "text" in object_name:
        return "TEXT"
    if "line" in object_name:
        return "LINE"
    return "UNKNOWN"


def _bbox(snapshot: dict[str, Any]) -> tuple[float, float, float, float] | None:
    raw = snapshot.get("bbox")
    if isinstance(raw, dict):
        minimum = raw.get("min")
        maximum = raw.get("max")
        if isinstance(minimum, list) and isinstance(maximum, list) and len(minimum) >= 2 and len(maximum) >= 2:
            return (float(minimum[0]), float(minimum[1]), float(maximum[0]), float(maximum[1]))
    if isinstance(raw, (list, tuple)) and len(raw) == 4:
        return (float(raw[0]), float(raw[1]), float(raw[2]), float(raw[3]))
    points = snapshot.get("points")
    if isinstance(points, list) and points:
        xs = [float(point[0]) for point in points if isinstance(point, list) and len(point) >= 2]
        ys = [float(point[1]) for point in points if isinstance(point, list) and len(point) >= 2]
        if xs and ys:
            return (min(xs), min(ys), max(xs), max(ys))
    return None


def _document_id(driver: Any) -> str:
    doc = getattr(driver, "doc", None)
    full_name = str(getattr(doc, "FullName", getattr(doc, "fullName", "")) or "").strip()
    name = str(getattr(doc, "Name", getattr(doc, "name", "")) or "").strip()
    return full_name or name or "autocad-active-document"


def _call_optional(driver: Any, method_name: str, **kwargs: Any) -> dict[str, Any]:
    method = getattr(driver, method_name, None)
    if not callable(method):
        return {"status": "not_checked", "reason": f"driver has no {method_name}"}
    try:
        result = method(**kwargs)
    except TypeError:
        result = method()
    if isinstance(result, dict):
        return dict(result)
    return {"status": "ok", "result": str(result)}


def _variant_point(values: list[float]) -> Any:
    import pythoncom  # type: ignore

    point = [float(values[0]), float(values[1]), float(values[2] if len(values) > 2 else 0.0)]
    return pythoncom.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, point)


def _variant_double_array(values: list[float]) -> Any:
    import pythoncom  # type: ignore

    return pythoncom.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(value) for value in values])


def _flatten_xy(points: list[list[float]]) -> list[float]:
    result: list[float] = []
    for point in points:
        result.extend([float(point[0]), float(point[1])])
    return result
