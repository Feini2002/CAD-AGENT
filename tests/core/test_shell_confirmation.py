from __future__ import annotations

import json
import unittest

from core.drawing_analysis.shell_candidate_report import read_shell_candidate_report_from_fixture
from core.drawing_analysis.shell_confirmation import (
    ShellConfirmationError,
    apply_shell_drawing_read_confirmation,
    build_shell_drawing_read_confirmation,
    load_shell_drawing_read_confirmation,
    validate_confirmation_against_report,
)
from core.schemas.validator import validate_value
from tests.bootstrap import PROJECT_ROOT


class ShellConfirmationTests(unittest.TestCase):
    def test_beta_drawing_read_04_apply_confirmation_to_shell_model(self) -> None:
        fixture = PROJECT_ROOT / "examples/drawing_read/sample_geometry_feature_fixture.json"
        report = read_shell_candidate_report_from_fixture(fixture)
        confirmation = load_shell_drawing_read_confirmation(
            PROJECT_ROOT / "examples/drawing_read/sample_shell_drawing_read_confirmation.json"
        )
        self.assertEqual(validate_confirmation_against_report(confirmation, report), [])
        shell = apply_shell_drawing_read_confirmation(report, confirmation)
        schema = json.loads(
            (PROJECT_ROOT / "core/schemas/shell_model.schema.json").read_text(encoding="utf-8")
        )
        errors = validate_value(shell, schema)
        self.assertEqual(errors, [])
        self.assertEqual(shell["shell_id"], "shell-drawing-read-sample-geometry")
        self.assertEqual(len(shell["openings"]), 1)
        self.assertEqual(len(shell["fixed_obstacles"]), 1)
        self.assertEqual(len(shell["no_place_zones"]), 1)
        self.assertEqual(shell["source"]["type"], "drawing_read_confirmation")

    def test_build_default_confirmation_round_trip(self) -> None:
        report = read_shell_candidate_report_from_fixture(
            PROJECT_ROOT / "examples/drawing_read/sample_geometry_feature_fixture.json"
        )
        confirmation = build_shell_drawing_read_confirmation(
            report,
            confirmation_id="confirm-auto-roundtrip",
        )
        shell = apply_shell_drawing_read_confirmation(report, confirmation)
        self.assertEqual(shell["shell_id"], "shell-drawing-read-confirmed")

    def test_missing_required_item_rejected(self) -> None:
        report = read_shell_candidate_report_from_fixture(
            PROJECT_ROOT / "examples/drawing_read/sample_geometry_feature_fixture.json"
        )
        confirmation = build_shell_drawing_read_confirmation(
            report,
            confirmation_id="confirm-incomplete",
        )
        confirmation["confirmed_items"] = []
        errors = validate_confirmation_against_report(confirmation, report)
        self.assertTrue(errors)
        with self.assertRaises(ShellConfirmationError):
            apply_shell_drawing_read_confirmation(report, confirmation)

    def test_excluded_draft_zone_omitted_from_shell(self) -> None:
        report = read_shell_candidate_report_from_fixture(
            PROJECT_ROOT / "examples/drawing_read/sample_geometry_feature_fixture.json"
        )
        confirmation = build_shell_drawing_read_confirmation(
            report,
            confirmation_id="confirm-exclude-zone",
            excluded_draft_ids=["draft-no-place-01"],
        )
        shell = apply_shell_drawing_read_confirmation(report, confirmation)
        self.assertEqual(shell["no_place_zones"], [])


if __name__ == "__main__":
    unittest.main()
