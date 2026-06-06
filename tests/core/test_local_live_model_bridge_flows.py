from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from tests.core.test_local_live_model_bridge import (
    _design_director_model_output,
    _model_output_for_schema,
    _now,
    _valid_preview_cad_plan,
)
from tests.helpers import temporary_artifact_dir


class SingleAgentLiveTests(unittest.TestCase):
    def test_single_agent_live_does_not_call_model_when_bridge_is_not_registered(self) -> None:
        from core.model_review.codex_cli_client import CodexCliReviewConfig
        from core.orchestrator.local_live_model_bridge import LocalLiveModelBridgeRuntime

        def fail_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
            raise AssertionError(f"model runner should not be called: {command}")

        with temporary_artifact_dir("single_agent_live_unregistered_bridge") as root:
            runtime = LocalLiveModelBridgeRuntime(root_dir=root, now=_now)

            result = runtime.run_single_agent_live(
                request_summary="未登记 bridge 时不能继续调用模型。",
                workspace_id="cad-agent-core-lab",
                bridge_id="unknown_bridge",
                agent_id="pipeline_design_director",
                config=CodexCliReviewConfig(enabled=True, model="gpt-5.5", timeout_seconds=30),
                runner=fail_runner,
                cwd=root,
            )

            self.assertEqual(result["state"], "waiting_for_bridge")
            self.assertIn("bridge_unregistered", result["blockedReasons"])
            self.assertFalse(result["modelInvoked"])
            self.assertEqual(result["tasks"][0]["state"], "pending")

    def test_single_agent_live_uses_codex_cli_prompt_pack_and_records_trace(self) -> None:
        from core.model_review.codex_cli_client import CodexCliReviewConfig
        from core.orchestrator.local_live_model_bridge import LocalLiveModelBridgeRuntime

        seen_commands: list[list[str]] = []

        def fake_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
            seen_commands.append(command)
            output_path = Path(command[command.index("--output-last-message") + 1])
            output_path.write_text(
                json.dumps(_design_director_model_output(), ensure_ascii=False),
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with temporary_artifact_dir("single_agent_live") as root:
            runtime = LocalLiveModelBridgeRuntime(root_dir=root, now=_now)
            runtime.register_bridge(
                bridge_id="bridge_user_pc_001",
                capabilities=["codex_cli_model_review"],
                version="local-test",
            )

            result = runtime.run_single_agent_live(
                request_summary="请 pipeline_design_director 先给茶几符号做设计判断。",
                workspace_id="cad-agent-core-lab",
                bridge_id="bridge_user_pc_001",
                agent_id="pipeline_design_director",
                config=CodexCliReviewConfig(enabled=True, model="gpt-5.5", timeout_seconds=30),
                runner=fake_runner,
                cwd=root,
            )

            self.assertEqual(result["completionClaim"], "single_agent_live")
            self.assertEqual(result["state"], "completed")
            self.assertTrue(result["modelInvoked"])
            self.assertFalse(result["modelUnavailable"])
            self.assertTrue(result["schemaValid"])
            self.assertFalse(result["cadGeometryVerified"])
            self.assertEqual(result["tasks"][0]["state"], "completed")
            self.assertEqual(
                result["tasks"][0]["result"]["traceRef"],
                "model_traces/pipeline_design_director/pipeline-design-director/trace_summary.md",
            )
            self.assertEqual(result["tasks"][0]["result"]["evidenceRefs"], ["agent_outputs/pipeline_design_director.json"])
            self.assertTrue((Path(result["runDir"]) / "agent_outputs" / "pipeline_design_director.json").is_file())
            self.assertTrue(
                (
                    Path(result["runDir"])
                    / "model_traces"
                    / "pipeline_design_director"
                    / "pipeline-design-director"
                    / "command.json"
                ).is_file()
            )
            self.assertTrue(seen_commands)
            self.assertIn("--model", seen_commands[0])
            self.assertEqual(seen_commands[0][seen_commands[0].index("--model") + 1], "gpt-5.5")


class MultiAgentLiveTests(unittest.TestCase):
    def test_multi_agent_live_runs_three_agents_and_prompts_reference_upstream_outputs(self) -> None:
        from core.model_review.codex_cli_client import CodexCliReviewConfig
        from core.orchestrator.local_live_model_bridge import LocalLiveModelBridgeRuntime

        def fake_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
            schema_path = command[command.index("--output-schema") + 1]
            output_path = Path(command[command.index("--output-last-message") + 1])
            output_path.write_text(
                json.dumps(_model_output_for_schema(schema_path), ensure_ascii=False),
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with temporary_artifact_dir("multi_agent_live") as root:
            runtime = LocalLiveModelBridgeRuntime(root_dir=root, now=_now)
            runtime.register_bridge(
                bridge_id="bridge_user_pc_001",
                capabilities=["codex_cli_model_review"],
                version="local-test",
            )

            result = runtime.run_multi_agent_live(
                request_summary="让设计总监、风格生成、设计复核三节点串行互读。",
                workspace_id="cad-agent-core-lab",
                bridge_id="bridge_user_pc_001",
                config=CodexCliReviewConfig(enabled=True, model="gpt-5.5", timeout_seconds=30),
                runner=fake_runner,
                cwd=root,
            )

            self.assertEqual(result["completionClaim"], "multi_agent_live")
            self.assertEqual(result["state"], "completed")
            self.assertTrue(result["modelInvoked"])
            self.assertFalse(result["cadGeometryVerified"])
            self.assertEqual([task["state"] for task in result["tasks"]], ["completed", "completed", "completed"])

            run_dir = Path(result["runDir"])
            for agent_id in ("pipeline_design_director", "pipeline_style_generator", "pipeline_design_reviewer"):
                self.assertTrue((run_dir / "agent_outputs" / f"{agent_id}.json").is_file(), agent_id)

            style_prompt = (
                run_dir / "model_traces" / "pipeline_style_generator" / "pipeline-style-generator" / "prompt.md"
            ).read_text(encoding="utf-8")
            review_prompt = (
                run_dir / "model_traces" / "pipeline_design_reviewer" / "pipeline-design-reviewer" / "prompt.md"
            ).read_text(encoding="utf-8")
            self.assertIn("agent_outputs/pipeline_design_director.json", style_prompt)
            self.assertIn("agent_outputs/pipeline_design_director.json", review_prompt)
            self.assertIn("agent_outputs/pipeline_style_generator.json", review_prompt)
            self.assertTrue(result["tasks"][1]["result"]["evidenceRefs"][0].endswith("pipeline_style_generator.json"))
            self.assertIn("agent_outputs/pipeline_design_director.json", result["tasks"][1]["result"]["evidenceRefs"])
            self.assertIn("agent_outputs/pipeline_style_generator.json", result["tasks"][2]["result"]["evidenceRefs"])


class CadMcpPreviewLiveTests(unittest.TestCase):
    def test_cad_mcp_preview_runs_stage3_and_stage4_without_saving_or_claiming_fake_cad_geometry(self) -> None:
        from core.model_review.codex_cli_client import CodexCliReviewConfig
        from core.orchestrator.local_live_model_bridge import LocalLiveModelBridgeRuntime

        def fake_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
            schema_path = command[command.index("--output-schema") + 1]
            output_path = Path(command[command.index("--output-last-message") + 1])
            output_path.write_text(
                json.dumps(_model_output_for_schema(schema_path), ensure_ascii=False),
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with temporary_artifact_dir("cad_mcp_preview_live") as root:
            runtime = LocalLiveModelBridgeRuntime(root_dir=root, now=_now)
            runtime.register_bridge(
                bridge_id="bridge_user_pc_001",
                capabilities=["codex_cli_model_review", "cad_mcp_preview"],
                version="local-test",
            )

            result = runtime.run_cad_mcp_preview_live(
                request_summary="让模型链路产出设计判断，再通过受控 Tool Contract 做 preview-only CAD preflight。",
                workspace_id="cad-agent-core-lab",
                bridge_id="bridge_user_pc_001",
                cad_plan=_valid_preview_cad_plan(),
                driver_mode="fake_driver_preflight",
                config=CodexCliReviewConfig(enabled=True, model="gpt-5.5", timeout_seconds=30),
                runner=fake_runner,
                cwd=root,
            )

            self.assertEqual(result["completionClaim"], "cad_mcp_preview_live")
            self.assertEqual(result["state"], "completed")
            self.assertEqual(result["runtimeStatus"], "completed")
            self.assertEqual(result["proofStatus"], "not_verified")
            self.assertTrue(result["modelInvoked"])
            self.assertFalse(result["cadGeometryVerified"])
            self.assertTrue(result["featureGates"]["cad_mcp_preview_live"]["enabled"])
            self.assertEqual(result["cadPreview"]["driverMode"], "fake_driver_preflight")
            self.assertEqual(result["cadPreview"]["proofStatus"], "not_verified")
            self.assertEqual(result["cadPreview"]["targetLayer"], "CODEX_PREVIEW")
            self.assertFalse(result["cadPreview"]["savedCurrentDwg"])
            self.assertFalse(result["cadPreview"]["cadGeometryVerified"])
            self.assertGreater(result["cadPreview"]["createdHandleCount"], 0)

            run_dir = Path(result["runDir"])
            for rel_path in (
                "candidate_outputs/cad_plan.candidate.json",
                "cad_reports/validation_report.json",
                "cad_reports/dry_run_report.json",
                "cad_reports/cad_preview_tool_report.json",
                "cad_reports/execution_summary.json",
                "cad_reports/readback_summary.json",
                "tool_traces/pipeline_audit.intent-validate-cad-plan.json",
                "tool_traces/pipeline_audit.intent-dry-run-cad-plan.json",
                "tool_traces/pipeline_intent.intent-preview-cad-execute.json",
            ):
                self.assertTrue((run_dir / rel_path).is_file(), rel_path)

            preview_report = json.loads((run_dir / "cad_reports" / "cad_preview_tool_report.json").read_text(encoding="utf-8"))
            readback = json.loads((run_dir / "cad_reports" / "readback_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(preview_report["resultStatus"], "not_verified")
            self.assertFalse(preview_report["savedCurrentDwg"])
            self.assertEqual(readback["readbackStatus"], "not_verified")
            self.assertEqual(readback["rawReadbackStatus"], "ok")


if __name__ == "__main__":
    unittest.main()
