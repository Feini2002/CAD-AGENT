from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "workbench-trace-viewer/v1"
DEFAULT_MAX_RUNS = 24
DEFAULT_MAX_TRACES = 80
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in values if item))


def _modified_time(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in _as_list(value) if str(item).strip()]


def _agent_ids_from_required_agents(value: Any) -> list[str]:
    agent_ids: list[str] = []
    for item in _as_list(value):
        if isinstance(item, str):
            agent_ids.append(item)
        elif isinstance(item, dict):
            agent_id = item.get("agentId") or item.get("id") or item.get("name")
            if agent_id:
                agent_ids.append(str(agent_id))
    return agent_ids


def _agent_ids_from_json_files(run_dir: Path) -> list[str]:
    agent_ids: list[str] = []
    for path in sorted((run_dir / "agent_outputs").glob("*.json")):
        if path.name.endswith(".model_review.json"):
            agent_ids.append(path.name.removesuffix(".model_review.json"))
        else:
            agent_ids.append(path.stem)
        payload = _read_json(path)
        for key in ("agentId", "id"):
            if payload.get(key):
                agent_ids.append(str(payload[key]))
    for path in sorted((run_dir / "model_traces").glob("*")):
        if path.is_dir():
            agent_ids.append(path.name)
        elif path.suffix == ".json":
            payload = _read_json(path)
            if payload.get("agentId"):
                agent_ids.append(str(payload["agentId"]))
    return agent_ids


def _run_dirs(root: Path) -> list[Path]:
    base = root / "output" / "runs"
    if not base.is_dir():
        return []
    candidates = [
        path
        for path in base.iterdir()
        if path.is_dir()
        and any(
            (path / rel).is_file()
            for rel in (
                "run_state.json",
                "dispatch_plan.json",
                "task_contract.json",
                "closeout_decision.json",
            )
        )
    ]
    return sorted(candidates, key=_modified_time, reverse=True)


def _gate_summary(run_dir: Path) -> list[dict[str, Any]]:
    gate_files = [
        ("validate_plan", run_dir / "cad_reports" / "validation_report.json"),
        ("dry_run", run_dir / "cad_reports" / "dry_run_report.json"),
        ("cad_readback", run_dir / "cad_reports" / "readback_summary.json"),
        ("visual_acceptance_review", run_dir / "agent_outputs" / "visual_acceptance_output.json"),
        ("visual_acceptance_review", run_dir / "agent_outputs" / "pipeline_visual_acceptance_reviewer.json"),
        ("neighbor_protection", run_dir / "cad_reports" / "neighbor_protection.json"),
        ("delete_scope_gate", run_dir / "cad_reports" / "delete_scope_gate.json"),
        ("asset_source_boundary", run_dir / "cad_reports" / "asset_source_boundary.json"),
        ("closeout_gate", run_dir / "closeout_decision.json"),
    ]
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for gate_id, path in gate_files:
        if not path.is_file():
            continue
        payload = _read_json(path)
        key = (gate_id, _rel(run_dir, path))
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "id": gate_id,
                "status": str(payload.get("status") or payload.get("decision") or "unknown"),
                "canDeliver": payload.get("can_deliver"),
                "blockingReasons": _string_list(payload.get("blocking_reasons") or payload.get("blockingReasons")),
                "source": _rel(run_dir, path),
            }
        )
    return rows


def _run_agent_ids(run_dir: Path) -> list[str]:
    required = _read_json(run_dir / "required_agents.json")
    dispatch = _read_json(run_dir / "dispatch_plan.json")
    contract = _read_json(run_dir / "task_contract.json")
    return _unique(
        [
            *_agent_ids_from_required_agents(required.get("requiredAgents")),
            *_agent_ids_from_required_agents(dispatch.get("requiredAgents")),
            *_agent_ids_from_required_agents(contract.get("requiredAgents")),
            *_agent_ids_from_json_files(run_dir),
        ]
    )


def _trace_files(run_dir: Path) -> list[Path]:
    base = run_dir / "model_traces"
    if not base.is_dir():
        return []
    return sorted(base.glob("**/*.json"), key=_modified_time, reverse=True)


def _external_trace_rows(root: Path, max_traces: int) -> list[dict[str, Any]]:
    base = root / "output" / "model_reviews" / "traces"
    if not base.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(base.glob("**/*.json"), key=_modified_time, reverse=True)[:max_traces]:
        payload = _read_json(path)
        agent_id = payload.get("agentId") or path.parent.name
        rows.append(
            {
                "agentId": str(agent_id),
                "status": str(payload.get("status") or payload.get("decision") or "unknown"),
                "source": _rel(root, path),
                "traceId": str(payload.get("traceId") or path.stem),
            }
        )
    return rows


