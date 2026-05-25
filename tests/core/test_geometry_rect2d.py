from __future__ import annotations

import unittest


from tests.bootstrap import PROJECT_ROOT

from core.geometry_backends.rect2d import (
    distance_to_opening_or_obstacle,
    expand_rect,
    path_to_rect_strips,
    rect_area,
    rect_center,
    rect_contains,
    rect_gap,
    rect_intersects,
    subtract_no_place_zones,
)


class Rect2DGeometryTests(unittest.TestCase):
    def test_basic_rect_operations_are_deterministic(self) -> None:
        rect = {"min": [100, 200], "max": [500, 800]}

        self.assertEqual(rect_area(rect), 240000.0)
        self.assertEqual(rect_center(rect), [300.0, 500.0])
        self.assertTrue(rect_intersects(rect, {"min": [400, 700], "max": [700, 900]}))
        self.assertFalse(rect_intersects(rect, {"min": [500, 800], "max": [900, 1200]}))
        self.assertTrue(rect_contains(rect, {"min": [120, 220], "max": [300, 400]}))
        self.assertFalse(rect_contains(rect, {"min": [0, 220], "max": [300, 400]}))
        self.assertEqual(expand_rect(rect, 50), {"min": [50.0, 150.0], "max": [550.0, 850.0]})

    def test_rect_gap_reports_axis_aligned_and_diagonal_clearance(self) -> None:
        rect = {"min": [0, 0], "max": [100, 100]}

        self.assertEqual(rect_gap(rect, {"min": [150, 20], "max": [250, 120]}), 50.0)
        self.assertEqual(rect_gap(rect, {"min": [150, 140], "max": [250, 240]}), 64.03124237432849)
        self.assertEqual(rect_gap(rect, {"min": [80, 80], "max": [120, 120]}), 0.0)

    def test_subtract_no_place_zones_splits_bbox_shell_conservatively(self) -> None:
        shell = {"type": "bbox", "min": [0, 0], "max": [1000, 500]}
        zones = [{"zone_id": "column-band", "bbox": {"min": [400, 0], "max": [600, 500]}}]

        result = subtract_no_place_zones(shell, zones)

        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["rects"], [{"min": [0.0, 0.0], "max": [400.0, 500.0]}, {"min": [600.0, 0.0], "max": [1000.0, 500.0]}])
        self.assertEqual(result["blocked_reasons"], [])

    def test_subtract_no_place_zones_returns_reason_when_shell_is_not_bbox(self) -> None:
        result = subtract_no_place_zones({"type": "orthogonal_polygon", "points": []}, [])

        self.assertEqual(result["status"], "unsupported")
        self.assertIn("bbox shell", result["blocked_reasons"][0])

    def test_subtract_no_place_zones_ignores_non_intersecting_zones(self) -> None:
        shell = {"type": "bbox", "min": [0, 0], "max": [1000, 500]}
        zones = [{"zone_id": "outside", "bbox": {"min": [1200, 0], "max": [1500, 500]}}]

        result = subtract_no_place_zones(shell, zones)

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["rects"], [{"min": [0.0, 0.0], "max": [1000.0, 500.0]}])
        self.assertEqual(result["blocked_reasons"], [])

    def test_path_to_rect_strips_converts_orthogonal_polyline(self) -> None:
        strips = path_to_rect_strips([[0, 100], [1000, 100], [1000, 400]], width=200)

        self.assertEqual(
            strips,
            [
                {"min": [0.0, 0.0], "max": [1000.0, 200.0]},
                {"min": [900.0, 100.0], "max": [1100.0, 400.0]},
            ],
        )

    def test_path_to_rect_strips_skips_duplicate_consecutive_points(self) -> None:
        strips = path_to_rect_strips([[0, 100], [1000, 100], [1000, 100]], width=200)

        self.assertEqual(strips, [{"min": [0.0, 0.0], "max": [1000.0, 200.0]}])

    def test_path_to_rect_strips_rejects_diagonal_segments_with_reason(self) -> None:
        with self.assertRaisesRegex(ValueError, "orthogonal"):
            path_to_rect_strips([[0, 0], [100, 100]], width=50)

    def test_distance_to_opening_or_obstacle_reports_nearest_targets(self) -> None:
        result = distance_to_opening_or_obstacle(
            [100, 100],
            openings=[{"opening_id": "entry", "center": [100, 500], "width": 900}],
            obstacles=[{"obstacle_id": "column", "bbox": {"min": [300, 50], "max": [500, 250]}}],
        )

        self.assertEqual(result["nearest_opening"]["id"], "entry")
        self.assertEqual(result["nearest_opening"]["distance"], 400.0)
        self.assertEqual(result["nearest_obstacle"]["id"], "column")
        self.assertEqual(result["nearest_obstacle"]["distance"], 200.0)


if __name__ == "__main__":
    unittest.main()
