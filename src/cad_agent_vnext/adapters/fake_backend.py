from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from cad_agent_vnext.domain.common import BBox2D
from cad_agent_vnext.domain.drawing import DrawingEntitySnapshot, DrawingSnapshot
from cad_agent_vnext.domain.patch import CadPatch, PatchOperation
from cad_agent_vnext.domain.primitives import Primitive
from cad_agent_vnext.domain.receipt import EntityReadback, ExecutionReceipt


FailureMode = Literal["wrong_layer"] | None


@dataclass(frozen=True)
class StoredEntity:
    handle: str
    semantic_object_id: str
    entity_type: str
    layer: str
    bbox: BBox2D | None

    def as_readback(self) -> EntityReadback:
        return EntityReadback(handle=self.handle, entity_type=self.entity_type, layer=self.layer, bbox=self.bbox)

    def as_snapshot(self) -> DrawingEntitySnapshot:
        return DrawingEntitySnapshot(handle=self.handle, entity_type=self.entity_type, layer=self.layer, bbox=self.bbox)


class FakeCadBackend:
    def __init__(self, *, failure_mode: FailureMode = None, partial_create_after: int | None = None) -> None:
        self.failure_mode = failure_mode
        self.partial_create_after = partial_create_after
        self._next_handle = 1
        self._entities: dict[str, StoredEntity] = {}
        self._semantic_to_handles: dict[str, list[str]] = {}
        self._transactions: dict[str, ExecutionReceipt] = {}
        self._rollback_snapshots: dict[str, tuple[dict[str, StoredEntity], dict[str, list[str]]]] = {}

    def inspect_document(self, *, run_id: str) -> DrawingSnapshot:
        return DrawingSnapshot(
            schema_version="drawing-snapshot/v1",
            run_id=run_id,
            document_id="fake-document",
            units="mm",
            current_space="model",
            active_layer="CODEX_PREVIEW",
            saved=False,
            target_region=None,
            nearby_entities=[entity.as_snapshot() for entity in self._entities.values()],
            snapshot_hash=f"fake:{len(self._entities)}:{self._next_handle}",
        )

    def apply_patch(self, patch: CadPatch) -> ExecutionReceipt:
        if patch.transaction_id in self._transactions:
            return self._receipt(
                patch=patch,
                status="blocked",
                errors=["duplicate_transaction_id"],
                rollback_token=None,
            )

        snapshot = (dict(self._entities), {key: list(value) for key, value in self._semantic_to_handles.items()})
        rollback_token = f"rollback:{patch.transaction_id}"
        self._rollback_snapshots[rollback_token] = snapshot

        created: list[str] = []
        updated: list[str] = []
        deleted: list[str] = []
        errors: list[str] = []
        status: Literal["succeeded", "blocked", "failed"] = "succeeded"

        for operation in patch.operations:
            if operation.action == "create":
                for primitive in operation.primitives:
                    if self.partial_create_after is not None and len(created) >= self.partial_create_after:
                        status = "failed"
                        errors.append("partial_create")
                        break
                    handle = self._new_handle()
                    entity = self._entity_from_primitive(handle, operation.semantic_object_id, primitive)
                    if self.failure_mode == "wrong_layer":
                        entity = StoredEntity(
                            handle=entity.handle,
                            semantic_object_id=entity.semantic_object_id,
                            entity_type=entity.entity_type,
                            layer="A-WALL",
                            bbox=entity.bbox,
                        )
                        status = "failed"
                        errors.append("wrong_layer_readback")
                    self._store(entity)
                    created.append(handle)
                if status == "failed":
                    break
            elif operation.action == "update":
                result = self._update_operation(operation)
                if result is None:
                    status = "failed"
                    errors.append("missing_handle")
                    break
                updated.extend(result)
            elif operation.action == "delete":
                result = self._delete_operation(operation)
                if result is None:
                    status = "failed"
                    errors.append("missing_handle")
                    break
                deleted.extend(result)

        receipt = self._receipt(
            patch=patch,
            status=status,
            created_handles=created,
            updated_handles=updated,
            deleted_handles=deleted,
            rollback_token=rollback_token,
            errors=errors,
        )
        self._transactions[patch.transaction_id] = receipt
        return receipt

    def readback(self, *, transaction_id: str) -> ExecutionReceipt:
        return ExecutionReceipt(
            schema_version="execution-receipt/v1",
            run_id="readback",
            transaction_id=transaction_id,
            backend="fake",
            status="succeeded",
            semantic_to_handles={key: list(value) for key, value in self._semantic_to_handles.items()},
            entities=[entity.as_readback() for entity in self._entities.values()],
            created_handles=[],
            updated_handles=[],
            deleted_handles=[],
            saved_current_dwg=False,
            rollback_token=None,
            errors=[],
            warnings=[],
        )

    def capture_view(self, *, transaction_id: str, output_path: str) -> str:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"backend": "fake", "transactionId": transaction_id, "visualAidOnly": True}, sort_keys=True),
            encoding="utf-8",
        )
        return str(path)

    def rollback(self, *, rollback_token: str) -> ExecutionReceipt:
        snapshot = self._rollback_snapshots.get(rollback_token)
        if snapshot is None:
            return ExecutionReceipt(
                schema_version="execution-receipt/v1",
                run_id="rollback",
                transaction_id=rollback_token,
                backend="fake",
                status="blocked",
                semantic_to_handles={key: list(value) for key, value in self._semantic_to_handles.items()},
                entities=[entity.as_readback() for entity in self._entities.values()],
                created_handles=[],
                updated_handles=[],
                deleted_handles=[],
                saved_current_dwg=False,
                rollback_token=None,
                errors=["unknown_rollback_token"],
                warnings=[],
            )
        self._entities, self._semantic_to_handles = (
            dict(snapshot[0]),
            {key: list(value) for key, value in snapshot[1].items()},
        )
        return ExecutionReceipt(
            schema_version="execution-receipt/v1",
            run_id="rollback",
            transaction_id=rollback_token,
            backend="fake",
            status="succeeded",
            semantic_to_handles={key: list(value) for key, value in self._semantic_to_handles.items()},
            entities=[entity.as_readback() for entity in self._entities.values()],
            created_handles=[],
            updated_handles=[],
            deleted_handles=[],
            saved_current_dwg=False,
            rollback_token=None,
            errors=[],
            warnings=[],
        )

    def _new_handle(self) -> str:
        handle = f"F{self._next_handle:04d}"
        self._next_handle += 1
        return handle

    def _store(self, entity: StoredEntity) -> None:
        self._entities[entity.handle] = entity
        handles = self._semantic_to_handles.setdefault(entity.semantic_object_id, [])
        if entity.handle not in handles:
            handles.append(entity.handle)

    def _entity_from_primitive(self, handle: str, semantic_object_id: str, primitive: Primitive) -> StoredEntity:
        return StoredEntity(
            handle=handle,
            semantic_object_id=semantic_object_id,
            entity_type=primitive.expected_entity_type,
            layer=primitive.layer,
            bbox=bbox_for_primitive(primitive),
        )

    def _update_operation(self, operation: PatchOperation) -> list[str] | None:
        if not operation.target_handles:
            return None
        updated: list[str] = []
        primitive = operation.primitives[0] if operation.primitives else None
        for handle in operation.target_handles:
            current = self._entities.get(handle)
            if current is None:
                return None
            if primitive is not None:
                self._entities[handle] = StoredEntity(
                    handle=handle,
                    semantic_object_id=operation.semantic_object_id,
                    entity_type=primitive.expected_entity_type,
                    layer=primitive.layer,
                    bbox=bbox_for_primitive(primitive),
                )
            updated.append(handle)
        return updated

    def _delete_operation(self, operation: PatchOperation) -> list[str] | None:
        if not operation.target_handles:
            return None
        deleted: list[str] = []
        for handle in operation.target_handles:
            entity = self._entities.pop(handle, None)
            if entity is None:
                return None
            handles = self._semantic_to_handles.get(entity.semantic_object_id, [])
            self._semantic_to_handles[entity.semantic_object_id] = [item for item in handles if item != handle]
            deleted.append(handle)
        return deleted

    def _receipt(
        self,
        *,
        patch: CadPatch,
        status: Literal["succeeded", "blocked", "failed"],
        created_handles: list[str] | None = None,
        updated_handles: list[str] | None = None,
        deleted_handles: list[str] | None = None,
        rollback_token: str | None = None,
        errors: list[str] | None = None,
    ) -> ExecutionReceipt:
        return ExecutionReceipt(
            schema_version="execution-receipt/v1",
            run_id=patch.run_id,
            transaction_id=patch.transaction_id,
            backend="fake",
            status=status,
            semantic_to_handles={key: list(value) for key, value in self._semantic_to_handles.items()},
            entities=[entity.as_readback() for entity in self._entities.values()],
            created_handles=created_handles or [],
            updated_handles=updated_handles or [],
            deleted_handles=deleted_handles or [],
            saved_current_dwg=False,
            rollback_token=rollback_token,
            errors=errors or [],
            warnings=[],
        )


