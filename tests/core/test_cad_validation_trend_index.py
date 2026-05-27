from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.verification.block_alpha_validation import build_block_alpha_no_cad_report, default_block_alpha_plan_path
from core.verification.cad_validation_runner import CommandResult, run_cad_validation
from core.verification.cad_validation_trend_index import CAD_VALIDATION_TREND_INDEX_FILENAME
from core.verification.evidence_trend import validate_evidence_trend_report
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class CadValidationTrendIndexTests(unittest.TestCase):
    def test_run_cad_validation_writes_historical_trend_index(self) -> None:
        output_root = artifact_path("cad_validation", "trend_index")
        previous_dir = output_root / "previous"
        current_dir = output_root / "current"
        previous_dir.mkdir(parents=True, exist_ok=True)
        previous_report = {
            "status": "pass",
            "generated_at": "2026-05-27T00:00:00",
            "include_cad": False,
            "evidence_summary": {
                "deferred_cad_readback_required_count": 1,
                "readback_geometry_verified_count": 0,
                "cad_capability_verified_count": 0,
                "non_cad_only": True,
            },
        }
        (previous_dir / "report.json").write_text(json.dumps(previous_report), encoding="utf-8")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "run_block_alpha_validation.py" in command_text and "--no-cad" in command_text:
                report = build_block_alpha_no_cad_report(plan_path=default_block_alpha_plan_path(PROJECT_ROOT))
                return CommandResult(returncode=0, stdout=json.dumps(report, ensure_ascii=False), stderr="")
            return CommandResult(returncode=0, stdout='{"status": "ok"}', stderr="")

        run_cad_validation(
            root=PROJECT_ROOT,
            output_dir=current_dir,
            include_cad=False,
            command_runner=fake_runner,
        )

        trend_path = current_dir / "evidence_trend" / CAD_VALIDATION_TREND_INDEX_FILENAME
        self.assertTrue(trend_path.is_file())
        trend = json.loads(trend_path.read_text(encoding="utf-8"))
        self.assertEqual(validate_evidence_trend_report(trend), [])
        self.assertEqual(trend["report_id"], "cad-validation-trend-index")
        self.assertEqual(trend["summary"]["snapshot_count"], 2)
        self.assertEqual({snapshot["source_kind"] for snapshot in trend["snapshots"]}, {"cad_validation"})
        self.assertIn("output/test_artifacts/cad_validation/trend_index/previous/report.json", {
            snapshot["source_path"] for snapshot in trend["snapshots"]
        })
        self.assertTrue(trend["summary"]["non_cad_only"])


if __name__ == "__main__":
    unittest.main()
