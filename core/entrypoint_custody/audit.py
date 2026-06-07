"""Readonly audit for entrypoint custody coverage and obvious bypass risks."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from core.entrypoint_custody.manifest import (
    HIGH_RISK_CLASSES,
    PROJECT_ROOT,
    load_entrypoint_manifest,
    validate_manifest_entry,
)


SCRIPT_ROOTS = (Path("scripts"),)
BAT_GLOBS = ("*.bat",)
ACTIVE_DOC_PATHS = (
    "AGENTS.md",
    "CORE_CONTEXT_BRIEF.md",
    "CORE_RESTRUCTURE_PLAN.md",
    "CORE_STATUS.md",
    "README.md",
    "docs/architecture/README.md",
    "docs/status/current.md",
    "docs/training/README.md",
)
COMMAND_RE = re.compile(r"(?P<entrypoint>(?:scripts[\\/][\w.\-]+\.py)|(?:[\w.\-]+\.bat))")
WORKFLOW_ROUTES_PATH = Path("examples/orchestrator/workflow_routes.json")


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _finding(code: str, message: str, *, severity: str = "warning", **extra: Any) -> dict[str, Any]:
    return {"code": code, "severity": severity, "message": message, **extra}


def _repo_scripts(root: Path) -> list[str]:
    rows: list[str] = []
    for script_root in SCRIPT_ROOTS:
        scan_root = root / script_root
        if scan_root.is_dir():
            rows.extend(_display_path(path, root) for path in sorted(scan_root.glob("*.py")))
    for pattern in BAT_GLOBS:
        rows.extend(_display_path(path, root) for path in sorted(root.glob(pattern)))
    return sorted(set(rows))


def _active_doc_references(root: Path) -> list[dict[str, Any]]:
    references: list[dict[str, Any]] = []
    for raw_doc in ACTIVE_DOC_PATHS:
        doc_path = root / raw_doc
        if not doc_path.is_file():
            continue
        try:
            text = doc_path.read_text(encoding="utf-8-sig")
        except OSError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for match in COMMAND_RE.finditer(line):
                references.append(
                    {
                        "doc": raw_doc,
                        "line": line_number,
                        "entrypoint": match.group("entrypoint").replace("\\", "/"),
                        "text": line.strip()[:220],
                    }
                )
    return references


def _workflow_route_references(root: Path) -> list[dict[str, Any]]:
    path = root / WORKFLOW_ROUTES_PATH
    if not path.is_file():
        return []
    try:
        import json

        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return []
    routes = payload.get("routes", [])
    if not isinstance(routes, list):
        return []
    references: list[dict[str, Any]] = []
    for route in routes:
        if not isinstance(route, dict):
            continue
        entrypoint = str(route.get("entrypoint", ""))
        if not entrypoint:
            continue
        references.append(
            {
                "workflowId": str(route.get("workflow_id", "")),
                "entrypoint": entrypoint,
                "requiresCad": bool(route.get("requires_cad")),
                "doc": WORKFLOW_ROUTES_PATH.as_posix(),
            }
        )
    return references


def _manifest_entry_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entry_map = manifest.get("entrypointMap")
    if isinstance(entry_map, dict):
        return {str(key): value for key, value in entry_map.items() if isinstance(value, dict)}
    entries = manifest.get("entrypoints", [])
    if not isinstance(entries, list):
        return {}
    return {
        str(entry["entrypoint"]): entry
        for entry in entries
        if isinstance(entry, dict) and entry.get("entrypoint")
    }


def build_entrypoint_custody_audit(
    root: Path | None = None,
    *,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    project_root = Path(root or PROJECT_ROOT)
    manifest = load_entrypoint_manifest(manifest_path)
    entries = _manifest_entry_map(manifest)
    findings: list[dict[str, Any]] = []

    for entry in entries.values():
        findings.extend(validate_manifest_entry(entry))

    repo_entrypoints = _repo_scripts(project_root)
    for entrypoint in repo_entrypoints:
        if entrypoint not in entries:
            findings.append(
                _finding(
                    "unregistered_repo_entrypoint",
                    "repo script or batch entrypoint is not classified in custody manifest.",
                    severity="warning",
                    entrypoint=entrypoint,
                    operatorAction="classify as active, diagnostic, history-only, or ignored with a reason.",
                )
            )

    for reference in _active_doc_references(project_root):
        entry = entries.get(reference["entrypoint"])
        if entry is None:
            findings.append(
                _finding(
                    "active_doc_references_unregistered_entrypoint",
                    "active documentation references an unregistered entrypoint.",
                    severity="blocked",
                    **reference,
                    operatorAction="register the entrypoint or move the reference to history/diagnostic wording.",
                )
            )
            continue
        if bool(entry.get("historyOnly")) or entry.get("custodyStatus") in {
            "capability_proof_history",
            "scene_benchmark_history",
            "deprecated_blocked",
        }:
            text = str(reference.get("text", ""))
            if not any(
                marker in text
                for marker in ("历史", "history", "diagnostic", "诊断", "deprecated", "旧", "已完成", "证据目录", "最终证据")
            ):
                findings.append(
                    _finding(
                        "active_doc_recommends_history_only_entrypoint",
                        "active documentation references a history-only entrypoint without history/diagnostic boundary.",
                        severity="blocked",
                        **reference,
                        custodyStatus=entry.get("custodyStatus"),
                        operatorAction="mark the command as history/diagnostic or remove it from current next.",
                    )
                )

    for reference in _workflow_route_references(project_root):
        entry = entries.get(reference["entrypoint"])
        if entry is None:
            findings.append(
                _finding(
                    "workflow_route_entrypoint_unregistered",
                    "workflow route points to an entrypoint missing from custody manifest.",
                    severity="blocked",
                    **reference,
                    operatorAction="register the route entrypoint or remove the stale route.",
                )
            )
            continue
        if reference["requiresCad"] and str(entry.get("directInvocationPolicy")) != "blocked_without_lease":
            findings.append(
                _finding(
                    "cad_workflow_route_not_lease_controlled",
                    "CAD workflow route entrypoint must be lease-controlled.",
                    severity="blocked",
                    **reference,
                    directInvocationPolicy=entry.get("directInvocationPolicy"),
                )
            )

    for entrypoint, entry in entries.items():
        risk_class = str(entry.get("riskClass", ""))
        high_risk = risk_class in HIGH_RISK_CLASSES or entry.get("custodyStatus") in {
            "training_controlled",
            "asset_controlled",
        }
        if high_risk and not bool(entry.get("requiresCustodyGate")):
            findings.append(
                _finding(
                    "high_risk_manifest_entry_without_runtime_gate",
                    "high-risk entrypoint is registered but not protected by runtime custody gate.",
                    severity="blocked",
                    entrypoint=entrypoint,
                    riskClass=risk_class,
                )
            )
        if bool(entry.get("maySaveCurrentDwg")):
            findings.append(
                _finding(
                    "entrypoint_may_save_current_dwg",
                    "entrypoint can save current DWG; this requires explicit user authorization and closeout evidence.",
                    severity="warning",
                    entrypoint=entrypoint,
                )
            )

    blocked = [finding for finding in findings if finding.get("severity") == "blocked"]
    warnings = [finding for finding in findings if finding.get("severity") == "warning"]
    return {
        "schemaVersion": "entrypoint-custody-audit/v1",
        "status": "blocked" if blocked else ("warnings_only" if warnings else "pass"),
        "summary": {
            "manifestPath": manifest.get("manifestPath"),
            "registeredEntrypoints": len(entries),
            "repoEntrypointsScanned": len(repo_entrypoints),
            "activeDocReferences": len(_active_doc_references(project_root)),
            "workflowRouteReferences": len(_workflow_route_references(project_root)),
            "blockedCount": len(blocked),
            "warningCount": len(warnings),
        },
        "findings": findings,
        "operatorAction": "fix blocked findings before claiming entrypoint custody is closed."
        if blocked
        else ("review warnings; they do not block low-risk use." if warnings else "no action required."),
    }
