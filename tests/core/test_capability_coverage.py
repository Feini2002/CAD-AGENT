from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.bootstrap import PROJECT_ROOT

from core.verification.capability_coverage import (
    DEFAULT_OUTPUT_PATH,
    build_capability_coverage_report,
    run_capability_coverage,
)
from core.verification.evidence_trend import validate_evidence_trend_report
from core.verification.capability_registry import load_capability_registry


class CapabilityCoverageTests(unittest.TestCase):
    def test_seed_registry_coverage_counts(self) -> None:
        registry_path = PROJECT_ROOT / "examples" / "capability_proof" / "cad_capability_registry.json"
        registry = load_capability_registry(registry_path, project_root=PROJECT_ROOT)
        report = build_capability_coverage_report(
            registry,
            registry_path=registry_path,
            project_root=PROJECT_ROOT,
            generated_at="2026-05-27T00:00:00Z",
        )

        summary = report["summary"]
        self.assertEqual(report["status"], "pass")
        self.assertGreaterEqual(summary["total_count"], 200)
        self.assertGreaterEqual(summary["verified_count"], 25)
        self.assertGreaterEqual(summary["showcase_count"], 1)
        self.assertEqual(summary["cad_proof_count"], summary["verified_count"] + summary["showcase_count"])
        self.assertGreater(summary["cad_proof_coverage_rate"], 0.0)
        self.assertIn("cad_strength_headline_percent", summary)
        self.assertIn("cad_strength_index_percent", summary)
        self.assertIn("scene_fragment_strength_percent", summary)
        self.assertGreater(summary["showcase_readiness_percent"], 0.0)
        self.assertLessEqual(
            summary["cad_strength_headline_percent"],
            summary["cad_strength_index_percent"],
        )
        self.assertEqual(report["cad_strength"]["cad_strength_headline_percent"], summary["cad_strength_headline_percent"])
        baseline = next(
            row for row in registry["capabilities"] if row["capability_id"] == "regression.baseline_cad_validation"
        )
        self.assertEqual(baseline["claim_level"], "verified")
        self.assertGreaterEqual(report["category_cad_proof"]["primitive"]["verified_count"], 6)
        self.assertGreaterEqual(report["category_cad_proof"]["other"]["verified_count"], 3)
        self.assertGreaterEqual(report["category_cad_proof"]["object"]["verified_count"], 8)
        self.assertGreaterEqual(report["category_cad_proof"]["intent"]["verified_count"], 3)
        self.assertEqual(sum(report["by_claim_level"].values()), summary["total_count"])
        self.assertIn("trend", report)
        self.assertEqual(report["trend"]["series_id"], "cad_capability_coverage")

    def test_run_capability_coverage_writes_output(self) -> None:
        output_path = PROJECT_ROOT / "output" / "test_artifacts" / "capability_coverage" / "cad_capability_coverage.json"
        if output_path.exists():
            output_path.unlink()
        report = run_capability_coverage(
            PROJECT_ROOT,
            output_path=output_path,
            generated_at="2026-05-27T00:00:01Z",
        )
        self.assertEqual(report["status"], "pass")
        self.assertTrue(output_path.is_file())
        on_disk = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk["summary"]["total_count"], report["summary"]["total_count"])
        rel = str(output_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        self.assertEqual(report.get("output_path"), rel)

    def test_run_capability_coverage_writes_evidence_trend_hook(self) -> None:
        output_path = (
            PROJECT_ROOT
            / "output"
            / "test_artifacts"
            / "capability_coverage"
            / "trend_hook"
            / "cad_capability_coverage.json"
        )
        trend_path = output_path.parent / "evidence_trend" / "capability_coverage_trend.json"
        if trend_path.exists():
            trend_path.unlink()

        report = run_capability_coverage(
            PROJECT_ROOT,
            output_path=output_path,
            generated_at="2026-05-27T00:00:03Z",
        )

        self.assertEqual(report["status"], "pass")
        self.assertTrue(trend_path.is_file())
        trend = json.loads(trend_path.read_text(encoding="utf-8"))
        self.assertEqual(validate_evidence_trend_report(trend), [])
        self.assertEqual(trend["report_id"], "capability-coverage-trend")
        self.assertEqual(trend["summary"]["snapshot_count"], 1)
        self.assertEqual(trend["snapshots"][0]["source_kind"], "capability_coverage")
        self.assertEqual(
            trend["snapshots"][0]["metrics"]["cad_proof_coverage_rate"],
            report["summary"]["cad_proof_coverage_rate"],
        )

    def test_default_output_path_is_under_capability_lab(self) -> None:
        self.assertEqual(
            DEFAULT_OUTPUT_PATH.as_posix(),
            "output/validation_runs/capability-lab/cad_capability_coverage.json",
        )

    def test_invalid_registry_returns_invalid_status(self) -> None:
        report = run_capability_coverage(
            PROJECT_ROOT,
            registry_path=PROJECT_ROOT / "examples" / "capability_proof" / "minimal_cad_capability_registry.json",
            output_path=None,
        )
        self.assertEqual(report["status"], "pass")

        broken = {
            "version": "0.1",
            "registry_id": "broken",
            "capabilities": [
                {
                    "capability_id": "broken.verified",
                    "display_name": "Broken",
                    "category": "intent",
                    "claim_level": "verified",
                    "ladder_level": "L1",
                }
            ],
        }
        broken_path = PROJECT_ROOT / "output" / "test_artifacts" / "capability_coverage" / "broken_registry.json"
        broken_path.parent.mkdir(parents=True, exist_ok=True)
        broken_path.write_text(json.dumps(broken), encoding="utf-8")
        invalid_report = run_capability_coverage(PROJECT_ROOT, registry_path=broken_path, output_path=None)
        self.assertEqual(invalid_report["status"], "invalid")
        self.assertTrue(invalid_report.get("errors"))


if __name__ == "__main__":
    unittest.main()
