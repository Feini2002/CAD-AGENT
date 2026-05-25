from __future__ import annotations

import unittest


from tests.bootstrap import PROJECT_ROOT

from core.geometry_backends.orthogonal import validate_orthogonal_polygon


class OrthogonalGeometryTests(unittest.TestCase):
    def test_closed_orthogonal_polygon_returns_area_and_bbox(self) -> None:
        result = validate_orthogonal_polygon([[0, 0], [400, 0], [400, 200], [200, 200], [200, 400], [0, 400], [0, 0]])

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["area"], 120000.0)
        self.assertEqual(result["bbox"], {"min": [0.0, 0.0], "max": [400.0, 400.0]})
        self.assertEqual(result["errors"], [])

    def test_open_polygon_fails_with_structured_reason(self) -> None:
        result = validate_orthogonal_polygon([[0, 0], [400, 0], [400, 200], [0, 200]])

        self.assertEqual(result["status"], "fail")
        self.assertIn("closed", result["errors"][0])

    def test_non_orthogonal_edge_fails_with_structured_reason(self) -> None:
        result = validate_orthogonal_polygon([[0, 0], [400, 0], [500, 200], [0, 200], [0, 0]])

        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("horizontal or vertical" in error for error in result["errors"]))

    def test_self_intersection_fails_with_structured_reason(self) -> None:
        result = validate_orthogonal_polygon([[0, 0], [400, 0], [400, 400], [100, 400], [100, -100], [0, -100], [0, 0]])

        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("self-intersection" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
