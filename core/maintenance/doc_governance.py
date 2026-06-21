"""Markdown governance checks for CAD Agent documentation architecture."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from core.maintenance.doc_handoff_governance import check_handoff_document, check_handoff_files


IGNORED_MARKDOWN_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "output",
    "venv",
}

HISTORY_PARTS = {"archive", "history", "snapshots", "completed-plans"}
ACTIVE_TABLE_C_ROOT_FILES = {
    "AGENTS.md",
    "CORE_CONTEXT_BRIEF.md",
    "CORE_STATUS.md",
    "README.md",
}

ACTIVE_TABLE_C_EXCLUDED = {
    "docs/status/changelog.md",
}

ACTIVE_DOC_LINE_BUDGETS = {
    "README.md": 140,
    "AGENTS.md": 220,
    "CORE_CONTEXT_BRIEF.md": 120,
    "CORE_RESTRUCTURE_PLAN.md": 140,
    "CORE_STATUS.md": 180,
    "docs/planning/任务清单.md": 140,
    "docs/status/current.md": 160,
    "docs/handoffs/current.md": 140,
    "docs/handoffs/package-index.md": 140,
}

IMMORTAL_DOC_LINE_BASELINES = {
    "README.md": 140,
    "AGENTS.md": 220,
    "CORE_CONTEXT_BRIEF.md": 120,
    "CORE_RESTRUCTURE_PLAN.md": 140,
    "CORE_STATUS.md": 180,
    "docs/governance/cad-agent-rules.md": 260,
}

IMMORTAL_DOC_ACTIVE_IGNORED_PARTS = {
    ".git",
    ".codegraph",
    ".codex",
    ".agents",
    ".pytest_cache",
    "__pycache__",
    "archive",
    "history",
    "node_modules",
    "output",
}

IMMORTAL_FACT_SCAN_DOCS = {
    "AGENTS.md",
    "CORE_CONTEXT_BRIEF.md",
    "CORE_RESTRUCTURE_PLAN.md",
    "CORE_STATUS.md",
    "README.md",
    "docs/architecture/system-architecture-convergence.md",
    "docs/governance/arch-doc-governance-boundary-package.md",
    "docs/governance/cad-agent-rules.md",
    "docs/handoffs/current.md",
    "docs/handoffs/package-index.md",
    "docs/planning/任务清单.md",
    "docs/status/current.md",
    "docs/status/issues.md",
}

PERMANENT_ROOT_MARKDOWN = {
    "AGENTS.md",
    "CORE_CONTEXT_BRIEF.md",
    "CORE_RESTRUCTURE_PLAN.md",
    "CORE_STATUS.md",
    "MODEL_DATA_EXPORT_AUTHORIZATION.md",
    "README.md",
}

FACT_OR_CHANGE_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+){1,}-[0-9]{2,}\b")
ROOT_SIDECAR_EXIT_MARKERS = (
    "archive",
    "closeout",
    "deprecate",
    "exit path",
    "move to",
    "superseded by",
    "退出路径",
    "归档",
    "收口",
    "完成后",
)
MAX_DUPLICATE_ID_FINDINGS = 20
BRIEF_ACTIVE_FACT_RE = re.compile(r"(?m)^-\s+\*\*([^*]+)\*\*")
COMPLETED_FACT_MARKERS = ("completed", "done", "已完成", "收口", "归档")
MERGE_ACTION_REQUIRED_FIELDS = (
    "factId",
    "authoritySource",
    "add",
    "replace",
    "demote",
    "reference",
    "touchedFiles",
    "skippedFiles",
    "evidence",
)

ROOT_MIGRATION_STUB_TARGETS = {
    "CAD卡壳排障入口.md": "docs/runbooks/blocker-playbook.md",
    "CAD符号语法入口.md": "docs/architecture/symbol-grammar.md",
    "CAD自动验证入口.md": "docs/runbooks/cad-validation.md",
    "变更记录入口.md": "docs/status/changelog.md",
    "路线图入口.md": "docs/roadmap/current.md",
    "视觉优先训练计划入口.md": "docs/training/visual-first-agent-plan.md",
    "训练错误记录入口.md": "docs/training/training-errors.md",
    "问题风险入口.md": "docs/status/issues.md",
    "长期规则入口.md": "docs/governance/cad-agent-rules.md",
    "当前状态入口.md": "docs/status/current.md",
}

HISTORICAL_TABLE_C_LINE_MARKERS = (
    "历史",
    "快照",
    "当时",
    "该条",
    "该轮",
    "仍为",
    "仍 **",
    "提升到",
    "升至",
    "→",
    "保持",
    "复跑后",
    "coverage 复跑",
    "因此前",
    "此前",
    "当时为",
    "记录 coverage",
    "主指标仍",
    "主指标 8.",
    "主指标 **8.",
)

TRAINING_CONTEXT_REQUIREMENTS = {
    "docs/training/README.md": ("pipeline_visual_intent", "visual_parts", "reference_match"),
}

OUTPUT_REPLY_POLICY_FORBIDDEN = (
    "聊天交付默认用 `AGENTS.md` 的 **1 张精简进度表**",
    "默认 1 张精简进度表",
    "每次 CAD Agent 相关交付，最终回复必须带",
    "后续每次 CAD Agent 相关改动后，都要大概估算并汇报",
    "完成或更新能力证明、代码轨、CAD 补验包，并改变",
    "完成或更新能力证明 / 代码轨 / CAD 补验包，并改变",
)

OUTPUT_REPLY_POLICY_EXCLUDED = {
    "docs/status/changelog.md",
}

OPENSPEC_MASTER_PLAN_SUBJECT_MARKERS = (
    "本文",
    "本文件",
    "本变更",
    "该变更",
    "this change",
    "this document",
    "this openspec change",
)

OPENSPEC_MASTER_PLAN_AUTHORITY_MARKERS = (
    "唯一 planmd",
    "only planmd",
    "master roadmap",
    "master plan",
    "主计划",
    "全局 backlog",
    "global backlog",
    "唯一主线",
    "only master",
)

OPENSPEC_NEGATION_MARKERS = (
    "不承载",
    "不得",
    "不应",
    "不能",
    "不替代",
    "不要",
    "防止",
    "not ",
    "must not",
    "shall not",
    "does not",
    "do not",
    "cannot",
    "rejected",
)

OPENSPEC_TASK_BACKLOG_MARKERS = (
    "全局 next",
    "总 next",
    "全局 backlog",
    "总 backlog",
    "剩余开发包队列",
    "remaining package queue",
    "global backlog",
    "global next",
)

OPENSPEC_METADATA_REQUIRED_STATUSES = {
    "proposed",
    "active",
    "implemented",
    "complete",
    "archive-ready",
    "archived",
    "superseded",
}

OPENSPEC_METADATA_RELATION_KEYS = ("dependsOn", "blockedBy", "supersedes")

OPENSPEC_OPEN_QUESTION_OPEN_STATUSES = {"open", ""}

TABLE_C_SUBJECT_MARKERS = (
    "表 C",
    "旧表 C",
    "真实 CAD 实力",
    "cad_strength_headline_percent",
    "cad_strength_index_percent",
)

TABLE_C_END_TO_END_CLAIM_MARKERS = (
    "端到端",
    "真实项目",
    "项目交付",
    "交付准备",
    "可交付",
    "已经具备",
    "已具备",
    "能画准",
    "施工图能力",
    "完整施工图",
    "白话已训通",
    "真实任务能力",
    "Agent Task Maturity",
    "Project Delivery Readiness",
)

TABLE_C_BOUNDARY_NEGATION_MARKERS = (
    "不代表",
    "不再代表",
    "不再表示",
    "不证明",
    "不能",
    "不得",
    "不是",
    "不等于",
    "不可",
    "不提升",
    "不计入",
    "不替代",
    "≠",
    "只表示",
    "只说明",
    "仅表示",
    "仅说明",
    "另看",
    "区分",
    "拆成",
    "误以为",
    "高估",
    "误导",
    "not ",
    "does not",
    "cannot",
    "must not",
    "shall not",
)

ARCHITECTURE_REQUEST_CHAIN_LEGACY = (
    "User Request -> semantic route -> A-to-A contract -> CAD_PLAN / asset workflow / training route -> "
    "execution -> verification -> promotion/sync"
)

ARCHITECTURE_HARDENING_REQUIREMENTS = {
    "docs/architecture/README.md": (
        "request context / run package",
        "Orchestrator Host / A-to-A contract",
        "required agents + hard gates",
        "verification / closeout",
        "Reviewer Host / delivery claims",
        "UTF-8 preflight",
        "CAD_PLAN validate/dry-run",
        "CODEX_PREVIEW/no-save",
        "A-to-A hard gate",
        "model trace chain",
        "asset source boundary",
        "reuse readback",
        "training promotion gate",
        "workbench sync",
    ),
    "docs/architecture/current-module-boundaries.md": (
        ARCHITECTURE_REQUEST_CHAIN_LEGACY,
        "core/orchestrator/",
        "core/assets/",
        "core/training/",
        "core/verification/",
        "agents/pipeline/",
        "agents/<scenario>/",
        "must not draw CAD details",
        "must not duplicate Core algorithms",
    ),
}

DATA_BLOAT_GOVERNANCE_TASK_KINDS = {
    "training_closeout",
    "focused_training_closeout",
    "training_queue_completion",
    "formal_training_workbench_sync",
    "system_asset_sedimentation",
    "asset_dwg_layout",
    "repository_artifact_governance",
    "training_data_bloat_governance",
}

DATA_BLOAT_GOVERNANCE_BLOCKS = {
    "training_closeout_complete_claim",
    "workbench_sync_complete_claim",
    "formal_workbench_sync_complete_claim",
    "a_to_a_complete_claim",
    "system_asset_sedimentation_complete_claim",
    "asset_governance_complete_claim",
    "asset_dwg_layout_complete_claim",
    "repository_artifact_governance_complete_claim",
    "artifact_cleanup_write",
    "delivery_complete_claim",
}

DATA_BLOAT_GOVERNANCE_ARTIFACTS = {
    "data_bloat_audit",
    "retention_report",
    "evidence_closure_summary",
}

DATA_BLOAT_FLOW_AGENTS = {
    "pipeline_context_curator",
    "pipeline_audit",
    "pipeline_learning_promoter",
    "pipeline_delivery",
}


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _is_ignored_path(path: Path, root: Path, *, include_output: bool) -> bool:
    parts = path.relative_to(root).parts
    ignored = IGNORED_MARKDOWN_DIRS if not include_output else IGNORED_MARKDOWN_DIRS - {"output"}
    return any(part in ignored for part in parts)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _line_claims_openspec_master_plan(line: str) -> bool:
    lowered = line.lower()
    if any(marker in lowered for marker in OPENSPEC_NEGATION_MARKERS):
        return False
    has_subject = any(marker in lowered for marker in OPENSPEC_MASTER_PLAN_SUBJECT_MARKERS)
    has_authority = any(marker in lowered for marker in OPENSPEC_MASTER_PLAN_AUTHORITY_MARKERS)
    return has_subject and has_authority


def _line_claims_openspec_global_backlog(line: str) -> bool:
    lowered = line.lower()
    if any(marker in lowered for marker in OPENSPEC_NEGATION_MARKERS):
        return False
    return any(marker in lowered for marker in OPENSPEC_TASK_BACKLOG_MARKERS)


def _line_claims_table_c_end_to_end(line: str) -> bool:
    lowered = line.lower()
    if not any(marker.lower() in lowered for marker in TABLE_C_SUBJECT_MARKERS):
        return False
    if not any(marker.lower() in lowered for marker in TABLE_C_END_TO_END_CLAIM_MARKERS):
        return False
    return not any(marker.lower() in lowered for marker in TABLE_C_BOUNDARY_NEGATION_MARKERS)


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def classify_markdown_document(path: str) -> str:
    normalized = path.replace("\\", "/")
    parts = normalized.split("/")
    name = parts[-1]
    if normalized in {"README.md", "AGENTS.md", "CORE_CONTEXT_BRIEF.md", "CORE_RESTRUCTURE_PLAN.md"}:
        return "root_control"
    if normalized == "CORE_STATUS.md" or normalized.startswith("docs/status/"):
        return "status"
    if "history" in parts or "archive" in parts:
        return "history"
    if normalized.startswith("docs/handoffs/"):
        return "handoff"
    if normalized.startswith("docs/verification/"):
        return "verification"
    if normalized.startswith("docs/planning/"):
        return "planning"
    if normalized.startswith("docs/governance/"):
        return "governance"
    if normalized.startswith("docs/runbooks/"):
        return "runbook"
    if normalized.startswith("docs/architecture/"):
        return "architecture"
    if name == "README.md":
        return "directory_index"
    return "other"


def build_doc_registry(root: Path, *, include_output: bool = False) -> dict[str, Any]:
    root = root.resolve()
    documents: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.md")):
        if _is_ignored_path(path, root, include_output=include_output):
            continue
        text = _read_text(path)
        rel_path = _rel(path, root)
        documents.append(
            {
                "path": rel_path,
                "title": _first_heading(text),
                "category": classify_markdown_document(rel_path),
                "line_count": len(text.splitlines()),
                "source_of_truth": rel_path
                in {
                    "AGENTS.md",
                    "CORE_CONTEXT_BRIEF.md",
                    "CORE_RESTRUCTURE_PLAN.md",
                    "CORE_STATUS.md",
                    "docs/planning/任务清单.md",
                    "docs/status/current.md",
                    "docs/status/changelog.md",
                    "docs/status/issues.md",
                },
            }
        )

    by_category: dict[str, int] = {}
    for row in documents:
        category = row["category"]
        by_category[category] = by_category.get(category, 0) + 1

    return {
        "status": "pass",
        "root": str(root),
        "summary": {
            "document_count": len(documents),
            "total_lines": sum(row["line_count"] for row in documents),
        },
        "by_category": dict(sorted(by_category.items())),
        "documents": documents,
    }


def _finding(code: str, path: str, message: str, *, severity: str = "medium") -> dict[str, str]:
    return {"code": code, "severity": severity, "path": path, "message": message}


def _parse_openspec_scalar(value: str) -> Any:
    text = value.strip()
    if not text:
        return ""
    if text in {"[]", "{}", "null", "Null", "NULL"}:
        return [] if text == "[]" else None
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return text[1:-1]
    if re.fullmatch(r"-?\d+", text):
        try:
            return int(text)
        except ValueError:
            return text
    return text


def _parse_openspec_change_ref(value: str) -> str:
    text = str(_parse_openspec_scalar(value)).strip()
    if text.startswith("change:"):
        return text.split(":", 1)[1].strip()
    return text


def _parse_openspec_metadata(text: str) -> dict[str, Any]:
    """Parse the constrained .openspec.yaml subset used by this repository."""

    data: dict[str, Any] = {
        "top": {},
        "lifecycle": {},
        "dependencies": {key: [] for key in OPENSPEC_METADATA_RELATION_KEYS},
        "openQuestions": [],
    }
    section = ""
    current_relation_key = ""
    current_question: dict[str, Any] | None = None

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent == 0:
            current_relation_key = ""
            current_question = None
            if ":" not in stripped:
                continue
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                data["top"][key] = _parse_openspec_scalar(value)
                section = key if key in {"lifecycle", "dependencies", "openQuestions"} else ""
                if key == "openQuestions" and data["top"][key] == []:
                    data["openQuestions"] = []
            else:
                section = key
            continue

        if section == "lifecycle" and indent >= 2 and ":" in stripped:
            key, value = stripped.split(":", 1)
            data["lifecycle"][key.strip()] = _parse_openspec_scalar(value)
            continue

        if section == "dependencies":
            if indent == 2 and ":" in stripped:
                key, value = stripped.split(":", 1)
                key = key.strip()
                if key in OPENSPEC_METADATA_RELATION_KEYS:
                    current_relation_key = key
                    parsed_value = _parse_openspec_scalar(value)
                    if isinstance(parsed_value, list):
                        data["dependencies"][key] = parsed_value
                    elif parsed_value:
                        data["dependencies"][key] = [_parse_openspec_change_ref(str(parsed_value))]
                continue

            if indent >= 4 and stripped.startswith("-") and current_relation_key:
                ref = _parse_openspec_change_ref(stripped[1:].strip())
                if ref:
                    data["dependencies"][current_relation_key].append(ref)
                continue

        if section == "openQuestions":
            if indent >= 2 and stripped.startswith("-"):
                item = stripped[1:].strip()
                current_question = {}
                data["openQuestions"].append(current_question)
                if ":" in item:
                    key, value = item.split(":", 1)
                    current_question[key.strip()] = _parse_openspec_scalar(value)
                continue

            if current_question is not None and indent >= 4 and ":" in stripped:
                key, value = stripped.split(":", 1)
                current_question[key.strip()] = _parse_openspec_scalar(value)

    return data


def _openspec_tasks_all_checked(tasks_path: Path) -> bool:
    if not tasks_path.is_file():
        return False
    for line in _read_text(tasks_path).splitlines():
        stripped = line.strip()
        if stripped.startswith("- [ ]"):
            return False
    return True


def _has_openspec_dependency_cycle(graph: dict[str, list[str]]) -> list[str]:
    visited: set[str] = set()
    visiting: set[str] = set()
    stack: list[str] = []
    cycle_nodes: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            if node in stack:
                cycle_nodes.update(stack[stack.index(node) :])
            else:
                cycle_nodes.add(node)
            return
        if node in visited:
            return
        visiting.add(node)
        stack.append(node)
        for target in graph.get(node, []):
            if target in graph:
                visit(target)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for change in sorted(graph):
        visit(change)

    return sorted(cycle_nodes)


def check_doc_source_of_truth(root: Path) -> dict[str, Any]:
    root = root.resolve()
    findings: list[dict[str, str]] = []
    for path in sorted(root.rglob("*.md")):
        if _is_ignored_path(path, root, include_output=False):
            continue
        rel_path = _rel(path, root)
        rel_parts = Path(rel_path).parts
        if any(part in HISTORY_PARTS for part in rel_parts):
            continue
        text = _read_text(path)

        if rel_path in {"当前状态入口.md", "docs/status/current.md"}:
            if "## 下一步计划" in text or re.search(r"(?im)^next\s*=", text):
                findings.append(
                    _finding(
                        "status_carries_next",
                        rel_path,
                        "Status docs must point to PlanMD/task ledger instead of carrying an independent next queue.",
                    )
                )

        if rel_path.startswith("docs/planning/") and rel_path != "docs/planning/任务清单.md":
            if "后置 Backlog" in text or "剩余开发包细分索引" in text:
                findings.append(
                    _finding(
                        "planning_doc_carries_backlog",
                        rel_path,
                        "Planning helper docs must not carry an independent backlog.",
                    )
                )

        if rel_path != "CORE_RESTRUCTURE_PLAN.md" and "唯一 PlanMD" in text and "CORE_RESTRUCTURE_PLAN.md" not in text:
            findings.append(
                _finding(
                    "unclear_planmd_reference",
                    rel_path,
                    "A PlanMD claim should explicitly point to CORE_RESTRUCTURE_PLAN.md.",
                    severity="low",
                )
            )

    return {
        "status": "pass" if not findings else "findings",
        "summary": {"finding_count": len(findings)},
        "findings": findings,
    }


def check_training_context_alignment(root: Path) -> dict[str, Any]:
    root = root.resolve()
    findings: list[dict[str, str]] = []
    checked_file_count = 0

    for rel_path, required_tokens in sorted(TRAINING_CONTEXT_REQUIREMENTS.items()):
        path = root / rel_path
        if not path.is_file():
            findings.append(
                _finding(
                    "missing_training_context_doc",
                    rel_path,
                    "Expected active training context document is missing.",
                )
            )
            continue

        checked_file_count += 1
        text = _read_text(path)
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                _finding(
                    "training_context_missing_token",
                    rel_path,
                    "Active training context is missing required Visual-First token(s): "
                    + ", ".join(missing),
                )
            )

    history_readme = root / "docs" / "history" / "README.md"
    if history_readme.is_file():
        checked_file_count += 1
        if "HISTORY-ONLY" not in _read_text(history_readme):
            findings.append(
                _finding(
                    "history_readme_missing_history_only_marker",
                    "docs/history/README.md",
                    "History README must explicitly mark archived documents as HISTORY-ONLY.",
                )
            )
    else:
        findings.append(
            _finding(
                "missing_history_readme",
                "docs/history/README.md",
                "History README is required to keep archived docs out of default context.",
            )
        )

    manifest_path = root / "agents" / "pipeline" / "pipeline_manifest.json"
    if manifest_path.is_file():
        checked_file_count += 1
        try:
            manifest = json.loads(_read_text(manifest_path))
        except json.JSONDecodeError:
            findings.append(
                _finding(
                    "pipeline_manifest_invalid_json",
                    "agents/pipeline/pipeline_manifest.json",
                    "Pipeline manifest must be valid JSON for training context governance.",
                )
            )
        else:
            orchestration = manifest.get("orchestration", {}) if isinstance(manifest, dict) else {}
            default_flow = orchestration.get("default_flow", [])
            if "pipeline_visual_intent" not in default_flow:
                findings.append(
                    _finding(
                        "pipeline_visual_intent_not_in_default_flow",
                        "agents/pipeline/pipeline_manifest.json",
                        "Default flow must include pipeline_visual_intent before CAD execution.",
                    )
                )

            gate = orchestration.get("hard_gates", {}).get("reference_match", {})
            gate_requires = set(gate.get("requires", [])) if isinstance(gate, dict) else set()
            gate_blocks = set(gate.get("blocks", [])) if isinstance(gate, dict) else set()
            required_inputs = {"style_target", "visual_parts", "visual_style_brief"}
            if not required_inputs.issubset(gate_requires) or "pipeline_execute" not in gate_blocks:
                findings.append(
                    _finding(
                        "reference_match_gate_incomplete",
                        "agents/pipeline/pipeline_manifest.json",
                        "reference_match gate must require style_target, visual_parts, visual_style_brief and block pipeline_execute.",
                    )
                )
    elif (root / "agents").exists():
        findings.append(
            _finding(
                "missing_pipeline_manifest",
                "agents/pipeline/pipeline_manifest.json",
                "Pipeline manifest is required when agents/ exists.",
            )
        )

    return {
        "status": "pass" if not findings else "findings",
        "summary": {
            "checked_file_count": checked_file_count,
            "finding_count": len(findings),
        },
        "findings": findings,
    }


def check_output_reply_policy(root: Path) -> dict[str, Any]:
    root = root.resolve()
    findings: list[dict[str, str]] = []
    checked_file_count = 0

    for path in sorted(root.rglob("*.md")):
        if _is_ignored_path(path, root, include_output=False):
            continue
        rel_path = _rel(path, root)
        if rel_path in OUTPUT_REPLY_POLICY_EXCLUDED:
            continue
        if any(part in HISTORY_PARTS for part in Path(rel_path).parts):
            continue
        checked_file_count += 1
        text = _read_text(path)
        for forbidden in OUTPUT_REPLY_POLICY_FORBIDDEN:
            if forbidden in text:
                findings.append(
                    _finding(
                        "stale_output_reply_policy",
                        rel_path,
                        "Active docs must keep ordinary final replies opt-in for progress tables; stale default progress-table wording found.",
                    )
                )
                break

    return {
        "status": "pass" if not findings else "findings",
        "summary": {
            "checked_file_count": checked_file_count,
            "finding_count": len(findings),
        },
        "findings": findings,
    }


def check_openspec_contracts(root: Path) -> dict[str, Any]:
    root = root.resolve()
    openspec_dir = root / "openspec"
    findings: list[dict[str, str]] = []
    active_change_file_count = 0
    active_change_count = 0
    metadata_by_change: dict[str, dict[str, Any]] = {}
    active_change_names: set[str] = set()
    known_change_names: set[str] = set()

    if not openspec_dir.exists():
        return {
            "status": "pass",
            "summary": {
                "openspec_present": False,
                "active_change_file_count": 0,
                "active_change_count": 0,
                "finding_count": 0,
            },
            "findings": findings,
        }

    config_path = openspec_dir / "config.yaml"
    config_yml_path = openspec_dir / "config.yml"
    existing_config_path = config_path if config_path.is_file() else config_yml_path
    if not existing_config_path.is_file():
        findings.append(
            _finding(
                "openspec_config_missing",
                "openspec/config.yaml",
                "OpenSpec is initialized but no config file defines the repository contract boundary.",
            )
        )
    else:
        config_text = _read_text(existing_config_path)
        if "CORE_RESTRUCTURE_PLAN.md" not in config_text:
            findings.append(
                _finding(
                    "openspec_config_missing_planmd_boundary",
                    _rel(existing_config_path, root),
                    "OpenSpec config must preserve CORE_RESTRUCTURE_PLAN.md as the single PlanMD boundary.",
                )
            )

    root_tasks_path = openspec_dir / "tasks.md"
    if root_tasks_path.is_file():
        findings.append(
            _finding(
                "openspec_root_tasks_forbidden",
                _rel(root_tasks_path, root),
                "OpenSpec tasks must live under openspec/changes/<change>/tasks.md, not as a root-level task ledger.",
            )
        )

    changes_dir = openspec_dir / "changes"
    if changes_dir.is_dir():
        archive_dir = changes_dir / "archive"
        if archive_dir.is_dir():
            known_change_names.update(path.name for path in archive_dir.iterdir() if path.is_dir())

        for change_dir in sorted(path for path in changes_dir.iterdir() if path.is_dir()):
            if change_dir.name == "archive":
                continue
            active_change_count += 1
            active_change_names.add(change_dir.name)
            known_change_names.add(change_dir.name)

            metadata_path = change_dir / ".openspec.yaml"
            if not metadata_path.is_file():
                findings.append(
                    _finding(
                        "openspec_change_metadata_missing",
                        _rel(metadata_path, root),
                        "Active OpenSpec changes must include .openspec.yaml metadata.",
                    )
                )
            else:
                metadata = _parse_openspec_metadata(_read_text(metadata_path))
                metadata_by_change[change_dir.name] = metadata
                top = metadata.get("top", {})
                lifecycle = metadata.get("lifecycle", {})

                if "metadataVersion" not in top:
                    findings.append(
                        _finding(
                            "openspec_metadata_missing_version",
                            _rel(metadata_path, root),
                            "OpenSpec change metadata must include metadataVersion.",
                        )
                    )

                status = str(lifecycle.get("status", "")).strip()
                if not status:
                    findings.append(
                        _finding(
                            "openspec_metadata_missing_lifecycle_status",
                            _rel(metadata_path, root),
                            "OpenSpec change metadata must include lifecycle.status.",
                        )
                    )
                elif status not in OPENSPEC_METADATA_REQUIRED_STATUSES:
                    findings.append(
                        _finding(
                            "openspec_metadata_invalid_lifecycle_status",
                            _rel(metadata_path, root),
                            "OpenSpec lifecycle.status must use a known value.",
                        )
                    )

                if status in {"complete", "archive-ready"} and not _openspec_tasks_all_checked(
                    change_dir / "tasks.md"
                ):
                    findings.append(
                        _finding(
                            "openspec_complete_change_tasks_not_checked",
                            _rel(change_dir / "tasks.md", root),
                            "OpenSpec changes marked complete or archive-ready must have all tasks checked.",
                        )
                    )

                archive_ready = lifecycle.get("archiveReady")
                archive_reason = str(lifecycle.get("archiveReason", "")).strip()
                if status == "complete" and archive_ready is False and not archive_reason:
                    findings.append(
                        _finding(
                            "openspec_complete_change_missing_archive_reason",
                            _rel(metadata_path, root),
                            "Completed OpenSpec changes left outside archive with archiveReady=false must include lifecycle.archiveReason.",
                        )
                    )

                if status in {"complete", "archive-ready"}:
                    for question in metadata.get("openQuestions", []):
                        question_status = str(question.get("status", "")).strip().lower()
                        if question_status in OPENSPEC_OPEN_QUESTION_OPEN_STATUSES:
                            findings.append(
                                _finding(
                                    "openspec_complete_change_has_unresolved_open_question",
                                    _rel(metadata_path, root),
                                    "OpenSpec changes marked complete or archive-ready must not keep openQuestions with status=open.",
                                )
                            )
                            break

            for md_path in sorted(change_dir.rglob("*.md")):
                active_change_file_count += 1
                for line in _read_text(md_path).splitlines():
                    if md_path.name == "tasks.md" and _line_claims_openspec_global_backlog(line):
                        findings.append(
                            _finding(
                                "openspec_change_tasks_claims_global_backlog",
                                _rel(md_path, root),
                                "OpenSpec change tasks must stay scoped to the change; global next/backlog belongs in CORE_RESTRUCTURE_PLAN.md and docs/planning/任务清单.md.",
                            )
                        )
                        break
                    if _line_claims_openspec_master_plan(line):
                        findings.append(
                            _finding(
                                "openspec_change_claims_master_plan",
                                _rel(md_path, root),
                                "Active OpenSpec changes must not claim PlanMD, master-roadmap, or global-backlog authority.",
                            )
                        )
                        break

    dependency_graph: dict[str, list[str]] = {change: [] for change in active_change_names}
    for change_name, metadata in sorted(metadata_by_change.items()):
        metadata_path = changes_dir / change_name / ".openspec.yaml"
        dependencies = metadata.get("dependencies", {})
        lifecycle = metadata.get("lifecycle", {})

        for relation_key in ("dependsOn", "blockedBy"):
            for target in dependencies.get(relation_key, []):
                if target not in known_change_names:
                    findings.append(
                        _finding(
                            "openspec_metadata_dependency_missing",
                            _rel(metadata_path, root),
                            f"OpenSpec change references missing {relation_key} target: {target}.",
                        )
                    )
                elif relation_key == "dependsOn":
                    dependency_graph.setdefault(change_name, []).append(target)

        for target in dependencies.get("supersedes", []):
            if target not in known_change_names:
                findings.append(
                    _finding(
                        "openspec_metadata_supersedes_missing",
                        _rel(metadata_path, root),
                        f"OpenSpec change references missing supersedes target: {target}.",
                    )
                )
                continue

            dependency_graph.setdefault(change_name, []).append(target)
            target_metadata = metadata_by_change.get(target)
            target_status = (
                str(target_metadata.get("lifecycle", {}).get("status", "")).strip()
                if target_metadata
                else "archived"
            )
            if target_status not in {"archived", "superseded"}:
                findings.append(
                    _finding(
                        "openspec_metadata_supersedes_target_not_closed",
                        _rel(metadata_path, root),
                        f"OpenSpec supersedes target should be archived or superseded before closeout: {target}.",
                        severity="low",
                    )
                )

        status = str(lifecycle.get("status", "")).strip()
        if status == "superseded" and not dependencies.get("supersedes"):
            findings.append(
                _finding(
                    "openspec_superseded_change_missing_supersedes_ref",
                    _rel(metadata_path, root),
                    "OpenSpec lifecycle.status=superseded should include a supersedes reference explaining the replacement.",
                    severity="low",
                )
            )

    cycle_nodes = _has_openspec_dependency_cycle(dependency_graph)
    for change_name in cycle_nodes:
        findings.append(
            _finding(
                "openspec_metadata_dependency_cycle",
                f"openspec/changes/{change_name}/.openspec.yaml",
                "OpenSpec dependsOn / supersedes metadata must not form a cycle.",
                severity="high",
            )
        )

    return {
        "status": "pass" if not findings else "findings",
        "summary": {
            "openspec_present": True,
            "active_change_file_count": active_change_file_count,
            "active_change_count": active_change_count,
            "finding_count": len(findings),
        },
        "findings": findings,
    }


def check_architecture_hardening_index(root: Path) -> dict[str, Any]:
    root = root.resolve()
    findings: list[dict[str, str]] = []
    checked_file_count = 0

    for rel_path, required_tokens in sorted(ARCHITECTURE_HARDENING_REQUIREMENTS.items()):
        path = root / rel_path
        if not path.is_file():
            findings.append(
                _finding(
                    "architecture_hardening_missing_doc",
                    rel_path,
                    "Architecture hardening requires this active documentation entry.",
                )
            )
            continue

        checked_file_count += 1
        text = _read_text(path)
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                _finding(
                    "architecture_hardening_missing_token",
                    rel_path,
                    "Architecture hardening doc is missing required token(s): " + ", ".join(missing),
                )
            )

    return {
        "status": "pass" if not findings else "findings",
        "summary": {
            "checked_file_count": checked_file_count,
            "finding_count": len(findings),
        },
        "findings": findings,
    }


def check_data_bloat_governance_manifest(root: Path) -> dict[str, Any]:
    root = root.resolve()
    manifest_path = root / "agents" / "pipeline" / "pipeline_manifest.json"
    findings: list[dict[str, str]] = []

    if not manifest_path.is_file():
        if (root / "AGENTS.md").is_file() or (root / "agents").is_dir():
            findings.append(
                _finding(
                    "data_bloat_manifest_missing",
                    "agents/pipeline/pipeline_manifest.json",
                    "Data-bloat governance requires the pipeline manifest to bind task kinds to hard gates.",
                )
            )
        return {
            "status": "pass" if not findings else "findings",
            "summary": {
                "manifest_present": False,
                "checked_task_kind_count": 0,
                "finding_count": len(findings),
            },
            "findings": findings,
        }

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "status": "findings",
            "summary": {
                "manifest_present": True,
                "checked_task_kind_count": 0,
                "finding_count": 1,
            },
            "findings": [
                _finding(
                    "data_bloat_manifest_invalid_json",
                    _rel(manifest_path, root),
                    f"Pipeline manifest is not valid JSON: {exc}",
                )
            ],
        }

    orchestration = manifest.get("orchestration", {})
    high_risk = set(orchestration.get("dynamic_dispatch_policy", {}).get("high_risk_task_kinds", []))
    low_risk = set(orchestration.get("dynamic_dispatch_policy", {}).get("low_risk_task_kinds", []))
    required_gates = orchestration.get("required_hard_gates_by_task_kind", {})
    hard_gates = orchestration.get("hard_gates", {})
    data_bloat_gate = hard_gates.get("data_bloat_governance", {})
    flow_variants = orchestration.get("flow_variants", {})
    artifacts = manifest.get("artifacts", {})

    if "training_workbench_sync" in high_risk or "training_workbench_sync" in required_gates:
        findings.append(
            _finding(
                "data_bloat_ambiguous_workbench_sync",
                _rel(manifest_path, root),
                "Use formal_training_workbench_sync for hard-gated closeout; plain workbench refresh must stay lightweight.",
            )
        )
    if "workbench_snapshot_refresh" not in low_risk:
        findings.append(
            _finding(
                "data_bloat_missing_workbench_refresh_exemption",
                _rel(manifest_path, root),
                "Manifest must keep workbench_snapshot_refresh as a low-risk viewing refresh so daily opening is not over-gated.",
            )
        )

    for task_kind in sorted(DATA_BLOAT_GOVERNANCE_TASK_KINDS):
        if task_kind not in high_risk:
            findings.append(
                _finding(
                    "data_bloat_task_kind_not_high_risk",
                    _rel(manifest_path, root),
                    f"{task_kind} must be listed as a high-risk task kind.",
                )
            )
        gates = set(required_gates.get(task_kind, []))
        if "data_bloat_governance" not in gates:
            findings.append(
                _finding(
                    "data_bloat_task_kind_missing_hard_gate",
                    _rel(manifest_path, root),
                    f"{task_kind} must require the data_bloat_governance hard gate.",
                )
            )

    missing_blocks = sorted(DATA_BLOAT_GOVERNANCE_BLOCKS - set(data_bloat_gate.get("blocks", [])))
    if missing_blocks:
        findings.append(
            _finding(
                "data_bloat_gate_missing_blocks",
                _rel(manifest_path, root),
                "data_bloat_governance must block completion claims: " + ", ".join(missing_blocks),
            )
        )

    missing_artifacts = sorted(DATA_BLOAT_GOVERNANCE_ARTIFACTS - set(artifacts))
    if missing_artifacts:
        findings.append(
            _finding(
                "data_bloat_missing_artifact_templates",
                _rel(manifest_path, root),
                "Manifest must declare data-bloat report artifact templates: " + ", ".join(missing_artifacts),
            )
        )

    missing_flow_agents = sorted(
        DATA_BLOAT_FLOW_AGENTS - set(flow_variants.get("training_data_bloat_governance", []))
    )
    if missing_flow_agents:
        findings.append(
            _finding(
                "data_bloat_flow_missing_agents",
                _rel(manifest_path, root),
                "training_data_bloat_governance flow must include: " + ", ".join(missing_flow_agents),
            )
        )

    readme_path = root / "agents" / "pipeline" / "README.md"
    if readme_path.is_file():
        readme_text = _read_text(readme_path)
        missing_readme_agents = sorted(
            agent.get("agent_id", "")
            for agent in manifest.get("agents", [])
            if agent.get("agent_id") and agent.get("agent_id") not in readme_text
        )
        if missing_readme_agents:
            findings.append(
                _finding(
                    "data_bloat_pipeline_readme_missing_agents",
                    _rel(readme_path, root),
                    "Pipeline README must list every manifest agent: " + ", ".join(missing_readme_agents),
                )
            )
    else:
        findings.append(
            _finding(
                "data_bloat_pipeline_readme_missing",
                "agents/pipeline/README.md",
                "Pipeline README must document manifest agents and data-bloat governance responsibilities.",
            )
        )

    return {
        "status": "pass" if not findings else "findings",
        "summary": {
            "manifest_present": True,
            "checked_task_kind_count": len(DATA_BLOAT_GOVERNANCE_TASK_KINDS),
            "finding_count": len(findings),
        },
        "findings": findings,
    }


def _is_active_table_c_doc(rel_path: str) -> bool:
    if rel_path in ACTIVE_TABLE_C_EXCLUDED:
        return False
    parts = Path(rel_path).parts
    if any(part in HISTORY_PARTS for part in parts):
        return False
    if rel_path in ACTIVE_TABLE_C_ROOT_FILES:
        return True
    return rel_path.startswith(("docs/status/", "docs/onboarding/", "docs/planning/任务清单.md"))


def _is_historical_table_c_line(line: str) -> bool:
    return any(marker in line for marker in HISTORICAL_TABLE_C_LINE_MARKERS)


def _load_coverage_values(coverage_path: Path) -> dict[str, Any]:
    data = json.loads(coverage_path.read_text(encoding="utf-8"))
    summary = data.get("summary", {})
    cad_strength = data.get("cad_strength", {})
    headline = _first_present(
        [data, summary, cad_strength],
        ("cad_strength_headline_percent",),
    )
    coverage = _first_present(
        [data, summary],
        ("cad_proof_coverage_percent", "cad_proof_coverage_rate"),
    )
    return {
        "headline": headline,
        "coverage": coverage,
        "ladder": str(
            data.get("highest_proven_ladder_level")
            or summary.get("highest_proven_ladder_level")
            or cad_strength.get("highest_proven_ladder_level")
            or data.get("highest_proven_ladder")
            or ""
        ),
    }


def _first_present(mappings: list[dict[str, Any]], keys: tuple[str, ...]) -> Any:
    for key in keys:
        for mapping in mappings:
            if isinstance(mapping, dict) and mapping.get(key) is not None:
                return mapping[key]
    return None


def _numbers_from_text(text: str) -> list[float]:
    values: list[float] = []
    for match in re.finditer(r"(?:约\s*)?(\d+(?:\.\d+)?)\s*%", text):
        values.append(float(match.group(1)))
    return values


def _table_c_numbers_from_relevant_lines(text: str) -> list[float]:
    values: list[float] = []
    for line in text.splitlines():
        if "真实 CAD 实力" not in line and "cad_strength_headline_percent" not in line:
            continue
        if _is_historical_table_c_line(line):
            continue
        if "约 xx%" in line or "约 **xx%**" in line:
            continue
        values.extend(_numbers_from_text(line))
    return values


def check_table_c_semantic_boundary(root: Path) -> dict[str, Any]:
    root = root.resolve()
    findings: list[dict[str, str]] = []
    checked_file_count = 0

    for path in sorted(root.rglob("*.md")):
        if _is_ignored_path(path, root, include_output=False):
            continue
        rel_path = _rel(path, root)
        if any(part in HISTORY_PARTS for part in Path(rel_path).parts):
            continue
        if not _is_active_table_c_doc(rel_path):
            continue
        text = _read_text(path)
        if not any(marker in text for marker in TABLE_C_SUBJECT_MARKERS):
            continue
        checked_file_count += 1
        for line_number, line in enumerate(text.splitlines(), start=1):
            if _line_claims_table_c_end_to_end(line):
                findings.append(
                    _finding(
                        "table_c_end_to_end_claim",
                        rel_path,
                        (
                            "Active docs must describe table C as Core Proof Coverage only; "
                            f"line {line_number} implies end-to-end task maturity or project delivery readiness."
                        ),
                    )
                )
                break

    return {
        "status": "pass" if not findings else "findings",
        "summary": {
            "checked_file_count": checked_file_count,
            "finding_count": len(findings),
        },
        "findings": findings,
    }


def check_root_migration_stubs(root: Path) -> dict[str, Any]:
    root = root.resolve()
    findings: list[dict[str, str]] = []
    checked_stub_count = 0
    documented_deleted_stub_count = 0
    migration_index = root / "docs" / "README.md"
    migration_index_text = _read_text(migration_index) if migration_index.is_file() else ""
    for rel_path, target in sorted(ROOT_MIGRATION_STUB_TARGETS.items()):
        stub_path = root / rel_path
        target_path = root / target
        if not stub_path.is_file():
            if rel_path in migration_index_text and target in migration_index_text and target_path.is_file():
                documented_deleted_stub_count += 1
            else:
                findings.append(
                    _finding(
                        "undocumented_root_migration_stub_deletion",
                        rel_path,
                        "Missing root compatibility stub must be documented in docs/README.md with its target.",
                    )
                )
            continue
        checked_stub_count += 1
        if not target_path.is_file():
            findings.append(
                _finding(
                    "broken_root_migration_target",
                    rel_path,
                    f"Stub target does not exist: {target}.",
                )
            )
    return {
        "status": "pass" if not findings else "findings",
        "summary": {
            "checked_stub_count": checked_stub_count,
            "documented_deleted_stub_count": documented_deleted_stub_count,
            "finding_count": len(findings),
        },
        "findings": findings,
    }


def check_active_doc_size_budgets(root: Path) -> dict[str, Any]:
    root = root.resolve()
    findings: list[dict[str, str]] = []
    checked_file_count = 0

    for rel_path, max_lines in sorted(ACTIVE_DOC_LINE_BUDGETS.items()):
        path = root / rel_path
        if not path.is_file():
            continue
        checked_file_count += 1
        line_count = len(_read_text(path).splitlines())
        if line_count > max_lines:
            findings.append(
                _finding(
                    "active_doc_over_budget",
                    rel_path,
                    f"Active document has {line_count} lines, over the finished-architecture budget of {max_lines}. Move completed details to history/archive and keep this file as a control surface.",
                )
            )

    return {
        "status": "pass" if not findings else "findings",
        "summary": {
            "checked_file_count": checked_file_count,
            "finding_count": len(findings),
        },
        "findings": findings,
    }


def _immortal_bloat_finding(
    code: str,
    path: str,
    message: str,
    *,
    severity: str = "warning",
    **extra: Any,
) -> dict[str, Any]:
    return {"code": code, "severity": severity, "path": path, "message": message, **extra}


def _is_immortal_active_markdown(path: Path, root: Path) -> bool:
    if path.suffix.lower() != ".md":
        return False
    parts = path.resolve().relative_to(root.resolve()).parts
    return not any(part in IMMORTAL_DOC_ACTIVE_IGNORED_PARTS for part in parts)


def _iter_immortal_active_markdown(root: Path) -> list[Path]:
    return [
        path
        for path in sorted(root.rglob("*.md"))
        if _is_immortal_active_markdown(path, root)
    ]


def _iter_immortal_fact_scan_markdown(root: Path) -> list[Path]:
    return [
        root / rel_path
        for rel_path in sorted(IMMORTAL_FACT_SCAN_DOCS)
        if (root / rel_path).is_file()
    ]


def _governance_rule_signals(text: str) -> set[str]:
    lowered = text.lower()
    signals: set[str] = set()
    if "cad_plan" in lowered and (
        "natural language" in lowered or "白话" in text or "直接跳到 cad" in lowered
    ):
        signals.add("cad_plan_gate")
    if "codex_preview" in lowered and ("only" in lowered or "只写" in text or "默认" in text):
        signals.add("codex_preview_write_boundary")
    if "core proof coverage" in lowered and (
        "agent task maturity" in lowered or "project delivery readiness" in lowered
    ):
        signals.add("table_c_maturity_boundary")
    if "data_bloat_governance" in lowered and ("hard gate" in lowered or "门禁" in text):
        signals.add("data_bloat_hard_gate")
    return signals


def _check_immortal_line_baselines(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for rel_path, baseline_lines in sorted(IMMORTAL_DOC_LINE_BASELINES.items()):
        path = root / rel_path
        if not path.is_file():
            continue
        line_count = len(_read_text(path).splitlines())
        rows.append(
            {
                "path": rel_path,
                "lineCount": line_count,
                "baselineLines": baseline_lines,
                "deltaLines": line_count - baseline_lines,
            }
        )
        if line_count <= baseline_lines:
            continue
        if rel_path == "CORE_CONTEXT_BRIEF.md":
            findings.append(
                _immortal_bloat_finding(
                    "core_context_brief_requires_review",
                    rel_path,
                    f"CORE_CONTEXT_BRIEF.md has {line_count} lines, over the immortal-doc baseline of {baseline_lines}; shrink it or require review before treating it as the stable short context.",
                    severity="require_review",
                    lineCount=line_count,
                    baselineLines=baseline_lines,
                )
            )
        else:
            findings.append(
                _immortal_bloat_finding(
                    "immortal_doc_over_baseline",
                    rel_path,
                    f"Immortal document has {line_count} lines, over the baseline of {baseline_lines}. Move volatile or completed detail into archive/status/history surfaces.",
                    lineCount=line_count,
                    baselineLines=baseline_lines,
                )
            )
    return rows, findings


def _check_repeated_fact_ids(root: Path) -> list[dict[str, Any]]:
    occurrences: dict[str, set[str]] = {}
    for path in _iter_immortal_fact_scan_markdown(root):
        rel_path = _rel(path, root)
        for token in set(FACT_OR_CHANGE_ID_RE.findall(_read_text(path))):
            occurrences.setdefault(token, set()).add(rel_path)

    findings: list[dict[str, Any]] = []
    for token, paths in sorted(occurrences.items()):
        if len(paths) <= 3:
            continue
        sorted_paths = sorted(paths)
        findings.append(
            _immortal_bloat_finding(
                "active_fact_id_repeated",
                sorted_paths[0],
                f"All-caps fact/change id {token} appears in {len(sorted_paths)} active documents; keep durable fact ownership narrow and move repeated narration to references.",
                factId=token,
                paths=sorted_paths,
                occurrenceDocumentCount=len(sorted_paths),
            )
        )
        if len(findings) >= MAX_DUPLICATE_ID_FINDINGS:
            break
    return findings


def _check_repeated_governance_rule_signals(root: Path) -> list[dict[str, Any]]:
    agents_path = root / "AGENTS.md"
    rules_path = root / "docs" / "governance" / "cad-agent-rules.md"
    if not agents_path.is_file() or not rules_path.is_file():
        return []

    repeated = sorted(
        _governance_rule_signals(_read_text(agents_path))
        & _governance_rule_signals(_read_text(rules_path))
    )
    return [
        _immortal_bloat_finding(
            "governance_rule_signal_repeated",
            "AGENTS.md",
            f"Governance rule signal {signal} appears in both AGENTS.md and docs/governance/cad-agent-rules.md; keep one owner and leave the other as a pointer when possible.",
            signal=signal,
            paths=["AGENTS.md", "docs/governance/cad-agent-rules.md"],
        )
        for signal in repeated
    ]


def _check_brief_active_fact_count(root: Path) -> list[dict[str, Any]]:
    path = root / "CORE_CONTEXT_BRIEF.md"
    if not path.is_file():
        return []
    text = _read_text(path)
    active_facts = BRIEF_ACTIVE_FACT_RE.findall(text)
    findings: list[dict[str, Any]] = []
    if len(active_facts) > 10:
        findings.append(
            _immortal_bloat_finding(
                "brief_active_fact_count_high",
                "CORE_CONTEXT_BRIEF.md",
                f"CORE_CONTEXT_BRIEF.md has {len(active_facts)} active fact bullets; keep only the facts needed for the next session and link to current/status/history for the rest.",
                activeFactCount=len(active_facts),
                maxRecommendedActiveFactCount=10,
            )
        )
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- **"):
            continue
        lowered = stripped.lower()
        if any(marker in lowered or marker in stripped for marker in COMPLETED_FACT_MARKERS):
            findings.append(
                _immortal_bloat_finding(
                    "completed_package_in_brief",
                    "CORE_CONTEXT_BRIEF.md",
                    "CORE_CONTEXT_BRIEF.md active facts include completed/archive wording; completed packages should usually be demoted to changelog, handoff, or history references.",
                    line=stripped[:180],
                )
            )
            break
    return findings


def _check_merge_action_templates(root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.md")):
        if path.name in PERMANENT_ROOT_MARKDOWN:
            continue
        text = _read_text(path)
        if "治理" not in text and "同步" not in text and "governance" not in text.lower():
            continue
        missing = [field for field in MERGE_ACTION_REQUIRED_FIELDS if field not in text]
        if not missing:
            continue
        findings.append(
            _immortal_bloat_finding(
                "merge_action_template_missing",
                path.name,
                "Governance sidecar mentions document sync/governance but lacks the full add/replace/demote/reference record template.",
                missingFields=missing,
            )
        )
    return findings


def _check_root_sidecar_exit_paths(root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    immortal_roots = {Path(path).name for path in IMMORTAL_DOC_LINE_BASELINES if "/" not in path}
    permanent_roots = immortal_roots | PERMANENT_ROOT_MARKDOWN
    for path in sorted(root.glob("*.md")):
        if path.name in permanent_roots:
            continue
        text = _read_text(path)
        lowered = text.lower()
        has_exit_path = any(marker in lowered or marker in text for marker in ROOT_SIDECAR_EXIT_MARKERS)
        if has_exit_path:
            continue
        findings.append(
            _immortal_bloat_finding(
                "root_sidecar_missing_exit_path",
                path.name,
                "Root sidecar Markdown file has no explicit exit/archive path. Add a closeout route or move the content under the owned docs surface.",
            )
        )
    return findings


def check_immortal_doc_bloat(root: Path) -> dict[str, Any]:
    root = root.resolve()
    baseline_rows, baseline_findings = _check_immortal_line_baselines(root)
    findings = [
        *baseline_findings,
        *_check_repeated_fact_ids(root),
        *_check_repeated_governance_rule_signals(root),
        *_check_brief_active_fact_count(root),
        *_check_merge_action_templates(root),
        *_check_root_sidecar_exit_paths(root),
    ]
    severity_counts: dict[str, int] = {}
    for finding in findings:
        severity = str(finding.get("severity", "warning"))
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    return {
        "status": "pass" if not findings else "findings",
        "summary": {
            "finding_count": len(findings),
            "baseline_doc_count": len(baseline_rows),
            "severity_counts": severity_counts,
        },
        "line_baselines": baseline_rows,
        "findings": findings,
    }


def check_table_c_values(root: Path, *, coverage_path: Path) -> dict[str, Any]:
    root = root.resolve()
    coverage = _load_coverage_values(coverage_path)
    expected_headline = coverage["headline"]
    findings: list[dict[str, str]] = []

    if expected_headline is None:
        return {
            "status": "findings",
            "summary": {"finding_count": 1},
            "findings": [
                _finding(
                    "missing_coverage_headline",
                    _rel(coverage_path.resolve(), root) if coverage_path.is_absolute() else str(coverage_path),
                    "Coverage JSON does not include cad_strength_headline_percent.",
                )
            ],
        }

    for path in sorted(root.rglob("*.md")):
        if _is_ignored_path(path, root, include_output=False):
            continue
        rel_path = _rel(path, root)
        if any(part in HISTORY_PARTS for part in Path(rel_path).parts):
            continue
        text = _read_text(path)
        if "真实 CAD 实力" not in text and "cad_strength_headline_percent" not in text:
            continue
        if not _is_active_table_c_doc(rel_path):
            if "历史" in text or "当前以 JSON 为准" in text or "以 coverage JSON 为准" in text:
                continue
            continue
        values = _table_c_numbers_from_relevant_lines(text)
        if not values:
            continue
        if all(abs(value - float(expected_headline)) > 0.05 for value in values):
            findings.append(
                _finding(
                    "stale_table_c_headline",
                    rel_path,
                    f"Active table C headline does not match coverage JSON value {expected_headline}.",
                )
            )

    return {
        "status": "pass" if not findings else "findings",
        "coverage_path": str(coverage_path),
        "summary": {"finding_count": len(findings), "expected_headline": expected_headline},
        "findings": findings,
    }


def _iter_markdown_link_targets(text: str) -> list[str]:
    targets: list[str] = []
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).strip()
        if not target:
            continue
        targets.append(target.split()[0].strip("<>"))
    return targets


def _is_external_or_anchor(target: str) -> bool:
    lowered = target.lower()
    return (
        lowered.startswith(("http://", "https://", "mailto:", "file:", "app://", "plugin://"))
        or lowered.startswith("#")
    )


def check_markdown_links(root: Path) -> dict[str, Any]:
    root = root.resolve()
    findings: list[dict[str, str]] = []
    checked_link_count = 0
    for path in sorted(root.rglob("*.md")):
        if _is_ignored_path(path, root, include_output=False):
            continue
        rel_path = _rel(path, root)
        if any(part in HISTORY_PARTS for part in Path(rel_path).parts):
            continue
        text = _read_text(path)
        for target in _iter_markdown_link_targets(text):
            if _is_external_or_anchor(target):
                continue
            checked_link_count += 1
            target_path_text = target.split("#", 1)[0]
            if not target_path_text:
                continue
            candidate = (path.parent / target_path_text).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                findings.append(
                    _finding(
                        "markdown_link_leaves_repo",
                        rel_path,
                        f"Markdown link target leaves repository: {target}.",
                    )
                )
                continue
            if not candidate.exists():
                findings.append(
                    _finding(
                        "missing_markdown_link_target",
                        rel_path,
                        f"Markdown link target does not exist: {target}.",
                    )
                )

    return {
        "status": "pass" if not findings else "findings",
        "summary": {"checked_link_count": checked_link_count, "finding_count": len(findings)},
        "findings": findings,
    }


def build_doc_governance_report(
    root: Path,
    *,
    coverage_path: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    coverage_path = coverage_path or root / "output" / "validation_runs" / "capability-lab" / "cad_capability_coverage.json"
    registry = build_doc_registry(root)
    source = check_doc_source_of_truth(root)
    table_c = (
        check_table_c_values(root, coverage_path=coverage_path)
        if coverage_path.is_file()
        else {
            "status": "findings",
            "summary": {"finding_count": 1},
            "findings": [
                _finding(
                    "missing_coverage_json",
                    _rel(coverage_path, root),
                    "Coverage JSON is required for table C stale-value checks.",
                )
            ],
        }
    )
    handoff = check_handoff_files(root)
    links = check_markdown_links(root)
    stubs = check_root_migration_stubs(root)
    table_c_semantic_boundary = check_table_c_semantic_boundary(root)
    active_doc_size = check_active_doc_size_budgets(root)
    training_context = check_training_context_alignment(root)
    output_policy = check_output_reply_policy(root)
    openspec_contracts = check_openspec_contracts(root)
    architecture_hardening = check_architecture_hardening_index(root)
    data_bloat_governance = check_data_bloat_governance_manifest(root)
    immortal_doc_bloat = check_immortal_doc_bloat(root)
    reports = {
        "doc_registry": registry,
        "source_of_truth": source,
        "table_c": table_c,
        "handoff": handoff,
        "links": links,
        "root_stubs": stubs,
        "table_c_semantic_boundary": table_c_semantic_boundary,
        "active_doc_size": active_doc_size,
        "training_context": training_context,
        "output_policy": output_policy,
        "openspec_contracts": openspec_contracts,
        "architecture_hardening": architecture_hardening,
        "data_bloat_governance": data_bloat_governance,
        "immortal_doc_bloat": immortal_doc_bloat,
    }
    finding_count = sum(report["summary"].get("finding_count", 0) for report in reports.values())
    return {
        "status": "pass" if finding_count == 0 else "findings",
        "root": str(root),
        "summary": {"finding_count": finding_count},
        **reports,
    }
