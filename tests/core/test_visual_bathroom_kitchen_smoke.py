from __future__ import annotations

import unittest

from tests.helpers import artifact_path

from core.verification.fake_cad_driver import FakeCadDriver
from core.verification.visual_room_plan_scene import (
    BATHROOM_PLAN_EXPECTED_TYPE_COUNTS,
    KITCHEN_PLAN_EXPECTED_TYPE_COUNTS,
)
from core.verification.visual_room_plan_smoke import run_visual_room_plan_smoke


class VisualBathroomKitchenSmokeTests(unittest.TestCase):
    def test_fake_driver_draws_bathroom_plan(self) -> None:
        output_dir = artifact_path("visual_bathroom_plan_smoke", "fake")
        report = run_visual_room_plan_smoke(
            output_dir=output_dir,
            driver_factory=FakeCadDriver,
            base_point=[211000, 90000, 0],
            scene="bathroom",
        )

        self.assertEqual(report["status"], "visual_geometry_verified")
        self.assertTrue(report["geometry_verified"])
        self.assertGreaterEqual(report["created_handle_count"], 55)
        self.assertEqual(report["actual"]["type_counts"], BATHROOM_PLAN_EXPECTED_TYPE_COUNTS)
        self.assertEqual(report["required_visual_groups"]["missed"], [])

    def test_fake_driver_draws_kitchen_plan(self) -> None:
        output_dir = artifact_path("visual_kitchen_plan_smoke", "fake")
        report = run_visual_room_plan_smoke(
            output_dir=output_dir,
            driver_factory=FakeCadDriver,
            base_point=[221500, 90000, 0],
            scene="kitchen",
        )

        self.assertEqual(report["status"], "visual_geometry_verified")
        self.assertTrue(report["geometry_verified"])
        self.assertGreaterEqual(report["created_handle_count"], 65)
        self.assertEqual(report["actual"]["type_counts"], KITCHEN_PLAN_EXPECTED_TYPE_COUNTS)
        self.assertEqual(report["required_visual_groups"]["missed"], [])


if __name__ == "__main__":
    unittest.main()
