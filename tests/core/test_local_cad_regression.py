from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.verification.cad_validation_types import CommandResult
from core.verification.local_cad_regression import run_local_cad_regression
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class LocalCadRegressionTests(unittest.TestCase):
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
        self.assertEqual(report["summary"]["deferred_case_count"], 2)
        steps = {step["id"]: step for step in report["steps"]}
        self.assertEqual(steps["baseline_cad_validation"]["status"], "pass")
        self.assertEqual(steps["project_sample_cad_check"]["status"], "deferred")
        self.assertEqual(steps["composition_cad_check"]["status"], "deferred")
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
