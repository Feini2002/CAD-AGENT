from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from cad_agent.domain.patch import CadPatch, PatchOperation
from cad_agent.domain.receipt import ExecutionReceipt
from cad_agent.policy.safety_policy import Gate0SafetyPolicy


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    checked: list[str] = field(default_factory=list)


def audit_patch_policy(
    patch: CadPatch,
    *,
    policy: Gate0SafetyPolicy | None = None,
    prior_receipt: ExecutionReceipt | None = None,
    repair: bool = False,
) -> PolicyDecision:
    resolved_policy = policy or Gate0SafetyPolicy()
    reasons: list[str] = []
    checked = [
        f"target_layer={_value(patch, 'target_layer')}",
        f"save_current_dwg={_value(patch, 'save_current_dwg', False)}",
        f"repair={repair}",
    ]

    if _value(patch, "target_layer") != resolved_policy.target_layer:
        reasons.append("target_layer_not_preview")
    if _value(patch, "save_current_dwg", False) is not False:
        reasons.append("save_current_dwg_forbidden")

    create_entity_count = 0
    for operation in _operations(patch):
        action = str(_value(operation, "action", ""))
        primitives = list(_value(operation, "primitives", []) or [])
        target_handles = [str(handle) for handle in (_value(operation, "target_handles", []) or [])]

        if action == "create":
            create_entity_count += len(primitives)
            if not primitives:
                reasons.append("create_without_primitives")
        elif action == "update":
            if not target_handles:
                reasons.append("update_without_target_handles")
            reasons.extend(_target_policy_reasons(operation, prior_receipt=prior_receipt, default_code="update_target_outside_prior_receipt"))
        elif action == "delete":
            if not target_handles:
                reasons.append("delete_without_victim_handles")
            if not repair and not resolved_policy.allow_delete:
                reasons.append("delete_forbidden")
            if target_handles:
                reasons.extend(_target_policy_reasons(operation, prior_receipt=prior_receipt, default_code="delete_target_outside_prior_receipt"))
        else:
            reasons.append(f"unsupported_operation:{action}")

        for primitive in primitives:
            if _value(primitive, "layer") != resolved_policy.target_layer:
                reasons.append("primitive_layer_not_preview")

    if create_entity_count > resolved_policy.max_created_entities:
        reasons.append("expected_entity_count_exceeds_budget")

    return PolicyDecision(allowed=not reasons, reasons=_unique(reasons), checked=checked)


def audit_receipt_policy(
    patch: CadPatch,
    *,
    receipt: Any,
    readback: Any,
    policy: Gate0SafetyPolicy | None = None,
) -> PolicyDecision:
    resolved_policy = policy or Gate0SafetyPolicy()
    reasons: list[str] = []
    checked = [
        f"receipt_status={_value(receipt, 'status', '')}",
        f"saved_current_dwg={_value(receipt, 'saved_current_dwg', '<missing>')}",
    ]

    if _value(receipt, "status") != "succeeded":
        reasons.append("backend_receipt_not_succeeded")
    if not _has_value(receipt, "saved_current_dwg"):
        reasons.append("backend_receipt_missing_savedCurrentDwg")
    elif _value(receipt, "saved_current_dwg") is not False:
        reasons.append("backend_saved_current_dwg_violation")

    created_handles = [str(handle) for handle in (_value(receipt, "created_handles", []) or [])]
    if len(created_handles) > resolved_policy.max_created_entities:
        reasons.append("receipt_created_entity_count_exceeds_budget")

    semantic_to_handles = dict(_value(receipt, "semantic_to_handles", {}) or {})
    expected_semantic_ids = [
        str(_value(operation, "semantic_object_id", ""))
        for operation in _operations(patch)
        if str(_value(operation, "action", "")) != "delete"
    ]
    for semantic_id in expected_semantic_ids:
        if semantic_id and not semantic_to_handles.get(semantic_id):
            reasons.append(f"semantic_id_missing:{semantic_id}")

    readback_entities = list(_value(readback, "entities", []) or [])
    readback_handles = {str(_value(entity, "handle", "")) for entity in readback_entities}
    missing_handles = [handle for handle in created_handles if handle not in readback_handles]
    if missing_handles:
        reasons.append(f"readback_handles_missing:{','.join(missing_handles)}")

    for entity in readback_entities:
        if _value(entity, "layer") != resolved_policy.target_layer:
            reasons.append("readback_wrong_layer")
        if _value(entity, "bbox") is None:
            reasons.append("readback_bbox_missing")

    return PolicyDecision(allowed=not reasons, reasons=_unique(reasons), checked=checked)


def handles_for_semantic(receipt: ExecutionReceipt | None, semantic_object_id: str) -> set[str]:
    if receipt is None:
        return set()
    return {str(handle) for handle in receipt.semantic_to_handles.get(semantic_object_id, [])}


def all_receipt_handles(receipt: ExecutionReceipt | None) -> set[str]:
    if receipt is None:
        return set()
    return {str(handle) for handles in receipt.semantic_to_handles.values() for handle in handles}


def _target_policy_reasons(operation: PatchOperation, *, prior_receipt: ExecutionReceipt | None, default_code: str) -> list[str]:
    target_handles = {str(handle) for handle in (_value(operation, "target_handles", []) or [])}
    semantic_object_id = str(_value(operation, "semantic_object_id", ""))
    semantic_handles = handles_for_semantic(prior_receipt, semantic_object_id)
    all_handles = all_receipt_handles(prior_receipt)
    if not target_handles:
        return []
    if not prior_receipt or not target_handles.issubset(all_handles):
        return [default_code]
    if not target_handles.issubset(semantic_handles):
        return ["repair_target_semantic_mismatch"]
    return []


def _operations(patch: CadPatch) -> list[PatchOperation]:
    return list(_value(patch, "operations", []) or [])


def _value(item: Any, name: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def _has_value(item: Any, name: str) -> bool:
    if isinstance(item, dict):
        return name in item
    return hasattr(item, name)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
