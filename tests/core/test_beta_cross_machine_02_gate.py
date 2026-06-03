from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.helpers import PROJECT_ROOT, artifact_path

from core.verification import cross_machine_reverify
from core.verification.cross_machine_reverify import run_beta_cross_machine_02_gate


class BetaCrossMachine02GateTests(unittest.TestCase):
    def test_no_cad_gate_builds_report(self) -> None:
        output_dir = artifact_path("beta_cross_machine_02", "no_cad")
        report = run_beta_cross_machine_02_gate(
            project_root=PROJECT_ROOT,
            output_dir=output_dir,
            include_real_cad=False,
            skip_unittest=True,
        )
        self.assertIn(report["status"], {"pass", "partial", "blocked"})
        report_path = output_dir / "beta_cross_machine_02_report.json"
        self.assertTrue(report_path.is_file())
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["package_id"], "BETA-CROSS-MACHINE-02")

    @patch("core.verification.cross_machine_reverify._probe_autocad_com")
    @patch("core.verification.cross_machine_reverify._run_subprocess")
    def test_real_cad_capture_passes_generated_execution_summary_to_preview(self, mock_run, mock_probe) -> None:
        output_dir = artifact_path("beta_cross_machine_02", "task_scoped_capture")
        mock_probe.return_value = {
            "step_id": "autocad_session",
            "title": "AutoCAD COM active document",
            "status": "pass",
            "active_document": "Drawing1.dwg",
        }

        def fake_run(command: list[str], *, project_root: Path, timeout: int = 600) -> dict[str, object]:
            if "scripts/execute_plan.py" in command:
                return {
                    "command": command,
                    "exit_code": 0,
                    "status": "pass",
                    "stdout": '{"status":"executed","created_handles":["H1","H2","H3","H4"]}',
                    "stdout_tail": '{"status":"executed","created_handles":["H1","H2","H3","H4"]}',
                    "stderr_tail": "",
                }
            if "scripts/render_preview.py" in command:
                output = Path(command[command.index("--output") + 1])
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b"fake-png")
                return {
                    "command": command,
                    "exit_code": 0,
                    "status": "pass",
                    "stdout": '{"status":"captured"}',
                    "stdout_tail": '{"status":"captured"}',
                    "stderr_tail": "",
                }
            return {"command": command, "exit_code": 0, "status": "pass", "stdout": "", "stdout_tail": "", "stderr_tail": ""}

        mock_run.side_effect = fake_run

        steps = cross_machine_reverify._run_real_cad_user_gate(
            project_root=PROJECT_ROOT,
            python_exe=Path("python.exe"),
            output_dir=output_dir,
        )

        capture = next(step for step in steps if step["step_id"] == "capture_window")
        command = capture["command"]
        self.assertIn("--execution-summary", command)
        summary_path = Path(command[command.index("--execution-summary") + 1])
        self.assertTrue(summary_path.is_file(), summary_path)
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(summary["created_handles"], ["H1", "H2", "H3", "H4"])


if __name__ == "__main__":
    unittest.main()
