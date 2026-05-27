from __future__ import annotations

import unittest

from core.agents.restaurant_beta_boundary import run_restaurant_beta_boundary_smoke
from core.agents.restaurant_p3_wave import (
    RESTAURANT_P3_ACCEPTANCE_DOC,
    RESTAURANT_P3_BOUNDARY_DOCS,
    RESTAURANT_P3_WAVE_PACKAGE_ID,
    assert_restaurant_p3_wave_contract,
    restaurant_p3_wave_status_summary,
)
from core.benchmarks.runner import run_benchmark_suite
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class RestProd03P3WaveRollupTests(unittest.TestCase):
    def test_restaurant_p3_wave_contract(self) -> None:
        assert_restaurant_p3_wave_contract(project_root=PROJECT_ROOT)

    def test_restaurant_p3_status_summary(self) -> None:
        summary = restaurant_p3_wave_status_summary(project_root=PROJECT_ROOT)
        self.assertTrue(summary["docs_present"])
        self.assertEqual(summary["package_id"], RESTAURANT_P3_WAVE_PACKAGE_ID)
        self.assertEqual(summary["child_package_count"], 2)
        self.assertEqual(summary["alpha_case_count"], 1)
        self.assertEqual(summary["beta_case_count"], 8)

    def test_acceptance_doc_closes_restaurant_wave(self) -> None:
        text = (PROJECT_ROOT / RESTAURANT_P3_ACCEPTANCE_DOC).read_text(encoding="utf-8")
        for short_id in ("REST-PROD-01", "REST-PROD-02", "REST-PROD-03"):
            with self.subTest(short_id=short_id):
                self.assertIn(short_id, text)
        for phrase in (
            "assert_restaurant_p3_wave_contract",
            "restaurant-prod-alpha-01",
            "restaurant-prod-beta-01",
            "benchmark_pass_non_cad",
            "blocked_expected_non_cad",
            "BETA-SCENE-03",
            "geometry_verified",
            "不得声称",
            "REST-PROD",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_all_boundary_docs_exist(self) -> None:
        for rel in RESTAURANT_P3_BOUNDARY_DOCS:
            with self.subTest(doc=rel):
                self.assertTrue((PROJECT_ROOT / rel).is_file())

    def test_restaurant_alpha_and_beta_no_cad_rerun(self) -> None:
        alpha = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/scene_alpha_benchmark.json",
            output_root=artifact_path("rest_prod_03", "alpha_no_cad"),
        )
        self.assertEqual(alpha["status"], "pass")
        by_id = {case["case_id"]: case for case in alpha["cases"]}
        self.assertEqual(by_id["scene_alpha_restaurant_blank_shell"]["actual"]["evidence_state"], "benchmark_pass_non_cad")

        beta = run_restaurant_beta_boundary_smoke(
            project_root=PROJECT_ROOT,
            output_root=artifact_path("rest_prod_03", "beta_no_cad"),
        )
        self.assertEqual(beta["status"], "pass")
        self.assertEqual(beta["summary"]["passed"], 8)
        self.assertEqual(beta["evidence_summary"]["readback_geometry_verified_count"], 0)

    def test_handoff_indexes_rest_prod_03(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("REST-PROD-03", handoff)
        self.assertIn("restaurant_prod_03_p3_wave_acceptance.md", handoff)


if __name__ == "__main__":
    unittest.main()
