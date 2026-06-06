"""Local rule-context retrieval for model-backed pipeline agents.

The pack is a compact, traceable input contract for read-only model calls. It
does not replace source rules, schema validation, CAD readback, or user review.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "rule-context-pack/v1"

DEFAULT_FORBIDDEN_ACTIONS = [
    "cad_write",
    "dwg_save",
    "delete_entities",
    "modify_formal_layers",
    "table_c_claim",
]
DEFAULT_CONTEXT_BUDGET = {
    "maxRuleRefs": 12,
    "maxDigestItems": 16,
    "maxUpstreamOutputs": 6,
}
DERIVED_DISPLAY_SOURCES = {
    "capability-map-data.js",
    "capability-map.html",
    "output/**/sync_report.json",
    "output/**/retention_report.json",
}


@dataclass(frozen=True)
class RuleSource:
    layer: str
    priority: int
    path: str
    anchor: str
    digest: str
    keywords: tuple[str, ...]
    critical: bool = False

    @property
    def source_ref(self) -> str:
        return f"{self.path}#{self.anchor}" if self.anchor else self.path


RULE_SOURCES = [
    RuleSource(
        layer="L0",
        priority=0,
        path="AGENTS.md",
        anchor="强制绘图准确性门槛",
        digest="模型只能只读判断，不能执行 CAD、保存 DWG、删除实体、改正式图层或替代 readback。",
        keywords=("cad", "cad_plan", "模型", "readback", "保存", "删除", "安全", "closeout"),
        critical=True,
    ),
    RuleSource(
        layer="L0",
        priority=1,
        path="docs/governance/cad-agent-rules.md",
        anchor="证据边界",
        digest="截图只作视觉辅助，不能替代 created handles、bbox、layer、sourceSpec、reuse replay 或用户验收。",
        keywords=("截图", "证据", "readback", "sourceSpec", "reuse", "验收"),
        critical=True,
    ),
    RuleSource(
        layer="L1",
        priority=2,
        path="CORE_CONTEXT_BRIEF.md",
        anchor="当前一口径",
        digest="当前仓库事实以 run package、trace、registry、coverage JSON 和训练事实源为准，派生快照不能反向证明能力。",
        keywords=("当前", "表 c", "trace", "capability", "derived", "工作台"),
    ),
    RuleSource(
        layer="L1",
        priority=3,
        path="CORE_RESTRUCTURE_PLAN.md",
        anchor="模型型 Agent 路由",
        digest="主 PlanMD 只保留路由入口和优先级；专项计划细节不能形成第二套 next。",
        keywords=("model", "agent", "plan", "priority", "next", "模型"),
    ),
    RuleSource(
        layer="L2",
        priority=4,
        path="docs/architecture/cad-agent-task-chain.md",
        anchor="系统任务链路",
        digest="自然语言不能直接跳到真实 CAD，必须先形成 CAD_PLAN 或结构化意图，并经过 validate、dry-run 和证据门禁。",
        keywords=("cad_plan", "任务链路", "自然语言", "validate", "dry-run", "intent", "dispatch"),
    ),
    RuleSource(
        layer="L2",
        priority=5,
        path="agents/pipeline/README.md",
        anchor="模型调用触发策略",
        digest="模型型 Agent 负责设计判断、拆解、复审和交付边界；确定性 safety gate 与 CAD readback 继续走规则层。",
        keywords=("设计", "模型", "trigger", "agent", "review", "dispatch", "readback"),
    ),
    RuleSource(
        layer="L3",
        priority=6,
        path="agents/pipeline/pipeline_manifest.json",
        anchor="model_bridge_expansion",
        digest="只有 manifest 已登记的 Agent 可进入 requiredAgents；未登记 Agent 只能作为 reviewed package / OpenSpec 候选。",
        keywords=("manifest", "agent", "required", "model_bridge", "未登记"),
    ),
    RuleSource(
        layer="L3",
        priority=7,
        path="core/model_review/prompt_packs/manifest.json",
        anchor="prompt packs",
        digest="Prompt Pack 必须绑定 registered Agent、schema、boundary rules、negative examples 和 converter。",
        keywords=("prompt", "schema", "pack", "model", "converter"),
    ),
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError:
        return ""


def _normalize_budget(context_budget: dict[str, Any] | None) -> dict[str, int]:
    merged = dict(DEFAULT_CONTEXT_BUDGET)
    if isinstance(context_budget, dict):
        for key in DEFAULT_CONTEXT_BUDGET:
            try:
                merged[key] = max(0, int(context_budget.get(key, merged[key])))
            except (TypeError, ValueError):
                merged[key] = DEFAULT_CONTEXT_BUDGET[key]
    return {key: int(value) for key, value in merged.items()}


def _query_terms(*values: Any) -> list[str]:
    terms: list[str] = []
    for value in values:
        if isinstance(value, list):
            terms.extend(_query_terms(*value))
        elif isinstance(value, tuple):
            terms.extend(_query_terms(*list(value)))
        elif value is not None:
            for token in str(value).replace("_", " ").replace("-", " ").split():
                lowered = token.casefold().strip()
                if lowered and lowered not in terms:
                    terms.append(lowered)
    return terms


def _matches(source: RuleSource, text: str, terms: list[str]) -> tuple[bool, list[str]]:
    if source.critical:
        return True, ["critical"]
    haystack = f"{source.path} {source.anchor} {source.digest} {text}".casefold()
    source_terms = [keyword.casefold() for keyword in source.keywords]
    matched = [term for term in terms if term in haystack or term in source_terms]
    return bool(matched), matched[:8]


def _source_hit(root: Path, source: RuleSource, terms: list[str]) -> dict[str, Any] | None:
    path = root / source.path
    if not path.is_file():
        return None
    text = _read_text(path)
    matched, matched_terms = _matches(source, text, terms)
    if not matched:
        return None
    return {
        "layer": source.layer,
        "priority": source.priority,
        "sourceRef": source.source_ref,
        "digest": source.digest,
        "matchedQueries": matched_terms,
        "critical": source.critical,
        "missing": False,
    }


def _budget_hits(hits: list[dict[str, Any]], budget: dict[str, int]) -> list[dict[str, Any]]:
    max_refs = budget["maxRuleRefs"]
    if max_refs <= 0:
        return [hit for hit in hits if hit.get("critical")]
    critical = [hit for hit in hits if hit.get("critical")]
    noncritical = [hit for hit in hits if not hit.get("critical")]
    allowed = max(max_refs, len(critical))
    return [*critical, *noncritical[: max(0, allowed - len(critical))]]


def _project_rel(root: Path, path: str | Path) -> str:
    value = Path(path)
    if not value.is_absolute():
        return str(value).replace("\\", "/")
    try:
        return str(value.resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        return str(value).replace("\\", "/")


def _schema_missing(root: Path, schemas: list[str]) -> list[str]:
    missing: list[str] = []
    for schema in schemas:
        path = root / schema
        if not path.is_file():
            missing.append(f"schema missing: {schema}")
    return missing


def _compact_upstream_outputs(upstream_outputs: list[dict[str, Any]], budget: dict[str, int]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in upstream_outputs[: budget["maxUpstreamOutputs"]]:
        if not isinstance(item, dict):
            continue
        result.append(
            {
                "agentId": str(item.get("agentId") or ""),
                "path": str(item.get("path") or ""),
                "status": str(item.get("status") or ""),
                "summary": str(item.get("summary") or "")[:300],
                "sha256": str(item.get("sha256") or ""),
            }
        )
    return result


def build_rule_context_pack(
    *,
    root: str | Path = PROJECT_ROOT,
    run_id: str,
    agent_id: str,
    task_kind: str,
    request_mode: str = "ordinary_execution",
    trigger_signals: list[str] | None = None,
    retrieval_queries: list[str] | None = None,
    schemas: list[str] | None = None,
    hard_gates: list[str] | None = None,
    forbidden_actions: list[str] | None = None,
    evidence_bundle: dict[str, Any] | None = None,
    upstream_outputs: list[dict[str, Any]] | None = None,
    context_budget: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a compact local rule-context pack for one model-backed Agent call."""

    repo_root = Path(root)
    budget = _normalize_budget(context_budget)
    signals = [str(item) for item in trigger_signals or []]
    queries = [str(item) for item in retrieval_queries or []]
    schema_refs = [_project_rel(repo_root, item) for item in schemas or []]
    gate_refs = [str(item) for item in hard_gates or []]
    forbidden = [*DEFAULT_FORBIDDEN_ACTIONS, *[str(item) for item in forbidden_actions or []]]
    forbidden = list(dict.fromkeys(item for item in forbidden if item))
    terms = _query_terms(agent_id, task_kind, request_mode, signals, queries, schema_refs, gate_refs, forbidden)

    all_hits = [_source_hit(repo_root, source, terms) for source in RULE_SOURCES]
    hits = sorted([hit for hit in all_hits if hit is not None], key=lambda item: int(item["priority"]))
    hits = _budget_hits(hits, budget)
    l0_found = any(hit.get("layer") == "L0" for hit in hits)

    missing_context: list[str] = []
    if not l0_found:
        missing_context.append("L0 safety rules missing")
    missing_context.extend(_schema_missing(repo_root, schema_refs))

    digest_limit = max(budget["maxDigestItems"], len([hit for hit in hits if hit.get("critical")]))
    rule_digest = [str(hit["digest"]) for hit in hits[:digest_limit]]
    if not any("模型只能只读判断" in item for item in rule_digest):
        for hit in hits:
            if "模型只能只读判断" in str(hit.get("digest")):
                rule_digest.insert(0, str(hit["digest"]))
                break

    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "blocked" if missing_context else "ready",
        "runId": run_id,
        "agentId": agent_id,
        "taskKind": task_kind,
        "requestMode": request_mode,
        "triggerSignals": signals,
        "sourceRefs": [str(hit["sourceRef"]) for hit in hits],
        "ruleDigest": rule_digest[:digest_limit],
        "retrievalQueries": queries,
        "retrievalHits": hits,
        "schemas": schema_refs,
        "hardGates": gate_refs,
        "forbiddenActions": forbidden,
        "evidenceBundle": evidence_bundle or {"cadPlan": None, "readback": None, "screenshot": None},
        "upstreamOutputs": _compact_upstream_outputs(upstream_outputs or [], budget),
        "contextBudget": {
            **budget,
            "criticalL0Preserved": l0_found,
            "derivedSourcesExcluded": sorted(DERIVED_DISPLAY_SOURCES),
        },
        "conflicts": [],
        "missingContext": missing_context,
        "generatedAt": _utc_now(),
        "writer": "core.orchestrator.rule_context_pack",
    }
