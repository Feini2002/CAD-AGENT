from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from cad_agent.adapters.autocad_backend import AutoCadBackend
from cad_agent.adapters.autocad_backend import _ExistingAutoCadDriver
from cad_agent.adapters.autocad_backend import _variant_double_array, _variant_point
from cad_agent.adapters.autocad_primitives import AUTOCAD_PRIMITIVE_MAP, primitive_to_autocad_call
from cad_agent.domain.patch import CadPatch, PatchOperation
from cad_agent.domain.primitives import Primitive


ROOT = Path(__file__).resolve().parents[2]


def primitive(
    primitive_type: str,
    geometry: dict[str, Any],
    *,
    primitive_id: str | None = None,
    semantic_object_id: str = "desk",
    expected_entity_type: str = "LWPOLYLINE",
) -> Primitive:
    return Primitive(
        primitive_id=primitive_id or f"{semantic_object_id}-{primitive_type}",
        semantic_object_id=semantic_object_id,
        primitive_type=primitive_type,  # type: ignore[arg-type]
        geometry=geometry,
        layer="CODEX_PREVIEW",
        style_token="preview.default",
        expected_entity_type=expected_entity_type,
    )


def create_patch(*primitives: Primitive, transaction_id: str = "txn-autocad") -> CadPatch:
    return CadPatch(
        schema_version="cad-patch/v1",
        run_id="run_autocad",
        transaction_id=transaction_id,
        target_layer="CODEX_PREVIEW",
        operations=[
            PatchOperation(
                op_id=f"create-{item.primitive_id}",
                action="create",
                semantic_object_id=item.semantic_object_id,
                primitives=[item],
            )
            for item in primitives
        ],
        save_current_dwg=False,
        forbidden_effects=["dwg_save", "formal_layer_write"],
    )


