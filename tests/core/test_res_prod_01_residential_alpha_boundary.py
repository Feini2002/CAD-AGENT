from __future__ import annotations

import unittest

from core.agents.residential_alpha_boundary import (
    EXPECTED_RESIDENTIAL_ALPHA_CASE_COUNT,
    RESIDENTIAL_PROD_01_BOUNDARY_DOC,
    RESIDENTIAL_PROD_01_PACKAGE_ID,
    assert_residential_alpha_boundary_contract,
    default_manifest_path,
    load_residential_prod_alpha_manifest,
    residential_alpha_boundary_status_summary,
)
from core.agents.scene_alpha import load_scene_preferences, validate_scene_alpha_preferences
from core.benchmarks.runner import run_benchmark_suite
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class ResProd01ResidentialAlphaBoundaryTests(unittest.TestCase):
    def test_res_prod_01_contract(self) -> None:
        assert_residential_alpha_boundary_contract(project_root=PROJECT_ROOT)

    def test_manifest_ids(self) -> None:
        manifest = load_residential_prod_alpha_manifest(default_manifest_path(PROJECT_ROOT))
        self.assertEqual(manifest["manifest_id"], "residential-prod-alpha-01")
        self.assertEqual(manifest["package_id"], RESIDENTIAL_PROD_01_PACKAGE_ID)
        self.assertEqual(manifest["scenario"], "residential")

    def test_residential_preferences_validate(self) -> None:
        preferences = load_scene_preferences("residential", root=PROJECT_ROOT)
        self.assertEqual(preferences["scenario"], "residential")
        self.assertEqual(validate_scene_alpha_preferences(preferences, scenario="residential"), [])

    def test_residential_alpha_benchmark_case_passes(self) -> None:
        result = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/scene_alpha_benchmark.json",
            output_root=artifact_path("res_prod_01", "benchmark_no_cad"),
        )
        self.assertEqual(result["status"], "pass", result)
        by_id = {case["case_id"]: case for case in result["cases"]}
        residential_case = by_id["scene_alpha_residential_blank_shell"]
        self.assertEqual(residential_case["actual"]["preferences_scenario"], "residential")
        self.assertEqual(residential_case["actual"]["selected_circulation_strategy"], "along_wall")
        self.assertEqual(residential_case["actual"]["evidence_state"], "benchmark_pass_non_cad")
        self.assertEqual(EXPECTED_RESIDENTIAL_ALPHA_CASE_COUNT, 1)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / RESIDENTIAL_PROD_01_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "RESIDENTIAL-PROD-01",
            "residential-prod-alpha-01",
            "scene-alpha-benchmark",
            "scene_alpha_residential_blank_shell",
            "assert_residential_alpha_boundary_contract",
            "benchmark_pass_non_cad",
            "BETA-SCENE-02",
            "geometry_verified",
            "不得声称",
            "OFFICE-PROD-01",
            "REST-PROD-01",
            "dry_run_valid_plan_only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_status_summary(self) -> None:
        summary = residential_alpha_boundary_status_summary(project_root=PROJECT_ROOT)
        self.assertEqual(summary["package_id"], RESIDENTIAL_PROD_01_PACKAGE_ID)
        self.assertEqual(summary["expected_case_count"], 1)

    def test_handoff_indexes_res_prod_01(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("RESIDENTIAL-PROD-01", handoff)
        self.assertIn("residential_prod_01_residential_alpha_boundary.md", handoff)


if __name__ == "__main__":
    unittest.main()
