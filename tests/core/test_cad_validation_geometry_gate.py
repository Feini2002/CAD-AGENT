from __future__ import annotations

import unittest
from pathlib import Path

from tests.helpers import artifact_path

from core.verification.cad_validation_geometry_gate import (
    build_geometry_infrastructure_gates,
    resolve_report_status_with_geometry_gate,
)
from core.verification.cad_validation_runner import CommandResult, run_cad_validation


class CadValidationGeometryGateTests(unittest.TestCase):
    def test_geometry_gate_passes_when_only_infrastructure_fails(self) -> None:
        records = [
            {"id": "unit_tests", "status": "fail", "required": True, "failure_category": "repo_regression"},
            {"id": "validate_sample_plan", "status": "pass", "required": True, "failure_category": ""},
            {"id": "dry_run_sample_plan", "status": "pass", "required": True, "failure_category": ""},
        ]
        gates = build_geometry_infrastructure_gates(records)
        self.assertEqual(gates["geometry_gate"]["status"], "pass")
        self.assertEqual(gates["infrastructure_gate"]["status"], "fail")
        self.assertEqual(
            resolve_report_status_with_geometry_gate(records, geometry_gate_mode=True),
            "pass",
        )
        self.assertEqual(
            resolve_report_status_with_geometry_gate(records, geometry_gate_mode=False),
            "fail",
        )

    def test_cad_validation_geometry_gate_mode_promotes_pass(self) -> None:
        output_dir = artifact_path("cad_validation", "geometry_gate_mode")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "unittest" in command_text and "discover" in command_text:
                return CommandResult(returncode=1, stdout="", stderr="unit test failure")
            return CommandResult(returncode=0, stdout='{"status": "ok"}', stderr="")

        report = run_cad_validation(
            root=Path(__file__).resolve().parents[2],
            output_dir=output_dir,
            include_cad=False,
            geometry_gate_mode=True,
            command_runner=fake_runner,
        )

        self.assertEqual(report["geometry_gate"]["status"], "pass")
        self.assertEqual(report["infrastructure_gate"]["status"], "fail")
        self.assertEqual(report["legacy_status"], "fail")
        self.assertEqual(report["status"], "pass")
        self.assertTrue(report.get("infrastructure_debt"))

    def test_environment_optional_mode_reports_infrastructure_debt_without_failing_geometry(self) -> None:
        output_dir = artifact_path("cad_validation", "environment_optional")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "unittest" in command_text and "discover" in command_text:
                return CommandResult(returncode=1, stdout="", stderr="unit test failure")
            return CommandResult(returncode=0, stdout='{"status": "ok"}', stderr="")

        report = run_cad_validation(
            root=Path(__file__).resolve().parents[2],
            output_dir=output_dir,
            include_cad=False,
            environment_optional=True,
            command_runner=fake_runner,
        )

        self.assertTrue(report["environment_optional"])
        self.assertEqual(report["geometry_gate"]["status"], "pass")
        self.assertEqual(report["infrastructure_gate"]["status"], "fail")
        self.assertEqual(report["legacy_status"], "fail")
        self.assertEqual(report["status"], "pass")
        self.assertTrue(report["infrastructure_debt"])
        self.assertIn("unit_tests", report["infrastructure_gate"]["failed_required_step_ids"])
