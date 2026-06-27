from __future__ import annotations

from pathlib import Path
from typing import Literal

from cad_agent.adapters.fake_backend import bbox_for_primitive
from cad_agent.adapters.autocad_backend import AutoCadBackend
from cad_agent.app.transaction_gateway import CadTransactionGateway
from cad_agent.app.run_workspace import DEFAULT_OUTPUT_ROOT, RunWorkspace
from cad_agent.domain.patch import CadPatch
from cad_agent.domain.receipt import EntityReadback, ExecutionReceipt
from cad_agent.tools.envelopes import ToolEnvelope


BackendName = Literal["fake", "autocad-existing"]


def execute_preview(
    *,
    run_id: str,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    backend: BackendName = "fake",
) -> ToolEnvelope:
    workspace = RunWorkspace.open(output_root=output_root, run_id=run_id)
    try:
        patch = CadPatch.model_validate(workspace.read_json_artifact("cad_patch.json"))
    except FileNotFoundError:
        return _blocked(run_id, ["cad_patch_missing"], "compile must produce cad_patch.json before execute-preview.")

    if backend == "fake":
        previous = _read_optional_receipt(workspace, "readback_receipt.json", run_id=run_id)
        prior_receipt = _read_optional_receipt(workspace, "execution_receipt.json", run_id=run_id)
        fake_backend = _ArtifactFakeBackend(run_id=run_id, previous=previous)
        gateway = CadTransactionGateway(backend=fake_backend)
        receipt = gateway.execute(patch, prior_receipt=prior_receipt, repair=_is_repair_patch(patch))
        readback = fake_backend.readback(transaction_id=patch.transaction_id)
    elif backend == "autocad-existing":
        try:
            adapter = AutoCadBackend.from_existing_autocad()
            prior_receipt = _read_optional_receipt(workspace, "execution_receipt.json", run_id=run_id)
            gateway = CadTransactionGateway(backend=adapter)
            receipt = gateway.execute(patch, prior_receipt=prior_receipt, repair=_is_repair_patch(patch))
            readback = adapter.readback(transaction_id=patch.transaction_id)
        except Exception as exc:
            return _blocked(run_id, [f"autocad_existing_unavailable:{type(exc).__name__}"], str(exc))
    else:
        return _blocked(run_id, [f"unsupported_backend:{backend}"], "Unsupported preview backend.")

    artifact_refs = [
        workspace.write_json_artifact("execution_receipt.json", receipt.model_dump(mode="json")),
        workspace.write_json_artifact("readback_receipt.json", readback.model_dump(mode="json")),
    ]
    status = "ok" if receipt.status == "succeeded" else "failed"
    return ToolEnvelope(
        status=status,
        run_id=run_id,
        artifact_refs=artifact_refs,
        next_actions=["verify"] if status == "ok" else ["rollback"],
        blocking_reasons=list(receipt.errors),
        summary=f"Preview execution finished with {backend}.",
    )


def rollback_run(*, run_id: str, output_root: str | Path = DEFAULT_OUTPUT_ROOT) -> ToolEnvelope:
    workspace = RunWorkspace.open(output_root=output_root, run_id=run_id)
    previous = _read_optional_receipt(workspace, "debug/pre_execution_readback.json", run_id=run_id)
    if previous is None:
        previous = _empty_receipt(run_id=run_id, transaction_id="rollback")
    artifact_ref = workspace.write_json_artifact("rollback_receipt.json", previous.model_dump(mode="json"))
    workspace.write_json_artifact("readback_receipt.json", previous.model_dump(mode="json"))
    return ToolEnvelope(
        status="ok",
        run_id=run_id,
        artifact_refs=[artifact_ref],
        next_actions=["closeout"],
        summary="Fake rollback restored the prior readback artifact state.",
    )


class _ArtifactFakeBackend:
    def __init__(self, *, run_id: str, previous: ExecutionReceipt | None) -> None:
        self.run_id = run_id
        self.previous = previous
        self.current = previous or _empty_receipt(run_id=run_id, transaction_id="initial")

    def apply_patch(self, patch: CadPatch) -> ExecutionReceipt:
        self.current = _apply_fake_patch(patch, previous=self.current)
        return self.current

    def readback(self, *, transaction_id: str) -> ExecutionReceipt:
        return _readback_from_receipt(self.current).model_copy(update={"transaction_id": transaction_id})

    def rollback(self, *, rollback_token: str) -> ExecutionReceipt:
        self.current = self.previous or _empty_receipt(run_id=self.run_id, transaction_id=rollback_token)
        return self.current.model_copy(update={"transaction_id": rollback_token, "rollback_token": None})


