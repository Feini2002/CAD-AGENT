from __future__ import annotations

from pathlib import Path

import pytest

from cad_agent_vnext.adapters.fake_backend import FakeCadBackend
from cad_agent_vnext.domain.patch import CadPatch, PatchOperation
from cad_agent_vnext.domain.primitives import Primitive


ROOT = Path(__file__).resolve().parents[3]


def rectangle_primitive(object_id: str, x: float, y: float, width: float = 100, depth: float = 50) -> Primitive:
    return Primitive(
        primitive_id=f"{object_id}-rect",
        semantic_object_id=object_id,
        primitive_type="rectangle",
        geometry={"origin": [x, y], "width": width, "depth": depth},
        layer="CODEX_PREVIEW",
        style_token="preview.default",
        expected_entity_type="LWPOLYLINE",
    )


def patch(transaction_id: str, operations: list[PatchOperation]) -> CadPatch:
    return CadPatch(
        schema_version="cad-patch/v1",
        run_id="run_001",
        transaction_id=transaction_id,
        target_layer="CODEX_PREVIEW",
        operations=operations,
        forbidden_effects=["dwg_save", "formal_layer_write"],
    )


def create_patch(transaction_id: str, object_ids: list[str]) -> CadPatch:
    return patch(
        transaction_id,
        [
            PatchOperation(
                op_id=f"create-{object_id}",
                action="create",
                semantic_object_id=object_id,
                primitives=[rectangle_primitive(object_id, index * 120, 0)],
            )
            for index, object_id in enumerate(object_ids)
        ],
    )


def test_port_definition_has_no_legacy_runtime_leaks():
    source = (ROOT / "src" / "cad_agent_vnext" / "domain" / "ports.py").read_text(encoding="utf-8")

    assert "inspect_document" in source
    assert "apply_patch" in source
    assert "readback" in source
    assert "capture_view" in source
    assert "rollback" in source
    for forbidden in ("COM", "AutoCAD.Application", "subprocess", "legacy report"):
        assert forbidden not in source


def test_fake_backend_creates_five_semantic_objects_with_readback():
    backend = FakeCadBackend()

    receipt = backend.apply_patch(create_patch("txn-create", ["desk", "monitor", "keyboard", "mouse", "vase"]))

    assert receipt.status == "succeeded"
    assert receipt.saved_current_dwg is False
    assert set(receipt.semantic_to_handles) == {"desk", "monitor", "keyboard", "mouse", "vase"}
    assert len(receipt.created_handles) == 5
    assert all(entity.layer == "CODEX_PREVIEW" for entity in receipt.entities)
    assert all(entity.bbox is not None for entity in receipt.entities)


def test_fake_backend_update_only_changes_target_handle():
    backend = FakeCadBackend()
    create_receipt = backend.apply_patch(create_patch("txn-create", ["desk", "monitor"]))
    desk_handle = create_receipt.semantic_to_handles["desk"][0]
    monitor_handle = create_receipt.semantic_to_handles["monitor"][0]
    before_monitor_bbox = next(entity.bbox for entity in create_receipt.entities if entity.handle == monitor_handle)

    update_receipt = backend.apply_patch(
        patch(
            "txn-update",
            [
                PatchOperation(
                    op_id="update-desk",
                    action="update",
                    semantic_object_id="desk",
                    target_handles=[desk_handle],
                    primitives=[rectangle_primitive("desk", 500, 200, width=200, depth=80)],
                )
            ],
        )
    )
    readback = backend.readback(transaction_id="txn-update")

    assert update_receipt.status == "succeeded"
    assert update_receipt.updated_handles == [desk_handle]
    assert next(entity.bbox for entity in readback.entities if entity.handle == monitor_handle) == before_monitor_bbox
    assert next(entity.bbox for entity in readback.entities if entity.handle == desk_handle) == (500, 200, 700, 280)


def test_fake_backend_rollback_restores_previous_state():
    backend = FakeCadBackend()
    receipt = backend.apply_patch(create_patch("txn-create", ["desk"]))

    rollback = backend.rollback(rollback_token=receipt.rollback_token or "")
    snapshot = backend.inspect_document(run_id="run_001")

    assert rollback.status == "succeeded"
    assert snapshot.nearby_entities == []
    assert rollback.saved_current_dwg is False


def test_fake_backend_reports_wrong_layer_failure():
    backend = FakeCadBackend(failure_mode="wrong_layer")

    receipt = backend.apply_patch(create_patch("txn-wrong-layer", ["desk"]))

    assert receipt.status == "failed"
    assert receipt.saved_current_dwg is False
    assert receipt.errors == ["wrong_layer_readback"]
    assert receipt.entities[0].layer == "A-WALL"


def test_fake_backend_reports_partial_create_failure():
    backend = FakeCadBackend(partial_create_after=1)

    receipt = backend.apply_patch(create_patch("txn-partial", ["desk", "monitor", "keyboard"]))

    assert receipt.status == "failed"
    assert receipt.created_handles == ["F0001"]
    assert receipt.errors == ["partial_create"]


def test_fake_backend_rejects_duplicate_transaction_id():
    backend = FakeCadBackend()
    first = backend.apply_patch(create_patch("txn-repeat", ["desk"]))
    second = backend.apply_patch(create_patch("txn-repeat", ["desk"]))

    assert first.status == "succeeded"
    assert second.status == "blocked"
    assert second.errors == ["duplicate_transaction_id"]
