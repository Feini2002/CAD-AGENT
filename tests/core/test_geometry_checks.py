from __future__ import annotations

import json
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.verification.geometry_checks import (
    check_block_reference_readback,
    check_plan_geometry,
    classify_block_readback_failure,
    expected_bbox_from_plan,
    expected_block_reference_from_plan,
    missing_block_reference_fields,
)


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

    def test_insert_block_alpha_plan_geometry_check_defers_to_entity_readback(self) -> None:
        plan = json.loads((PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json").read_text(encoding="utf-8"))
        checks = check_plan_geometry(plan)
        self.assertEqual(checks[0]["name"], "block_reference_readback_required")
        self.assertEqual(checks[0]["status"], "not_run")

    def test_block_reference_readback_passes_for_matching_entity(self) -> None:
        plan = json.loads((PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json").read_text(encoding="utf-8"))
        expected = expected_block_reference_from_plan(plan)
        entity = {
            "handle": "BR1",
            "type": "block_reference",
            **expected,
        }
        checks = check_block_reference_readback(plan, entity)
        self.assertTrue(all(check["status"] == "pass" for check in checks))

    def test_block_reference_readback_reports_missing_fields(self) -> None:
        plan = json.loads((PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json").read_text(encoding="utf-8"))
        entity = {"handle": "BR1", "type": "block_reference", "layer": "CODEX_PREVIEW"}
        self.assertIn("block_name", missing_block_reference_fields(entity))
        checks = check_block_reference_readback(plan, entity)
        self.assertEqual(checks[0]["failure_category"], "readback_missing")
        self.assertEqual(classify_block_readback_failure("readback_fields"), "readback_missing")

    def test_block_reference_readback_reports_block_name_mismatch(self) -> None:
        plan = json.loads((PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json").read_text(encoding="utf-8"))
        entity = {
            "handle": "BR1",
            "type": "block_reference",
            "block_name": "OTHER_BLOCK",
            "insertion_point": [1200.0, 800.0, 0.0],
            "rotation": 0.0,
            "scale": [1.0, 1.0, 1.0],
            "layer": "CODEX_PREVIEW",
            "bbox": {"min": [1200.0, 800.0], "max": [2100.0, 1250.0]},
        }
        checks = check_block_reference_readback(plan, entity)
        failed = {check["name"]: check for check in checks if check["status"] == "fail"}
        self.assertEqual(failed["block_name"]["failure_category"], "block_name_mismatch")
        self.assertEqual(classify_block_readback_failure("block_name"), "block_name_mismatch")

    def test_block_reference_readback_reports_anchor_mismatch(self) -> None:
        plan = json.loads((PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json").read_text(encoding="utf-8"))
        entity = {
            "handle": "BR1",
            "type": "block_reference",
            "block_name": "CODEX_TEST_BLOCK_001",
            "insertion_point": [0.0, 0.0, 0.0],
            "rotation": 0.0,
            "scale": [1.0, 1.0, 1.0],
            "layer": "CODEX_PREVIEW",
            "bbox": {"min": [1200.0, 800.0], "max": [2100.0, 1250.0]},
        }
        checks = check_block_reference_readback(plan, entity)
        failed = {check["name"]: check for check in checks if check["status"] == "fail"}
        self.assertEqual(failed["insertion_point"]["failure_category"], "anchor_mismatch")


if __name__ == "__main__":
    unittest.main()
