from __future__ import annotations

import json
import unittest

from core.agents.residential_scene_beta import run_residential_scene_beta_benchmark
from core.agents.scene_beta import (
    default_residential_scene_beta_benchmark_path,
    load_scene_beta_residential_preferences,
    residential_beta_observable_signature,
    validate_scene_beta_residential_preferences,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class SceneBetaResidentialTests(unittest.TestCase):
    def test_beta_scene_02_residential_preferences_contract(self) -> None:
        preferences = load_scene_beta_residential_preferences(root=PROJECT_ROOT)
        errors = validate_scene_beta_residential_preferences(preferences)
        self.assertEqual(errors, [], errors)
        signature = residential_beta_observable_signature(preferences)
        self.assertEqual(signature["tier"], "beta")
        self.assertEqual(signature["preferred_circulation_strategy"], "along_wall")
        self.assertEqual(signature["primary_object_type"], "cabinet")
        self.assertIn("bed", preferences["object_preferences"])
        self.assertIn("sofa", preferences["object_preferences"])

    def test_beta_scene_02_residential_benchmark_passes(self) -> None:
        output_root = artifact_path("benchmarks", "beta_scene_02")
        result = run_residential_scene_beta_benchmark(project_root=PROJECT_ROOT, output_root=output_root)

        self.assertEqual(result.get("preference_validation"), "pass", result)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 8, "passed": 8, "failed": 0})
        evidence = result["evidence_summary"]
        self.assertEqual(evidence["benchmark_pass_non_cad_count"], 7)
        self.assertEqual(evidence["blocked_expected_non_cad_count"], 1)

        suite = json.loads(default_residential_scene_beta_benchmark_path(PROJECT_ROOT).read_text(encoding="utf-8"))
        tiers = {case["case_tier"] for case in suite["cases"]}
        self.assertEqual(tiers, {"object", "bedroom", "dining", "storage", "blank_shell", "failure"})


if __name__ == "__main__":
    unittest.main()
