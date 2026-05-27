from __future__ import annotations

import unittest

from core.agents.scene_beta_explanation import (
    SCENE_BETA_EXPLANATION_DOC,
    SCENE_BETA_EXPLANATION_PACKAGE_ID,
    build_all_scene_beta_explanations,
    build_scene_beta_explanation,
    scene_beta_explanation_status_summary,
)
from core.agents.scene_beta import load_scene_beta_office_preferences
from tests.bootstrap import PROJECT_ROOT


class SceneProd05SceneExplanationTemplateTests(unittest.TestCase):
    def test_scene_beta_explanation_for_office_names_core_effects(self) -> None:
        preferences = load_scene_beta_office_preferences(root=PROJECT_ROOT)
        explanation = build_scene_beta_explanation(preferences)

        self.assertEqual(explanation["package_id"], SCENE_BETA_EXPLANATION_PACKAGE_ID)
        self.assertEqual(explanation["scenario"], "office")
        self.assertEqual(explanation["tier"], "beta")
        self.assertEqual(explanation["role"], "scene_preference_explanation")
        self.assertIn("examples/benchmarks/office_scene_beta_benchmark.json", explanation["benchmark_suite"])
        self.assertGreaterEqual(len(explanation["preference_to_core"]), 6)
        self.assertGreaterEqual(len(explanation["benchmark_observables"]), 4)
        self.assertIn("benchmark_pass_non_cad", explanation["evidence_boundaries"])
        self.assertIn("geometry_verified", " ".join(explanation["does_not_claim"]))

    def test_all_scene_beta_explanations_cover_three_scenarios(self) -> None:
        explanations = build_all_scene_beta_explanations(project_root=PROJECT_ROOT)
        self.assertEqual(set(explanations), {"office", "residential", "restaurant"})
        self.assertEqual(explanations["office"]["observable_signature"]["preferred_circulation_strategy"], "straight_spine")
        self.assertEqual(explanations["residential"]["observable_signature"]["preferred_circulation_strategy"], "along_wall")
        self.assertEqual(explanations["restaurant"]["observable_signature"]["preferred_circulation_strategy"], "l_spine")

    def test_status_summary(self) -> None:
        summary = scene_beta_explanation_status_summary(project_root=PROJECT_ROOT)
        self.assertEqual(summary["package_id"], SCENE_BETA_EXPLANATION_PACKAGE_ID)
        self.assertTrue(summary["doc_present"])
        self.assertEqual(summary["scenario_count"], 3)
        self.assertEqual(summary["benchmark_suite_count"], 3)
        self.assertEqual(summary["readback_geometry_verified_count"], 0)

    def test_explanation_doc_states_boundaries(self) -> None:
        text = (PROJECT_ROOT / SCENE_BETA_EXPLANATION_DOC).read_text(encoding="utf-8")
        for phrase in (
            "SCENE-PROD-05",
            "BETA-SCENE-04",
            "build_scene_beta_explanation",
            "benchmark_pass_non_cad",
            "blocked_expected_non_cad",
            "geometry_verified",
            "不得声称",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_handoff_indexes_scene_prod_05(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("SCENE-PROD-05", handoff)
        self.assertIn("scene_prod_05_scene_explanation_template.md", handoff)


if __name__ == "__main__":
    unittest.main()
