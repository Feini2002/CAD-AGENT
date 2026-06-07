from __future__ import annotations

import json
import unittest

from core.model_review.codex_cli_client import CodexCliReviewConfig
from core.orchestrator.request_context import build_request_context
from core.orchestrator.run_package_state import create_run_package
from tests.helpers import temporary_artifact_dir


class OrchestratorHostRuntimeTests(unittest.TestCase):
    def _run_package(self, *, user_request: str, request_kind: str = "draw") -> object:
        root_cm = temporary_artifact_dir("orchestrator_host_runtime")
        root = root_cm.__enter__()
        self.addCleanup(root_cm.__exit__, None, None, None)
        context = build_request_context(
            context_id="host-runtime-case",
            request_kind=request_kind,
            user_request=user_request,
            available_inputs=["cad_plan"] if request_kind == "draw" else [],
            allow_cad=request_kind == "draw",
        )
        state = create_run_package(
            "host-runtime-case",
            user_request={"text": user_request, "requestKind": request_kind},
            context_pack={
                "schemaVersion": "run-package-context-pack/v1",
                "runId": "host-runtime-case",
                "requestContext": context,
            },
            root_dir=root,
        )
        return root / state["runId"]

    def test_visible_draw_requires_visual_acceptance_and_writes_runtime_files(self) -> None:
        from core.orchestrator.orchestrator_host_runtime import run_orchestrator_host_runtime

        run_dir = self._run_package(user_request="画一个小茶几并加中文标注，完成后给我看。")

        report = run_orchestrator_host_runtime(
            run_dir,
            config=CodexCliReviewConfig(enabled=False),
        )

        self.assertEqual(report["dispatchPlan"]["route"], "standard_draw")
        self.assertIn("pipeline_visual_acceptance_reviewer", report["requiredAgents"]["agentIds"])
        self.assertIn("visual_acceptance_review", report["dispatchPlan"]["hardGates"])
        self.assertIn("cad_readback", report["dispatchPlan"]["hardGates"])
        self.assertFalse(report["modelReview"]["modelInvoked"])
        for filename in (
            "dispatch_plan.json",
            "task_contract.json",
            "required_agents.json",
            "risk_assessment.json",
        ):
            self.assertTrue((run_dir / filename).is_file(), filename)

    def test_delete_or_cleanup_requires_delete_scope_gate(self) -> None:
        from core.orchestrator.orchestrator_host_runtime import run_orchestrator_host_runtime

        run_dir = self._run_package(user_request="删除上一轮画错的 CODEX_PREVIEW 对象，只做局部修复。")

        report = run_orchestrator_host_runtime(run_dir, config=CodexCliReviewConfig(enabled=False))

        self.assertEqual(report["dispatchPlan"]["route"], "local_repair")
        self.assertIn("pipeline_repair", report["requiredAgents"]["agentIds"])
        self.assertIn("delete_scope_gate", report["dispatchPlan"]["hardGates"])
        self.assertIn("victim_set_preview", report["riskAssessment"]["requiredBeforeCad"])

    def test_nearby_placement_requires_neighbor_protection(self) -> None:
        from core.orchestrator.orchestrator_host_runtime import run_orchestrator_host_runtime

        run_dir = self._run_package(user_request="在 A1 表格旁边放一个 A2 面板，不能碰到旁边内容。")

        report = run_orchestrator_host_runtime(run_dir, config=CodexCliReviewConfig(enabled=False))

        self.assertIn("neighbor_protection", report["dispatchPlan"]["hardGates"])
        self.assertIn("occupied_bbox_check", report["riskAssessment"]["requiredBeforeCad"])
        self.assertIn("pipeline_visual_acceptance_reviewer", report["requiredAgents"]["agentIds"])

    def test_asset_sedimentation_requires_asset_agents_and_data_bloat_gate(self) -> None:
        from core.orchestrator.orchestrator_host_runtime import run_orchestrator_host_runtime

        run_dir = self._run_package(user_request="沉淀这个沙发为通用资产，收进系统资产库。")

        report = run_orchestrator_host_runtime(run_dir, config=CodexCliReviewConfig(enabled=False))

        self.assertEqual(report["dispatchPlan"]["route"], "system_asset_sedimentation")
        for agent_id in (
            "pipeline_asset_governor",
            "pipeline_asset_librarian",
            "pipeline_asset_dwg_curator",
            "pipeline_asset_reuse_auditor",
        ):
            self.assertIn(agent_id, report["requiredAgents"]["agentIds"])
        for gate in ("asset_governance", "asset_dwg_curation", "asset_reuse_audit", "data_bloat_governance"):
            self.assertIn(gate, report["dispatchPlan"]["hardGates"])
        self.assertEqual(report["dispatchPlan"]["complexityAssessment"]["riskLevel"], "high")
        self.assertIn("data_bloat_governance", report["dispatchPlan"]["routeBudget"]["mustKeepHardGates"])

    def test_quick_trial_gets_cheapest_route_budget_without_skipping_hard_gates(self) -> None:
        from core.orchestrator.orchestrator_host_runtime import run_orchestrator_host_runtime

        run_dir = self._run_package(user_request="试一下画一个小茶几，先看看，不沉淀。")

        report = run_orchestrator_host_runtime(run_dir, config=CodexCliReviewConfig(enabled=False))

        self.assertEqual(report["dispatchPlan"]["route"], "quick_trial")
        self.assertEqual(report["dispatchPlan"]["complexityAssessment"]["complexity"], "low")
        self.assertEqual(report["dispatchPlan"]["routeBudget"]["mode"], "quick_draw")
        self.assertIn("preview_only_boundary", report["dispatchPlan"]["routeBudget"]["mustKeepHardGates"])
        self.assertIn("cad_readback", report["dispatchPlan"]["routeBudget"]["mustKeepHardGates"])
        self.assertIn("pipeline_design_director", report["dispatchPlan"]["routeBudget"]["skippableAgents"])

    def test_unregistered_agent_is_candidate_not_effective_required_agent(self) -> None:
        from core.orchestrator.orchestrator_host_runtime import run_orchestrator_host_runtime

        run_dir = self._run_package(
            user_request="这个资产排版需要新增 pipeline_asset_polish_reviewer 复审，但先不要临场激活。"
        )

        report = run_orchestrator_host_runtime(run_dir, config=CodexCliReviewConfig(enabled=False))

        self.assertNotIn("pipeline_asset_polish_reviewer", report["requiredAgents"]["agentIds"])
        requests = report["requiredAgents"]["additionalAgentRequests"]
        self.assertEqual(requests[0]["requestedAgentId"], "pipeline_asset_polish_reviewer")
        self.assertEqual(requests[0]["status"], "needs_reviewed_package")
        self.assertEqual(report["dispatchPlan"]["status"], "blocked")

    def test_written_required_agents_file_marks_prompt_pack_availability(self) -> None:
        from core.orchestrator.orchestrator_host_runtime import run_orchestrator_host_runtime

        run_dir = self._run_package(user_request="画一个小椅子，完成后给用户验收。")
        run_orchestrator_host_runtime(run_dir, config=CodexCliReviewConfig(enabled=False))

        required_agents = json.loads((run_dir / "required_agents.json").read_text(encoding="utf-8"))
        visual_agent = {
            item["agentId"]: item for item in required_agents["agents"]
        }["pipeline_visual_acceptance_reviewer"]
        self.assertTrue(visual_agent["registered"])
        self.assertTrue(visual_agent["promptPackAvailable"])
        self.assertFalse(visual_agent["mayExecuteCad"])

    def test_model_payload_includes_written_rule_context_pack(self) -> None:
        from core.orchestrator.orchestrator_host_runtime import run_orchestrator_host_runtime

        run_dir = self._run_package(user_request="先做设计判断，再给出 CAD_PLAN 草案，不要直接写 CAD。")
        observed: dict[str, str] = {}

        def fake_runner(command, *, input, cwd, text, encoding, errors, capture_output, timeout, check):
            import subprocess
            from pathlib import Path

            observed["prompt"] = input
            output_path = Path(command[command.index("--output-last-message") + 1])
            output_path.write_text(
                json.dumps(
                    {
                        "status": "pass",
                        "route": "standard_draw",
                        "taskKind": "ordinary_orchestration",
                        "userIntentSummary": "design before CAD",
                        "requiredAgents": ["pipeline_design_director"],
                        "dispatchRationale": [],
                        "hardGates": ["cad_plan_required"],
                        "needsUserConfirmation": False,
                        "blockedBeforeExecution": False,
                        "blockingReasons": [],
                        "additionalAgentRequests": [],
                        "statePatch": {
                            "phase": "orchestrator_reviewed",
                            "phaseLabelForUser": "主编排已复审",
                            "completedEvidence": ["rule context pack"],
                            "pendingEvidence": [],
                            "pendingUserAction": "",
                            "blockedReason": "",
                            "nextSafeAction": "continue",
                        },
                        "finalResponseAllowedClaims": ["orchestrator reviewed only"],
                        "evidenceUsed": ["rule_context_pack.json"],
                        "evidenceMissing": [],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        report = run_orchestrator_host_runtime(
            run_dir,
            config=CodexCliReviewConfig(enabled=True, model="gpt-5.5"),
            runner=fake_runner,
        )

        self.assertTrue((run_dir / "rule_context_pack.json").is_file())
        self.assertEqual(report["ruleContextPack"]["status"], "ready")
        self.assertIn("rule_context_pack.json", report["inputRefs"]["ruleContextPack"])
        self.assertIn("ruleContextPack", observed["prompt"])
        self.assertIn("模型只能只读判断", observed["prompt"])

    def test_status_query_uses_deterministic_route_even_when_model_config_enabled(self) -> None:
        from core.orchestrator.orchestrator_host_runtime import run_orchestrator_host_runtime

        run_dir = self._run_package(user_request="查询当前开发状态，不要设计、不要 CAD。", request_kind="status")

        def forbidden_runner(*_args, **_kwargs):
            raise AssertionError("status query must not invoke model runner")

        report = run_orchestrator_host_runtime(
            run_dir,
            config=CodexCliReviewConfig(enabled=True, model="gpt-5.5"),
            runner=forbidden_runner,
        )

        self.assertFalse(report["modelReview"]["modelInvoked"])
        self.assertFalse(report["modelTriggerDecision"]["modelRequired"])
        self.assertEqual(report["modelTriggerDecision"]["status"], "deterministic_only")


if __name__ == "__main__":
    unittest.main()
