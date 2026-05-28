"""Handoff-specific governance checks for split package documentation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


REQUIRED_HANDOFF_SECTIONS = tuple(str(index) for index in range(1, 10))
CAPABILITY_EXTENSION_MARKERS = ("10.", "11.", "12.", "capability_id", "claim_level")


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _finding(code: str, path: str, message: str, *, severity: str = "medium") -> dict[str, str]:
    return {"code": code, "severity": severity, "path": path, "message": message}


def _package_lookup_key(package_name: str) -> str:
    cleaned = package_name.replace("`", "").strip()
    cleaned = re.sub(r"^\d+\.\s*", "", cleaned)
    for separator in ("：", "（", "(", " ", " / "):
        if separator in cleaned:
            return cleaned.split(separator, 1)[0].strip()
    return cleaned


def _handoff_sections(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(?m)^##\s+(.+)$", text))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match.group(1).strip(), text[start:end]))
    return sections


def check_handoff_document(text: str, *, path: str) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    checked_sections = 0
    ignored_titles = {"目录", "交接包标准模板（每包 9 项）", "当前交接说明", "Codex 校验快速指引"}
    package_markers = ("V-PROOF", "RCAD", "STRUCT", "CAD-VAL", "CAD-EVIDENCE", "LCAD", "R-", "SCENE", "REST", "OFFICE", "CORE", "RBLOCK", "DRAW", "CFIT", "VCAD")
    for title, body in _handoff_sections(text):
        if title in ignored_titles or not any(marker in title for marker in package_markers):
            continue
        checked_sections += 1
        missing = [number for number in REQUIRED_HANDOFF_SECTIONS if f"{number}." not in body]
        if missing:
            findings.append(
                _finding(
                    "handoff_missing_required_sections",
                    path,
                    f"Section {title!r} is missing handoff items: {', '.join(missing)}.",
                )
            )
        if any(marker in title for marker in ("V-PROOF", "RCAD")) and not all(
            marker in body for marker in CAPABILITY_EXTENSION_MARKERS
        ):
            findings.append(
                _finding(
                    "handoff_missing_capability_extension",
                    path,
                    f"Section {title!r} is missing capability proof extension markers.",
                )
            )

    return {
        "status": "pass" if not findings else "findings",
        "path": path,
        "summary": {"checked_section_count": checked_sections, "finding_count": len(findings)},
        "findings": findings,
    }


def check_handoff_files(root: Path) -> dict[str, Any]:
    root = root.resolve()
    candidates = [
        root / "docs" / "handoffs" / "current.md",
        root / "docs" / "handoffs" / "CURSOR_PACKAGE_HANDOFFS.md",
    ]
    reports: list[dict[str, Any]] = []
    for path in candidates:
        if path.is_file():
            reports.append(check_handoff_document(_read_text(path), path=_rel(path, root)))
    index_report = check_handoff_package_index(root)
    findings = [finding for report in reports for finding in report["findings"]]
    findings.extend(index_report["findings"])
    return {
        "status": "pass" if not findings else "findings",
        "summary": {
            "checked_file_count": len(reports),
            "checked_index_row_count": index_report["summary"]["checked_row_count"],
            "finding_count": len(findings),
        },
        "reports": reports,
        "package_index": index_report,
        "findings": findings,
    }


def check_handoff_package_index(root: Path) -> dict[str, Any]:
    root = root.resolve()
    path = root / "docs" / "handoffs" / "package-index.md"
    findings: list[dict[str, str]] = []
    checked_row_count = 0
    if not path.is_file():
        return {
            "status": "findings",
            "summary": {"checked_row_count": 0, "finding_count": 1},
            "findings": [
                _finding(
                    "missing_handoff_package_index",
                    "docs/handoffs/package-index.md",
                    "Handoff package index is required after splitting current/archive handoffs.",
                )
            ],
        }

    for line in _read_text(path).splitlines():
        if not line.startswith("|") or "---" in line or "序号" in line:
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) < 3:
            continue
        checked_row_count += 1
        package_name = columns[1]
        target = columns[2].strip("` ")
        if not target:
            findings.append(
                _finding(
                    "handoff_index_missing_target_cell",
                    _rel(path, root),
                    f"Handoff package {package_name!r} has an empty target cell.",
                )
            )
            continue
        target_path = (path.parent / target).resolve()
        try:
            target_path.relative_to(root)
        except ValueError:
            findings.append(
                _finding(
                    "handoff_index_target_leaves_repo",
                    _rel(path, root),
                    f"Handoff package {package_name!r} points outside the repository: {target}.",
                )
            )
            continue
        if not target_path.is_file():
            findings.append(
                _finding(
                    "handoff_index_missing_target",
                    _rel(path, root),
                    f"Handoff package {package_name!r} points to a missing file: {target}.",
                )
            )
            continue
        if target == "current.md":
            current_text = _read_text(target_path)
            package_key = _package_lookup_key(package_name)
            if package_key and package_key not in current_text:
                findings.append(
                    _finding(
                        "handoff_index_current_missing_package_section",
                        _rel(path, root),
                        f"Handoff package {package_name!r} points to current.md, but the current handoff window does not contain {package_key!r}. Move the row to archive or restore the current section.",
                    )
                )

    return {
        "status": "pass" if not findings else "findings",
        "path": _rel(path, root),
        "summary": {"checked_row_count": checked_row_count, "finding_count": len(findings)},
        "findings": findings,
    }
