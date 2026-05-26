from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import artifact_path

from core.verification.block_alpha_validation import build_block_alpha_no_cad_report, default_block_alpha_plan_path
from core.verification.cad_validation_runner import CommandResult, run_cad_validation
from core.verification.evidence_contract import (
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)
from tests.core.cad_validation_payloads import (
    block_alpha_geometry_verified_payload as _block_alpha_geometry_verified_payload,
    cad_capability_verified_probe_payload as _cad_capability_verified_probe_payload,
    readback_geometry_verified_payload as _readback_geometry_verified_payload,
)


class CadValidationRunnerTests(unittest.TestCase):
    def test_output_dir_must_stay_under_project_output(self) -> None:
        root = Path(__file__).resolve().parents[2]

        with self.assertRaises(ValueError):
            run_cad_validation(
                root=root,
                output_dir=root / "tests" / "outside_cad_validation_output",
                include_cad=False,
                command_runner=lambda command, cwd, timeout_seconds: CommandResult(
                    returncode=0,
                    stdout='{"status": "ok"}',
                    stderr="",
                ),
            )

    def test_no_cad_run_records_block_alpha_deferred_evidence(self) -> None:
        output_dir = artifact_path("cad_validation", "block_alpha_no_cad")

        root = Path(__file__).resolve().parents[2]

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "run_block_alpha_validation.py" in command_text and "--no-cad" in command_text:
                report = build_block_alpha_no_cad_report(plan_path=default_block_alpha_plan_path(root))
                return CommandResult(returncode=0, stdout=json.dumps(report, ensure_ascii=False), stderr="")
            return CommandResult(returncode=0, stdout='{"status": "ok"}', stderr="")

        report = run_cad_validation(
            root=root,
            output_dir=output_dir,
            include_cad=False,
            command_runner=fake_runner,
        )

        steps = {step["id"]: step for step in report["steps"]}
        self.assertEqual(report["status"], "pass")
        self.assertEqual(steps["block_alpha_deferred_evidence"]["status"], "pass")
        self.assertEqual(steps["block_alpha_deferred_evidence"]["evidence_state"], EVIDENCE_DEFERRED_CAD_READBACK)
        self.assertFalse(report["block_alpha"]["geometry_verified"])
        self.assertTrue(report["evidence_summary"]["non_cad_only"])
        self.assertEqual(report["evidence_summary"]["readback_geometry_verified_count"], 0)
        block_report = json.loads((output_dir / "block_alpha_report.json").read_text(encoding="utf-8"))
        self.assertEqual(block_report["status"], "deferred")
        self.assertEqual(block_report["geometry_accuracy"], NON_CAD_GEOMETRY_ACCURACY)

    def test_no_cad_block_alpha_only_records_deferred_evidence(self) -> None:
        output_dir = artifact_path("cad_validation", "block_alpha_only_no_cad")

        root = Path(__file__).resolve().parents[2]

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "run_block_alpha_validation.py" in command_text and "--no-cad" in command_text:
                report = build_block_alpha_no_cad_report(plan_path=default_block_alpha_plan_path(root))
                return CommandResult(returncode=0, stdout=json.dumps(report, ensure_ascii=False), stderr="")
            return CommandResult(returncode=0, stdout='{"status": "ok"}', stderr="")

        report = run_cad_validation(
            root=root,
            output_dir=output_dir,
            include_cad=False,
            block_alpha_only=True,
            command_runner=fake_runner,
        )

        steps = {step["id"]: step for step in report["steps"]}
        self.assertEqual(report["status"], "pass")
        self.assertIn("block_alpha_deferred_evidence", steps)
        self.assertEqual(report["block_alpha"]["step_id"], "block_alpha_deferred_evidence")
        self.assertFalse(report["block_alpha"]["geometry_verified"])

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
        self.assertEqual(steps["block_alpha_execute"]["status"], "not_run")
        self.assertEqual(steps["block_alpha_readback"]["status"], "not_run")
        self.assertFalse((output_dir / "execution_summary.json").exists())
        self.assertFalse((output_dir / "readback_report.json").exists())

    def test_all_successful_steps_report_pass(self) -> None:
        output_dir = artifact_path("cad_validation", "pass")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "insert_block_alpha_test.json" in command_text and "execute_plan.py" in command_text:
                return CommandResult(returncode=0, stdout='{"status": "executed", "created_handles": ["BR1"]}', stderr="")
            if "execute_plan.py" in command_text:
                return CommandResult(returncode=0, stdout='{"status": "executed", "created_handles": ["ABCD"]}', stderr="")
            if "inspect_dwg.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(_readback_geometry_verified_payload(handle="ABCD", screenshot=output_dir / "cad-validation-window.png")),
                    stderr="",
                )
            if "run_cad_capability_probe.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(_cad_capability_verified_probe_payload()),
                    stderr="",
                )
            if "run_block_alpha_validation.py" in command_text:
                return CommandResult(returncode=0, stdout=json.dumps(_block_alpha_geometry_verified_payload()), stderr="")
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
        self.assertEqual(steps["cad_capability_probe"]["evidence_state"], EVIDENCE_CAD_CAPABILITY_VERIFIED)
        self.assertEqual(steps["inspect_readback"]["evidence_state"], EVIDENCE_READBACK_GEOMETRY_VERIFIED)
        self.assertEqual(steps["block_alpha_readback"]["status"], "pass")
        self.assertTrue((output_dir / "block_alpha_report.json").exists())
        self.assertEqual(steps["capture_screen"]["screenshot_role"], "visual_aid_only")
        self.assertIn("--capture-autocad-window", steps["capture_screen"]["command"])
        self.assertIn("cad-validation-window.png", " ".join(steps["capture_screen"]["command"]))
        self.assertTrue((output_dir / "cad_capability_probe.json").exists())
        self.assertTrue((output_dir / "execution_summary.json").exists())
        self.assertTrue((output_dir / "cad-validation-window.png").as_posix().endswith("cad-validation-window.png"))
        self.assertGreaterEqual(report["evidence_summary"]["readback_geometry_verified_count"], 1)
        self.assertEqual(report["evidence_summary"]["cad_capability_verified_count"], 1)
        self.assertFalse(report["evidence_summary"]["non_cad_only"])

    def test_top_level_pass_downgraded_when_readback_evidence_state_invalid(self) -> None:
        output_dir = artifact_path("cad_validation", "readback_invalid_evidence_state")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "execute_plan.py" in command_text:
                return CommandResult(returncode=0, stdout='{"status": "executed", "created_handles": ["H1"]}', stderr="")
            if "inspect_dwg.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "geometry_verified",
                            "evidence_state": "benchmark_pass_non_cad",
                            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
                            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
                            "evidence": {"execution_summary": {"created_handles": ["H1"]}, "screenshot": ""},
                            "actual": {
                                "entities": [{"handle": "H1", "type": "line", "layer": "CODEX_PREVIEW"}],
                                "created_handles": ["H1"],
                            },
                            "checks": [
                                {"name": "readback_scope", "status": "pass"},
                                {"name": "created_handles_scope", "status": "pass"},
                            ],
                        }
                    ),
                    stderr="",
                )
            if "run_cad_capability_probe.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(_cad_capability_verified_probe_payload(checks=[{"name": "line", "status": "pass"}])),
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
        stderr = steps["inspect_readback"]["stderr_excerpt"]
        self.assertTrue(
            "unknown evidence_state" in stderr or "benchmark_pass_non_cad" in stderr,
            stderr,
        )

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
                return CommandResult(returncode=0, stdout=json.dumps(_cad_capability_verified_probe_payload(checks=[])), stderr="")
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

    def test_readback_report_geometry_verified_requires_created_handle_evidence(self) -> None:
        output_dir = artifact_path("cad_validation", "readback_fake_geometry_verified")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "execute_plan.py" in command_text:
                return CommandResult(returncode=0, stdout='{"status": "executed", "created_handles": ["H1"]}', stderr="")
            if "inspect_dwg.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "geometry_verified",
                            "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
                            "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK,
                            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
                            "evidence": {},
                            "actual": {"entities": [{"handle": "H1", "type": "line"}]},
                            "checks": [
                                {"name": "readback_scope", "status": "pass"},
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
                        _cad_capability_verified_probe_payload(
                            checks=[{"name": "handle_readback_count", "status": "pass"}],
                        )
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
        self.assertEqual(steps["inspect_readback"]["status"], "fail")
        self.assertIn("created_handles", steps["inspect_readback"]["stderr_excerpt"])

    def test_block_alpha_readback_requires_created_handles_and_block_reference_entity(self) -> None:
        output_dir = artifact_path("cad_validation", "block_alpha_fake_geometry_verified")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "AutoCADComDriver" in command_text:
                return CommandResult(returncode=0, stdout="COM OK: TEST.dwg", stderr="")
            if "insert_block_alpha_test.json" in command_text and "execute_plan.py" in command_text:
                return CommandResult(returncode=0, stdout='{"status": "executed", "created_handles": ["BR1"]}', stderr="")
            if "run_block_alpha_validation.py" in command_text:
                payload = _block_alpha_geometry_verified_payload()
                payload.pop("created_handles")
                payload["entity"] = {"handle": "BR1", "type": "line"}
                return CommandResult(returncode=0, stdout=json.dumps(payload), stderr="")
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
        self.assertIn("created_handles", steps["block_alpha_readback"]["stderr_excerpt"])

    def test_cad_capability_probe_must_be_verified_for_cad_pass(self) -> None:
        output_dir = artifact_path("cad_validation", "capability_not_verified")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "execute_plan.py" in command_text:
                return CommandResult(returncode=0, stdout='{"status": "executed", "created_handles": ["H1"]}', stderr="")
            if "inspect_dwg.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(_readback_geometry_verified_payload(handle="H1")),
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

    def test_cad_capability_probe_missing_evidence_fields_fail_gate(self) -> None:
        output_dir = artifact_path("cad_validation", "capability_missing_evidence")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "execute_plan.py" in command_text:
                return CommandResult(returncode=0, stdout='{"status": "executed", "created_handles": ["H1"]}', stderr="")
            if "inspect_dwg.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(_readback_geometry_verified_payload(handle="H1")),
                    stderr="",
                )
            if "run_cad_capability_probe.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "cad_capability_verified",
                            "checks": [{"name": "handle_readback_count", "status": "pass"}],
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
        self.assertIn("missing required field", steps["cad_capability_probe"]["stderr_excerpt"])


if __name__ == "__main__":
    unittest.main()
