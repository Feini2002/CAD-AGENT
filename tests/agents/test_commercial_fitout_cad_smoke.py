from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.agents.commercial_fitout_cad_smoke import (
    PRODUCT_CLAIM_BOUNDARY,
    run_commercial_fitout_cad_smoke,
    run_commercial_fitout_cad_smoke_with_workflow,
)
from core.agents.commercial_fitout_sample_confirmation import run_fitout_sample_confirmation_loop
from core.project_samples.cad_check import collect_sample_plan_paths
from core.schemas.validator import validate_value
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


class CommercialFitoutCadSmokeTests(unittest.TestCase):
    def _confirmed_workflow_dir(self) -> Path:
        output_dir = artifact_path("commercial_fitout_sample", "cad_smoke_workflow")
        report = run_fitout_sample_confirmation_loop(output_dir, project_root=PROJECT_ROOT)
        self.assertEqual(report["status"], "ok", report)
        plans = collect_sample_plan_paths(output_dir)
        self.assertGreaterEqual(len(plans), 1)
        return output_dir

    def test_fake_driver_geometry_verified_for_fitout_sample(self) -> None:
        workflow_dir = self._confirmed_workflow_dir()
        cad_dir = artifact_path("commercial_fitout_sample", "cad_smoke_fake")
        report = run_commercial_fitout_cad_smoke(
            workflow_dir,
            output_dir=cad_dir,
            project_root=PROJECT_ROOT,
            driver=FakeCadDriver(),
            offset=[70000, 40000, 0],
        )

        self.assertEqual(report["status"], "geometry_verified", report)
        self.assertEqual(report["evidence_state"], EVIDENCE_READBACK_GEOMETRY_VERIFIED)
        self.assertEqual(report["geometry_accuracy"], GEOMETRY_VERIFIED_BY_READBACK)
        self.assertEqual(report["screenshot_role"], SCREENSHOT_NOT_APPLICABLE)
        self.assertEqual(validate_evidence_triplet(report), "")
        self.assertTrue(report["geometry_verified"])
        self.assertGreater(report["created_handle_count"], 0)
        self.assertFalse(PRODUCT_CLAIM_BOUNDARY["declares_scene_product"])
        self.assertFalse(report["product_claim_boundary"]["declares_full_fitout_delivery"])

        schema = json.loads(
            (PROJECT_ROOT / "core/schemas/commercial_fitout_cad_smoke_report.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(validate_value(report, schema), [])

    def test_no_cad_deferred(self) -> None:
        workflow_dir = self._confirmed_workflow_dir()
        cad_dir = artifact_path("commercial_fitout_sample", "cad_smoke_deferred")
        report = run_commercial_fitout_cad_smoke(
            workflow_dir,
            output_dir=cad_dir,
            project_root=PROJECT_ROOT,
            no_cad=True,
        )

        self.assertEqual(report["status"], "deferred")
        self.assertEqual(report["evidence_state"], EVIDENCE_DEFERRED_CAD_READBACK)
        self.assertEqual(report["geometry_accuracy"], NON_CAD_GEOMETRY_ACCURACY)
        self.assertFalse(report["geometry_verified"])
        self.assertGreaterEqual(report["plan_count"], 1)

    def test_with_workflow_runs_confirmation_then_cad(self) -> None:
        workflow_dir = artifact_path("commercial_fitout_sample", "cad_smoke_end_to_end")
        cad_dir = artifact_path("commercial_fitout_sample", "cad_smoke_end_to_end_cad")
        report = run_commercial_fitout_cad_smoke_with_workflow(
            project_root=PROJECT_ROOT,
            workflow_output_dir=workflow_dir,
            cad_output_dir=cad_dir,
            driver=FakeCadDriver(),
            offset=[72000, 42000, 0],
        )
        self.assertEqual(report["status"], "geometry_verified", report)
        self.assertTrue((cad_dir / "commercial_fitout_cad_smoke_report.json").is_file())


if __name__ == "__main__":
    unittest.main()