def _apply_fake_patch(patch: CadPatch, *, previous: ExecutionReceipt | None) -> ExecutionReceipt:
    state = previous or _empty_receipt(run_id=patch.run_id, transaction_id=patch.transaction_id)
    entities = {entity.handle: entity for entity in state.entities}
    semantic_to_handles = {key: list(value) for key, value in state.semantic_to_handles.items()}
    created: list[str] = []
    updated: list[str] = []
    deleted: list[str] = []
    errors: list[str] = []

    for operation in patch.operations:
        if operation.action == "create":
            handles = semantic_to_handles.setdefault(operation.semantic_object_id, [])
            for primitive in operation.primitives:
                handle = _next_handle(entities)
                entities[handle] = EntityReadback(
                    handle=handle,
                    entity_type=primitive.expected_entity_type,
                    layer=primitive.layer,
                    bbox=bbox_for_primitive(primitive),
                )
                handles.append(handle)
                created.append(handle)
        elif operation.action == "update":
            if not operation.target_handles:
                errors.append("missing_target_handles")
                break
            for index, handle in enumerate(operation.target_handles):
                primitive = operation.primitives[min(index, len(operation.primitives) - 1)] if operation.primitives else None
                if handle not in entities or primitive is None:
                    errors.append("missing_handle")
                    break
                entities[handle] = EntityReadback(
                    handle=handle,
                    entity_type=primitive.expected_entity_type,
                    layer=primitive.layer,
                    bbox=bbox_for_primitive(primitive),
                )
                updated.append(handle)
            if errors:
                break
        elif operation.action == "delete":
            if not operation.target_handles:
                errors.append("missing_target_handles")
                break
            for handle in operation.target_handles:
                if handle not in entities:
                    errors.append("missing_handle")
                    break
                entities.pop(handle)
                handles = semantic_to_handles.get(operation.semantic_object_id, [])
                semantic_to_handles[operation.semantic_object_id] = [item for item in handles if item != handle]
                deleted.append(handle)
            if errors:
                break

    return ExecutionReceipt(
        schema_version="execution-receipt/v1",
        run_id=patch.run_id,
        transaction_id=patch.transaction_id,
        backend="fake",
        status="failed" if errors else "succeeded",
        semantic_to_handles=semantic_to_handles,
        entities=list(entities.values()),
        created_handles=created,
        updated_handles=updated,
        deleted_handles=deleted,
        saved_current_dwg=False,
        rollback_token=f"fake-rollback:{patch.transaction_id}",
        errors=errors,
        warnings=[],
    )


def _readback_from_receipt(receipt: ExecutionReceipt) -> ExecutionReceipt:
    return receipt.model_copy(update={"created_handles": [], "updated_handles": [], "deleted_handles": [], "rollback_token": None})


def _read_optional_receipt(workspace: RunWorkspace, artifact_ref: str, *, run_id: str) -> ExecutionReceipt | None:
    try:
        receipt = ExecutionReceipt.model_validate(workspace.read_json_artifact(artifact_ref))
    except FileNotFoundError:
        return None
    if artifact_ref == "readback_receipt.json":
        workspace.write_json_artifact("debug/pre_execution_readback.json", receipt.model_dump(mode="json"))
    return receipt


def _is_repair_patch(patch: CadPatch) -> bool:
    return any(operation.action != "create" for operation in patch.operations)


def _empty_receipt(*, run_id: str, transaction_id: str) -> ExecutionReceipt:
    return ExecutionReceipt(
        schema_version="execution-receipt/v1",
        run_id=run_id,
        transaction_id=transaction_id,
        backend="fake",
        status="succeeded",
        semantic_to_handles={},
        entities=[],
        created_handles=[],
        updated_handles=[],
        deleted_handles=[],
        saved_current_dwg=False,
        rollback_token=None,
        errors=[],
        warnings=[],
    )


def _next_handle(entities: dict[str, EntityReadback]) -> str:
    index = len(entities) + 1
    while True:
        handle = f"F{index:04d}"
        if handle not in entities:
            return handle
        index += 1


def _blocked(run_id: str, reasons: list[str], summary: str) -> ToolEnvelope:
    return ToolEnvelope(status="blocked", run_id=run_id, blocking_reasons=reasons, summary=summary)
