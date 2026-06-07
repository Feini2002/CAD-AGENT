"""Build sanitized evidence portfolios for model-backed Agent judgement."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PORTFOLIO_FILE = "evidence_portfolio.json"

SAFE_SUMMARY_KEYS = (
    "status",
    "resultStatus",
    "readbackStatus",
    "cadGeometryVerified",
    "savedCurrentDwg",
    "targetLayer",
    "createdHandleCount",
    "blockingReasons",
    "issues",
    "warnings",
)

BLOCKED_SUFFIXES = (".dwg", ".dwt", ".bak")
BLOCKED_REF_PARTS = ("capability-map-data.js", "capability-map.html", "training_workbench_sync_report", "retention_report")


def _project_rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve())


def _run_rel(run_dir: Path, path: Path) -> str:
    return str(path.resolve().relative_to(run_dir.resolve())).replace("\\", "/")


def _resolve_ref(run_dir: Path, ref: str | Path) -> Path:
    path = Path(ref)
    if path.is_absolute():
        return path.resolve()
    run_candidate = (run_dir / path).resolve()
    if run_candidate.exists():
        return run_candidate
    project_candidate = (PROJECT_ROOT / path).resolve()
    if project_candidate.exists():
        return project_candidate
    return run_candidate


def _path_root(path: Path, run_dir: Path) -> str:
    resolved = path.resolve()
    for root_name, root in (("run_package", run_dir), ("project", PROJECT_ROOT)):
        try:
            resolved.relative_to(root.resolve())
            return root_name
        except ValueError:
            continue
    return "external"


def _blocked_reason(ref_text: str, path: Path, run_dir: Path) -> str:
    lowered = ref_text.casefold().replace("\\", "/")
    if _path_root(path, run_dir) == "external":
        return "external_path_not_exportable"
    if path.suffix.casefold() in BLOCKED_SUFFIXES:
        return "native_cad_file_not_exportable"
    if any(part.casefold() in lowered for part in BLOCKED_REF_PARTS):
        return "derived_or_diagnostic_snapshot_not_fact_source"
    if "output/" in lowered and lowered.rstrip("/") in {"output", "output/"}:
        return "whole_output_not_exportable"
    return ""


def _compact_json_file(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.suffix.casefold() != ".json":
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    return {key: payload[key] for key in SAFE_SUMMARY_KEYS if key in payload}


def _artifact(
    *,
    role: str,
    source_type: str,
    ref: str,
    run_dir: Path,
    token_budget: int,
) -> dict[str, Any]:
    path = _resolve_ref(run_dir, ref)
    path_root = _path_root(path, run_dir)
    blocked = _blocked_reason(ref, path, run_dir)
    sanitized = not blocked
    artifact: dict[str, Any] = {
        "role": role,
        "sourceType": source_type,
        "ref": ref.replace("\\", "/"),
        "pathRoot": path_root,
        "sanitized": sanitized,
        "exportAllowedReason": "minimal_summary_ref" if sanitized else "",
        "blockedReason": blocked,
        "notProofOf": ["CAD geometry", "user acceptance", "Project Delivery Readiness"],
        "tokenBudget": token_budget,
    }
    if sanitized:
        artifact["summary"] = _compact_json_file(path)
    return artifact


def build_evidence_portfolio(
    *,
    run_dir: str | Path,
    user_request: str,
    route: str,
    task_kind: str,
    hard_gates: list[str],
    evidence_refs: list[str] | None = None,
    memory_refs: list[str] | None = None,
    history_refs: list[str] | None = None,
    token_budget: int = 4000,
) -> dict[str, Any]:
    """Write a sanitized model judgement portfolio inside a run package."""

    run_root = Path(run_dir).resolve()
    run_root.mkdir(parents=True, exist_ok=True)
    artifacts: list[dict[str, Any]] = []
    for ref in evidence_refs or []:
        artifacts.append(_artifact(role="current_evidence", source_type="run_artifact", ref=str(ref), run_dir=run_root, token_budget=600))
    for ref in memory_refs or []:
        artifacts.append(_artifact(role="agent_memory", source_type="project_fact_source", ref=str(ref), run_dir=run_root, token_budget=300))
    for ref in history_refs or []:
        artifacts.append(_artifact(role="historical_risk", source_type="project_status", ref=str(ref), run_dir=run_root, token_budget=300))

    blocking_reasons = [str(item["blockedReason"]) for item in artifacts if item.get("blockedReason")]
    payload = {
        "schemaVersion": "evidence-portfolio/v1",
        "status": "blocked" if blocking_reasons else "ready",
        "userIntentSummary": user_request[:240],
        "route": str(route),
        "taskKind": str(task_kind),
        "hardGates": [str(item) for item in hard_gates],
        "artifacts": artifacts,
        "exportRefs": [str(item["ref"]) for item in artifacts if item.get("sanitized")],
        "blockingReasons": list(dict.fromkeys(blocking_reasons)),
        "tokenBudget": int(token_budget),
        "evidenceBoundary": {
            "cadWriteAuthorized": False,
            "saveCurrentDwgAuthorized": False,
            "deleteAuthorized": False,
            "notProofOf": [
                "CAD geometry",
                "用户验收",
                "Core Proof Coverage",
                "Project Delivery Readiness",
                "截图只能作为 visual_aid_only",
            ],
        },
    }
    path = run_root / PORTFOLIO_FILE
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "schemaVersion": "evidence-portfolio-build-result/v1",
        "status": payload["status"],
        "portfolioRef": _run_rel(run_root, path),
        "portfolioProjectRef": _project_rel(path),
        "exportRefs": payload["exportRefs"],
        "blockingReasons": payload["blockingReasons"],
    }
