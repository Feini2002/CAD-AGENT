"""Scene Registry loader and lookup for Core Orchestrator / Scene Router."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY_PATH = PROJECT_ROOT / "examples" / "orchestrator" / "scene_registry.json"

MATURITY_LEVELS = (
    "core_only",
    "scene_alpha",
    "scene_beta",
    "scene_product",
    "scaffold",
)

DEFAULT_SCENE_ID = "no_scene"


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_scene_registry(registry: dict[str, Any], *, project_root: Path | None = None) -> list[str]:
    """Semantic validation beyond JSON Schema."""

    errors: list[str] = []
    root = project_root or PROJECT_ROOT

    _require(str(registry.get("version", "")) == "0.1", "version must be 0.1.", errors)
    default_scene_id = str(registry.get("default_scene_id", ""))
    _require(default_scene_id == DEFAULT_SCENE_ID, f"default_scene_id must be {DEFAULT_SCENE_ID!r}.", errors)

    scenes = registry.get("scenes", [])
    _require(isinstance(scenes, list) and scenes, "scenes must be a non-empty array.", errors)
    if not isinstance(scenes, list):
        return errors

    seen_ids: set[str] = set()
    has_no_scene = False
    for index, scene in enumerate(scenes):
        prefix = f"scenes[{index}]"
        if not isinstance(scene, dict):
            errors.append(f"{prefix} must be an object.")
            continue
        scene_id = str(scene.get("scene_id", ""))
        _require(bool(scene_id), f"{prefix}.scene_id is required.", errors)
        if scene_id in seen_ids:
            errors.append(f"duplicate scene_id: {scene_id}")
        seen_ids.add(scene_id)
        if scene_id == DEFAULT_SCENE_ID:
            has_no_scene = True
            _require(scene.get("maturity") == "core_only", f"{scene_id} must have maturity=core_only.", errors)
            _require(not scene.get("trigger_terms"), f"{scene_id} must not define trigger_terms.", errors)

        _require(scene.get("may_bypass_core") is False, f"{prefix}.may_bypass_core must be false.", errors)
        _require(scene.get("auto_activate") is False, f"{prefix}.auto_activate must be false.", errors)

        maturity = str(scene.get("maturity", ""))
        if maturity not in MATURITY_LEVELS:
            errors.append(f"{prefix}.maturity is invalid.")

        if scene_id != DEFAULT_SCENE_ID:
            terms = scene.get("trigger_terms", [])
            _require(
                isinstance(terms, list) and len(terms) > 0,
                f"{prefix}.trigger_terms must be non-empty for scene modules.",
                errors,
            )

        preferences_path = scene.get("preferences_path")
        if isinstance(preferences_path, str) and preferences_path.strip():
            path = root / preferences_path
            if not path.is_file():
                errors.append(f"{prefix}.preferences_path does not exist: {preferences_path}")

        agent_dir = scene.get("agent_dir")
        if isinstance(agent_dir, str) and agent_dir.strip():
            path = root / agent_dir
            if not path.is_dir():
                errors.append(f"{prefix}.agent_dir does not exist: {agent_dir}")

    _require(has_no_scene, f"registry must include scene_id={DEFAULT_SCENE_ID!r}.", errors)
    _require(default_scene_id in seen_ids, "default_scene_id must reference a registered scene.", errors)

    required_ids = {"no_scene", "commercial_fitout", "residential", "restaurant", "office"}
    missing = required_ids - seen_ids
    if missing:
        errors.append(f"missing required scene ids: {', '.join(sorted(missing))}")

    return errors


def load_scene_registry(path: Path | None = None) -> dict[str, Any]:
    """Load and semantically validate the scene registry fixture."""

    registry_path = path or DEFAULT_REGISTRY_PATH
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    errors = validate_scene_registry(registry)
    if errors:
        raise ValueError("Invalid SCENE_REGISTRY: " + "; ".join(errors))
    return registry


def list_scene_ids(registry: dict[str, Any]) -> list[str]:
    scenes = registry.get("scenes", [])
    if not isinstance(scenes, list):
        return []
    return [str(scene["scene_id"]) for scene in scenes if isinstance(scene, dict) and scene.get("scene_id")]


def get_scene(registry: dict[str, Any], scene_id: str) -> dict[str, Any] | None:
    for scene in registry.get("scenes", []):
        if isinstance(scene, dict) and str(scene.get("scene_id")) == scene_id:
            return scene
    return None


def get_default_scene_id(registry: dict[str, Any]) -> str:
    return str(registry.get("default_scene_id", DEFAULT_SCENE_ID))


def scene_is_registered(registry: dict[str, Any], scene_id: str) -> bool:
    return get_scene(registry, scene_id) is not None


def scenes_by_maturity(registry: dict[str, Any], maturity: str) -> list[dict[str, Any]]:
    return [
        scene
        for scene in registry.get("scenes", [])
        if isinstance(scene, dict) and str(scene.get("maturity")) == maturity
    ]


def match_trigger_terms(registry: dict[str, Any], text: str) -> list[dict[str, Any]]:
    """Return scene records whose trigger_terms appear in text (case-insensitive)."""

    lowered = text.lower()
    matches: list[dict[str, Any]] = []
    for scene in registry.get("scenes", []):
        if not isinstance(scene, dict):
            continue
        if scene.get("scene_id") == DEFAULT_SCENE_ID:
            continue
        for term in scene.get("trigger_terms", []):
            if isinstance(term, str) and term.lower() in lowered:
                matches.append(scene)
                break
    return matches
