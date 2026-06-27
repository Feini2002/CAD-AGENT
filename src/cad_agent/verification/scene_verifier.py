from __future__ import annotations

from cad_agent.domain.drawing import DrawingSnapshot
from cad_agent.domain.receipt import ExecutionReceipt
from cad_agent.domain.scene import SceneSpec
from cad_agent.domain.verification import VerificationCheck, VerificationReport
from cad_agent.planning.scene_compiler import CompileSceneResult
from cad_agent.verification.receipt_checks import check_receipt_integrity
from cad_agent.verification.relation_checks import check_scene_geometry


def verify_scene_execution(
    *,
    scene: SceneSpec,
    compile_result: CompileSceneResult,
    receipt: ExecutionReceipt,
    readback: ExecutionReceipt | None = None,
    snapshot: DrawingSnapshot,
) -> VerificationReport:
    if compile_result.patch is None:
        return VerificationReport(
            schema_version="verification-report/v1",
            run_id=scene.run_id,
            overall_status="blocked",
            checks=[
                VerificationCheck(
                    check_id="compile_result",
                    status="blocked",
                    severity="blocking",
                    observed={"reason": "compile_result_missing_patch"},
                )
            ],
            allowed_claims=[],
            blocking_reasons=["compile_result_missing_patch"],
        )

    effective_readback = readback or receipt
    checks = [
        *check_receipt_integrity(patch=compile_result.patch, receipt=receipt, readback=effective_readback),
        *check_scene_geometry(
            scene=scene,
            patch=compile_result.patch,
            receipt=receipt,
            readback=effective_readback,
            snapshot=snapshot,
        ),
    ]
    blocking_reasons = _blocking_reasons(checks)
    return VerificationReport(
        schema_version="verification-report/v1",
        run_id=scene.run_id,
        overall_status=_overall_status(checks),
        checks=checks,
        allowed_claims=_allowed_claims(checks),
        blocking_reasons=blocking_reasons,
    )


def _overall_status(checks: list[VerificationCheck]) -> str:
    failed = [check for check in checks if check.status != "passed"]
    if not failed:
        return "passed"
    if any(check.status == "blocked" or check.severity == "blocking" and check.repair_hint == "rollback_blocked" for check in failed):
        return "blocked"
    return "failed"


def _allowed_claims(checks: list[VerificationCheck]) -> list[str]:
    if _overall_status(checks) != "passed":
        return []
    return ["deterministic_verification_passed", "preview_geometry_verified", "savedCurrentDwg=false"]


def _blocking_reasons(checks: list[VerificationCheck]) -> list[str]:
    reasons: list[str] = []
    for check in checks:
        if check.status == "passed":
            continue
        reason = check.observed.get("reason")
        if isinstance(reason, str):
            reasons.append(reason)
        else:
            reasons.append(check.check_id)
    return reasons
