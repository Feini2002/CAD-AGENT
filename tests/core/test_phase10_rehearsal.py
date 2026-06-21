from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest

from tests.helpers import PROJECT_ROOT, temporary_artifact_dir


def _cad_plan(*, layer: str = "CODEX_PREVIEW") -> dict[str, object]:
    return {
        "version": "0.1",
        "domain": "generic",
        "intent": "draw_object",
        "object": {
            "type": "table",
            "name": "Phase 10 rehearsal table",
            "width": 900,
            "depth": 450,
        },
        "placement": {
            "mode": "absolute",
            "base_point": [76000, 42000, 0],
        },
        "drawing": {
            "layer": layer,
            "include_label": False,
            "include_dimensions": False,
        },
        "confidence": 0.91,
        "needs_confirmation": False,
    }


def _scope(
    *,
    confirmed: bool = True,
    run_count: int = 2,
    layer: str = "CODEX_PREVIEW",
    phase9_exit_run_dir: str = "",
    backend: str = "cad-session-host",
) -> dict[str, object]:
    return {
        "scopeId": "phase10.table.rehearsal",
        "scopeConfirmed": confirmed,
        "objectFamily": "table",
        "capability": "single_table_preview_repeatability",
        "backend": backend,
        "runCount": run_count,
        "phase9ExitRunDir": phase9_exit_run_dir,
        "cadPlans": [_cad_plan(layer=layer)],
    }


def _verified_phase9_run(root) -> object:
    from core.contracts.phase9_preview import run_phase9_single_preview
    from core.verification.fake_cad_driver import FakeCadDriver

    phase9_root = root / "phase9_verified"
    run_phase9_single_preview(
        cad_plan=_cad_plan(),
        output_dir=phase9_root,
        driver_factory=FakeCadDriver,
        driver_backend="cad_session_host",
    )
    return phase9_root


def _verified_rehearsal_run(root, name: str) -> object:
    from core.contracts.phase9_preview import run_phase9_single_preview
    from core.verification.fake_cad_driver import FakeCadDriver

    run_root = root / name
    run_phase9_single_preview(
        cad_plan=_cad_plan(),
        output_dir=run_root,
        driver_factory=FakeCadDriver,
        driver_backend="cad_session_host",
    )
    return run_root


def _mutate_report(run_root, **updates: object) -> None:
    report_path = run_root / "phase9_preview_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report.update(updates)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_ready_rehearsal_plan(root) -> object:
    from core.contracts.phase10_rehearsal import prepare_phase10_rehearsal_plan

    phase9_root = _verified_phase9_run(root)
    result = prepare_phase10_rehearsal_plan(
        scope=_scope(run_count=2, phase9_exit_run_dir=str(phase9_root)),
        output_dir=root,
    )
    return result["planPath"]


def _fake_live_preview_executor(*, cad_plan, output_dir, backend, run_id):
    from core.contracts.phase9_preview import run_phase9_single_preview
    from core.verification.fake_cad_driver import FakeCadDriver

    return run_phase9_single_preview(
        cad_plan=dict(cad_plan),
        output_dir=output_dir,
        driver_factory=FakeCadDriver,
        driver_backend="cad_session_host",
        task_id=str(run_id),
    ).report


def _confirmation_statement() -> str:
    return "confirm phase10.table.rehearsal uses CODEX_PREVIEW only, runCount=2, no current DWG save"


def _write_ready_scope_receipt(root) -> object:
    from core.contracts.phase10_rehearsal import build_phase10_rehearsal_scope_receipt

    plan_path = _write_ready_rehearsal_plan(root)
    build_phase10_rehearsal_scope_receipt(
        plan_path=plan_path,
        output_dir=root,
        live_runs_confirmed=True,
        confirmation_statement=_confirmation_statement(),
    )
    return plan_path


def _write_ready_launch_packet(root) -> object:
    from core.contracts.phase10_rehearsal import build_phase10_rehearsal_launch_packet

    plan_path = _write_ready_scope_receipt(root)
    build_phase10_rehearsal_launch_packet(
        plan_path=plan_path,
        output_dir=root,
        live_runs_confirmed=True,
        env={
            "CAD_SESSION_HOST_URL": "http://127.0.0.1:39001",
            "CAD_SESSION_TOKEN": "test-token",
        },
    )
    return plan_path


