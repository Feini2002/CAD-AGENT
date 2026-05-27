from __future__ import annotations

import unittest

from core.agents.restaurant_beta_boundary import (
    EXPECTED_RESTAURANT_BETA_CASE_COUNT,
    REST_PROD_02_BOUNDARY_DOC,
    REST_PROD_02_PACKAGE_ID,
    assert_restaurant_beta_boundary_contract,
    default_manifest_path,
    load_restaurant_prod_beta_manifest,
    restaurant_beta_boundary_status_summary,
    run_restaurant_beta_boundary_smoke,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class RestProd02RestaurantBetaBoundaryTests(unittest.TestCase):
    def test_rest_prod_02_contract(self) -> None:
        assert_restaurant_beta_boundary_contract(project_root=PROJECT_ROOT)

    def test_manifest_ids(self) -> None:
        manifest = load_restaurant_prod_beta_manifest(default_manifest_path(PROJECT_ROOT))
        self.assertEqual(manifest["manifest_id"], "restaurant-prod-beta-01")
        self.assertEqual(manifest["package_id"], REST_PROD_02_PACKAGE_ID)
        self.assertEqual(manifest["scenario"], "restaurant")
        self.assertEqual(len(manifest["required_case_tiers"]), 6)

    def test_restaurant_beta_benchmark_eight_pass(self) -> None:
        result = run_restaurant_beta_boundary_smoke(
            project_root=PROJECT_ROOT,
            output_root=artifact_path("rest_prod_02", "beta_no_cad"),
        )
        self.assertEqual(result.get("preference_validation"), "pass", result)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"]["passed"], EXPECTED_RESTAURANT_BETA_CASE_COUNT)
        evidence = result["evidence_summary"]
        self.assertEqual(evidence["benchmark_pass_non_cad_count"], 7)
        self.assertEqual(evidence["blocked_expected_non_cad_count"], 1)
        self.assertEqual(evidence.get("readback_geometry_verified_count"), 0)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / REST_PROD_02_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "REST-PROD-02",
            "restaurant-prod-beta-01",
            "restaurant-scene-beta-benchmark",
            "assert_restaurant_beta_boundary_contract",
            "BETA-SCENE-03",
            "benchmark_pass_non_cad",
            "blocked_expected_non_cad",
            "geometry_verified",
            "不得声称",
            "REST-PROD-01",
            "dry_run_valid_plan_only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_status_summary(self) -> None:
        summary = restaurant_beta_boundary_status_summary(project_root=PROJECT_ROOT)
        self.assertEqual(summary["package_id"], REST_PROD_02_PACKAGE_ID)
        self.assertEqual(summary["expected_case_count"], 8)

    def test_handoff_indexes_rest_prod_02(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("REST-PROD-02", handoff)
        self.assertIn("restaurant_prod_02_restaurant_beta_boundary.md", handoff)


if __name__ == "__main__":
    unittest.main()
