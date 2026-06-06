from __future__ import annotations

import json
import unittest
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO

from tests.helpers import temporary_artifact_dir


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_valid_model_trace(run_dir: Path, trace_ref: str, *, agent_id: str) -> None:
    trace_dir = run_dir / Path(trace_ref).parent
    trace_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / trace_ref).write_text("model trace summary\n", encoding="utf-8")
    _write_json(
        trace_dir / "trace_review.json",
        {
            "schemaVersion": "model-trace-review/v1",
            "status": "pass",
            "blockingReasons": [],
        },
    )
    _write_json(
        trace_dir / "trace_manifest.json",
        {
            "schemaVersion": 1,
            "provider": "codex_cli",
            "route": "codex_cli_local",
            "agentId": agent_id,
        },
    )
    _write_json(
        trace_dir / "command.json",
        {
            "schemaVersion": 1,
            "status": "built",
            "sanitized": True,
            "command": ["codex.cmd", "exec", "--model", "gpt-5.5", "--sandbox", "read-only", "-"],
        },
    )
    _write_json(
        trace_dir / "normalized_output.json",
        {
            "schemaVersion": 1,
            "status": "pass",
            "modelProviderStatus": {
                "provider": "codex_cli",
                "route": "codex_cli_local",
                "modelInvoked": True,
                "modelUnavailable": False,
                "schemaValid": True,
            },
        },
    )


