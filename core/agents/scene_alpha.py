"""Scene Alpha preferences contract (X-SCENE-01)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCENE_ALPHA_SCENARIOS: tuple[str, ...] = ("office", "residential", "restaurant")

REQUIRED_PREFERENCE_KEYS: tuple[str, ...] = (
    "version",
    "scenario",
    "preview_layer",
    "object_preferences",
    "circulation",
    "layout_weights",
    "scene_alpha",
)


def load_scene_preferences(scenario: str, *, root: Path) -> dict[str, Any]:
    if scenario not in SCENE_ALPHA_SCENARIOS:
        raise ValueError(f"unknown scene alpha scenario: {scenario}")
    path = root / "agents" / scenario / "preferences.json"
    if not path.is_file():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a JSON object")
    return data


def circulation_preferences_for_core(preferences: dict[str, Any]) -> dict[str, Any]:
    """Merge circulation block with layout_weights for Core layout/circulation entrypoints."""

    circulation = preferences.get("circulation", {})
    if not isinstance(circulation, dict):
        return {}
    merged = dict(circulation)
    layout_weights = preferences.get("layout_weights", {})
    if isinstance(layout_weights, dict):
        merged.setdefault("layout_weights", layout_weights)
    return merged


def observable_signature(preferences: dict[str, Any]) -> dict[str, Any]:
    circulation = preferences.get("circulation", {})
    if not isinstance(circulation, dict):
        circulation = {}
    object_preferences = preferences.get("object_preferences", [])
    layout_weights = preferences.get("layout_weights", {})
    strategy_weights = circulation.get("circulation_strategy_weights", {})
    return {
        "scenario": str(preferences.get("scenario", "")),
        "primary_object_type": str(object_preferences[0]) if object_preferences else "",
        "main_aisle_width_mm": int(circulation.get("main_aisle_width_mm", 0)),
        "secondary_aisle_width_mm": int(circulation.get("secondary_aisle_width_mm", 0)),
        "layout_weight_keys": tuple(sorted(layout_weights.keys())) if isinstance(layout_weights, dict) else (),
        "preferred_circulation_strategy": preferred_circulation_strategy(strategy_weights),
    }


def preferred_circulation_strategy(strategy_weights: dict[str, Any]) -> str:
    if not strategy_weights:
        return ""
    return max(
        strategy_weights.keys(),
        key=lambda key: float(strategy_weights.get(key, 0)),
    )


def validate_scene_alpha_preferences(preferences: dict[str, Any], *, scenario: str) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_PREFERENCE_KEYS:
        if key not in preferences:
            errors.append(f"{scenario}: missing {key}")
    scene_alpha = preferences.get("scene_alpha")
    if not isinstance(scene_alpha, dict) or scene_alpha.get("tier") != "alpha":
        errors.append(f"{scenario}: scene_alpha.tier must be 'alpha'")
    circulation = preferences.get("circulation", {})
    if not isinstance(circulation, dict):
        errors.append(f"{scenario}: circulation must be an object")
    elif not isinstance(circulation.get("circulation_strategy_weights"), dict):
        errors.append(f"{scenario}: circulation.circulation_strategy_weights required")
    return errors


def assert_alpha_preferences_distinct(signatures: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    scenarios = list(signatures.keys())
    for index, left in enumerate(scenarios):
        for right in scenarios[index + 1 :]:
            left_sig = signatures[left]
            right_sig = signatures[right]
            if left_sig == right_sig:
                errors.append(f"{left} and {right} have identical observable preference signatures")
            if left_sig["primary_object_type"] == right_sig["primary_object_type"]:
                errors.append(f"{left} and {right} share primary_object_type={left_sig['primary_object_type']!r}")
            if left_sig["preferred_circulation_strategy"] == right_sig["preferred_circulation_strategy"]:
                errors.append(
                    f"{left} and {right} share preferred_circulation_strategy="
                    f"{left_sig['preferred_circulation_strategy']!r}"
                )
    return errors
