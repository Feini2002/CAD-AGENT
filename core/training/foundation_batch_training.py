"""Batch training runner for the remaining CAD foundation-operation items."""

from __future__ import annotations

import json
import re
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from core.safety.policy import PREVIEW_LAYER
from core.safety.write_guard import run_negative_write_guard_checks
from core.training.adaptive_replay_planner import build_adaptive_replay_plan, disabled_adaptive_replay_plan
from core.training.capability_growth_profile import build_capability_growth_profile
from core.training.expression_regression_gate import evaluate_expression_regression_guard
from core.training.foundation_panel_drawings import (
    LINEWEIGHT_STANDARD_SAMPLES,
    PANEL_COLUMNS,
    PANEL_GAP,
    PANEL_HEIGHT,
    PANEL_WIDTH,
    driver_declares_operation_batch,
    draw_foundation_item,
)
from core.training.streaming_demo import ClockFn, SleepFn, StreamingCadDemoConfig, StreamingCadDemoRecorder
from core.verification.render_preview import build_screenshot_decision, prepare_autocad_for_capture, visual_preview_payload


FOUNDATION_FIRST_10_IDS = [
    "cad-primitives",
    "cad-selection-edit",
    "cad-transform",
    "cad-offset-trim",
    "cad-layer-discipline",
    "cad-closure-constraints",
    "cad-readback-audit",
    "cad-units-scale",
    "cad-coordinate-input",
    "cad-osnap-ortho-polar",
]

FOUNDATION_REMAINING_21_IDS = [
    "cad-polyline-width-cleanup",
    "cad-hatch-boundary",
    "cad-boundary-region",
    "cad-fillet-chamfer",
    "cad-stretch-edit",
    "cad-block-insert-attribute",
    "cad-block-rotate-scale",
    "cad-xref-underlay-protect",
    "cad-layout-viewport",
    "cad-plot-scale-titleblock",
    "cad-redline-revision",
    "cad-layer-lineweight-standard",
    "cad-selection-by-room",
    "cad-array-copy-pattern",
    "cad-measure-distance-area",
    "cad-purge-audit-cleanup",
    "cad-dim-style-baseline",
    "cad-text-mleader-style",
    "cad-handle-bbox-report",
    "cad-layer-pollution-check",
    "cad-safe-undo-rollback",
]
FOUNDATION_ALL_31_IDS = FOUNDATION_FIRST_10_IDS + FOUNDATION_REMAINING_21_IDS

FOUNDATION_BATCH_CONFIGS: dict[str, dict[str, Any]] = {
    "remaining-21": {
        "ids": FOUNDATION_REMAINING_21_IDS,
        "queueId": "cad-foundation-remaining-21",
        "mode": "unsupervised_batch_chinese_labels",
        "artifactPrefix": "remaining_21",
        "displayStart": 11,
        "label": "剩余 21 项基础 CAD 操作",
    },
    "all-31": {
        "ids": FOUNDATION_ALL_31_IDS,
        "queueId": "cad-foundation-all-31",
        "mode": "unsupervised_full_batch_retrain",
        "artifactPrefix": "all_31",
        "displayStart": 1,
        "label": "完整 31 项基础 CAD 操作",
    },
}

QUEUE_ID = "cad-foundation-remaining-21"
MODE = "unsupervised_batch_chinese_labels"
LATIN_WORD_RE = re.compile(r"[A-Za-z]{2,}")
TRAINING_PARKING_GAP = 2000.0
LINEWEIGHT_STANDARD_CAPABILITY_ID = "cad-layer-lineweight-standard"


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _artifact(path: Path, output_dir: Path) -> str:
    try:
        return path.resolve().relative_to(output_dir.resolve()).as_posix()
    except ValueError:
        return str(path)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}


def _batch_config(batch_preset: str) -> dict[str, Any]:
    if batch_preset not in FOUNDATION_BATCH_CONFIGS:
        raise ValueError(f"unknown foundation batch preset: {batch_preset}")
    return FOUNDATION_BATCH_CONFIGS[batch_preset]


def _previous_training_handles(output_dir: Path, *, artifact_prefix: str = "remaining_21") -> list[str]:
    summary = _read_json(output_dir / f"{artifact_prefix}_execution_summary.json")
    handles = summary.get("created_handles")
    if not isinstance(handles, list):
        return []
    return [str(handle) for handle in handles if handle]


def _program_map(programs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(program.get("capabilityId", "")): program for program in programs}


def foundation_batch_programs(programs: list[dict[str, Any]], capability_ids: list[str]) -> list[dict[str, Any]]:
    by_id = _program_map(programs)
    missing = [capability_id for capability_id in capability_ids if capability_id not in by_id]
    if missing:
        raise ValueError(f"training programs missing from workbench data: {missing}")
    return [by_id[capability_id] for capability_id in capability_ids]


