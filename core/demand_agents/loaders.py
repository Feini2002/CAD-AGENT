"""Load and validate data-only demand-side role Agent records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.path_safety import validate_safe_path_segment


CURRENT_SCENE_IDS = {
    "residential",
    "office",
    "restaurant",
    "commercial_fitout",
    "exhibition",
    "custom",
}

SUPPORTED_TARGET_PIPELINES = {"object_spec", "object_detail_spec", "composition_spec", "blank_shell"}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return data


def _require_non_empty_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string.")
    return value


def _require_non_empty_string_list(value: object, *, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty string list.")
    items: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{label}[{index}] must be a non-empty string.")
        items.append(item)
    return items


def _validate_agent(agent: Any, *, label: str) -> dict[str, Any]:
    if not isinstance(agent, dict):
        raise ValueError(f"{label} must be an object.")
    agent_id = validate_safe_path_segment(agent.get("agent_id"), label=f"{label}.agent_id")
    scene_id = validate_safe_path_segment(agent.get("scene_id"), label=f"{label}.scene_id")
    if scene_id not in CURRENT_SCENE_IDS:
        raise ValueError(f"{label}.scene_id is not supported: {scene_id}")
    role_name = _require_non_empty_string(agent.get("role_name"), label=f"{label}.role_name")
    user_level = _require_non_empty_string(agent.get("user_level"), label=f"{label}.user_level")
    demand_focus = _require_non_empty_string_list(agent.get("demand_focus"), label=f"{label}.demand_focus")
    sample_requests = _require_non_empty_string_list(
        agent.get("sample_requests"),
        label=f"{label}.sample_requests",
    )
    core_targets = _require_non_empty_string_list(
        agent.get("core_capability_targets"),
        label=f"{label}.core_capability_targets",
    )
    return {
        **agent,
        "agent_id": agent_id,
        "scene_id": scene_id,
        "role_name": role_name,
        "user_level": user_level,
        "demand_focus": demand_focus,
        "sample_requests": sample_requests,
        "core_capability_targets": core_targets,
    }


def load_demand_agent_registry(path: Path) -> dict[str, Any]:
    data = _load_json(path)
    agents = data.get("agents")
    if not isinstance(agents, list) or not agents:
        raise ValueError("demand agent registry must contain a non-empty agents list.")
    validated = [_validate_agent(agent, label=f"agents[{index}]") for index, agent in enumerate(agents)]
    ids = [agent["agent_id"] for agent in validated]
    if len(ids) != len(set(ids)):
        raise ValueError("demand agent registry contains duplicate agent_id values.")
    return {**data, "agents": validated}


def summarize_scene_coverage(registry: dict[str, Any]) -> dict[str, int]:
    coverage: dict[str, int] = {}
    for agent in registry.get("agents", []):
        if not isinstance(agent, dict):
            continue
        scene_id = str(agent.get("scene_id", ""))
        if scene_id:
            coverage[scene_id] = coverage.get(scene_id, 0) + 1
    return dict(sorted(coverage.items()))


def demand_agent_by_id(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(agent["agent_id"]): agent
        for agent in registry.get("agents", [])
        if isinstance(agent, dict) and agent.get("agent_id")
    }


def _validate_demand_case(case: Any, *, label: str, agents_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(case, dict):
        raise ValueError(f"{label} must be an object.")
    if case.get("pipeline") != "demand_case":
        raise ValueError(f"{label}.pipeline must be demand_case.")
    case_id = validate_safe_path_segment(case.get("case_id"), label=f"{label}.case_id")
    demand_agent_id = validate_safe_path_segment(
        case.get("demand_agent_id"),
        label=f"{label}.demand_agent_id",
    )
    if demand_agent_id not in agents_by_id:
        raise ValueError(f"{label}.unknown demand_agent_id: {demand_agent_id}")
    target_pipeline = _require_non_empty_string(
        case.get("target_pipeline"),
        label=f"{label}.target_pipeline",
    )
    if target_pipeline not in SUPPORTED_TARGET_PIPELINES:
        raise ValueError(f"{label}.target_pipeline is not supported: {target_pipeline}")
    request_text = _require_non_empty_string(case.get("request_text"), label=f"{label}.request_text")
    core_targets = _require_non_empty_string_list(
        case.get("core_capability_targets"),
        label=f"{label}.core_capability_targets",
    )
    return {
        **case,
        "case_id": case_id,
        "demand_agent_id": demand_agent_id,
        "scene_id": agents_by_id[demand_agent_id]["scene_id"],
        "target_pipeline": target_pipeline,
        "request_text": request_text,
        "core_capability_targets": core_targets,
    }


def load_demand_cases(path: Path, *, registry: dict[str, Any]) -> list[dict[str, Any]]:
    data = _load_json(path)
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("demand benchmark suite must contain a non-empty cases list.")
    agents_by_id = demand_agent_by_id(registry)
    demand_cases = [case for case in cases if isinstance(case, dict) and case.get("pipeline") == "demand_case"]
    if not demand_cases:
        raise ValueError("demand benchmark suite must contain at least one demand_case.")
    return [
        _validate_demand_case(case, label=f"cases[{index}]", agents_by_id=agents_by_id)
        for index, case in enumerate(demand_cases)
    ]