class RecordingAutoCadDriver:
    def __init__(self) -> None:
        self.doc = SimpleNamespace(Name="active.dwg", FullName=r"C:\active.dwg")
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.entities: dict[str, dict[str, Any]] = {}
        self.deleted_handles: list[str] = []
        self.next_handle = 0

    def ensure_layer(self, layer: str, *, layer_role: str = "preview") -> dict[str, str]:
        self.calls.append(("ensure_layer", {"layer": layer, "layer_role": layer_role}))
        return {"status": "ok"}

    def draw_line(self, **kwargs: Any) -> dict[str, str]:
        return self._record("draw_line", kwargs, "LINE", bbox_from_points=[kwargs["start_point"], kwargs["end_point"]])

    def draw_polyline(self, **kwargs: Any) -> dict[str, str]:
        return self._record("draw_polyline", kwargs, "LWPOLYLINE", bbox_from_points=kwargs["points"])

    def draw_circle(self, **kwargs: Any) -> dict[str, str]:
        center = kwargs["center"]
        radius = kwargs["radius"]
        return self._record(
            "draw_circle",
            kwargs,
            "CIRCLE",
            bbox=(center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
        )

    def draw_arc(self, **kwargs: Any) -> dict[str, str]:
        center = kwargs["center"]
        radius = kwargs["radius"]
        return self._record(
            "draw_arc",
            kwargs,
            "ARC",
            bbox=(center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
        )

    def draw_text(self, **kwargs: Any) -> dict[str, str]:
        position = kwargs["position"]
        return self._record(
            "draw_text",
            kwargs,
            "TEXT",
            bbox=(position[0], position[1], position[0] + 1, position[1] + 1),
        )

    def snapshot_handles(self, *, handles: list[str], layer: str | None = None) -> list[dict[str, Any]]:
        result = []
        for handle in handles:
            entity = self.entities.get(handle)
            if entity and (layer is None or entity["layer"] == layer):
                result.append(dict(entity))
        return result

    def snapshot_modelspace(self, *, layer: str | None = None) -> list[dict[str, Any]]:
        return [
            dict(entity)
            for entity in self.entities.values()
            if layer is None or entity["layer"] == layer
        ]

    def zoom_to_handles(self, *, handles: list[str], layer: str | None = None, padding_ratio: float = 0.15) -> dict[str, Any]:
        self.calls.append(
            (
                "zoom_to_handles",
                {"handles": list(handles), "layer": layer, "padding_ratio": padding_ratio},
            )
        )
        return {"status": "zoomed_to_handles"}

    def refresh_view(self) -> dict[str, str]:
        self.calls.append(("refresh_view", {}))
        return {"status": "refreshed"}

    def delete_entity_by_handle(self, handle: str) -> None:
        self.calls.append(("delete_entity_by_handle", {"handle": handle}))
        del self.entities[str(handle)]
        self.deleted_handles.append(str(handle))

    def _record(
        self,
        method: str,
        kwargs: dict[str, Any],
        entity_type: str,
        *,
        bbox: tuple[float, float, float, float] | None = None,
        bbox_from_points: list[list[float | int]] | None = None,
    ) -> dict[str, str]:
        self.calls.append((method, dict(kwargs)))
        self.next_handle += 1
        handle = f"L{self.next_handle:04d}"
        resolved_bbox = bbox
        if bbox_from_points:
            xs = [float(point[0]) for point in bbox_from_points]
            ys = [float(point[1]) for point in bbox_from_points]
            resolved_bbox = (min(xs), min(ys), max(xs), max(ys))
        self.entities[handle] = {
            "handle": handle,
            "type": entity_type.lower(),
            "entity_type": entity_type,
            "object_name": f"AcDb{entity_type.title()}",
            "layer": kwargs["layer"],
            "bbox": {"min": [resolved_bbox[0], resolved_bbox[1]], "max": [resolved_bbox[2], resolved_bbox[3]]}
            if resolved_bbox
            else None,
        }
        return {"handle": handle}


class GuardedDeleteRecordingAutoCadDriver(RecordingAutoCadDriver):
    def __init__(self) -> None:
        super().__init__()
        self.write_guard = SimpleNamespace(allow_delete=False)
        self.delete_allow_values: list[bool] = []

    def delete_entity_by_handle(self, handle: str) -> None:
        self.delete_allow_values.append(bool(self.write_guard.allow_delete))
        if not self.write_guard.allow_delete:
            raise RuntimeError("delete_not_allowed")
        super().delete_entity_by_handle(handle)


def test_autocad_primitive_map_is_explicit_for_gate0_types():
    assert AUTOCAD_PRIMITIVE_MAP == {
        "line": ("draw_line", "LINE"),
        "rectangle": ("draw_polyline", "LWPOLYLINE"),
        "polyline": ("draw_polyline", "LWPOLYLINE"),
        "circle": ("draw_circle", "CIRCLE"),
        "arc": ("draw_arc", "ARC"),
        "text": ("draw_text", "TEXT"),
        "ellipse": ("draw_polyline", "LWPOLYLINE"),
    }


def test_primitive_to_autocad_call_maps_geometry_and_preview_layer():
    cases = [
        (
            primitive("line", {"start": [0, 0], "end": [10, 0]}, expected_entity_type="LINE"),
            "draw_line",
            {"start_point": [0.0, 0.0, 0.0], "end_point": [10.0, 0.0, 0.0]},
        ),
        (
            primitive("rectangle", {"origin": [2, 3], "width": 10, "depth": 5}),
            "draw_polyline",
            {
                "points": [
                    [2.0, 3.0, 0.0],
                    [12.0, 3.0, 0.0],
                    [12.0, 8.0, 0.0],
                    [2.0, 8.0, 0.0],
                ],
                "closed": True,
            },
        ),
        (
            primitive("circle", {"center": [4, 5], "radius": 3}, expected_entity_type="CIRCLE"),
            "draw_circle",
            {"center": [4.0, 5.0, 0.0], "radius": 3.0},
        ),
        (
            primitive("text", {"position": [7, 8], "text": "Desk"}, expected_entity_type="TEXT"),
            "draw_text",
            {"position": [7.0, 8.0, 0.0], "text": "Desk", "height": 12.0},
        ),
    ]

    for item, expected_method, expected_kwargs in cases:
        call = primitive_to_autocad_call(item)

        assert call.method == expected_method
        assert call.kwargs["layer"] == "CODEX_PREVIEW"
        assert call.kwargs["layer_role"] == "preview"
        for key, value in expected_kwargs.items():
            assert call.kwargs[key] == value


def test_variant_helpers_use_win32com_variant_constructor(monkeypatch):
    fake_pythoncom = SimpleNamespace(VT_ARRAY=0x2000, VT_R8=5)

    class FakeClient:
        def VARIANT(self, variant_type: int, value: list[float]) -> tuple[str, int, tuple[float, ...]]:
            return ("variant", variant_type, tuple(value))

    fake_client = FakeClient()
    fake_win32com = SimpleNamespace(client=fake_client)
    monkeypatch.setitem(sys.modules, "pythoncom", fake_pythoncom)
    monkeypatch.setitem(sys.modules, "win32com", fake_win32com)
    monkeypatch.setitem(sys.modules, "win32com.client", fake_client)

    assert _variant_point([1, 2.5]) == ("variant", 0x2000 | 5, (1.0, 2.5, 0.0))
    assert _variant_double_array([0, 1.5, 2]) == ("variant", 0x2000 | 5, (0.0, 1.5, 2.0))


def test_autocad_backend_applies_patch_and_readbacks_created_handles():
    driver = RecordingAutoCadDriver()
    backend = AutoCadBackend(driver=driver)
    patch = create_patch(
        primitive("rectangle", {"origin": [0, 0], "width": 100, "depth": 60}, semantic_object_id="desk"),
        primitive(
            "circle",
            {"center": [30, 30], "radius": 8},
            semantic_object_id="mouse",
            expected_entity_type="CIRCLE",
        ),
        primitive(
            "text",
            {"position": [0, 72], "text": "Desk"},
            semantic_object_id="label",
            expected_entity_type="TEXT",
        ),
    )

    receipt = backend.apply_patch(patch)
    readback = backend.readback(transaction_id=patch.transaction_id)

    assert receipt.status == "succeeded"
    assert receipt.backend == "autocad-existing"
    assert receipt.saved_current_dwg is False
    assert receipt.created_handles == ["L0001", "L0002", "L0003"]
    assert receipt.semantic_to_handles == {"desk": ["L0001"], "mouse": ["L0002"], "label": ["L0003"]}
    assert [name for name, _ in driver.calls if name.startswith("draw_")] == [
        "draw_polyline",
        "draw_circle",
        "draw_text",
    ]
    assert all(entity.layer == "CODEX_PREVIEW" for entity in receipt.entities)
    assert all(entity.bbox is not None for entity in readback.entities)


def test_autocad_backend_rollback_deletes_only_transaction_handles():
    driver = RecordingAutoCadDriver()
    backend = AutoCadBackend(driver=driver)
    first = backend.apply_patch(
        create_patch(
            primitive("circle", {"center": [0, 0], "radius": 5}, semantic_object_id="first", expected_entity_type="CIRCLE"),
            transaction_id="txn-first",
        )
    )
    second = backend.apply_patch(
        create_patch(
            primitive(
                "circle",
                {"center": [20, 0], "radius": 5},
                semantic_object_id="second",
                expected_entity_type="CIRCLE",
            ),
            transaction_id="txn-second",
        )
    )

    rollback = backend.rollback(rollback_token=first.rollback_token or "")

    assert rollback.status == "succeeded"
    assert rollback.deleted_handles == ["L0001"]
    assert driver.deleted_handles == ["L0001"]
    assert driver.snapshot_handles(handles=second.created_handles, layer="CODEX_PREVIEW")


def test_autocad_backend_rollback_temporarily_allows_preview_delete():
    driver = GuardedDeleteRecordingAutoCadDriver()
    backend = AutoCadBackend(driver=driver)
    receipt = backend.apply_patch(
        create_patch(
            primitive("circle", {"center": [0, 0], "radius": 5}, semantic_object_id="probe", expected_entity_type="CIRCLE")
        )
    )

    rollback = backend.rollback(rollback_token=receipt.rollback_token or "")

    assert rollback.status == "succeeded"
    assert rollback.deleted_handles == ["L0001"]
    assert driver.delete_allow_values == [True]
    assert driver.write_guard.allow_delete is False


def test_autocad_backend_rollback_succeeds_when_post_delete_readback_fails():
    class PostDeleteReadbackFailureDriver(RecordingAutoCadDriver):
        def snapshot_handles(self, *, handles: list[str], layer: str | None = None) -> list[dict[str, Any]]:
            if self.deleted_handles:
                raise RuntimeError("modelspace enumeration failed after delete")
            return super().snapshot_handles(handles=handles, layer=layer)

    driver = PostDeleteReadbackFailureDriver()
    backend = AutoCadBackend(driver=driver)
    receipt = backend.apply_patch(
        create_patch(
            primitive("circle", {"center": [0, 0], "radius": 5}, semantic_object_id="probe", expected_entity_type="CIRCLE")
        )
    )

    rollback = backend.rollback(rollback_token=receipt.rollback_token or "")

    assert rollback.status == "succeeded"
    assert rollback.deleted_handles == ["L0001"]
    assert rollback.entities == []
    assert rollback.warnings == ["post_delete_readback_failed:RuntimeError:modelspace enumeration failed after delete"]


def test_existing_autocad_driver_delete_uses_handle_to_object_without_modelspace_enumeration():
    class FakeEntity:
        def __init__(self) -> None:
            self.Layer = "CODEX_PREVIEW"
            self.deleted = False

        def Delete(self) -> None:
            self.deleted = True

    class BrokenModelSpace:
        def __iter__(self):
            raise RuntimeError("modelspace enumeration unavailable")

    entity = FakeEntity()
    doc = SimpleNamespace(HandleToObject=lambda handle: entity)
    driver = object.__new__(_ExistingAutoCadDriver)
    driver.doc = doc
    driver.modelspace = BrokenModelSpace()

    driver.delete_entity_by_handle("A1")

    assert entity.deleted is True


def test_autocad_backend_does_not_import_old_system_modules():
    source_root = ROOT / "src" / "cad_agent"
    offenders = []
    for path in source_root.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        if "from core." in source or "import core." in source:
            relative = path.relative_to(ROOT).as_posix()
            offenders.append(relative)

    assert offenders == []