def _run_summary(root: Path, run_dir: Path) -> dict[str, Any]:
    state = _read_json(run_dir / "run_state.json")
    dispatch = _read_json(run_dir / "dispatch_plan.json")
    closeout = _read_json(run_dir / "closeout_decision.json")
    trace_files = _trace_files(run_dir)
    run_id = state.get("runId") or dispatch.get("runId") or closeout.get("runId") or run_dir.name
    evidence_boundary = closeout.get("evidence_boundary", {})
    return {
        "runId": str(run_id),
        "runDir": _rel(root, run_dir),
        "stateStatus": str(state.get("status") or closeout.get("status") or "unknown"),
        "route": str(dispatch.get("route") or dispatch.get("taskKind") or ""),
        "agentsCalled": _run_agent_ids(run_dir),
        "hardGates": _string_list(dispatch.get("hardGates")),
        "gateSummary": _gate_summary(run_dir),
        "promptPackTraceCount": len(trace_files),
        "traceSources": [_rel(root, path) for path in trace_files[:12]],
        "closeout": {
            "status": closeout.get("status", "missing"),
            "canDeliver": bool(closeout.get("can_deliver")) if closeout else False,
            "blockingReasons": _string_list(closeout.get("blocking_reasons")),
        },
        "evidenceBoundary": {
            "checked": _string_list(evidence_boundary.get("checked") if isinstance(evidence_boundary, dict) else []),
            "notChecked": _string_list(
                evidence_boundary.get("not_checked") if isinstance(evidence_boundary, dict) else []
            ),
            "notProven": _string_list(
                evidence_boundary.get("notProven") if isinstance(evidence_boundary, dict) else []
            ),
        },
    }


def _contract_workbench_context(contract_workbench: dict[str, Any] | None) -> dict[str, Any]:
    rows = _contract_projection_rows(contract_workbench)
    summary = {}
    if isinstance(contract_workbench, dict) and isinstance(contract_workbench.get("summary"), dict):
        summary = dict(contract_workbench["summary"])
    if not summary:
        summary = _contract_projection_summary(rows)
    return {
        "readOnly": True,
        "mutatedTargets": [],
        "summary": summary,
        "blockedTaskIds": [str(row.get("task_id") or "") for row in rows if row.get("completion_status") == "blocked"],
        "notVerifiedTaskIds": [
            str(row.get("task_id") or "")
            for row in rows
            if row.get("verification_status") != "verified" or row.get("completion_status") == "not_verified"
        ],
    }


def _contract_projection_rows(contract_workbench: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(contract_workbench, dict):
        return []
    views = contract_workbench.get("views", {}) if isinstance(contract_workbench.get("views"), dict) else {}
    evidence_center = views.get("evidenceCenter", {}) if isinstance(views.get("evidenceCenter"), dict) else {}
    candidates = (
        evidence_center.get("contractWorkbenchProjections")
        or contract_workbench.get("contractWorkbenchProjections")
        or []
    )
    return [dict(row) for row in _as_list(candidates) if isinstance(row, dict)]


def _contract_projection_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    blocked = [row for row in rows if row.get("completion_status") == "blocked"]
    not_verified = [
        row
        for row in rows
        if row.get("verification_status") != "verified" or row.get("completion_status") == "not_verified"
    ]
    return {
        "projectionCount": len(rows),
        "readyCount": len([row for row in rows if row.get("completion_status") == "ready"]),
        "blockedCount": len(blocked),
        "notVerifiedCount": len(not_verified),
        "ledgerRecordCount": sum(_safe_int(row.get("ledger_record_count")) for row in rows),
    }


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def build_workbench_trace_viewer_data(
    root: str | Path = PROJECT_ROOT,
    *,
    max_runs: int = DEFAULT_MAX_RUNS,
    max_traces: int = DEFAULT_MAX_TRACES,
    contract_workbench: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a derived, read-only trace snapshot for the training workbench."""

    repo_root = Path(root)
    runs = [_run_summary(repo_root, run_dir) for run_dir in _run_dirs(repo_root)[:max_runs]]
    external_traces = _external_trace_rows(repo_root, max_traces)
    agent_ids = sorted({agent_id for run in runs for agent_id in run.get("agentsCalled", [])})
    blocked = [run for run in runs if run.get("closeout", {}).get("canDeliver") is False]
    ready = [run for run in runs if run.get("closeout", {}).get("canDeliver") is True]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": _utc_now(),
        "sourcePolicy": {
            "derivedOnly": True,
            "truthSources": ["output/runs/**", "output/model_reviews/traces/**"],
            "notProofOf": [
                "does_not_prove_cad_geometry",
                "does_not_replace_created_handles_readback",
                "does_not_replace_user_visual_acceptance",
                "does_not_upgrade_table_c",
            ],
            "evidenceBoundary": "该面板只帮助查看 Agent 调用、模型 trace 和 gate 状态；真实 CAD 仍以 source JSON、registry、created handles 回读和用户验收为准。",
        },
        "summary": {
            "runCount": len(runs),
            "readyRunCount": len(ready),
            "blockedRunCount": len(blocked),
            "agentCount": len(agent_ids),
            "externalTraceCount": len(external_traces),
        },
        "contractWorkbench": _contract_workbench_context(contract_workbench),
        "agentIds": agent_ids,
        "runs": runs,
        "externalTraces": external_traces,
    }


def write_workbench_trace_viewer_data(
    output_path: str | Path,
    root: str | Path = PROJECT_ROOT,
    *,
    max_runs: int = DEFAULT_MAX_RUNS,
    max_traces: int = DEFAULT_MAX_TRACES,
    contract_workbench: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = build_workbench_trace_viewer_data(
        root,
        max_runs=max_runs,
        max_traces=max_traces,
        contract_workbench=contract_workbench,
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data
