from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.agents.scene_alpha import SCENE_ALPHA_SCENARIOS, load_scene_preferences
from core.agents.scene_explanation import (
    RULES_SECTION_NOT_CLAIM,
    RULES_SECTION_PREFERENCE_CORE,
    build_scene_explanation,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class SceneExplanationTests(unittest.TestCase):
    def test_x_scene_04_build_explanation_matches_manifest(self) -> None:
        manifest = json.loads((PROJECT_ROOT / "agents" / "scene_alpha_manifest.json").read_text(encoding="utf-8"))
        expected_by_scenario = {
            entry["scenario"]: entry["expected"] for entry in manifest["scenarios"]
        }

        for scenario in SCENE_ALPHA_SCENARIOS:
            with self.subTest(scenario=scenario):
                preferences = load_scene_preferences(scenario, root=PROJECT_ROOT)
                explanation = build_scene_explanation(preferences)
                expected = expected_by_scenario[scenario]
                signature = explanation["observable_signature"]

                self.assertEqual(explanation["scenario"], scenario)
                self.assertEqual(explanation["role"], "scene_preference_layer")
                self.assertEqual(signature["primary_object_type"], expected["primary_object_type"])
                self.assertEqual(
                    signature["preferred_circulation_strategy"],
                    expected["preferred_circulation_strategy"],
                )
                self.assertGreaterEqual(len(explanation["preference_to_core"]), 5)
                self.assertGreaterEqual(len(explanation["does_not_claim"]), 2)

    def test_x_scene_04_alpha_rules_include_explanation_sections(self) -> None:
        for scenario in SCENE_ALPHA_SCENARIOS:
            with self.subTest(scenario=scenario):
                rules = (PROJECT_ROOT / "agents" / scenario / "rules.md").read_text(encoding="utf-8")
                self.assertIn(RULES_SECTION_PREFERENCE_CORE, rules)
                self.assertIn(RULES_SECTION_NOT_CLAIM, rules)
                self.assertIn("geometry_verified", rules)
                self.assertIn("blank_shell", rules.lower())

    def test_x_scene_04_explanation_template_doc_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "verification" / "scene_alpha_explanation_template.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("benchmark_pass_non_cad", text)
        self.assertIn("geometry_verified", text)
        self.assertIn("build_scene_explanation", text)

    def test_x_scene_04_first_handoff_documents_scene_alpha_limits(self) -> None:
        handoff = (PROJECT_ROOT / "docs" / "onboarding" / "first-handoff.md").read_text(encoding="utf-8")
        required = [
            "Scene Alpha",
            "benchmark_pass_non_cad",
            "geometry_verified",
            "scene_alpha_explanation_template",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, handoff)


if __name__ == "__main__":
    unittest.main()
