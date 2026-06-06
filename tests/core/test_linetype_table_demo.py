from __future__ import annotations

import unittest

from tests.helpers import temporary_artifact_dir


class LinetypeTableDemoTests(unittest.TestCase):
    def test_visible_text_validation_rejects_question_mark_corruption(self) -> None:
        from core.training.linetype_table_demo import LINETYPE_TABLE_ROWS, validate_visible_text

        corrupted_rows = [dict(row) for row in LINETYPE_TABLE_ROWS]
        corrupted_rows[0]["name"] = "????"

        result = validate_visible_text(corrupted_rows)

        self.assertEqual(result["status"], "fail")
        self.assertIn("????", result["question_hits"])
        self.assertEqual(result["encodingPreflight"]["status"], "fail")

    def test_visible_text_validation_rejects_mojibake_before_drawing(self) -> None:
        from core.training.linetype_table_demo import LINETYPE_TABLE_ROWS, validate_visible_text

        corrupted_rows = [dict(row) for row in LINETYPE_TABLE_ROWS]
        corrupted_rows[0]["name"] = "绾垮瀷鏍峰紡"

        result = validate_visible_text(corrupted_rows)

        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["encodingPreflight"]["status"], "fail")
        issue_kinds = {issue["kind"] for issue in result["encodingPreflight"]["issues"]}
        self.assertIn("gbk_mojibake_hint", issue_kinds)

    def test_draw_linetype_table_preserves_chinese_and_records_streaming(self) -> None:
        from core.training.linetype_table_demo import draw_linetype_table
        from core.training.streaming_demo import StreamingCadDemoConfig
        from core.verification.fake_cad_driver import FakeCadDriver

        sleeps: list[float] = []
        driver = FakeCadDriver()
        with temporary_artifact_dir("linetype_table_demo") as root:
            report = draw_linetype_table(
                driver=driver,
                output_dir=root,
                streaming_config=StreamingCadDemoConfig.hybrid(
                    item_delay_seconds=0.01,
                    operation_delay_seconds=0.02,
                    operation_budget_per_item=2,
                    zoom_each_item=True,
                ),
                sleep_fn=sleeps.append,
            )

            self.assertEqual(report["status"], "pass", report)
            self.assertEqual(report["targetLayer"], "CODEX_PREVIEW")
            self.assertEqual(report["dryRun"]["row_count"], 42)
            self.assertEqual(report["layoutPolicy"]["mode"], "integrated_dual_panel")
            self.assertEqual(report["layoutPolicy"]["panelCount"], 2)
            self.assertEqual(report["pageCount"], 1)
            self.assertEqual(report["panelCount"], 2)
            self.assertEqual(len(report["panels"]), 2)
            self.assertEqual(sum(panel["dataRowCount"] for panel in report["panels"]), 42)
            self.assertEqual(report["dryRun"]["visible_text_validation"]["status"], "pass")
            self.assertEqual(report["missingHandles"], [])
            self.assertEqual(len(report["created_handles"]), report["createdHandleCount"])
            self.assertEqual(report["visibleTextReadback"]["questionTextCount"], 0)
            self.assertEqual(report["visibleTextReadback"]["latinTextCount"], 0)
            texts = report["visibleTextReadback"]["texts"]
            self.assertIn("线型样式与颜色归纳表", texts)
            self.assertIn("连续实线", texts)
            self.assertIn("1", texts)
            self.assertIn("42", texts)
            self.assertNotIn("一", texts)
            self.assertNotIn("四十二", texts)

            layout_policy = report["layoutPolicy"]
            self.assertFalse(layout_policy["solidFillUsed"])
            self.assertTrue(layout_policy["titleBandMerged"])
            self.assertTrue(layout_policy["groupRowsMerged"])
            self.assertEqual(layout_policy["rowNumberStyle"], "arabic")
            self.assertEqual(layout_policy["rowHeightStrategy"], "adaptive_min_height")
            self.assertEqual(layout_policy["sampleFitStrategy"], "fit_to_sample_cell_bbox")
            self.assertEqual(layout_policy["sampleCellMargin"], 20.0)
            self.assertEqual(report["layoutChecks"]["solidFillEntityCount"], 0)
            self.assertEqual(report["layoutChecks"]["groupRowVerticalSegmentCount"], 0)
            self.assertTrue(report["layoutChecks"]["singleOuterFrame"])
            self.assertEqual(report["layoutChecks"]["separatePageTitleCount"], 0)
            self.assertEqual(report["layoutChecks"]["sampleOutOfCellCount"], 0)
            self.assertEqual(report["layoutChecks"]["sampleOutOfCellRows"], [])
            self.assertLessEqual(report["layoutChecks"]["panelBottomDelta"], 170.0)

            style_verification = report["styleVerification"]
            self.assertEqual(style_verification["status"], "pass", style_verification)
            self.assertEqual(style_verification["evidenceSource"], "fake_driver")
            self.assertEqual(style_verification["rowCountExpected"], 42)
            self.assertEqual(style_verification["rowCountChecked"], 42)
            self.assertEqual(style_verification["styleMismatchCount"], 0)
            self.assertEqual(len(style_verification["rows"]), 42)
            self.assertTrue(all(row["sampleHandles"] for row in style_verification["rows"]))

            dashed_row = next(row for row in style_verification["rows"] if row["visibleName"] == "短虚线")
            self.assertEqual(dashed_row["expectedStyle"]["linetype"], "DASHED")
            self.assertEqual(dashed_row["expectedStyle"]["linetypeScale"], 35.0)
            self.assertEqual(dashed_row["expectedStyle"]["lineweightMm"], 0.25)
            self.assertEqual(dashed_row["expectedStyle"]["colorName"], "yellow")
            self.assertEqual(dashed_row["mismatch"]["status"], "pass")

            by_layer_row = next(row for row in style_verification["rows"] if row["visibleName"] == "尺寸线与尺寸界线")
            self.assertEqual(by_layer_row["expectedStyle"]["styleSource"], "by_layer")
            self.assertEqual(by_layer_row["mismatch"]["status"], "pass")
            self.assertIn("尺寸线与尺寸界线", report["byLayerOverrideChecks"]["byLayerRows"])
            self.assertGreater(report["byLayerOverrideChecks"]["explicitOverrideRowCount"], 0)

            opening_row = next(row for row in style_verification["rows"] if row["visibleName"] == "开启范围线")
            opening_arc = next(item for item in opening_row["componentReadbacks"] if item["entityType"] == "arc")
            opening_lines = [item for item in opening_row["componentReadbacks"] if item["entityType"] == "line"]
            self.assertGreaterEqual(opening_arc["radius"], 110.0)
            self.assertEqual(len(opening_lines), 2)

            object_coverage = report["objectTypeCoverage"]
            for object_type in ("line", "polyline", "circle", "text", "arc", "rectangle_component"):
                self.assertEqual(object_coverage[object_type]["status"], "pass", object_coverage)
                self.assertGreaterEqual(object_coverage[object_type]["readback"], 1)
            self.assertEqual(report["plotEvidenceBoundary"]["status"], "not_checked")
            self.assertFalse(report["plotEvidenceBoundary"]["savedDwg"])

            streaming = report["streamingMode"]
            self.assertTrue(streaming["enabled"])
            self.assertEqual(streaming["mode"], "hybrid")
            self.assertGreater(streaming["event_count"], 0)
            self.assertGreater(streaming["operation_delay_count"], 0)
            self.assertEqual(streaming["item_delay_count"], 42)
            self.assertIn(0.01, sleeps)
            self.assertIn(0.02, sleeps)

            item_complete_events = [event for event in streaming["events"] if event["event"] == "item_complete"]
            self.assertEqual(len(item_complete_events), 42)
            self.assertTrue(all(event["zoom"]["status"] == "zoomed_to_handles" for event in item_complete_events))

    def test_script_entry_runs_from_utf8_file_payload(self) -> None:
        from scripts.draw_linetype_table import run_linetype_table_demo

        with temporary_artifact_dir("linetype_table_demo_script") as root:
            report = run_linetype_table_demo(
                output_dir=root,
                fake_cad=True,
                stream_demo=True,
                capture_preview=False,
            )

            self.assertEqual(report["status"], "pass", report)
            self.assertEqual(report["dryRun"]["payloadTransport"], "utf8_file_or_module_only")
            self.assertEqual(report["visibleTextReadback"]["questionTextCount"], 0)
            self.assertEqual(report["styleVerification"]["status"], "pass")
            self.assertTrue(report["streamingMode"]["enabled"])

    def test_draw_linetype_table_supports_variable_row_counts(self) -> None:
        from core.training.linetype_table_demo import LINETYPE_TABLE_ROWS, draw_linetype_table
        from core.verification.fake_cad_driver import FakeCadDriver

        rows = [dict(row) for row in LINETYPE_TABLE_ROWS[:17]]
        with temporary_artifact_dir("linetype_table_variable_rows") as root:
            report = draw_linetype_table(driver=FakeCadDriver(), output_dir=root, rows=rows)

            self.assertEqual(report["status"], "pass", report)
            self.assertEqual(report["dryRun"]["row_count"], 17)
            self.assertEqual(sum(panel["dataRowCount"] for panel in report["panels"]), 17)
            self.assertEqual(report["styleVerification"]["rowCountExpected"], 17)
            self.assertEqual(report["layoutAudit"]["status"], "pass", report["layoutAudit"])

    def test_layout_audit_detects_sample_overflow_even_if_report_flags_pass(self) -> None:
        from core.training.linetype_table_audit import audit_linetype_table_layout
        from core.training.linetype_table_demo import draw_linetype_table
        from core.verification.fake_cad_driver import FakeCadDriver

        driver = FakeCadDriver()
        with temporary_artifact_dir("linetype_table_audit_independent") as root:
            report = draw_linetype_table(driver=driver, output_dir=root)
            snapshot = driver.snapshot_handles(handles=report["created_handles"], layer=report["targetLayer"])
            report["layoutChecks"]["sampleOutOfCellCount"] = 0
            report["layoutChecks"]["sampleOutOfCellRows"] = []
            first_record = report["rowHandles"][0]
            first_record["sampleCellBbox"] = {"min": [0.0, 0.0], "max": [1.0, 1.0]}

            audit = audit_linetype_table_layout(report, snapshot=snapshot)

            self.assertEqual(audit["sampleCellContainmentAudit"]["status"], "fail", audit)
            self.assertEqual(audit["status"], "fail", audit)

    def test_layout_audit_detects_missing_sample_handles(self) -> None:
        from core.training.linetype_table_audit import audit_linetype_table_layout
        from core.training.linetype_table_demo import draw_linetype_table
        from core.verification.fake_cad_driver import FakeCadDriver

        driver = FakeCadDriver()
        with temporary_artifact_dir("linetype_table_audit_missing_handle") as root:
            report = draw_linetype_table(driver=driver, output_dir=root)
            snapshot = driver.snapshot_handles(handles=report["created_handles"], layer=report["targetLayer"])
            first_record = report["rowHandles"][0]
            first_record["sampleHandles"] = ["MISSING-HANDLE"]

            audit = audit_linetype_table_layout(report, snapshot=snapshot)

            self.assertEqual(audit["sampleCellContainmentAudit"]["status"], "fail", audit)
            self.assertEqual(audit["sampleCellContainmentAudit"]["missingSampleHandleCount"], 1)
            self.assertEqual(audit["status"], "fail", audit)


if __name__ == "__main__":
    unittest.main()
