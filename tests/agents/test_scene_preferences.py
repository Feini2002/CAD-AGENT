from __future__ import annotations

import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

from core.agents.scene_alpha import (
    SCENE_ALPHA_SCENARIOS,
    assert_alpha_preferences_distinct,
    circulation_preferences_for_core,
    load_scene_preferences,
    observable_signature,
    validate_scene_alpha_preferences,
)
from core.layout_engine.basic_layout import create_layout_candidates
from core.layout_engine.path_generation import generate_circulation_candidates


def _alpha_project_model() -> dict:
    return {
        "project_id": "project-scene-alpha-circulation",
        "shell_id": "shell-scene-alpha-test",
        "spaces": [{"boundary": {"min": [0, 0], "max": [9000, 5200]}}],
        "openings": [{"opening_id": "entry-main", "type": "entry", "center": [0, 2600], "width": 1200}],
        "fixed_obstacles": [],
        "required_connections": [{"connection_id": "deep", "target": "zone", "point": [8000, 2600]}],
    }


class ScenePreferencesTests(unittest.TestCase):
    def test_x_scene_01_alpha_scenarios_locked_and_distinct(self) -> None:
        manifest = json.loads((PROJECT_ROOT / "agents" / "scene_alpha_manifest.json").read_text(encoding="utf-8"))
        manifest_scenarios = {item["scenario"] for item in manifest["scenarios"]}
        self.assertEqual(set(SCENE_ALPHA_SCENARIOS), manifest_scenarios)

        signatures: dict[str, dict] = {}
        for scenario in SCENE_ALPHA_SCENARIOS:
            preferences = load_scene_preferences(scenario, root=PROJECT_ROOT)
            errors = validate_scene_alpha_preferences(preferences, scenario=scenario)
            self.assertEqual(errors, [], errors)
            signatures[scenario] = observable_signature(preferences)

        distinct_errors = assert_alpha_preferences_distinct(signatures)
        self.assertEqual(distinct_errors, [], distinct_errors)

        for entry in manifest["scenarios"]:
            scenario = entry["scenario"]
            expected = entry["expected"]
            actual = signatures[scenario]
            self.assertEqual(actual["primary_object_type"], expected["primary_object_type"])
            self.assertEqual(actual["preferred_circulation_strategy"], expected["preferred_circulation_strategy"])

    def test_x_scene_01_circulation_strategy_weights_change_top_candidate(self) -> None:
        project_model = _alpha_project_model()
        top_by_scenario: dict[str, str] = {}
        for scenario in SCENE_ALPHA_SCENARIOS:
            preferences = load_scene_preferences(scenario, root=PROJECT_ROOT)
            circulation_prefs = circulation_preferences_for_core(preferences)
            candidates = generate_circulation_candidates(project_model, circulation_prefs)
            self.assertGreaterEqual(len(candidates), 2)
            top_by_scenario[scenario] = candidates[0]["strategy"]

        self.assertEqual(
            top_by_scenario,
            {
                "office": "straight_spine",
                "residential": "along_wall",
                "restaurant": "l_spine",
            },
        )
        self.assertEqual(len(set(top_by_scenario.values())), 3)

    def test_x_scene_01_layout_spacing_differs_by_secondary_aisle_width(self) -> None:
        project_model = {
            "project_id": "project-scene-alpha-spacing",
            "spaces": [{"boundary": {"min": [0, 0], "max": [6000, 3000]}}],
        }
        object_specs = [
            {"object_id": "object-a", "size": {"width": 1000, "depth": 500, "height": 1000}},
            {"object_id": "object-b", "size": {"width": 1000, "depth": 500, "height": 1000}},
        ]
        second_x: dict[str, float] = {}
        for scenario in SCENE_ALPHA_SCENARIOS:
            preferences = load_scene_preferences(scenario, root=PROJECT_ROOT)
            circulation = preferences["circulation"]
            layout = create_layout_candidates(
                project_model=project_model,
                object_specs=object_specs,
                preferences={
                    "object_spacing_mm": circulation["secondary_aisle_width_mm"],
                    "minimum_clearance_mm": circulation["secondary_aisle_width_mm"],
                    "main_aisle_width_mm": circulation["main_aisle_width_mm"],
                },
            )
            second_x[scenario] = layout["candidates"][0]["placements"][1]["base_point"][0]

        self.assertEqual(second_x["residential"], 1750)
        self.assertEqual(second_x["office"], 1850)
        self.assertEqual(second_x["restaurant"], 1950)
        self.assertEqual(len(set(second_x.values())), 3)
    def test_core_scene_preferences_exist_for_primary_scenarios(self) -> None:
        for scenario in ["commercial_fitout", "residential", "office", "restaurant"]:
            with self.subTest(scenario=scenario):
                path = PROJECT_ROOT / "agents" / scenario / "preferences.json"
                self.assertTrue(path.exists())
                preferences = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(preferences["preview_layer"], "CODEX_PREVIEW")
                self.assertGreater(preferences["circulation"]["main_aisle_width_mm"], 0)

    def test_preferences_do_not_contain_core_execution_terms(self) -> None:
        forbidden = ["AutoCADComDriver", "execute_plan", "snapshot_modelspace", "save_dwg", "delete_entity"]
        for path in (PROJECT_ROOT / "agents").glob("*/preferences.json"):
            content = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, content)

    def test_scene_preferences_can_change_core_layout_spacing(self) -> None:
        project_model = {
            "project_id": "project-preferences-test",
            "spaces": [{"boundary": {"min": [0, 0], "max": [5000, 2000]}}],
        }
        first = {"object_id": "object-a", "size": {"width": 1000, "depth": 500, "height": 1000}}
        second = {"object_id": "object-b", "size": {"width": 1000, "depth": 500, "height": 1000}}

        compact = create_layout_candidates(
            project_model=project_model,
            object_specs=[first, second],
            preferences={"object_spacing_mm": 100, "minimum_clearance_mm": 100},
        )
        commercial = create_layout_candidates(
            project_model=project_model,
            object_specs=[first, second],
            preferences={"object_spacing_mm": 900, "minimum_clearance_mm": 900},
        )

        compact_second_x = compact["candidates"][0]["placements"][1]["base_point"][0]
        commercial_second_x = commercial["candidates"][0]["placements"][1]["base_point"][0]
        self.assertEqual(compact_second_x, 1100)
        self.assertEqual(commercial_second_x, 1900)

    def test_primary_scenario_preferences_create_distinct_layout_inputs(self) -> None:
        project_model = {
            "project_id": "project-scene-diff-test",
            "spaces": [{"boundary": {"min": [0, 0], "max": [6000, 3000]}}],
        }
        first = {"object_id": "object-a", "size": {"width": 1000, "depth": 500, "height": 1000}}
        second = {"object_id": "object-b", "size": {"width": 1000, "depth": 500, "height": 1000}}
        second_x_by_scenario = {}

        for scenario in ["commercial_fitout", "residential", "office", "restaurant"]:
            preferences = json.loads((PROJECT_ROOT / "agents" / scenario / "preferences.json").read_text(encoding="utf-8"))
            layout_preferences = {
                "object_spacing_mm": preferences["circulation"]["secondary_aisle_width_mm"],
                "minimum_clearance_mm": preferences["circulation"]["secondary_aisle_width_mm"],
                "main_aisle_width_mm": preferences["circulation"]["main_aisle_width_mm"],
            }
            layout = create_layout_candidates(
                project_model=project_model,
                object_specs=[first, second],
                preferences=layout_preferences,
            )
            second_x_by_scenario[scenario] = layout["candidates"][0]["placements"][1]["base_point"][0]

        self.assertEqual(
            second_x_by_scenario,
            {
                "commercial_fitout": 1900,
                "residential": 1750,
                "office": 1850,
                "restaurant": 1950,
            },
        )


if __name__ == "__main__":
    unittest.main()
