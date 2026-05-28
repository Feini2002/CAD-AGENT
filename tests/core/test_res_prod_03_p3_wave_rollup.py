from __future__ import annotations

import unittest

from core.agents.residential_beta_boundary import run_residential_beta_boundary_smoke
from core.agents.residential_p3_wave import (
    RESIDENTIAL_P3_ACCEPTANCE_DOC,
    RESIDENTIAL_P3_BOUNDARY_DOCS,
    RESIDENTIAL_P3_WAVE_PACKAGE_ID,
    assert_residential_p3_wave_contract,
    residential_p3_wave_status_summary,
)
from core.benchmarks.runner import run_benchmark_suite
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class ResProd03P3WaveRollupTests(unittest.TestCase):
    def test_residential_p3_wave_contract(self) -> None:
        assert_residential_p3_wave_contract(project_root=PROJECT_ROOT)

    def test_residential_p3_status_summary(self) -> None:
        summary = residential_p3_wave_status_summary(project_root=PROJECT_ROOT)
        self.assertTrue(summary["docs_present"])
        self.assertEqual(summary["package_id"], RESIDENTIAL_P3_WAVE_PACKAGE_ID)
        self.assertEqual(summary["child_package_count"], 2)
        self.assertEqual(summary["alpha_case_count"], 1)
        self.assertEqual(summary["beta_case_count"], 8)

    def test_acceptance_doc_closes_residential_wave(self) -> None:
        text = (PROJECT_ROOT / RESIDENTIAL_P3_ACCEPTANCE_DOC).read_text(encoding="utf-8")
        for short_id in ("RESIDENTIAL-PROD-01", "RESIDENTIAL-PROD-02", "RESIDENTIAL-PROD-03"):
            with self.subTest(short_id=short_id):
                self.assertIn(short_id, text)
        for phrase in (
            "assert_residential_p3_wave_contract",
            "residential-prod-alpha-01",
            "residential-prod-beta-01",
            "benchmark_pass_non_cad",
            "blocked_expected_non_cad",
            "BETA-SCENE-02",
            "geometry_verified",
            "不得声称",
            "RESIDENTIAL-PROD",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_all_boundary_docs_exist(self) -> None:
        for rel in RESIDENTIAL_P3_BOUNDARY_DOCS:
            with self.subTest(doc=rel):
                self.assertTrue((PROJECT_ROOT / rel).is_file())

    def test_residential_alpha_and_beta_no_cad_rerun(self) -> None:
        alpha = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/scene_alpha_benchmark.json",
            output_root=artifact_path("res_prod_03", "alpha_no_cad"),
        )
        self.assertEqual(alpha["status"], "pass")
        by_id = {case["case_id"]: case for case in alpha["cases"]}
        self.assertEqual(
            by_id["scene_alpha_residential_blank_shell"]["actual"]["evidence_state"],
            "benchmark_pass_non_cad",
        )

        beta = run_residential_beta_boundary_smoke(
            project_root=PROJECT_ROOT,
            output_root=artifact_path("res_prod_03", "beta_no_cad"),
        )
        self.assertEqual(beta["status"], "pass")
        self.assertEqual(beta["summary"]["passed"], 8)
        self.assertEqual(beta["evidence_summary"]["readback_geometry_verified_count"], 0)

    def test_handoff_indexes_res_prod_03(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("RESIDENTIAL-PROD-03", handoff)
        self.assertIn("residential_prod_03_p3_wave_acceptance.md", handoff)


if __name__ == "__main__":
    unittest.main()
