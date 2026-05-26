"""Lightweight scene-agent helpers (preferences contract only; no CAD execution)."""

from core.agents.scene_alpha import (
    SCENE_ALPHA_SCENARIOS,
    circulation_preferences_for_core,
    load_scene_preferences,
    observable_signature,
    preferred_circulation_strategy,
    validate_scene_alpha_preferences,
)
from core.agents.scene_beta import (
    SCENE_BETA_OFFICE_SCENARIO,
    SCENE_BETA_RESIDENTIAL_SCENARIO,
    SCENE_BETA_RESTAURANT_SCENARIO,
    load_scene_beta_office_preferences,
    load_scene_beta_residential_preferences,
    load_scene_beta_restaurant_preferences,
    validate_scene_beta_office_preferences,
    validate_scene_beta_residential_preferences,
    validate_scene_beta_restaurant_preferences,
)

__all__ = [
    "SCENE_ALPHA_SCENARIOS",
    "SCENE_BETA_OFFICE_SCENARIO",
    "SCENE_BETA_RESIDENTIAL_SCENARIO",
    "SCENE_BETA_RESTAURANT_SCENARIO",
    "circulation_preferences_for_core",
    "load_scene_preferences",
    "load_scene_beta_office_preferences",
    "load_scene_beta_residential_preferences",
    "load_scene_beta_restaurant_preferences",
    "observable_signature",
    "preferred_circulation_strategy",
    "validate_scene_alpha_preferences",
    "validate_scene_beta_office_preferences",
    "validate_scene_beta_residential_preferences",
    "validate_scene_beta_restaurant_preferences",
]
