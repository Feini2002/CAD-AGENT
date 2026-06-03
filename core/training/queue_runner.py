from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


CAD_FOUNDATION_FIRST_10 = [
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

QUEUE_PRESETS = {
    "cad-foundation-first-10": CAD_FOUNDATION_FIRST_10,
}


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _program_by_id(programs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(program["capabilityId"]): program for program in programs}


def _item_from_program(program: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "index": index,
        "capabilityId": program["capabilityId"],
        "programId": program["id"],
        "name": program["name"],
        "group": program["group"],
        "priority": program["priority"],
        "nextTrainingTarget": program["nextTrainingTarget"],
        "focus": program["focus"],
        "status": "pending",
        "decision": "",
        "feedback": "",
        "reviewChecklist": review_checklist(program),
    }


def review_checklist(program: dict[str, Any]) -> list[str]:
    name = program["name"]
    return [
        f"确认本项训练目标是否对：{name} / {program['nextTrainingTarget']}。",
        "如果已经真实落图，检查是否只写 CODEX_PREVIEW，且没有污染正式图层。",
        "检查 created handles、entity type、bbox、关键端点、闭合 / gap / open endpoint 是否可回读。",
        "如果你目视不满意，直接在 Codex 对话框说“记反馈：……”并描述不准点。",
    ]


def build_training_queue(
    programs: list[dict[str, Any]],
    *,
    preset: str = "cad-foundation-first-10",
    mode: str = "supervised",
) -> dict[str, Any]:
    if preset not in QUEUE_PRESETS:
        raise ValueError(f"unknown training queue preset: {preset}")
    if mode != "supervised":
        raise ValueError("training queue v1 only supports supervised mode")

    programs_by_id = _program_by_id(programs)
    missing = [capability_id for capability_id in QUEUE_PRESETS[preset] if capability_id not in programs_by_id]
    if missing:
        raise ValueError(f"training programs missing from workbench data: {missing}")

    now = _utc_now()
    items = [_item_from_program(programs_by_id[capability_id], index) for index, capability_id in enumerate(QUEUE_PRESETS[preset])]
    return {
        "schemaVersion": 1,
        "queueId": preset,
        "preset": preset,
        "mode": mode,
        "status": "ready",
        "createdAt": now,
        "updatedAt": now,
        "currentIndex": 0,
        "items": items,
        "latestPause": {},
    }


def load_queue_state(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_queue_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updatedAt"] = _utc_now()
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _current_item(state: dict[str, Any]) -> dict[str, Any] | None:
    index = int(state.get("currentIndex", 0))
    items = state.get("items", [])
    if index >= len(items):
        return None
    return items[index]


def _advance_to_next_pending(state: dict[str, Any]) -> dict[str, Any] | None:
    items = state["items"]
    for index, item in enumerate(items):
        if item["status"] == "pending":
            state["currentIndex"] = index
            return item
    state["currentIndex"] = len(items)
    state["status"] = "completed"
    return None


def _pause_item(state: dict[str, Any], item: dict[str, Any]) -> None:
    item["status"] = "paused_for_human"
    state["status"] = "paused_for_human"
    state["latestPause"] = {
        "capabilityId": item["capabilityId"],
        "name": item["name"],
        "reason": "human_review_required",
        "reviewChecklist": item["reviewChecklist"],
    }


def _next_command(state_path: Path, decision: str = "pass") -> str:
    return f"$py scripts\\run_training_queue.py --state \"{state_path}\" --decision {decision}"


def _paused_message(item: dict[str, Any], state_path: Path) -> str:
    checklist = "\n".join(f"{idx}. {line}" for idx, line in enumerate(item["reviewChecklist"], start=1))
    return (
        f"队列已暂停在第 {item['index'] + 1} 项：{item['name']}。\n"
        f"训练目标：{item['nextTrainingTarget']}\n\n"
        "请在 Codex 对话框按下面内容验收：\n"
        f"{checklist}\n\n"
        "如果通过，运行：\n"
        f"{_next_command(state_path, 'pass')}\n"
        "如果不准，直接告诉我“记反馈：哪里不对”，或运行：\n"
        f"{_next_command(state_path, 'fail')}"
    )


def _blocked_message(item: dict[str, Any], feedback: str) -> str:
    return (
        f"队列已在第 {item['index'] + 1} 项阻塞：{item['name']}。\n"
        f"你记录的不准点：{feedback or '未填写。'}\n"
        "下一步请在 Codex 对话框说“记反馈：……”并补充具体不准点，我会先修本项，再恢复队列。"
    )


def _report(state: dict[str, Any], state_path: Path, message: str) -> dict[str, Any]:
    item = _current_item(state)
    return {
        "status": state["status"],
        "queueId": state["queueId"],
        "statePath": str(state_path),
        "currentIndex": state["currentIndex"],
        "totalCount": len(state["items"]),
        "currentItem": item or {},
        "humanMessage": message,
        "nextCommand": _next_command(state_path, "pass") if item else "",
    }


def run_training_queue_step(
    programs: list[dict[str, Any]],
    *,
    state_path: Path,
    preset: str = "cad-foundation-first-10",
    mode: str = "supervised",
    decision: str | None = None,
    feedback: str = "",
    reset: bool = False,
) -> dict[str, Any]:
    state = None if reset else load_queue_state(state_path)
    if state is None:
        state = build_training_queue(programs, preset=preset, mode=mode)

    item = _current_item(state)
    if item is None:
        state["status"] = "completed"
        write_queue_state(state_path, state)
        return _report(state, state_path, "训练队列已经全部完成。")

    if item["status"] == "paused_for_human":
        if decision == "pass":
            item["status"] = "completed"
            item["decision"] = "pass"
            item["feedback"] = feedback
            item = _advance_to_next_pending(state)
            if item is None:
                write_queue_state(state_path, state)
                return _report(state, state_path, "训练队列已经全部完成。")
        elif decision == "fail":
            item["status"] = "blocked"
            item["decision"] = "fail"
            item["feedback"] = feedback
            state["status"] = "blocked"
            write_queue_state(state_path, state)
            return _report(state, state_path, _blocked_message(item, feedback))
        elif decision:
            raise ValueError("decision must be pass or fail")
        else:
            write_queue_state(state_path, state)
            return _report(state, state_path, _paused_message(item, state_path))

    if item["status"] == "blocked":
        state["status"] = "blocked"
        write_queue_state(state_path, state)
        return _report(state, state_path, _blocked_message(item, item.get("feedback", "")))

    if item["status"] == "pending":
        _pause_item(state, item)
        write_queue_state(state_path, state)
        return _report(state, state_path, _paused_message(item, state_path))

    item = _advance_to_next_pending(state)
    if item is None:
        write_queue_state(state_path, state)
        return _report(state, state_path, "训练队列已经全部完成。")
    _pause_item(state, item)
    write_queue_state(state_path, state)
    return _report(state, state_path, _paused_message(item, state_path))
