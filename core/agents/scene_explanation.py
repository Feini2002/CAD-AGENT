"""Scene Alpha explanation helpers (X-SCENE-04)."""

from __future__ import annotations

from typing import Any

from core.agents.scene_alpha import observable_signature, preferred_circulation_strategy

RULES_SECTION_PREFERENCE_CORE = "## Preference → Core Mapping"
RULES_SECTION_NOT_CLAIM = "## What Scene Alpha Does Not Claim"

CORE_EFFECT_NOT_CLAIMS: tuple[str, ...] = (
    "Does not prove geometry_verified or real-project CAD accuracy.",
    "Does not replace block library, collision engine, or blank-shell pipeline implementation.",
    "Does not bypass validate, dry-run, CODEX_PREVIEW, or VERIFICATION_REPORT.",
)


def build_scene_explanation(preferences: dict[str, Any]) -> dict[str, Any]:
    """Structured explanation of how scene preferences steer Core (not an Agent brain)."""

    circulation = preferences.get("circulation", {})
    if not isinstance(circulation, dict):
        circulation = {}
    object_preferences = preferences.get("object_preferences", [])
    strategy_weights = circulation.get("circulation_strategy_weights", {})
    if not isinstance(strategy_weights, dict):
        strategy_weights = {}
    signature = observable_signature(preferences)

    return {
        "version": "0.1",
        "scenario": str(preferences.get("scenario", "")),
        "role": "scene_preference_layer",
        "summary": (
            "Scene preferences adjust Core circulation width, strategy weights, and object priority; "
            "Core blank_shell pipeline performs zone split, placement, proposal, and CAD_PLAN generation."
        ),
        "observable_signature": signature,
        "preference_to_core": [
            {
                "preference": "circulation.main_aisle_width_mm",
                "core_entry": "core.layout_engine.path_generation.generate_circulation_candidates",
                "effect": "Sets main aisle strip width for circulation candidates.",
                "observable": circulation.get("main_aisle_width_mm"),
            },
            {
                "preference": "circulation.secondary_aisle_width_mm",
                "core_entry": "core.layout_engine.basic_layout.create_layout_candidates",
                "effect": "Feeds object spacing / clearance in layout candidates.",
                "observable": circulation.get("secondary_aisle_width_mm"),
            },
            {
                "preference": "circulation.circulation_strategy_weights",
                "core_entry": "core.workflows.blank_shell_candidates._select_circulation_for_zones",
                "effect": "Adds weight to circulation score when selecting Top-1 strategy for zones.",
                "observable": preferred_circulation_strategy(strategy_weights),
            },
            {
                "preference": "object_preferences",
                "core_entry": "workflow.object_types + core.block_engine.block_selector",
                "effect": "Orders object types in blank_shell workflow; steers block/category priority.",
                "observable": object_preferences[0] if object_preferences else "",
            },
            {
                "preference": "preview_layer",
                "core_entry": "core.execution / CAD_PLAN layer policy",
                "effect": "Targets CODEX_PREVIEW for non-destructive draws.",
                "observable": preferences.get("preview_layer"),
            },
            {
                "preference": "layout_weights",
                "core_entry": "core.proposal_engine (ranking hooks)",
                "effect": "Documents business priority mix; does not implement ranking in agents/.",
                "observable": (
                    sorted(preferences.get("layout_weights", {}).keys())
                    if isinstance(preferences.get("layout_weights"), dict)
                    else []
                ),
            },
        ],
        "does_not_claim": list(CORE_EFFECT_NOT_CLAIMS),
    }
