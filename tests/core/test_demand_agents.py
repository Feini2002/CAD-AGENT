from __future__ import annotations

import json
import unittest

from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path

from core.benchmarks.runner import run_benchmark_suite
from core.demand_agents.loaders import (
    load_demand_agent_registry,
    load_demand_cases,
    summarize_scene_coverage,
)


DEMAND_REGISTRY_PATH = PROJECT_ROOT / "agents" / "demand_side" / "role_agents.json"
DEMAND_BENCHMARK_PATH = PROJECT_ROOT / "examples" / "benchmarks" / "demand_side_agent_benchmark.json"


class DemandAgentTests(unittest.TestCase):
    def test_demand_agent_registry_covers_current_scene_agents(self) -> None:
        registry = load_demand_agent_registry(DEMAND_REGISTRY_PATH)

        self.assertGreaterEqual(len(registry["agents"]), 12)
        coverage = summarize_scene_coverage(registry)
        self.assertEqual(
            set(coverage),
            {"residential", "office", "restaurant", "commercial_fitout", "exhibition", "custom"},
        )
        for scene_id, count in coverage.items():
            with self.subTest(scene_id=scene_id):
                self.assertGreaterEqual(count, 2)

    def test_demand_agent_records_keep_user_voice_and_core_mapping(self) -> None:
        registry = load_demand_agent_registry(DEMAND_REGISTRY_PATH)
        by_id = {agent["agent_id"]: agent for agent in registry["agents"]}

        self.assertIn("residential_beginner_homeowner", by_id)
        beginner = by_id["residential_beginner_homeowner"]
        self.assertEqual(beginner["scene_id"], "residential")
        self.assertIn("你能生成一个比较精细的餐桌吗？", beginner["sample_requests"])
        self.assertIn("composition_engine", beginner["core_capability_targets"])
        self.assertIn("plan_engine", beginner["core_capability_targets"])

    def test_demand_case_records_reference_known_agents_and_target_pipeline(self) -> None:
        registry = load_demand_agent_registry(DEMAND_REGISTRY_PATH)
        cases = load_demand_cases(DEMAND_BENCHMARK_PATH, registry=registry)

        self.assertGreaterEqual(len(cases), 8)
        by_id = {case["case_id"]: case for case in cases}
        self.assertEqual(
            by_id["demand_residential_beginner_dining_table"]["demand_agent_id"],
            "residential_beginner_homeowner",
        )
        self.assertEqual(
            by_id["demand_residential_beginner_dining_table"]["target_pipeline"],
            "object_detail_spec",
        )
        self.assertEqual(
            by_id["demand_office_admin_task_chair"]["target_pipeline"],
            "object_detail_spec",
        )

    def test_demand_agent_benchmark_runs_cross_scene_demands(self) -> None:
        result = run_benchmark_suite(
            DEMAND_BENCHMARK_PATH,
            output_root=artifact_path("benchmarks", "demand_side_agents"),
        )

        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["suite_id"], "demand-side-agent-benchmark")
        self.assertGreaterEqual(result["summary"]["total"], 8)
        self.assertEqual(result["summary"]["failed"], 0)
        scenes = {case["actual"]["scene_id"] for case in result["cases"]}
        self.assertEqual(
            scenes,
            {"residential", "office", "restaurant", "commercial_fitout", "exhibition", "custom"},
        )
        for case in result["cases"]:
            actual = case["actual"]
            self.assertTrue(actual["demand_agent_id"])
            self.assertTrue(actual["request_text"])
            self.assertTrue(actual["core_capability_targets"])
            self.assertIn(
                actual["target_pipeline"],
                {"object_spec", "object_detail_spec", "composition_spec", "blank_shell"},
            )
            self.assertEqual(actual["evidence_state"], "benchmark_pass_non_cad")
            self.assertEqual(actual["geometry_accuracy"], "not_verified_without_cad_readback")

    def test_demand_case_rejects_unknown_agent_reference(self) -> None:
        registry = load_demand_agent_registry(DEMAND_REGISTRY_PATH)
        suite_path = artifact_path("benchmarks", "bad_demand_agent", "suite.json")
        suite_path.write_text(
            json.dumps(
                {
                    "version": "0.1",
                    "suite_id": "bad-demand-agent",
                    "cases": [
                        {
                            "case_id": "bad_agent_ref",
                            "pipeline": "demand_case",
                            "demand_agent_id": "missing_agent",
                            "target_pipeline": "object_spec",
                            "object_type": "desk",
                            "request_text": "生成一个办公桌",
                            "core_capability_targets": ["object_engine"],
                            "expected": {
                                "pipeline_status": "ok",
                                "dry_run_status": "valid",
                                "verification_status": "unverified",
                                "evidence_state": "benchmark_pass_non_cad",
                                "geometry_accuracy": "not_verified_without_cad_readback",
                                "screenshot_role": "visual_aid_only",
                            },
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "unknown demand_agent_id"):
            load_demand_cases(suite_path, registry=registry)


if __name__ == "__main__":
    unittest.main()
