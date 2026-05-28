from __future__ import annotations

import json
import unittest

from tests.helpers import PROJECT_ROOT, artifact_path

from core.verification.cross_machine_reverify import run_beta_cross_machine_02_gate


class BetaCrossMachine02GateTests(unittest.TestCase):
    def test_no_cad_gate_builds_report(self) -> None:
        output_dir = artifact_path("beta_cross_machine_02", "no_cad")
        report = run_beta_cross_machine_02_gate(
            project_root=PROJECT_ROOT,
            output_dir=output_dir,
            include_real_cad=False,
            skip_unittest=True,
        )
        self.assertIn(report["status"], {"pass", "partial", "blocked"})
        report_path = output_dir / "beta_cross_machine_02_report.json"
        self.assertTrue(report_path.is_file())
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["package_id"], "BETA-CROSS-MACHINE-02")


if __name__ == "__main__":
    unittest.main()
