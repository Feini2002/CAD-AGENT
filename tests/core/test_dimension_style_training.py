from __future__ import annotations

import json
from types import SimpleNamespace
import unittest
from pathlib import Path
from unittest.mock import patch

from core.training.dimension_style_training import DIMENSION_STYLE_SPECS, run_dimension_style_training, validate_visible_text
from core.verification.fake_cad_driver import FakeCadDriver
from scripts.run_dimension_style_training import (
    _activate_target_document,
    _cleanup_previous_handles,
    _target_document_from_cleanup_report,
)


class DimensionStyleTrainingTests(unittest.TestCase):
    def test_visible_text_preflight_accepts_chinese_style_specs(self) -> None:
        report = validate_visible_text()

        self.assertEqual(report["status"], "pass")
        self.assertEqual(len(DIMENSION_STYLE_SPECS), 10)
        self.assertFalse(report["questionHits"])

    def test_fake_cad_training_creates_dimension_readback_for_each_style(self) -> None:
        report = run_dimension_style_training(driver=FakeCadDriver(), output_dir=Path("."), write_report=False)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["scope"]["mode"], "focused")
        self.assertEqual(report["styleCount"], 10)
        self.assertGreaterEqual(report["scaleVariantCount"], 20)
        self.assertGreaterEqual(report["dimensionReadbackCount"], 10)
        self.assertEqual(report["safety"]["targetLayer"], "CODEX_PREVIEW")
        self.assertFalse(report["safety"]["savedCurrentDwg"])
        self.assertEqual(report["audit"]["failedStyleCount"], 0)
        for row in report["audit"]["rows"]:
            self.assertEqual(row["status"], "pass")
            self.assertNotEqual(row["dimensionKind"], "level_marker")
            self.assertGreaterEqual(row["dimensionReadbackCount"], 1)
            self.assertGreaterEqual(row["scaleVariantCount"], 2)
            self.assertTrue(row["styleName"].startswith("训练-"))

    def test_only_style_training_reuses_previous_panel_bounds(self) -> None:
        panel_bounds = {"min": [1000.0, 2000.0, 0.0], "max": [4900.0, 3660.0, 0.0]}

        report = run_dimension_style_training(
            driver=FakeCadDriver(),
            output_dir=Path("."),
            write_report=False,
            only_style="dimstyle.interior.elevation.opening_width_height",
            panel_bounds_override=panel_bounds,
        )

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["scope"]["mode"], "focused_repair")
        self.assertEqual(report["styleCount"], 1)
        self.assertEqual(report["canonicalStyleCount"], 10)
        self.assertEqual(list(report["panelHandlesByStyle"]), ["训练-室内-洞口宽高尺寸"])
        self.assertEqual(report["panelBoundsByStyle"]["训练-室内-洞口宽高尺寸"], panel_bounds)
        self.assertEqual(report["parkingAnchor"]["mode"], "previous_panel_bounds")
        self.assertGreaterEqual(report["dimensionReadbackCount"], 1)

    def test_opening_dimensions_keep_readable_clearance_and_report_visible_text(self) -> None:
        panel_bounds = {"min": [1000.0, 2000.0, 0.0], "max": [4900.0, 3660.0, 0.0]}

        report = run_dimension_style_training(
            driver=FakeCadDriver(),
            output_dir=Path("."),
            write_report=False,
            only_style="dimstyle.interior.elevation.opening_width_height",
            panel_bounds_override=panel_bounds,
        )

        row = report["audit"]["rows"][0]
        self.assertEqual(row["status"], "pass")
        self.assertIsNotNone(row.get("layoutChecks"))
        self.assertEqual(row.get("layoutChecks", {}).get("footerOverlap"), "pass")
        self.assertEqual(row.get("layoutChecks", {}).get("displayMeasurementMismatch"), "pass")
        self.assertGreaterEqual(row["expectedDimensionHandleCount"], 2)
        for dim in row["dimensionReadbacks"]:
            self.assertIn("text", dim)
            self.assertIn("xline1_point", dim)
            self.assertIn("xline2_point", dim)
        width_dim = next(dim for dim in row["dimensionReadbacks"] if dim.get("text") == "900")
        height_dim = next(dim for dim in row["dimensionReadbacks"] if dim.get("text") == "2100")
        floor_y = min(height_dim["xline1_point"][1], height_dim["xline2_point"][1])
        self.assertLessEqual(width_dim["bbox"]["max"][1], floor_y - 120.0)

    def test_elevation_height_dimensions_keep_readable_clearance(self) -> None:
        panel_bounds = {"min": [1000.0, 2000.0, 0.0], "max": [4900.0, 3660.0, 0.0]}

        report = run_dimension_style_training(
            driver=FakeCadDriver(),
            output_dir=Path("."),
            write_report=False,
            only_style="dimstyle.interior.elevation.height_tick",
            panel_bounds_override=panel_bounds,
        )

        row = report["audit"]["rows"][0]
        self.assertEqual(row["status"], "pass")
        self.assertIsNotNone(row.get("layoutChecks"))
        self.assertEqual(row.get("layoutChecks", {}).get("footerOverlap"), "pass")
        self.assertEqual(row.get("layoutChecks", {}).get("displayMeasurementMismatch"), "pass")
        self.assertGreaterEqual(row["expectedDimensionHandleCount"], 1)

    def test_cleanup_report_can_delete_only_one_style_panel(self) -> None:
        class FakeEntity:
            def __init__(self, layer: str) -> None:
                self.Layer = layer
                self.deleted = False

            def Delete(self) -> None:
                self.deleted = True

        class FakeDoc:
            def __init__(self, entities: dict[str, FakeEntity]) -> None:
                self.entities = entities

            def HandleToObject(self, handle: str) -> FakeEntity:
                return self.entities[handle]

            def Regen(self, _mode: int) -> None:
                return None

        entities = {
            "A1": FakeEntity("CODEX_PREVIEW"),
            "B1": FakeEntity("CODEX_PREVIEW"),
            "C1": FakeEntity("CODEX_PREVIEW"),
        }
        driver = SimpleNamespace(doc=FakeDoc(entities))
        report_payload = {
            "createdHandles": ["A1", "B1", "C1"],
            "dimensionStyleSpecs": [
                {
                    "styleId": "dimstyle.interior.elevation.opening_width_height",
                    "cadStyleName": "训练-室内-洞口宽高尺寸",
                    "visibleTitle": "室内-洞口宽高尺寸",
                }
            ],
            "panelHandlesByStyle": {"训练-室内-洞口宽高尺寸": ["B1"]},
        }

        with patch.object(Path, "read_text", return_value=json.dumps(report_payload, ensure_ascii=False)):
            cleanup = _cleanup_previous_handles(
                driver,
                Path("dimension_style_training_report.json"),
                only_style="室内-洞口宽高尺寸",
            )

        self.assertEqual(cleanup["status"], "pass")
        self.assertEqual(cleanup["deletedHandles"], ["B1"])
        self.assertEqual(cleanup["scope"]["source"], "previous_panelHandlesByStyle")
        self.assertFalse(entities["A1"].deleted)
        self.assertTrue(entities["B1"].deleted)
        self.assertFalse(entities["C1"].deleted)

    def test_cleanup_report_target_document_is_activated_before_redraw(self) -> None:
        class FakeDocument:
            def __init__(self, full_name: str) -> None:
                self.FullName = full_name
                self.ModelSpace = object()
                self.activated = False

            def Activate(self) -> None:
                self.activated = True

        target = str(Path("output") / "unit-temp" / "Drawing2.dwg")
        report_path = Path("output") / "unit-temp" / "dimension_style_training_report.json"
        other_doc = FakeDocument(str(Path("output") / "unit-temp" / "Other.dwg"))
        target_doc = FakeDocument(target)
        driver = SimpleNamespace(
            app=SimpleNamespace(Documents=[other_doc, target_doc]),
            doc=other_doc,
            model_space=other_doc.ModelSpace,
        )

        with patch.object(Path, "read_text", return_value=json.dumps({"activeDocument": {"fullName": target}})):
            self.assertEqual(_target_document_from_cleanup_report(report_path), target)
        switch = _activate_target_document(driver, target)

        self.assertEqual(switch["status"], "pass")
        self.assertTrue(target_doc.activated)
        self.assertIs(driver.doc, target_doc)
        self.assertIs(driver.model_space, target_doc.ModelSpace)


if __name__ == "__main__":
    unittest.main()
