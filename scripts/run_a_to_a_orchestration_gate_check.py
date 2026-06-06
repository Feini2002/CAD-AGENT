#!/usr/bin/env python3
"""Check A-to-A orchestration hard gates for asset and visual layout workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.orchestrator.a_to_a_task_contract import build_a_to_a_task_contract  # noqa: E402
from core.orchestrator.request_context import build_request_context  # noqa: E402
from core.orchestrator.workflow_dispatch import DISPATCH_BLOCKED, orchestrate_request  # noqa: E402


ASSET_AGENTS = (
    "pipeline_asset_governor",
    "pipeline_asset_librarian",
    "pipeline_asset_dwg_curator",
    "pipeline_asset_reuse_auditor",
)
VISUAL_AGENT = "pipeline_visual_layout_reviewer"
VISUAL_ACCEPTANCE_AGENT = "pipeline_visual_acceptance_reviewer"
DESIGN_AGENTS = (
    "pipeline_design_director",
    "pipeline_style_generator",
    "pipeline_design_reviewer",
)
DESIGN_TASK_KINDS = (
    "design_stage",
    "style_candidate_generation",
    "design_review",
)
REQUIRED_HARD_GATES = (
    "system_architecture_canvas",
    "main_agent_dispatch_awareness",
    "design_intelligence",
    "asset_governance",
    "asset_dwg_curation",
    "asset_reuse_audit",
    "visual_layout_review",
    "visual_acceptance_review",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _pass_outputs() -> dict[str, Any]:
    return {
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
        "pipeline_visual_acceptance_reviewer": {
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
        },
    }


def _design_pass_outputs() -> dict[str, Any]:
    return {
        "pipeline_design_director": {
            "status": "pass",
            "designStrategy": {"summary": "先生成 A/B/C 三套尺寸表达候选。"},
            "drawingTypeDecision": "dimension_style_showcase",
            "expressionPurpose": "candidate comparison before user choice",
            "designIntent": "new parameterized style candidates",
            "requiredChildAgents": ["pipeline_style_generator", "pipeline_design_reviewer"],
            "openQuestions": [],
            "evidenceBoundary": {"checked": ["request semantics"], "notChecked": ["cad readback"]},
        },
        "pipeline_style_generator": {
            "status": "pass",
            "styleDecision": "multiple",
            "styleCandidates": [
                {"candidateId": "A", "summary": "compact"},
                {"candidateId": "B", "summary": "balanced"},
                {"candidateId": "C", "summary": "presentation"},
            ],
            "selectedStyleCandidate": "",
            "styleParameterGrammar": {"size": "width/depth/text hierarchy"},
            "candidateTradeoffs": [],
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
            "designReview": "ready for A/B/C user choice",
            "professionalDrawingLike": "pass",
            "readability": "pass",
            "industryHabitFit": "pass",
            "scaleAndProportionFit": "pass",
            "styleCandidateFit": "pass",
            "contentMatchesDesignPurpose": "pass",
            "needsUserChoice": True,
            "repairOrRegenerateRecommendation": {"mode": "ask_user_choice"},
        },
    }


def _manifest_checks(root: Path) -> tuple[list[str], list[str]]:
    checked: list[str] = []
    issues: list[str] = []
    manifest = _read_json(root / "agents/pipeline/pipeline_manifest.json")
    orchestration = manifest.get("orchestration", {}) if isinstance(manifest.get("orchestration"), dict) else {}
    agent_ids = {str(agent.get("agent_id", "")) for agent in manifest.get("agents", []) if isinstance(agent, dict)}
    flow_variants = orchestration.get("flow_variants", {}) if isinstance(orchestration.get("flow_variants"), dict) else {}
    default_flow = orchestration.get("default_flow", []) if isinstance(orchestration.get("default_flow"), list) else []
    hard_gate_map = (
        orchestration.get("required_hard_gates_by_task_kind", {})
        if isinstance(orchestration.get("required_hard_gates_by_task_kind"), dict)
        else {}
    )
    hard_gates = orchestration.get("hard_gates", {}) if isinstance(orchestration.get("hard_gates"), dict) else {}
    main_agent_identity = (
        orchestration.get("main_agent_identity", {}) if isinstance(orchestration.get("main_agent_identity"), dict) else {}
    )
    dynamic_dispatch_policy = (
        orchestration.get("dynamic_dispatch_policy", {})
        if isinstance(orchestration.get("dynamic_dispatch_policy"), dict)
        else {}
    )
    high_risk_task_kinds = (
        dynamic_dispatch_policy.get("high_risk_task_kinds", [])
        if isinstance(dynamic_dispatch_policy.get("high_risk_task_kinds"), list)
        else []
    )
    unregistered_policy = (
        orchestration.get("unregistered_agent_request_policy", {})
        if isinstance(orchestration.get("unregistered_agent_request_policy"), dict)
        else {}
    )
    forbidden_patterns = manifest.get("forbidden_patterns", {}) if isinstance(manifest.get("forbidden_patterns"), dict) else {}

    for agent_id in [*ASSET_AGENTS, VISUAL_AGENT, VISUAL_ACCEPTANCE_AGENT, *DESIGN_AGENTS]:
        if agent_id in agent_ids:
            checked.append(f"agent registered: {agent_id}")
        else:
            issues.append(f"missing agent registration: {agent_id}")

    design_flow_present = all(agent_id in default_flow for agent_id in DESIGN_AGENTS)
    if design_flow_present:
        checked.append("default flow includes design intelligence chain")
    else:
        issues.append("default flow missing design intelligence chain")
    if (
        design_flow_present
        and default_flow.index("pipeline_design_director") < default_flow.index("pipeline_style_generator")
        and default_flow.index("pipeline_style_generator") < default_flow.index("pipeline_visual_intent")
        and default_flow.index("pipeline_visual_acceptance_reviewer") < default_flow.index("pipeline_design_reviewer")
    ):
        checked.append("default flow orders design director/style generator/reviewer correctly")
    elif design_flow_present:
        issues.append("default flow order for design intelligence chain is incorrect")

    for task_kind in DESIGN_TASK_KINDS:
        if task_kind in high_risk_task_kinds:
            checked.append(f"high-risk task kind registered: {task_kind}")
        else:
            issues.append(f"missing high-risk task kind: {task_kind}")
        gates_for_task = hard_gate_map.get(task_kind, []) if isinstance(hard_gate_map.get(task_kind), list) else []
        if "design_intelligence" in gates_for_task:
            checked.append(f"{task_kind} requires design_intelligence gate")
        else:
            issues.append(f"{task_kind} missing design_intelligence gate")

    asset_layout_flow = flow_variants.get("asset_dwg_layout", [])
    if isinstance(asset_layout_flow, list) and VISUAL_AGENT in asset_layout_flow:
        checked.append("asset_dwg_layout flow includes visual layout reviewer")
    else:
        issues.append("asset_dwg_layout flow missing visual layout reviewer")
    if isinstance(asset_layout_flow, list) and VISUAL_ACCEPTANCE_AGENT in asset_layout_flow:
        checked.append("asset_dwg_layout flow includes visual acceptance reviewer")
    else:
        issues.append("asset_dwg_layout flow missing visual acceptance reviewer")

    sedimentation_flow = flow_variants.get("system_asset_sedimentation", [])
    for agent_id in ASSET_AGENTS:
        if isinstance(sedimentation_flow, list) and agent_id in sedimentation_flow:
            checked.append(f"system_asset_sedimentation includes {agent_id}")
        else:
            issues.append(f"system_asset_sedimentation missing {agent_id}")

    for gate in REQUIRED_HARD_GATES:
        if gate in hard_gates:
            checked.append(f"hard gate registered: {gate}")
        else:
            issues.append(f"missing hard gate: {gate}")

    repo_governance_gates = (
        hard_gate_map.get("repository_artifact_governance", [])
        if isinstance(hard_gate_map.get("repository_artifact_governance"), list)
        else []
    )
    if "system_architecture_canvas" in repo_governance_gates:
        checked.append("repository artifact governance requires system architecture canvas gate")
    else:
        issues.append("repository_artifact_governance missing system_architecture_canvas gate")
    architecture_gate = hard_gates.get("system_architecture_canvas", {}) if isinstance(hard_gates.get("system_architecture_canvas"), dict) else {}
    architecture_requires = architecture_gate.get("requires", []) if isinstance(architecture_gate.get("requires"), list) else []
    missing_architecture_fields = sorted(
        {
            "seven_layer_canvas",
            "old_module_layer_mapping",
            "metric_reframe",
            "training_pause_boundary",
            "no_second_master_plan",
        }.difference(architecture_requires)
    )
    if not missing_architecture_fields:
        checked.append("system architecture canvas gate declares layer, metric, training, and PlanMD boundaries")
    else:
        issues.append(f"system architecture canvas gate missing fields: {missing_architecture_fields}")

    if main_agent_identity.get("identity") == "pipeline_orchestrator_main_agent":
        checked.append("main agent identity registered")
    else:
        issues.append("missing orchestration.main_agent_identity.identity")

    if dynamic_dispatch_policy.get("registered_agent_only") is True and dynamic_dispatch_policy.get("reason_required") is True:
        checked.append("dynamic dispatch policy requires registered agents and reasons")
    else:
        issues.append("dynamic dispatch policy missing registered_agent_only/reason_required")

    if unregistered_policy.get("activation_allowed_in_current_task") is False:
        checked.append("unregistered agent requests cannot activate in current task")
    else:
        issues.append("unregistered agent request policy must block current-task activation")

    if "unregistered_agent_activated" in forbidden_patterns:
        checked.append("forbidden pattern registered: unregistered_agent_activated")
    else:
        issues.append("missing forbidden pattern: unregistered_agent_activated")

    visual_gate = hard_gates.get("visual_layout_review", {}) if isinstance(hard_gates.get("visual_layout_review"), dict) else {}
    visual_requires = visual_gate.get("requires", []) if isinstance(visual_gate.get("requires"), list) else []
    if "layoutReadabilityAcceptable" in visual_requires:
        checked.append("visual layout gate requires layoutReadabilityAcceptable")
    else:
        issues.append("visual layout gate missing layoutReadabilityAcceptable")

    visual_agent_file = root / "agents/pipeline/visual_layout_reviewer/agent.json"
    if visual_agent_file.is_file():
        checked.append("visual layout reviewer definition exists")
    else:
        issues.append("missing visual layout reviewer definition")
    visual_acceptance_gate = (
        hard_gates.get("visual_acceptance_review", {})
        if isinstance(hard_gates.get("visual_acceptance_review"), dict)
        else {}
    )
    visual_acceptance_requires = (
        visual_acceptance_gate.get("requires", [])
        if isinstance(visual_acceptance_gate.get("requires"), list)
        else []
    )
    if "noMojibake" in visual_acceptance_requires and "textReadable" in visual_acceptance_requires:
        checked.append("visual acceptance gate requires readability and mojibake checks")
    else:
        issues.append("visual acceptance gate missing readability/mojibake checks")
    visual_acceptance_agent_file = root / "agents/pipeline/visual_acceptance_reviewer/agent.json"
    if visual_acceptance_agent_file.is_file():
        checked.append("visual acceptance reviewer definition exists")
    else:
        issues.append("missing visual acceptance reviewer definition")

    design_gate = hard_gates.get("design_intelligence", {}) if isinstance(hard_gates.get("design_intelligence"), dict) else {}
    design_requires = design_gate.get("requires", []) if isinstance(design_gate.get("requires"), list) else []
    design_required_fields = {
        "designStrategy",
        "drawingTypeDecision",
        "expressionPurpose",
        "styleCandidate_or_designWaiver",
        "designReview_when_visible_output",
    }
    missing_design_fields = sorted(design_required_fields.difference(design_requires))
    if not missing_design_fields:
        checked.append("design intelligence gate requires strategy, drawing type, style candidate, and review")
    else:
        issues.append(f"design intelligence gate missing fields: {missing_design_fields}")
    for agent_id in DESIGN_AGENTS:
        agent_file = root / f"agents/pipeline/{agent_id.removeprefix('pipeline_')}/agent.json"
        if agent_file.is_file():
            checked.append(f"design agent definition exists: {agent_id}")
        else:
            issues.append(f"missing design agent definition: {agent_id}")
    for pattern in ("design_stage_skipped", "template_style_without_design_reasoning", "design_review_skipped"):
        if pattern in forbidden_patterns:
            checked.append(f"forbidden pattern registered: {pattern}")
        else:
            issues.append(f"missing forbidden pattern: {pattern}")

    return checked, issues


def _contract_checks() -> tuple[list[str], list[str]]:
    checked: list[str] = []
    issues: list[str] = []

    warehouse_context = build_request_context(
        context_id="a2a-check-asset-layout",
        request_kind="draw",
        user_request="把系统资产 DWG 做成仓库货架排版，保留可扩展货位和检索动线",
        allow_cad=True,
    )
    warehouse_contract = build_a_to_a_task_contract(warehouse_context)
    if warehouse_contract.get("taskKind") == "asset_dwg_layout":
        checked.append("contract detects asset_dwg_layout")
    else:
        issues.append(f"contract taskKind mismatch: {warehouse_contract.get('taskKind')}")
    if VISUAL_AGENT in warehouse_contract.get("missingRequiredAgents", []):
        checked.append("contract blocks missing visual layout reviewer")
    else:
        issues.append("contract did not block missing visual layout reviewer")
    self_check = warehouse_contract.get("mainAgentSelfCheck", {})
    if isinstance(self_check, dict) and self_check.get("identity") == "pipeline_orchestrator_main_agent":
        checked.append("contract emits mainAgentSelfCheck identity")
    else:
        issues.append("contract missing mainAgentSelfCheck identity")
    dispatch_decision = warehouse_contract.get("dispatchDecision", {})
    dynamic_additions = (
        dispatch_decision.get("registeredAdditionalAgents", []) if isinstance(dispatch_decision, dict) else []
    )
    if any(isinstance(item, dict) and item.get("agentId") == VISUAL_AGENT and item.get("reason") for item in dynamic_additions):
        checked.append("contract records registered visual layout dynamic dispatch")
    else:
        issues.append("contract missing registered visual layout dynamic dispatch reason")
    if any(
        isinstance(item, dict)
        and item.get("agentId") == VISUAL_ACCEPTANCE_AGENT
        and item.get("reason")
        for item in dynamic_additions
    ):
        checked.append("contract records registered visual acceptance dynamic dispatch")
    else:
        issues.append("contract missing registered visual acceptance dynamic dispatch reason")

    sediment_context = build_request_context(
        context_id="a2a-check-sedimentation",
        request_kind="draw",
        user_request="沉淀这个尺寸样式为通用资产，收进系统资产库",
        allow_cad=True,
    )
    sediment_contract = build_a_to_a_task_contract(sediment_context)
    if sediment_contract.get("taskKind") == "system_asset_sedimentation":
        checked.append("contract detects system_asset_sedimentation")
    else:
        issues.append(f"sedimentation taskKind mismatch: {sediment_contract.get('taskKind')}")

    warehouse_context["agent_outputs"] = _pass_outputs()
    ready_contract = build_a_to_a_task_contract(warehouse_context)
    if ready_contract.get("status") == "ready":
        checked.append("contract becomes ready after required agent outputs pass")
    else:
        issues.append("contract stayed blocked after required agent outputs pass")

    incomplete_visual_context = build_request_context(
        context_id="a2a-check-incomplete-visual-review",
        request_kind="draw",
        user_request="把系统资产 DWG 做成仓库货架排版",
        allow_cad=True,
    )
    incomplete_outputs = _pass_outputs()
    incomplete_outputs[VISUAL_AGENT] = {"status": "pass"}
    incomplete_visual_context["agent_outputs"] = incomplete_outputs
    incomplete_contract = build_a_to_a_task_contract(incomplete_visual_context)
    if incomplete_contract.get("status") == "blocked" and "visual_layout_review" in incomplete_contract.get(
        "failedHardGates", []
    ):
        checked.append("contract blocks incomplete visual layout reviewer fields")
    else:
        issues.append("contract did not block incomplete visual layout reviewer fields")
    visual_failures = (
        incomplete_contract.get("agentOutputSummary", {})
        .get(VISUAL_AGENT, {})
        .get("visualFailures", [])
    )
    if "layoutReadabilityAcceptable" in visual_failures:
        checked.append("contract blocks missing layoutReadabilityAcceptable")
    else:
        issues.append("contract did not report missing layoutReadabilityAcceptable")

    unregistered_context = build_request_context(
        context_id="a2a-check-unregistered-agent-request",
        request_kind="draw",
        user_request="系统资产 DWG 排版反复润色失败，需要新增 pipeline_asset_polish_reviewer 复审",
        allow_cad=True,
    )
    unregistered_contract = build_a_to_a_task_contract(unregistered_context)
    unregistered_decision = unregistered_contract.get("dispatchDecision", {})
    additional_requests = (
        unregistered_decision.get("additionalAgentRequests", [])
        if isinstance(unregistered_decision, dict)
        else []
    )
    if any(
        isinstance(item, dict)
        and item.get("requestedAgentId") == "pipeline_asset_polish_reviewer"
        and item.get("status") == "needs_reviewed_package"
        for item in additional_requests
    ):
        checked.append("contract keeps unregistered agent as reviewed-package candidate")
    else:
        issues.append("contract did not keep unregistered agent as reviewed-package candidate")
    effective_agents = (
        unregistered_decision.get("effectiveRequiredAgents", [])
        if isinstance(unregistered_decision, dict)
        else []
    )
    if "pipeline_asset_polish_reviewer" not in effective_agents:
        checked.append("contract does not activate unregistered agent")
    else:
        issues.append("contract activated unregistered agent")

    forced_context = build_request_context(
        context_id="a2a-check-unregistered-agent-forced",
        request_kind="draw",
        user_request="系统资产 DWG 仓库货架排版",
        allow_cad=True,
    )
    forced_context["force_effective_required_agents"] = ["pipeline_asset_polish_reviewer"]
    forced_contract = build_a_to_a_task_contract(forced_context)
    if forced_contract.get("status") == "blocked" and "main_agent_dispatch_awareness" in forced_contract.get(
        "failedHardGates", []
    ):
        checked.append("contract blocks forced unregistered effective agent")
    else:
        issues.append("contract did not block forced unregistered effective agent")

    design_context = build_request_context(
        context_id="a2a-check-style-candidates",
        request_kind="draw",
        user_request="为新场景生成 A/B/C 三套尺寸样式方案候选，要有创造性表达",
        allow_cad=True,
    )
    design_contract = build_a_to_a_task_contract(design_context)
    if design_contract.get("taskKind") == "style_candidate_generation":
        checked.append("contract detects style_candidate_generation")
    else:
        issues.append(f"style candidate taskKind mismatch: {design_contract.get('taskKind')}")
    for agent_id in DESIGN_AGENTS:
        if agent_id in design_contract.get("missingRequiredAgents", []):
            checked.append(f"contract blocks missing design agent: {agent_id}")
        else:
            issues.append(f"contract did not block missing design agent: {agent_id}")
    if "design_intelligence" in design_contract.get("hardGates", []):
        checked.append("contract requires design_intelligence for style candidates")
    else:
        issues.append("contract missing design_intelligence for style candidates")

    design_context["agent_outputs"] = _design_pass_outputs()
    ready_design_contract = build_a_to_a_task_contract(design_context)
    if ready_design_contract.get("status") == "ready":
        checked.append("style candidate contract becomes ready after design outputs pass")
    else:
        issues.append("style candidate contract stayed blocked after design outputs pass")

    guidance_context = build_request_context(
        context_id="a2a-check-style-guidance",
        request_kind="general",
        user_request="优化语义合同：新样式、创造性表达、A/B/C 发后选这些词不要当做死命令，不一定每次都三套。",
        allow_cad=False,
    )
    guidance_contract = build_a_to_a_task_contract(guidance_context)
    if guidance_contract.get("taskKind") == "ordinary_orchestration":
        checked.append("contract treats style wording guidance as ordinary orchestration")
    else:
        issues.append(f"style wording guidance over-triggered taskKind: {guidance_contract.get('taskKind')}")
    if "style_candidate_generation" not in guidance_contract.get("triggeredSemantics", []):
        checked.append("contract keeps A/B/C guidance as soft signal")
    else:
        issues.append("contract treated A/B/C guidance as hard style_candidate_generation")
    decomposition = guidance_contract.get("semanticDecomposition", {})
    if isinstance(decomposition, dict) and decomposition.get("requestMode") == "semantic_contract_guidance":
        checked.append("contract emits semantic decomposition for dialogue/CLI layer")
    else:
        issues.append("contract missing semantic decomposition for guidance request")

    question_context = build_request_context(
        context_id="a2a-check-style-question",
        request_kind="general",
        user_request="是不是以后提到新样式就必须 A/B/C？先回答规则，不要执行。",
        allow_cad=False,
    )
    question_contract = build_a_to_a_task_contract(question_context)
    question_decomposition = question_contract.get("semanticDecomposition", {})
    if question_contract.get("taskKind") == "ordinary_orchestration" and isinstance(
        question_decomposition, dict
    ) and question_decomposition.get("requestMode") == "semantic_question":
        checked.append("contract treats style rule questions as non-execution semantics")
    else:
        issues.append("contract over-triggered style rule question")

    two_option_context = build_request_context(
        context_id="a2a-check-two-options",
        request_kind="draw",
        user_request="给玄关柜生成两个尺寸样式方案让我选，不要 A/B/C 三套。",
        allow_cad=True,
    )
    two_option_contract = build_a_to_a_task_contract(two_option_context)
    two_option_routing = two_option_contract.get("semanticDecomposition", {}).get("designRouting", {})
    if (
        two_option_contract.get("taskKind") == "style_candidate_generation"
        and two_option_routing.get("requestedCandidateCount") == 2
        and two_option_routing.get("candidateLabelPolicy") == "numeric_or_named_options"
    ):
        checked.append("contract extracts two-option candidate count without forcing A/B/C")
    else:
        issues.append("contract failed to extract two-option candidate count")

    dispatch_report = orchestrate_request(
        build_request_context(
            context_id="a2a-check-dispatch",
            request_kind="draw",
            user_request="系统资产库像仓库货架一样重新排版，注意动线和可扩展货位",
            allow_cad=True,
        )
    )
    dispatch = dispatch_report.get("workflow_dispatch", {})
    if dispatch.get("status") == DISPATCH_BLOCKED and "a-to-a hard gate" in str(dispatch.get("reason", "")):
        checked.append("orchestrator dispatch blocked by a-to-a hard gate")
    else:
        issues.append(f"orchestrator did not expose a-to-a hard gate block: {dispatch}")

    return checked, issues


def run_check(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    root = Path(project_root)
    checked: list[str] = []
    issues: list[str] = []

    manifest_checked, manifest_issues = _manifest_checks(root)
    contract_checked, contract_issues = _contract_checks()
    checked.extend(manifest_checked)
    checked.extend(contract_checked)
    issues.extend(manifest_issues)
    issues.extend(contract_issues)
    status = "pass" if not issues else "fail"
    hardening_status = "complete_for_current_scope" if not issues else "needs_a_to_a_hardening"

    return {
        "status": status,
        "checked": checked,
        "issues": issues,
        "polishHardeningDecision": {
            "status": hardening_status,
            "categories": [hardening_status],
            "scope": "a_to_a_task_contract_orchestration_package",
            "evidenceBoundary": {
                "checked": checked,
                "notChecked": [
                    "real CAD DWG relayout",
                    "concrete task visual_layout_review output",
                    "concrete task visual_acceptance_review output",
                    "real CAD asset reuse replay",
                ],
            },
        },
        "wroteCad": False,
        "savedDwg": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check A-to-A orchestration hard gates.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_check(project_root=args.project_root)
    if args.output:
        output = args.output if args.output.is_absolute() else args.project_root / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