def _write_production_like_closeout_artifacts(root) -> object:
    from core.contracts.phase10_rehearsal import evaluate_phase10_rehearsal_runs

    plan_path = _write_ready_launch_packet(root)
    plan = json.loads((root / "phase10_rehearsal_plan.json").read_text(encoding="utf-8"))
    run_01 = _verified_rehearsal_run(root, "run_01")
    run_02 = _verified_rehearsal_run(root, "run_02")
    aggregate = evaluate_phase10_rehearsal_runs(run_dirs=[run_01, run_02], output_dir=root)
    execution_path = root / "phase10_rehearsal_execution.json"
    execution = {
        "schemaVersion": "phase10-rehearsal-execution/v1",
        "phase": "Phase 10",
        "packageId": "phase10.focused-harness-rehearsal",
        "taskId": "phase10.focused-harness-rehearsal.execute",
        "status": "ready",
        "verificationStatus": "verified",
        "cadGeometryVerified": True,
        "cadWritesAttempted": True,
        "liveRunsConfirmed": True,
        "executorMode": "cad_agent_harness_preview",
        "plannedRunCount": 2,
        "executedRunCount": 2,
        "planPath": str(plan_path),
        "scopeReceiptPath": str(root / "phase10_rehearsal_scope_receipt.json"),
        "outputDir": str(root),
        "executionPath": str(execution_path),
        "runSpecs": plan["runSpecs"],
        "runResults": [
            {
                "runId": "phase10-rehearsal-run-01",
                "outputDir": str(run_01),
                "status": "geometry_verified",
                "verificationStatus": "verified",
            },
            {
                "runId": "phase10-rehearsal-run-02",
                "outputDir": str(run_02),
                "status": "geometry_verified",
                "verificationStatus": "verified",
            },
        ],
        "aggregateResult": aggregate,
        "blockingReasons": [],
        "missingEvidence": [],
        "allowedEffects": ["phase10_rehearsal_live_preview_runs"],
        "forbiddenEffects": [],
        "completionBoundary": "test-production-like-execution-artifact",
        "notEvidenceFor": ["training_resume", "table_c_progress", "plugin_readiness"],
    }
    execution_path.write_text(json.dumps(execution, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return execution_path


class Phase10RehearsalTests(unittest.TestCase):
    def test_rehearsal_scope_proposal_derives_candidate_without_confirming_or_writing_cad(self) -> None:
        from core.contracts.phase10_rehearsal import build_phase10_rehearsal_scope_proposal

        with temporary_artifact_dir("phase10_scope_proposal_ready") as root:
            phase9_root = _verified_phase9_run(root)
            result = build_phase10_rehearsal_scope_proposal(
                phase9_exit_run_dir=phase9_root,
                output_dir=root,
            )
            proposal = json.loads((root / "phase10_rehearsal_scope_proposal.json").read_text(encoding="utf-8"))

        candidate = result["candidateScope"]
        self.assertEqual(result["schemaVersion"], "phase10-rehearsal-scope-proposal/v1")
        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["proposalReady"])
        self.assertFalse(result["scopeConfirmed"])
        self.assertFalse(result["liveRunsConfirmed"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertEqual(candidate["scopeConfirmed"], False)
        self.assertEqual(candidate["objectFamily"], "table")
        self.assertEqual(candidate["capability"], "single_table_preview_repeatability")
        self.assertEqual(candidate["backend"], "cad-session-host")
        self.assertEqual(candidate["runCount"], 2)
        self.assertEqual(candidate["cadPlans"][0]["drawing"]["layer"], "CODEX_PREVIEW")
        self.assertEqual(result["blockingReasons"], [])
        self.assertIn("operator_scope_confirmation", result["nextAllowedEffects"])
        self.assertIn("phase10_scope_confirmation", result["notEvidenceFor"])
        self.assertEqual(proposal, result)

    def test_rehearsal_scope_proposal_blocks_without_ready_phase9_evidence(self) -> None:
        from core.contracts.phase10_rehearsal import build_phase10_rehearsal_scope_proposal

        with temporary_artifact_dir("phase10_scope_proposal_missing_source") as root:
            result = build_phase10_rehearsal_scope_proposal(
                phase9_exit_run_dir=root / "missing_phase9_run",
                output_dir=root,
            )

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["proposalReady"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertIn("phase10_scope_proposal_phase9_exit_invalid", result["blockingReasons"])
        self.assertIn("phase10_scope_proposal_cad_plan_missing", result["blockingReasons"])
        self.assertEqual(result["nextAllowedEffects"], [])

    def test_harness_rehearsal_scope_proposal_command_outputs_json_without_cad_write(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        with temporary_artifact_dir("phase10_harness_scope_proposal") as root:
            phase9_root = _verified_phase9_run(root)
            result = run_harness_command(
                "rehearsal-scope-proposal",
                run_dir=phase9_root,
                output_dir=root,
            )

        self.assertEqual(result["schemaVersion"], "cad-agent-harness-result/v1")
        self.assertEqual(result["command"], "rehearsal-scope-proposal")
        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["proposalReady"])
        self.assertFalse(result["scopeConfirmed"])
        self.assertFalse(result["cadGeometryVerified"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertEqual(result["candidateScope"]["objectFamily"], "table")

    def test_script_rehearsal_scope_proposal_outputs_json_result(self) -> None:
        script = PROJECT_ROOT / "scripts" / "cad_agent_harness.py"

        with temporary_artifact_dir("phase10_harness_scope_proposal_script") as root:
            phase9_root = _verified_phase9_run(root)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "rehearsal-scope-proposal",
                    "--run-dir",
                    str(phase9_root),
                    "--output-dir",
                    str(root),
                    "--json",
                ],
                cwd=PROJECT_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "rehearsal-scope-proposal")
        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["proposalReady"])
        self.assertFalse(result["scopeConfirmed"])
        self.assertFalse(result["cadWritesAttempted"])

    def test_rehearsal_plan_blocks_without_confirmed_scope_and_does_not_plan_runs(self) -> None:
        from core.contracts.phase10_rehearsal import prepare_phase10_rehearsal_plan

        with temporary_artifact_dir("phase10_unconfirmed_scope") as root:
            result = prepare_phase10_rehearsal_plan(scope=_scope(confirmed=False), output_dir=root)
            plan = json.loads((root / "phase10_rehearsal_plan.json").read_text(encoding="utf-8"))

        self.assertEqual(result["schemaVersion"], "phase10-rehearsal-plan-result/v1")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["cadWritesAttempted"])
        self.assertEqual(result["runSpecs"], [])
        self.assertEqual(plan["runSpecs"], [])
        self.assertIn("phase10_scope_not_confirmed", result["blockingReasons"])

    def test_rehearsal_plan_requires_codex_preview_and_at_least_two_runs(self) -> None:
        from core.contracts.phase10_rehearsal import prepare_phase10_rehearsal_plan

        with temporary_artifact_dir("phase10_invalid_scope") as root:
            phase9_root = _verified_phase9_run(root)
            result = prepare_phase10_rehearsal_plan(
                scope=_scope(run_count=1, layer="0", phase9_exit_run_dir=str(phase9_root)),
                output_dir=root,
            )

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["cadWritesAttempted"])
        self.assertIn("phase10_repetition_count_too_low", result["blockingReasons"])
        self.assertIn("phase10_non_preview_layer_forbidden", result["blockingReasons"])

    def test_rehearsal_plan_requires_ready_phase9_exit_reference(self) -> None:
        from core.contracts.phase10_rehearsal import prepare_phase10_rehearsal_plan

        with temporary_artifact_dir("phase10_missing_phase9_exit_ref") as root:
            result = prepare_phase10_rehearsal_plan(scope=_scope(run_count=2), output_dir=root)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("phase9_exit_reference_missing", result["blockingReasons"])

    def test_rehearsal_plan_blocks_fake_backend(self) -> None:
        from core.contracts.phase10_rehearsal import prepare_phase10_rehearsal_plan

        with temporary_artifact_dir("phase10_fake_backend_scope") as root:
            phase9_root = _verified_phase9_run(root)
            result = prepare_phase10_rehearsal_plan(
                scope=_scope(
                    run_count=2,
                    backend="fake-driver",
                    phase9_exit_run_dir=str(phase9_root),
                ),
                output_dir=root,
            )

        self.assertEqual(result["status"], "blocked")
        self.assertIn("phase10_real_backend_required", result["blockingReasons"])

    def test_rehearsal_plan_materializes_repeatable_preview_runs_without_executing_cad(self) -> None:
        from core.contracts.phase10_rehearsal import prepare_phase10_rehearsal_plan

        with temporary_artifact_dir("phase10_ready_scope") as root:
            phase9_root = _verified_phase9_run(root)
            result = prepare_phase10_rehearsal_plan(
                scope=_scope(run_count=2, phase9_exit_run_dir=str(phase9_root)),
                output_dir=root,
            )
            plan = json.loads((root / "phase10_rehearsal_plan.json").read_text(encoding="utf-8"))
            scope = json.loads((root / "phase10_rehearsal_scope.json").read_text(encoding="utf-8"))

        self.assertEqual(result["status"], "ready")
        self.assertFalse(result["cadWritesAttempted"])
        self.assertEqual(result["phase"], "Phase 10")
        self.assertEqual(result["backend"], "cad-session-host")
        self.assertEqual(result["blockingReasons"], [])
        self.assertEqual(len(result["runSpecs"]), 2)
        self.assertEqual(plan["schemaVersion"], "phase10-rehearsal-plan/v1")
        self.assertEqual(scope["schemaVersion"], "phase10-rehearsal-scope/v1")
        self.assertEqual(plan["notEvidenceFor"], ["training_resume", "table_c_progress", "plugin_readiness"])
        self.assertTrue(all(item["command"] == "preview" for item in result["runSpecs"]))
        self.assertTrue(all(item["targetLayer"] == "CODEX_PREVIEW" for item in result["runSpecs"]))
        self.assertTrue(all(item["outputDir"].endswith(f"run_{index:02d}") for index, item in enumerate(result["runSpecs"], start=1)))

    def test_harness_rehearsal_plan_command_outputs_json_without_cad_write(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        with temporary_artifact_dir("phase10_harness_rehearsal_plan") as root:
            phase9_root = _verified_phase9_run(root)
            result = run_harness_command(
                "rehearsal-plan",
                scope=_scope(run_count=2, phase9_exit_run_dir=str(phase9_root)),
                output_dir=root,
            )

        self.assertEqual(result["schemaVersion"], "cad-agent-harness-result/v1")
        self.assertEqual(result["command"], "rehearsal-plan")
        self.assertEqual(result["status"], "ready")
        self.assertFalse(result["cadGeometryVerified"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertEqual(result["verificationStatus"], "not_verified")
        self.assertEqual(len(result["rehearsalPlan"]["runSpecs"]), 2)

    def test_script_rehearsal_plan_outputs_json_result(self) -> None:
        script = PROJECT_ROOT / "scripts" / "cad_agent_harness.py"

        with temporary_artifact_dir("phase10_harness_rehearsal_plan_script") as root:
            phase9_root = _verified_phase9_run(root)
            scope_path = root / "scope.json"
            scope_path.write_text(
                json.dumps(_scope(run_count=2, phase9_exit_run_dir=str(phase9_root)), ensure_ascii=False),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "rehearsal-plan",
                    "--scope",
                    str(scope_path),
                    "--output-dir",
                    str(root),
                    "--json",
                ],
                cwd=PROJECT_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "rehearsal-plan")
        self.assertEqual(result["status"], "ready")
        self.assertFalse(result["cadWritesAttempted"])

    def test_rehearsal_scope_receipt_records_confirmation_without_cad_write(self) -> None:
        from core.contracts.phase10_rehearsal import build_phase10_rehearsal_scope_receipt

        with temporary_artifact_dir("phase10_scope_receipt_ready") as root:
            plan_path = _write_ready_rehearsal_plan(root)
            result = build_phase10_rehearsal_scope_receipt(
                plan_path=plan_path,
                output_dir=root,
                live_runs_confirmed=True,
                confirmation_statement=_confirmation_statement(),
            )
            receipt = json.loads((root / "phase10_rehearsal_scope_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(result["schemaVersion"], "phase10-rehearsal-scope-receipt/v1")
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["verificationStatus"], "not_verified")
        self.assertTrue(result["scopeConfirmed"])
        self.assertTrue(result["liveRunsConfirmed"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertEqual(result["plannedRunCount"], 2)
        self.assertEqual(result["blockingReasons"], [])
        self.assertEqual(result["nextAllowedEffects"], ["phase10_rehearsal_launch_packet_write"])
        self.assertIn("phase10_live_preview_not_executed_by_scope_receipt", result["notEvidenceFor"])
        self.assertEqual(receipt, result)

    def test_harness_rehearsal_scope_receipt_command_outputs_json_without_cad_write(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        with temporary_artifact_dir("phase10_harness_scope_receipt") as root:
            plan_path = _write_ready_rehearsal_plan(root)
            result = run_harness_command(
                "rehearsal-scope-receipt",
                plan_path=plan_path,
                output_dir=root,
                live_runs_confirmed=True,
                confirmation_statement=_confirmation_statement(),
            )

        self.assertEqual(result["schemaVersion"], "cad-agent-harness-result/v1")
        self.assertEqual(result["command"], "rehearsal-scope-receipt")
        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["scopeConfirmed"])
        self.assertTrue(result["liveRunsConfirmed"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertEqual(result["plannedRunCount"], 2)

    def test_script_rehearsal_scope_receipt_outputs_json_result(self) -> None:
        script = PROJECT_ROOT / "scripts" / "cad_agent_harness.py"

        with temporary_artifact_dir("phase10_harness_scope_receipt_script") as root:
            plan_path = _write_ready_rehearsal_plan(root)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "rehearsal-scope-receipt",
                    "--plan",
                    str(plan_path),
                    "--output-dir",
                    str(root),
                    "--confirm-live-runs",
                    "--confirmation",
                    _confirmation_statement(),
                    "--json",
                ],
                cwd=PROJECT_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "rehearsal-scope-receipt")
        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["scopeConfirmed"])
        self.assertFalse(result["cadWritesAttempted"])

    def test_rehearsal_result_blocks_until_run_dirs_exist_without_executing_cad(self) -> None:
        from core.contracts.phase10_rehearsal import evaluate_phase10_rehearsal_runs

        with temporary_artifact_dir("phase10_missing_rehearsal_runs") as root:
            result = evaluate_phase10_rehearsal_runs(
                run_dirs=[root / "run_01", root / "run_02"],
                output_dir=root,
            )

        self.assertEqual(result["schemaVersion"], "phase10-rehearsal-result/v1")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["cadWritesAttempted"])
        self.assertIn("phase10_rehearsal_run_missing", result["blockingReasons"])
        self.assertIn("phase10_live_preview_not_executed_by_aggregator", result["notEvidenceFor"])

    def test_rehearsal_result_accepts_two_verified_runs_and_writes_diff_and_failure_ledger(self) -> None:
        from core.contracts.phase10_rehearsal import evaluate_phase10_rehearsal_runs

        with temporary_artifact_dir("phase10_verified_rehearsal_runs") as root:
            run_01 = _verified_rehearsal_run(root, "run_01")
            run_02 = _verified_rehearsal_run(root, "run_02")
            result = evaluate_phase10_rehearsal_runs(run_dirs=[run_01, run_02], output_dir=root)
            diff = json.loads((root / "phase10_rehearsal_diff_summary.json").read_text(encoding="utf-8"))
            failure_ledger = json.loads((root / "phase10_rehearsal_failure_ledger.json").read_text(encoding="utf-8"))

        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["verificationStatus"], "verified")
        self.assertTrue(result["cadGeometryVerified"])
        self.assertEqual(result["blockingReasons"], [])
        self.assertTrue(result["stableGeometry"])
        self.assertEqual(diff["schemaVersion"], "phase10-rehearsal-diff-summary/v1")
        self.assertTrue(diff["stableGeometry"])
        self.assertEqual(diff["diffCount"], 0)
        self.assertEqual(failure_ledger["schemaVersion"], "phase10-rehearsal-failure-ledger/v1")
        self.assertEqual(failure_ledger["failureCount"], 0)

    def test_rehearsal_result_blocks_saved_current_dwg(self) -> None:
        from core.contracts.phase10_rehearsal import evaluate_phase10_rehearsal_runs

        with temporary_artifact_dir("phase10_saved_current_dwg") as root:
            run_01 = _verified_rehearsal_run(root, "run_01")
            run_02 = _verified_rehearsal_run(root, "run_02")
            _mutate_report(run_02, savedCurrentDwg=True)
            result = evaluate_phase10_rehearsal_runs(run_dirs=[run_01, run_02], output_dir=root)
            failure_ledger = json.loads((root / "phase10_rehearsal_failure_ledger.json").read_text(encoding="utf-8"))

        self.assertEqual(result["status"], "blocked")
        self.assertIn("phase10_run_saved_current_dwg", result["blockingReasons"])
        self.assertEqual(failure_ledger["failureCount"], 1)
        self.assertIn("phase10_run_saved_current_dwg", failure_ledger["failures"][0]["blockingReasons"])

    def test_rehearsal_result_blocks_geometry_signature_drift(self) -> None:
        from core.contracts.phase10_rehearsal import evaluate_phase10_rehearsal_runs

        with temporary_artifact_dir("phase10_geometry_drift") as root:
            run_01 = _verified_rehearsal_run(root, "run_01")
            run_02 = _verified_rehearsal_run(root, "run_02")
            report_path = run_02 / "phase9_preview_report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["geometryAudit"]["bbox"]["size"] = [920.0, 450.0]
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result = evaluate_phase10_rehearsal_runs(run_dirs=[run_01, run_02], output_dir=root)
            diff = json.loads((root / "phase10_rehearsal_diff_summary.json").read_text(encoding="utf-8"))

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["stableGeometry"])
        self.assertIn("phase10_rehearsal_geometry_diff_detected", result["blockingReasons"])
        self.assertEqual(diff["diffCount"], 1)

    def test_harness_rehearsal_result_command_outputs_readonly_aggregate(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        with temporary_artifact_dir("phase10_harness_rehearsal_result") as root:
            _verified_rehearsal_run(root, "run_01")
            _verified_rehearsal_run(root, "run_02")
            result = run_harness_command("rehearsal-result", run_dir=root)

        self.assertEqual(result["schemaVersion"], "cad-agent-harness-result/v1")
        self.assertEqual(result["command"], "rehearsal-result")
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["verificationStatus"], "verified")
        self.assertTrue(result["cadGeometryVerified"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertTrue(result["rehearsalResult"]["stableGeometry"])
        self.assertEqual(result["registryAuthorization"]["status"], "allowed")
        self.assertEqual(result["adapterId"], "harness.rehearsal-result")

    def test_harness_rehearsal_result_blocks_forbidden_effect_before_writing_artifacts(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        with temporary_artifact_dir("phase10_harness_rehearsal_result_forbidden_effect") as root:
            result = run_harness_command(
                "rehearsal-result",
                run_dir=root,
                requested_effects=["dwg_save"],
            )
            result_artifact_exists = (root / "phase10_rehearsal_result.json").exists()

        self.assertEqual(result["schemaVersion"], "cad-agent-harness-result/v1")
        self.assertEqual(result["command"], "rehearsal-result")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["registryAuthorization"]["status"], "blocked")
        self.assertEqual(result["adapterId"], "harness.rehearsal-result")
        self.assertIn("dwg_save", " ".join(result["blockingReasons"]))
        self.assertFalse(result["cadWritesAttempted"])
        self.assertFalse(result_artifact_exists)

    def test_script_rehearsal_result_outputs_json_result(self) -> None:
        script = PROJECT_ROOT / "scripts" / "cad_agent_harness.py"

        with temporary_artifact_dir("phase10_harness_rehearsal_result_script") as root:
            _verified_rehearsal_run(root, "run_01")
            _verified_rehearsal_run(root, "run_02")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "rehearsal-result",
                    "--run-dir",
                    str(root),
                    "--json",
                ],
                cwd=PROJECT_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "rehearsal-result")
        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["cadGeometryVerified"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertEqual(result["registryAuthorization"]["status"], "allowed")

    def test_script_rehearsal_result_forbidden_effect_cannot_bypass_registry(self) -> None:
        script = PROJECT_ROOT / "scripts" / "cad_agent_harness.py"

        with temporary_artifact_dir("phase10_harness_rehearsal_result_script_forbidden") as root:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "rehearsal-result",
                    "--run-dir",
                    str(root),
                    "--requested-effect",
                    "dwg_save",
                    "--json",
                ],
                cwd=PROJECT_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)
            result_artifact_exists = (root / "phase10_rehearsal_result.json").exists()

        self.assertEqual(result["command"], "rehearsal-result")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["registryAuthorization"]["status"], "blocked")
        self.assertEqual(result["adapterId"], "harness.rehearsal-result")
        self.assertIn("dwg_save", " ".join(result["blockingReasons"]))
        self.assertFalse(result["cadWritesAttempted"])
        self.assertFalse(result_artifact_exists)

    def test_rehearsal_launch_packet_blocks_without_confirmation_or_host_env(self) -> None:
        from core.contracts.phase10_rehearsal import build_phase10_rehearsal_launch_packet

        with temporary_artifact_dir("phase10_launch_packet_blocked") as root:
            plan_path = _write_ready_rehearsal_plan(root)
            result = build_phase10_rehearsal_launch_packet(
                plan_path=plan_path,
                output_dir=root,
                env={},
            )
            packet = json.loads((root / "phase10_rehearsal_launch_packet.json").read_text(encoding="utf-8"))

        self.assertEqual(result["schemaVersion"], "phase10-rehearsal-launch-packet/v1")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["launchAllowed"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertFalse(result["sessionHostEnvReady"])
        self.assertIn("phase10_live_runs_not_confirmed", result["blockingReasons"])
        self.assertIn("phase10_session_host_env_missing", result["blockingReasons"])
        self.assertEqual(packet["blockingReasons"], result["blockingReasons"])

    def test_rehearsal_launch_packet_ready_without_executing_cad(self) -> None:
        from core.contracts.phase10_rehearsal import build_phase10_rehearsal_launch_packet

        with temporary_artifact_dir("phase10_launch_packet_ready") as root:
            plan_path = _write_ready_scope_receipt(root)
            result = build_phase10_rehearsal_launch_packet(
                plan_path=plan_path,
                output_dir=root,
                live_runs_confirmed=True,
                env={
                    "CAD_SESSION_HOST_URL": "http://127.0.0.1:39001",
                    "CAD_SESSION_TOKEN": "test-token",
                },
            )
            run_01_exists = (root / "run_01").exists()

        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["launchAllowed"])
        self.assertTrue(result["sessionHostEnvReady"])
        self.assertTrue(result["scopeReceiptReady"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertFalse(run_01_exists)
        self.assertEqual(result["nextAllowedEffects"], ["phase10_rehearsal_live_preview_runs"])
        self.assertIn("rehearsal-run", result["launchCommand"]["argv"])
        self.assertIn("--scope-receipt", result["launchCommand"]["argv"])
        self.assertIn("--confirm-live-runs", result["launchCommand"]["argv"])
        self.assertIn("phase10_live_preview_not_executed_by_preflight", result["notEvidenceFor"])

    def test_rehearsal_launch_packet_blocks_stale_scope_receipt_after_plan_change(self) -> None:
        from core.contracts.phase10_rehearsal import build_phase10_rehearsal_launch_packet

        with temporary_artifact_dir("phase10_launch_packet_stale_receipt") as root:
            plan_path = _write_ready_scope_receipt(root)
            plan_file = root / "phase10_rehearsal_plan.json"
            plan = json.loads(plan_file.read_text(encoding="utf-8"))
            plan["operatorNote"] = "mutated after scope receipt"
            plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result = build_phase10_rehearsal_launch_packet(
                plan_path=plan_path,
                output_dir=root,
                live_runs_confirmed=True,
                env={
                    "CAD_SESSION_HOST_URL": "http://127.0.0.1:39001",
                    "CAD_SESSION_TOKEN": "test-token",
                },
            )

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["launchAllowed"])
        self.assertFalse(result["scopeReceiptReady"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertIn("phase10_scope_receipt_plan_hash_mismatch", result["blockingReasons"])
        self.assertIn("phase10_scope_confirmation_receipt", result["missingEvidence"])

    def test_harness_rehearsal_preflight_command_blocks_by_default(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        with temporary_artifact_dir("phase10_harness_rehearsal_preflight") as root:
            plan_path = _write_ready_rehearsal_plan(root)
            result = run_harness_command(
                "rehearsal-preflight",
                plan_path=plan_path,
                output_dir=root,
            )

        self.assertEqual(result["schemaVersion"], "cad-agent-harness-result/v1")
        self.assertEqual(result["command"], "rehearsal-preflight")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["launchAllowed"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertIn("phase10_live_runs_not_confirmed", result["blockingReasons"])

    def test_script_rehearsal_preflight_blocks_without_confirmation(self) -> None:
        script = PROJECT_ROOT / "scripts" / "cad_agent_harness.py"

        with temporary_artifact_dir("phase10_harness_rehearsal_preflight_script") as root:
            plan_path = _write_ready_rehearsal_plan(root)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "rehearsal-preflight",
                    "--plan",
                    str(plan_path),
                    "--output-dir",
                    str(root),
                    "--json",
                ],
                cwd=PROJECT_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "rehearsal-preflight")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["cadWritesAttempted"])

    def test_rehearsal_closeout_blocks_until_execution_and_result_exist(self) -> None:
        from core.contracts.phase10_rehearsal import evaluate_phase10_rehearsal_closeout

        with temporary_artifact_dir("phase10_closeout_missing_artifacts") as root:
            _write_ready_launch_packet(root)
            result = evaluate_phase10_rehearsal_closeout(rehearsal_dir=root, output_dir=root)
            closeout = json.loads((root / "phase10_rehearsal_closeout.json").read_text(encoding="utf-8"))

        self.assertEqual(result["schemaVersion"], "phase10-rehearsal-closeout/v1")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["phase10CloseoutAllowed"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertIn("phase10_closeout_execution_missing", result["blockingReasons"])
        self.assertIn("phase10_closeout_result_missing", result["blockingReasons"])
        self.assertEqual(closeout["blockingReasons"], result["blockingReasons"])

    def test_rehearsal_closeout_blocks_injected_executor_artifacts(self) -> None:
        from core.contracts.phase10_rehearsal import (
            evaluate_phase10_rehearsal_closeout,
            execute_phase10_rehearsal_plan,
        )

        with temporary_artifact_dir("phase10_closeout_injected_executor") as root:
            plan_path = _write_ready_launch_packet(root)
            execute_phase10_rehearsal_plan(
                plan_path=plan_path,
                output_dir=root,
                live_runs_confirmed=True,
                preview_executor=_fake_live_preview_executor,
            )
            result = evaluate_phase10_rehearsal_closeout(rehearsal_dir=root, output_dir=root)

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["phase10CloseoutAllowed"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertTrue(result["sourceCadWritesAttempted"])
        self.assertIn("phase10_closeout_executor_mode_not_production", result["blockingReasons"])

    def test_rehearsal_closeout_accepts_production_like_verified_artifacts_without_running_cad(self) -> None:
        from core.contracts.phase10_rehearsal import evaluate_phase10_rehearsal_closeout

        with temporary_artifact_dir("phase10_closeout_ready_artifacts") as root:
            _write_production_like_closeout_artifacts(root)
            result = evaluate_phase10_rehearsal_closeout(rehearsal_dir=root, output_dir=root)

        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["verificationStatus"], "verified")
        self.assertTrue(result["phase10CloseoutAllowed"])
        self.assertTrue(result["phase11Allowed"])
        self.assertTrue(result["cadGeometryVerified"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertTrue(result["sourceCadWritesAttempted"])
        self.assertEqual(result["allowedClaims"], ["phase10_focused_rehearsal_stable"])
        self.assertEqual(result["blockingReasons"], [])

    def test_rehearsal_closeout_blocks_missing_scope_receipt_artifact(self) -> None:
        from core.contracts.phase10_rehearsal import evaluate_phase10_rehearsal_closeout

        with temporary_artifact_dir("phase10_closeout_missing_scope_receipt") as root:
            _write_production_like_closeout_artifacts(root)
            (root / "phase10_rehearsal_scope_receipt.json").unlink()
            result = evaluate_phase10_rehearsal_closeout(rehearsal_dir=root, output_dir=root)

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["phase10CloseoutAllowed"])
        self.assertFalse(result["phase11Allowed"])
        self.assertIn("phase10_closeout_scope_receipt_missing", result["blockingReasons"])
        self.assertIn("phase10_scope_confirmation_receipt", result["missingEvidence"])

    def test_rehearsal_closeout_blocks_mixed_foreign_result_artifact(self) -> None:
        from core.contracts.phase10_rehearsal import evaluate_phase10_rehearsal_closeout

        with temporary_artifact_dir("phase10_closeout_mixed_artifacts") as root:
            _write_production_like_closeout_artifacts(root)
            foreign_root = root / "foreign"
            _write_production_like_closeout_artifacts(foreign_root)
            shutil.copyfile(
                foreign_root / "phase10_rehearsal_result.json",
                root / "phase10_rehearsal_result.json",
            )
            result = evaluate_phase10_rehearsal_closeout(rehearsal_dir=root, output_dir=root)

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["phase10CloseoutAllowed"])
        self.assertFalse(result["phase11Allowed"])
        self.assertIn("phase10_closeout_artifact_result_path_mismatch", result["blockingReasons"])
        self.assertIn("phase10_closeout_artifact_result_mismatch", result["blockingReasons"])
        self.assertIn("phase10_closeout_artifact_run_dirs_mismatch", result["blockingReasons"])

    def test_rehearsal_closeout_blocks_non_object_json_artifact(self) -> None:
        from core.contracts.phase10_rehearsal import evaluate_phase10_rehearsal_closeout

        with temporary_artifact_dir("phase10_closeout_non_object_json") as root:
            _write_ready_launch_packet(root)
            (root / "phase10_rehearsal_execution.json").write_text("[]\n", encoding="utf-8")
            result = evaluate_phase10_rehearsal_closeout(rehearsal_dir=root, output_dir=root)

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["phase10CloseoutAllowed"])
        self.assertIn("phase10_closeout_execution_invalid", result["blockingReasons"])

    def test_harness_rehearsal_closeout_command_outputs_json(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        with temporary_artifact_dir("phase10_harness_rehearsal_closeout") as root:
            _write_production_like_closeout_artifacts(root)
            result = run_harness_command("rehearsal-closeout", run_dir=root)

        self.assertEqual(result["schemaVersion"], "cad-agent-harness-result/v1")
        self.assertEqual(result["command"], "rehearsal-closeout")
        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["phase10CloseoutAllowed"])
        self.assertTrue(result["phase11Allowed"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertTrue(result["sourceCadWritesAttempted"])

    def test_script_rehearsal_closeout_outputs_json_result(self) -> None:
        script = PROJECT_ROOT / "scripts" / "cad_agent_harness.py"

        with temporary_artifact_dir("phase10_harness_rehearsal_closeout_script") as root:
            _write_production_like_closeout_artifacts(root)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "rehearsal-closeout",
                    "--run-dir",
                    str(root),
                    "--json",
                ],
                cwd=PROJECT_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "rehearsal-closeout")
        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["phase10CloseoutAllowed"])
        self.assertFalse(result["cadWritesAttempted"])

    def test_rehearsal_run_blocks_without_live_confirmation_and_does_not_execute(self) -> None:
        from core.contracts.phase10_rehearsal import execute_phase10_rehearsal_plan

        calls: list[str] = []

        def executor(**kwargs):
            calls.append(str(kwargs.get("run_id")))
            return {}

        with temporary_artifact_dir("phase10_live_run_unconfirmed") as root:
            plan_path = _write_ready_rehearsal_plan(root)
            result = execute_phase10_rehearsal_plan(
                plan_path=plan_path,
                output_dir=root,
                preview_executor=executor,
            )
            execution = json.loads((root / "phase10_rehearsal_execution.json").read_text(encoding="utf-8"))

        self.assertEqual(result["schemaVersion"], "phase10-rehearsal-execution/v1")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["cadWritesAttempted"])
        self.assertEqual(result["executedRunCount"], 0)
        self.assertEqual(calls, [])
        self.assertIn("phase10_live_runs_not_confirmed", result["blockingReasons"])
        self.assertEqual(execution["blockingReasons"], result["blockingReasons"])

    def test_rehearsal_run_blocks_without_session_host_configuration_by_default(self) -> None:
        from core.contracts.phase10_rehearsal import execute_phase10_rehearsal_plan

        with temporary_artifact_dir("phase10_live_run_missing_host_env") as root:
            plan_path = _write_ready_scope_receipt(root)
            result = execute_phase10_rehearsal_plan(
                plan_path=plan_path,
                output_dir=root,
                live_runs_confirmed=True,
                env={},
            )

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["cadWritesAttempted"])
        self.assertIn("phase10_session_host_env_missing", result["blockingReasons"])

    def test_rehearsal_run_executes_confirmed_plan_with_injected_executor_then_aggregates(self) -> None:
        from core.contracts.phase10_rehearsal import execute_phase10_rehearsal_plan

        with temporary_artifact_dir("phase10_live_run_injected_executor") as root:
            plan_path = _write_ready_scope_receipt(root)
            result = execute_phase10_rehearsal_plan(
                plan_path=plan_path,
                output_dir=root,
                live_runs_confirmed=True,
                preview_executor=_fake_live_preview_executor,
            )

        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["verificationStatus"], "verified")
        self.assertTrue(result["cadWritesAttempted"])
        self.assertEqual(result["executedRunCount"], 2)
        self.assertTrue(result["aggregateResult"]["stableGeometry"])
        self.assertIn("injected_executor_result_is_not_production_cad_proof", result["notEvidenceFor"])

    def test_harness_rehearsal_run_command_blocks_without_confirmation(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        with temporary_artifact_dir("phase10_harness_rehearsal_run_blocked") as root:
            plan_path = _write_ready_rehearsal_plan(root)
            result = run_harness_command(
                "rehearsal-run",
                plan_path=plan_path,
                output_dir=root,
            )

        self.assertEqual(result["schemaVersion"], "cad-agent-harness-result/v1")
        self.assertEqual(result["command"], "rehearsal-run")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["cadWritesAttempted"])
        self.assertIn("phase10_live_runs_not_confirmed", result["blockingReasons"])

    def test_script_rehearsal_run_blocks_without_confirmation(self) -> None:
        script = PROJECT_ROOT / "scripts" / "cad_agent_harness.py"

        with temporary_artifact_dir("phase10_harness_rehearsal_run_script_blocked") as root:
            plan_path = _write_ready_rehearsal_plan(root)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "rehearsal-run",
                    "--plan",
                    str(plan_path),
                    "--output-dir",
                    str(root),
                    "--json",
                ],
                cwd=PROJECT_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "rehearsal-run")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["cadWritesAttempted"])


if __name__ == "__main__":
    unittest.main()
