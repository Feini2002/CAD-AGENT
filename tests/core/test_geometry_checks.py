from __future__ import annotations

import json
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.verification.geometry_checks import check_plan_geometry, expected_bbox_from_plan


def load_plan() -> dict[str, object]:
    return json.loads((PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json").read_text(encoding="utf-8"))


class GeometryChecksTests(unittest.TestCase):
    def test_expected_bbox_comes_from_plan_geometry(self) -> None:
        bbox = expected_bbox_from_plan(load_plan())

        self.assertEqual(bbox, {"min": [0, 0], "max": [1800, 600]})

    def test_plan_geometry_checks_boundary(self) -> None:
        checks = check_plan_geometry(load_plan(), boundary={"min": [0, 0], "max": [3000, 1800]})

        self.assertEqual({check["status"] for check in checks}, {"pass"})

    def test_plan_geometry_reports_boundary_failure(self) -> None:
        checks = check_plan_geometry(load_plan(), boundary={"min": [100, 100], "max": [1000, 500]})

        failed = {check["name"] for check in checks if check["status"] == "fail"}
        self.assertIn("inside_boundary", failed)


if __name__ == "__main__":
    unittest.main()
