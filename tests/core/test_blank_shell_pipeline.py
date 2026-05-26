from __future__ import annotations

import json
import unittest
from pathlib import Path


from tests.bootstrap import PROJECT_ROOT

from core.workflows.blank_shell_pipeline import build_blank_shell_candidate_sets, run_blank_shell_pipeline
from core.layout_engine.path_generation import generate_circulation_candidates
from core.project_model.project_builder import build_project_model
from core.drawing_analysis.shell_loader import load_manual_shell
from core.schemas.validator import load_json
from core.block_engine.block_library import load_block_library
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
            "candidate_sets",
            "function_zones",
            "placements",
            "layout_proposal",
            "design_proposal",
            "cad_plans",
            "dry_run_report",
            "dry_run_reports",
            "verification_report",
            "verification_reports",
        ]:
            self.assertIn(key, result["artifacts"])
            self.assertTrue(Path(result["artifacts"][key]).exists())
        self.assertGreaterEqual(result["metrics"]["circulation_candidates"], 2)
        self.assertGreaterEqual(result["metrics"]["zone_placement_candidates"], 2)
        self.assertGreaterEqual(result["metrics"]["zones"], 2)
        candidate_sets = json.loads(Path(result["artifacts"]["candidate_sets"]).read_text(encoding="utf-8"))
        self.assertIn("circulation_branches", candidate_sets)
        self.assertGreaterEqual(len(candidate_sets["circulation_branches"]), 2)
        self.assertEqual(
            candidate_sets["selection"]["circulation_strategy"],
            result["metrics"]["selected_circulation_strategy"],
        )
        selected_branch = next(
            branch for branch in candidate_sets["circulation_branches"] if branch["selected"]
        )
        self.assertGreaterEqual(len(selected_branch["zone_placement_candidates"]), 1)
        self.assertTrue(
            any(candidate["selected"] for candidate in selected_branch["zone_placement_candidates"])
        )
        proposal = json.loads(Path(result["artifacts"]["design_proposal"]).read_text(encoding="utf-8"))
        detail = proposal["comparison_detail"]
        self.assertIn("metrics", detail)
        self.assertGreaterEqual(detail["metrics"]["circulation_branch_count"], 2)
        self.assertIn("object_coverage_rate", detail["metrics"])
        self.assertIn("continuity", detail["circulation_continuity"])
        self.assertGreaterEqual(len(detail["ranking_reasons"]), 1)
        self.assertTrue(proposal["comparison_summary"])
        self.assertGreaterEqual(len(proposal["candidates"]), 2)
        self.assertGreaterEqual(result["metrics"]["placements"], 5)
        self.assertEqual(result["dry_run_report"]["status"], "valid")
        self.assertEqual(result["dry_run_summary"]["plan_count"], result["metrics"]["cad_plans"])
        self.assertEqual(result["dry_run_summary"]["valid_count"], result["metrics"]["cad_plans"])
        self.assertEqual(result["verification_report"]["status"], "unverified")
        self.assertEqual(result["verification_summary"]["total"], result["metrics"]["cad_plans"])
        self.assertEqual(result["verification_summary"]["status_counts"], {"unverified": result["metrics"]["cad_plans"]})

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

    def test_candidate_sets_include_all_circulation_branches(self) -> None:
        workflow = load_json(PROJECT_ROOT / "examples/workflows/blank_shell_layout_loop.json")
        inputs = workflow["inputs"]
        brief = load_json(PROJECT_ROOT / inputs["design_brief"])
        drawing = load_json(PROJECT_ROOT / inputs["drawing_model"])
        shell = load_manual_shell(PROJECT_ROOT / inputs["shell_model"])
        project_model = build_project_model(brief, drawing, shell_model=shell).project_model
        circulation_candidates = generate_circulation_candidates(project_model, {})
        candidate_sets, *_ = build_blank_shell_candidate_sets(
            shell=shell,
            circulation_candidates=circulation_candidates,
            object_types=workflow.get("object_types", []),
            block_library=load_block_library(),
            placement_preferences={},
        )
        self.assertGreaterEqual(candidate_sets["counts"]["circulation_candidates"], 2)
        self.assertGreaterEqual(candidate_sets["counts"]["zone_placement_candidates"], 2)
        strategies = {branch["strategy"] for branch in candidate_sets["circulation_branches"]}
        self.assertIn("straight_spine", strategies)
        self.assertIn("l_spine", strategies)

    def test_blank_shell_dry_run_and_verification_cover_every_cad_plan(self) -> None:
        result = run_blank_shell_pipeline(
            PROJECT_ROOT / "examples/workflows/blank_shell_office_layout_loop.json",
            output_dir=artifact_path("blank_shell_pipeline", "all_plan_evidence"),
        )

        self.assertEqual(result["status"], "ok")
        dry_run_reports = json.loads(Path(result["artifacts"]["dry_run_reports"]).read_text(encoding="utf-8"))
        verification_reports = json.loads(Path(result["artifacts"]["verification_reports"]).read_text(encoding="utf-8"))
        self.assertEqual(len(dry_run_reports), result["metrics"]["cad_plans"])
        self.assertEqual(len(verification_reports), result["metrics"]["cad_plans"])
        self.assertTrue(all(report["status"] == "valid" for report in dry_run_reports))
        self.assertTrue(all(report["status"] == "unverified" for report in verification_reports))


if __name__ == "__main__":
    unittest.main()
