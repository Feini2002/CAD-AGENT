from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.agents.office_scene_beta import run_office_scene_beta_benchmark
from core.agents.scene_beta import (
    default_office_scene_beta_benchmark_path,
    load_scene_beta_office_preferences,
    office_beta_observable_signature,
    validate_scene_beta_office_preferences,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class SceneBetaOfficeTests(unittest.TestCase):
    def test_beta_scene_01_office_preferences_contract(self) -> None:
        manifest = json.loads((PROJECT_ROOT / "agents" / "scene_beta_manifest.json").read_text(encoding="utf-8"))
        self.assertIn("office", manifest["active_scenarios"])
        preferences = load_scene_beta_office_preferences(root=PROJECT_ROOT)
        errors = validate_scene_beta_office_preferences(preferences)
        self.assertEqual(errors, [], errors)
        signature = office_beta_observable_signature(preferences)
        self.assertEqual(signature["tier"], "beta")
        self.assertEqual(signature["preferred_circulation_strategy"], "straight_spine")
        self.assertEqual(signature["primary_object_type"], "table")
        self.assertGreaterEqual(signature["object_preference_count"], 6)

    def test_beta_scene_01_office_benchmark_passes(self) -> None:
        output_root = artifact_path("benchmarks", "beta_scene_01")
        result = run_office_scene_beta_benchmark(project_root=PROJECT_ROOT, output_root=output_root)

        self.assertEqual(result.get("preference_validation"), "pass", result)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 9, "passed": 9, "failed": 0})
        self.assertEqual(result.get("expected_evidence_summary_errors", []), [])
        evidence = result["evidence_summary"]
        self.assertEqual(evidence["benchmark_pass_non_cad_count"], 7)
        self.assertEqual(evidence["blocked_expected_non_cad_count"], 2)

        tiers = set()
        suite = json.loads(default_office_scene_beta_benchmark_path(PROJECT_ROOT).read_text(encoding="utf-8"))
        for case in suite["cases"]:
            tiers.add(case["case_tier"])
        self.assertEqual(tiers, {"object", "micro_scene", "blank_shell", "failure"})

        summary_path = output_root / "benchmark_summary.json"
        self.assertTrue(summary_path.is_file())


if __name__ == "__main__":
    unittest.main()
