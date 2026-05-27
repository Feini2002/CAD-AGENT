from __future__ import annotations

import unittest

from core.agents.scene_regression_gate import (
    SCENE_PROD_06_ACCEPTANCE_DOC,
    SCENE_PROD_06_PACKAGE_ID,
    assert_scene_prod_06_regression_gate_contract,
    run_scene_prod_06_regression_gate,
    scene_prod_06_status_summary,
)
from tests.bootstrap import PROJECT_ROOT


class SceneProd06RegressionGateTests(unittest.TestCase):
    def test_scene_prod_06_contract_runs_selected_scene_benchmarks(self) -> None:
        assert_scene_prod_06_regression_gate_contract(project_root=PROJECT_ROOT)

    def test_regression_gate_summary_covers_three_scene_beta_suites(self) -> None:
        summary = run_scene_prod_06_regression_gate(
            project_root=PROJECT_ROOT,
            output_root=PROJECT_ROOT / "output" / "test_artifacts" / "scene-prod-06-regression-gate",
        )

        self.assertEqual(summary["package_id"], SCENE_PROD_06_PACKAGE_ID)
        self.assertEqual(summary["status"], "pass")
        self.assertEqual(summary["scenario_count"], 3)
        self.assertEqual(set(summary["scenarios"]), {"office", "residential", "restaurant"})
        self.assertEqual(summary["benchmark_total_count"], 25)
        self.assertEqual(summary["benchmark_passed_count"], 25)
        self.assertEqual(summary["readback_geometry_verified_count"], 0)
        self.assertTrue(summary["non_cad_only"])

    def test_status_summary_names_boundaries_without_running_benchmarks(self) -> None:
        summary = scene_prod_06_status_summary(project_root=PROJECT_ROOT)

        self.assertEqual(summary["package_id"], SCENE_PROD_06_PACKAGE_ID)
        self.assertTrue(summary["doc_present"])
        self.assertEqual(summary["scenario_count"], 3)
        self.assertIn("benchmark_pass_non_cad", summary["evidence_boundaries"])
        self.assertIn("not_verified_without_cad_readback", summary["evidence_boundaries"])

    def test_acceptance_doc_states_no_cad_boundary(self) -> None:
        text = (PROJECT_ROOT / SCENE_PROD_06_ACCEPTANCE_DOC).read_text(encoding="utf-8")
        for phrase in (
            "SCENE-PROD-06",
            "BETA-SCENE-05",
            "run_scene_prod_06_regression_gate",
            "office",
            "residential",
            "restaurant",
            "benchmark_pass_non_cad",
            "geometry_verified",
            "repo audit",
            "不得声称",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
