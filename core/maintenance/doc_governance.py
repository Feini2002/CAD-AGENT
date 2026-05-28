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
    "CAD_AGENT_STATUS.md",
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

ROOT_MIGRATION_STUB_TARGETS = {
    "CAD_AGENT_AUTONOMOUS_VALIDATION.md": "docs/runbooks/cad-validation.md",
    "CAD_AGENT_BLOCKER_PLAYBOOK.md": "docs/runbooks/blocker-playbook.md",
    "CAD_AGENT_CHANGELOG.md": "docs/status/changelog.md",
    "CAD_AGENT_ISSUES.md": "docs/status/issues.md",
    "CAD_AGENT_RULES.md": "docs/governance/cad-agent-rules.md",
    "CAD_AGENT_STATUS.md": "docs/status/current.md",
    "CORE_ROADMAP.md": "docs/roadmap/current.md",
    "SYMBOL_CORE_01_CAD_SYMBOL_GRAMMAR.md": "docs/architecture/symbol-grammar.md",
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
    "CORE_CONTEXT_BRIEF.md": ("Visual-First", "visual_parts"),
    "CORE_RESTRUCTURE_PLAN.md": ("Visual-First", "visual_parts"),
    "docs/training/README.md": ("pipeline_visual_intent", "visual_parts", "reference_match"),
    "docs/planning/任务清单.md": ("Visual-First", "visual_parts"),
}


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _is_ignored_path(path: Path, root: Path, *, include_output: bool) -> bool:
    parts = path.relative_to(root).parts
    ignored = IGNORED_MARKDOWN_DIRS if not include_output else IGNORED_MARKDOWN_DIRS - {"output"}
    return any(part in ignored for part in parts)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


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

        if rel_path in {"CAD_AGENT_STATUS.md", "docs/status/current.md"}:
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


def check_root_migration_stubs(root: Path) -> dict[str, Any]:
    root = root.resolve()
    findings: list[dict[str, str]] = []
    checked_stub_count = 0
    for rel_path, target in sorted(ROOT_MIGRATION_STUB_TARGETS.items()):
        stub_path = root / rel_path
        if not stub_path.is_file():
            findings.append(
                _finding(
                    "missing_root_migration_stub",
                    rel_path,
                    "Expected root compatibility stub is missing after DOC-ARCH migration.",
                )
            )
            continue
        checked_stub_count += 1
        target_path = root / target
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
        "summary": {"checked_stub_count": checked_stub_count, "finding_count": len(findings)},
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
    active_doc_size = check_active_doc_size_budgets(root)
    training_context = check_training_context_alignment(root)
    reports = {
        "doc_registry": registry,
        "source_of_truth": source,
        "table_c": table_c,
        "handoff": handoff,
        "links": links,
        "root_stubs": stubs,
        "active_doc_size": active_doc_size,
        "training_context": training_context,
    }
    finding_count = sum(report["summary"].get("finding_count", 0) for report in reports.values())
    return {
        "status": "pass" if finding_count == 0 else "findings",
        "root": str(root),
        "summary": {"finding_count": finding_count},
        **reports,
    }
