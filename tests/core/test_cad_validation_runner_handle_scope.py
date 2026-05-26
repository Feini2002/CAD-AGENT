from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import artifact_path

from core.verification.cad_validation_runner import CommandResult, run_cad_validation
from core.verification.evidence_contract import (
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE,
    SCREENSHOT_NOT_APPLICABLE,
)
from tests.core.cad_validation_payloads import (
    block_alpha_geometry_verified_payload as _block_alpha_geometry_verified_payload,
    cad_capability_verified_probe_payload as _cad_capability_verified_probe_payload,
    readback_geometry_verified_payload as _readback_geometry_verified_payload,
)


class CadValidationRunnerHandleScopeTests(unittest.TestCase):
    def test_readback_report_handles_must_match_execution_summary(self) -> None:
        output_dir = artifact_path("cad_validation", "readback_handle_mismatch")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "execute_plan.py" in command_text:
                return CommandResult(returncode=0, stdout='{"status": "executed", "created_handles": ["H1"]}', stderr="")
            if "inspect_dwg.py" in command_text:
                return CommandResult(returncode=0, stdout=json.dumps(_readback_geometry_verified_payload(handle="OTHER")), stderr="")
            if "run_cad_capability_probe.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(_cad_capability_verified_probe_payload()),
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
        self.assertEqual(steps["inspect_readback"]["status"], "fail")
        self.assertIn("execution_summary", steps["inspect_readback"]["stderr_excerpt"])

    def test_block_alpha_readback_handles_must_match_execution_summary(self) -> None:
        output_dir = artifact_path("cad_validation", "block_alpha_handle_mismatch")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "AutoCADComDriver" in command_text:
                return CommandResult(returncode=0, stdout="COM OK: TEST.dwg", stderr="")
            if "insert_block_alpha_test.json" in command_text and "execute_plan.py" in command_text:
                return CommandResult(returncode=0, stdout='{"status": "executed", "created_handles": ["EXPECTED"]}', stderr="")
            if "run_block_alpha_validation.py" in command_text:
                return CommandResult(returncode=0, stdout=json.dumps(_block_alpha_geometry_verified_payload()), stderr="")
            return CommandResult(returncode=0, stdout='{"status": "ok"}', stderr="")

        report = run_cad_validation(
            root=Path(__file__).resolve().parents[2],
            output_dir=output_dir,
            include_cad=True,
            block_alpha_only=True,
            command_runner=fake_runner,
        )

        steps = {step["id"]: step for step in report["steps"]}
        self.assertEqual(report["status"], "fail")
        self.assertEqual(steps["block_alpha_readback"]["status"], "fail")
        self.assertIn("execution_summary", steps["block_alpha_readback"]["stderr_excerpt"])


if __name__ == "__main__":
    unittest.main()
