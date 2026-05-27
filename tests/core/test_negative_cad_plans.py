from __future__ import annotations

import unittest

from tests.bootstrap import PROJECT_ROOT

from core.verification.negative_cad_plans import run_negative_cad_plan_suite


class NegativeCadPlanTests(unittest.TestCase):
    def test_negative_manifest_rejects_all_fixtures(self) -> None:
        report = run_negative_cad_plan_suite(root=PROJECT_ROOT)
        self.assertEqual(report["status"], "pass")
        self.assertGreaterEqual(report["fixture_count"], 8)
        for row in report["fixtures"]:
            with self.subTest(fixture_id=row["id"]):
                self.assertEqual(row["status"], "pass")
                self.assertTrue(row["validate_errors"])
