from __future__ import annotations

import unittest

from tests.helpers import artifact_path

from core.verification.fake_cad_driver import FakeCadDriver
from core.verification.visual_room_plan_scene import RETAIL_SHOWROOM_EXPECTED_TYPE_COUNTS
from core.verification.visual_room_plan_smoke import run_visual_room_plan_smoke


class VisualRetailShowroomSmokeTests(unittest.TestCase):
    def test_fake_driver_draws_retail_showroom(self) -> None:
        output_dir = artifact_path("visual_retail_showroom_smoke", "fake")
        report = run_visual_room_plan_smoke(
            output_dir=output_dir,
            driver_factory=FakeCadDriver,
            base_point=[200500, 90000, 0],
            scene="retail",
        )

        self.assertEqual(report["status"], "visual_geometry_verified")
        self.assertTrue(report["geometry_verified"])
        self.assertGreaterEqual(report["created_handle_count"], 70)
        self.assertEqual(report["actual"]["type_counts"], RETAIL_SHOWROOM_EXPECTED_TYPE_COUNTS)
        self.assertEqual(report["required_visual_groups"]["missed"], [])


if __name__ == "__main__":
    unittest.main()
