"""Scene Beta preferences contract (BETA-SCENE-01 office, BETA-SCENE-02 residential)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.agents.scene_alpha import (
    circulation_preferences_for_core,
    load_scene_preferences,
    observable_signature,
    preferred_circulation_strategy,
)

SCENE_BETA_OFFICE_SCENARIO = "office"
SCENE_BETA_RESIDENTIAL_SCENARIO = "residential"
SCENE_BETA_RESTAURANT_SCENARIO = "restaurant"
BETA_TIER = "beta"
OFFICE_BENCHMARK_REL = Path("examples/benchmarks/office_scene_beta_benchmark.json")
RESIDENTIAL_BENCHMARK_REL = Path("examples/benchmarks/residential_scene_beta_benchmark.json")
RESTAURANT_BENCHMARK_REL = Path("examples/benchmarks/restaurant_scene_beta_benchmark.json")


def default_office_scene_beta_benchmark_path(project_root: Path) -> Path:
    return project_root / OFFICE_BENCHMARK_REL


def default_residential_scene_beta_benchmark_path(project_root: Path) -> Path:
    return project_root / RESIDENTIAL_BENCHMARK_REL


def default_restaurant_scene_beta_benchmark_path(project_root: Path) -> Path:
    return project_root / RESTAURANT_BENCHMARK_REL


def load_scene_beta_preferences(scenario: str, *, root: Path) -> dict[str, Any]:
    if scenario not in {
        SCENE_BETA_OFFICE_SCENARIO,
        SCENE_BETA_RESIDENTIAL_SCENARIO,
        SCENE_BETA_RESTAURANT_SCENARIO,
    }:
        raise ValueError(f"unsupported scene beta scenario: {scenario}")
    return load_scene_preferences(scenario, root=root)


def load_scene_beta_office_preferences(*, root: Path) -> dict[str, Any]:
    return load_scene_beta_preferences(SCENE_BETA_OFFICE_SCENARIO, root=root)


def load_scene_beta_residential_preferences(*, root: Path) -> dict[str, Any]:
    return load_scene_beta_preferences(SCENE_BETA_RESIDENTIAL_SCENARIO, root=root)


def load_scene_beta_restaurant_preferences(*, root: Path) -> dict[str, Any]:
    return load_scene_beta_preferences(SCENE_BETA_RESTAURANT_SCENARIO, root=root)


def _validate_scene_beta_base(
    preferences: dict[str, Any],
    *,
    scenario: str,
    benchmark_rel: Path,
    required_object_types: set[str],
    preferred_strategy: str,
    min_object_preferences: int = 3,
) -> list[str]:
    errors: list[str] = []
    if str(preferences.get("scenario", "")) != scenario:
        errors.append(f"scenario must be {scenario!r}")
    scene_beta = preferences.get("scene_beta")
    if not isinstance(scene_beta, dict) or scene_beta.get("tier") != BETA_TIER:
        errors.append("scene_beta.tier must be 'beta'")
    suite = scene_beta.get("benchmark_suite") if isinstance(scene_beta, dict) else None
    if suite != benchmark_rel.as_posix():
        errors.append(f"scene_beta.benchmark_suite must be {benchmark_rel.as_posix()!r}")
    object_prefs = preferences.get("object_preferences", [])
    if not isinstance(object_prefs, list) or len(object_prefs) < min_object_preferences:
        errors.append(f"object_preferences must list at least {min_object_preferences} types")
    if not required_object_types.issubset({str(item) for item in object_prefs}):
        errors.append(f"object_preferences must include {sorted(required_object_types)}")
    circulation = preferences.get("circulation", {})
    if isinstance(circulation, dict):
        weights = circulation.get("circulation_strategy_weights", {})
        if preferred_circulation_strategy(weights) != preferred_strategy:
            errors.append(f"{scenario} beta must prefer {preferred_strategy} circulation")
    return errors


def validate_scene_beta_office_preferences(preferences: dict[str, Any]) -> list[str]:
    return _validate_scene_beta_base(
        preferences,
        scenario=SCENE_BETA_OFFICE_SCENARIO,
        benchmark_rel=OFFICE_BENCHMARK_REL,
        required_object_types={"table", "cabinet", "computer_desk"},
        preferred_strategy="straight_spine",
        min_object_preferences=6,
    )


def validate_scene_beta_residential_preferences(preferences: dict[str, Any]) -> list[str]:
    return _validate_scene_beta_base(
        preferences,
        scenario=SCENE_BETA_RESIDENTIAL_SCENARIO,
        benchmark_rel=RESIDENTIAL_BENCHMARK_REL,
        required_object_types={"cabinet", "sofa", "bed", "shelf"},
        preferred_strategy="along_wall",
        min_object_preferences=6,
    )


def validate_scene_beta_restaurant_preferences(preferences: dict[str, Any]) -> list[str]:
    return _validate_scene_beta_base(
        preferences,
        scenario=SCENE_BETA_RESTAURANT_SCENARIO,
        benchmark_rel=RESTAURANT_BENCHMARK_REL,
        required_object_types={"chair", "table", "counter"},
        preferred_strategy="l_spine",
        min_object_preferences=4,
    )


def scene_beta_observable_signature(preferences: dict[str, Any]) -> dict[str, Any]:
    signature = observable_signature(preferences)
    scene_beta = preferences.get("scene_beta", {})
    return {
        **signature,
        "tier": str(scene_beta.get("tier", "")) if isinstance(scene_beta, dict) else "",
        "benchmark_suite": str(scene_beta.get("benchmark_suite", "")) if isinstance(scene_beta, dict) else "",
        "object_preference_count": len(preferences.get("object_preferences", [])),
    }


def office_beta_observable_signature(preferences: dict[str, Any]) -> dict[str, Any]:
    return scene_beta_observable_signature(preferences)


def residential_beta_observable_signature(preferences: dict[str, Any]) -> dict[str, Any]:
    return scene_beta_observable_signature(preferences)


def office_beta_preferences_for_core(*, root: Path) -> dict[str, Any]:
    return circulation_preferences_for_core(load_scene_beta_office_preferences(root=root))


def residential_beta_preferences_for_core(*, root: Path) -> dict[str, Any]:
    return circulation_preferences_for_core(load_scene_beta_residential_preferences(root=root))


def restaurant_beta_preferences_for_core(*, root: Path) -> dict[str, Any]:
    return circulation_preferences_for_core(load_scene_beta_restaurant_preferences(root=root))
