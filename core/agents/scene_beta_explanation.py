"""Scene Beta explanation helpers (BETA-SCENE-04 / SCENE-PROD-05)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.agents.scene_beta import (
    load_scene_beta_office_preferences,
    load_scene_beta_residential_preferences,
    load_scene_beta_restaurant_preferences,
    scene_beta_observable_signature,
)

SCENE_BETA_EXPLANATION_PACKAGE_ID = "SCENE-PROD-05-SCENE-EXPLANATION-TEMPLATE"
SCENE_BETA_EXPLANATION_DOC = "docs/verification/scene_prod_05_scene_explanation_template.md"

SCENE_BETA_DOES_NOT_CLAIM: tuple[str, ...] = (
    "Does not prove geometry_verified or real-project CAD accuracy.",
    "Does not turn agents/<scenario>/preferences.json into a full scene product Agent.",
    "Does not replace Core layout, collision, block selection, CAD_PLAN validation, or CAD execution.",
    "Does not treat benchmark_pass_non_cad or blocked_expected_non_cad as CAD readback evidence.",
)

SCENE_BETA_EVIDENCE_BOUNDARIES: tuple[str, ...] = (
    "benchmark_pass_non_cad",
    "blocked_expected_non_cad",
    "not_verified_without_cad_readback",
)


def build_scene_beta_explanation(preferences: dict[str, Any]) -> dict[str, Any]:
    """Structured explanation of how scene beta preferences steer Core and benchmarks."""

    circulation = preferences.get("circulation", {})
    if not isinstance(circulation, dict):
        circulation = {}
    scene_beta = preferences.get("scene_beta", {})
    if not isinstance(scene_beta, dict):
        scene_beta = {}
    object_preferences = preferences.get("object_preferences", [])
    if not isinstance(object_preferences, list):
        object_preferences = []
    layout_weights = preferences.get("layout_weights", {})
    if not isinstance(layout_weights, dict):
        layout_weights = {}

    signature = scene_beta_observable_signature(preferences)
    benchmark_suite = str(scene_beta.get("benchmark_suite", ""))

    return {
        "package_id": SCENE_BETA_EXPLANATION_PACKAGE_ID,
        "version": "0.1",
        "scenario": str(preferences.get("scenario", "")),
        "tier": str(scene_beta.get("tier", "")),
        "role": "scene_preference_explanation",
        "benchmark_suite": benchmark_suite,
        "summary": (
            "Scene beta preferences explain object priority, circulation weights, and benchmark observables; "
            "Core still owns layout generation, validation, dry-run, CAD_PLAN generation, and CAD evidence gates."
        ),
        "observable_signature": signature,
        "preference_to_core": [
            {
                "preference": "scene_beta.benchmark_suite",
                "core_entry": "core.benchmarks.runner.run_benchmark_suite",
                "effect": "Selects the no-CAD benchmark suite used to make scene behavior observable.",
                "observable": benchmark_suite,
            },
            {
                "preference": "object_preferences",
                "core_entry": "workflow.object_types + core.block_engine.block_selector",
                "effect": "Orders object types and steers catalog / block priority without implementing object geometry in agents/.",
                "observable": object_preferences[:4],
            },
            {
                "preference": "circulation.main_aisle_width_mm",
                "core_entry": "core.layout_engine.path_generation.generate_circulation_candidates",
                "effect": "Sets main aisle width for candidate circulation strips.",
                "observable": circulation.get("main_aisle_width_mm"),
            },
            {
                "preference": "circulation.secondary_aisle_width_mm",
                "core_entry": "core.layout_engine.basic_layout.create_layout_candidates",
                "effect": "Feeds object spacing and clearance in layout candidates.",
                "observable": circulation.get("secondary_aisle_width_mm"),
            },
            {
                "preference": "circulation.circulation_strategy_weights",
                "core_entry": "core.workflows.blank_shell_candidates._select_circulation_for_zones",
                "effect": "Makes the preferred circulation strategy observable in benchmark summaries.",
                "observable": signature.get("preferred_circulation_strategy"),
            },
            {
                "preference": "layout_weights",
                "core_entry": "core.proposal_engine ranking hooks",
                "effect": "Documents business scoring priorities; scene layer does not rank final deliverables alone.",
                "observable": sorted(layout_weights.keys()),
            },
            {
                "preference": "preview_layer",
                "core_entry": "core.execution / CAD_PLAN layer policy",
                "effect": "Keeps any eventual CAD write non-destructive and preview scoped.",
                "observable": preferences.get("preview_layer"),
            },
        ],
        "benchmark_observables": [
            "scenario",
            "primary_object_type",
            "preferred_circulation_strategy",
            "object_preference_count",
            "benchmark_suite",
        ],
        "evidence_boundaries": list(SCENE_BETA_EVIDENCE_BOUNDARIES),
        "does_not_claim": list(SCENE_BETA_DOES_NOT_CLAIM),
    }


def build_all_scene_beta_explanations(*, project_root: Path) -> dict[str, dict[str, Any]]:
    root = project_root.resolve()
    return {
        "office": build_scene_beta_explanation(load_scene_beta_office_preferences(root=root)),
        "residential": build_scene_beta_explanation(load_scene_beta_residential_preferences(root=root)),
        "restaurant": build_scene_beta_explanation(load_scene_beta_restaurant_preferences(root=root)),
    }


def scene_beta_explanation_status_summary(*, project_root: Path) -> dict[str, Any]:
    explanations = build_all_scene_beta_explanations(project_root=project_root)
    benchmark_suites = {
        explanation.get("benchmark_suite")
        for explanation in explanations.values()
        if explanation.get("benchmark_suite")
    }
    return {
        "package_id": SCENE_BETA_EXPLANATION_PACKAGE_ID,
        "doc": SCENE_BETA_EXPLANATION_DOC,
        "doc_present": (project_root.resolve() / SCENE_BETA_EXPLANATION_DOC).is_file(),
        "scenario_count": len(explanations),
        "benchmark_suite_count": len(benchmark_suites),
        "scenarios": sorted(explanations),
        "readback_geometry_verified_count": 0,
    }
