from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.verification.cad_plan_fixture_suite import run_cad_plan_fixture_suite
from core.verification.fake_cad_driver import FakeCadDriver
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class CadPlanFixtureSuiteTests(unittest.TestCase):
    def test_no_cad_fixture_suite_validates_and_dry_runs_all_fixtures(self) -> None:
        output_dir = artifact_path("cad_plan_fixture_suite", "no_cad")
        report = run_cad_plan_fixture_suite(root=PROJECT_ROOT, output_dir=output_dir, no_cad=True)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["fixture_count"], 6)
        self.assertEqual(report["passed_fixture_count"], 6)
        self.assertTrue(all(item["validate_status"] == "pass" for item in report["fixtures"]))
        self.assertTrue(all(item["dry_run_status"] == "valid" for item in report["fixtures"]))
        self.assertTrue(all(item["cad_execution_status"] == "deferred" for item in report["fixtures"]))
        self.assertTrue((output_dir / "cad_plan_fixture_suite_report.json").is_file())

    def test_fake_cad_execution_path_executes_preview_fixtures(self) -> None:
        output_dir = artifact_path("cad_plan_fixture_suite", "fake_cad")
        report = run_cad_plan_fixture_suite(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            no_cad=False,
            driver_factory=FakeCadDriver,
        )

        self.assertEqual(report["status"], "geometry_verified")
        for item in report["fixtures"]:
            with self.subTest(fixture=item["id"]):
                self.assertEqual(item["cad_execution_status"], "executed")
                self.assertGreater(item["created_handle_count"], 0)
                self.assertIn("safety", item["execution_summary"])
        self.assertEqual(report["status"], "geometry_verified")
        self.assertTrue(report["geometry_verified"])
