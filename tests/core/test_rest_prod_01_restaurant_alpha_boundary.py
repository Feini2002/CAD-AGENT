from __future__ import annotations

import unittest

from core.agents.restaurant_alpha_boundary import (
    EXPECTED_RESTAURANT_ALPHA_CASE_COUNT,
    REST_PROD_01_BOUNDARY_DOC,
    REST_PROD_01_PACKAGE_ID,
    assert_restaurant_alpha_boundary_contract,
    default_manifest_path,
    load_restaurant_prod_alpha_manifest,
    restaurant_alpha_boundary_status_summary,
)
from core.agents.scene_alpha import load_scene_preferences, validate_scene_alpha_preferences
from core.benchmarks.runner import run_benchmark_suite
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class RestProd01RestaurantAlphaBoundaryTests(unittest.TestCase):
    def test_rest_prod_01_contract(self) -> None:
        assert_restaurant_alpha_boundary_contract(project_root=PROJECT_ROOT)

    def test_manifest_ids(self) -> None:
        manifest = load_restaurant_prod_alpha_manifest(default_manifest_path(PROJECT_ROOT))
        self.assertEqual(manifest["manifest_id"], "restaurant-prod-alpha-01")
        self.assertEqual(manifest["package_id"], REST_PROD_01_PACKAGE_ID)
        self.assertEqual(manifest["scenario"], "restaurant")

    def test_restaurant_preferences_validate(self) -> None:
        preferences = load_scene_preferences("restaurant", root=PROJECT_ROOT)
        self.assertEqual(preferences["scenario"], "restaurant")
        self.assertEqual(validate_scene_alpha_preferences(preferences, scenario="restaurant"), [])

    def test_restaurant_alpha_benchmark_case_passes(self) -> None:
        result = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/scene_alpha_benchmark.json",
            output_root=artifact_path("rest_prod_01", "benchmark_no_cad"),
        )
        self.assertEqual(result["status"], "pass", result)
        by_id = {case["case_id"]: case for case in result["cases"]}
        restaurant_case = by_id["scene_alpha_restaurant_blank_shell"]
        self.assertEqual(restaurant_case["actual"]["preferences_scenario"], "restaurant")
        self.assertEqual(restaurant_case["actual"]["selected_circulation_strategy"], "l_spine")
        self.assertEqual(restaurant_case["actual"]["evidence_state"], "benchmark_pass_non_cad")
        self.assertEqual(EXPECTED_RESTAURANT_ALPHA_CASE_COUNT, 1)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / REST_PROD_01_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "REST-PROD-01",
            "restaurant-prod-alpha-01",
            "scene-alpha-benchmark",
            "scene_alpha_restaurant_blank_shell",
            "assert_restaurant_alpha_boundary_contract",
            "benchmark_pass_non_cad",
            "BETA-SCENE-03",
            "geometry_verified",
            "不得声称",
            "OFFICE-PROD-01",
            "dry_run_valid_plan_only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_status_summary(self) -> None:
        summary = restaurant_alpha_boundary_status_summary(project_root=PROJECT_ROOT)
        self.assertEqual(summary["package_id"], REST_PROD_01_PACKAGE_ID)
        self.assertEqual(summary["expected_case_count"], 1)

    def test_handoff_indexes_rest_prod_01(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("REST-PROD-01", handoff)
        self.assertIn("restaurant_prod_01_restaurant_alpha_boundary.md", handoff)


if __name__ == "__main__":
    unittest.main()
