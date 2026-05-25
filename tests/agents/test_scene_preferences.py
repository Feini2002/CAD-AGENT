from __future__ import annotations

import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

from core.layout_engine.basic_layout import create_layout_candidates


class ScenePreferencesTests(unittest.TestCase):
    def test_core_scene_preferences_exist_for_primary_scenarios(self) -> None:
        for scenario in ["commercial_fitout", "residential", "office"]:
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

        for scenario in ["commercial_fitout", "residential", "office"]:
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
            },
        )


if __name__ == "__main__":
    unittest.main()
