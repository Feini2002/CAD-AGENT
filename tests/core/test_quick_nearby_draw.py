from __future__ import annotations

import unittest

from core.quick_tasks.nearby_draw import run_quick_nearby_draw
from core.verification.fake_cad_driver import FakeCadDriver, FakeCadEntity


class QuickNearbyDrawTests(unittest.TestCase):
    def test_draws_sofa_near_selected_focus_without_global_preview_bbox(self) -> None:
        driver = FakeCadDriver()
        driver.current_viewport_bbox = {"min": [0, 0], "max": [5000, 3000]}
        driver.selected_handles = ["S1"]
        driver.entities["S1"] = FakeCadEntity(
            handle="S1",
            object_name="AcDbBlockReference",
            layer="SOURCE",
            bbox={"min": [500, 800], "max": [1500, 1400]},
        )
        driver.entities["FAR_PREVIEW"] = FakeCadEntity(
            handle="FAR_PREVIEW",
            object_name="AcDbLine",
            layer="CODEX_PREVIEW",
            StartPoint=[100000, 100000, 0],
            EndPoint=[101000, 100000, 0],
        )

        report = run_quick_nearby_draw(
            driver,
            phrase="在旁边画个沙发",
            object_type="sofa",
        )

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["mode"], "quick_trial")
        self.assertEqual(report["placement_resolution"]["anchor_source"], "selected_handles")
        self.assertEqual(report["placement_resolution"]["base_point"], [1800.0, 800.0, 0])
        self.assertLessEqual(report["created_handle_count"], 20)
        self.assertEqual(report["object"]["width"], 1800.0)
        self.assertEqual(report["object"]["depth"], 750.0)
        self.assertTrue(report["nearby_audit"]["geometry_verified"])
        self.assertTrue(report["nearby_audit"]["checks"]["created_bbox_in_original_viewport"])
        self.assertLess(report["created_bbox"]["max"][0], 5000)

    def test_blocks_without_current_viewport_instead_of_using_far_fallback(self) -> None:
        driver = FakeCadDriver()
        driver.selected_handles = ["S1"]
        driver.entities["S1"] = FakeCadEntity(
            handle="S1",
            object_name="AcDbBlockReference",
            layer="SOURCE",
            bbox={"min": [500, 800], "max": [1500, 1400]},
        )
        before_count = len(driver.entities)

        report = run_quick_nearby_draw(
            driver,
            phrase="在旁边画个沙发",
            object_type="sofa",
        )

        self.assertEqual(report["status"], "blocked")
        self.assertIn("viewport_bbox is required", report["placement_resolution"]["blocked_reasons"][0])
        self.assertEqual(report["created_handle_count"], 0)
        self.assertEqual(len(driver.entities), before_count)

    def test_visual_deictic_request_records_scope_and_stays_in_current_view(self) -> None:
        driver = FakeCadDriver()
        driver.current_viewport_bbox = {"min": [0, 0], "max": [5000, 3000]}
        driver.selected_handles = ["S1"]
        driver.entities["S1"] = FakeCadEntity(
            handle="S1",
            object_name="AcDbBlockReference",
            layer="SOURCE",
            bbox={"min": [500, 800], "max": [1500, 1400]},
        )
        driver.entities["FAR_PREVIEW"] = FakeCadEntity(
            handle="FAR_PREVIEW",
            object_name="AcDbLine",
            layer="CODEX_PREVIEW",
            StartPoint=[100000, 100000, 0],
            EndPoint=[101000, 100000, 0],
        )

        report = run_quick_nearby_draw(
            driver,
            phrase="按截图这里画个沙发",
            object_type="sofa",
            visual_context={"source": "user_screenshot", "target_hint": "marked_region"},
        )

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["input_scope"]["scope_type"], "visual_limited")
        self.assertTrue(report["input_scope"]["visual_request"])
        self.assertEqual(report["input_scope"]["visual_source"], "user_screenshot")
        self.assertEqual(report["placement_resolution"]["anchor_source"], "selected_handles")
        self.assertIn("visual_focus_anchor", report["placement_resolution"]["checked"])
        self.assertTrue(report["nearby_audit"]["checks"]["created_bbox_in_original_viewport"])
        self.assertLess(report["created_bbox"]["max"][0], 5000)

    def test_visual_deictic_request_needs_confirmation_for_ambiguous_view(self) -> None:
        driver = FakeCadDriver()
        driver.current_viewport_bbox = {"min": [0, 0], "max": [6000, 3000]}
        driver.entities["A1"] = FakeCadEntity(
            handle="A1",
            object_name="AcDbBlockReference",
            layer="SOURCE",
            bbox={"min": [500, 800], "max": [1400, 1400]},
        )
        driver.entities["B1"] = FakeCadEntity(
            handle="B1",
            object_name="AcDbBlockReference",
            layer="SOURCE",
            bbox={"min": [3400, 800], "max": [4300, 1400]},
        )
        before_count = len(driver.entities)

        report = run_quick_nearby_draw(
            driver,
            phrase="在图片这里画个沙发",
            object_type="sofa",
            visual_context={"source": "user_screenshot", "target_hint": "marked_region"},
        )

        self.assertEqual(report["status"], "needs_confirmation")
        self.assertEqual(report["input_scope"]["scope_type"], "visual_limited")
        self.assertEqual(report["created_handle_count"], 0)
        self.assertEqual(len(driver.entities), before_count)
        self.assertIn("Visible focus is ambiguous", report["placement_resolution"]["blocked_reasons"][0])


if __name__ == "__main__":
    unittest.main()
