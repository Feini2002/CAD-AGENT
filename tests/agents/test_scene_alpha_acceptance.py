from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.agents.scene_alpha import SCENE_ALPHA_SCENARIOS
from core.agents.scene_boundary_scan import scan_agent_tree
from core.benchmarks.runner import run_benchmark_suite
from core.maintenance.repo_audit import run_repo_audit
from tests.helpers import PROJECT_ROOT, artifact_path


AGENTS_ROOT = PROJECT_ROOT / "agents"
VERIFICATION_DOCS = (
    "scene_alpha_preferences_contract.md",
    "scene_alpha_agent_boundaries.md",
    "scene_alpha_explanation_template.md",
    "scene_alpha_acceptance.md",
)


class SceneAlphaAcceptanceTests(unittest.TestCase):
    def test_x_scene_05_verification_doc_bundle_exists(self) -> None:
        verification_root = PROJECT_ROOT / "docs" / "verification"
        for name in VERIFICATION_DOCS:
            with self.subTest(doc=name):
                self.assertTrue((verification_root / name).is_file(), name)

    def test_x_scene_05_acceptance_doc_states_claims_and_limits(self) -> None:
        text = (PROJECT_ROOT / "docs" / "verification" / "scene_alpha_acceptance.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("现在可以声称什么", text)
        self.assertIn("不能声称什么", text)
        self.assertIn("geometry_verified", text)
        self.assertIn("benchmark_pass_non_cad", text)

    def test_x_scene_05_scene_alpha_benchmark_three_scenes_non_cad_only(self) -> None:
        result = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/scene_alpha_benchmark.json",
            output_root=artifact_path("benchmarks", "x_scene_05"),
        )

        self.assertEqual(result["status"], "pass", result)
        summary = result["evidence_summary"]
        self.assertEqual(summary["case_count"], 3)
        self.assertEqual(summary["benchmark_pass_non_cad_count"], 3)
        self.assertEqual(summary.get("readback_geometry_verified_count", 0), 0)
        self.assertTrue(summary.get("non_cad_only", True))

        by_id = {case["case_id"]: case for case in result["cases"]}
        self.assertEqual(len(by_id), 3)
        for scenario, strategy in (
            ("office", "straight_spine"),
            ("residential", "along_wall"),
            ("restaurant", "l_spine"),
        ):
            case_id = f"scene_alpha_{scenario}_blank_shell"
            actual = by_id[case_id]["actual"]
            self.assertEqual(actual["preferences_scenario"], scenario)
            self.assertEqual(actual["selected_circulation_strategy"], strategy)
            self.assertEqual(actual["evidence_state"], "benchmark_pass_non_cad")

    def test_x_scene_05_manifest_links_benchmark_and_docs(self) -> None:
        manifest = json.loads((AGENTS_ROOT / "scene_alpha_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual({item["scenario"] for item in manifest["scenarios"]}, set(SCENE_ALPHA_SCENARIOS))
        self.assertIn("benchmark_suite", manifest)
        self.assertIn("explanation_template", manifest)
        self.assertIn("acceptance_doc", manifest)

    def test_x_scene_05_agents_tree_boundary_scan_clean(self) -> None:
        violations = scan_agent_tree(AGENTS_ROOT)
        self.assertEqual(violations, [], violations)

    def test_x_scene_05_agent_tests_directory_no_sys_path_pollution(self) -> None:
        report = run_repo_audit(PROJECT_ROOT / "tests" / "agents")
        path_insert_findings = [
            finding for finding in report["findings"] if finding["code"] == "raw_sys_path_insert"
        ]
        self.assertEqual(path_insert_findings, [], path_insert_findings)


if __name__ == "__main__":
    unittest.main()
