from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from cad_agent_vnext.adapters.fake_backend import FakeCadBackend
from cad_agent_vnext.app.transaction_gateway import CadTransactionGateway
from cad_agent_vnext.domain.patch import CadPatch, PatchOperation
from cad_agent_vnext.domain.primitives import Primitive
from cad_agent_vnext.domain.receipt import EntityReadback, ExecutionReceipt
from cad_agent_vnext.policy.safety_policy import Gate0SafetyPolicy
from cad_agent_vnext.policy.transaction_policy import audit_patch_policy


ROOT = Path(__file__).resolve().parents[3]


def rectangle(object_id: str = "desk", *, x: float = 0, layer: str = "CODEX_PREVIEW") -> Primitive:
    return Primitive(
        primitive_id=f"{object_id}-rect",
        semantic_object_id=object_id,
        primitive_type="rectangle",
        geometry={"origin": [x, 0], "width": 100, "depth": 50},
        layer=layer,  # type: ignore[arg-type]
        style_token="preview.default",
        expected_entity_type="LWPOLYLINE",
    )


def patch(
    transaction_id: str = "txn-gateway",
    *,
    operations: list[PatchOperation] | None = None,
    primitives: list[Primitive] | None = None,
) -> CadPatch:
    if operations is None:
        operations = [
            PatchOperation(
                op_id="create-desk",
                action="create",
                semantic_object_id="desk",
                primitives=primitives or [rectangle("desk")],
            )
        ]
    return CadPatch(
        schema_version="cad-patch/v1",
        run_id="run_gateway",
        transaction_id=transaction_id,
        target_layer="CODEX_PREVIEW",
        operations=operations,
        save_current_dwg=False,
        forbidden_effects=["dwg_save", "formal_layer_write"],
    )


def update_patch(target_handle: str, *, semantic_object_id: str = "desk", transaction_id: str = "txn-update") -> CadPatch:
    return patch(
        transaction_id,
        operations=[
            PatchOperation(
                op_id="update-desk",
                action="update",
                semantic_object_id=semantic_object_id,
                target_handles=[target_handle],
                primitives=[rectangle(semantic_object_id, x=200)],
            )
        ],
    )


def delete_patch(target_handle: str, *, semantic_object_id: str = "desk", transaction_id: str = "txn-delete") -> CadPatch:
    return patch(
        transaction_id,
        operations=[
            PatchOperation(
                op_id="delete-desk",
                action="delete",
                semantic_object_id=semantic_object_id,
                target_handles=[target_handle],
            )
        ],
    )


class CountingBackend:
    def __init__(self, inner: FakeCadBackend | None = None) -> None:
        self.inner = inner or FakeCadBackend()
        self.apply_calls = 0
        self.readback_calls = 0
        self.rollback_calls = 0

    def inspect_document(self, *, run_id: str):
        return self.inner.inspect_document(run_id=run_id)

    def apply_patch(self, item: CadPatch):
        self.apply_calls += 1
        return self.inner.apply_patch(item)

    def readback(self, *, transaction_id: str):
        self.readback_calls += 1
        return self.inner.readback(transaction_id=transaction_id)

    def capture_view(self, *, transaction_id: str, output_path: str):
        return self.inner.capture_view(transaction_id=transaction_id, output_path=output_path)

    def rollback(self, *, rollback_token: str):
        self.rollback_calls += 1
        return self.inner.rollback(rollback_token=rollback_token)


class MutatingReadbackBackend(CountingBackend):
    def __init__(self, *, layer: str = "CODEX_PREVIEW", bbox: tuple[float, float, float, float] | None = (0, 0, 1, 1)) -> None:
        super().__init__()
        self.layer = layer
        self.bbox = bbox

    def readback(self, *, transaction_id: str):
        receipt = super().readback(transaction_id=transaction_id)
        entities = [
            EntityReadback(handle=entity.handle, entity_type=entity.entity_type, layer=self.layer, bbox=self.bbox)
            for entity in receipt.entities
        ]
        return receipt.model_copy(update={"entities": entities})


class DroppingReadbackBackend(CountingBackend):
    def readback(self, *, transaction_id: str):
        receipt = super().readback(transaction_id=transaction_id)
        return receipt.model_copy(update={"entities": receipt.entities[:-1]})


class SemanticMissingBackend(CountingBackend):
    def apply_patch(self, item: CadPatch):
        receipt = super().apply_patch(item)
        return receipt.model_copy(update={"semantic_to_handles": {}})


class FailureReceiptBackend(CountingBackend):
    def apply_patch(self, item: CadPatch):
        receipt = super().apply_patch(item)
        return receipt.model_copy(update={"status": "failed", "errors": ["backend_failed"]})


