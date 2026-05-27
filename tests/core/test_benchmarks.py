from __future__ import annotations

import json
import shutil
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.benchmarks.runner import run_benchmark_case, run_benchmark_suite, summarize_benchmark_evidence
from tests.helpers import artifact_path

OBJECT_SPEC_EXPECTED_NON_CAD = {
    "pipeline_status": "ok",
    "dry_run_status": "valid",
    "verification_status": "unverified",
    "evidence_state": "benchmark_pass_non_cad",
    "geometry_accuracy": "not_verified_without_cad_readback",
    "screenshot_role": "visual_aid_only",
}


class BenchmarkRunnerTests(unittest.TestCase):
    def test_non_cad_core_benchmark_runs_pipeline_case(self) -> None:
        result = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/non_cad_core_benchmark.json",
            output_root=artifact_path("benchmarks", "non_cad_core"),
        )

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["summary"], {"total": 1, "passed": 1, "failed": 0})
        case = result["cases"][0]
        self.assertEqual(case["case_id"], "minimal-cabinet-non-cad")
        self.assertEqual(case["actual"]["pipeline_status"], "ok")
        self.assertEqual(case["actual"]["dry_run_status"], "valid")
        self.assertEqual(case["actual"]["verification_status"], "unverified")

    def test_blank_shell_core_benchmark_runs_eight_cases(self) -> None:
        result = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/blank_shell_core_benchmark.json",
            output_root=artifact_path("benchmarks", "blank_shell_core"),
        )

        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 8, "passed": 8, "failed": 0})
        self.assertEqual(
            {case["case_id"] for case in result["cases"]},
            {
                "retail_blank_shell",
                "office_small_suite",
                "residential_living_room",
                "restaurant_small_front",
                "long_narrow_office_main_aisle",
                "office_obstacle_avoidance_riser",
                "too_small_room_for_workstation",
                "corridor_riser_blocks_main_path",
            },
        )
        pass_cases = [case for case in result["cases"] if case["actual"]["pipeline_status"] == "ok"]
        for case in pass_cases:
            self.assertGreaterEqual(case["actual"]["candidate_count"], 2)
            self.assertGreaterEqual(case["actual"]["zone_placement_candidate_count"], 2)
            self.assertGreaterEqual(case["actual"]["zone_count"], 1)
            self.assertGreaterEqual(case["actual"]["placement_count"], 4)
            self.assertTrue(case["actual"]["has_comparison_detail"])
            self.assertGreaterEqual(case["actual"]["circulation_branch_count"], 2)
            self.assertGreaterEqual(case["actual"]["object_coverage_rate"], 0.6)
        blocked = [case for case in result["cases"] if case["actual"]["pipeline_status"] == "blocked"]
        self.assertEqual(len(blocked), 2)
        for case in blocked:
            self.assertEqual(case["actual"]["evidence_state"], "blocked_expected_non_cad")
            self.assertEqual(case["actual"]["cad_plan_count"], 0)

    def test_y_mc_04_blank_shell_near_real_and_failure_cases(self) -> None:
        result = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/blank_shell_core_benchmark.json",
            output_root=artifact_path("benchmarks", "y_mc_04"),
        )

        self.assertEqual(result["status"], "pass", result)
        summary = result["evidence_summary"]
        self.assertEqual(summary["case_count"], 8)
        self.assertEqual(summary["benchmark_pass_non_cad_count"], 6)
        self.assertEqual(summary["blocked_expected_non_cad_count"], 2)
        by_id = {case["case_id"]: case for case in result["cases"]}
        self.assertEqual(by_id["long_narrow_office_main_aisle"]["actual"]["shell_id"], "shell-office-long-narrow")
        self.assertGreaterEqual(by_id["office_obstacle_avoidance_riser"]["actual"]["fixed_obstacle_count"], 2)
        self.assertEqual(by_id["too_small_room_for_workstation"]["actual"]["failure_category"], "insufficient_space")
        self.assertEqual(by_id["corridor_riser_blocks_main_path"]["actual"]["shell_id"], "shell-blank-corridor-riser-block")

    def test_x_scene_02_scene_alpha_multi_scene_benchmark(self) -> None:
        result = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/scene_alpha_benchmark.json",
            output_root=artifact_path("benchmarks", "x_scene_02"),
        )

        self.assertEqual(result["status"], "pass", result)
        summary = result["evidence_summary"]
        self.assertEqual(summary["case_count"], 3)
        self.assertEqual(summary["benchmark_pass_non_cad_count"], 3)
        self.assertEqual(summary["readback_geometry_verified_count"], 0)
        by_id = {case["case_id"]: case for case in result["cases"]}
        self.assertEqual(
            by_id["scene_alpha_office_blank_shell"]["actual"]["selected_circulation_strategy"],
            "straight_spine",
        )
        self.assertEqual(
            by_id["scene_alpha_residential_blank_shell"]["actual"]["selected_circulation_strategy"],
            "along_wall",
        )
        self.assertEqual(
            by_id["scene_alpha_restaurant_blank_shell"]["actual"]["selected_circulation_strategy"],
            "l_spine",
        )
        for case_id, scenario in (
            ("scene_alpha_office_blank_shell", "office"),
            ("scene_alpha_residential_blank_shell", "residential"),
            ("scene_alpha_restaurant_blank_shell", "restaurant"),
        ):
            actual = by_id[case_id]["actual"]
            self.assertEqual(actual["preferences_scenario"], scenario)
            self.assertTrue(actual["has_comparison_detail"])

    def test_y_mc_03_blank_shell_benchmark_multi_candidate_assertions(self) -> None:
        result = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/blank_shell_core_benchmark.json",
            output_root=artifact_path("benchmarks", "y_mc_03"),
        )

        self.assertEqual(result["status"], "pass", result)
        residential = next(
            case for case in result["cases"] if case["case_id"] == "residential_living_room"
        )
        self.assertEqual(residential["actual"]["object_coverage_rate"], 1.0)
        self.assertEqual(residential["actual"]["selected_failed_reason_distribution"], {})
        office = next(case for case in result["cases"] if case["case_id"] == "office_small_suite")
        self.assertTrue({"desk", "chair", "cabinet"}.issubset(set(office["actual"]["object_types"])))

    def test_blank_shell_benchmark_cases_use_distinct_workflows(self) -> None:
        suite = json.loads(
            (PROJECT_ROOT / "examples/benchmarks/blank_shell_core_benchmark.json").read_text(encoding="utf-8")
        )

        workflows = [case["workflow"] for case in suite["cases"]]
        self.assertEqual(len(workflows), 8)
        self.assertEqual(len(set(workflows)), 8)

    def test_blank_shell_case_supports_phase_r_evidence_and_assertions(self) -> None:
        result = run_benchmark_case(
            {
                "case_id": "office-alpha-contract",
                "pipeline": "blank_shell",
                "workflow": "examples/workflows/blank_shell_office_layout_loop.json",
                "expected": {
                    "pipeline_status": "ok",
                    "dry_run_status": "valid",
                    "verification_status": "unverified",
                    "evidence_state": "benchmark_pass_non_cad",
                    "geometry_accuracy": "not_verified_without_cad_readback",
                    "screenshot_role": "visual_aid_only",
                    "minimums": {
                        "candidate_count": 2,
                        "zone_count": 2,
                        "placement_count": 5,
                        "cad_plan_count": 1,
                    },
                    "contains_object_types": ["desk", "chair", "cabinet"],
                },
            },
            root=PROJECT_ROOT,
            output_root=artifact_path("benchmarks", "phase_r_assertions"),
        )

        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertEqual(result["actual"]["evidence_state"], "benchmark_pass_non_cad")
        self.assertEqual(result["actual"]["geometry_accuracy"], "not_verified_without_cad_readback")
        self.assertEqual(result["actual"]["screenshot_role"], "visual_aid_only")
        self.assertTrue({"desk", "chair", "cabinet"}.issubset(set(result["actual"]["object_types"])))

    def test_office_alpha_benchmark_runs_phase_r_contract(self) -> None:
        result = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/office_alpha_benchmark.json",
            output_root=artifact_path("benchmarks", "office_alpha"),
        )

        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["suite_id"], "office-alpha-benchmark")
        self.assertEqual(result["summary"], {"total": 18, "passed": 18, "failed": 0})
        self.assertEqual(
            {case["case_id"] for case in result["cases"]},
            {
                "office_desk_default_spec",
                "office_chair_default_spec",
                "office_cabinet_default_spec",
                "computer_desk_default_spec",
                "storage_cabinet_front_clearance",
                "file_cabinet_default_spec",
                "single_desk_chair_pair",
                "desk_with_back_cabinet",
                "two_workstations_shared_aisle",
                "entry_reception_clearance",
                "long_narrow_office_main_aisle",
                "office_obstacle_avoidance_riser",
                "meeting_computer_mixed_zone",
                "office_small_suite_alpha",
                "too_small_room_for_workstation",
                "office_invalid_workflow_input",
                "door_clearance_conflict",
                "cabinet_pullback_conflict",
            },
        )
        for case in result["cases"]:
            if case["case_id"] == "office_invalid_workflow_input":
                self.assertEqual(case["actual"]["pipeline_status"], "invalid", case)
                self.assertEqual(case["actual"]["evidence_state"], "invalid_configuration")
                self.assertEqual(case["actual"]["geometry_accuracy"], "not_verified_without_cad_readback")
                continue
            if case["case_id"] in {
                "too_small_room_for_workstation",
                "door_clearance_conflict",
                "cabinet_pullback_conflict",
            }:
                self.assertEqual(case["actual"]["pipeline_status"], "blocked", case)
                self.assertEqual(case["actual"]["evidence_state"], "blocked_expected_non_cad")
                self.assertEqual(case["actual"]["geometry_accuracy"], "not_verified_without_cad_readback")
                continue
            self.assertEqual(case["actual"]["evidence_state"], "benchmark_pass_non_cad")
            self.assertEqual(case["actual"]["geometry_accuracy"], "not_verified_without_cad_readback")
            self.assertEqual(case["actual"]["screenshot_role"], "visual_aid_only")
        by_id = {case["case_id"]: case for case in result["cases"]}
        self.assertEqual(by_id["office_desk_default_spec"]["actual"]["width"], 1400)
        self.assertEqual(by_id["office_chair_default_spec"]["actual"]["height"], 850)
        self.assertIn("front_panel", by_id["office_cabinet_default_spec"]["actual"]["component_roles"])
        self.assertEqual(by_id["computer_desk_default_spec"]["actual"]["placement_role"], "screen_workstation")
        self.assertIn("monitor_zone", by_id["computer_desk_default_spec"]["actual"]["component_roles"])
        self.assertIn(
            "cabinet_front_clearance",
            by_id["storage_cabinet_front_clearance"]["actual"]["clearance_ref_roles"],
        )
        self.assertIn(
            "cabinet_front_clearance",
            by_id["file_cabinet_default_spec"]["actual"]["clearance_ref_roles"],
        )
        self.assertIn(
            "chair_pullback_clearance",
            by_id["single_desk_chair_pair"]["actual"]["clearance_ref_roles"],
        )
        self.assertIn("seating_for_desk", by_id["single_desk_chair_pair"]["actual"]["binding_relations"])
        self.assertIn("main_aisle", by_id["two_workstations_shared_aisle"]["actual"]["circulation_roles"])
        self.assertIn("entry_clearance", by_id["entry_reception_clearance"]["actual"]["clearance_ref_roles"])
        self.assertEqual(
            by_id["long_narrow_office_main_aisle"]["actual"]["shell_id"],
            "shell-office-long-narrow",
        )
        self.assertGreaterEqual(by_id["office_obstacle_avoidance_riser"]["actual"]["no_place_zone_count"], 2)
        self.assertGreaterEqual(by_id["office_obstacle_avoidance_riser"]["actual"]["fixed_obstacle_count"], 2)
        self.assertIn(
            "computer_desk",
            by_id["meeting_computer_mixed_zone"]["actual"]["object_types"],
        )
        self.assertTrue(
            {"desk", "chair", "cabinet"}.issubset(
                set(by_id["office_small_suite_alpha"]["actual"]["object_types"])
            )
        )
        self.assertEqual(
            by_id["too_small_room_for_workstation"]["actual"]["failure_category"],
            "insufficient_space",
        )
        self.assertEqual(by_id["too_small_room_for_workstation"]["actual"]["cad_plan_count"], 0)
        self.assertEqual(by_id["office_invalid_workflow_input"]["actual"]["pipeline_status"], "invalid")
        self.assertEqual(
            by_id["office_invalid_workflow_input"]["actual"]["evidence_state"],
            "invalid_configuration",
        )
        self.assertEqual(
            by_id["door_clearance_conflict"]["actual"]["failure_category"],
            "entry_clearance_conflict",
        )
        self.assertEqual(
            by_id["cabinet_pullback_conflict"]["actual"]["failure_category"],
            "clearance_conflict",
        )
        summary = result["evidence_summary"]
        self.assertTrue(summary["non_cad_only"])
        self.assertEqual(summary["geometry_verified_case_count"], 0)
        self.assertEqual(summary["evidence_state_counts"]["benchmark_pass_non_cad"], 14)
        self.assertEqual(summary["evidence_state_counts"]["blocked_expected_non_cad"], 3)
        self.assertEqual(summary["evidence_state_counts"]["invalid_configuration"], 1)
        self.assertEqual(
            summary["failure_category_counts"],
            {
                "insufficient_space": 1,
                "entry_clearance_conflict": 1,
                "clearance_conflict": 1,
            },
        )
        summary_path = artifact_path("benchmarks", "office_alpha") / "benchmark_summary.json"
        self.assertTrue(summary_path.is_file())

    def test_summarize_benchmark_evidence_counts_states(self) -> None:
        summary = summarize_benchmark_evidence(
            [
                {
                    "actual": {
                        "evidence_state": "benchmark_pass_non_cad",
                        "geometry_accuracy": "not_verified_without_cad_readback",
                        "screenshot_role": "visual_aid_only",
                        "pipeline_status": "ok",
                    }
                },
                {
                    "actual": {
                        "evidence_state": "blocked_expected_non_cad",
                        "geometry_accuracy": "not_verified_without_cad_readback",
                        "screenshot_role": "visual_aid_only",
                        "pipeline_status": "blocked",
                        "failure_category": "insufficient_space",
                    }
                },
            ]
        )
        self.assertEqual(summary["case_count"], 2)
        self.assertEqual(summary["benchmark_pass_non_cad_count"], 1)
        self.assertEqual(summary["blocked_expected_non_cad_count"], 1)
        self.assertEqual(summary["failure_category_counts"]["insufficient_space"], 1)
        self.assertTrue(summary["non_cad_only"])

    def test_r4_three_benchmark_suites_match_expected_evidence_summary(self) -> None:
        suites = [
            (
                PROJECT_ROOT / "examples/benchmarks/blank_shell_core_benchmark.json",
                artifact_path("benchmarks", "r4_blank_shell"),
                {"benchmark_pass_non_cad_count": 6, "blocked_expected_non_cad_count": 2, "case_count": 8},
            ),
            (
                PROJECT_ROOT / "examples/benchmarks/interior_delivery_benchmark.json",
                artifact_path("benchmarks", "r4_interior"),
                {"benchmark_pass_non_cad_count": 3, "case_count": 3},
            ),
            (
                PROJECT_ROOT / "examples/benchmarks/office_alpha_benchmark.json",
                artifact_path("benchmarks", "r4_office"),
                {
                    "benchmark_pass_non_cad_count": 14,
                    "blocked_expected_non_cad_count": 3,
                    "invalid_configuration_count": 1,
                    "case_count": 18,
                },
            ),
        ]
        for suite_path, output_root, expected_rollup in suites:
            result = run_benchmark_suite(suite_path, output_root=output_root)
            self.assertEqual(result["status"], "pass", result.get("evidence_summary_errors", result))
            summary = result["evidence_summary"]
            self.assertTrue(summary["non_cad_only"], suite_path.name)
            self.assertEqual(summary["readback_geometry_verified_count"], 0)
            for key, value in expected_rollup.items():
                self.assertEqual(summary[key], value, f"{suite_path.name}:{key}")
            summary_path = output_root / "benchmark_summary.json"
            self.assertTrue(summary_path.is_file())

    def test_object_spec_benchmark_case_runs_plan_dry_run_contract(self) -> None:
        result = run_benchmark_case(
            {
                "case_id": "office-desk-object-spec",
                "pipeline": "object_spec",
                "object_type": "desk",
                "expected": {
                    "pipeline_status": "ok",
                    "dry_run_status": "valid",
                    "verification_status": "unverified",
                    "evidence_state": "benchmark_pass_non_cad",
                    "geometry_accuracy": "not_verified_without_cad_readback",
                    "screenshot_role": "visual_aid_only",
                    "object_type": "desk",
                    "width": 1400,
                    "depth": 700,
                    "height": 750,
                    "contains_component_roles": ["worktop", "clearance_zone"],
                },
            },
            root=PROJECT_ROOT,
            output_root=artifact_path("benchmarks", "object_spec_contract"),
        )

        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertIn("object_spec", result["artifacts"])
        self.assertIn("cad_plan", result["artifacts"])

    def test_benchmark_case_id_must_be_safe_path_segment(self) -> None:
        with self.assertRaisesRegex(ValueError, "case_id"):
            run_benchmark_case(
                {
                    "case_id": "../escape",
                    "pipeline": "object_spec",
                    "object_type": "desk",
                    "expected": OBJECT_SPEC_EXPECTED_NON_CAD,
                },
                root=PROJECT_ROOT,
                output_root=artifact_path("benchmarks", "unsafe_case_id"),
            )

    def test_benchmark_output_root_must_stay_under_project_output(self) -> None:
        output_root = PROJECT_ROOT / "tests" / "outside_benchmark_output"
        try:
            with self.assertRaisesRegex(ValueError, "output_root"):
                run_benchmark_case(
                    {
                        "case_id": "safe-case",
                        "pipeline": "object_spec",
                        "object_type": "desk",
                        "expected": OBJECT_SPEC_EXPECTED_NON_CAD,
                    },
                    root=PROJECT_ROOT,
                    output_root=output_root,
                )
        finally:
            if output_root.exists():
                shutil.rmtree(output_root, ignore_errors=True)

    def test_composition_spec_benchmark_case_runs_persona_delivery_contract(self) -> None:
        result = run_benchmark_case(
            {
                "case_id": "interior-designer-bedroom-combo",
                "pipeline": "composition_spec",
                "composition_id": "bedroom_bed_rug",
                "persona_role": "interior_designer",
                "request_text": "生成一个床铺加地毯的卧室组合",
                "expected": {
                    "pipeline_status": "ok",
                    "dry_run_status": "valid",
                    "verification_status": "unverified",
                    "evidence_state": "benchmark_pass_non_cad",
                    "geometry_accuracy": "not_verified_without_cad_readback",
                    "screenshot_role": "visual_aid_only",
                    "persona_role": "interior_designer",
                    "composition_id": "bedroom_bed_rug",
                    "object_count": 2,
                    "cad_plan_count": 2,
                    "visual_preview_status": "written",
                    "contains_object_types": ["bed", "rug"],
                    "contains_object_roles": ["primary_bed", "soft_zone"],
                },
            },
            root=PROJECT_ROOT,
            output_root=artifact_path("benchmarks", "composition_contract"),
        )

        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertIn("composition_spec", result["artifacts"])
        self.assertIn("preview_svg", result["artifacts"])

    def test_interior_delivery_benchmark_runs_three_persona_compositions(self) -> None:
        result = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/interior_delivery_benchmark.json",
            output_root=artifact_path("benchmarks", "interior_delivery"),
        )

        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 3, "passed": 3, "failed": 0})
        self.assertEqual(
            {case["actual"]["composition_id"] for case in result["cases"]},
            {"bedroom_bed_rug", "dining_table_set", "office_desk_combo"},
        )
        for case in result["cases"]:
            self.assertEqual(case["actual"]["evidence_state"], "benchmark_pass_non_cad")
            self.assertEqual(case["actual"]["visual_preview_status"], "written")

if __name__ == "__main__":
    unittest.main()
