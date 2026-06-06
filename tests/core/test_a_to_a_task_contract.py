from __future__ import annotations

import json
import unittest

from core.orchestrator.a_to_a_task_contract import build_a_to_a_task_contract
from core.orchestrator.request_context import build_request_context
from core.orchestrator.workflow_dispatch import DISPATCH_BLOCKED, orchestrate_request
from tests.helpers import PROJECT_ROOT


def _visual_acceptance_pass_output() -> dict[str, object]:
    return {
        "status": "pass",
        "visualAcceptanceDecision": "pass",
        "aestheticAcceptable": "pass",
        "textReadable": "pass",
        "noMojibake": "pass",
        "noSevereOverlap": "pass",
        "noSevereClipping": "pass",
        "alignmentAcceptable": "pass",
        "contentMatchesIntent": "pass",
        "reusableOutputLikely": "pass",
        "evidenceBoundaryRespected": "pass",
        "nonScreenshotEvidenceChecked": "pass",
        "blockingReasons": [],
    }


def _design_agent_pass_outputs() -> dict[str, object]:
    return {
        "pipeline_design_director": {
            "status": "pass",
            "designStrategy": {"summary": "为新场景先做三套可比较尺寸表达。"},
            "drawingTypeDecision": "dimension_style_showcase",
            "expressionPurpose": "让用户比较 A/B/C 三种尺寸标注表达。",
            "designIntent": "新场景参数化生成，不复刻旧十个样式。",
            "requiredChildAgents": ["pipeline_style_generator", "pipeline_design_reviewer"],
            "openQuestions": [],
            "evidenceBoundary": {"checked": ["request semantics"], "notChecked": ["CAD readback"]},
        },
        "pipeline_style_generator": {
            "status": "pass",
            "styleDecision": "multiple",
            "styleCandidates": [
                {"candidateId": "A", "summary": "紧凑型"},
                {"candidateId": "B", "summary": "均衡型"},
                {"candidateId": "C", "summary": "展示型"},
            ],
            "selectedStyleCandidate": "",
            "styleParameterGrammar": {"size": "width/depth/text hierarchy"},
            "candidateTradeoffs": [
                {"candidateId": "A", "tradeoff": "信息密度高"},
                {"candidateId": "B", "tradeoff": "默认推荐"},
                {"candidateId": "C", "tradeoff": "更醒目"},
            ],
            "needsUserChoice": True,
            "styleWaiverReason": "",
            "candidateCountPolicy": "explicit_count",
            "requestedCandidateCount": 3,
            "candidateLabelPolicy": "abc",
            "creativityPolicy": "contextual_not_forced",
            "semanticRoutingConfidence": "high",
        },
        "pipeline_design_reviewer": {
            "status": "pass",
            "designReview": "三套候选均可读，交给用户选择。",
            "professionalDrawingLike": "pass",
            "readability": "pass",
            "industryHabitFit": "pass",
            "scaleAndProportionFit": "pass",
            "styleCandidateFit": "pass",
            "contentMatchesDesignPurpose": "pass",
            "needsUserChoice": True,
            "repairOrRegenerateRecommendation": {"mode": "ask_user_choice", "reason": "A/B/C 都是有效方案。"},
        },
    }


