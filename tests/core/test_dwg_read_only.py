from __future__ import annotations

import json
import unittest

from core.drawing_analysis.dwg_read_only import (
    READ_ONLY_POLICY,
    build_dwg_entity_summary,
    read_entity_summary_from_driver,
    read_entity_summary_from_fixture,
)
from core.schemas.validator import validate_value
from core.verification.fake_cad_driver import FakeCadDriver
from tests.bootstrap import PROJECT_ROOT


class DwgReadOnlyTests(unittest.TestCase):
    def test_beta_drawing_read_01_fixture_summary_schema_and_counts(self) -> None:
        summary = read_entity_summary_from_fixture(
            PROJECT_ROOT / "examples/drawing_read/sample_modelspace_entities.json"
        )
        schema = json.loads(
            (PROJECT_ROOT / "core/schemas/dwg_entity_summary.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(validate_value(summary, schema), [])
        self.assertTrue(summary["read_only"])
        self.assertEqual(summary["entity_count"], 6)
        self.assertEqual(summary["handle_count"], 6)
        self.assertEqual(summary["type_counts"]["line"], 4)
        self.assertEqual(summary["type_counts"]["text"], 1)
        self.assertEqual(summary["type_counts"]["block_reference"], 1)
        self.assertEqual(summary["bbox_union"]["max"], [5000.0, 4000.0])

        layers = {item["layer"]: item for item in summary["layer_statistics"]}
        self.assertEqual(layers["A-WALL"]["entity_count"], 4)
        self.assertEqual(layers["A-TEXT"]["entity_count"], 1)
        self.assertIn("H101", summary["handles_sample"])

    def test_read_only_policy_is_non_mutating(self) -> None:
        self.assertFalse(READ_ONLY_POLICY["mutate_dwg"])
        self.assertFalse(READ_ONLY_POLICY["save_dwg"])
        self.assertFalse(READ_ONLY_POLICY["write_entities"])

    def test_fake_cad_driver_entity_summary(self) -> None:
        driver = FakeCadDriver()
        driver.draw_rectangle(corner1=[0, 0, 0], corner2=[1000, 500, 0], layer="CODEX_PREVIEW")
        driver.draw_text(text="probe", position=[100, 100, 0], layer="CODEX_PREVIEW")

        summary = read_entity_summary_from_driver(driver, layer="CODEX_PREVIEW")
        self.assertGreaterEqual(summary["entity_count"], 1)
        self.assertEqual(summary["source"]["type"], "driver")
        self.assertIn("line", summary["type_counts"])

    def test_build_dwg_entity_summary_layer_bbox_union(self) -> None:
        summary = build_dwg_entity_summary(
            [
                {
                    "handle": "1",
                    "layer": "L1",
                    "type": "line",
                    "start_point": [10, 20, 0],
                    "end_point": [30, 40, 0],
                }
            ],
            source={"type": "unit_test"},
        )
        layer = summary["layer_statistics"][0]
        self.assertEqual(layer["bbox_union"]["min"], [10.0, 20.0])
        self.assertEqual(layer["bbox_union"]["max"], [30.0, 40.0])


if __name__ == "__main__":
    unittest.main()
