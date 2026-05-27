from __future__ import annotations

import json
import unittest

from tests.bootstrap import PROJECT_ROOT

from core.schemas.validator import validate_value
from core.verification.evidence_trend import (
    EVIDENCE_TREND_SOURCE_KINDS,
    build_evidence_trend_report,
    build_evidence_trend_snapshot,
    validate_evidence_trend_report,
)
from core.verification.evidence_vocabulary import (
    EVIDENCE_BENCHMARK_PASS_NON_CAD,
    EVIDENCE_NEGATIVE_GUARD_VERIFIED,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    EVIDENCE_STATE_VALUES,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)


class EvidenceTrendTests(unittest.TestCase):
    def test_snapshot_completes_counts_and_keeps_negative_guard_out_of_cad_proof(self) -> None:
        snapshot = build_evidence_trend_snapshot(
            snapshot_id="negative-runner-fake-final",
            series_id="negative_cad_runner",
            source_kind="negative_cad_runner",
            source_path="output/validation_runs/neg-cad-proof-sync/negative-runner-fake-final/negative_cad_runner_report.json",
            snapshot_at="2026-05-27T00:00:00Z",
            evidence_state_counts={EVIDENCE_NEGATIVE_GUARD_VERIFIED: 1},
            geometry_accuracy_counts={NON_CAD_GEOMETRY_ACCURACY: 1},
            screenshot_role_counts={SCREENSHOT_NOT_APPLICABLE: 1},
            metrics={"created_handle_count": 0, "blocked_attempt_count": 4},
        )

        self.assertEqual(set(snapshot["evidence_state_counts"]), EVIDENCE_STATE_VALUES)
        self.assertEqual(snapshot["evidence_state_counts"][EVIDENCE_NEGATIVE_GUARD_VERIFIED], 1)
        self.assertEqual(snapshot["summary"]["guard_only_count"], 1)
        self.assertEqual(snapshot["summary"]["cad_proof_state_count"], 0)
        self.assertEqual(snapshot["summary"]["geometry_verified_count"], 0)
        self.assertTrue(snapshot["summary"]["non_cad_only"])

    def test_report_validation_rejects_unknown_evidence_state(self) -> None:
        snapshot = build_evidence_trend_snapshot(
            snapshot_id="baseline",
            series_id="local_cad_regression",
            source_kind="local_cad_regression",
            source_path="output/validation_runs/local-cad-regression-no-cad/local_cad_regression_report.json",
            snapshot_at="2026-05-27T00:00:01Z",
            evidence_state_counts={EVIDENCE_BENCHMARK_PASS_NON_CAD: 1},
        )
        snapshot["evidence_state_counts"]["made_up_state"] = 1
        report = build_evidence_trend_report(
            report_id="evidence-trend-test",
            generated_at="2026-05-27T00:00:02Z",
            snapshots=[snapshot],
        )

        errors = validate_evidence_trend_report(report)

        self.assertTrue(errors)
        self.assertIn("made_up_state", "\n".join(errors))

    def test_schema_vocabulary_matches_shared_evidence_values(self) -> None:
        schema_path = PROJECT_ROOT / "core" / "schemas" / "evidence_trend.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        state_schema = schema["properties"]["snapshots"]["items"]["properties"]["evidence_state_counts"]

        self.assertEqual(set(state_schema["required"]), EVIDENCE_STATE_VALUES)
        self.assertEqual(set(state_schema["properties"]), EVIDENCE_STATE_VALUES)
        self.assertIn("negative_cad_runner", EVIDENCE_TREND_SOURCE_KINDS)

        report = build_evidence_trend_report(
            report_id="evidence-trend-minimal",
            generated_at="2026-05-27T00:00:03Z",
            snapshots=[
                build_evidence_trend_snapshot(
                    snapshot_id="geometry-verified",
                    series_id="cad_validation",
                    source_kind="cad_validation",
                    source_path="output/validation_runs/example/readback_report.json",
                    snapshot_at="2026-05-27T00:00:03Z",
                    evidence_state_counts={EVIDENCE_READBACK_GEOMETRY_VERIFIED: 1},
                )
            ],
        )

        self.assertEqual(validate_value(report, schema), [])
        self.assertEqual(validate_evidence_trend_report(report), [])


if __name__ == "__main__":
    unittest.main()
