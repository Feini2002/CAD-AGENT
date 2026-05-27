from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.verification.cad_validation_types import CommandResult
from core.verification.evidence_trend import validate_evidence_trend_report
from core.verification.evidence_vocabulary import EVIDENCE_DEFERRED_CAD_READBACK
from core.verification.local_cad_regression import run_local_cad_regression
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class LocalCadRegressionTrendTests(unittest.TestCase):
    def test_no_cad_mode_writes_evidence_trend_rollup(self) -> None:
        output_dir = artifact_path("local_cad_regression", "trend_no_cad")

        def fake_runner(command: list[str], cwd: Path, timeout_seconds: int) -> CommandResult:
            command_text = " ".join(command)
            if "run_cad_validation.py" in command_text:
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "status": "pass",
                            "evidence_summary": {
                                "deferred_cad_readback_required_count": 1,
                                "readback_geometry_verified_count": 0,
                                "cad_capability_verified_count": 0,
                            },
                        }
                    ),
                    stderr="",
                )
            return CommandResult(
                returncode=0,
                stdout=json.dumps({"status": "deferred", "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK}),
                stderr="",
            )

        run_local_cad_regression(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            include_cad=False,
            command_runner=fake_runner,
        )

        trend_path = output_dir / "evidence_trend" / "local_cad_regression_trend.json"
        self.assertTrue(trend_path.is_file())
        trend = json.loads(trend_path.read_text(encoding="utf-8"))
        self.assertEqual(validate_evidence_trend_report(trend), [])
        self.assertEqual(trend["report_id"], "local-cad-regression-trend")
        self.assertEqual(trend["snapshots"][0]["source_kind"], "local_cad_regression")
        self.assertEqual(trend["summary"]["snapshot_count"], 1)
        self.assertGreater(trend["summary"]["deferred_count"], 0)
        self.assertTrue(trend["summary"]["non_cad_only"])


if __name__ == "__main__":
    unittest.main()
