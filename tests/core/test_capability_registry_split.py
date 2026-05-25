from __future__ import annotations

import unittest

from tests.bootstrap import PROJECT_ROOT

from core.capabilities import specs
from core.capabilities.registry import get_capability, list_capabilities, run_capability, validate_capability_registry


EXPECTED_CAPABILITY_IDS = [
    "benchmark.non_cad_suite",
    "drawing_analysis.load_shell_model",
    "layout.create_candidates",
    "layout.create_zone_placements",
    "layout.generate_circulation_candidates",
    "layout.split_function_zones",
    "object.explain",
    "plan.model_to_plans",
    "project_model.build",
    "proposal.compare_layout_candidates",
    "verification.no_cad_report",
    "workflow.artifact_graph",
    "workflow.blank_shell_pipeline",
]


class CapabilityRegistrySplitTests(unittest.TestCase):
    def test_public_catalog_ids_are_stable(self) -> None:
        self.assertEqual([item["capability_id"] for item in list_capabilities()], EXPECTED_CAPABILITY_IDS)

    def test_registry_facade_still_validates_metadata(self) -> None:
        self.assertEqual(validate_capability_registry(), [])

    def test_unknown_capability_still_returns_structured_error(self) -> None:
        result = run_capability("missing.capability", {})
        self.assertEqual(result["status"], "unknown_capability")
        self.assertEqual(result["capability_id"], "missing.capability")

    def test_get_capability_hides_runner(self) -> None:
        spec = get_capability("workflow.blank_shell_pipeline")
        self.assertNotIn("runner", spec)
        self.assertEqual(spec["capability_id"], "workflow.blank_shell_pipeline")

    def test_registry_validation_requires_callable_runner(self) -> None:
        original = specs.CAPABILITIES["workflow.blank_shell_pipeline"]["runner"]
        specs.CAPABILITIES["workflow.blank_shell_pipeline"]["runner"] = "not-callable"
        try:
            errors = validate_capability_registry()
        finally:
            specs.CAPABILITIES["workflow.blank_shell_pipeline"]["runner"] = original

        self.assertIn("workflow.blank_shell_pipeline: runner must be callable.", errors)

    def test_path_based_capabilities_reject_paths_outside_project(self) -> None:
        result = run_capability(
            "workflow.blank_shell_pipeline",
            {"workflow_path": "../outside.json", "output_dir": "output/test_artifacts/capabilities/outside_path"},
        )

        self.assertEqual(result["status"], "failed")
        self.assertTrue(any("must stay under project root" in error for error in result["errors"]))

    def test_capability_output_paths_must_stay_under_output_directory(self) -> None:
        result = run_capability(
            "benchmark.non_cad_suite",
            {
                "suite_path": "examples/benchmarks/non_cad_core_benchmark.json",
                "output_root": str(PROJECT_ROOT.parent / "outside-benchmark-output"),
            },
        )

        self.assertEqual(result["status"], "failed")
        self.assertTrue(any("must stay under project output directory" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
