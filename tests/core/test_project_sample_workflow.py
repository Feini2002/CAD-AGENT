from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.project_samples.workflow import (
    DEFAULT_SAMPLE_ID,
    default_sample_workflow_path,
    run_sample_blank_shell_workflow,
    validate_sample_workflow_result,
    write_sample_workflow_report,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class ProjectSampleWorkflowTests(unittest.TestCase):
    def test_beta_project_sample_03_workflow_produces_cad_plan_dry_run_and_verification(self) -> None:
        output_dir = artifact_path("project_samples", "beta_project_sample_03")
        result = run_sample_blank_shell_workflow(
            DEFAULT_SAMPLE_ID,
            project_root=PROJECT_ROOT,
            output_dir=output_dir,
        )

        self.assertEqual(result["status"], "ok", result.get("errors"))
        contract_errors = validate_sample_workflow_result(result)
        self.assertEqual(contract_errors, [], contract_errors)

        self.assertEqual(result["dry_run_report"]["status"], "valid")
        self.assertEqual(result["verification_report"]["status"], "unverified")
        self.assertGreaterEqual(result["metrics"]["cad_plans"], 1)
        self.assertGreaterEqual(result["metrics"]["placements"], 1)

        cad_plan = json.loads(Path(result["artifacts"]["cad_plan"]).read_text(encoding="utf-8"))
        self.assertEqual(cad_plan["drawing"]["layer"], "CODEX_PREVIEW")

        report_path = write_sample_workflow_report(result, output_dir=output_dir)
        self.assertTrue(report_path.is_file())
        summary = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertFalse(summary["geometry_verified"])
        self.assertEqual(summary["evidence_claim"], "non_cad_pipeline_only")
        self.assertEqual(summary["contract_errors"], [])

    def test_default_workflow_points_at_project_sample_fixtures(self) -> None:
        workflow_path = default_sample_workflow_path(PROJECT_ROOT)
        workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
        inputs = workflow["inputs"]
        self.assertIn("projects/sample_blank_shell", inputs["shell_model"])
        self.assertIn("projects/sample_blank_shell/fixtures", inputs["design_brief"])


if __name__ == "__main__":
    unittest.main()
