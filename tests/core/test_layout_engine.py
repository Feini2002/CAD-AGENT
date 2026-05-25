from __future__ import annotations

import unittest


from tests.bootstrap import PROJECT_ROOT

from core.layout_engine.basic_layout import create_layout_candidates
from core.layout_engine.clearance import check_clearance
from core.layout_engine.circulation import check_main_aisle_width
from core.object_engine.parametric_objects import create_object_spec


class LayoutEngineTests(unittest.TestCase):
    def test_create_layout_candidates_places_multiple_objects_without_overlap(self) -> None:
        project_model = {
            "project_id": "project-layout",
            "spaces": [{"space_id": "space-1", "boundary": {"min": [0, 0], "max": [5000, 2500]}}],
        }
        specs = [
            create_object_spec("cabinet", width=1800, depth=600),
            create_object_spec("table", width=1200, depth=700),
        ]

        layout = create_layout_candidates(project_model=project_model, object_specs=specs)

        self.assertEqual(layout["candidates"][0]["checks"][0]["status"], "pass")
        self.assertGreaterEqual(layout["candidates"][0]["score"], 0.7)
        self.assertEqual(len(layout["candidates"][0]["placements"]), 2)

    def test_clearance_check_reports_failure(self) -> None:
        checks = check_clearance(
            [
                {"object_id": "a", "bbox": {"min": [0, 0], "max": [1000, 1000]}},
                {"object_id": "b", "bbox": {"min": [1050, 0], "max": [2050, 1000]}},
            ],
            minimum_clearance=100,
        )

        self.assertEqual(checks[0]["status"], "fail")

    def test_main_aisle_width_check_uses_remaining_shell_depth(self) -> None:
        checks = check_main_aisle_width(
            placements=[
                {"object_id": "cabinet", "bbox": {"min": [0, 0], "max": [1800, 600]}},
            ],
            boundary={"min": [0, 0], "max": [4000, 1800]},
            minimum_width=1200,
        )

        self.assertEqual(checks[0]["status"], "pass")

        failing = check_main_aisle_width(
            placements=[
                {"object_id": "cabinet", "bbox": {"min": [0, 0], "max": [1800, 900]}},
            ],
            boundary={"min": [0, 0], "max": [4000, 1800]},
            minimum_width=1200,
        )

        self.assertEqual(failing[0]["status"], "fail")

    def test_layout_candidates_include_circulation_check_from_preferences(self) -> None:
        project_model = {
            "project_id": "project-circulation",
            "spaces": [{"space_id": "space-1", "boundary": {"min": [0, 0], "max": [5000, 1800]}}],
        }

        layout = create_layout_candidates(
            project_model=project_model,
            object_specs=[create_object_spec("cabinet", width=1800, depth=900)],
            preferences={"main_aisle_width_mm": 1200},
        )

        checks = {check["name"]: check["status"] for check in layout["candidates"][0]["checks"]}
        self.assertEqual(checks["main_aisle_width"], "fail")


if __name__ == "__main__":
    unittest.main()