def foundation_remaining_programs(programs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return foundation_batch_programs(programs, FOUNDATION_REMAINING_21_IDS)


def _foundation_item_entries(
    programs: list[dict[str, Any]],
    selected_capability_ids: list[str] | None = None,
    *,
    capability_ids: list[str] | None = None,
    display_start: int = 11,
) -> list[tuple[int, dict[str, Any]]]:
    items = foundation_batch_programs(programs, capability_ids or FOUNDATION_REMAINING_21_IDS)
    by_id = {
        str(item["capabilityId"]): (index, {**item, "displayIndex": display_start + index})
        for index, item in enumerate(items)
    }
    if not selected_capability_ids:
        return [(index, {**item, "displayIndex": display_start + index}) for index, item in enumerate(items)]
    missing = [capability_id for capability_id in selected_capability_ids if capability_id not in by_id]
    if missing:
        raise ValueError(f"focused foundation training ids are unknown: {missing}")
    return [by_id[capability_id] for capability_id in selected_capability_ids]


def _bbox_from_entities(entities: list[dict[str, Any]]) -> dict[str, list[float]] | None:
    xs: list[float] = []
    ys: list[float] = []
    for entity in entities:
        bbox = entity.get("bbox")
        if isinstance(bbox, dict):
            minimum = bbox.get("min")
            maximum = bbox.get("max")
            if isinstance(minimum, list) and isinstance(maximum, list) and len(minimum) >= 2 and len(maximum) >= 2:
                xs.extend([float(minimum[0]), float(maximum[0])])
                ys.extend([float(minimum[1]), float(maximum[1])])
                continue
        for key in ("start_point", "end_point", "position", "center", "insertion_point"):
            point = entity.get(key)
            if isinstance(point, list) and len(point) >= 2:
                xs.append(float(point[0]))
                ys.append(float(point[1]))
        points = entity.get("points")
        if isinstance(points, list):
            for point in points:
                if isinstance(point, list) and len(point) >= 2:
                    xs.append(float(point[0]))
                    ys.append(float(point[1]))
    if not xs or not ys:
        return None
    return {"min": [min(xs), min(ys)], "max": [max(xs), max(ys)]}


def _bbox_overlap(a: dict[str, list[float]] | None, b: dict[str, list[float]] | None) -> bool:
    if a is None or b is None:
        return False
    return not (
        float(a["max"][0]) <= float(b["min"][0])
        or float(b["max"][0]) <= float(a["min"][0])
        or float(a["max"][1]) <= float(b["min"][1])
        or float(b["max"][1]) <= float(a["min"][1])
    )


def _parking_anchor(
    driver: Any,
    output_dir: Path,
    existing_bbox: dict[str, list[float]] | None,
    *,
    artifact_prefix: str = "remaining_21",
) -> dict[str, Any]:
    previous_handles = _previous_training_handles(output_dir, artifact_prefix=artifact_prefix)
    previous_entities = []
    if previous_handles and hasattr(driver, "snapshot_handles"):
        previous_entities = driver.snapshot_handles(handles=previous_handles, layer=PREVIEW_LAYER)
    previous_bbox = _bbox_from_entities(previous_entities)
    if previous_bbox is not None:
        base = [float(previous_bbox["max"][0]) + TRAINING_PARKING_GAP, float(previous_bbox["max"][1]), 0.0]
        return {
            "source": "previous_handles",
            "bbox": previous_bbox,
            "basePoint": base,
            "resolvedHandleCount": len(previous_entities),
            "handleCount": len(previous_handles),
            "rule": "用户移动上一轮训练对象后，以这些句柄的当前位置作为训练停放区参考。",
        }
    if existing_bbox is not None:
        base = [float(existing_bbox["max"][0]) + TRAINING_PARKING_GAP, float(existing_bbox["max"][1]), 0.0]
        return {
            "source": "global_preview_bbox",
            "bbox": existing_bbox,
            "basePoint": base,
            "resolvedHandleCount": 0,
            "handleCount": len(previous_handles),
            "rule": "没有可回读的上一轮句柄时，才退回到全局预览 bbox 右侧空白区。",
        }
    return {
        "source": "origin",
        "bbox": None,
        "basePoint": [0.0, 0.0, 0.0],
        "resolvedHandleCount": 0,
        "handleCount": len(previous_handles),
        "rule": "没有旧预览对象时，从原点训练停放区开始。",
    }


def _contains_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def _contains_latin_word(text: str) -> bool:
    return bool(LATIN_WORD_RE.search(text))


def _panel_origin(base: list[float], index: int) -> list[float]:
    column = index % PANEL_COLUMNS
    row = index // PANEL_COLUMNS
    return [
        base[0] + column * (PANEL_WIDTH + PANEL_GAP),
        base[1] - row * (PANEL_HEIGHT + PANEL_GAP),
        0.0,
    ]


def _build_plan(
    item_entries: list[tuple[int, dict[str, Any]]],
    base: list[float],
    *,
    scope: dict[str, Any],
    training_options: dict[str, Any] | None = None,
    queue_id: str = QUEUE_ID,
    batch_mode: str = MODE,
    replay_mode: str = "smoke_replay",
    adaptive_replay: dict[str, Any] | None = None,
) -> dict[str, Any]:
    plan_items = []
    for original_index, item in item_entries:
        origin = _panel_origin(base, original_index)
        display_number = int(item.get("displayIndex", original_index + 11))
        expected_evidence = [
            f"仅写 {PREVIEW_LAYER} 图层",
            "创建句柄回读",
            "可见标注必须为中文",
            "已检查 / 未检查边界",
        ]
        if item["capabilityId"] == LINEWEIGHT_STANDARD_CAPABILITY_ID:
            expected_evidence.append("三档线宽与连续线 / 中心线 / 虚线必须回读")
        plan_items.append(
            {
                "index": display_number,
                "capabilityId": item["capabilityId"],
                "title": item["name"],
                "basePoint": origin,
                "focus": item.get("focus", ""),
                "expectedEvidence": expected_evidence,
            }
        )
    return {
        "schemaVersion": 1,
        "queueId": queue_id,
        "mode": batch_mode,
        "scope": scope,
        "replayMode": replay_mode,
        "adaptiveReplay": {
            "status": (adaptive_replay or {}).get("status", "disabled"),
            "itemCount": len((adaptive_replay or {}).get("items", [])),
            "doesNotUpdateProfile": True,
        },
        "trainingOptions": training_options or {},
        "basePoint": base,
        "items": plan_items,
        "safety": {
            "previewLayer": PREVIEW_LAYER,
            "saveDwg": False,
            "overwriteDwg": False,
            "deleteFormalEntities": False,
        },
    }


def _validate_plan(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ids = [str(item.get("capabilityId", "")) for item in plan.get("items", [])]
    expected_ids = plan.get("scope", {}).get("requestedCapabilityIds") or FOUNDATION_REMAINING_21_IDS
    if ids != expected_ids:
        errors.append("foundation item ids are out of requested order or incomplete")
    if plan.get("safety", {}).get("previewLayer") != PREVIEW_LAYER:
        errors.append("training batch must draw on CODEX_PREVIEW")
    for item in plan.get("items", []):
        if not item.get("basePoint"):
            errors.append(f"{item.get('capabilityId')} is missing basePoint")
    return errors


def _dry_run(plan: dict[str, Any]) -> dict[str, Any]:
    errors = _validate_plan(plan)
    entities = []
    for item in plan.get("items", []):
        x, y, z = item["basePoint"]
        entities.append(
            {
                "capabilityId": item["capabilityId"],
                "expectedLayer": PREVIEW_LAYER,
                "expectedPanelBBox": {
                    "min": [x, y - PANEL_HEIGHT],
                    "max": [x + PANEL_WIDTH, y],
                },
                "expectedEvidence": item["expectedEvidence"],
                "z": z,
            }
        )
    return {
        "schemaVersion": 1,
        "status": "invalid" if errors else "pass",
        "validation_errors": errors,
        "queueId": plan["queueId"],
        "itemCount": len(plan.get("items", [])),
        "entities": entities,
        "human_summary": f"{len(plan.get('items', []))} 项 CAD 基础操作训练面板 dry-run"
        if not errors
        else "INVALID TRAINING PLAN",
    }


def _run_timed(
    label: str,
    callback: Callable[[], Any],
    *,
    timeout_seconds: int,
    watchdog: list[dict[str, Any]],
    clock_fn: ClockFn = time.monotonic,
) -> Any:
    started = clock_fn()
    try:
        return callback()
    finally:
        elapsed = clock_fn() - started
        watchdog.append(
            {
                "step": label,
                "elapsedSeconds": round(elapsed, 3),
                "timeoutSeconds": timeout_seconds,
                "status": "timeout" if elapsed > timeout_seconds else "pass",
            }
        )


def _check(name: str, status: bool, message: str) -> dict[str, str]:
    return {"name": name, "status": "pass" if status else "fail", "message": message}


def _tool_call_granularity_report(
    *,
    requested_item_count: int,
    driver: Any,
    batch_log: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    batch_method_available = driver_declares_operation_batch(driver)
    observed_batch_calls = len(batch_log or [])
    return {
        "policy": "unified_quality_chain_latency_optimized",
        "minimumExternalSubmitUnit": "foundation_item",
        "preferredExternalSubmitUnit": "foundation_batch",
        "maxExternalSubmitCalls": max(1, int(requested_item_count)),
        "primitiveExternalCallsAllowed": False,
        "driverBatchMethodAvailable": batch_method_available,
        "actualSubmitUnit": "foundation_item" if batch_method_available else "primitive_fallback_internal_debug",
        "observedBatchSubmitCalls": observed_batch_calls,
        "reason": (
            "Training and formal drawing use the same quality chain; CAD calls are grouped at item/batch "
            "granularity so titles, frames, text, and sample geometry are not submitted as separate MCP units."
        ),
    }


def _lineweight_linetype_evidence(readback: list[dict[str, Any]]) -> dict[str, Any]:
    expected_lineweights = sorted(int(sample["lineweight"]) for sample in LINEWEIGHT_STANDARD_SAMPLES)
    expected_linetypes = sorted(str(sample["linetype"]).upper() for sample in LINEWEIGHT_STANDARD_SAMPLES)
    styled_lines = []
    for entity in readback:
        if entity.get("type") != "line":
            continue
        lineweight = entity.get("lineweight")
        linetype = entity.get("linetype")
        if lineweight is None or linetype is None:
            continue
        lineweight_value = int(lineweight)
        linetype_value = str(linetype).upper()
        if lineweight_value not in expected_lineweights or linetype_value not in expected_linetypes:
            continue
        styled_lines.append(
            {
                "handle": str(entity.get("handle", "")),
                "lineweight": lineweight_value,
                "linetype": linetype_value,
                "linetypeScale": float(entity.get("linetype_scale", 0.0)),
            }
        )
    actual_lineweights = sorted({int(entity["lineweight"]) for entity in styled_lines})
    actual_linetypes = sorted({str(entity["linetype"]).upper() for entity in styled_lines})
    actual_linetype_scales = sorted({round(float(entity["linetypeScale"]), 3) for entity in styled_lines})
    expected_linetype_scales = sorted({round(float(sample["linetype_scale"]), 3) for sample in LINEWEIGHT_STANDARD_SAMPLES})
    status = (
        actual_lineweights == expected_lineweights
        and actual_linetypes == expected_linetypes
        and actual_linetype_scales == expected_linetype_scales
    )
    return {
        "status": "pass" if status else "fail",
        "styledLineCount": len(styled_lines),
        "lineweights": actual_lineweights,
        "linetypes": actual_linetypes,
        "linetypeScales": actual_linetype_scales,
        "expectedLineweights": expected_lineweights,
        "expectedLinetypes": expected_linetypes,
        "expectedLinetypeScales": expected_linetype_scales,
        "styledLines": styled_lines,
        "message": f"lineweights={actual_lineweights} linetypes={actual_linetypes} linetype_scales={actual_linetype_scales}",
    }


def _adaptive_check_set(
    *,
    capability_profile: dict[str, Any],
    adaptive_replay: dict[str, Any],
    regression_guard: dict[str, Any],
    safety_boundaries: dict[str, Any],
) -> list[dict[str, str]]:
    return [
        _check(
            "adaptive_replay_profile_source",
            capability_profile.get("status") != "blocked",
            str(capability_profile.get("reason") or capability_profile.get("profileSource", {}).get("status", "")),
        ),
        _check(
            "adaptive_replay_plan",
            adaptive_replay.get("status") in {"disabled", "pass"},
            str(adaptive_replay.get("reason") or adaptive_replay.get("status", "")),
        ),
        _check(
            "expression_regression_guard",
            regression_guard.get("status") in {"not_applicable", "pass"},
            str(regression_guard.get("reason") or regression_guard.get("status", "")),
        ),
        _check(
            "worker_deploy_not_required",
            safety_boundaries.get("worker", {}).get("deployRequired") is False,
            "deployRequired=false",
        ),
    ]


def _blocked_adaptive_report(
    *,
    output_dir: Path,
    generated: str,
    queue_id: str,
    batch_mode: str,
    scope: dict[str, Any],
    replay_mode: str,
    batch_preset: str,
    artifact_prefix: str,
    capability_profile: dict[str, Any],
    adaptive_replay: dict[str, Any],
    regression_guard: dict[str, Any],
    safety_boundaries: dict[str, Any],
    blocked_reason: str,
) -> dict[str, Any]:
    report_path = output_dir / f"{artifact_prefix}_report.json"
    state_path = output_dir.parent / "queue_state.json"
    checks = _adaptive_check_set(
        capability_profile=capability_profile,
        adaptive_replay=adaptive_replay,
        regression_guard=regression_guard,
        safety_boundaries=safety_boundaries,
    )
    report = {
        "status": "blocked",
        "generated_at": generated,
        "active_document": "",
        "queueId": queue_id,
        "mode": str(scope.get("mode", "batch")),
        "batchMode": batch_mode,
        "scope": scope,
        "replayMode": replay_mode,
        "passType": "not_passed",
        "batchPreset": batch_preset,
        "capabilityProfile": capability_profile,
        "adaptiveReplay": adaptive_replay,
        "regressionGuard": regression_guard,
        "memoryWriteMode": "no_write",
        "claimBoundaries": [
            "adaptive_replay_blocked_before_cad_write",
            "not_training_acceptance",
            "not_growth_replay_pass",
        ],
        "safetyBoundaries": safety_boundaries,
        "timeoutSeconds": 30,
        "selfRecoveryAttempted": False,
        "circuitBreakerTriggered": False,
        "blockedReason": blocked_reason,
        "existing_preview_bbox_before": None,
        "parking_anchor": {"source": "not_run", "bbox": None, "basePoint": [0.0, 0.0, 0.0]},
        "batch_bbox": None,
        "created_handle_count": 0,
        "readback_count": 0,
        "actual_type_counts": {},
        "actual_layer_counts": {},
        "missing_handles": [],
        "streamingMode": {"enabled": False, "event_count": 0},
        "items": [],
        "checks": checks,
        "watchdog": [],
        "write_guard": {"status": "not_run", "reason": "adaptive replay blocked before CAD write"},
        "screenshotDecision": {"shouldCapture": False, "reason": "adaptive replay blocked before CAD write"},
        "visualPreview": {
            "status": "skipped",
            "role": "visual_aid_only",
            "reason": "adaptive replay blocked before CAD write",
        },
        "visual_self_check": {
            "status": "blocked",
            "preview_path": "",
            "review": "自适应训练在进入 CAD 写入前被安全边界阻断。",
            "remaining_visual_limits": "未执行 CAD 写入，截图不适用。",
        },
        "artifacts": {
            "training_plan": "",
            "dry_run": "",
            "execution_summary": "",
            "preview": "",
            "report": _artifact(report_path, output_dir),
        },
    }
    queue_state = {
        "schemaVersion": 1,
        "queueId": queue_id,
        "mode": str(scope.get("mode", "batch")),
        "batchMode": batch_mode,
        "scope": scope,
        "status": "blocked",
        "updatedAt": generated,
        "currentIndex": 0,
        "totalCount": len(scope.get("requestedCapabilityIds", [])),
        "completionEvidencePath": str(report_path),
        "items": [],
    }
    _write_json(report_path, report)
    _write_json(state_path, queue_state)
    return report


def run_foundation_remaining_training_batch(
    *,
    programs: list[dict[str, Any]],
    driver: Any,
    output_dir: Path,
    generated_at: str | None = None,
    timeout_seconds: int = 30,
    capture_preview: bool = True,
    selected_capability_ids: list[str] | None = None,
    scope_reason: str = "",
    training_options: dict[str, Any] | None = None,
    anchor_output_dir: Path | None = None,
    streaming_config: StreamingCadDemoConfig | None = None,
    sleep_fn: SleepFn | None = None,
    clock_fn: ClockFn | None = None,
    batch_preset: str = "remaining-21",
    replay_mode: str = "smoke_replay",
    profile_source: Path | None = None,
    allow_low_expression: bool = False,
    project_root: Path | None = None,
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = generated_at or _utc_now()
    config = _batch_config(batch_preset)
    capability_ids = list(config["ids"])
    queue_id = str(config["queueId"])
    batch_mode = str(config["mode"])
    artifact_prefix = str(config["artifactPrefix"])
    display_start = int(config["displayStart"])
    batch_label = str(config["label"])
    item_entries = _foundation_item_entries(
        programs,
        selected_capability_ids,
        capability_ids=capability_ids,
        display_start=display_start,
    )
    requested_ids = [str(item["capabilityId"]) for _, item in item_entries]
    scope_mode = "focused" if selected_capability_ids else "batch"
    scope = {
        "mode": scope_mode,
        "requestedCapabilityIds": requested_ids,
        "scopeReason": scope_reason,
        "fullBatchAllowed": not bool(selected_capability_ids),
        "rule": (
            "点名单项或子图样时只做轻量级 focused retraining；只有用户明确要求全部/整批/重新跑所有时才允许整批训练。"
            if selected_capability_ids
            else f"用户请求整批训练或未限制范围时，才执行{batch_label}。"
        ),
        "batchPreset": batch_preset,
    }
    capability_profile = build_capability_growth_profile(
        programs=programs,
        capability_ids=requested_ids,
        replay_mode=replay_mode,
        profile_source=profile_source,
        project_root=project_root or Path.cwd(),
        generated_at=generated,
    )
    if replay_mode != "smoke_replay" and capability_profile.get("status") != "blocked":
        profile_source_status = str(capability_profile.get("profileSource", {}).get("status", ""))
        default_profiles = [
            str(profile.get("capabilityId", ""))
            for profile in capability_profile.get("profiles", [])
            if isinstance(profile, dict) and profile.get("status") == "default"
        ]
        if profile_source_status != "pass":
            capability_profile = {
                **capability_profile,
                "status": "blocked",
                "reason": "profile_source_required_for_growth_or_standard_replay",
            }
        elif default_profiles:
            capability_profile = {
                **capability_profile,
                "status": "blocked",
                "reason": "generated_default_profile_used",
                "defaultProfileCapabilityIds": default_profiles,
            }
    adaptive_replay = build_adaptive_replay_plan(
        replay_mode=replay_mode,
        scope=scope,
        capability_profile=capability_profile,
        allow_low_expression=allow_low_expression,
    )
    regression_guard = evaluate_expression_regression_guard(
        adaptive_replay.get("items", []),
        replay_mode=replay_mode,
        allow_low_expression=allow_low_expression,
    )
    safety_boundaries = adaptive_replay.get("safetyBoundaries") or disabled_adaptive_replay_plan(
        replay_mode
    ).get("safetyBoundaries", {})
    if capability_profile.get("status") == "blocked" or adaptive_replay.get("status") == "blocked":
        blocked_reason = str(
            capability_profile.get("reason")
            or adaptive_replay.get("reason")
            or "adaptive_replay_blocked"
        )
        return _blocked_adaptive_report(
            output_dir=output_dir,
            generated=generated,
            queue_id=queue_id,
            batch_mode=batch_mode,
            scope=scope,
            replay_mode=replay_mode,
            batch_preset=batch_preset,
            artifact_prefix=artifact_prefix,
            capability_profile=capability_profile,
            adaptive_replay=adaptive_replay,
            regression_guard=regression_guard,
            safety_boundaries=safety_boundaries,
            blocked_reason=blocked_reason,
        )

    existing_entities = []
    if hasattr(driver, "snapshot_modelspace"):
        existing_entities = driver.snapshot_modelspace(layer=None)
    existing_bbox = _bbox_from_entities(existing_entities)
    parking_anchor = _parking_anchor(
        driver,
        Path(anchor_output_dir or output_dir),
        existing_bbox,
        artifact_prefix=artifact_prefix,
    )
    base = list(parking_anchor["basePoint"])

    plan = _build_plan(
        item_entries,
        base,
        scope=scope,
        training_options=training_options,
        queue_id=queue_id,
        batch_mode=batch_mode,
        replay_mode=replay_mode,
        adaptive_replay=adaptive_replay,
    )
    dry_run = _dry_run(plan)
    watchdog: list[dict[str, Any]] = []
    item_reports: list[dict[str, Any]] = []
    all_handles: list[str] = []
    blocked_reason = ""
    active_clock_fn = clock_fn or time.monotonic
    streaming_recorder = StreamingCadDemoRecorder(
        config=streaming_config or StreamingCadDemoConfig.disabled(),
        driver=driver,
        sleep_fn=sleep_fn or time.sleep,
        clock_fn=active_clock_fn,
    )
    adaptive_item_map = {
        str(item.get("capabilityId", "")): item
        for item in adaptive_replay.get("items", [])
        if isinstance(item, dict)
    }

    for original_index, item in item_entries:
        origin = _panel_origin(base, original_index)
        capability_id = str(item["capabilityId"])
        display_number = int(item.get("displayIndex", original_index + display_start))
        streaming_recorder.start_item(capability_id=capability_id, index=display_number)
        draw_watchdog_index = len(watchdog)
        before_draw_demo_delay = streaming_recorder.delay_seconds_total
        try:
            handles = _run_timed(
                f"draw:{capability_id}",
                lambda item=item, index=original_index, origin=origin: draw_foundation_item(
                    driver,
                    item,
                    index,
                    origin,
                    options=training_options,
                    streaming_recorder=streaming_recorder,
                ),
                timeout_seconds=timeout_seconds,
                watchdog=watchdog,
                clock_fn=active_clock_fn,
            )
        except Exception as exc:
            handles = []
            blocked_reason = f"{capability_id} failed: {exc}"
        finally:
            after_draw_demo_delay = streaming_recorder.delay_seconds_total
            draw_demo_delay = max(0.0, after_draw_demo_delay - before_draw_demo_delay)
            if len(watchdog) > draw_watchdog_index:
                draw_step = watchdog[-1]
                if draw_step.get("step") == f"draw:{capability_id}":
                    elapsed = float(draw_step.get("elapsedSeconds", 0.0))
                    net_elapsed = max(0.0, elapsed - draw_demo_delay)
                    draw_step["demoDelaySeconds"] = round(draw_demo_delay, 3)
                    draw_step["netElapsedSeconds"] = round(net_elapsed, 3)
                    draw_step["status"] = "timeout" if net_elapsed > timeout_seconds else "pass"
        all_handles.extend(handles)
        readback = driver.snapshot_handles(handles=handles, layer=PREVIEW_LAYER) if hasattr(driver, "snapshot_handles") else []
        style_evidence = (
            _lineweight_linetype_evidence(readback) if capability_id == LINEWEIGHT_STANDARD_CAPABILITY_ID else None
        )
        style_evidence_failed = bool(style_evidence and style_evidence.get("status") != "pass")
        item_blocked_reason = blocked_reason
        if style_evidence_failed:
            item_blocked_reason = (
                f"{capability_id} lineweight/linetype evidence failed: {style_evidence.get('message')}"
            )
            if not blocked_reason:
                blocked_reason = item_blocked_reason
        item_status = (
            "pass"
            if handles and len(readback) == len(set(handles)) and not item_blocked_reason
            else "blocked"
        )
        if item_status == "pass":
            streaming_recorder.after_item(handles, capability_id=capability_id)
        item_report = {
            "capabilityId": capability_id,
            "title": f"{display_number:02d} {item['name']}",
            "status": item_status,
            "handles": list(dict.fromkeys(handles)),
            "handle_count": len(set(handles)),
            "readback_count": len(readback),
            "feedback": "中文训练面板已生成；句柄已回读；全部在 CODEX_PREVIEW"
            if item_status == "pass"
            else item_blocked_reason,
            "focus": item.get("focus", ""),
        }
        if style_evidence is not None:
            item_report["styleEvidence"] = style_evidence
        if capability_id in adaptive_item_map:
            adaptive_item = adaptive_item_map[capability_id]
            item_report["adaptiveReplay"] = adaptive_item
            item_report["profileVersionUsed"] = adaptive_item.get("profileVersionUsed", "")
            item_report["consumedLessonIds"] = adaptive_item.get("consumedLessonIds", [])
            item_report["whyExpressionLevelChosen"] = adaptive_item.get("whyExpressionLevelChosen", "")
            item_report["acceptedLowExpression"] = bool(adaptive_item.get("acceptedLowExpression", False))
        item_reports.append(item_report)
        if blocked_reason:
            break

    all_handles = list(dict.fromkeys(all_handles))
    readback_entities = driver.snapshot_handles(handles=all_handles, layer=PREVIEW_LAYER) if hasattr(driver, "snapshot_handles") else []
    batch_bbox = _bbox_from_entities(readback_entities)
    type_counts = dict(Counter(str(entity.get("type", "unknown")) for entity in readback_entities))
    layer_counts = dict(Counter(str(entity.get("layer", "")) for entity in readback_entities))
    missing_handles = sorted(set(all_handles) - {str(entity.get("handle")) for entity in readback_entities})
    text_values = [str(entity.get("text", "")) for entity in readback_entities if entity.get("type") == "text"]
    english_label_terms = [text for text in text_values if _contains_latin_word(text)]
    guard_report = run_negative_write_guard_checks(driver)

    zoom_result: dict[str, Any] = {"status": "skipped", "reason": "capture_preview disabled"}
    if capture_preview and hasattr(driver, "zoom_to_handles"):
        try:
            zoom_result = _run_timed(
                "zoom_to_handles",
                lambda: driver.zoom_to_handles(handles=all_handles, layer=PREVIEW_LAYER),
                timeout_seconds=timeout_seconds,
                watchdog=watchdog,
                clock_fn=active_clock_fn,
            )
        except Exception as exc:
            zoom_result = {"status": "failed", "error": str(exc)}

    timed_out = [step for step in watchdog if step["status"] == "timeout"]
    if parking_anchor.get("source") == "global_preview_bbox":
        parking_anchor["source"] = "global_modelspace_bbox"
        parking_anchor["rule"] = "没有可回读的上一轮句柄时，退回到全模型空间 bbox 右侧空白区，避让旧训练层和正式画布内容。"
    non_overlap_reference_bbox = parking_anchor.get("bbox") if parking_anchor.get("source") == "previous_handles" else existing_bbox
    streaming_summary = streaming_recorder.summary()
    lineweight_style_reports = [
        item.get("styleEvidence", {})
        for item in item_reports
        if item.get("capabilityId") == LINEWEIGHT_STANDARD_CAPABILITY_ID
    ]
    lineweight_style_required = LINEWEIGHT_STANDARD_CAPABILITY_ID in requested_ids
    lineweight_style_pass = (
        not lineweight_style_required
        or bool(lineweight_style_reports)
        and all(report.get("status") == "pass" for report in lineweight_style_reports)
    )
    checks = [
        _check(
            "all_items_generated",
            len(item_reports) == len(requested_ids) and all(item["status"] == "pass" for item in item_reports),
            f"{len([item for item in item_reports if item['status'] == 'pass'])}/{len(requested_ids)}",
        ),
        _check(
            "persistent_handle_readback",
            bool(all_handles) and len(readback_entities) == len(all_handles) and not missing_handles,
            f"{len(readback_entities)}/{len(all_handles)}",
        ),
        _check(
            "preview_layer_only",
            bool(readback_entities) and set(layer_counts) == {PREVIEW_LAYER},
            f"layer_counts={layer_counts}",
        ),
        _check(
            "outside_existing_preview_bbox",
            not _bbox_overlap(non_overlap_reference_bbox, batch_bbox),
            f"batch bbox does not overlap {parking_anchor.get('source')} bbox",
        ),
        _check(
            "formal_layer_write_guard",
            guard_report.get("status") == "pass",
            f"blocked_attempts={guard_report.get('blocked_attempt_count', 0)}",
        ),
        _check(
            "dwg_not_saved",
            any(check.get("name") == "block_save" and check.get("status") == "pass" for check in guard_report.get("checks", [])),
            "save operation blocked by preview write guard",
        ),
        _check(
            "chinese_labels",
            len(text_values) >= len(item_reports)
            and all(_contains_cjk(text) for text in text_values)
            and not english_label_terms,
            f"text_labels={len(text_values)} latin_terms={len(english_label_terms)}",
        ),
        _check(
            "lineweight_linetype_standard",
            lineweight_style_pass,
            "not requested"
            if not lineweight_style_required
            else "; ".join(str(report.get("message", "")) for report in lineweight_style_reports),
        ),
        _check(
            "watchdog_no_timeout",
            not timed_out,
            f"timeouts={len(timed_out)} timeoutSeconds={timeout_seconds}",
        ),
        _check(
            "streaming_demo_mode",
            True,
            "enabled="
            + str(streaming_summary.get("enabled", False)).lower()
            + f" streaming_events={streaming_summary.get('event_count', 0)}"
            + f" operation_delays={streaming_summary.get('operation_delay_count', 0)}"
            + f" item_delays={streaming_summary.get('item_delay_count', 0)}"
            + f" measured_delay_seconds={streaming_summary.get('delaySecondsTotal', 0.0)}",
        ),
    ]
    checks.extend(
        _adaptive_check_set(
            capability_profile=capability_profile,
            adaptive_replay=adaptive_replay,
            regression_guard=regression_guard,
            safety_boundaries=safety_boundaries,
        )
    )
    status = "pass" if dry_run["status"] == "pass" and all(check["status"] == "pass" for check in checks) else "blocked"
    driver_batch_log = getattr(driver, "batch_execution_log", [])
    tool_call_granularity = _tool_call_granularity_report(
        requested_item_count=len(requested_ids),
        driver=driver,
        batch_log=driver_batch_log if isinstance(driver_batch_log, list) else [],
    )

    plan_path = output_dir / f"{artifact_prefix}_training_plan.json"
    dry_run_path = output_dir / f"{artifact_prefix}_dry_run.json"
    execution_summary_path = output_dir / f"{artifact_prefix}_execution_summary.json"
    preview_path = output_dir / f"{artifact_prefix}_preview.png"
    report_path = output_dir / f"{artifact_prefix}_report.json"
    state_path = output_dir.parent / "queue_state.json"

    execution_summary = {
        "status": status,
        "queueId": queue_id,
        "mode": scope_mode,
        "batchMode": batch_mode,
        "scope": scope,
        "replayMode": replay_mode,
        "passType": "smoke_only" if replay_mode == "smoke_replay" else replay_mode,
        "capabilityProfile": capability_profile,
        "adaptiveReplay": adaptive_replay,
        "regressionGuard": regression_guard,
        "memoryWriteMode": "no_write"
        if replay_mode == "smoke_replay" or scope_mode == "focused"
        else "merge_append_required",
        "safetyBoundaries": safety_boundaries,
        "trainingOptions": training_options or {},
        "generated_at": generated,
        "created_handles": all_handles,
        "created_handle_count": len(all_handles),
        "readback_count": len(readback_entities),
        "readback_entities": readback_entities,
        "batch_bbox": batch_bbox,
        "zoom": zoom_result,
        "streamingMode": streaming_summary,
        "toolCallGranularity": tool_call_granularity,
        "watchdog": watchdog,
        "output_dir": str(output_dir),
    }

    _write_json(execution_summary_path, execution_summary)
    visual_preview: dict[str, Any] = {
        "status": "skipped",
        "role": "visual_aid_only",
        "reason": "capture_preview disabled",
        "focus": {"status": "skipped"},
    }
    screenshot_decision = build_screenshot_decision(
        task_kind="focused_retraining" if scope_mode == "focused" else "training_batch",
        evidence_stage="focused_retraining" if scope_mode == "focused" else "formal_acceptance",
        execution_summary=execution_summary_path,
        capture_requested=capture_preview,
        key_readback_passed=status == "pass",
        formal_acceptance=scope_mode != "focused",
        agent_role="cad_designer",
    )
    visual_preview["screenshotDecision"] = screenshot_decision
    preview_rel_path = ""
    if capture_preview:
        try:
            capture_result = prepare_autocad_for_capture(
                preview_path,
                execution_summary=execution_summary_path,
                layer=PREVIEW_LAYER,
            )
            if not isinstance(capture_result.get("screenshotDecision"), dict):
                capture_result["screenshotDecision"] = screenshot_decision
            visual_preview = dict(capture_result.get("visualPreview") or visual_preview_payload(capture_result))
            visual_preview["screenshotDecision"] = capture_result.get("screenshotDecision", screenshot_decision)
            screenshot_decision = dict(visual_preview["screenshotDecision"])
            preview_rel_path = _artifact(preview_path, output_dir)
        except Exception as exc:
            visual_preview = {
                "status": "failed",
                "role": "visual_aid_only",
                "output": str(preview_path),
                "failure_category": "screenshot_failed",
                "message": str(exc),
                "focus": {"status": "unknown"},
                "screenshotDecision": screenshot_decision,
            }
    execution_summary["visualPreview"] = visual_preview
    execution_summary["screenshotDecision"] = screenshot_decision

    report = {
        "status": status,
        "generated_at": generated,
        "active_document": str(getattr(getattr(driver, "doc", None), "Name", "")),
        "queueId": queue_id,
        "mode": scope_mode,
        "batchMode": batch_mode,
        "scope": scope,
        "replayMode": replay_mode,
        "passType": "smoke_only" if replay_mode == "smoke_replay" else replay_mode,
        "capabilityProfile": capability_profile,
        "adaptiveReplay": adaptive_replay,
        "regressionGuard": regression_guard,
        "memoryWriteMode": "no_write"
        if replay_mode == "smoke_replay" or scope_mode == "focused"
        else "merge_append_required",
        "claimBoundaries": (
            ["smoke_only", "not_growth_replay", "not_formal_acceptance", "not_project_delivery_readiness"]
            if replay_mode == "smoke_replay"
            else ["profile_context_only", "current_pass_requires_created_handles_readback"]
        ),
        "safetyBoundaries": safety_boundaries,
        "trainingOptions": training_options or {},
        "timeoutSeconds": timeout_seconds,
        "selfRecoveryAttempted": bool(blocked_reason or timed_out),
        "circuitBreakerTriggered": bool(blocked_reason or len(timed_out) >= 2),
        "blockedReason": blocked_reason,
        "existing_preview_bbox_before": existing_bbox,
        "existing_context_bbox_before": existing_bbox,
        "parking_anchor": parking_anchor,
        "batch_bbox": batch_bbox,
        "created_handle_count": len(all_handles),
        "readback_count": len(readback_entities),
        "actual_type_counts": type_counts,
        "actual_layer_counts": layer_counts,
        "missing_handles": missing_handles,
        "streamingMode": streaming_summary,
        "toolCallGranularity": tool_call_granularity,
        "items": item_reports,
        "checks": checks,
        "watchdog": watchdog,
        "write_guard": guard_report,
        "screenshotDecision": screenshot_decision,
        "visualPreview": visual_preview,
        "visual_self_check": {
            "status": "pass" if status == "pass" else "blocked",
            "preview_path": preview_rel_path,
            "review": f"{len(requested_ids)} 项 CAD 基础操作中文面板已生成；句柄、边界框、图层守卫和已检查 / 未检查边界已完成机器自检。",
            "remaining_visual_limits": "截图只作目视辅助；训练通过仍以创建句柄回读、图层和检查项为准。",
        },
        "artifacts": {
            "training_plan": _artifact(plan_path, output_dir),
            "dry_run": _artifact(dry_run_path, output_dir),
            "execution_summary": _artifact(execution_summary_path, output_dir),
            "preview": _artifact(preview_path, output_dir) if preview_rel_path else "",
            "report": _artifact(report_path, output_dir),
        },
    }

    queue_state = {
        "schemaVersion": 1,
        "queueId": queue_id,
        "mode": scope_mode,
        "batchMode": batch_mode,
        "scope": scope,
        "replayMode": replay_mode,
        "adaptiveReplay": {
            "status": adaptive_replay.get("status"),
            "itemCount": len(adaptive_replay.get("items", [])),
        },
        "regressionGuard": {"status": regression_guard.get("status")},
        "status": "completed" if status == "pass" else "blocked",
        "updatedAt": generated,
        "currentIndex": len(item_reports),
        "totalCount": len(requested_ids),
        "completionEvidencePath": str(report_path),
        "items": [
            {
                "index": index,
                "capabilityId": item["capabilityId"],
                "name": item["title"],
                "status": "completed" if item["status"] == "pass" else item["status"],
                "decision": "pass" if item["status"] == "pass" else "blocked",
                "evidencePath": str(report_path),
            }
            for index, item in enumerate(item_reports)
        ],
    }

    _write_json(plan_path, plan)
    _write_json(dry_run_path, dry_run)
    _write_json(execution_summary_path, execution_summary)
    _write_json(report_path, report)
    _write_json(state_path, queue_state)
    return report
