from __future__ import annotations

import math
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.verification.inspect_dwg import (
    load_execution_summary,
    normalize_com_entity,
    snapshot_entities,
    snapshot_entities_by_handles,
)
from core.verification.verification_report import (
    build_verification_report,
    snapshot_diff,
    summarize_verification_reports,
)
from core.schemas.validator import validate_value
import json


class FakeLine:
    ObjectName = "AcDbLine"
    Layer = "CODEX_PREVIEW"
    Handle = "L1"
    StartPoint = [0, 0, 0]
    EndPoint = [1800, 0, 0]


class FakeText:
    ObjectName = "AcDbText"
    Layer = "CODEX_PREVIEW"
    Handle = "T1"
    TextString = "测试柜"
    InsertionPoint = [900, 300, 0]


class FakeCircle:
    ObjectName = "AcDbCircle"
    Layer = "CODEX_PREVIEW"
    Handle = "C1"
    Center = [500, 250, 0]
    Radius = 100


class FakeArc:
    ObjectName = "AcDbArc"
    Layer = "CODEX_PREVIEW"
    Handle = "A1"
    Center = [700, 250, 0]
    Radius = 80
    StartAngle = 0
    EndAngle = 1.5707963267948966


class FakePolyline:
    ObjectName = "AcDbPolyline"
    Layer = "CODEX_PREVIEW"
    Handle = "P1"
    Coordinates = [0, 0, 400, 0, 400, 200]
    Closed = True


class FakeBlockReference:
    ObjectName = "AcDbBlockReference"
    Layer = "CODEX_PREVIEW"
    Handle = "BR1"
    EffectiveName = "CODEX_TEST_BLOCK_001"
    InsertionPoint = [1200, 800, 0]
    Rotation = math.radians(90)
    XScaleFactor = 1.0
    YScaleFactor = 1.0
    ZScaleFactor = 1.0

    def GetBoundingBox(self) -> tuple[list[float], list[float]]:
        return [1200.0, 800.0, 0.0], [2100.0, 1250.0, 0.0]


