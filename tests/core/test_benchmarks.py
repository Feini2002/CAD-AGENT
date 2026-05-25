from __future__ import annotations

import json
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.benchmarks.runner import run_benchmark_case, run_benchmark_suite
from tests.helpers import artifact_path


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

    def test_blank_shell_core_benchmark_runs_four_cases(self) -> None:
        result = run_benchmark_suite(
            PROJECT_ROOT / "examples/benchmarks/blank_shell_core_benchmark.json",
            output_root=artifact_path("benchmarks", "blank_shell_core"),
        )

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["summary"], {"total": 4, "passed": 4, "failed": 0})
        self.assertEqual(
            {case["case_id"] for case in result["cases"]},
            {"retail_blank_shell", "office_small_suite", "residential_living_room", "restaurant_small_front"},
        )
        for case in result["cases"]:
            self.assertGreaterEqual(case["actual"]["candidate_count"], 2)
            self.assertGreaterEqual(case["actual"]["zone_count"], 2)
            self.assertGreaterEqual(case["actual"]["placement_count"], 5)

    def test_blank_shell_benchmark_cases_use_distinct_workflows(self) -> None:
        suite = json.loads(
            (PROJECT_ROOT / "examples/benchmarks/blank_shell_core_benchmark.json").read_text(encoding="utf-8")
        )

        workflows = [case["workflow"] for case in suite["cases"]]
        self.assertEqual(len(workflows), 4)
        self.assertEqual(len(set(workflows)), 4)

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
        self.assertEqual(result["summary"], {"total": 4, "passed": 4, "failed": 0})
        self.assertEqual(
            {case["case_id"] for case in result["cases"]},
            {
                "office_desk_default_spec",
                "office_chair_default_spec",
                "office_cabinet_default_spec",
                "office_small_suite_alpha",
            },
        )
        for case in result["cases"]:
            self.assertEqual(case["actual"]["evidence_state"], "benchmark_pass_non_cad")
            self.assertEqual(case["actual"]["geometry_accuracy"], "not_verified_without_cad_readback")
            self.assertEqual(case["actual"]["screenshot_role"], "visual_aid_only")
        by_id = {case["case_id"]: case for case in result["cases"]}
        self.assertEqual(by_id["office_desk_default_spec"]["actual"]["width"], 1400)
        self.assertEqual(by_id["office_chair_default_spec"]["actual"]["height"], 850)
        self.assertIn("front_panel", by_id["office_cabinet_default_spec"]["actual"]["component_roles"])
        self.assertTrue(
            {"desk", "chair", "cabinet"}.issubset(
                set(by_id["office_small_suite_alpha"]["actual"]["object_types"])
            )
        )

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

    def test_benchmark_suite_rejects_non_object_cases(self) -> None:
        suite_path = artifact_path("benchmarks", "invalid_suite", "suite.json")
        suite_path.parent.mkdir(parents=True, exist_ok=True)
        suite_path.write_text(
            json.dumps({"version": "0.1", "suite_id": "invalid", "cases": ["not-a-case"]}),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "cases\\[0\\] must be an object"):
            run_benchmark_suite(
                suite_path,
                output_root=artifact_path("benchmarks", "invalid_suite", "out"),
            )

    def test_benchmark_suite_rejects_empty_case_list(self) -> None:
        suite_path = artifact_path("benchmarks", "empty_suite", "suite.json")
        suite_path.parent.mkdir(parents=True, exist_ok=True)
        suite_path.write_text(
            json.dumps({"version": "0.1", "suite_id": "empty", "cases": []}),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "cases must not be empty"):
            run_benchmark_suite(
                suite_path,
                output_root=artifact_path("benchmarks", "empty_suite", "out"),
            )

    def test_benchmark_case_requires_expected_assertions(self) -> None:
        with self.assertRaisesRegex(ValueError, "expected must be a non-empty object"):
            run_benchmark_case(
                {
                    "case_id": "missing-expected",
                    "pipeline": "object_spec",
                    "object_type": "desk",
                },
                root=PROJECT_ROOT,
                output_root=artifact_path("benchmarks", "missing_expected"),
            )


if __name__ == "__main__":
    unittest.main()
