from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.drawing_analysis.shell_loader import load_manual_shell
from core.layout_engine.path_generation import generate_circulation_candidates
from core.project_model.project_builder import build_project_model
from core.schemas.validator import validate_value


def load_example(path: str) -> dict[str, object]:
    return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))


def build_retail_shell_project() -> dict[str, object]:
    brief = load_example("examples/design_briefs/minimal_cabinet_brief.json")
    drawing = load_example("examples/drawing_models/minimal_empty_room.json")
    shell = load_manual_shell(PROJECT_ROOT / "examples/shell_models/retail_blank_shell.json")
    return build_project_model(brief, drawing, shell_model=shell).project_model


class CirculationGenerationTests(unittest.TestCase):
    def test_generates_multiple_circulation_candidates_from_shell_context(self) -> None:
        candidates = generate_circulation_candidates(
            build_retail_shell_project(),
            preferences={"main_aisle_width_mm": 1200},
        )

        self.assertGreaterEqual(len(candidates), 2)
        strategies = {candidate["strategy"] for candidate in candidates}
        self.assertIn("straight_spine", strategies)
        self.assertIn("l_spine", strategies)

    def test_generated_paths_include_schema_fields_and_validate(self) -> None:
        schema = load_example("core/schemas/circulation_model.schema.json")
        candidates = generate_circulation_candidates(
            build_retail_shell_project(),
            preferences={"main_aisle_width_mm": 1200},
        )

        for candidate in candidates:
            with self.subTest(strategy=candidate["strategy"]):
                path = candidate["paths"][0]
                self.assertIn("polyline", path)
                self.assertIn("connects", path)
                self.assertIn("path_surface", path)
                self.assertIn("blocked_reasons", path)
                self.assertIn("score", path)
                self.assertEqual(validate_value(candidate, schema), [])

    def test_fixed_obstacle_overlap_keeps_blocked_reason(self) -> None:
        candidates = generate_circulation_candidates(
            build_retail_shell_project(),
            preferences={"main_aisle_width_mm": 1200},
        )
        straight = next(candidate for candidate in candidates if candidate["strategy"] == "straight_spine")

        self.assertEqual(straight["status"], "blocked")
        self.assertTrue(straight["paths"][0]["blocked_reasons"])
        self.assertIn("fixed_obstacle:column-01", straight["paths"][0]["blocked_reasons"][0])

    def test_preferences_change_strategy_order_without_domain_branching(self) -> None:
        candidates = generate_circulation_candidates(
            build_retail_shell_project(),
            preferences={
                "main_aisle_width_mm": 1200,
                "circulation_strategy_weights": {"along_wall": 3.0, "straight_spine": 1.0, "l_spine": 1.0},
            },
        )

        self.assertEqual(candidates[0]["strategy"], "along_wall")

    def test_circulation_examples_validate_against_schema(self) -> None:
        schema = load_example("core/schemas/circulation_model.schema.json")

        for example in [
            "examples/circulation_models/retail_straight_spine.json",
            "examples/circulation_models/retail_l_spine.json",
        ]:
            with self.subTest(example=example):
                model = load_example(example)
                self.assertEqual(validate_value(model, schema), [])


if __name__ == "__main__":
    unittest.main()