def bbox_for_primitive(primitive: Primitive) -> BBox2D | None:
    geometry = primitive.geometry
    if primitive.primitive_type == "rectangle":
        origin = geometry["origin"]
        x = float(origin[0])
        y = float(origin[1])
        return (x, y, x + float(geometry["width"]), y + float(geometry["depth"]))
    if primitive.primitive_type == "circle":
        center = geometry["center"]
        radius = float(geometry["radius"])
        return (float(center[0]) - radius, float(center[1]) - radius, float(center[0]) + radius, float(center[1]) + radius)
    if primitive.primitive_type == "line":
        start = geometry["start"]
        end = geometry["end"]
        xs = [float(start[0]), float(end[0])]
        ys = [float(start[1]), float(end[1])]
        return (min(xs), min(ys), max(xs), max(ys))
    if primitive.primitive_type == "polyline":
        points = geometry["points"]
        xs = [float(point[0]) for point in points]
        ys = [float(point[1]) for point in points]
        return (min(xs), min(ys), max(xs), max(ys))
    if primitive.primitive_type == "text":
        insert = geometry["insert"]
        width = float(geometry.get("width", 0))
        height = float(geometry.get("height", 0))
        return (float(insert[0]), float(insert[1]), float(insert[0]) + width, float(insert[1]) + height)
    return None
