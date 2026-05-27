from __future__ import annotations

import unittest

from core.agents.office_alpha_boundary import (
    EXPECTED_OFFICE_ALPHA_CASE_COUNT,
    OFFICE_PROD_01_BOUNDARY_DOC,
    OFFICE_PROD_01_PACKAGE_ID,
    assert_office_alpha_boundary_contract,
    default_manifest_path,
    load_office_prod_alpha_manifest,
    office_alpha_boundary_status_summary,
)
from core.agents.scene_alpha import load_scene_preferences, validate_scene_alpha_preferences
from core.benchmarks.runner import run_benchmark_suite
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class OfficeProd01OfficeAlphaBoundaryTests(unittest.TestCase):
    def test_office_prod_01_contract(self) -> None:
        assert_office_alpha_boundary_contract(project_root=PROJECT_ROOT)

    def test_manifest_ids(self) -> None:
        manifest = load_office_prod_alpha_manifest(default_manifest_path(PROJECT_ROOT))
        self.assertEqual(manifest["manifest_id"], "office-prod-alpha-01")
        self.assertEqual(manifest["package_id"], OFFICE_PROD_01_PACKAGE_ID)
        self.assertEqual(manifest["scenario"], "office")

    def test_office_preferences_validate(self) -> None:
        preferences = load_scene_preferences("office", root=PROJECT_ROOT)
        self.assertEqual(preferences["scenario"], "office")
        self.assertEqual(validate_scene_alpha_preferences(preferences, scenario="office"), [])

    def test_office_alpha_benchmark_eighteen_pass(self) -> None:
        result = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/office_alpha_benchmark.json",
            output_root=artifact_path("office_prod_01", "benchmark_no_cad"),
        )
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"]["passed"], EXPECTED_OFFICE_ALPHA_CASE_COUNT)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / OFFICE_PROD_01_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "OFFICE-PROD-01",
            "office-prod-alpha-01",
            "office-alpha-benchmark",
            "assert_office_alpha_boundary_contract",
            "benchmark_pass_non_cad",
            "V-PROOF-24",
            "geometry_verified",
            "不得声称",
            "REST-PROD",
            "dry_run_valid_plan_only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_status_summary(self) -> None:
        summary = office_alpha_boundary_status_summary(project_root=PROJECT_ROOT)
        self.assertEqual(summary["package_id"], OFFICE_PROD_01_PACKAGE_ID)
        self.assertEqual(summary["expected_case_count"], 18)

    def test_handoff_indexes_office_prod_01(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("OFFICE-PROD-01", handoff)
        self.assertIn("office_prod_01_office_alpha_boundary.md", handoff)


if __name__ == "__main__":
    unittest.main()
