from __future__ import annotations

import unittest


from tests.bootstrap import PROJECT_ROOT

from core.verification.self_check import run_self_check


class SelfCheckTests(unittest.TestCase):
    def test_self_check_reports_core_pipeline_and_screenshot_tooling(self) -> None:
        report = run_self_check(PROJECT_ROOT)

        self.assertIn(report["status"], {"pass", "warn"})
        checks = {check["name"]: check for check in report["checks"]}

        self.assertEqual(checks["required_files"]["status"], "pass")
        self.assertEqual(checks["sample_plan_validates"]["status"], "pass")
        self.assertEqual(checks["preview_execution_without_cad"]["status"], "pass")
        self.assertIn(checks["screenshot_tooling"]["status"], {"pass", "warn"})


if __name__ == "__main__":
    unittest.main()
