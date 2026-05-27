from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path

from core.verification.evidence_contract import validate_capability_probe_evidence
from core.verification.guard_full_cad_runner import (
    evaluate_guard_full_strict_gate,
    run_guard_full_cad_runner,
)


class GuardFullCadRunnerTests(unittest.TestCase):
    def test_fake_strict_guard_chain_passes(self) -> None:
        output_dir = artifact_path("guard_full_cad_runner", "fake_strict")
        report = run_guard_full_cad_runner(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            use_real_cad=False,
            strict=True,
        )
        self.assertEqual(report["status"], "pass")
        self.assertTrue(report["strict"])
        self.assertEqual(report["strict_gate"]["status"], "pass")
        self.assertEqual(report["mode"], "fake_cad")
        self.assertEqual(report["subreports"]["write_guard"]["status"], "pass")
        self.assertEqual(report["subreports"]["negative_cad"]["status"], "pass")
        self.assertEqual(report["subreports"]["capability_probe"]["status"], "cad_capability_verified")

        report_path = output_dir / "guard_full_cad_report.json"
        self.assertTrue(report_path.exists())
        probe_path = output_dir / "subreports" / "capability_probe" / "cad_capability_probe.json"
        probe = json.loads(probe_path.read_text(encoding="utf-8"))
        self.assertEqual(validate_capability_probe_evidence(probe), "")
        self.assertTrue((output_dir / "subreports" / "capability_probe" / "active_document_snapshot.json").exists())

    def test_strict_gate_fails_when_probe_missing_session_guard(self) -> None:
        gate = evaluate_guard_full_strict_gate(
            write_guard={"status": "pass", "negative_cad_plans": {"status": "pass"}, "fake_write_guard": {"status": "pass"}},
            negative_cad={"status": "pass", "evidence_state": "negative_guard_verified"},
            capability_probe={"status": "cad_capability_verified"},
        )
        self.assertEqual(gate["status"], "fail")
        self.assertTrue(any("session_guard" in failure for failure in gate["failures"]))

    def test_boundary_doc_names_lcad_14_contract(self) -> None:
        text = Path("docs/verification/guard_full_cad_boundary.md").read_text(encoding="utf-8")
        self.assertIn("LCAD-14-GUARD-FULL-CAD", text)
        self.assertIn("guard_full_cad_report.json", text)
        self.assertIn("RCAD-21", text)
        self.assertIn("V-PROOF-52", text)
        self.assertIn("不得声称", text)


if __name__ == "__main__":
    unittest.main()
