from __future__ import annotations

import json
import unittest

from tests.helpers import artifact_path

from core.verification.fake_cad_driver import FakeCadDriver
from core.verification.visual_room_plan_smoke import (
    ROOM_PLAN_EXPECTED_TYPE_COUNTS,
    run_visual_room_plan_smoke,
)


class VisualRoomPlanSmokeTests(unittest.TestCase):
    def test_fake_driver_draws_annotated_room_plan(self) -> None:
        output_dir = artifact_path("visual_room_plan_smoke", "fake")
        report = run_visual_room_plan_smoke(
            output_dir=output_dir,
            driver_factory=FakeCadDriver,
            base_point=[190000, 90000, 0],
        )

        self.assertEqual(report["status"], "visual_geometry_verified")
        self.assertTrue(report["geometry_verified"])
        self.assertGreaterEqual(report["created_handle_count"], 80)
        self.assertGreaterEqual(report["visual_detail_score_percent"], 85)
        self.assertEqual(report["actual"]["type_counts"], ROOM_PLAN_EXPECTED_TYPE_COUNTS)
        self.assertEqual(report["actual"]["layer_counts"], {"CODEX_PREVIEW": report["created_handle_count"]})
        self.assertEqual(report["required_visual_groups"]["missed"], [])

        for group in (
            "segmented_double_wall",
            "door_leaf_and_swing",
            "window_symbol",
            "dimension_chain",
            "room_tags",
            "furniture_cluster",
        ):
            self.assertGreaterEqual(report["required_visual_groups"]["hit_counts"][group], 1)

        self.assertEqual(report["safety"]["layer"], "CODEX_PREVIEW")
        self.assertFalse(report["safety"]["saved_dwg"])
        self.assertFalse(report["safety"]["deleted_entities"])
        self.assertFalse(report["safety"]["modified_formal_layers"])

        saved_report = output_dir / "visual_room_plan_smoke_report.json"
        saved_summary = output_dir / "visual_room_plan_execution_summary.json"
        self.assertTrue(saved_report.is_file())
        self.assertTrue(saved_summary.is_file())
        self.assertEqual(json.loads(saved_report.read_text(encoding="utf-8"))["status"], "visual_geometry_verified")


if __name__ == "__main__":
    unittest.main()
