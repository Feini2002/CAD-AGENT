#!/usr/bin/env python3
"""Validate that the training workbench snapshot has not drifted from repo facts."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:  # Imported as scripts.run_training_workbench_agent_check.
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()


DATA_ASSIGNMENT_RE = re.compile(r"^\s*window\.CAD_CAPABILITY_MAP_DATA\s*=\s*(?P<payload>\{.*\})\s*;\s*$", re.S)
COMMON_PROMPT_CONTRACT_REL = "agents/COMMON_PROMPT_CONTRACT.md"
COMMON_PROMPT_RULES = (
    "CAD 测试必须使用中文标注；图层名、文件名、Schema key 等技术名允许保留原文。",
    "落图前先选择不覆盖旧图形的测试画布，避免重叠用户已有图块。",
    "通过前必须回读 created handles，并说明 checked / not_checked。",
    "真实 CAD 测试默认只写 CODEX_PREVIEW，不保存 DWG，不污染正式图层。",
    "用户用箭头、蓝圈或截图指定 CAD 位置时，先识别被指对象及相对位置，不得默认另起训练模块。",
    "图像反馈类 CAD 修正应优先从当前 AutoCAD 实体回读参照 bbox，再按当前画面语义定位；不要套旧 execution summary 坐标。",
    "若用户要求同尺寸补画样本，先从已存在样本 bbox 推导尺寸，再画新对象并回读 created handles。",
    "误画在其它区域的预览实体默认保留，未经用户明确批准不得删除 CAD 对象或保存 DWG。",
)
SCREENSHOT_ORCHESTRATION_PHRASES = (
    "截图编排",
    "target_handles",
    "repair_plan",
    "execution_summary.created_handles",
    "PrintWindow",
    "visual_aid_only",
    "focus_target_unavailable",
)
SYSTEM_ASSET_REUSE_PHRASES = (
    "系统资产",
    "system_asset_reuse_workflow",
    "style_export",
    "style_definition",
    "native_style_definition_written",
    "nativeVisiblePanelEvidence",
    "reuseWorkflowProbe",
    "training_panel",
    "savedCurrentDwg=false",
)
VISUAL_WAREHOUSE_PHRASES = (
    "layoutReadabilityAcceptable",
    "aisleClearanceAcceptable",
    "contentDensityAcceptable",
    "sourceProofRolesSeparated",
    "layerSemanticsAcceptable",
    "nonScreenshotEvidenceChecked",
    "layerCounts",
    "nativeVisiblePanelEvidence",
    "reuseWorkflowProbe",
    "ASSET_PROOF_CONTENT",
    "ASSET_SOURCE_BOUNDARY",
)
MODEL_BACKED_AGENT_PHRASES = (
    "模型型复审",
    "core/model_review",
    "codex.cmd exec",
    "modelBackedReview",
    "modelBackedVisualAcceptance",
    "modelProviderStatus",
    "modelUnavailable",
    "schemaValid",
    "modelAssistedDecision",
    "modelBackedRepairPlan",
    "proposal_only",
    "repairRecommendation",
    "blockingReasons",
)


def parse_iso_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return fallback


def load_workbench_data(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    match = DATA_ASSIGNMENT_RE.match(text)
    if not match:
        raise ValueError(f"{path} is not a capability-map-data.js assignment")
    return json.loads(match.group("payload"))


def check(name: str, passed: bool, detail: str) -> dict[str, str]:
    return {"name": name, "status": "pass" if passed else "fail", "detail": detail}


def run_agent_check(
    root: Path = PROJECT_ROOT,
    data_path: Path | None = None,
    html_path: Path | None = None,
) -> dict[str, Any]:
    data_file = data_path or root / "capability-map-data.js"
    html_file = html_path or root / "capability-map.html"
    checks: list[dict[str, str]] = []

    try:
        data = load_workbench_data(data_file)
    except Exception as exc:  # noqa: BLE001 - report contract should preserve exact failure.
        return {
            "status": "fail",
            "data_path": str(data_file),
            "html_path": str(html_file),
            "checks": [check("load_snapshot", False, str(exc))],
            "summary": {"check_count": 1, "failed_check_count": 1},
        }

    checks.append(check("schema_v2", data.get("schemaVersion") == 2, "训练工作台数据必须是 schemaVersion=2。"))

    programs = data.get("trainingPrograms", [])
    agents = data.get("agentProfiles", [])
    contracts = data.get("promptContracts", [])
    checks.append(check("has_training_programs", bool(programs), f"trainingPrograms={len(programs)}"))
    checks.append(check("has_agent_profiles", bool(agents), f"agentProfiles={len(agents)}"))
    checks.append(check("has_prompt_contracts", bool(contracts), f"promptContracts={len(contracts)}"))
    designer = data.get("designerAgent", {})
    growth_stages = data.get("growthStages", [])
    foundation_courses = data.get("foundationCourses", [])
    training_batches = data.get("trainingBatches", [])
    validation_checkers = data.get("validationCheckers", [])
    checks.append(check("designer_agent_declared", designer.get("id") == "cad_designer", f"designerAgent.id={designer.get('id')}"))
    checks.append(check("growth_stages_declared", len(growth_stages) >= 7, f"growthStages={len(growth_stages)}"))
    checks.append(check("foundation_courses_declared", len(foundation_courses) >= 7, f"foundationCourses={len(foundation_courses)}"))
    checks.append(check("training_batches_declared", len(training_batches) >= 6, f"trainingBatches={len(training_batches)}"))
    checks.append(check("validation_checkers_declared", len(validation_checkers) >= 8, f"validationCheckers={len(validation_checkers)}"))

    program_ids = {program.get("capabilityId") for program in programs}
    batch_ids = {batch.get("id") for batch in training_batches}
    checker_ids = {checker.get("id") for checker in validation_checkers}
    missing_batch_programs = sorted(
        {
            program_id
            for batch in training_batches
            for program_id in batch.get("programIds", [])
            if program_id not in program_ids
        }
    )
    missing_batch_dependencies = sorted(
        {
            dependency_id
            for batch in training_batches
            for dependency_id in batch.get("dependsOn", [])
            if dependency_id not in batch_ids
        }
    )
    missing_batch_checkers = sorted(
        {
            checker_id
            for batch in training_batches
            for checker_id in batch.get("checkerIds", [])
            if checker_id not in checker_ids
        }
    )
    checks.append(check("training_batch_program_refs_exist", not missing_batch_programs, f"missing={missing_batch_programs}"))
    checks.append(check("training_batch_dependencies_exist", not missing_batch_dependencies, f"missing={missing_batch_dependencies}"))
    checks.append(check("training_batch_checker_refs_exist", not missing_batch_checkers, f"missing={missing_batch_checkers}"))

    agent_ids = {agent.get("id") for agent in agents}
    contract_ids = {contract.get("agentId") for contract in contracts}
    responsible_ids = {
        agent_id
        for program in programs
        for agent_id in program.get("responsibleAgentIds", [])
    }
    missing_agents = sorted(responsible_ids - agent_ids)
    missing_contracts = sorted(responsible_ids - contract_ids)
    checks.append(check("responsible_agents_have_profiles", not missing_agents, f"missing={missing_agents}"))
    checks.append(check("responsible_agents_have_contracts", not missing_contracts, f"missing={missing_contracts}"))

    missing_refs: list[str] = []
    wildcard_refs: list[str] = []
    for contract in contracts:
        for source_ref in contract.get("sourceRefs", []):
            source_path = source_ref.get("path", "")
            if not source_path:
                missing_refs.append("<empty>")
                continue
            if "<" in source_path or "*" in source_path:
                wildcard_refs.append(source_path)
                continue
            if not (root / source_path).is_file():
                missing_refs.append(source_path)
    checks.append(check("source_refs_are_concrete", not wildcard_refs, f"wildcard={wildcard_refs}"))
    checks.append(check("source_refs_exist", not missing_refs, f"missing={missing_refs}"))

    missing_common_contract_refs = [
        str(contract.get("agentId") or contract.get("id") or "<unknown>")
        for contract in contracts
        if COMMON_PROMPT_CONTRACT_REL not in {source_ref.get("path") for source_ref in contract.get("sourceRefs", [])}
    ]
    duplicated_common_rules: list[str] = []
    common_contract_text = ""
    common_contract_path = root / COMMON_PROMPT_CONTRACT_REL
    if common_contract_path.is_file():
        common_contract_text = common_contract_path.read_text(encoding="utf-8", errors="replace")
    missing_screenshot_phrases = [
        phrase for phrase in SCREENSHOT_ORCHESTRATION_PHRASES if phrase not in common_contract_text
    ]
    missing_system_asset_phrases = [
        phrase for phrase in SYSTEM_ASSET_REUSE_PHRASES if phrase not in common_contract_text
    ]
    missing_visual_warehouse_phrases = [
        phrase for phrase in VISUAL_WAREHOUSE_PHRASES if phrase not in common_contract_text
    ]
    missing_model_backed_agent_phrases = [
        phrase for phrase in MODEL_BACKED_AGENT_PHRASES if phrase not in common_contract_text
    ]
    for prompt_path in sorted((root / "agents").glob("**/prompt_addendum.md")):
        text = prompt_path.read_text(encoding="utf-8", errors="replace")
        rel_path = prompt_path.relative_to(root).as_posix()
        for rule in COMMON_PROMPT_RULES:
            if rule in text:
                duplicated_common_rules.append(f"{rel_path}::{rule}")
    checks.append(
        check(
            "common_prompt_contract_referenced",
            not missing_common_contract_refs,
            f"missing={missing_common_contract_refs}",
        )
    )
    checks.append(
        check(
            "screenshot_orchestration_rules_in_common_contract",
            common_contract_path.is_file() and not missing_screenshot_phrases,
            f"missing_phrases={missing_screenshot_phrases}",
        )
    )
    checks.append(
        check(
            "system_asset_reuse_rules_in_common_contract",
            common_contract_path.is_file() and not missing_system_asset_phrases,
            f"missing_phrases={missing_system_asset_phrases}",
        )
    )
    checks.append(
        check(
            "visual_warehouse_rules_in_common_contract",
            common_contract_path.is_file() and not missing_visual_warehouse_phrases,
            f"missing_phrases={missing_visual_warehouse_phrases}",
        )
    )
    checks.append(
        check(
            "model_backed_agent_rules_in_common_contract",
            common_contract_path.is_file() and not missing_model_backed_agent_phrases,
            f"missing_phrases={missing_model_backed_agent_phrases}",
        )
    )
    checks.append(
        check(
            "prompt_addenda_do_not_duplicate_common_rules",
            not duplicated_common_rules,
            f"duplicates={duplicated_common_rules}",
        )
    )

    learning = data.get("trainingLearning", {})
    training_sources = data.get("trainingSources", [])
    source_by_path = {
        str(source.get("path", "")): source
        for source in training_sources
        if source.get("path")
    }
    fact_source_paths = {
        path
        for path, source in source_by_path.items()
        if source.get("role") == "fact_source"
    }
    missing_training_sources = [
        path
        for path, source in source_by_path.items()
        if source.get("status", "active") == "active" and not (root / path).is_file()
    ]
    checks.append(check("training_sources_declared", bool(training_sources), f"trainingSources={len(training_sources)}"))
    checks.append(check("training_source_paths_exist", not missing_training_sources, f"missing={missing_training_sources}"))

    training_source_summary = data.get("trainingSourceSummary", {})
    portable_policy = str(training_source_summary.get("portableEvidencePolicy", ""))
    recommendation_code = str(training_source_summary.get("recommendationCode", ""))
    restore_paths = training_source_summary.get("restorePaths", [])
    checks.append(
        check(
            "training_source_summary_declared",
            training_source_summary.get("schemaVersion") == "training-source-summary/v1",
            f"schemaVersion={training_source_summary.get('schemaVersion')}",
        )
    )
    checks.append(
        check(
            "training_source_summary_portable_policy_declared",
            "不是浏览器缓存" in portable_policy
            and bool(recommendation_code)
            and isinstance(restore_paths, list)
            and "output/training_queues/**" in restore_paths,
            f"recommendationCode={recommendation_code} restorePaths={restore_paths}",
        )
    )

    accepted_programs = [program for program in programs if program.get("trainingAcceptance")]
    accepted_sources = sorted(
        {
            program.get("trainingAcceptance", {}).get("source", "")
            for program in accepted_programs
            if program.get("trainingAcceptance", {}).get("source")
        }
    )
    accepted_sources_not_registered = [
        path for path in accepted_sources if path not in fact_source_paths
    ]
    accepted_sources_use_derived_snapshot = [
        path
        for path in accepted_sources
        if source_by_path.get(path, {}).get("role") == "derived"
    ]
    checks.append(
        check(
            "accepted_training_sources_registered",
            not accepted_sources_not_registered,
            f"missing={accepted_sources_not_registered}",
        )
    )
    checks.append(
        check(
            "accepted_training_uses_fact_sources",
            not accepted_sources_use_derived_snapshot,
            f"derived_used={accepted_sources_use_derived_snapshot}",
        )
    )
    missing_learning = [
        program.get("capabilityId")
        for program in accepted_programs
        if program.get("learningPromotion", {}).get("status") != "promoted"
    ]
    gate_decision_keys = {
        "updateTrainingSource",
        "updateWorkbench",
        "updateBaseRules",
        "updateTaskRules",
        "updateAgentCalibration",
        "updateChecker",
        "retestOriginalTask",
    }
    missing_promotion_gate: list[str] = []
    incomplete_promotion_gate: list[str] = []
    for program in accepted_programs:
        learning_promotion = program.get("learningPromotion", {})
        if learning_promotion.get("status") != "promoted":
            continue
        gate = learning_promotion.get("promotionGate", {})
        if gate.get("schemaVersion") != 1:
            missing_promotion_gate.append(str(program.get("capabilityId")))
            continue
        decisions = gate.get("decisions", {})
        missing_keys = sorted(gate_decision_keys - set(decisions))
        if missing_keys:
            incomplete_promotion_gate.append(f"{program.get('capabilityId')}:{missing_keys}")
    missing_plain_acceptance = [
        program.get("capabilityId")
        for program in accepted_programs
        if not program.get("trainingAcceptance", {}).get("plainLanguageSummary")
    ]
    raw_path_in_visible_training = [
        program.get("capabilityId")
        for program in accepted_programs
        if any(
            token in " ".join(
                [
                    str(program.get("stageState", {}).get("note", "")),
                    str(program.get("assetStates", {}).get("trained", {}).get("note", "")),
                ]
            )
            for token in (".json", "output/")
        )
    ]
    checks.append(
        check(
            "accepted_training_has_learning_promotion",
            not missing_learning,
            f"missing_learning={missing_learning}",
        )
    )
    checks.append(
        check(
            "systemized_training_has_promotion_gate",
            not missing_promotion_gate,
            f"missing={missing_promotion_gate}",
        )
    )
    checks.append(
        check(
            "promotion_gate_decisions_complete",
            not incomplete_promotion_gate,
            f"incomplete={incomplete_promotion_gate}",
        )
    )
    checks.append(
        check(
            "accepted_training_has_plain_language_summary",
            not missing_plain_acceptance,
            f"missing_plain={missing_plain_acceptance}",
        )
    )
    checks.append(
        check(
            "accepted_training_visible_text_hides_backend_paths",
            not raw_path_in_visible_training,
            f"raw_path_visible={raw_path_in_visible_training}",
        )
    )
    learning_refs = sorted(
        {
            source_ref
            for agent in learning.get("byAgent", {}).values()
            for source_ref in agent.get("sourceRefs", [])
            if source_ref
        }
    )
    missing_learning_refs = [path for path in learning_refs if not (root / path).is_file()]
    contract_ref_paths = {
        source_ref.get("path")
        for contract in contracts
        for source_ref in contract.get("sourceRefs", [])
    }
    missing_contract_learning_refs = [path for path in learning_refs if path not in contract_ref_paths]
    checks.append(check("agent_learning_refs_exist", not missing_learning_refs, f"missing={missing_learning_refs}"))
    checks.append(
        check(
            "prompt_contracts_include_learning_refs",
            not missing_contract_learning_refs,
            f"missing={missing_contract_learning_refs}",
        )
    )

    table_c = data.get("tableCBoundary", {})
    coverage_rel = table_c.get("sourcePath", "output/validation_runs/capability-lab/cad_capability_coverage.json")
    coverage_path = root / coverage_rel
    coverage = read_json(coverage_path, {})
    coverage_headline = coverage.get("summary", {}).get("cad_strength_headline_percent")
    data_headline = table_c.get("headlinePercent")
    checks.append(check("coverage_source_exists", coverage_path.is_file(), coverage_rel))
    checks.append(
        check(
            "table_c_headline_matches_coverage",
            coverage_headline == data_headline,
            f"data={data_headline}, coverage={coverage_headline}",
        )
    )
    table_c_boundary_text = " ".join(
        [
            str(table_c.get("label", "")),
            str(table_c.get("metricLabel", "")),
            str(table_c.get("legacyAlias", "")),
            str(table_c.get("note", "")),
            " ".join(str(item) for item in table_c.get("notProofOf", []) if item),
        ]
    )
    checks.append(
        check(
            "table_c_three_maturity_boundary_declared",
            "Core Proof Coverage" in table_c_boundary_text
            and "Agent Task Maturity" in table_c_boundary_text
            and "Project Delivery Readiness" in table_c_boundary_text,
            table_c_boundary_text,
        )
    )

    generated_at = parse_iso_datetime(data.get("generatedAt", ""))
    coverage_generated_at = parse_iso_datetime(coverage.get("generated_at", ""))
    generated_after_coverage = bool(generated_at and coverage_generated_at and generated_at >= coverage_generated_at)
    checks.append(
        check(
            "snapshot_generated_after_coverage",
            generated_after_coverage,
            f"snapshot={data.get('generatedAt')}, coverage={coverage.get('generated_at')}",
        )
    )

    sync = data.get("workbenchSync", {})
    checks.append(check("sync_boundary_declared", sync.get("mode") == "static_snapshot", "workbenchSync.mode=static_snapshot"))
    checks.append(check("sync_command_declared", "sync_training_workbench.py" in sync.get("recommendedCommand", ""), sync.get("recommendedCommand", "")))
    checks.append(check("launcher_declared", sync.get("launcher") == "start_training_workbench.bat", sync.get("launcher", "")))
    trace_viewer = data.get("modelTraceViewer", {})
    trace_policy = trace_viewer.get("sourcePolicy", {}) if isinstance(trace_viewer, dict) else {}
    trace_truth_sources = set(trace_policy.get("truthSources", [])) if isinstance(trace_policy, dict) else set()
    trace_not_proof = set(trace_policy.get("notProofOf", [])) if isinstance(trace_policy, dict) else set()
    checks.append(
        check(
            "model_trace_viewer_declared",
            trace_viewer.get("schemaVersion") == "workbench-trace-viewer/v1",
            f"schemaVersion={trace_viewer.get('schemaVersion')}",
        )
    )
    checks.append(
        check(
            "model_trace_viewer_derived_only",
            trace_policy.get("derivedOnly") is True
            and "does_not_prove_cad_geometry" in trace_not_proof,
            f"derivedOnly={trace_policy.get('derivedOnly')} notProofOf={sorted(trace_not_proof)}",
        )
    )
    checks.append(
        check(
            "model_trace_viewer_truth_sources_declared",
            {"output/runs/**", "output/model_reviews/traces/**"}.issubset(trace_truth_sources),
            f"truthSources={sorted(trace_truth_sources)}",
        )
    )

    workbench_v3 = data.get("workbenchV3", {})
    workbench_v3 = workbench_v3 if isinstance(workbench_v3, dict) else {}
    v3_policy = workbench_v3.get("sourcePolicy", {}) if isinstance(workbench_v3.get("sourcePolicy"), dict) else {}
    v3_views = workbench_v3.get("views", {}) if isinstance(workbench_v3.get("views"), dict) else {}
    v3_facts = workbench_v3.get("facts", {}) if isinstance(workbench_v3.get("facts"), dict) else {}
    command_center = v3_views.get("commandCenter", {}) if isinstance(v3_views.get("commandCenter"), dict) else {}
    agent_graph = v3_views.get("agentGraph", {}) if isinstance(v3_views.get("agentGraph"), dict) else {}
    evidence_center = v3_views.get("evidenceCenter", {}) if isinstance(v3_views.get("evidenceCenter"), dict) else {}
    source_registry = v3_facts.get("sourceRegistry", [])
    source_registry = source_registry if isinstance(source_registry, list) else []
    next_candidates = command_center.get("nextTrainingCandidates", [])
    next_candidates = next_candidates if isinstance(next_candidates, list) else []
    v3_gateboard = command_center.get("gateboard", [])
    v3_gateboard = v3_gateboard if isinstance(v3_gateboard, list) else []
    graph_nodes = agent_graph.get("nodes", [])
    graph_edges = agent_graph.get("edges", [])
    graph_nodes = graph_nodes if isinstance(graph_nodes, list) else []
    graph_edges = graph_edges if isinstance(graph_edges, list) else []
    evidence_bundles = evidence_center.get("evidenceBundles", [])
    evidence_bundles = evidence_bundles if isinstance(evidence_bundles, list) else []
    v3_truth_sources = set(v3_policy.get("truthSources", [])) if isinstance(v3_policy.get("truthSources"), list) else set()
    v3_not_proof = set(v3_policy.get("notProofOf", [])) if isinstance(v3_policy.get("notProofOf"), list) else set()
    v3_derived_artifacts = set(v3_policy.get("derivedArtifacts", [])) if isinstance(v3_policy.get("derivedArtifacts"), list) else set()

    checks.append(
        check(
            "workbench_v3_declared",
            workbench_v3.get("schemaVersion") == "workbench-data-contract/v3-draft",
            f"schemaVersion={workbench_v3.get('schemaVersion')}",
        )
    )
    checks.append(
        check(
            "workbench_v3_source_policy_derived_only",
            v3_policy.get("derivedOnly") is True
            and {"capability-map-data.js", "capability-map.html"}.issubset(v3_derived_artifacts)
            and "docs/training/training-sources.json" in v3_truth_sources
            and "cad_geometry" in v3_not_proof,
            f"derivedOnly={v3_policy.get('derivedOnly')} derivedArtifacts={sorted(v3_derived_artifacts)} truthSources={sorted(v3_truth_sources)} notProofOf={sorted(v3_not_proof)}",
        )
    )
    checks.append(
        check(
            "workbench_v3_source_registry_declared",
            bool(source_registry)
            and all(source.get("role") != "derived" or source.get("evidenceUse") == "display_only" for source in source_registry),
            f"sourceRegistry={len(source_registry)}",
        )
    )
    checks.append(
        check(
            "workbench_v3_command_center_declared",
            bool(command_center.get("evidenceBoundary"))
            and bool(command_center.get("derivedBoundary"))
            and isinstance(command_center.get("sourceHealth"), dict),
            f"keys={sorted(command_center.keys())}",
        )
    )
    checks.append(
        check(
            "workbench_v3_next_candidates_declared",
            bool(next_candidates)
            and all(
                {"id", "label", "routeMode", "responsibleAgentIds", "evidenceRequired", "blockingConditions"}.issubset(candidate)
                for candidate in next_candidates
            ),
            f"nextTrainingCandidates={len(next_candidates)}",
        )
    )
    checks.append(
        check(
            "workbench_v3_gateboard_declared",
            {"snapshot_freshness", "source_health", "table_c_boundary"}.issubset({gate.get("id") for gate in v3_gateboard})
            and all({"id", "label", "status", "detail"}.issubset(gate) for gate in v3_gateboard),
            f"gateboard={len(v3_gateboard)}",
        )
    )
    checks.append(
        check(
            "workbench_v3_agent_graph_declared",
            agent_graph.get("schemaVersion") == "agent-system-workbench/v1"
            and any(node.get("id") == "agent:cad_designer" for node in graph_nodes)
            and any(edge.get("edgeType") == "responsible_for" for edge in graph_edges),
            f"nodes={len(graph_nodes)} edges={len(graph_edges)}",
        )
    )
    checks.append(
        check(
            "workbench_v3_evidence_bundles_declared",
            bool(evidence_bundles)
            and all({"programId", "capabilityId", "evidenceTypes", "sourceRefs", "notProven"}.issubset(bundle) for bundle in evidence_bundles)
            and any("derived_snapshot" in bundle.get("evidenceTypes", []) for bundle in evidence_bundles),
            f"evidenceBundles={len(evidence_bundles)}",
        )
    )

    html_text = html_file.read_text(encoding="utf-8") if html_file.exists() else ""
    checks.append(check("html_sync_panel_present", "syncPanel" in html_text, "页面必须显示同步状态。"))
    checks.append(check("html_polling_present", "initSnapshotPolling" in html_text, "HTTP 启动时页面必须能检测新快照。"))
    checks.append(
        check(
            "html_boundary_copy_present",
            "Core Proof Coverage" in html_text
            and "Agent Task Maturity" in html_text
            and "Project Delivery Readiness" in html_text,
            "页面必须保留 Core Proof Coverage / Agent Task Maturity / Project Delivery Readiness 三口径边界说明。",
        )
    )
    checks.append(check("html_learning_promotion_present", "learningPromotion" in html_text and "已学习" in html_text, "页面必须显示智能体学习沉淀状态。"))
    checks.append(check("html_trace_viewer_present", "view-traces" in html_text and "renderTraceViewer" in html_text, "页面必须显示模型 Trace 派生视图。"))
    checks.append(
        check(
            "html_flightdeck_overview_present",
            'data-tab="overview"' in html_text
            and 'id="view-overview"' in html_text
            and "renderCommandCenter" in html_text
            and "commandCenter" in html_text
            and "训练飞控台" in html_text,
            "页面必须默认提供训练飞控台首屏。",
        )
    )
    checks.append(
        check(
            "html_training_source_sync_present",
            "训练证据同步" in html_text and "trainingSourceSummary" in html_text,
            "页面必须解释跨电脑训练证据同步状态。",
        )
    )

    failed = [item for item in checks if item["status"] != "pass"]
    return {
        "status": "pass" if not failed else "fail",
        "data_path": str(data_file),
        "html_path": str(html_file),
        "checks": checks,
        "summary": {"check_count": len(checks), "failed_check_count": len(failed)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the CAD Agent training workbench snapshot.")
    parser.add_argument("--data", type=Path, default=PROJECT_ROOT / "capability-map-data.js")
    parser.add_argument("--html", type=Path, default=PROJECT_ROOT / "capability-map.html")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "output" / "validation_runs" / "training-workbench-sync" / "agent_check.json")
    args = parser.parse_args()

    report = run_agent_check(PROJECT_ROOT, data_path=args.data, html_path=args.html)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
