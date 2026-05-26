from __future__ import annotations

import json
import unittest

from core.drawing_analysis.shell_candidate_report import (
    build_shell_candidate_confidence_report,
    read_shell_candidate_report_from_fixture,
)
from core.drawing_analysis.geometry_candidates import read_geometry_candidates_from_fixture
from core.schemas.validator import validate_value
from tests.bootstrap import PROJECT_ROOT


class ShellCandidateReportTests(unittest.TestCase):
    def test_beta_drawing_read_03_complete_fixture_schema_and_confidence(self) -> None:
        fixture = PROJECT_ROOT / "examples/drawing_read/sample_geometry_feature_fixture.json"
        report = read_shell_candidate_report_from_fixture(fixture)
        schema = json.loads(
            (PROJECT_ROOT / "core/schemas/shell_candidate_confidence_report.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(validate_value(report, schema), [])
        self.assertGreaterEqual(report["confidence"]["overall"], 0.7)
        self.assertGreaterEqual(report["confidence"]["boundary"], 0.75)
        self.assertEqual(len(report["shell_candidate_draft"]["proposed_openings"]), 1)
        self.assertTrue(report["ready_for_human_confirmation_file"])
        gap_codes = {item["code"] for item in report["gaps"]}
        self.assertNotIn("missing_entry_opening", gap_codes)
        confirm_codes = {item["code"] for item in report["human_confirmation_items"]}
        self.assertIn("confirm_boundary_bbox", confirm_codes)

    def test_beta_drawing_read_03_incomplete_fixture_has_blocker_gap(self) -> None:
        fixture = PROJECT_ROOT / "examples/drawing_read/sample_geometry_walls_only_fixture.json"
        report = read_shell_candidate_report_from_fixture(fixture)
        gap_codes = {item["code"] for item in report["gaps"]}
        self.assertIn("missing_entry_opening", gap_codes)
        self.assertFalse(report["ready_for_human_confirmation_file"])
        self.assertTrue(
            any(item["code"] == "resolve_gap" for item in report["human_confirmation_items"]),
        )

    def test_machine_assert_confidence_keys_present(self) -> None:
        candidates = read_geometry_candidates_from_fixture(
            PROJECT_ROOT / "examples/drawing_read/sample_geometry_feature_fixture.json"
        )
        report = build_shell_candidate_confidence_report(candidates)
        for key in ("overall", "boundary", "openings", "fixed_obstacles", "no_place_zones"):
            self.assertIn(key, report["confidence"])


if __name__ == "__main__":
    unittest.main()
