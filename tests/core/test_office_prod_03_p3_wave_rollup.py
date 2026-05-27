from __future__ import annotations

import unittest

from core.agents.office_p3_wave import (
    OFFICE_P3_ACCEPTANCE_DOC,
    OFFICE_P3_BOUNDARY_DOCS,
    OFFICE_P3_WAVE_PACKAGE_ID,
    assert_office_p3_wave_contract,
    office_p3_wave_status_summary,
)
from core.agents.office_beta_boundary import run_office_beta_boundary_smoke
from core.benchmarks.runner import run_benchmark_suite
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class OfficeProd03P3WaveRollupTests(unittest.TestCase):
    def test_office_p3_wave_contract(self) -> None:
        assert_office_p3_wave_contract(project_root=PROJECT_ROOT)

    def test_office_p3_status_summary(self) -> None:
        summary = office_p3_wave_status_summary(project_root=PROJECT_ROOT)
        self.assertTrue(summary["docs_present"])
        self.assertEqual(summary["package_id"], OFFICE_P3_WAVE_PACKAGE_ID)
        self.assertEqual(summary["child_package_count"], 2)
        self.assertEqual(summary["alpha_case_count"], 18)
        self.assertEqual(summary["beta_case_count"], 9)

    def test_acceptance_doc_closes_office_wave(self) -> None:
        text = (PROJECT_ROOT / OFFICE_P3_ACCEPTANCE_DOC).read_text(encoding="utf-8")
        for short_id in ("OFFICE-PROD-01", "OFFICE-PROD-02", "OFFICE-PROD-03"):
            with self.subTest(short_id=short_id):
                self.assertIn(short_id, text)
        for phrase in (
            "assert_office_p3_wave_contract",
            "office-prod-alpha-01",
            "office-prod-beta-01",
            "benchmark_pass_non_cad",
            "blocked_expected_non_cad",
            "V-PROOF-24",
            "geometry_verified",
            "不得声称",
            "REST-PROD-01",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_all_boundary_docs_exist(self) -> None:
        for rel in OFFICE_P3_BOUNDARY_DOCS:
            with self.subTest(doc=rel):
                self.assertTrue((PROJECT_ROOT / rel).is_file())

    def test_office_alpha_and_beta_no_cad_rerun(self) -> None:
        alpha = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/office_alpha_benchmark.json",
            output_root=artifact_path("office_prod_03", "alpha_no_cad"),
        )
        self.assertEqual(alpha["status"], "pass")
        self.assertEqual(alpha["summary"]["passed"], 18)

        beta = run_office_beta_boundary_smoke(
            project_root=PROJECT_ROOT,
            output_root=artifact_path("office_prod_03", "beta_no_cad"),
        )
        self.assertEqual(beta["status"], "pass")
        self.assertEqual(beta["summary"]["passed"], 9)
        self.assertEqual(beta["evidence_summary"]["readback_geometry_verified_count"], 0)

    def test_handoff_indexes_office_prod_03(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("OFFICE-PROD-03", handoff)
        self.assertIn("office_prod_03_p3_wave_acceptance.md", handoff)


if __name__ == "__main__":
    unittest.main()
