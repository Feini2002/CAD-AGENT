from __future__ import annotations

import unittest

from core.orchestrator.a_to_a_task_contract import build_a_to_a_task_contract
from core.orchestrator.request_context import build_request_context
from core.orchestrator.workflow_dispatch import DISPATCH_BLOCKED, orchestrate_request


class AToATaskContractTests(unittest.TestCase):
    def test_visual_warehouse_layout_requires_visual_layout_reviewer_hard_gate(self) -> None:
        context = build_request_context(
            context_id="req-a2a-warehouse-layout",
            request_kind="draw",
            user_request="把通用资产 DWG 改成仓库置物架，分类排版，优化动线和展示形式",
            allow_cad=True,
        )

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["taskKind"], "asset_dwg_layout")
        self.assertIn("pipeline_visual_layout_reviewer", contract["requiredAgents"])
        self.assertIn("visual_layout_review", contract["hardGates"])
        self.assertEqual(contract["status"], "blocked")
        self.assertIn("pipeline_visual_layout_reviewer", contract["missingRequiredAgents"])

    def test_high_risk_contract_reports_main_agent_self_check(self) -> None:
        context = build_request_context(
            context_id="req-a2a-main-agent-self-check",
            request_kind="draw",
            user_request="把系统资产 DWG 做成仓库货架排版，保留检索动线",
            allow_cad=True,
        )

        contract = build_a_to_a_task_contract(context)

        self_check = contract["mainAgentSelfCheck"]
        self.assertEqual(self_check["status"], "pass")
        self.assertEqual(self_check["identity"], "pipeline_orchestrator_main_agent")
        self.assertIn("dispatch", self_check["mission"])
        self.assertEqual(self_check["taskUnderstanding"]["taskKind"], "asset_dwg_layout")
        self.assertFalse(self_check["responsibilityBoundary"]["mayExecuteCad"])
        self.assertIn("cannot activate unregistered agents", self_check["knownLimits"])
        self.assertIn("pipeline manifest", self_check["decisionBasis"])

    def test_failed_main_agent_self_check_blocks_delivery_claim(self) -> None:
        context = build_request_context(
            context_id="req-a2a-main-agent-self-check-fail",
            request_kind="draw",
            user_request="把系统资产 DWG 做成仓库货架排版",
            allow_cad=True,
        )
        context["main_agent_self_check_override"] = {
            "status": "fail",
            "reason": "manifest policy missing during replay",
        }

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["status"], "blocked")
        self.assertIn("main_agent_dispatch_awareness", contract["failedHardGates"])
        self.assertFalse(contract["deliveryBoundary"]["mayClaimComplete"])
        self.assertIn("main agent self-check failed", "; ".join(contract["blockingReasons"]))

    def test_visual_layout_semantics_records_registered_dynamic_dispatch(self) -> None:
        context = build_request_context(
            context_id="req-a2a-dynamic-visual-agent",
            request_kind="draw",
            user_request="系统资产 DWG 仓库货架排版，检查货位、动线和展示形式",
            allow_cad=True,
        )

        contract = build_a_to_a_task_contract(context)

        decision = contract["dispatchDecision"]
        dynamic_agents = {item["agentId"]: item for item in decision["registeredAdditionalAgents"]}
        self.assertIn("pipeline_visual_layout_reviewer", dynamic_agents)
        self.assertIn("visual_layout_review", dynamic_agents["pipeline_visual_layout_reviewer"]["hardGate"])
        self.assertTrue(dynamic_agents["pipeline_visual_layout_reviewer"]["reason"])
        self.assertIn("pipeline_visual_layout_reviewer", decision["effectiveRequiredAgents"])
        self.assertIn("visual_layout_review", contract["hardGates"])

    def test_unregistered_agent_need_stays_reviewed_package_candidate(self) -> None:
        context = build_request_context(
            context_id="req-a2a-unregistered-agent-request",
            request_kind="draw",
            user_request="系统资产 DWG 排版反复润色失败，需要新增 pipeline_asset_polish_reviewer 复审",
            allow_cad=True,
        )

        contract = build_a_to_a_task_contract(context)

        decision = contract["dispatchDecision"]
        requested_agents = {item["requestedAgentId"]: item for item in decision["additionalAgentRequests"]}
        self.assertIn("pipeline_asset_polish_reviewer", requested_agents)
        self.assertEqual(requested_agents["pipeline_asset_polish_reviewer"]["status"], "needs_reviewed_package")
        self.assertTrue(decision["reviewedPackageRequired"])
        self.assertNotIn("pipeline_asset_polish_reviewer", decision["effectiveRequiredAgents"])

    def test_unregistered_effective_agent_is_blocked(self) -> None:
        context = build_request_context(
            context_id="req-a2a-unregistered-agent-active",
            request_kind="draw",
            user_request="系统资产 DWG 仓库货架排版",
            allow_cad=True,
        )
        context["force_effective_required_agents"] = ["pipeline_asset_polish_reviewer"]

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["status"], "blocked")
        self.assertIn("main_agent_dispatch_awareness", contract["failedHardGates"])
        self.assertIn("unregistered required agents", "; ".join(contract["blockingReasons"]))

    def test_orchestrator_blocks_when_required_a_to_a_agent_output_is_missing(self) -> None:
        context = build_request_context(
            context_id="req-a2a-missing-visual-review",
            request_kind="draw",
            user_request="系统资产库像仓库货架一样重新排版，注意动线和可扩展货位",
            allow_cad=True,
        )

        report = orchestrate_request(context)

        self.assertEqual(report["a_to_a_task_contract"]["status"], "blocked")
        self.assertEqual(report["workflow_dispatch"]["status"], DISPATCH_BLOCKED)
        self.assertFalse(report["may_execute"])
        self.assertIn("a-to-a hard gate", report["workflow_dispatch"]["reason"])

    def test_system_asset_sedimentation_dispatches_fixed_asset_agents(self) -> None:
        context = build_request_context(
            context_id="req-a2a-sedimentation",
            request_kind="draw",
            user_request="沉淀这个尺寸样式为通用资产，收进系统资产库",
            allow_cad=True,
        )

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["taskKind"], "system_asset_sedimentation")
        for agent_id in [
            "pipeline_asset_governor",
            "pipeline_asset_librarian",
            "pipeline_asset_dwg_curator",
            "pipeline_asset_reuse_auditor",
        ]:
            self.assertIn(agent_id, contract["requiredAgents"])
        self.assertIn("asset_governance", contract["hardGates"])
        self.assertIn("asset_dwg_curation", contract["hardGates"])
        self.assertIn("asset_reuse_audit", contract["hardGates"])

    def test_agent_outputs_satisfy_required_hard_gates(self) -> None:
        context = build_request_context(
            context_id="req-a2a-visual-reviewed",
            request_kind="draw",
            user_request="把系统资产 DWG 做成仓库货架排版",
            allow_cad=True,
        )
        context["agent_outputs"] = {
            "pipeline_asset_governor": {"status": "pass"},
            "pipeline_asset_librarian": {"status": "pass"},
            "pipeline_asset_dwg_curator": {"status": "pass"},
            "pipeline_asset_reuse_auditor": {"status": "pass"},
            "pipeline_visual_layout_reviewer": {
                "status": "pass",
                "layoutMatchesMetaphor": "pass",
                "primaryShelvesClear": "pass",
                "layoutReadabilityAcceptable": "pass",
                "aisleClearanceAcceptable": "pass",
                "contentDensityAcceptable": "pass",
                "sourceProofRolesSeparated": "pass",
                "layerSemanticsAcceptable": "pass",
                "futureExpansionClear": "pass",
                "retrievalPathReadable": "pass",
                "visualNoiseAcceptable": "pass",
                "nonScreenshotEvidenceChecked": "pass",
            },
        }

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["status"], "ready")
        self.assertEqual(contract["missingRequiredAgents"], [])
        self.assertEqual(contract["failedHardGates"], [])

    def test_visual_layout_reviewer_must_report_readability_fields(self) -> None:
        context = build_request_context(
            context_id="req-a2a-visual-review-old-pass-shape",
            request_kind="draw",
            user_request="system asset DWG warehouse shelf layout",
            allow_cad=True,
        )
        context["agent_outputs"] = {
            "pipeline_asset_governor": {"status": "pass"},
            "pipeline_asset_librarian": {"status": "pass"},
            "pipeline_asset_dwg_curator": {"status": "pass"},
            "pipeline_asset_reuse_auditor": {"status": "pass"},
            "pipeline_visual_layout_reviewer": {
                "status": "pass",
                "layoutMatchesMetaphor": "pass",
                "primaryShelvesClear": "pass",
                "futureExpansionClear": "pass",
                "retrievalPathReadable": "pass",
                "visualNoiseAcceptable": "pass",
            },
        }

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["status"], "blocked")
        self.assertIn("visual_layout_review", contract["failedHardGates"])
        self.assertIn(
            "layoutReadabilityAcceptable",
            contract["agentOutputSummary"]["pipeline_visual_layout_reviewer"]["visualFailures"],
        )

    def test_visual_layout_reviewer_missing_required_fields_fails_gate(self) -> None:
        context = build_request_context(
            context_id="req-a2a-visual-review-incomplete",
            request_kind="draw",
            user_request="把系统资产 DWG 做成仓库货架排版",
            allow_cad=True,
        )
        context["agent_outputs"] = {
            "pipeline_asset_governor": {"status": "pass"},
            "pipeline_asset_librarian": {"status": "pass"},
            "pipeline_asset_dwg_curator": {"status": "pass"},
            "pipeline_asset_reuse_auditor": {"status": "pass"},
            "pipeline_visual_layout_reviewer": {"status": "pass"},
        }

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["status"], "blocked")
        self.assertIn("visual_layout_review", contract["failedHardGates"])
        self.assertEqual(contract["missingRequiredAgents"], [])


if __name__ == "__main__":
    unittest.main()
