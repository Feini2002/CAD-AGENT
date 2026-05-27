from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.verification.cad_capability_probe import run_cad_capability_probe
from core.verification.evidence_contract import validate_capability_probe_evidence
from core.verification.fake_cad_driver import FakeCadDriver
from tests.helpers import artifact_path


class SessionSnapshotCapabilityProbeBoundaryTests(unittest.TestCase):
    def test_probe_attaches_consistent_session_guard_and_snapshot_artifact(self) -> None:
        output_dir = artifact_path("cad_capability_probe", "session_guard")

        report = run_cad_capability_probe(driver_factory=FakeCadDriver, output_dir=output_dir)

        self.assertEqual(report["status"], "cad_capability_verified")
        self.assertIn("session_guard", report)
        self.assertEqual(report["session_guard"]["status"], "consistent")
        comparison = report["session_guard"]["comparison"]
        self.assertIsInstance(comparison, dict)
        self.assertGreater(int(comparison.get("preview_layer_entity_delta", 0)), 0)
        checks = {check["name"]: check for check in comparison.get("checks", [])}
        self.assertEqual(checks["active_document_identity_stable"]["status"], "pass")
        self.assertEqual(validate_capability_probe_evidence(report), "")
        snapshot_path = output_dir / "active_document_snapshot.json"
        self.assertTrue(snapshot_path.exists())
        saved = json.loads(snapshot_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "consistent")

    def test_probe_fails_when_multiple_documents_open(self) -> None:
        report = run_cad_capability_probe(
            driver_factory=lambda: FakeCadDriver(open_document_count=2),
            output_dir=artifact_path("cad_capability_probe", "session_guard_multi_doc"),
        )

        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["session_guard"]["status"], "blocked")
        checks = {check["name"]: check for check in report["checks"]}
        self.assertEqual(checks["session_guard_consistent"]["status"], "fail")

    def test_boundary_doc_names_session_guard_contract(self) -> None:
        text = Path("docs/verification/session_snapshot_capability_probe_boundary.md").read_text(encoding="utf-8")

        required_terms = [
            "LCAD-13-SESSION-SNAPSHOT-CAD",
            "session_guard",
            "active_document_snapshot.json",
            "active_document_identity_stable",
            "V-PROOF-52",
            "geometry_verified",
        ]
        for term in required_terms:
            self.assertIn(term, text)


if __name__ == "__main__":
    unittest.main()
