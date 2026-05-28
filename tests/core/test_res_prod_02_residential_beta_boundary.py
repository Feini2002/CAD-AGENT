from __future__ import annotations

import unittest

from core.agents.residential_beta_boundary import (
    EXPECTED_RESIDENTIAL_BETA_CASE_COUNT,
    RESIDENTIAL_PROD_02_BOUNDARY_DOC,
    RESIDENTIAL_PROD_02_PACKAGE_ID,
    assert_residential_beta_boundary_contract,
    default_manifest_path,
    load_residential_prod_beta_manifest,
    residential_beta_boundary_status_summary,
    run_residential_beta_boundary_smoke,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class ResProd02ResidentialBetaBoundaryTests(unittest.TestCase):
    def test_res_prod_02_contract(self) -> None:
        assert_residential_beta_boundary_contract(project_root=PROJECT_ROOT)

    def test_manifest_ids(self) -> None:
        manifest = load_residential_prod_beta_manifest(default_manifest_path(PROJECT_ROOT))
        self.assertEqual(manifest["manifest_id"], "residential-prod-beta-01")
        self.assertEqual(manifest["package_id"], RESIDENTIAL_PROD_02_PACKAGE_ID)
        self.assertEqual(manifest["scenario"], "residential")
        self.assertEqual(len(manifest["required_case_tiers"]), 6)

    def test_residential_beta_benchmark_eight_pass(self) -> None:
        result = run_residential_beta_boundary_smoke(
            project_root=PROJECT_ROOT,
            output_root=artifact_path("res_prod_02", "beta_no_cad"),
        )
        self.assertEqual(result.get("preference_validation"), "pass", result)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"]["passed"], EXPECTED_RESIDENTIAL_BETA_CASE_COUNT)
        evidence = result["evidence_summary"]
        self.assertEqual(evidence["benchmark_pass_non_cad_count"], 7)
        self.assertEqual(evidence["blocked_expected_non_cad_count"], 1)
        self.assertEqual(evidence.get("readback_geometry_verified_count"), 0)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / RESIDENTIAL_PROD_02_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "RESIDENTIAL-PROD-02",
            "residential-prod-beta-01",
            "residential-scene-beta-benchmark",
            "assert_residential_beta_boundary_contract",
            "BETA-SCENE-02",
            "benchmark_pass_non_cad",
            "blocked_expected_non_cad",
            "geometry_verified",
            "不得声称",
            "RESIDENTIAL-PROD-01",
            "dry_run_valid_plan_only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_status_summary(self) -> None:
        summary = residential_beta_boundary_status_summary(project_root=PROJECT_ROOT)
        self.assertEqual(summary["package_id"], RESIDENTIAL_PROD_02_PACKAGE_ID)
        self.assertEqual(summary["expected_case_count"], 8)

    def test_handoff_indexes_res_prod_02(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("RESIDENTIAL-PROD-02", handoff)
        self.assertIn("residential_prod_02_residential_beta_boundary.md", handoff)


if __name__ == "__main__":
    unittest.main()