class LocalLiveModelBridgeDiagnosticsTests(unittest.TestCase):
    def test_worker_ready_report_stops_before_bridge_when_bridge_is_not_required(self) -> None:
        from core.orchestrator.local_live_model_bridge import LocalLiveModelBridgeRuntime
        from core.orchestrator.local_live_model_bridge_diagnostics import diagnose_run

        with temporary_artifact_dir("local_live_bridge_diag_worker_only") as root:
            runtime = LocalLiveModelBridgeRuntime(root_dir=root)
            state = runtime.create_run(
                request_summary="白话触发 Worker，但默认只证明 worker_orchestration_ready。",
                workspace_id="cad-agent-core-lab",
                target_stage="worker_orchestration_ready",
                agent_ids=["pipeline_design_director"],
            )

            report = diagnose_run(Path(state["runDir"]))

            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["completionClaim"], "worker_orchestration_ready")
            self.assertEqual(report["firstBlockedAt"], "")
            self.assertEqual(report["stageDiagnostics"][0]["stage"], "worker_orchestration_ready")
            self.assertEqual(report["stageDiagnostics"][0]["status"], "pass")
            self.assertEqual(report["stageDiagnostics"][1]["stage"], "local_bridge_connected")
            self.assertEqual(report["stageDiagnostics"][1]["status"], "not_enabled")

    def test_bridge_offline_report_identifies_local_bridge_gate(self) -> None:
        from core.orchestrator.local_live_model_bridge import LocalLiveModelBridgeRuntime
        from core.orchestrator.local_live_model_bridge_diagnostics import diagnose_run

        with temporary_artifact_dir("local_live_bridge_diag_bridge_offline") as root:
            runtime = LocalLiveModelBridgeRuntime(root_dir=root)
            runtime.register_bridge(bridge_id="bridge_user_pc_001", capabilities=["codex_cli_model_review"])
            runtime.mark_bridge_offline("bridge_user_pc_001", reason="bridge process is not running")
            state = runtime.create_run(
                request_summary="需要 bridge，但本地 bridge 不在线。",
                workspace_id="cad-agent-core-lab",
                target_stage="single_agent_live",
                agent_ids=["pipeline_design_director"],
            )
            runtime.lease_task(
                bridge_id="bridge_user_pc_001",
                capabilities=["codex_cli_model_review"],
                heartbeat_token="hb-1",
                run_id=state["runId"],
            )

            report = diagnose_run(Path(state["runDir"]))

            self.assertEqual(report["status"], "blocked")
            self.assertEqual(report["firstBlockedAt"], "local_bridge_connected")
            bridge_stage = report["stageDiagnostics"][1]
            self.assertEqual(bridge_stage["status"], "blocked")
            self.assertIn("bridge process is not running", bridge_stage["blockedReasons"])
            self.assertEqual(report["nextAction"], "start_or_register_local_bridge")

    def test_fake_cad_preview_report_marks_real_cad_geometry_as_blocked(self) -> None:
        from core.orchestrator.local_live_model_bridge_diagnostics import diagnose_run

        with temporary_artifact_dir("local_live_bridge_diag_fake_cad") as root:
            run_dir = root / "run_fake_cad"
            _write_json(
                run_dir / "worker_run_state.json",
                {
                    "schemaVersion": "worker_run_state/v1",
                    "runId": "run_fake_cad",
                    "runDir": str(run_dir),
                    "state": "completed",
                    "completionClaim": "cad_mcp_preview_live",
                    "currentStage": "cad_mcp_preview_live",
                    "modelInvoked": True,
                    "modelUnavailable": False,
                    "schemaValid": True,
                    "cadGeometryVerified": False,
                    "tasks": [
                        {
                            "taskId": "task_pipeline_design_director_001",
                            "agentId": "pipeline_design_director",
                            "state": "completed",
                            "result": {
                                "modelInvoked": True,
                                "modelUnavailable": False,
                                "schemaValid": True,
                                "traceRef": "model_traces/pipeline_design_director/pipeline-design-director/trace_summary.md",
                            },
                        },
                        {
                            "taskId": "task_pipeline_style_generator_001",
                            "agentId": "pipeline_style_generator",
                            "state": "completed",
                            "result": {
                                "modelInvoked": True,
                                "modelUnavailable": False,
                                "schemaValid": True,
                                "traceRef": "model_traces/pipeline_style_generator/pipeline-style-generator/trace_summary.md",
                            },
                        },
                        {
                            "taskId": "task_pipeline_design_reviewer_001",
                            "agentId": "pipeline_design_reviewer",
                            "state": "completed",
                            "result": {
                                "modelInvoked": True,
                                "modelUnavailable": False,
                                "schemaValid": True,
                                "traceRef": "model_traces/pipeline_design_reviewer/pipeline-design-reviewer/trace_summary.md",
                            },
                        },
                    ],
                    "cadPreview": {
                        "status": "pass",
                        "driverMode": "fake_driver_preflight",
                        "targetLayer": "CODEX_PREVIEW",
                        "savedCurrentDwg": False,
                        "cadGeometryVerified": False,
                        "createdHandleCount": 7,
                        "readbackStatus": "not_verified",
                    },
                },
            )
            _write_valid_model_trace(
                run_dir,
                "model_traces/pipeline_design_director/pipeline-design-director/trace_summary.md",
                agent_id="pipeline_design_director",
            )
            _write_valid_model_trace(
                run_dir,
                "model_traces/pipeline_style_generator/pipeline-style-generator/trace_summary.md",
                agent_id="pipeline_style_generator",
            )
            _write_valid_model_trace(
                run_dir,
                "model_traces/pipeline_design_reviewer/pipeline-design-reviewer/trace_summary.md",
                agent_id="pipeline_design_reviewer",
            )

            report = diagnose_run(run_dir)

            self.assertEqual(report["status"], "blocked")
            self.assertEqual(report["firstBlockedAt"], "cad_mcp_preview_live")
            cad_stage = report["stageDiagnostics"][4]
            self.assertEqual(cad_stage["status"], "blocked")
            self.assertIn("real CAD geometry not verified", cad_stage["blockedReasons"])
            self.assertEqual(report["nextAction"], "open_autocad_or_use_cad_ready_gate")

    def test_live_model_summary_without_trace_is_blocked(self) -> None:
        from core.orchestrator.local_live_model_bridge_diagnostics import diagnose_run

        with temporary_artifact_dir("local_live_bridge_diag_missing_trace") as root:
            run_dir = root / "run_missing_trace"
            _write_json(
                run_dir / "worker_run_state.json",
                {
                    "schemaVersion": "worker_run_state/v1",
                    "runId": "run_missing_trace",
                    "runDir": str(run_dir),
                    "state": "completed",
                    "completionClaim": "single_agent_live",
                    "currentStage": "single_agent_live",
                    "modelInvoked": True,
                    "modelUnavailable": False,
                    "schemaValid": True,
                    "cadGeometryVerified": False,
                    "featureGates": {
                        "worker_orchestration_ready": {"enabled": True},
                        "local_bridge_connected": {"enabled": True},
                        "single_agent_live": {"enabled": True},
                        "multi_agent_live": {"enabled": False},
                        "cad_mcp_preview_live": {"enabled": False},
                        "current_dwg_save": {"enabled": False},
                    },
                    "tasks": [
                        {
                            "taskId": "task_pipeline_design_director_001",
                            "agentId": "pipeline_design_director",
                            "state": "completed",
                            "leasedBy": "bridge_user_pc_001",
                            "result": {
                                "modelInvoked": True,
                                "modelUnavailable": False,
                                "schemaValid": True,
                                "traceRef": "model_traces/missing/trace_summary.md",
                            },
                        }
                    ],
                },
            )

            report = diagnose_run(run_dir)

            self.assertEqual(report["status"], "blocked")
            self.assertEqual(report["firstBlockedAt"], "single_agent_live")
            self.assertIn("model trace missing: model_traces/missing/trace_summary.md", report["blockedReasons"])

    def test_live_model_trace_requires_codex_route_and_command(self) -> None:
        from core.orchestrator.local_live_model_bridge_diagnostics import diagnose_run

        with temporary_artifact_dir("local_live_bridge_diag_bad_trace") as root:
            run_dir = root / "run_bad_trace"
            trace_ref = "model_traces/pipeline_design_director/pipeline-design-director/trace_summary.md"
            _write_json(
                run_dir / "worker_run_state.json",
                {
                    "schemaVersion": "worker_run_state/v1",
                    "runId": "run_bad_trace",
                    "runDir": str(run_dir),
                    "state": "completed",
                    "completionClaim": "single_agent_live",
                    "currentStage": "single_agent_live",
                    "modelInvoked": True,
                    "modelUnavailable": False,
                    "schemaValid": True,
                    "cadGeometryVerified": False,
                    "featureGates": {
                        "worker_orchestration_ready": {"enabled": True},
                        "local_bridge_connected": {"enabled": True},
                        "single_agent_live": {"enabled": True},
                        "multi_agent_live": {"enabled": False},
                        "cad_mcp_preview_live": {"enabled": False},
                        "current_dwg_save": {"enabled": False},
                    },
                    "tasks": [
                        {
                            "taskId": "task_pipeline_design_director_001",
                            "agentId": "pipeline_design_director",
                            "state": "completed",
                            "leasedBy": "bridge_user_pc_001",
                            "result": {
                                "modelInvoked": True,
                                "modelUnavailable": False,
                                "schemaValid": True,
                                "traceRef": trace_ref,
                            },
                        }
                    ],
                },
            )
            _write_valid_model_trace(run_dir, trace_ref, agent_id="pipeline_design_director")
            command_path = run_dir / Path(trace_ref).parent / "command.json"
            command = json.loads(command_path.read_text(encoding="utf-8"))
            command["command"] = ["codex.cmd", "--model", "gpt-5.5"]
            command_path.write_text(json.dumps(command, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            output_path = run_dir / Path(trace_ref).parent / "normalized_output.json"
            output = json.loads(output_path.read_text(encoding="utf-8"))
            output["modelProviderStatus"]["route"] = "manual_fixture"
            output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            report = diagnose_run(run_dir)

            self.assertEqual(report["status"], "blocked")
            self.assertEqual(report["firstBlockedAt"], "single_agent_live")
            self.assertIn("model provider route is manual_fixture", report["blockedReasons"])
            self.assertIn("codex exec command missing", report["blockedReasons"])

    def test_cli_emits_json_and_can_fail_on_blocked(self) -> None:
        from core.orchestrator.local_live_model_bridge import LocalLiveModelBridgeRuntime
        from scripts.diagnose_local_live_model_bridge import main

        with temporary_artifact_dir("local_live_bridge_diag_cli") as root:
            runtime = LocalLiveModelBridgeRuntime(root_dir=root)
            runtime.register_bridge(bridge_id="bridge_user_pc_001", capabilities=["codex_cli_model_review"])
            runtime.mark_bridge_offline("bridge_user_pc_001", reason="bridge is offline")
            state = runtime.create_run(
                request_summary="需要 live model，但 bridge 离线。",
                workspace_id="cad-agent-core-lab",
                target_stage="single_agent_live",
                agent_ids=["pipeline_design_director"],
            )
            runtime.lease_task(
                bridge_id="bridge_user_pc_001",
                capabilities=["codex_cli_model_review"],
                heartbeat_token="hb-1",
                run_id=state["runId"],
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                rc = main(["--run-dir", str(Path(state["runDir"]))])
            payload = json.loads(stdout.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["firstBlockedAt"], "local_bridge_connected")

            stdout = StringIO()
            with redirect_stdout(stdout):
                rc = main(["--run-dir", str(Path(state["runDir"])), "--fail-on-blocked"])
            self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
