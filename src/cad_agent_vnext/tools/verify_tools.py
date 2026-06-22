from __future__ import annotations

from pathlib import Path

from cad_agent_vnext.app.run_workspace import DEFAULT_OUTPUT_ROOT, RunWorkspace
from cad_agent_vnext.domain.drawing import DrawingSnapshot
from cad_agent_vnext.domain.receipt import ExecutionReceipt
from cad_agent_vnext.domain.scene import SceneSpec
from cad_agent_vnext.domain.verification import VerificationReport
from cad_agent_vnext.planning.scene_compiler import CompileSceneResult
from cad_agent_vnext.tools.envelopes import ToolEnvelope
from cad_agent_vnext.verification.repair_planner import plan_scene_repair
from cad_agent_vnext.verification.scene_verifier import verify_scene_execution


def verify_run(*, run_id: str, output_root: str | Path = DEFAULT_OUTPUT_ROOT) -> ToolEnvelope:
    workspace = RunWorkspace.open(output_root=output_root, run_id=run_id)
    missing = _missing_required(
        workspace,
        ["scene_spec.json", "compile_result.json", "execution_receipt.json", "readback_receipt.json", "drawing_snapshot.json"],
    )
    if missing:
        return _blocked(run_id, [f"{missing}_missing"], f"{missing} is required before verify.")

    scene = SceneSpec.model_validate(workspace.read_json_artifact("scene_spec.json"))
    compile_result = CompileSceneResult.model_validate(workspace.read_json_artifact("compile_result.json"))
    receipt = ExecutionReceipt.model_validate(workspace.read_json_artifact("execution_receipt.json"))
    readback = ExecutionReceipt.model_validate(workspace.read_json_artifact("readback_receipt.json"))
    snapshot = DrawingSnapshot.model_validate(workspace.read_json_artifact("drawing_snapshot.json"))
    report = verify_scene_execution(scene=scene, compile_result=compile_result, receipt=receipt, readback=readback, snapshot=snapshot)
    artifact_ref = workspace.write_json_artifact("verification_report.json", report.model_dump(mode="json"))

    if report.overall_status == "passed":
        return ToolEnvelope(
            status="ok",
            run_id=run_id,
            artifact_refs=[artifact_ref],
            next_actions=["closeout"],
            summary="Deterministic verification passed.",
        )
    return ToolEnvelope(
        status="blocked" if report.overall_status == "blocked" else "failed",
        run_id=run_id,
        artifact_refs=[artifact_ref],
        next_actions=["repair", "rollback"],
        blocking_reasons=list(report.blocking_reasons),
        summary="Deterministic verification did not pass.",
    )


def repair_run(*, run_id: str, output_root: str | Path = DEFAULT_OUTPUT_ROOT) -> ToolEnvelope:
    workspace = RunWorkspace.open(output_root=output_root, run_id=run_id)
    missing = _missing_required(workspace, ["scene_spec.json", "compile_result.json", "verification_report.json", "execution_receipt.json"])
    if missing:
        return _blocked(run_id, [f"{missing}_missing"], f"{missing} is required before repair.")

    scene = SceneSpec.model_validate(workspace.read_json_artifact("scene_spec.json"))
    compile_result = CompileSceneResult.model_validate(workspace.read_json_artifact("compile_result.json"))
    report = VerificationReport.model_validate(workspace.read_json_artifact("verification_report.json"))
    receipt = ExecutionReceipt.model_validate(workspace.read_json_artifact("execution_receipt.json"))
    repair = plan_scene_repair(scene=scene, compile_result=compile_result, verification_report=report, prior_receipt=receipt)
    artifact_refs = [workspace.write_json_artifact("repair_plan.json", repair.model_dump(mode="json"))]
    if repair.patch is not None:
        artifact_refs.append(workspace.write_json_artifact("repair_patch.json", repair.patch.model_dump(mode="json")))
        artifact_refs.append(workspace.write_json_artifact("cad_patch.json", repair.patch.model_dump(mode="json")))

    if repair.status != "succeeded":
        return ToolEnvelope(
            status="blocked",
            run_id=run_id,
            artifact_refs=artifact_refs,
            blocking_reasons=list(repair.blocking_reasons),
            summary="No safe local repair patch was produced.",
        )
    return ToolEnvelope(
        status="ok",
        run_id=run_id,
        artifact_refs=artifact_refs,
        next_actions=["execute-preview", "verify"],
        summary="Local repair patch produced for failed semantic IDs only.",
    )


def closeout_run(*, run_id: str, output_root: str | Path = DEFAULT_OUTPUT_ROOT) -> ToolEnvelope:
    workspace = RunWorkspace.open(output_root=output_root, run_id=run_id)
    try:
        report = VerificationReport.model_validate(workspace.read_json_artifact("verification_report.json"))
    except FileNotFoundError:
        return _blocked(run_id, ["verification_report_missing"], "verify must run before closeout.")
    if report.overall_status != "passed":
        return _blocked(run_id, ["verification_not_passed"], "closeout requires deterministic verification to pass.")
    try:
        receipt = ExecutionReceipt.model_validate(workspace.read_json_artifact("execution_receipt.json"))
    except FileNotFoundError:
        return _blocked(run_id, ["execution_receipt_missing"], "execution_receipt.json is required before closeout.")

    closeout = {
        "schemaVersion": "cad-agent-vnext-closeout/v1",
        "runId": run_id,
        "status": "validated",
        "verificationStatus": report.overall_status,
        "savedCurrentDwg": receipt.saved_current_dwg,
        "evidenceRefs": workspace.evidence_refs(),
        "allowedClaims": list(report.allowed_claims),
    }
    artifact_ref = workspace.write_json_artifact("closeout.json", closeout)
    return ToolEnvelope(
        status="ok",
        run_id=run_id,
        artifact_refs=[artifact_ref],
        summary="Run closeout completed with deterministic fake verification evidence.",
    )


def _missing_required(workspace: RunWorkspace, refs: list[str]) -> str | None:
    for artifact_ref in refs:
        try:
            workspace.artifact_path(artifact_ref).read_text(encoding="utf-8")
        except FileNotFoundError:
            return artifact_ref.removesuffix(".json")
    return None


def _blocked(run_id: str, reasons: list[str], summary: str) -> ToolEnvelope:
    return ToolEnvelope(status="blocked", run_id=run_id, blocking_reasons=reasons, summary=summary)
