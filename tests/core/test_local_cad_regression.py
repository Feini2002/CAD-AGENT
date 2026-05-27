from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.verification.cad_validation_types import CommandResult
from core.schemas.validator import validate_json
from core.verification.local_cad_regression import (
    DEFAULT_MANIFEST_RELATIVE_PATH,
    load_regression_manifest,
    run_local_cad_regression,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class LocalCadRegressionTests(unittest.TestCase):
    def test_lcad_01_default_manifest_declares_cases_and_safety_boundaries(self) -> None:
        manifest_path = PROJECT_ROOT / DEFAULT_MANIFEST_RELATIVE_PATH
        manifest = load_regression_manifest(manifest_path)

        schema_errors = validate_json(
            PROJECT_ROOT / "core" / "schemas" / "cad_regression_manifest.schema.json",
            manifest_path,
        )
        self.assertEqual(schema_errors, [])

        cases = {case["id"]: case for case in manifest["cases"]}
        self.assertEqual(
            set(cases),
            {
                "baseline_cad_validation",
                "project_sample_cad_check",
                "composition_cad_check",
                "primitive_matrix_cad",
                "primitive_matrix_no_cad",
                "cad_plan_fixture_suite_no_cad",
                "cad_plan_fixture_suite_cad",
                "complex_cad_smoke",
            },
        )
        for case in cases.values():
            with self.subTest(case=case["id"]):
                self.assertIsInstance(case["requires_real_cad"], bool)
                self.assertTrue(case["expected_evidence_state"])
                self.assertTrue(case["output_path"])
                self.assertIsInstance(case["command"], list)
                self.assertGreaterEqual(len(case["command"]), 1)
                self.assertEqual(case["safety"]["layer"], "CODEX_PREVIEW")
                self.assertFalse(case["safety"]["saved_dwg"])
                self.assertFalse(case["safety"]["deleted_entities"])
                self.assertFalse(case["safety"]["modified_formal_layers"])

    def test_lcad_01_manifest_rejects_missing_required_fields(self) -> None:
        invalid_manifest = artifact_path("local_cad_regression", "invalid_manifest.json")
        invalid_manifest.write_text(
            json.dumps(
                {
                    "version": "0.1",
                    "suite_id": "invalid_local_cad_regression",
                    "safety": {
                        "layer": "CODEX_PREVIEW",
                        "saved_dwg": False,
                        "deleted_entities": False,
                        "modified_formal_layers": False,
                    },
                    "cases": [
                        {
                            "id": "missing_requires_real_cad",
                            "title": "Broken manifest case",
                            "entrypoint": "scripts/run_cad_validation.py",
                            "expected_evidence_state": "readback_geometry_verified",
                            "output_path": "broken/report.json",
                            "command": ["scripts/run_cad_validation.py"],
                            "safety": {
                                "layer": "CODEX_PREVIEW",
                                "saved_dwg": False,
                                "deleted_entities": False,
                                "modified_formal_layers": False,
                            },
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, r"cases\[0\]\.requires_real_cad"):
            load_regression_manifest(invalid_manifest)

    def test_lcad_01_no_cad_report_includes_manifest_metadata(self) -> None:
        output_dir = artifact_path("local_cad_regression", "manifest_metadata")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "run_cad_validation.py" in command_text:
                return CommandResult(returncode=0, stdout=json.dumps({"status": "pass"}), stderr="")
            if "run_project_sample_cad_check.py" in command_text:
                return CommandResult(returncode=0, stdout=json.dumps({"status": "deferred"}), stderr="")
            if "run_complex_cad_smoke.py" in command_text:
                return CommandResult(returncode=0, stdout=json.dumps({"status": "deferred"}), stderr="")
            if "run_primitive_matrix.py" in command_text:
                self.assertIn("--no-cad", command)
                return CommandResult(returncode=0, stdout=json.dumps({"status": "pass"}), stderr="")
            if "run_cad_plan_fixture_suite.py" in command_text:
                self.assertIn("--no-cad", command)
                return CommandResult(returncode=0, stdout=json.dumps({"status": "pass"}), stderr="")
            raise AssertionError(f"unexpected command: {command}")

        report = run_local_cad_regression(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            include_cad=False,
            command_runner=fake_runner,
        )

        self.assertEqual(report["manifest"]["suite_id"], "local_cad_regression")
        self.assertEqual(report["manifest"]["case_count"], 8)
        self.assertEqual(
            [case["id"] for case in report["manifest"]["cases"]],
            [
                "baseline_cad_validation",
                "project_sample_cad_check",
                "composition_cad_check",
                "primitive_matrix_cad",
                "primitive_matrix_no_cad",
                "cad_plan_fixture_suite_no_cad",
                "cad_plan_fixture_suite_cad",
                "complex_cad_smoke",
            ],
        )

    def test_lcad_02_selected_case_runs_only_project_sample_from_manifest(self) -> None:
        output_dir = artifact_path("local_cad_regression", "selected_project_sample")
        commands: list[list[str]] = []

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            commands.append(command)
            command_text = " ".join(command)
            if "run_project_sample_cad_check.py" in command_text:
                self.assertIn("--no-cad", command)
                return CommandResult(returncode=0, stdout=json.dumps({"status": "deferred"}), stderr="")
            raise AssertionError(f"unexpected command: {command}")

        report = run_local_cad_regression(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            include_cad=False,
            selected_case_ids=["project_sample_cad_check"],
            command_runner=fake_runner,
        )

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["selected_case_ids"], ["project_sample_cad_check"])
        self.assertEqual(report["summary"]["selected_case_count"], 1)
        self.assertEqual([step["id"] for step in report["steps"]], ["project_sample_cad_check"])
        self.assertFalse(any("run_cad_validation.py" in " ".join(command) for command in commands))
        self.assertFalse(any("run_composition_cad_check.py" in " ".join(command) for command in commands))
        self.assertFalse(any("run_complex_cad_smoke.py" in " ".join(command) for command in commands))

    def test_complex_cad_smoke_can_be_selected_from_manifest(self) -> None:
        output_dir = artifact_path("local_cad_regression", "selected_complex_cad_smoke")
        commands: list[list[str]] = []

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            commands.append(command)
            command_text = " ".join(command)
            if "run_complex_cad_smoke.py" in command_text:
                self.assertIn("--no-cad", command)
                return CommandResult(returncode=0, stdout=json.dumps({"status": "deferred"}), stderr="")
            raise AssertionError(f"unexpected command: {command}")

        report = run_local_cad_regression(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            include_cad=False,
            selected_case_ids=["complex_cad_smoke"],
            command_runner=fake_runner,
        )

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["summary"]["selected_case_count"], 1)
        self.assertEqual([step["id"] for step in report["steps"]], ["complex_cad_smoke"])
        self.assertTrue(any("run_complex_cad_smoke.py" in " ".join(command) for command in commands))

    def test_lcad_02_unknown_selected_case_is_rejected_before_running_commands(self) -> None:
        output_dir = artifact_path("local_cad_regression", "unknown_selected_case")
        commands: list[list[str]] = []

        with self.assertRaisesRegex(ValueError, "unknown selected manifest case"):
            run_local_cad_regression(
                root=PROJECT_ROOT,
                output_dir=output_dir,
                include_cad=False,
                selected_case_ids=["missing_case"],
                command_runner=lambda command, cwd, timeout_seconds: commands.append(command) or CommandResult(0, "{}", ""),
            )

        self.assertEqual(commands, [])

    def test_no_cad_mode_builds_deferred_matrix_without_running_cad_only_checks(self) -> None:
        output_dir = artifact_path("local_cad_regression", "no_cad_matrix")
        commands: list[list[str]] = []

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            commands.append(command)
            command_text = " ".join(command)
            if "run_cad_validation.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "pass",
                            "include_cad": False,
                            "block_alpha": {"geometry_verified": False},
                            "evidence_summary": {
                                "non_cad_only": True,
                                "readback_geometry_verified_count": 0,
                                "cad_capability_verified_count": 0,
                            },
                        }
                    ),
                    stderr="",
                )
            if "run_project_sample_cad_check.py" in command_text:
                self.assertIn("--no-cad", command)
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "deferred",
                            "geometry_verified": False,
                            "created_handle_count": 0,
                            "evidence_state": "deferred_cad_readback_required",
                        }
                    ),
                    stderr="",
                )
            if "run_complex_cad_smoke.py" in command_text:
                self.assertIn("--no-cad", command)
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "deferred",
                            "geometry_verified": False,
                            "created_handle_count": 0,
                            "evidence_state": "deferred_cad_readback_required",
                        }
                    ),
                    stderr="",
                )
            if "run_primitive_matrix.py" in command_text:
                self.assertIn("--no-cad", command)
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps({"status": "pass", "geometry_verified": False}),
                    stderr="",
                )
            if "run_cad_plan_fixture_suite.py" in command_text:
                self.assertIn("--no-cad", command)
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps({"status": "pass", "geometry_verified": False}),
                    stderr="",
                )
            raise AssertionError(f"unexpected command: {command}")

        report = run_local_cad_regression(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            include_cad=False,
            command_runner=fake_runner,
        )

        self.assertEqual(report["status"], "pass")
        self.assertTrue(report["summary"]["non_cad_only"])
        self.assertEqual(report["summary"]["geometry_verified_case_count"], 0)
        self.assertEqual(report["summary"]["deferred_case_count"], 5)
        steps = {step["id"]: step for step in report["steps"]}
        self.assertEqual(steps["baseline_cad_validation"]["status"], "pass")
        self.assertEqual(steps["project_sample_cad_check"]["status"], "deferred")
        self.assertEqual(steps["composition_cad_check"]["status"], "deferred")
        self.assertEqual(steps["primitive_matrix_cad"]["status"], "deferred")
        self.assertEqual(steps["primitive_matrix_no_cad"]["status"], "pass")
        self.assertEqual(steps["cad_plan_fixture_suite_no_cad"]["status"], "pass")
        self.assertEqual(steps["cad_plan_fixture_suite_cad"]["status"], "deferred")
        self.assertEqual(steps["complex_cad_smoke"]["status"], "deferred")
        self.assertEqual(steps["composition_cad_check"]["returncode"], None)
        self.assertFalse(any("run_composition_cad_check.py" in " ".join(command) for command in commands))
        self.assertTrue((output_dir / "local_cad_regression_report.json").is_file())

    def test_real_cad_strict_mode_fails_when_project_sample_is_not_geometry_verified(self) -> None:
        output_dir = artifact_path("local_cad_regression", "strict_project_sample_deferred")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "run_cad_validation.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "pass",
                            "include_cad": True,
                            "block_alpha": {"geometry_verified": True},
                            "evidence_summary": {
                                "non_cad_only": False,
                                "readback_geometry_verified_count": 2,
                                "cad_capability_verified_count": 1,
                            },
                        }
                    ),
                    stderr="",
                )
            if "run_project_sample_cad_check.py" in command_text:
                self.assertIn("--require-cad-verified", command)
                return CommandResult(
                    returncode=1,
                    stdout=json.dumps({"status": "deferred", "geometry_verified": False}),
                    stderr="CAD geometry verification required but report is not geometry_verified.",
                )
            if "run_benchmark_suite.py" in command_text:
                return CommandResult(returncode=0, stdout=json.dumps({"status": "pass"}), stderr="")
            if "run_composition_cad_check.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "geometry_verified",
                            "verified_case_count": 3,
                            "created_handle_count": 55,
                        }
                    ),
                    stderr="",
                )
            if "run_complex_cad_smoke.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "geometry_verified",
                            "geometry_verified": True,
                            "created_handle_count": 23,
                        }
                    ),
                    stderr="",
                )
            if "run_primitive_matrix.py" in command_text:
                if "--no-cad" in command:
                    return CommandResult(
                        returncode=0,
                        stdout=json.dumps({"status": "pass", "geometry_verified": False}),
                        stderr="",
                    )
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "pass",
                            "geometry_verified": True,
                            "probe_status": "cad_capability_verified",
                        }
                    ),
                    stderr="",
                )
            if "run_cad_plan_fixture_suite.py" in command_text:
                if "--no-cad" in command:
                    return CommandResult(returncode=0, stdout=json.dumps({"status": "pass"}), stderr="")
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "pass",
                            "geometry_verified": True,
                            "passed_fixture_count": 3,
                        }
                    ),
                    stderr="",
                )
            raise AssertionError(f"unexpected command: {command}")

        report = run_local_cad_regression(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            include_cad=True,
            require_cad_verified=True,
            command_runner=fake_runner,
        )

        self.assertEqual(report["status"], "fail")
        steps = {step["id"]: step for step in report["steps"]}
        self.assertEqual(steps["project_sample_cad_check"]["status"], "fail")
        self.assertEqual(steps["project_sample_cad_check"]["failure_category"], "cad_geometry_not_verified")
        self.assertEqual(report["summary"]["failed_case_count"], 1)
        self.assertTrue(report["summary"]["strict"])

    def test_composition_cad_check_is_skipped_when_benchmark_artifacts_fail(self) -> None:
        output_dir = artifact_path("local_cad_regression", "composition_dependency_skip")
        commands: list[list[str]] = []

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            commands.append(command)
            command_text = " ".join(command)
            if "run_cad_validation.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "pass",
                            "include_cad": True,
                            "block_alpha": {"geometry_verified": True},
                            "evidence_summary": {"non_cad_only": False, "readback_geometry_verified_count": 2},
                        }
                    ),
                    stderr="",
                )
            if "run_project_sample_cad_check.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps({"status": "geometry_verified", "geometry_verified": True}),
                    stderr="",
                )
            if "run_benchmark_suite.py" in command_text:
                return CommandResult(returncode=1, stdout=json.dumps({"status": "fail"}), stderr="bad fixture")
            if "run_complex_cad_smoke.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps({"status": "geometry_verified", "geometry_verified": True, "created_handle_count": 23}),
                    stderr="",
                )
            if "run_primitive_matrix.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps({"status": "pass", "geometry_verified": True}),
                    stderr="",
                )
            if "run_cad_plan_fixture_suite.py" in command_text:
                if "--no-cad" in command:
                    return CommandResult(returncode=0, stdout=json.dumps({"status": "pass"}), stderr="")
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps({"status": "pass", "geometry_verified": True}),
                    stderr="",
                )
            raise AssertionError(f"unexpected command: {command}")

        report = run_local_cad_regression(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            include_cad=True,
            require_cad_verified=True,
            command_runner=fake_runner,
        )

        self.assertEqual(report["status"], "fail")
        steps = {step["id"]: step for step in report["steps"]}
        self.assertEqual(steps["interior_delivery_benchmark"]["status"], "fail")
        self.assertEqual(steps["composition_cad_check"]["status"], "not_run")
        self.assertEqual(steps["composition_cad_check"]["blocked_by"], "interior_delivery_benchmark")
        self.assertFalse(any("run_composition_cad_check.py" in " ".join(command) for command in commands))

    def test_output_dir_must_stay_under_project_output(self) -> None:
        with self.assertRaisesRegex(ValueError, "output_dir"):
            run_local_cad_regression(
                root=PROJECT_ROOT,
                output_dir=PROJECT_ROOT / "tests" / "outside_local_cad_regression",
                include_cad=False,
                command_runner=lambda command, cwd, timeout_seconds: CommandResult(0, "{}", ""),
            )


if __name__ == "__main__":
    unittest.main()
