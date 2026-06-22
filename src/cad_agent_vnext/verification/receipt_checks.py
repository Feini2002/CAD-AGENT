from __future__ import annotations

from collections import Counter

from cad_agent_vnext.domain.patch import CadPatch
from cad_agent_vnext.domain.receipt import EntityReadback, ExecutionReceipt
from cad_agent_vnext.domain.verification import VerificationCheck
from cad_agent_vnext.verification.geometry_checks import union_bboxes


PREVIEW_LAYER = "CODEX_PREVIEW"


def entities_by_handle(receipt: ExecutionReceipt) -> dict[str, EntityReadback]:
    return {entity.handle: entity for entity in receipt.entities}


def expected_types_by_object(patch: CadPatch) -> dict[str, list[str]]:
    expected: dict[str, list[str]] = {}
    for operation in patch.operations:
        expected.setdefault(operation.semantic_object_id, []).extend(
            primitive.expected_entity_type for primitive in operation.primitives
        )
    return expected


def object_bboxes(mapping: dict[str, list[str]], entities: dict[str, EntityReadback]) -> dict[str, tuple[float, float, float, float]]:
    boxes: dict[str, tuple[float, float, float, float]] = {}
    for object_id, handles in mapping.items():
        bbox = union_bboxes(entity.bbox for handle in handles if (entity := entities.get(handle)) and entity.bbox is not None)
        if bbox is not None:
            boxes[object_id] = bbox
    return boxes


def check_receipt_integrity(
    *,
    patch: CadPatch,
    receipt: ExecutionReceipt,
    readback: ExecutionReceipt,
) -> list[VerificationCheck]:
    checks: list[VerificationCheck] = []
    expected_types = expected_types_by_object(patch)
    readback_entities = entities_by_handle(readback)
    effective_mapping = readback.semantic_to_handles or receipt.semantic_to_handles

    if getattr(receipt, "saved_current_dwg", False) is not False:
        checks.append(
            _check(
                check_id="saved_current_dwg",
                status="blocked",
                severity="blocking",
                reason="saved_current_dwg_true",
            )
        )

    if receipt.status != "succeeded":
        checks.append(
            _check(
                check_id="receipt_status",
                status="failed",
                severity="warning",
                reason=f"receipt_status:{receipt.status}",
                observed={"errors": list(receipt.errors)},
            )
        )

    for object_id, types in expected_types.items():
        handles = list(effective_mapping.get(object_id) or receipt.semantic_to_handles.get(object_id) or [])
        entities = [readback_entities[handle] for handle in handles if handle in readback_entities]

        if not handles or not entities:
            checks.append(
                _check(
                    check_id="missing_object",
                    status="failed",
                    severity="blocking",
                    subject_ids=[object_id],
                    reason=f"missing_object:{object_id}",
                    expected={"entity_count": len(types)},
                    observed={"handles": handles},
                    repair_hint="add_missing",
                )
            )
            continue

        missing_handles = [handle for handle in receipt.semantic_to_handles.get(object_id, []) if handle not in readback_entities]
        if missing_handles:
            checks.append(
                _check(
                    check_id="readback_missing",
                    status="failed",
                    severity="blocking",
                    subject_ids=[object_id],
                    reason=f"readback_missing:{object_id}",
                    observed={"missing_handles": missing_handles},
                    repair_hint="add_missing",
                )
            )

        wrong_layers = [entity.handle for entity in entities if entity.layer != PREVIEW_LAYER]
        if wrong_layers:
            checks.append(
                _check(
                    check_id="wrong_layer",
                    status="blocked",
                    severity="blocking",
                    subject_ids=[object_id],
                    reason=f"wrong_layer:{object_id}",
                    expected={"layer": PREVIEW_LAYER},
                    observed={"handles": wrong_layers},
                    repair_hint="rollback_blocked",
                )
            )

        empty_bbox_handles = [entity.handle for entity in entities if entity.bbox is None]
        if empty_bbox_handles:
            checks.append(
                _check(
                    check_id="readback_bbox_empty",
                    status="failed",
                    severity="blocking",
                    subject_ids=[object_id],
                    reason=f"readback_bbox_empty:{object_id}",
                    observed={"handles": empty_bbox_handles},
                    repair_hint="update_target",
                )
            )

        observed_types = [entity.entity_type for entity in entities]
        if Counter(observed_types) != Counter(types):
            checks.append(
                _check(
                    check_id="entity_type_mismatch",
                    status="failed",
                    severity="blocking",
                    subject_ids=[object_id],
                    reason=f"entity_type_mismatch:{object_id}",
                    expected={"entity_types": types},
                    observed={"entity_types": observed_types},
                    repair_hint="update_target",
                )
            )

    return checks


def _check(
    *,
    check_id: str,
    status: str,
    severity: str,
    reason: str,
    subject_ids: list[str] | None = None,
    expected: dict | None = None,
    observed: dict | None = None,
    repair_hint: str | None = None,
) -> VerificationCheck:
    observed_payload = dict(observed or {})
    observed_payload["reason"] = reason
    return VerificationCheck(
        check_id=check_id,
        status=status,
        severity=severity,
        subject_ids=subject_ids or [],
        expected=expected or {},
        observed=observed_payload,
        repair_hint=repair_hint,
    )
