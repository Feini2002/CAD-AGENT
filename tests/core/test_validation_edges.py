from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path

from core.verification.cad_validation_runner import CommandResult, run_validation
from core.verification.verification_report import build_verification_report


class ValidationEdgeTests(unittest.TestCase):
    def test_cad_validation_writes_report_when_required_step_fails(self) -> None:
        output_dir = artifact_path("validation_edges", "failed_run")

        def fake_runner(command: list[str], cwd):
            if "scripts/self_check.py" in command:
                return CommandResult(returncode=1, stdout="", stderr="self check exploded")
            return CommandResult(returncode=0, stdout="{}", stderr="")

        report = run_validation(output_dir=output_dir, include_cad=False, runner=fake_runner)

        self.assertEqual(report["status"], "fail")
        self.assertTrue((output_dir / "report.json").exists())
        saved = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "fail")

    def test_run_validation_resolves_relative_output_dir_under_root(self) -> None:
        output_dir = Path("output/test_artifacts/validation_edges/relative_run")

        def fake_runner(command: list[str], cwd):
            return CommandResult(returncode=0, stdout="{}", stderr="")

        report = run_validation(output_dir=output_dir, include_cad=False, root=PROJECT_ROOT, runner=fake_runner)

        expected_dir = PROJECT_ROOT / output_dir
        self.assertEqual(report["output_dir"], str(expected_dir))
        self.assertTrue((expected_dir / "report.json").exists())

    def test_run_validation_relative_output_uses_explicit_root_not_cwd(self) -> None:
        root = artifact_path("validation_edges", "explicit_root")
        output_dir = Path("output/test_artifacts/validation_edges/explicit_relative_run")

        def fake_runner(command: list[str], cwd):
            return CommandResult(returncode=0, stdout="{}", stderr="")

        report = run_validation(output_dir=output_dir, include_cad=False, root=root, runner=fake_runner)

        expected_dir = root / output_dir
        self.assertEqual(report["output_dir"], str(expected_dir))
        self.assertTrue((expected_dir / "report.json").exists())

    def test_verification_does_not_upgrade_with_missing_screenshot_path(self) -> None:
        plan_path = artifact_path("validation_edges", "plan.json")
        plan_path.write_text(
            json.dumps(
                {
                    "version": "0.1",
                    "domain": "generic",
                    "intent": "draw_object",
                    "object": {"type": "cabinet", "name": "柜体", "width": 100, "depth": 50},
                    "placement": {"mode": "absolute", "base_point": [0, 0, 0]},
                    "drawing": {"layer": "CODEX_PREVIEW", "include_label": True, "include_dimensions": True},
                    "confidence": 1.0,
                    "needs_confirmation": False,
                    "safety": {"preview_only": True},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        report = build_verification_report(plan_path=plan_path, screenshot_path="missing-screen.png")

        self.assertEqual(report["status"], "unverified")
        self.assertIn("Geometry has not been fully verified from CAD readback.", report["limitations"])


if __name__ == "__main__":
    unittest.main()
