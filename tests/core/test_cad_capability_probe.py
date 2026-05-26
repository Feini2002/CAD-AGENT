from __future__ import annotations

import json
import unittest

from tests.helpers import artifact_path

from core.verification.cad_capability_probe import run_cad_capability_probe
from core.verification.entity_level_evidence import entity_level_evidence_allows_probe_pass
from core.verification.evidence_contract import (
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    EVIDENCE_DEFERRED_CAD_READBACK,
    GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
    validate_capability_probe_evidence,
)
from core.verification.fake_cad_driver import FakeCadDriver


class CadCapabilityProbeTests(unittest.TestCase):
    def test_probe_creates_preview_entities_and_verifies_handle_readback(self) -> None:
        output_dir = artifact_path("cad_capability_probe", "pass")

        report = run_cad_capability_probe(driver_factory=FakeCadDriver, output_dir=output_dir)

        self.assertEqual(report["status"], "cad_capability_verified")
        self.assertEqual(report["evidence_state"], EVIDENCE_CAD_CAPABILITY_VERIFIED)
        self.assertEqual(report["geometry_accuracy"], GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE)
        self.assertEqual(report["screenshot_role"], SCREENSHOT_NOT_APPLICABLE)
        self.assertIn("contract_version", report)
        self.assertIn("block_reference", report["contract"]["entities"])
        self.assertIn("insert_block_alpha", report["contract"]["entities"]["block_reference"]["intents"])
        self.assertEqual(report["active_document"], "sample-active.dwg")
        self.assertEqual(report["layer"], "CODEX_PREVIEW")
        self.assertEqual(len(report["created_handles"]), 11)
        self.assertEqual(
            report["actual"]["type_counts"],
            {"arc": 1, "circle": 1, "dimension": 2, "line": 5, "polyline": 1, "text": 1},
        )
        self.assertTrue(all(check["status"] == "pass" for check in report["checks"]))
        self.assertIn("entity_evidence", report)
        self.assertTrue(entity_level_evidence_allows_probe_pass(report["entity_evidence"]))
        polyline_entries = [entry for entry in report["entity_evidence"] if entry["primitive"] == "polyline"]
        hatch_entries = [entry for entry in report["entity_evidence"] if entry["primitive"] == "hatch"]
        self.assertEqual(len(polyline_entries), 1)
        self.assertEqual(polyline_entries[0]["status"], "pass")
        self.assertEqual(len(hatch_entries), 1)
        self.assertEqual(hatch_entries[0]["status"], "deferred")
        self.assertEqual(validate_capability_probe_evidence(report), "")
        self.assertTrue((output_dir / "cad_capability_probe.json").exists())

        saved = json.loads((output_dir / "cad_capability_probe.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "cad_capability_verified")

    def test_probe_fails_when_created_handle_is_not_read_back(self) -> None:
        report = run_cad_capability_probe(
            driver_factory=lambda: FakeCadDriver(missing_readback_handle="H103"),
            output_dir=artifact_path("cad_capability_probe", "missing_handle"),
        )

        checks = {check["name"]: check for check in report["checks"]}
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["failure_category"], "readback_failed")
        self.assertEqual(checks["handle_readback_count"]["status"], "fail")
        self.assertIn("H103", checks["handle_readback_count"]["message"])

    def test_probe_reports_connection_failure_as_external_blocker(self) -> None:
        def raise_connection_error() -> FakeCadDriver:
            raise RuntimeError("No active AutoCAD.Application instance is available.")

        report = run_cad_capability_probe(
            driver_factory=raise_connection_error,
            output_dir=artifact_path("cad_capability_probe", "connection_failure"),
        )

        self.assertEqual(report["status"], "external_blocker")
        self.assertEqual(report["evidence_state"], EVIDENCE_DEFERRED_CAD_READBACK)
        self.assertEqual(report["geometry_accuracy"], NON_CAD_GEOMETRY_ACCURACY)
        self.assertEqual(report["failure_category"], "cad_connection_failed")
        self.assertIn("No active AutoCAD", report["error"])


if __name__ == "__main__":
    unittest.main()
