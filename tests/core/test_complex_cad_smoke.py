from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.verification.complex_cad_smoke import (
    EXPECTED_TYPE_COUNTS,
    resolve_complex_output_dir,
    run_complex_cad_smoke,
)
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
)
from core.verification.fake_cad_driver import FakeCadDriver
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class ComplexCadSmokeTests(unittest.TestCase):
    def test_complex_smoke_draws_mixed_entities_and_verifies_created_handles(self) -> None:
        output_dir = artifact_path("complex_cad_smoke", "pass")

        report = run_complex_cad_smoke(driver_factory=FakeCadDriver, output_dir=output_dir)

        self.assertEqual(report["status"], "geometry_verified")
        self.assertTrue(report["geometry_verified"])
        self.assertEqual(report["evidence_state"], EVIDENCE_READBACK_GEOMETRY_VERIFIED)
        self.assertEqual(report["geometry_accuracy"], GEOMETRY_VERIFIED_BY_READBACK)
        self.assertEqual(report["layer"], "CODEX_PREVIEW")
        self.assertEqual(report["expected"]["type_counts"], EXPECTED_TYPE_COUNTS)
        self.assertEqual(report["actual"]["type_counts"], EXPECTED_TYPE_COUNTS)
        self.assertEqual(report["created_handle_count"], sum(EXPECTED_TYPE_COUNTS.values()))
        self.assertEqual(len(report["created_handles"]), report["created_handle_count"])
        self.assertTrue(all(check["status"] == "pass" for check in report["checks"]))
        self.assertTrue(report["safety"]["writes_only_preview_layer"])
        self.assertFalse(report["safety"]["saves_dwg"])
        self.assertFalse(report["safety"]["deletes_entities"])
        self.assertFalse(report["safety"]["modifies_formal_layers"])
        self.assertFalse(report["safety"]["saved_dwg"])
        checks = {check["name"]: check for check in report["checks"]}
        self.assertEqual(checks["preview_only_audit"]["status"], "pass")
        self.assertTrue((output_dir / "complex_cad_smoke_report.json").is_file())
        summary = json.loads((output_dir / "complex_cad_execution_summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["safety"]["layer"], "CODEX_PREVIEW")
        self.assertTrue((output_dir / "complex_cad_execution_summary.json").is_file())

        saved = json.loads((output_dir / "complex_cad_smoke_report.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "geometry_verified")

    def test_complex_smoke_no_cad_is_deferred_not_geometry_verified(self) -> None:
        output_dir = artifact_path("complex_cad_smoke", "no_cad")

        report = run_complex_cad_smoke(output_dir=output_dir, include_cad=False)

        self.assertEqual(report["status"], "deferred")
        self.assertFalse(report["geometry_verified"])
        self.assertEqual(report["evidence_state"], EVIDENCE_DEFERRED_CAD_READBACK)
        self.assertEqual(report["geometry_accuracy"], NON_CAD_GEOMETRY_ACCURACY)
        self.assertEqual(report["created_handle_count"], 0)
        self.assertEqual(report["created_handles"], [])

    def test_complex_smoke_fails_when_created_handle_is_not_read_back(self) -> None:
        report = run_complex_cad_smoke(
            driver_factory=lambda: FakeCadDriver(missing_readback_handle="H112"),
            output_dir=artifact_path("complex_cad_smoke", "missing_handle"),
        )

        checks = {check["name"]: check for check in report["checks"]}
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["failure_category"], "readback_failed")
        self.assertEqual(checks["handle_readback_count"]["status"], "fail")
        self.assertIn("H112", checks["handle_readback_count"]["message"])

    def test_complex_smoke_cli_output_must_stay_under_project_output(self) -> None:
        output_dir = resolve_complex_output_dir(
            Path("output/validation_runs/complex-safe-output"),
            project_root=PROJECT_ROOT,
        )
        self.assertTrue(output_dir.is_relative_to((PROJECT_ROOT / "output").resolve()))

        with self.assertRaisesRegex(ValueError, "output_dir must stay under project output directory"):
            resolve_complex_output_dir(PROJECT_ROOT.parent / "outside-complex-smoke", project_root=PROJECT_ROOT)


if __name__ == "__main__":
    unittest.main()
