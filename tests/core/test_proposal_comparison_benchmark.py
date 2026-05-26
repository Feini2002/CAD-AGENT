from __future__ import annotations

import json
import unittest

from core.proposal_engine.benchmark import default_proposal_comparison_benchmark_path, run_proposal_comparison_benchmark
from core.proposal_engine.comparison_summary import (
    build_proposal_comparison_summary,
    validate_proposal_comparison_summary,
)
from core.proposal_engine.proposal_comparison import build_blank_shell_comparison_detail
from core.workflows.blank_shell_pipeline import build_blank_shell_candidate_sets
from core.layout_engine.path_generation import generate_circulation_candidates
from core.project_model.project_builder import build_project_model
from core.drawing_analysis.shell_loader import load_manual_shell
from core.block_engine.block_library import load_block_library
from core.schemas.validator import validate_value
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class ProposalComparisonBenchmarkTests(unittest.TestCase):
    def test_beta_proposal_02_summary_schema_fields(self) -> None:
        workflow = json.loads(
            (PROJECT_ROOT / "examples/workflows/blank_shell_layout_loop.json").read_text(encoding="utf-8")
        )
        inputs = workflow["inputs"]
        brief = json.loads((PROJECT_ROOT / inputs["design_brief"]).read_text(encoding="utf-8"))
        drawing = json.loads((PROJECT_ROOT / inputs["drawing_model"]).read_text(encoding="utf-8"))
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
        detail = build_blank_shell_comparison_detail(
            candidate_sets=candidate_sets,
            layout_proposal={
                "layout_id": "layout-test",
                "candidates": [{"candidate_id": "c1", "score": 1.0, "checks": [], "placements": []}],
            },
            object_types=workflow.get("object_types", []),
        )
        summary = detail["proposal_comparison_summary"]
        self.assertEqual(validate_proposal_comparison_summary(summary), [])
        schema = json.loads(
            (PROJECT_ROOT / "core/schemas/proposal_comparison_summary.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(validate_value(summary, schema), [])
        self.assertIn("object_coverage", summary)
        self.assertIn("circulation", summary)
        self.assertIn("conflicts", summary)
        self.assertIn("failure_reasons", summary)

    def test_beta_proposal_02_benchmark_suite_passes(self) -> None:
        output_root = artifact_path("benchmarks", "beta_proposal_02")
        result = run_proposal_comparison_benchmark(project_root=PROJECT_ROOT, output_root=output_root)

        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 4, "passed": 4, "failed": 0})
        evidence = result["evidence_summary"]
        self.assertEqual(evidence["case_count"], 4)
        self.assertEqual(evidence.get("readback_geometry_verified_count", 0), 0)

        by_id = {case["case_id"]: case for case in result["cases"]}
        retail = by_id["retail_comparison_summary"]
        self.assertTrue(retail["actual"].get("has_proposal_comparison_summary"))
        self.assertGreaterEqual(retail["actual"]["object_coverage_rate"], 0.6)

        residential = by_id["residential_full_coverage_summary"]
        self.assertEqual(residential["actual"]["object_coverage_rate"], 1.0)
        self.assertIn("zone_placement_best", residential["actual"].get("ranking_reason_codes", []))

        summary_path = output_root / "benchmark_summary.json"
        self.assertTrue(summary_path.is_file())

    def test_proposal_comparison_benchmark_suite_file_exists(self) -> None:
        path = default_proposal_comparison_benchmark_path(PROJECT_ROOT)
        self.assertTrue(path.is_file())
        suite = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(suite["suite_id"], "proposal-comparison-benchmark")


if __name__ == "__main__":
    unittest.main()
