from __future__ import annotations

import unittest

from core.agents.office_beta_boundary import (
    EXPECTED_OFFICE_BETA_CASE_COUNT,
    OFFICE_PROD_02_BOUNDARY_DOC,
    OFFICE_PROD_02_PACKAGE_ID,
    assert_office_beta_boundary_contract,
    default_manifest_path,
    load_office_prod_beta_manifest,
    office_beta_boundary_status_summary,
    run_office_beta_boundary_smoke,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class OfficeProd02OfficeBetaBoundaryTests(unittest.TestCase):
    def test_office_prod_02_contract(self) -> None:
        assert_office_beta_boundary_contract(project_root=PROJECT_ROOT)

    def test_manifest_ids(self) -> None:
        manifest = load_office_prod_beta_manifest(default_manifest_path(PROJECT_ROOT))
        self.assertEqual(manifest["manifest_id"], "office-prod-beta-01")
        self.assertEqual(manifest["package_id"], OFFICE_PROD_02_PACKAGE_ID)
        self.assertEqual(len(manifest["required_case_tiers"]), 4)

    def test_office_beta_benchmark_nine_pass(self) -> None:
        result = run_office_beta_boundary_smoke(
            project_root=PROJECT_ROOT,
            output_root=artifact_path("office_prod_02", "beta_no_cad"),
        )
        self.assertEqual(result.get("preference_validation"), "pass", result)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"]["passed"], EXPECTED_OFFICE_BETA_CASE_COUNT)
        evidence = result["evidence_summary"]
        self.assertEqual(evidence["benchmark_pass_non_cad_count"], 7)
        self.assertEqual(evidence["blocked_expected_non_cad_count"], 2)
        self.assertEqual(evidence.get("readback_geometry_verified_count"), 0)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / OFFICE_PROD_02_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "OFFICE-PROD-02",
            "office-prod-beta-01",
            "office-scene-beta-benchmark",
            "assert_office_beta_boundary_contract",
            "BETA-SCENE-01",
            "benchmark_pass_non_cad",
            "blocked_expected_non_cad",
            "V-PROOF-24",
            "geometry_verified",
            "不得声称",
            "OFFICE-PROD-01",
            "dry_run_valid_plan_only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_status_summary(self) -> None:
        summary = office_beta_boundary_status_summary(project_root=PROJECT_ROOT)
        self.assertEqual(summary["package_id"], OFFICE_PROD_02_PACKAGE_ID)
        self.assertEqual(summary["expected_case_count"], 9)

    def test_handoff_indexes_office_prod_02(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("OFFICE-PROD-02", handoff)
        self.assertIn("office_prod_02_office_beta_boundary.md", handoff)


if __name__ == "__main__":
    unittest.main()
