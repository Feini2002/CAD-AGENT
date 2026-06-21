#!/usr/bin/env python
"""Build the lightweight runtime trace snapshot used by the training workbench."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.runtime.encoding_guard import configure_utf8_process


DEFAULT_OUTPUT = Path("output/runtime_traces/latest.json")
WORKER_CHECKLIST = Path("docs/deploy/worker-orchestrator-deploy-checklist.md")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _mtime_ms(path: Path) -> int | None:
    try:
        return int(path.stat().st_mtime * 1000)
    except OSError:
        return None


def _iso_from_mtime(path: Path) -> str:
    ms = _mtime_ms(path)
    if ms is None:
        return ""
    return datetime.fromtimestamp(ms / 1000, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _latest_run_dir(root: Path) -> Path | None:
    run_root = root / "output" / "runs"
    if not run_root.is_dir():
        return None
    candidates = [path for path in run_root.glob("model-agent-live-collab-proof-*") if path.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.stat().st_mtime)


def _latest_preview(root: Path, run_id: str) -> Path | None:
    preview_root = root / "output" / "previews"
    if not preview_root.is_dir():
        return None
    candidates = list(preview_root.glob("worker-bridge-cad-preview-*.png"))
    if not candidates and run_id:
        candidates = list(preview_root.glob(f"*{run_id}*.png"))
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.stat().st_mtime)


def _latest_visual_review(root: Path, run_id: str) -> Path | None:
    review_root = root / "output" / "validation_runs"
    if not review_root.is_dir():
        return None
    candidates = list(review_root.glob("worker-bridge-cad-preview-*/visual-review/visual_review_report.json"))
    if run_id:
        exact = list(review_root.glob(f"*{run_id}*/visual-review/visual_review_report.json"))
        if exact:
            candidates = exact
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.stat().st_mtime)


def _relative(root: Path, path: Path | None) -> str:
    if not path:
        return ""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _extract_worker(checklist: Path) -> dict[str, str]:
    text = checklist.read_text(encoding="utf-8") if checklist.is_file() else ""
    run_ids = re.findall(r"run_\d+_worker_orchestration_ready_[a-z0-9]+", text)
    versions = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", text)
    return {
        "workerName": "cadagent" if "cadagent" in text else "",
        "workerUrl": "https://cadagent.cmw1196466375.workers.dev" if "cadagent.cmw1196466375.workers.dev" in text else "",
        "workerRunId": run_ids[-1] if run_ids else "",
        "workerVersion": versions[-1] if versions else "",
    }


def _step(
    *,
    step_id: str,
    label: str,
    owner: str,
    status: str,
    detail: str,
    evidence: str = "",
    blocker: str = "",
    at: str = "",
    duration_ms: int | None = None,
) -> dict[str, Any]:
    return {
        "id": step_id,
        "label": label,
        "owner": owner,
        "status": status,
        "detail": detail,
        "durationMs": duration_ms,
        "at": at,
        "blocker": blocker,
        "evidence": evidence,
    }


def _duration(previous_ms: int | None, current_ms: int | None) -> int | None:
    if previous_ms is None or current_ms is None:
        return None
    delta = current_ms - previous_ms
    return delta if delta >= 0 else None


def build_snapshot(root: Path) -> dict[str, Any]:
    run_dir = _latest_run_dir(root)
    worker = _extract_worker(root / WORKER_CHECKLIST)

    result = _read_json(run_dir / "model_agent_chain_result.json") if run_dir else {}
    preview_report = _read_json(run_dir / "cad_reports" / "cad_preview_tool_report.json") if run_dir else {}
    execution = _read_json(run_dir / "cad_reports" / "execution_summary.json") if run_dir else {}
    readback = _read_json(run_dir / "cad_reports" / "readback_summary.json") if run_dir else {}
    closeout = _read_json(run_dir / "closeout_decision.json") if run_dir else {}
    validation = _read_json(run_dir / "cad_reports" / "validation_report.json") if run_dir else {}
    dry_run = _read_json(run_dir / "cad_reports" / "dry_run_report.json") if run_dir else {}

    run_id = str(result.get("runId") or (run_dir.name if run_dir else "") or "")
    screenshot_path = _latest_preview(root, run_id)
    visual_review_path = _latest_visual_review(root, run_id)
    visual_review = _read_json(visual_review_path) if visual_review_path else {}

    evidence_times = [
        root / WORKER_CHECKLIST,
        run_dir / "model_agent_chain_result.json" if run_dir else None,
        run_dir / "cad_reports" / "validation_report.json" if run_dir else None,
        run_dir / "cad_reports" / "dry_run_report.json" if run_dir else None,
        run_dir / "cad_reports" / "cad_preview_tool_report.json" if run_dir else None,
        run_dir / "cad_reports" / "readback_summary.json" if run_dir else None,
        screenshot_path,
        visual_review_path,
    ]
    mtimes = [_mtime_ms(path) if isinstance(path, Path) else None for path in evidence_times]

    closeout_blockers = closeout.get("blocking_reasons") or closeout.get("blockingReasons") or result.get("closeoutEvidence", {}).get("blockingReasons") or []
    if not isinstance(closeout_blockers, list):
        closeout_blockers = [str(closeout_blockers)]
    visual_blockers = [
        check.get("message")
        for check in visual_review.get("checks", [])
        if isinstance(check, dict) and check.get("status") == "fail"
    ]

    steps = [
        _step(
            step_id="codex_plaintext",
            label="Codex 白话理解",
            owner="codex",
            status="pass" if run_dir else "not_checked",
            detail="由当前 Codex 会话把白话转成受控 quick smoke，不作为独立后台事实源。",
            evidence=_relative(root, run_dir / "user_request.json") if run_dir else "",
            at=_iso_from_mtime(run_dir / "user_request.json") if run_dir else "",
            duration_ms=None,
        ),
        _step(
            step_id="worker_smoke",
            label="Cloudflare Worker 通道",
            owner="worker",
            status="pass" if worker.get("workerRunId") else "not_checked",
            detail=f"{worker.get('workerRunId') or '未找到远程 smoke runId'} · version {worker.get('workerVersion') or 'unknown'}",
            evidence=_relative(root, root / WORKER_CHECKLIST),
            at=_iso_from_mtime(root / WORKER_CHECKLIST),
            duration_ms=_duration(mtimes[0], mtimes[1]),
        ),
        _step(
            step_id="agent_chain",
            label="Agent 链路拆分",
            owner="codex-agent",
            status="pass" if result.get("modelChainStatus") == "ready" else result.get("modelChainStatus") or "not_checked",
            detail=f"{len(result.get('agentOutputChain') or [])} 个输出；本轮使用 fixture model，不证明真实 gpt-5.5 provider。",
            evidence=_relative(root, run_dir / "model_agent_chain_result.json") if run_dir else "",
            at=_iso_from_mtime(run_dir / "model_agent_chain_result.json") if run_dir else "",
            duration_ms=_duration(mtimes[1], mtimes[2]),
        ),
        _step(
            step_id="validate_plan",
            label="CAD_PLAN 校验",
            owner="pipeline_audit",
            status=validation.get("status") or "pass" if validation else "not_checked",
            detail="validate_plan 通过后才允许进入受控 CAD preview。",
            evidence=_relative(root, run_dir / "cad_reports" / "validation_report.json") if run_dir else "",
            at=_iso_from_mtime(run_dir / "cad_reports" / "validation_report.json") if run_dir else "",
            duration_ms=_duration(mtimes[2], mtimes[3]),
        ),
        _step(
            step_id="dry_run",
            label="dry-run 预演",
            owner="pipeline_audit",
            status=dry_run.get("status") or "pass" if dry_run else "not_checked",
            detail="只预演 CAD_PLAN，不写正式图层。",
            evidence=_relative(root, run_dir / "cad_reports" / "dry_run_report.json") if run_dir else "",
            at=_iso_from_mtime(run_dir / "cad_reports" / "dry_run_report.json") if run_dir else "",
            duration_ms=_duration(mtimes[3], mtimes[4]),
        ),
        _step(
            step_id="cad_preview",
            label="CAD-MCP 安全预览",
            owner="local-bridge/cad",
            status="pass" if preview_report.get("cadGeometryVerified") is True else preview_report.get("status") or "not_checked",
            detail=f"{preview_report.get('createdHandleCount', 0)} created handles · layer {preview_report.get('targetLayer') or 'unknown'} · savedCurrentDwg={preview_report.get('savedCurrentDwg')}",
            evidence=_relative(root, run_dir / "cad_reports" / "cad_preview_tool_report.json") if run_dir else "",
            at=_iso_from_mtime(run_dir / "cad_reports" / "cad_preview_tool_report.json") if run_dir else "",
            duration_ms=_duration(mtimes[4], mtimes[5]),
        ),
        _step(
            step_id="cad_readback",
            label="CAD 回读",
            owner="local-bridge/cad",
            status="pass" if readback.get("readbackStatus") == "ok" and readback.get("cadGeometryVerified") is True else readback.get("readbackStatus") or "not_checked",
            detail=f"{readback.get('readbackEntityCount', 0)} readback entities · savedCurrentDwg={readback.get('savedCurrentDwg')}",
            evidence=_relative(root, run_dir / "cad_reports" / "readback_summary.json") if run_dir else "",
            at=_iso_from_mtime(run_dir / "cad_reports" / "readback_summary.json") if run_dir else "",
            duration_ms=_duration(mtimes[5], mtimes[6]),
        ),
        _step(
            step_id="screenshot",
            label="截图证据",
            owner="pipeline_audit",
            status="pass" if screenshot_path and screenshot_path.is_file() else "not_checked",
            detail="截图只是 visual_aid_only，不能替代 handles/readback。",
            evidence=_relative(root, screenshot_path),
            at=_iso_from_mtime(screenshot_path) if screenshot_path else "",
            duration_ms=_duration(mtimes[6], mtimes[7]),
        ),
        _step(
            step_id="closeout",
            label="收尾门禁",
            owner="pipeline_delivery",
            status="blocked" if closeout_blockers or visual_blockers else closeout.get("status") or "not_checked",
            detail="; ".join([str(item) for item in [*closeout_blockers, *visual_blockers] if item]) or "未发现阻断项。",
            evidence=_relative(root, visual_review_path or (run_dir / "closeout_decision.json" if run_dir else None)),
            blocker="; ".join([str(item) for item in [*closeout_blockers, *visual_blockers] if item]),
            at=_iso_from_mtime(visual_review_path or (run_dir / "closeout_decision.json" if run_dir else None)) if (visual_review_path or run_dir) else "",
            duration_ms=None,
        ),
    ]

    status = "blocked" if any(step["status"] == "blocked" for step in steps) else "pass" if any(step["status"] == "pass" for step in steps) else "not_checked"
    total_duration = None
    numeric_times = [time for time in mtimes if isinstance(time, int)]
    if len(numeric_times) >= 2:
        total_duration = max(numeric_times) - min(numeric_times)

    return {
        "schemaVersion": "cad-agent-runtime-trace/v1",
        "generatedAt": _utc_now(),
        "status": status,
        "runId": run_id,
        "worker": worker,
        "runDir": _relative(root, run_dir),
        "totalDurationMs": total_duration,
        "steps": steps,
        "evidence": {
            "runPackage": _relative(root, run_dir),
            "screenshot": _relative(root, screenshot_path),
            "visualReview": _relative(root, visual_review_path),
            "cadPreviewReport": _relative(root, run_dir / "cad_reports" / "cad_preview_tool_report.json") if run_dir else "",
        },
        "storagePolicy": {
            "mode": "rolling_latest_only",
            "writes": [_relative(root, root / DEFAULT_OUTPUT)],
            "keepsHistory": False,
            "createsNewTraceFiles": False,
            "doesNotClean": [
                "output/runs/**",
                "output/previews/**",
                "output/validation_runs/**",
            ],
            "humanSummary": "链路追踪只覆盖写 latest.json，不按每轮追加历史；原始 CAD 证据包仍由仓库保留策略单独治理。",
        },
        "boundary": [
            "本面板读取本地快照，不主动执行 CAD。",
            "durationMs 由证据文件时间推导；缺少事件日志时显示为未记录。",
            "quick smoke 不等于正式训练、真实 gpt-5.5 provider proof 或表 C 提升。",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    configure_utf8_process()
    parser = argparse.ArgumentParser(description="Build a lightweight runtime trace snapshot for capability-map.html.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    snapshot = build_snapshot(root)
    output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "pass", "output": _relative(root, output), "runId": snapshot.get("runId"), "traceStatus": snapshot.get("status")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
