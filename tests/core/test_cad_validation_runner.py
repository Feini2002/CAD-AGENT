from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import artifact_path

from core.verification.cad_validation_runner import CommandResult, run_cad_validation


class CadValidationRunnerTests(unittest.TestCase):
    def test_cad_connection_failure_is_reported_as_external_blocker(self) -> None:
        output_dir = artifact_path("cad_validation", "external_blocker")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "AutoCADComDriver" in command_text:
                return CommandResult(returncode=1, stdout="", stderr="AutoCAD is not running")
            return CommandResult(returncode=0, stdout='{"status": "pass"}', stderr="")

        report = run_cad_validation(
            root=Path(__file__).resolve().parents[2],
            output_dir=output_dir,
            include_cad=True,
            command_runner=fake_runner,
        )

        self.assertEqual(report["status"], "external_blocker")
        steps = {step["id"]: step for step in report["steps"]}
        self.assertEqual(steps["autocad_com_connect"]["status"], "fail")
        self.assertEqual(steps["autocad_com_connect"]["failure_category"], "cad_connection_failed")
        self.assertTrue((output_dir / "report.json").exists())
        self.assertTrue((output_dir / "report.md").exists())

        saved = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "external_blocker")

    def test_cad_connection_failure_skips_dependent_cad_steps(self) -> None:
        output_dir = artifact_path("cad_validation", "cad_dependency_skip")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "AutoCADComDriver" in command_text:
                return CommandResult(returncode=1, stdout="", stderr="AutoCAD.Application invalid class string")
            return CommandResult(returncode=0, stdout='{"status": "pass"}', stderr="")

        report = run_cad_validation(
            root=Path(__file__).resolve().parents[2],
            output_dir=output_dir,
            include_cad=True,
            command_runner=fake_runner,
        )

        steps = {step["id"]: step for step in report["steps"]}
        self.assertEqual(report["status"], "external_blocker")
        self.assertEqual(steps["autocad_com_connect"]["status"], "fail")
        self.assertEqual(steps["execute_sample_plan"]["status"], "not_run")
        self.assertEqual(steps["capture_screen"]["status"], "not_run")
        self.assertEqual(steps["inspect_readback"]["status"], "not_run")
        self.assertFalse((output_dir / "execution_summary.json").exists())
        self.assertFalse((output_dir / "readback_report.json").exists())

    def test_all_successful_steps_report_pass(self) -> None:
        output_dir = artifact_path("cad_validation", "pass")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "execute_plan.py" in command_text:
                return CommandResult(returncode=0, stdout='{"status": "executed", "created_handles": ["ABCD"]}', stderr="")
            if "inspect_dwg.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "geometry_verified",
                            "checks": [
                                {"name": "geometry_readback", "status": "pass"},
                                {"name": "created_handles_scope", "status": "pass"},
                            ],
                        }
                    ),
                    stderr="",
                )
            if "run_cad_capability_probe.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "cad_capability_verified",
                            "checks": [
                                {"name": "handle_readback_count", "status": "pass"},
                                {"name": "readback_type_counts", "status": "pass"},
                            ],
                        }
                    ),
                    stderr="",
                )
            return CommandResult(returncode=0, stdout='{"status": "ok"}', stderr="")

        report = run_cad_validation(
            root=Path(__file__).resolve().parents[2],
            output_dir=output_dir,
            include_cad=True,
            command_runner=fake_runner,
        )

        self.assertEqual(report["status"], "pass")
        steps = {step["id"]: step for step in report["steps"]}
        self.assertEqual(steps["cad_capability_probe"]["status"], "pass")
        self.assertEqual(steps["capture_screen"]["screenshot_role"], "visual_aid_only")
        self.assertIn("--capture-autocad-window", steps["capture_screen"]["command"])
        self.assertIn("cad-validation-window.png", " ".join(steps["capture_screen"]["command"]))
        self.assertTrue((output_dir / "cad_capability_probe.json").exists())
        self.assertTrue((output_dir / "execution_summary.json").exists())
        self.assertTrue((output_dir / "cad-validation-window.png").as_posix().endswith("cad-validation-window.png"))

    def test_readback_report_must_be_geometry_verified_for_cad_pass(self) -> None:
        output_dir = artifact_path("cad_validation", "readback_not_verified")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "execute_plan.py" in command_text:
                return CommandResult(returncode=0, stdout='{"status": "executed", "created_handles": ["H1"]}', stderr="")
            if "inspect_dwg.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "screenshot_captured",
                            "checks": [
                                {"name": "geometry_readback", "status": "not_run"},
                                {"name": "created_handles_scope", "status": "warning"},
                            ],
                        }
                    ),
                    stderr="",
                )
            if "run_cad_capability_probe.py" in command_text:
                return CommandResult(returncode=0, stdout='{"status": "cad_capability_verified", "checks": []}', stderr="")
            return CommandResult(returncode=0, stdout='{"status": "ok"}', stderr="")

        report = run_cad_validation(
            root=Path(__file__).resolve().parents[2],
            output_dir=output_dir,
            include_cad=True,
            command_runner=fake_runner,
        )

        steps = {step["id"]: step for step in report["steps"]}
        self.assertEqual(report["status"], "fail")
        self.assertEqual(steps["inspect_readback"]["status"], "fail")
        self.assertEqual(steps["inspect_readback"]["failure_category"], "readback_failed")
        self.assertIn("geometry_verified", steps["inspect_readback"]["stderr_excerpt"])

    def test_cad_capability_probe_must_be_verified_for_cad_pass(self) -> None:
        output_dir = artifact_path("cad_validation", "capability_not_verified")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "execute_plan.py" in command_text:
                return CommandResult(returncode=0, stdout='{"status": "executed", "created_handles": ["H1"]}', stderr="")
            if "inspect_dwg.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps({"status": "geometry_verified", "checks": [{"name": "readback_scope", "status": "pass"}]}),
                    stderr="",
                )
            if "run_cad_capability_probe.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "failed",
                            "checks": [
                                {"name": "handle_readback_count", "status": "fail"},
                            ],
                        }
                    ),
                    stderr="",
                )
            return CommandResult(returncode=0, stdout='{"status": "ok"}', stderr="")

        report = run_cad_validation(
            root=Path(__file__).resolve().parents[2],
            output_dir=output_dir,
            include_cad=True,
            command_runner=fake_runner,
        )

        steps = {step["id"]: step for step in report["steps"]}
        self.assertEqual(report["status"], "fail")
        self.assertEqual(steps["cad_capability_probe"]["status"], "fail")
        self.assertEqual(steps["cad_capability_probe"]["failure_category"], "cad_capability_failed")
        self.assertIn("cad_capability_verified", steps["cad_capability_probe"]["stderr_excerpt"])


if __name__ == "__main__":
    unittest.main()
