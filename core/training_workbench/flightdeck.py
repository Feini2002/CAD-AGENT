from __future__ import annotations

from pathlib import Path
from typing import Any


WORKBENCH_V3_SCHEMA = "workbench-data-contract/v3-draft"


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _path_exists(root: Path, rel_path: str) -> bool:
    if not rel_path:
        return False
    return (root / rel_path).is_file()


def build_source_registry(root: Path, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in sources:
        rel_path = str(source.get("path") or "")
        role = str(source.get("role") or "")
        status = str(source.get("status") or "active")
        exists = _path_exists(root, rel_path)
        if role == "derived":
            status_class = "derived"
            evidence_use = "display_only"
        elif status == "archived":
            status_class = "archived_only"
            evidence_use = "historical_reference_only"
        elif role == "fact_source" and status == "active" and exists:
            status_class = "active_fact_source"
            evidence_use = "eligible_fact_source"
        elif role == "fact_source":
            status_class = "missing_evidence"
            evidence_use = "blocked_until_restored"
        else:
            status_class = "unknown"
            evidence_use = "not_checked"
        rows.append(
            {
                "id": source.get("id") or rel_path,
                "kind": source.get("kind") or "unknown",
                "role": role or "unknown",
                "status": status,
                "path": rel_path,
                "exists": exists,
                "owner": source.get("owner") or "",
                "statusClass": status_class,
                "evidenceUse": evidence_use,
                "desc": source.get("desc") or "",
            }
        )
    return rows


def _gate(
    gate_id: str,
    label: str,
    status: str,
    detail: str,
    *,
    source_path: str = "",
    blocked_claims: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": gate_id,
        "label": label,
        "status": status,
        "detail": detail,
        "sourcePath": source_path,
        "blockedClaims": blocked_claims or [],
    }


def build_gateboard(data: dict[str, Any], source_registry: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sync = data.get("workbenchSync", {}) if isinstance(data.get("workbenchSync"), dict) else {}
    table_c = data.get("tableCBoundary", {}) if isinstance(data.get("tableCBoundary"), dict) else {}
    source_summary = data.get("trainingSourceSummary", {}) if isinstance(data.get("trainingSourceSummary"), dict) else {}
    active_missing = int(source_summary.get("activeFactSourceMissingCount") or 0)
    active_acceptance = int(source_summary.get("activeTrainingAcceptanceReportCount") or 0)
    archived_acceptance = int(source_summary.get("archivedTrainingAcceptanceReportCount") or 0)

    snapshot_ok = sync.get("generatedAfterCoverage") is not False
    coverage_exists = table_c.get("sourceExists") is not False
    source_status = "blocked" if active_missing else "warning" if not active_acceptance and archived_acceptance else "pass"
    return [
        _gate(
            "snapshot_freshness",
            "快照新鲜度",
            "pass" if snapshot_ok else "blocked",
            "快照不早于 coverage。" if snapshot_ok else "快照可能早于 coverage，需要重新同步。",
            source_path="capability-map-data.js",
            blocked_claims=[] if snapshot_ok else ["workbench_sync_complete_claim"],
        ),
        _gate(
            "coverage_source",
            "Coverage 来源",
            "pass" if coverage_exists else "blocked",
            "表 C coverage JSON 可读取。" if coverage_exists else "表 C coverage JSON 缺失或未声明。",
            source_path=table_c.get("sourcePath", "output/validation_runs/capability-lab/cad_capability_coverage.json"),
            blocked_claims=[] if coverage_exists else ["table_c_claim"],
        ),
        _gate(
            "source_health",
            "训练事实源",
            source_status,
            source_summary.get("recommendedAction")
            or "训练状态依赖 active fact_source；archived 只作历史索引。",
            source_path="docs/training/training-sources.json",
            blocked_claims=["training_acceptance_claim"] if source_status == "blocked" else [],
        ),
        _gate(
            "agent_check_status",
            "Agent check 收尾",
            "not_checked",
            "Agent check 在快照生成后由 sync_training_workbench.py / run_training_workbench_agent_check.py 执行；本 gate 只提醒不能用生成阶段状态替代收尾检查。",
            source_path="scripts/run_training_workbench_agent_check.py",
            blocked_claims=["workbench_sync_complete_claim"],
        ),
        _gate(
            "encoding_health",
            "中文编码",
            "not_checked",
            "飞控台展示 UTF-8 派生快照；正式 CAD 写入前仍需入口编码预检。",
            blocked_claims=["cad_write_claim"],
        ),
        _gate(
            "data_bloat_evidence_closure",
            "数据防膨胀 / 证据闭合",
            "not_checked",
            "本页只显示 compact 派生摘要；正式训练收尾仍需 data-bloat / evidence-closure gate。",
            blocked_claims=["training_closeout_complete_claim", "artifact_cleanup_write"],
        ),
        _gate(
            "table_c_boundary",
            "表 C 边界",
            "pass" if coverage_exists else "blocked",
            "表 C 来自 coverage JSON，不等于训练项 pass、Agent 成熟度或 Prompt ready。",
            source_path=table_c.get("sourcePath", ""),
        ),
        _gate(
            "derived_snapshot_policy",
            "派生快照边界",
            "pass",
            "capability-map-data.js 与 HTML 只作显示器，不登记为 active fact_source。",
            source_path="capability-map-data.js",
        ),
    ]


def build_next_training_candidates(data: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    programs = _as_list(data.get("trainingPrograms"))
    source_summary = data.get("trainingSourceSummary", {}) if isinstance(data.get("trainingSourceSummary"), dict) else {}
    needs_restore = source_summary.get("recommendationCode") == "restore_remote_evidence_before_retraining"

    def sort_key(program: dict[str, Any]) -> tuple[int, int, str]:
        priority_rank = {"P0": 0, "P1": 1, "P2": 2}.get(str(program.get("priority")), 3)
        complete_rank = 1 if program.get("isFullyComplete") else 0
        return (complete_rank, priority_rank, str(program.get("name") or ""))

    candidates: list[dict[str, Any]] = []
    for program in sorted(programs, key=sort_key):
        if program.get("isFullyComplete"):
            continue
        responsible = [str(agent_id) for agent_id in program.get("responsibleAgentIds", [])]
        route_mode = "focused_retraining" if program.get("matrixGroup") == "CAD 基础操作" else "formal_acceptance"
        blocking = []
        if needs_restore:
            blocking.append("本机 active 验收报告为 0，历史证据为 archived；优先恢复旧 evidence 后再判断是否重训。")
        candidates.append(
            {
                "id": program.get("id"),
                "programId": program.get("id"),
                "capabilityId": program.get("capabilityId"),
                "label": program.get("name"),
                "priority": program.get("priority"),
                "group": program.get("matrixGroup") or program.get("group"),
                "routeMode": route_mode,
                "reason": f"{program.get('priority', 'P?')} · {program.get('stageState', {}).get('label', '待训练')} · {program.get('nextTrainingTarget', '')}",
                "responsibleAgentIds": responsible,
                "evidenceRequired": [
                    *program.get("evidenceRequired", [])[:3],
                    "通过前必须声明 checked / not_checked，截图不能替代 CAD readback。",
                ],
                "blockingConditions": blocking,
            }
        )
        if len(candidates) >= limit:
            break
    return candidates


def build_agent_graph(
    data: dict[str, Any],
    source_registry: list[dict[str, Any]] | None = None,
    gateboard: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    programs = _as_list(data.get("trainingPrograms"))
    agents = _as_list(data.get("agentProfiles"))
    contracts = _as_list(data.get("promptContracts"))
    source_registry = source_registry or []
    gateboard = gateboard or []
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for agent in agents:
        agent_id = str(agent.get("id") or "")
        if not agent_id:
            continue
        nodes.append(
            {
                "id": f"agent:{agent_id}",
                "label": agent.get("name") or agent_id,
                "nodeType": "agent",
                "group": agent.get("group") or "unknown",
                "executionMode": (agent.get("executionModel") or {}).get("type", "rule_contract"),
                "sourceRefs": agent.get("docs", []),
                "evidenceBoundary": "Agent 成熟度不是 CAD 几何证明。",
            }
        )

    for contract in contracts:
        agent_id = str(contract.get("agentId") or "")
        if not agent_id:
            continue
        nodes.append(
            {
                "id": f"prompt-contract:{agent_id}",
                "label": contract.get("agentName") or agent_id,
                "nodeType": "prompt_contract",
                "group": "prompt",
                "sourceRefs": [ref.get("path") for ref in contract.get("sourceRefs", []) if ref.get("path")],
                "evidenceBoundary": contract.get("evidenceBoundary") or "Prompt contract 不代表模型已调用或 CAD 已通过。",
            }
        )
        edges.append(
            {
                "id": f"edge-agent-prompt-{agent_id}",
                "from": f"agent:{agent_id}",
                "to": f"prompt-contract:{agent_id}",
                "edgeType": "has_prompt_contract",
                "required": True,
            }
        )

    source_node_by_path: dict[str, str] = {}
    for source in source_registry:
        source_id = str(source.get("id") or source.get("path") or "")
        source_path = str(source.get("path") or "")
        if not source_id and not source_path:
            continue
        node_id = f"source:{source_id or source_path}"
        source_node_by_path[source_path] = node_id
        nodes.append(
            {
                "id": node_id,
                "label": source.get("kind") or source_path or source_id,
                "nodeType": "evidence_source",
                "group": source.get("role") or "source",
                "statusClass": source.get("statusClass"),
                "sourceRefs": [source_path] if source_path else [],
                "evidenceBoundary": source.get("evidenceUse") or "not_checked",
            }
        )

    for gate in gateboard:
        gate_id = str(gate.get("id") or "")
        if not gate_id:
            continue
        node_id = f"gate:{gate_id}"
        nodes.append(
            {
                "id": node_id,
                "label": gate.get("label") or gate_id,
                "nodeType": "hard_gate",
                "group": "gateboard",
                "status": gate.get("status") or "not_checked",
                "sourceRefs": [gate.get("sourcePath")] if gate.get("sourcePath") else [],
                "evidenceBoundary": "Gate 状态不替代 CAD readback 或用户验收。",
            }
        )
        source_path = str(gate.get("sourcePath") or "")
        if source_path and source_path in source_node_by_path:
            edges.append(
                {
                    "id": f"edge-gate-{gate_id}-source-{source_node_by_path[source_path]}",
                    "from": node_id,
                    "to": source_node_by_path[source_path],
                    "edgeType": "checked_against_source",
                    "required": False,
                }
            )

    seen_program_nodes: set[str] = set()
    for program in programs:
        program_node = f"program:{program.get('capabilityId')}"
        if program_node not in seen_program_nodes:
            nodes.append(
                {
                    "id": program_node,
                    "label": program.get("name") or program.get("capabilityId"),
                    "nodeType": "training_program",
                    "group": program.get("matrixGroup") or program.get("group"),
                    "sourceRefs": [],
                    "evidenceBoundary": "训练计划项不是 CAD 通过证明。",
                }
            )
        acceptance = program.get("trainingAcceptance", {}) if isinstance(program.get("trainingAcceptance"), dict) else {}
        acceptance_source = str(acceptance.get("source") or "")
        if acceptance_source and acceptance_source in source_node_by_path:
            edges.append(
                {
                    "id": f"edge-program-{program.get('capabilityId')}-source-{source_node_by_path[acceptance_source]}",
                    "from": program_node,
                    "to": source_node_by_path[acceptance_source],
                    "edgeType": "uses_evidence_source",
                    "required": True,
                    "capabilityId": program.get("capabilityId"),
                }
            )
            seen_program_nodes.add(program_node)
        for agent_id in program.get("responsibleAgentIds", []):
            edges.append(
                {
                    "id": f"edge-program-{program.get('capabilityId')}-agent-{agent_id}",
                    "from": program_node,
                    "to": f"agent:{agent_id}",
                    "edgeType": "responsible_for",
                    "required": agent_id == program.get("ownerAgentId"),
                    "programId": program.get("id"),
                    "capabilityId": program.get("capabilityId"),
                }
            )

    return {
        "schemaVersion": "agent-system-workbench/v1",
        "nodes": nodes,
        "edges": edges,
        "sourcePolicy": {
            "derivedOnly": True,
            "truthSources": [
                "agents/pipeline/pipeline_manifest.json",
                "agents/**/agent.json",
                "agents/**/rules.md",
                "docs/training/training-sources.json",
            ],
        },
    }


def build_evidence_bundles(data: dict[str, Any]) -> list[dict[str, Any]]:
    bundles: list[dict[str, Any]] = []
    for program in _as_list(data.get("trainingPrograms")):
        acceptance = program.get("trainingAcceptance", {}) if isinstance(program.get("trainingAcceptance"), dict) else {}
        learning = program.get("learningPromotion", {}) if isinstance(program.get("learningPromotion"), dict) else {}
        evidence_types = ["derived_snapshot"]
        source_refs = ["capability-map-data.js"]
        if acceptance:
            evidence_types.append("training_acceptance_report")
            if acceptance.get("source"):
                source_refs.append(str(acceptance.get("source")))
            if acceptance.get("readbackCount") or acceptance.get("handleCount"):
                evidence_types.append("cad_readback")
        if learning.get("status") == "promoted":
            evidence_types.append("learning_promotion")
        status = "systemized" if learning.get("status") == "promoted" else "accepted" if acceptance else "planned"
        bundles.append(
            {
                "id": f"evidence:{program.get('capabilityId')}",
                "programId": program.get("id"),
                "capabilityId": program.get("capabilityId"),
                "label": program.get("name"),
                "status": status,
                "evidenceTypes": evidence_types,
                "sourceRefs": source_refs,
                "checked": ["training plan snapshot"] + (["acceptance summary"] if acceptance else []),
                "notProven": [
                    "derived snapshot does not prove CAD geometry",
                    "screenshot or trace still requires CAD readback when claiming real CAD output",
                ],
            }
        )
    return bundles


def build_workbench_v3(root: Path, data: dict[str, Any]) -> dict[str, Any]:
    source_registry = build_source_registry(root, _as_list(data.get("trainingSources")))
    gateboard = build_gateboard(data, source_registry)
    candidates = build_next_training_candidates(data)
    agent_graph = build_agent_graph(data, source_registry, gateboard)
    evidence_bundles = build_evidence_bundles(data)
    command_center = {
        "title": "CAD Agent 训练飞控台",
        "summary": "默认回答今天能不能训、训什么、谁负责、证据缺哪里。",
        "nextTrainingCandidates": candidates,
        "gateboard": gateboard,
        "sourceHealth": {
            "activeFactSourceCount": len([source for source in source_registry if source["statusClass"] == "active_fact_source"]),
            "archivedOnlyCount": len([source for source in source_registry if source["statusClass"] == "archived_only"]),
            "derivedCount": len([source for source in source_registry if source["statusClass"] == "derived"]),
            "missingEvidenceCount": len([source for source in source_registry if source["statusClass"] == "missing_evidence"]),
        },
        "agentDispatchSummary": {
            "agentCount": len(_as_list(data.get("agentProfiles"))),
            "edgeCount": len(agent_graph["edges"]),
            "primaryAgentId": (data.get("designerAgent") or {}).get("id", "cad_designer"),
        },
        "latestRunSummary": (data.get("modelTraceViewer") or {}).get("summary", {}),
        "evidenceBoundary": "表 C、训练进度、Agent 成熟度、Prompt ready、Trace 和截图必须分开；真实 CAD 仍看 created handles / readback / audit。",
        "derivedBoundary": "capability-map-data.js 和 capability-map.html 是派生快照，不是事实源。",
    }
    return {
        "schemaVersion": WORKBENCH_V3_SCHEMA,
        "meta": {
            "generatedAt": data.get("generatedAt"),
            "snapshotMode": "static_snapshot",
            "rootSchemaVersion": data.get("schemaVersion"),
        },
        "facts": {
            "sourceRegistry": source_registry,
            "trainingProgramCount": len(_as_list(data.get("trainingPrograms"))),
            "agentCount": len(_as_list(data.get("agentProfiles"))),
            "promptContractCount": len(_as_list(data.get("promptContracts"))),
        },
        "indices": {
            "programById": {program.get("id"): program.get("capabilityId") for program in _as_list(data.get("trainingPrograms"))},
            "agentById": {agent.get("id"): agent.get("name") for agent in _as_list(data.get("agentProfiles"))},
        },
        "views": {
            "commandCenter": command_center,
            "agentGraph": agent_graph,
            "evidenceCenter": {
                "sourceRegistry": source_registry,
                "evidenceBundles": evidence_bundles,
                "coverageBoundary": data.get("tableCBoundary", {}),
            },
        },
        "syncHealth": {
            "gateboard": gateboard,
            "sourceHealth": command_center["sourceHealth"],
        },
        "sourcePolicy": {
            "derivedOnly": True,
            "derivedArtifacts": ["capability-map-data.js", "capability-map.html"],
            "truthSources": [
                "docs/training/training-sources.json",
                "output/validation_runs/capability-lab/cad_capability_coverage.json",
                "agents/**/training_memory.json",
                "agents/**/prompt_addendum.md",
                "output/runs/**",
            ],
            "notProofOf": [
                "cad_geometry",
                "training_acceptance",
                "user_acceptance",
                "table_c_promotion",
            ],
        },
    }
