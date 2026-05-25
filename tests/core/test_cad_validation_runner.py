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

    def test_all_successful_steps_report_pass(self) -> None:
        output_dir = artifact_path("cad_validation", "pass")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            return CommandResult(returncode=0, stdout='{"status": "ok", "created_handles": ["ABCD"]}', stderr="")

        report = run_cad_validation(
            root=Path(__file__).resolve().parents[2],
            output_dir=output_dir,
            include_cad=True,
            command_runner=fake_runner,
        )

        self.assertEqual(report["status"], "pass")
        self.assertTrue((output_dir / "execution_summary.json").exists())
        self.assertTrue((output_dir / "cad-validation-screen.png").as_posix().endswith("cad-validation-screen.png"))


if __name__ == "__main__":
    unittest.main()
