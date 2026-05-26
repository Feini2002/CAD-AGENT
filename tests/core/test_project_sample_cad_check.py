from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.project_samples.cad_check import (
    collect_sample_plan_paths,
    run_project_sample_cad_check,
    run_project_sample_cad_check_with_workflow,
)
from core.project_samples.workflow import DEFAULT_SAMPLE_ID, run_sample_blank_shell_workflow
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
    validate_evidence_triplet,
)
from core.verification.fake_cad_driver import FakeCadDriver
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class ProjectSampleCadCheckTests(unittest.TestCase):
    def _workflow_output_dir(self) -> Path:
        output_dir = artifact_path("project_samples", "beta_project_sample_05_workflow")
        result = run_sample_blank_shell_workflow(
            DEFAULT_SAMPLE_ID,
            project_root=PROJECT_ROOT,
            output_dir=output_dir,
        )
        self.assertEqual(result["status"], "ok", result.get("errors"))
        return output_dir

    def test_beta_project_sample_05_collects_plan_items(self) -> None:
        workflow_dir = self._workflow_output_dir()
        plans = collect_sample_plan_paths(workflow_dir)
        self.assertGreaterEqual(len(plans), 1)
        self.assertTrue(all(path.name.startswith("cad_plan_") for path in plans))

    def test_beta_project_sample_05_fake_driver_geometry_verified(self) -> None:
        workflow_dir = self._workflow_output_dir()
        cad_dir = artifact_path("project_samples", "beta_project_sample_05_cad_fake")
        report = run_project_sample_cad_check(
            workflow_dir,
            output_dir=cad_dir,
            driver=FakeCadDriver(),
            offset=[30000, 15000, 0],
        )

        self.assertEqual(report["status"], "geometry_verified", report)
        self.assertEqual(report["evidence_state"], EVIDENCE_READBACK_GEOMETRY_VERIFIED)
        self.assertEqual(report["geometry_accuracy"], GEOMETRY_VERIFIED_BY_READBACK)
        self.assertEqual(report["screenshot_role"], SCREENSHOT_NOT_APPLICABLE)
        self.assertEqual(validate_evidence_triplet(report), "")
        self.assertTrue(report["geometry_verified"])
        self.assertGreater(report["created_handle_count"], 0)
        self.assertEqual(report["safety"]["layer"], "CODEX_PREVIEW")
        self.assertFalse(report["safety"]["saved_dwg"])

        report_path = cad_dir / "project_sample_cad_check_report.json"
        self.assertTrue(report_path.is_file())
        saved = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "geometry_verified")

    def test_beta_project_sample_05_no_cad_deferred(self) -> None:
        workflow_dir = self._workflow_output_dir()
        cad_dir = artifact_path("project_samples", "beta_project_sample_05_cad_deferred")
        report = run_project_sample_cad_check(
            workflow_dir,
            output_dir=cad_dir,
            no_cad=True,
        )

        self.assertEqual(report["status"], "deferred")
        self.assertEqual(report["evidence_state"], EVIDENCE_DEFERRED_CAD_READBACK)
        self.assertEqual(report["geometry_accuracy"], NON_CAD_GEOMETRY_ACCURACY)
        self.assertEqual(report["screenshot_role"], SCREENSHOT_NOT_APPLICABLE)
        self.assertEqual(validate_evidence_triplet(report), "")
        self.assertFalse(report["geometry_verified"])
        self.assertGreaterEqual(report["plan_count"], 1)

    def test_cli_require_cad_verified_rejects_deferred_no_cad_report(self) -> None:
        workflow_dir = self._workflow_output_dir()
        cad_dir = artifact_path("project_samples", "beta_project_sample_05_cad_strict_deferred")

        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts/run_project_sample_cad_check.py"),
                "--no-cad",
                "--workflow-output-dir",
                str(workflow_dir),
                "--output-dir",
                str(cad_dir),
                "--require-cad-verified",
            ],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        report_path = cad_dir / "project_sample_cad_check_report.json"
        self.assertTrue(report_path.is_file(), completed.stderr)
        saved = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "deferred")
        self.assertFalse(saved["geometry_verified"])

    def test_cad_check_rejects_workflow_dir_outside_project_output(self) -> None:
        outside_workflow = PROJECT_ROOT / "tests" / "outside_project_sample_workflow"
        cad_dir = artifact_path("project_samples", "outside_workflow_rejected")

        with self.assertRaisesRegex(ValueError, "workflow_output_dir"):
            run_project_sample_cad_check(
                outside_workflow,
                output_dir=cad_dir,
                no_cad=True,
            )

    def test_cad_check_rejects_output_dir_outside_project_output(self) -> None:
        workflow_dir = self._workflow_output_dir()
        outside_output = PROJECT_ROOT / "tests" / "outside_project_sample_cad"

        with self.assertRaisesRegex(ValueError, "output_dir"):
            run_project_sample_cad_check(
                workflow_dir,
                output_dir=outside_output,
                no_cad=True,
            )

    def test_failed_sample_cad_check_uses_deferred_evidence_vocabulary(self) -> None:
        workflow_dir = self._workflow_output_dir()
        cad_dir = artifact_path("project_samples", "beta_project_sample_05_cad_failed")
        report = run_project_sample_cad_check(
            workflow_dir,
            output_dir=cad_dir,
            driver=FakeCadDriver(missing_readback_handle="H101"),
            offset=[30000, 15000, 0],
        )

        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["evidence_state"], EVIDENCE_DEFERRED_CAD_READBACK)
        self.assertEqual(report["geometry_accuracy"], NON_CAD_GEOMETRY_ACCURACY)
        self.assertEqual(report["screenshot_role"], SCREENSHOT_NOT_APPLICABLE)
        self.assertEqual(validate_evidence_triplet(report), "")
        self.assertFalse(report["geometry_verified"])

    def test_run_with_workflow_bootstraps_missing_output(self) -> None:
        workflow_dir = artifact_path("project_samples", "beta_project_sample_05_workflow_bootstrap")
        cad_dir = artifact_path("project_samples", "beta_project_sample_05_cad_bootstrap")
        report = run_project_sample_cad_check_with_workflow(
            project_root=PROJECT_ROOT,
            workflow_output_dir=workflow_dir,
            cad_output_dir=cad_dir,
            driver=FakeCadDriver(),
            offset=[32000, 16000, 0],
        )
        self.assertEqual(report["status"], "geometry_verified")


if __name__ == "__main__":
    unittest.main()
