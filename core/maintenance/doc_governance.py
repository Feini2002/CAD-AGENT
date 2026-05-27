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


def _is_active_table_c_doc(rel_path: str) -> bool:
    parts = Path(rel_path).parts
    if any(part in HISTORY_PARTS for part in parts):
        return False
    if rel_path in ACTIVE_TABLE_C_ROOT_FILES:
        return True
    return rel_path.startswith(("docs/status/", "docs/onboarding/", "docs/planning/任务清单.md"))


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
        values.extend(_numbers_from_text(line))
    return values


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
    reports = {
        "doc_registry": registry,
        "source_of_truth": source,
        "table_c": table_c,
        "handoff": handoff,
        "links": links,
    }
    finding_count = sum(report["summary"].get("finding_count", 0) for report in reports.values())
    return {
        "status": "pass" if finding_count == 0 else "findings",
        "root": str(root),
        "summary": {"finding_count": finding_count},
        **reports,
    }
