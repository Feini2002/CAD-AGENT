from __future__ import annotations

import json
import unittest

from core.agents.healthcare_scene_beta import run_healthcare_scene_beta_benchmark
from core.agents.scene_beta import (
    default_healthcare_scene_beta_benchmark_path,
    load_scene_beta_healthcare_preferences,
    scene_beta_observable_signature,
    validate_scene_beta_healthcare_preferences,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class SceneBetaHealthcareTests(unittest.TestCase):
    def test_beta_scene_04_healthcare_preferences_contract(self) -> None:
        preferences = load_scene_beta_healthcare_preferences(root=PROJECT_ROOT)
        errors = validate_scene_beta_healthcare_preferences(preferences)
        self.assertEqual(errors, [], errors)
        signature = scene_beta_observable_signature(preferences)
        self.assertEqual(signature["tier"], "beta")
        self.assertEqual(signature["preferred_circulation_strategy"], "straight_spine")
        self.assertEqual(signature["primary_object_type"], "cabinet")

    def test_beta_scene_04_healthcare_benchmark_passes(self) -> None:
        output_root = artifact_path("benchmarks", "beta_scene_04_healthcare")
        result = run_healthcare_scene_beta_benchmark(project_root=PROJECT_ROOT, output_root=output_root)

        self.assertEqual(result.get("preference_validation"), "pass", result)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 6, "passed": 6, "failed": 0})
        evidence = result["evidence_summary"]
        self.assertEqual(evidence["benchmark_pass_non_cad_count"], 5)
        self.assertEqual(evidence["blocked_expected_non_cad_count"], 1)

        suite = json.loads(default_healthcare_scene_beta_benchmark_path(PROJECT_ROOT).read_text(encoding="utf-8"))
        tiers = {case["case_tier"] for case in suite["cases"]}
        self.assertEqual(
            tiers,
            {"object", "clinical", "waiting", "blank_shell", "failure"},
        )


if __name__ == "__main__":
    unittest.main()