class RollbackFailingBackend(FailureReceiptBackend):
    def rollback(self, *, rollback_token: str):
        self.rollback_calls += 1
        return ExecutionReceipt(
            schema_version="execution-receipt/v1",
            run_id="rollback",
            transaction_id=rollback_token,
            backend="fake",
            status="blocked",
            semantic_to_handles={},
            entities=[],
            created_handles=[],
            updated_handles=[],
            deleted_handles=[],
            saved_current_dwg=False,
            rollback_token=None,
            errors=["rollback_failed"],
        )


class MissingSavedFlagBackend:
    def __init__(self, *, saved_value: Any = None, include_saved: bool = False) -> None:
        self.apply_calls = 0
        self.readback_calls = 0
        self.rollback_calls = 0
        self.saved_value = saved_value
        self.include_saved = include_saved

    def apply_patch(self, item: CadPatch):
        self.apply_calls += 1
        data = {
            "schema_version": "execution-receipt/v1",
            "run_id": item.run_id,
            "transaction_id": item.transaction_id,
            "backend": "malicious",
            "status": "succeeded",
            "semantic_to_handles": {"desk": ["H1"]},
            "entities": [EntityReadback(handle="H1", entity_type="LWPOLYLINE", layer="CODEX_PREVIEW", bbox=(0, 0, 1, 1))],
            "created_handles": ["H1"],
            "updated_handles": [],
            "deleted_handles": [],
            "rollback_token": "rollback:malicious",
            "errors": [],
            "warnings": [],
        }
        if self.include_saved:
            data["saved_current_dwg"] = self.saved_value
        return SimpleNamespace(**data)

    def readback(self, *, transaction_id: str):
        self.readback_calls += 1
        return SimpleNamespace(
            transaction_id=transaction_id,
            entities=[EntityReadback(handle="H1", entity_type="LWPOLYLINE", layer="CODEX_PREVIEW", bbox=(0, 0, 1, 1))],
        )

    def rollback(self, *, rollback_token: str):
        self.rollback_calls += 1
        return SimpleNamespace(status="succeeded", errors=[])


class OverBudgetReceiptBackend(MissingSavedFlagBackend):
    def __init__(self) -> None:
        super().__init__(saved_value=False, include_saved=True)

    def apply_patch(self, item: CadPatch):
        handles = [f"H{index}" for index in range(101)]
        return SimpleNamespace(
            schema_version="execution-receipt/v1",
            run_id=item.run_id,
            transaction_id=item.transaction_id,
            backend="malicious",
            status="succeeded",
            semantic_to_handles={"desk": handles},
            entities=[
                EntityReadback(handle=handle, entity_type="LWPOLYLINE", layer="CODEX_PREVIEW", bbox=(0, 0, 1, 1))
                for handle in handles
            ],
            created_handles=handles,
            updated_handles=[],
            deleted_handles=[],
            saved_current_dwg=False,
            rollback_token="rollback:over-budget",
            errors=[],
            warnings=[],
        )

    def readback(self, *, transaction_id: str):
        receipt = self.apply_patch(patch(transaction_id))
        return SimpleNamespace(transaction_id=transaction_id, entities=receipt.entities)


def error_codes(receipt: ExecutionReceipt) -> set[str]:
    return {item.split(":", 1)[0] for item in receipt.errors}


def test_gateway_normal_create_runs_apply_then_immediate_readback():
    backend = CountingBackend()
    gateway = CadTransactionGateway(backend=backend)

    receipt = gateway.execute(patch())

    assert receipt.status == "succeeded"
    assert receipt.saved_current_dwg is False
    assert backend.apply_calls == 1
    assert backend.readback_calls == 1
    assert receipt.created_handles == ["F0001"]
    assert receipt.semantic_to_handles == {"desk": ["F0001"]}
    assert all(entity.bbox is not None for entity in receipt.entities)


@pytest.mark.parametrize(
    ("bad_patch", "expected_error"),
    [
        (patch().model_copy(update={"target_layer": "A-WALL"}), "target_layer_not_preview"),
        (patch().model_copy(update={"save_current_dwg": True}), "save_current_dwg_forbidden"),
        (patch(primitives=[rectangle().model_copy(update={"layer": "A-WALL"})]), "primitive_layer_not_preview"),
        (
            patch(primitives=[rectangle(f"obj-{index}", x=index * 120) for index in range(101)]),
            "expected_entity_count_exceeds_budget",
        ),
        (
            patch(operations=[PatchOperation(op_id="delete-empty", action="delete", semantic_object_id="desk")]),
            "delete_without_victim_handles",
        ),
        (delete_patch("OUTSIDE"), "delete_forbidden"),
        (update_patch("OUTSIDE"), "update_target_outside_prior_receipt"),
    ],
)
def test_gateway_blocks_policy_violations_before_backend(bad_patch: CadPatch, expected_error: str):
    backend = CountingBackend()
    gateway = CadTransactionGateway(backend=backend)

    receipt = gateway.execute(bad_patch)

    assert receipt.status == "blocked"
    assert expected_error in error_codes(receipt)
    assert backend.apply_calls == 0
    assert backend.readback_calls == 0


