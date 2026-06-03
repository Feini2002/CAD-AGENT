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
from core.training.foundation_panel_drawings import (
    LINEWEIGHT_STANDARD_SAMPLES,
    PANEL_COLUMNS,
    PANEL_GAP,
    PANEL_HEIGHT,
    PANEL_WIDTH,
    draw_foundation_item,
)
from core.training.streaming_demo import ClockFn, SleepFn, StreamingCadDemoConfig, StreamingCadDemoRecorder
from core.verification.render_preview import build_screenshot_decision, prepare_autocad_for_capture, visual_preview_payload


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


def _previous_training_handles(output_dir: Path) -> list[str]:
    summary = _read_json(output_dir / "remaining_21_execution_summary.json")
    handles = summary.get("created_handles")
    if not isinstance(handles, list):
        return []
    return [str(handle) for handle in handles if handle]


def _program_map(programs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(program.get("capabilityId", "")): program for program in programs}


def foundation_remaining_programs(programs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = _program_map(programs)
    missing = [capability_id for capability_id in FOUNDATION_REMAINING_21_IDS if capability_id not in by_id]
    if missing:
        raise ValueError(f"training programs missing from workbench data: {missing}")
    return [by_id[capability_id] for capability_id in FOUNDATION_REMAINING_21_IDS]


def _foundation_item_entries(
    programs: list[dict[str, Any]],
    selected_capability_ids: list[str] | None = None,
) -> list[tuple[int, dict[str, Any]]]:
    items = foundation_remaining_programs(programs)
    by_id = {str(item["capabilityId"]): (index, item) for index, item in enumerate(items)}
    if not selected_capability_ids:
        return list(enumerate(items))
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


def _parking_anchor(driver: Any, output_dir: Path, existing_bbox: dict[str, list[float]] | None) -> dict[str, Any]:
    previous_handles = _previous_training_handles(output_dir)
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
) -> dict[str, Any]:
    plan_items = []
    for original_index, item in item_entries:
        origin = _panel_origin(base, original_index)
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
                "index": original_index + 11,
                "capabilityId": item["capabilityId"],
                "title": item["name"],
                "basePoint": origin,
                "focus": item.get("focus", ""),
                "expectedEvidence": expected_evidence,
            }
        )
    return {
        "schemaVersion": 1,
        "queueId": QUEUE_ID,
        "mode": MODE,
        "scope": scope,
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
        errors.append("remaining foundation item ids are out of requested order or incomplete")
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
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = generated_at or _utc_now()
    item_entries = _foundation_item_entries(programs, selected_capability_ids)
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
            else "用户请求整批训练或未限制范围时，才执行完整 21 项批量训练。"
        ),
    }

    existing_entities = []
    if hasattr(driver, "snapshot_modelspace"):
        existing_entities = driver.snapshot_modelspace(layer=PREVIEW_LAYER)
    existing_bbox = _bbox_from_entities(existing_entities)
    parking_anchor = _parking_anchor(driver, Path(anchor_output_dir or output_dir), existing_bbox)
    base = list(parking_anchor["basePoint"])

    plan = _build_plan(item_entries, base, scope=scope, training_options=training_options)
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

    for original_index, item in item_entries:
        origin = _panel_origin(base, original_index)
        capability_id = str(item["capabilityId"])
        streaming_recorder.start_item(capability_id=capability_id, index=original_index + 11)
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
            "title": f"{original_index + 11:02d} {item['name']}",
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
    status = "pass" if dry_run["status"] == "pass" and all(check["status"] == "pass" for check in checks) else "blocked"

    plan_path = output_dir / "remaining_21_training_plan.json"
    dry_run_path = output_dir / "remaining_21_dry_run.json"
    execution_summary_path = output_dir / "remaining_21_execution_summary.json"
    preview_path = output_dir / "remaining_21_preview.png"
    report_path = output_dir / "remaining_21_report.json"
    state_path = output_dir.parent / "queue_state.json"

    execution_summary = {
        "status": status,
        "queueId": QUEUE_ID,
        "mode": scope_mode,
        "batchMode": MODE,
        "scope": scope,
        "trainingOptions": training_options or {},
        "generated_at": generated,
        "created_handles": all_handles,
        "created_handle_count": len(all_handles),
        "readback_count": len(readback_entities),
        "readback_entities": readback_entities,
        "batch_bbox": batch_bbox,
        "zoom": zoom_result,
        "streamingMode": streaming_summary,
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
        "queueId": QUEUE_ID,
        "mode": scope_mode,
        "batchMode": MODE,
        "scope": scope,
        "trainingOptions": training_options or {},
        "timeoutSeconds": timeout_seconds,
        "selfRecoveryAttempted": bool(blocked_reason or timed_out),
        "circuitBreakerTriggered": bool(blocked_reason or len(timed_out) >= 2),
        "blockedReason": blocked_reason,
        "existing_preview_bbox_before": existing_bbox,
        "parking_anchor": parking_anchor,
        "batch_bbox": batch_bbox,
        "created_handle_count": len(all_handles),
        "readback_count": len(readback_entities),
        "actual_type_counts": type_counts,
        "actual_layer_counts": layer_counts,
        "missing_handles": missing_handles,
        "streamingMode": streaming_summary,
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
        "queueId": QUEUE_ID,
        "mode": scope_mode,
        "batchMode": MODE,
        "scope": scope,
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
