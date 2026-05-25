from __future__ import annotations

import json
import unittest
from pathlib import Path


from tests.bootstrap import PROJECT_ROOT

from core.workflows.blank_shell_pipeline import run_blank_shell_pipeline
from tests.helpers import artifact_path


class BlankShellPipelineTests(unittest.TestCase):
    def test_blank_shell_pipeline_writes_expected_artifacts(self) -> None:
        result = run_blank_shell_pipeline(
            PROJECT_ROOT / "examples/workflows/blank_shell_layout_loop.json",
            output_dir=artifact_path("blank_shell_pipeline", "retail"),
        )

        self.assertEqual(result["status"], "ok")
        for key in [
            "shell_model",
            "project_model",
            "circulation_candidates",
            "function_zones",
            "placements",
            "layout_proposal",
            "design_proposal",
            "cad_plans",
            "dry_run_report",
            "verification_report",
        ]:
            self.assertIn(key, result["artifacts"])
            self.assertTrue(Path(result["artifacts"][key]).exists())
        self.assertGreaterEqual(result["metrics"]["circulation_candidates"], 2)
        self.assertGreaterEqual(result["metrics"]["zones"], 2)
        self.assertGreaterEqual(result["metrics"]["placements"], 5)
        self.assertEqual(result["dry_run_report"]["status"], "valid")
        self.assertEqual(result["verification_report"]["status"], "unverified")

    def test_cad_plan_dimensions_match_layout_placement_bbox(self) -> None:
        result = run_blank_shell_pipeline(
            PROJECT_ROOT / "examples/workflows/blank_shell_layout_loop.json",
            output_dir=artifact_path("blank_shell_pipeline", "placement_plan_consistency"),
        )

        self.assertEqual(result["status"], "ok")
        layout = json.loads(Path(result["artifacts"]["layout_proposal"]).read_text(encoding="utf-8"))
        cad_plans = json.loads(Path(result["artifacts"]["cad_plans"]).read_text(encoding="utf-8"))
        placements_by_object = {
            placement["object_id"]: placement
            for placement in layout["candidates"][0]["placements"]
        }
        for cad_plan in cad_plans:
            object_spec_id = cad_plan["object"]["object_spec_id"]
            placement = placements_by_object[object_spec_id]
            bbox = placement["bbox"]
            bbox_width = bbox["max"][0] - bbox["min"][0]
            bbox_depth = bbox["max"][1] - bbox["min"][1]
            self.assertEqual(cad_plan["object"]["width"], bbox_width)
            self.assertEqual(cad_plan["object"]["depth"], bbox_depth)

    def test_residential_workflow_selects_zone_that_can_fit_objects(self) -> None:
        result = run_blank_shell_pipeline(
            PROJECT_ROOT / "examples/workflows/blank_shell_residential_layout_loop.json",
            output_dir=artifact_path("blank_shell_pipeline", "residential"),
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["metrics"]["failed_checks"], 0)
        self.assertEqual(result["metrics"]["cad_plans"], 5)


if __name__ == "__main__":
    unittest.main()