class AToATaskContractTests(unittest.TestCase):
    def test_pipeline_manifest_requires_architecture_canvas_gate_for_repo_governance(self) -> None:
        manifest = json.loads((PROJECT_ROOT / "agents/pipeline/pipeline_manifest.json").read_text(encoding="utf-8"))
        orchestration = manifest["orchestration"]

        self.assertIn("system_architecture_canvas", orchestration["hard_gates"])
        self.assertIn(
            "system_architecture_canvas",
            orchestration["required_hard_gates_by_task_kind"]["repository_artifact_governance"],
        )
        gate = orchestration["hard_gates"]["system_architecture_canvas"]
        self.assertIn("seven_layer_canvas", gate["requires"])
        self.assertIn("repository_artifact_governance_complete_claim", gate["blocks"])

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
        self.assertIn("pipeline_visual_acceptance_reviewer", contract["requiredAgents"])
        self.assertIn("visual_layout_review", contract["hardGates"])
        self.assertIn("visual_acceptance_review", contract["hardGates"])
        self.assertEqual(contract["status"], "blocked")
        self.assertIn("pipeline_visual_layout_reviewer", contract["missingRequiredAgents"])
        self.assertIn("pipeline_visual_acceptance_reviewer", contract["missingRequiredAgents"])

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
        self.assertIn("pipeline_visual_acceptance_reviewer", dynamic_agents)
        self.assertIn(
            "visual_acceptance_review",
            dynamic_agents["pipeline_visual_acceptance_reviewer"]["hardGate"],
        )
        self.assertIn("pipeline_visual_layout_reviewer", decision["effectiveRequiredAgents"])
        self.assertIn("pipeline_visual_acceptance_reviewer", decision["effectiveRequiredAgents"])
        self.assertIn("visual_layout_review", contract["hardGates"])
        self.assertIn("visual_acceptance_review", contract["hardGates"])

    def test_new_style_candidate_request_requires_design_intelligence_agents(self) -> None:
        context = build_request_context(
            context_id="req-a2a-style-candidates",
            request_kind="draw",
            user_request="给新场景生成 A/B/C 三套尺寸样式，要有创造性表达和方案候选，不要复刻旧样式",
            allow_cad=True,
        )

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["taskKind"], "style_candidate_generation")
        for agent_id in [
            "pipeline_design_director",
            "pipeline_style_generator",
            "pipeline_design_reviewer",
        ]:
            self.assertIn(agent_id, contract["requiredAgents"])
            self.assertIn(agent_id, contract["missingRequiredAgents"])
        self.assertIn("design_intelligence", contract["hardGates"])
        self.assertEqual(contract["status"], "blocked")
        dynamic_agents = {
            item["agentId"]: item
            for item in contract["dispatchDecision"]["registeredAdditionalAgents"]
        }
        self.assertIn("pipeline_design_director", dynamic_agents)
        self.assertIn("pipeline_style_generator", dynamic_agents)
        self.assertIn("pipeline_design_reviewer", dynamic_agents)

    def test_semantic_contract_guidance_does_not_force_style_candidates(self) -> None:
        context = build_request_context(
            context_id="req-a2a-style-language-guidance",
            request_kind="general",
            user_request=(
                "继续优化语义合同，比如新样式、创造性表达、A/B/C 发后选这些东西，"
                "不要当做死命令；不一定每次都要三种样式，要根据我的指令精确拆分。"
            ),
            allow_cad=False,
        )

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["taskKind"], "ordinary_orchestration")
        self.assertNotIn("pipeline_style_generator", contract["requiredAgents"])
        self.assertNotIn("style_candidate_generation", contract["triggeredSemantics"])
        decomposition = contract["semanticDecomposition"]
        self.assertEqual(decomposition["requestMode"], "semantic_contract_guidance")
        self.assertEqual(decomposition["designRouting"]["decision"], "no_design_agents")
        self.assertEqual(decomposition["designRouting"]["candidateCountPolicy"], "contextual_not_forced")

    def test_single_style_request_does_not_force_abc_candidates(self) -> None:
        context = build_request_context(
            context_id="req-a2a-single-style",
            request_kind="draw",
            user_request="给这个玄关柜画一个更稳的尺寸样式，不用多方案，也不用让我选 A/B/C。",
            allow_cad=True,
        )

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["taskKind"], "design_stage")
        self.assertIn("pipeline_design_director", contract["requiredAgents"])
        self.assertNotIn("pipeline_style_generator", contract["requiredAgents"])
        self.assertNotIn("pipeline_design_reviewer", contract["requiredAgents"])
        self.assertNotIn("style_candidate_generation", contract["triggeredSemantics"])
        self.assertIn("design_style_hint", contract["triggeredSemantics"])
        self.assertEqual(
            contract["semanticDecomposition"]["designRouting"]["candidateCountPolicy"],
            "single_or_auto_selected_allowed",
        )

    def test_style_generator_may_waive_candidates_when_director_does_not_need_them(self) -> None:
        context = build_request_context(
            context_id="req-a2a-style-waived-output",
            request_kind="draw",
            user_request="只做设计判断，不生成多方案候选。",
            allow_cad=True,
        )
        context["force_effective_required_agents"] = ["pipeline_style_generator"]
        context["agent_outputs"] = {
            "pipeline_design_director": {
                "status": "pass",
                "designStrategy": {"summary": "沿用当前表达，只做小幅稳定化。"},
                "drawingTypeDecision": "dimension_style_refinement",
                "expressionPurpose": "单方案优化。",
                "designIntent": "不需要多候选。",
                "requiredChildAgents": [],
                "openQuestions": [],
                "evidenceBoundary": {"checked": ["request semantics"], "notChecked": ["CAD readback"]},
            },
            "pipeline_style_generator": {
                "status": "pass",
                "styleDecision": "waived",
                "styleCandidates": [],
                "selectedStyleCandidate": "",
                "styleParameterGrammar": {},
                "candidateTradeoffs": [],
                "needsUserChoice": False,
                "styleWaiverReason": "用户明确不需要多方案候选。",
                "candidateCountPolicy": "contextual_not_forced",
                "requestedCandidateCount": 0,
                "candidateLabelPolicy": "not_applicable",
                "creativityPolicy": "contextual_not_forced",
                "semanticRoutingConfidence": "medium",
            },
        }

        contract = build_a_to_a_task_contract(context)

        self.assertNotIn("design_intelligence", contract["failedHardGates"])
        self.assertNotIn("styleCandidates_count", str(contract["agentOutputSummary"]))

    def test_style_rule_question_is_semantic_question_not_generation(self) -> None:
        context = build_request_context(
            context_id="req-a2a-style-question",
            request_kind="general",
            user_request="是不是我以后只要提到新样式，你就每次都必须生成 A/B/C？先回答规则，不要执行。",
            allow_cad=False,
        )

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["taskKind"], "ordinary_orchestration")
        decomposition = contract["semanticDecomposition"]
        self.assertEqual(decomposition["requestMode"], "semantic_question")
        self.assertEqual(decomposition["designRouting"]["decision"], "no_design_agents")
        self.assertEqual(decomposition["designRouting"]["confidence"], "high")

    def test_semantic_analysis_only_request_does_not_dispatch_design_agents(self) -> None:
        context = build_request_context(
            context_id="req-a2a-analysis-only",
            request_kind="general",
            user_request="先在对话框里帮我拆解语义：给玄关柜做一个新样式，但先不要落图也不要生成方案。",
            allow_cad=False,
        )

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["taskKind"], "ordinary_orchestration")
        self.assertEqual(contract["semanticDecomposition"]["requestMode"], "semantic_analysis_only")
        self.assertEqual(contract["semanticDecomposition"]["designRouting"]["decision"], "semantic_analysis_only")
        self.assertNotIn("pipeline_design_director", contract["requiredAgents"])

    def test_two_option_request_extracts_candidate_count_without_forcing_abc(self) -> None:
        context = build_request_context(
            context_id="req-a2a-two-options",
            request_kind="draw",
            user_request="给玄关柜生成两个尺寸样式方案让我选，不要 A/B/C 三套。",
            allow_cad=True,
        )

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["taskKind"], "style_candidate_generation")
        routing = contract["semanticDecomposition"]["designRouting"]
        self.assertEqual(routing["candidateCountPolicy"], "explicit_count")
        self.assertEqual(routing["requestedCandidateCount"], 2)
        self.assertEqual(routing["candidateLabelPolicy"], "numeric_or_named_options")

    def test_creativity_negation_keeps_style_as_single_strategy_hint(self) -> None:
        context = build_request_context(
            context_id="req-a2a-no-creativity",
            request_kind="draw",
            user_request="给玄关柜画一个新样式，但不要创造性发挥，也不要多候选。",
            allow_cad=True,
        )

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["taskKind"], "design_stage")
        routing = contract["semanticDecomposition"]["designRouting"]
        self.assertEqual(routing["creativityPolicy"], "suppressed_by_user")
        self.assertEqual(routing["candidateCountPolicy"], "single_or_auto_selected_allowed")
        self.assertNotIn("pipeline_style_generator", contract["requiredAgents"])

    def test_design_intelligence_outputs_release_style_candidate_contract(self) -> None:
        context = build_request_context(
            context_id="req-a2a-style-candidates-ready",
            request_kind="draw",
            user_request="为新场景生成 A/B/C 三套尺寸样式方案候选并在 CAD readback 后设计复核",
            allow_cad=True,
        )
        context["agent_outputs"] = _design_agent_pass_outputs()

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["taskKind"], "style_candidate_generation")
        self.assertEqual(contract["status"], "ready")
        self.assertEqual(contract["missingRequiredAgents"], [])
        self.assertNotIn("design_intelligence", contract["failedHardGates"])

    def test_generic_acceptance_report_does_not_trigger_visual_acceptance_reviewer(self) -> None:
        context = build_request_context(
            context_id="req-a2a-generic-acceptance-report",
            request_kind="report",
            user_request="please prepare an acceptance report for the previous engineering package",
            allow_cad=False,
        )

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["taskKind"], "ordinary_orchestration")
        self.assertNotIn("pipeline_visual_acceptance_reviewer", contract["requiredAgents"])
        self.assertNotIn("visual_acceptance_review", contract["hardGates"])

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
            "pipeline_visual_acceptance_reviewer": _visual_acceptance_pass_output(),
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
            "pipeline_visual_acceptance_reviewer": _visual_acceptance_pass_output(),
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
            "pipeline_visual_acceptance_reviewer": _visual_acceptance_pass_output(),
        }

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["status"], "blocked")
        self.assertIn("visual_layout_review", contract["failedHardGates"])
        self.assertEqual(contract["missingRequiredAgents"], [])


if __name__ == "__main__":
    unittest.main()
