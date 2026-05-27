from __future__ import annotations

import unittest

from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path

from core.verification.write_guard_cad_runner import run_write_guard_cad_runner


class WriteGuardCadRunnerTests(unittest.TestCase):
    def test_fake_guard_and_negative_plans_pass(self) -> None:
        output_dir = artifact_path("write_guard_cad_runner", "fake_only")
        report = run_write_guard_cad_runner(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            include_real_cad_guard=False,
        )
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["negative_cad_plans"]["status"], "pass")
        self.assertEqual(report["fake_write_guard"]["status"], "pass")
        self.assertIsNone(report["real_write_guard"])


if __name__ == "__main__":
    unittest.main()
