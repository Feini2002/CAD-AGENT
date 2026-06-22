from __future__ import annotations

from cad_agent_vnext.domain.drawing import DrawingSnapshot
from cad_agent_vnext.domain.patch import CadPatch
from cad_agent_vnext.domain.receipt import ExecutionReceipt
from cad_agent_vnext.domain.scene import SceneObjectSpec, SceneSpec
from cad_agent_vnext.domain.verification import VerificationCheck
from cad_agent_vnext.planning.footprints import primitives_bbox
from cad_agent_vnext.verification.geometry_checks import (
    bbox_center,
    bbox_inside,
    bboxes_close,
    overlap_ratio,
    union_bboxes,
)
from cad_agent_vnext.verification.receipt_checks import entities_by_handle, object_bboxes


SEVERE_OVERLAP_RATIO = 0.2


def check_scene_geometry(
    *,
    scene: SceneSpec,
    patch: CadPatch,
    receipt: ExecutionReceipt,
    readback: ExecutionReceipt,
    snapshot: DrawingSnapshot,
) -> list[VerificationCheck]:
    checks: list[VerificationCheck] = []
    entities = entities_by_handle(readback)
    mapping = readback.semantic_to_handles or receipt.semantic_to_handles
    observed_bboxes = object_bboxes(mapping, entities)
    desired_bboxes = _desired_bboxes(patch)
    objects = {item.id: item for item in scene.objects}

    for object_id, desired_bbox in desired_bboxes.items():
        observed_bbox = observed_bboxes.get(object_id)
        if observed_bbox is not None and not bboxes_close(observed_bbox, desired_bbox):
            checks.append(
                _check(
                    check_id="bbox_mismatch",
                    subject_ids=[object_id],
                    reason=f"bbox_mismatch:{object_id}",
                    expected={"bbox": desired_bbox},
                    observed={"bbox": observed_bbox},
                    repair_hint="update_target",
                )
            )

    for item in scene.objects:
        if not item.placement.on:
            continue
        object_bbox = observed_bboxes.get(item.id)
        surface_bbox = observed_bboxes.get(item.placement.on)
        if object_bbox is not None and surface_bbox is not None and not bbox_inside(object_bbox, surface_bbox):
            checks.append(
                _check(
                    check_id="inside_surface",
                    subject_ids=[item.id],
                    reason=f"outside_surface:{item.id}:{item.placement.on}",
                    expected={"inside": item.placement.on},
                    observed={"bbox": object_bbox, "surface_bbox": surface_bbox},
                    repair_hint="update_target",
                )
            )

    object_ids = [item.id for item in scene.objects if item.id in observed_bboxes]
    for index, first_id in enumerate(object_ids):
        for second_id in object_ids[index + 1 :]:
            if _is_surface_pair(objects[first_id], objects[second_id]):
                continue
            ratio = overlap_ratio(observed_bboxes[first_id], observed_bboxes[second_id])
            if ratio > SEVERE_OVERLAP_RATIO:
                subject = _repair_subject(objects[first_id], objects[second_id])
                checks.append(
                    _check(
                        check_id="severe_overlap",
                        subject_ids=[subject],
                        reason=f"severe_overlap:{first_id}:{second_id}",
                        observed={"overlap_ratio": ratio},
                        repair_hint="update_target",
                    )
                )

    for item in scene.objects:
        item_bbox = observed_bboxes.get(item.id)
        if item_bbox is None:
            continue
        item_center = bbox_center(item_bbox)
        placement = item.placement
        if placement.in_front_of and placement.in_front_of in observed_bboxes:
            reference_center = bbox_center(observed_bboxes[placement.in_front_of])
            if item_center[1] >= reference_center[1]:
                checks.append(
                    _check(
                        check_id="wrong_side",
                        subject_ids=[item.id],
                        reason=f"wrong_side:{item.id}:in_front_of:{placement.in_front_of}",
                        repair_hint="update_target",
                    )
                )
        if placement.left_of and placement.left_of in observed_bboxes:
            reference_center = bbox_center(observed_bboxes[placement.left_of])
            if item_center[0] >= reference_center[0]:
                checks.append(
                    _check(
                        check_id="wrong_side",
                        subject_ids=[item.id],
                        reason=f"wrong_side:{item.id}:left_of:{placement.left_of}",
                        repair_hint="update_target",
                    )
                )
        if placement.right_of and placement.right_of in observed_bboxes:
            reference_center = bbox_center(observed_bboxes[placement.right_of])
            if item_center[0] <= reference_center[0]:
                checks.append(
                    _check(
                        check_id="wrong_side",
                        subject_ids=[item.id],
                        reason=f"wrong_side:{item.id}:right_of:{placement.right_of}",
                        repair_hint="update_target",
                    )
                )

    for blocked_reason in _nearby_modification_reasons(receipt=receipt, readback=readback, snapshot=snapshot):
        checks.append(
            _check(
                check_id="nearby_handle_protection",
                status="blocked",
                severity="blocking",
                reason=blocked_reason,
                repair_hint="rollback_blocked",
            )
        )

    return checks


def _desired_bboxes(patch: CadPatch) -> dict[str, tuple[float, float, float, float]]:
    bboxes: dict[str, tuple[float, float, float, float]] = {}
    for operation in patch.operations:
        if operation.primitives:
            bboxes[operation.semantic_object_id] = primitives_bbox(operation.primitives)
    return bboxes


def _is_surface_pair(first: SceneObjectSpec, second: SceneObjectSpec) -> bool:
    return first.placement.on == second.id or second.placement.on == first.id


def _repair_subject(first: SceneObjectSpec, second: SceneObjectSpec) -> str:
    if _references(first, second.id):
        return first.id
    if _references(second, first.id):
        return second.id
    return second.id


def _references(item: SceneObjectSpec, reference_id: str) -> bool:
    placement = item.placement
    return reference_id in {
        placement.on,
        placement.in_front_of,
        placement.behind,
        placement.left_of,
        placement.right_of,
        placement.align_x,
        placement.align_y,
    }


def _nearby_modification_reasons(
    *,
    receipt: ExecutionReceipt,
    readback: ExecutionReceipt,
    snapshot: DrawingSnapshot,
) -> list[str]:
    nearby = {entity.handle: entity for entity in snapshot.nearby_entities}
    modified_handles = set(receipt.updated_handles) | set(receipt.deleted_handles)
    reasons = [f"nearby_handle_modified:{handle}" for handle in sorted(modified_handles & set(nearby))]
    readback_entities = entities_by_handle(readback)
    for handle, entity in nearby.items():
        observed = readback_entities.get(handle)
        if observed is not None and observed.bbox != entity.bbox:
            reasons.append(f"nearby_handle_modified:{handle}")
    return sorted(set(reasons))


def _check(
    *,
    check_id: str,
    reason: str,
    status: str = "failed",
    severity: str = "blocking",
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