class VerificationReportTests(unittest.TestCase):
    def test_unverified_report_does_not_claim_geometry_accuracy(self) -> None:
        report = build_verification_report(
            plan_path=PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json",
            execution_summary={"status": "executed"},
        )

        self.assertEqual(report["status"], "executed_only")
        self.assertEqual(report["checks"][0]["status"], "not_run")
        self.assertTrue(report["requires_real_cad"])

    def test_fake_readback_without_created_handles_cannot_claim_geometry_verified(self) -> None:
        entities = [
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [0, 0, 0], "end_point": [1800, 0, 0]},
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [1800, 0, 0], "end_point": [1800, 600, 0]},
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [1800, 600, 0], "end_point": [0, 600, 0]},
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [0, 600, 0], "end_point": [0, 0, 0]},
            {"type": "text", "layer": "CODEX_PREVIEW", "text": "测试柜", "position": [900, 300, 0]},
            {"type": "dimension", "layer": "CODEX_PREVIEW"},
            {"type": "dimension", "layer": "CODEX_PREVIEW"},
        ]

        report = build_verification_report(
            plan_path=PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json",
            entities=entities,
            entities_are_scoped=True,
        )

        self.assertEqual(report["status"], "unverified")
        self.assertIn("untrusted_scope_claim", [check["name"] for check in report["checks"]])

    def test_created_handles_are_required_when_scope_claim_uses_handles(self) -> None:
        entities = [
            {"handle": "H1", "type": "line", "layer": "CODEX_PREVIEW", "start_point": [0, 0, 0], "end_point": [1800, 0, 0]},
            {"handle": "H2", "type": "line", "layer": "CODEX_PREVIEW", "start_point": [1800, 0, 0], "end_point": [1800, 600, 0]},
            {"handle": "H3", "type": "line", "layer": "CODEX_PREVIEW", "start_point": [1800, 600, 0], "end_point": [0, 600, 0]},
            {"handle": "H4", "type": "line", "layer": "CODEX_PREVIEW", "start_point": [0, 600, 0], "end_point": [0, 0, 0]},
            {"handle": "H5", "type": "text", "layer": "CODEX_PREVIEW", "text": "测试柜", "position": [900, 300, 0]},
            {"handle": "H6", "type": "dimension", "layer": "CODEX_PREVIEW"},
            {"handle": "H7", "type": "dimension", "layer": "CODEX_PREVIEW"},
        ]

        report = build_verification_report(
            plan_path=PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json",
            entities=entities,
            created_handles=["H1", "H2", "H3", "H4", "H5", "H6", "H7"],
        )

        self.assertEqual(report["status"], "geometry_verified")

        missing_report = build_verification_report(
            plan_path=PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json",
            entities=entities,
            created_handles=["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"],
        )

        self.assertNotEqual(missing_report["status"], "geometry_verified")
        scope = missing_report["actual"]["created_handle_scope"]
        self.assertEqual(scope["miss_count"], 1)
        checks = {check["name"]: check for check in missing_report["checks"]}
        self.assertEqual(checks["created_handles_scope"]["status"], "fail")

    def test_missing_screenshot_file_does_not_count_as_screenshot_evidence(self) -> None:
        report = build_verification_report(
            plan_path=PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json",
            screenshot_path=PROJECT_ROOT / "output" / "previews" / "does-not-exist.png",
        )

        self.assertEqual(report["status"], "unverified")
        self.assertIn("screenshot_evidence", [check["name"] for check in report["checks"]])

    def test_failed_readback_stays_failed_even_with_screenshot(self) -> None:
        entities = [
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [0, 0, 0], "end_point": [100, 0, 0]},
        ]

        report = build_verification_report(
            plan_path=PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json",
            entities=entities,
            screenshot_path=PROJECT_ROOT / "output" / "previews" / "fake.png",
            execution_summary={"status": "executed"},
            entities_are_scoped=True,
        )

        self.assertEqual(report["status"], "failed")

    def test_correct_size_at_wrong_base_point_fails(self) -> None:
        entities = [
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [100, 100, 0], "end_point": [1900, 100, 0]},
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [1900, 100, 0], "end_point": [1900, 700, 0]},
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [1900, 700, 0], "end_point": [100, 700, 0]},
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [100, 700, 0], "end_point": [100, 100, 0]},
            {"type": "text", "layer": "CODEX_PREVIEW", "text": "测试柜", "position": [1000, 400, 0]},
            {"type": "dimension", "layer": "CODEX_PREVIEW"},
            {"type": "dimension", "layer": "CODEX_PREVIEW"},
        ]

        report = build_verification_report(
            plan_path=PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json",
            entities=entities,
            entities_are_scoped=True,
        )

        self.assertEqual(report["status"], "failed")
        self.assertIn("base_point", [check["name"] for check in report["checks"] if check["status"] == "fail"])

    def test_wrong_layer_label_and_dimensions_do_not_satisfy_preview_layer(self) -> None:
        entities = [
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [0, 0, 0], "end_point": [1800, 0, 0]},
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [1800, 0, 0], "end_point": [1800, 600, 0]},
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [1800, 600, 0], "end_point": [0, 600, 0]},
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [0, 600, 0], "end_point": [0, 0, 0]},
            {"type": "text", "layer": "A-ANNO", "text": "测试柜", "position": [900, 300, 0]},
            {"type": "dimension", "layer": "A-ANNO"},
            {"type": "dimension", "layer": "A-ANNO"},
        ]

        report = build_verification_report(
            plan_path=PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json",
            entities=entities,
            entities_are_scoped=True,
        )

        failed = {check["name"] for check in report["checks"] if check["status"] == "fail"}
        self.assertEqual(report["status"], "failed")
        self.assertIn("label_text", failed)
        self.assertIn("dimension_count", failed)

    def test_unscoped_entities_cannot_claim_geometry_verified(self) -> None:
        entities = [
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [0, 0, 0], "end_point": [1800, 0, 0]},
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [1800, 0, 0], "end_point": [1800, 600, 0]},
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [1800, 600, 0], "end_point": [0, 600, 0]},
            {"type": "line", "layer": "CODEX_PREVIEW", "start_point": [0, 600, 0], "end_point": [0, 0, 0]},
            {"type": "text", "layer": "CODEX_PREVIEW", "text": "测试柜", "position": [900, 300, 0]},
            {"type": "dimension", "layer": "CODEX_PREVIEW"},
            {"type": "dimension", "layer": "CODEX_PREVIEW"},
        ]

        report = build_verification_report(
            plan_path=PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json",
            entities=entities,
        )

        self.assertEqual(report["status"], "unverified")
        self.assertIn("warning", {check["status"] for check in report["checks"]})

    def test_build_report_output_validates_against_schema_subset(self) -> None:
        report = build_verification_report(
            plan_path=PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json",
            execution_summary={"status": "executed"},
        )
        schema = json.loads(
            (PROJECT_ROOT / "core" / "schemas" / "verification_report.schema.json").read_text(encoding="utf-8")
        )

        self.assertEqual(validate_value(report, schema), [])

    def test_snapshot_diff_reports_added_and_removed_entities_by_handle(self) -> None:
        diff = snapshot_diff(
            before_entities=[
                {"handle": "A", "type": "line", "layer": "CODEX_PREVIEW"},
                {"handle": "B", "type": "text", "layer": "CODEX_PREVIEW"},
            ],
            after_entities=[
                {"handle": "B", "type": "text", "layer": "CODEX_PREVIEW"},
                {"handle": "C", "type": "dimension", "layer": "CODEX_PREVIEW"},
            ],
        )

        self.assertEqual(diff["added_handles"], ["C"])
        self.assertEqual(diff["removed_handles"], ["A"])
        self.assertEqual(diff["unchanged_count"], 1)

    def test_failed_report_includes_repair_suggestions(self) -> None:
        report = build_verification_report(
            plan_path=PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json",
            entities=[
                {"handle": "H1", "type": "line", "layer": "CODEX_PREVIEW", "start_point": [100, 100, 0], "end_point": [200, 100, 0]},
            ],
            created_handles=["H1"],
        )

        suggestions = {item["check"]: item["suggestion"] for item in report["repair_suggestions"]}
        self.assertEqual(report["status"], "failed")
        self.assertIn("bbox_size", suggestions)
        self.assertIn("base_point", suggestions)

    def test_batch_verification_summary_counts_statuses(self) -> None:
        reports = [
            {"report_id": "r1", "status": "geometry_verified", "requires_real_cad": []},
            {"report_id": "r2", "status": "failed", "requires_real_cad": []},
            {"report_id": "r3", "status": "unverified", "requires_real_cad": ["readback"]},
        ]

        summary = summarize_verification_reports(reports)

        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["status_counts"]["geometry_verified"], 1)
        self.assertEqual(summary["status_counts"]["failed"], 1)
        self.assertEqual(summary["requires_real_cad_count"], 1)

    def test_com_like_entities_normalize_to_plain_readback(self) -> None:
        line = normalize_com_entity(FakeLine())
        text = normalize_com_entity(FakeText())
        circle = normalize_com_entity(FakeCircle())
        arc = normalize_com_entity(FakeArc())
        polyline = normalize_com_entity(FakePolyline())

        self.assertEqual(line["type"], "line")
        self.assertEqual(line["end_point"], [1800.0, 0.0, 0.0])
        self.assertEqual(text["type"], "text")
        self.assertEqual(text["text"], "测试柜")
        self.assertEqual(circle["type"], "circle")
        self.assertEqual(circle["center"], [500.0, 250.0, 0.0])
        self.assertEqual(circle["radius"], 100.0)
        self.assertEqual(circle["bbox"], {"min": [400.0, 150.0], "max": [600.0, 350.0]})
        self.assertEqual(arc["type"], "arc")
        self.assertEqual(arc["start_angle"], 0.0)
        self.assertEqual(arc["end_angle"], 1.5707963267948966)
        self.assertEqual(polyline["type"], "polyline")
        self.assertEqual(polyline["points"], [[0.0, 0.0, 0.0], [400.0, 0.0, 0.0], [400.0, 200.0, 0.0]])
        self.assertTrue(polyline["closed"])

        block = normalize_com_entity(FakeBlockReference())
        self.assertEqual(block["type"], "block_reference")
        self.assertEqual(block["block_name"], "CODEX_TEST_BLOCK_001")
        self.assertEqual(block["insertion_point"], [1200.0, 800.0, 0.0])
        self.assertAlmostEqual(block["rotation"], 90.0)
        self.assertEqual(block["scale"], [1.0, 1.0, 1.0])
        self.assertEqual(block["bbox"], {"min": [1200.0, 800.0], "max": [2100.0, 1250.0]})

    def test_snapshot_uses_driver_readback_when_available(self) -> None:
        class Driver:
            def snapshot_modelspace(self, *, layer: str | None = None) -> list[dict[str, object]]:
                return [{"type": "line", "layer": layer or "CODEX_PREVIEW"}]

        self.assertEqual(snapshot_entities(Driver(), layer="CODEX_PREVIEW")[0]["layer"], "CODEX_PREVIEW")

    def test_snapshot_by_handles_uses_handle_lookup_without_modelspace_scan(self) -> None:
        class FakeModelSpace:
            def __iter__(self):
                raise AssertionError("full modelspace scan should not run when handles are available")

        class FakeDocument:
            def HandleToObject(self, handle: str) -> object:
                entity = FakeLine()
                entity.Handle = handle
                return entity

        class Driver:
            doc = FakeDocument()
            model_space = FakeModelSpace()

        entities = snapshot_entities_by_handles(Driver(), ["H1", "H2"], layer="CODEX_PREVIEW")

        self.assertEqual([entity["handle"] for entity in entities], ["H1", "H2"])
        self.assertEqual({entity["layer"] for entity in entities}, {"CODEX_PREVIEW"})

    def test_execution_summary_loader_extracts_created_handles(self) -> None:
        path = PROJECT_ROOT / "output" / "test_artifacts" / "verification" / "execution_summary.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{"status": "executed", "created_handles": ["H1", "H2"]}', encoding="utf-8")

        summary, handles = load_execution_summary(path)

        self.assertEqual(summary["status"], "executed")
        self.assertEqual(handles, ["H1", "H2"])


if __name__ == "__main__":
    unittest.main()