def test_policy_constants_match_gate0_contract():
    policy = Gate0SafetyPolicy()

    assert policy.preview_only is True
    assert policy.target_layer == "CODEX_PREVIEW"
    assert policy.save_current_dwg is False
    assert policy.allow_delete is False
    assert policy.allow_formal_layer is False
    assert policy.max_created_entities == 100
    assert policy.max_repair_rounds == 2


def test_repair_update_is_allowed_only_for_prior_receipt_target_handle():
    backend = CountingBackend()
    gateway = CadTransactionGateway(backend=backend)
    created = gateway.execute(patch("txn-create"))

    repaired = gateway.execute(update_patch(created.created_handles[0], transaction_id="txn-repair"), prior_receipt=created, repair=True)
    wrong_semantic = gateway.execute(
        update_patch(created.created_handles[0], semantic_object_id="other", transaction_id="txn-wrong-semantic"),
        prior_receipt=created,
        repair=True,
    )

    assert repaired.status == "succeeded"
    assert "repair_target_semantic_mismatch" in error_codes(wrong_semantic)
    assert wrong_semantic.status == "blocked"


def test_repair_delete_is_allowed_for_prior_receipt_target_handle():
    backend = CountingBackend()
    gateway = CadTransactionGateway(backend=backend)
    created = gateway.execute(patch("txn-create"))

    deleted = gateway.execute(delete_patch(created.created_handles[0], transaction_id="txn-repair-delete"), prior_receipt=created, repair=True)

    assert deleted.status == "succeeded"
    assert deleted.deleted_handles == created.created_handles


@pytest.mark.parametrize(
    ("backend", "expected_error"),
    [
        (DroppingReadbackBackend(), "readback_handles_missing"),
        (MutatingReadbackBackend(layer="A-WALL"), "readback_wrong_layer"),
        (MutatingReadbackBackend(bbox=None), "readback_bbox_missing"),
        (SemanticMissingBackend(), "semantic_id_missing"),
        (FailureReceiptBackend(), "backend_receipt_not_succeeded"),
        (MissingSavedFlagBackend(include_saved=False), "backend_receipt_missing_savedCurrentDwg"),
        (MissingSavedFlagBackend(saved_value=True, include_saved=True), "backend_saved_current_dwg_violation"),
        (OverBudgetReceiptBackend(), "receipt_created_entity_count_exceeds_budget"),
    ],
)
def test_gateway_rolls_back_receipt_or_readback_policy_failures(backend: Any, expected_error: str):
    gateway = CadTransactionGateway(backend=backend)

    receipt = gateway.execute(patch())

    assert receipt.status == "failed"
    assert expected_error in error_codes(receipt)
    assert backend.rollback_calls == 1


def test_gateway_reports_rollback_failure_without_hiding_original_error():
    backend = RollbackFailingBackend()
    gateway = CadTransactionGateway(backend=backend)

    receipt = gateway.execute(patch())

    assert receipt.status == "failed"
    assert "backend_receipt_not_succeeded" in error_codes(receipt)
    assert "rollback_failed" in error_codes(receipt)


def test_gateway_blocks_duplicate_transaction_id_before_backend_reexecution():
    backend = CountingBackend()
    gateway = CadTransactionGateway(backend=backend)

    first = gateway.execute(patch("txn-duplicate"))
    second = gateway.execute(patch("txn-duplicate"))

    assert first.status == "succeeded"
    assert second.status == "blocked"
    assert "duplicate_transaction_id" in error_codes(second)
    assert backend.apply_calls == 1


def test_app_and_tools_do_not_call_backend_apply_patch_directly():
    offenders = []
    for root in [ROOT / "src" / "cad_agent_vnext" / "app", ROOT / "src" / "cad_agent_vnext" / "tools"]:
        for path in root.rglob("*.py"):
            if path.name == "transaction_gateway.py":
                continue
            if ".apply_patch(" in path.read_text(encoding="utf-8"):
                offenders.append(path.relative_to(ROOT).as_posix())

    assert offenders == []


def test_transaction_policy_exposes_standalone_patch_audit():
    decision = audit_patch_policy(patch())

    assert decision.allowed is True
    assert decision.reasons == []
