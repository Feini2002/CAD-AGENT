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
REQUIRED_HARD_GATES = (
    "main_agent_dispatch_awareness",
    "asset_governance",
    "asset_dwg_curation",
    "asset_reuse_audit",
    "visual_layout_review",
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
    }


def _manifest_checks(root: Path) -> tuple[list[str], list[str]]:
    checked: list[str] = []
    issues: list[str] = []
    manifest = _read_json(root / "agents/pipeline/pipeline_manifest.json")
    orchestration = manifest.get("orchestration", {}) if isinstance(manifest.get("orchestration"), dict) else {}
    agent_ids = {str(agent.get("agent_id", "")) for agent in manifest.get("agents", []) if isinstance(agent, dict)}
    flow_variants = orchestration.get("flow_variants", {}) if isinstance(orchestration.get("flow_variants"), dict) else {}
    hard_gates = orchestration.get("hard_gates", {}) if isinstance(orchestration.get("hard_gates"), dict) else {}
    main_agent_identity = (
        orchestration.get("main_agent_identity", {}) if isinstance(orchestration.get("main_agent_identity"), dict) else {}
    )
    dynamic_dispatch_policy = (
        orchestration.get("dynamic_dispatch_policy", {})
        if isinstance(orchestration.get("dynamic_dispatch_policy"), dict)
        else {}
    )
    unregistered_policy = (
        orchestration.get("unregistered_agent_request_policy", {})
        if isinstance(orchestration.get("unregistered_agent_request_policy"), dict)
        else {}
    )
    forbidden_patterns = manifest.get("forbidden_patterns", {}) if isinstance(manifest.get("forbidden_patterns"), dict) else {}

    for agent_id in [*ASSET_AGENTS, VISUAL_AGENT]:
        if agent_id in agent_ids:
            checked.append(f"agent registered: {agent_id}")
        else:
            issues.append(f"missing agent registration: {agent_id}")

    asset_layout_flow = flow_variants.get("asset_dwg_layout", [])
    if isinstance(asset_layout_flow, list) and VISUAL_AGENT in asset_layout_flow:
        checked.append("asset_dwg_layout flow includes visual layout reviewer")
    else:
        issues.append("asset_dwg_layout flow missing visual layout reviewer")

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
