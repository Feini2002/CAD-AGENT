from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import Field

from cad_agent.domain.common import StrictModel
from cad_agent.domain.patch import CadPatch, PatchOperation
from cad_agent.domain.receipt import ExecutionReceipt
from cad_agent.domain.scene import SceneSpec
from cad_agent.domain.verification import VerificationReport
from cad_agent.planning.scene_compiler import CompileSceneResult


class RepairPlanResult(StrictModel):
    status: Literal["succeeded", "blocked"]
    patch: CadPatch | None = None
    repaired_semantic_ids: list[str] = Field(default_factory=list)
    repair_round: int = 1
    blocking_reasons: list[str] = Field(default_factory=list)


def plan_scene_repair(
    *,
    scene: SceneSpec,
    compile_result: CompileSceneResult,
    verification_report: VerificationReport,
    prior_receipt: ExecutionReceipt,
    repair_round: int = 1,
    max_rounds: int = 2,
) -> RepairPlanResult:
    if repair_round > max_rounds:
        return _blocked(repair_round=repair_round, reasons=["max_repair_rounds_exceeded"])
    if verification_report.overall_status == "passed":
        return _blocked(repair_round=repair_round, reasons=["no_repair_needed"])
    if compile_result.patch is None:
        return _blocked(repair_round=repair_round, reasons=["compile_result_missing_patch"])
    if _has_safety_block(verification_report):
        return _blocked(repair_round=repair_round, reasons=["safety_failure_not_repairable"])

    original_operations = {operation.semantic_object_id: operation for operation in compile_result.patch.operations}
    repair_ids = _repair_ids(scene=scene, report=verification_report)
    operations: list[PatchOperation] = []
    for object_id in repair_ids:
        original = original_operations.get(object_id)
        if original is None:
            continue
        handles = prior_receipt.semantic_to_handles.get(object_id, [])
        if _needs_create(verification_report, object_id) or not handles:
            operations.append(
                PatchOperation(
                    op_id=f"repair:{repair_round}:create:{object_id}",
                    action="create",
                    semantic_object_id=object_id,
                    primitives=list(original.primitives),
                )
            )
        else:
            operations.append(
                PatchOperation(
                    op_id=f"repair:{repair_round}:update:{object_id}",
                    action="update",
                    semantic_object_id=object_id,
                    target_handles=list(handles),
                    primitives=list(original.primitives),
                )
            )

    if not operations:
        return _blocked(repair_round=repair_round, reasons=["no_repairable_failures"])

    transaction_id = _repair_transaction_id(prior_receipt.transaction_id, repair_round, operations)
    patch = CadPatch(
        schema_version="cad-patch/v1",
        run_id=scene.run_id,
        transaction_id=transaction_id,
        target_layer="CODEX_PREVIEW",
        operations=operations,
        save_current_dwg=False,
        forbidden_effects=["dwg_save", "formal_layer_write"],
    )
    return RepairPlanResult(
        status="succeeded",
        patch=patch,
        repaired_semantic_ids=[operation.semantic_object_id for operation in operations],
        repair_round=repair_round,
        blocking_reasons=[],
    )


def _has_safety_block(report: VerificationReport) -> bool:
    return any(check.status == "blocked" or check.repair_hint == "rollback_blocked" for check in report.checks)


def _repair_ids(*, scene: SceneSpec, report: VerificationReport) -> list[str]:
    scene_order = [item.id for item in scene.objects]
    wanted: set[str] = set()
    for check in report.checks:
        if check.status == "passed" or check.repair_hint not in {"add_missing", "update_target"}:
            continue
        wanted.update(check.subject_ids)
    return [object_id for object_id in scene_order if object_id in wanted]


def _needs_create(report: VerificationReport, object_id: str) -> bool:
    return any(
        check.status != "passed" and check.repair_hint == "add_missing" and object_id in check.subject_ids
        for check in report.checks
    )


def _repair_transaction_id(prior_transaction_id: str, repair_round: int, operations: list[PatchOperation]) -> str:
    payload = {
        "prior": prior_transaction_id,
        "repair_round": repair_round,
        "operations": [operation.model_dump(mode="json") for operation in operations],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"repair-{hashlib.sha256(encoded).hexdigest()[:24]}"


def _blocked(*, repair_round: int, reasons: list[str]) -> RepairPlanResult:
    return RepairPlanResult(status="blocked", patch=None, repaired_semantic_ids=[], repair_round=repair_round, blocking_reasons=reasons)
