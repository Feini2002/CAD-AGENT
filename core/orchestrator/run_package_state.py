"""File-backed run packages for resumable orchestrator work."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import re
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN_ROOT = PROJECT_ROOT / "output" / "runs"

RUN_STATES = [
    "created",
    "context_collected",
    "orchestrator_reviewed",
    "dispatch_ready",
    "cad_executed",
    "visual_reviewed",
    "repair_needed",
    "blocked",
    "ready_for_delivery",
    "delivered",
]

RUN_PACKAGE_FILES = [
    "user_request.json",
    "context_pack.json",
    "task_contract.json",
    "dispatch_plan.json",
    "state.json",
    "final_report.md",
]

RUN_PACKAGE_SUBDIRS = [
    "agent_outputs",
    "cad_reports",
    "screenshots",
    "model_traces",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slugify_run_id(run_id: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", str(run_id)).strip(".-_").lower()
    slug = re.sub(r"-{2,}", "-", slug)
    return slug or f"run-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"


def _resolve_child(root: Path, child: str) -> Path:
    root = root.resolve()
    path = (root / child).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"run package path escaped root: {path}")
    return path


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _normalize_files(files: Iterable[str | Path] | None) -> list[str]:
    if files is None:
        return []
    return [str(item).replace("\\", "/") for item in files]


def _blank_stage_state() -> dict[str, Any]:
    return {
        "status": "pending",
        "inputFiles": [],
        "outputFiles": [],
        "blockingReason": "",
    }


def create_run_package(
    run_id: str,
    *,
    user_request: dict[str, Any],
    context_pack: dict[str, Any] | None = None,
    root_dir: str | Path = DEFAULT_RUN_ROOT,
) -> dict[str, Any]:
    """Create a resumable run package under ``output/runs/<run_id>/``."""

    root = Path(root_dir)
    root.mkdir(parents=True, exist_ok=True)
    safe_run_id = _slugify_run_id(run_id)
    run_dir = _resolve_child(root, safe_run_id)
    run_dir.mkdir(parents=True, exist_ok=False)
    for dirname in RUN_PACKAGE_SUBDIRS:
        (run_dir / dirname).mkdir()

    now = _utc_now()
    _write_json(
        run_dir / "user_request.json",
        {
            "schemaVersion": "run-package-user-request/v1",
            "runId": safe_run_id,
            "writtenAt": now,
            "userRequest": user_request,
        },
    )
    _write_json(
        run_dir / "context_pack.json",
        context_pack
        or {
            "schemaVersion": "run-package-context-pack/v1",
            "runId": safe_run_id,
            "status": "not_collected",
            "items": [],
        },
    )
    _write_json(
        run_dir / "task_contract.json",
        {
            "schemaVersion": "run-package-task-contract/v1",
            "runId": safe_run_id,
            "status": "not_reviewed",
            "blockingReasons": [],
        },
    )
    _write_json(
        run_dir / "dispatch_plan.json",
        {
            "schemaVersion": "run-package-dispatch-plan/v1",
            "runId": safe_run_id,
            "status": "not_ready",
            "tasks": [],
        },
    )
    (run_dir / "final_report.md").write_text(
        f"# Run Package {safe_run_id}\n\nStatus: created\n",
        encoding="utf-8",
    )

    state = {
        "schemaVersion": "run-package-state/v1",
        "runId": safe_run_id,
        "runDir": str(run_dir),
        "status": "created",
        "currentStage": "created",
        "createdAt": now,
        "updatedAt": now,
        "stages": {stage: _blank_stage_state() for stage in RUN_STATES},
        "events": [],
    }
    state["stages"]["created"] = {
        "status": "completed",
        "inputFiles": ["user_request.json"],
        "outputFiles": RUN_PACKAGE_FILES + RUN_PACKAGE_SUBDIRS,
        "blockingReason": "",
    }
    state["events"].append(
        {
            "at": now,
            "stage": "created",
            "status": "completed",
            "inputFiles": ["user_request.json"],
            "outputFiles": RUN_PACKAGE_FILES + RUN_PACKAGE_SUBDIRS,
            "blockingReason": "",
        }
    )
    _write_json(run_dir / "state.json", state)
    return state


def load_run_state(run_dir_or_state_path: str | Path) -> dict[str, Any]:
    """Load ``state.json`` from either a run directory or an explicit file path."""

    path = Path(run_dir_or_state_path)
    state_path = path / "state.json" if path.is_dir() else path
    return json.loads(state_path.read_text(encoding="utf-8"))


def advance_run_state(
    run_dir_or_state_path: str | Path,
    stage: str,
    *,
    input_files: Iterable[str | Path] | None = None,
    output_files: Iterable[str | Path] | None = None,
    blocking_reason: str = "",
) -> dict[str, Any]:
    """Advance a run package stage and persist the updated ``state.json``."""

    if stage not in RUN_STATES:
        raise ValueError(f"unknown run package stage: {stage}")
    if stage == "blocked" and not blocking_reason.strip():
        raise ValueError("blocking_reason is required when advancing to blocked")

    path = Path(run_dir_or_state_path)
    state_path = path / "state.json" if path.is_dir() else path
    state = load_run_state(state_path)
    now = _utc_now()
    stage_status = "blocked" if stage == "blocked" else "completed"
    input_list = _normalize_files(input_files)
    output_list = _normalize_files(output_files)
    reason = blocking_reason.strip()

    state["status"] = stage
    state["currentStage"] = stage
    state["updatedAt"] = now
    stages = state.setdefault("stages", {})
    for planned_stage in RUN_STATES:
        stages.setdefault(planned_stage, _blank_stage_state())
    stages[stage] = {
        "status": stage_status,
        "inputFiles": input_list,
        "outputFiles": output_list,
        "blockingReason": reason,
    }
    state.setdefault("events", []).append(
        {
            "at": now,
            "stage": stage,
            "status": stage_status,
            "inputFiles": input_list,
            "outputFiles": output_list,
            "blockingReason": reason,
        }
    )
    _write_json(state_path, state)
    return state
