from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.bootstrap import PROJECT_ROOT
from tests.core.cad_validation_payloads import readback_geometry_verified_payload

from core.verification.capability_coverage import build_capability_coverage_report
from core.verification.capability_registry import (
    load_capability_registry,
    load_registry_bundle,
    save_capability_registry,
    validate_capability_registry,
)
from core.verification.capability_registry_writeback import (
    WritebackRequest,
    apply_writeback,
    capability_id_for_regression_case,
    extract_geometry_evidence_from_report,
    run_registry_writeback,
    suggest_writebacks_from_regression_output,
)
from core.verification.evidence_contract import (
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE,
)


class CapabilityRegistryWritebackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.artifact_root = PROJECT_ROOT / "output" / "test_artifacts" / "capability_writeback"
        self.artifact_root.mkdir(parents=True, exist_ok=True)

    def test_load_registry_bundle_indexes_rows(self) -> None:
        bundle = load_registry_bundle(
            PROJECT_ROOT / "examples" / "capability_proof" / "cad_capability_registry.json",
            project_root=PROJECT_ROOT,
        )
        self.assertIsNotNone(bundle.get_row("regression.baseline_cad_validation"))
        self.assertEqual(validate_capability_registry(bundle.registry), [])

    def test_apply_writeback_upgrades_row_when_geometry_verified(self) -> None:
        registry = json.loads(
            (
                PROJECT_ROOT / "examples" / "capability_proof" / "cad_capability_registry.json"
            ).read_text(encoding="utf-8")
        )
        report_path = self.artifact_root / "baseline_readback_report.json"
        report_path.write_text(json.dumps(readback_geometry_verified_payload()), encoding="utf-8")
        rel_report = str(report_path.relative_to(PROJECT_ROOT)).replace("\\", "/")

        result = apply_writeback(
            registry,
            WritebackRequest(
                capability_id="regression.baseline_cad_validation",
                report_path=rel_report,
            ),
            project_root=PROJECT_ROOT,
            dry_run=False,
        )
        self.assertEqual(result.status, "applied")
        row = next(
            item
            for item in registry["capabilities"]
            if item["capability_id"] == "regression.baseline_cad_validation"
        )
        self.assertEqual(row["claim_level"], "verified")
        self.assertEqual(row["evidence"]["report_path"], rel_report)
        self.assertNotIn("deferred_reason", row)
        self.assertEqual(validate_capability_registry(registry), [])

    def test_apply_writeback_rejects_deferred_report(self) -> None:
        registry = load_capability_registry(
            PROJECT_ROOT / "examples" / "capability_proof" / "cad_capability_registry.json",
            project_root=PROJECT_ROOT,
        )
        report_path = self.artifact_root / "deferred_probe.json"
        report_path.write_text(
            json.dumps(
                {
                    "status": "deferred",
                    "evidence_state": "deferred_cad_readback_required",
                    "geometry_accuracy": "not_verified_without_cad_readback",
                    "screenshot_role": "not_applicable",
                }
            ),
            encoding="utf-8",
        )
        result = apply_writeback(
            registry,
            WritebackRequest(
                capability_id="regression.primitive_matrix_no_cad",
                report_path=str(report_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            ),
            project_root=PROJECT_ROOT,
            dry_run=True,
        )
        self.assertEqual(result.status, "rejected")

    def test_run_registry_writeback_dry_run_then_apply_updates_coverage(self) -> None:
        registry_copy_path = self.artifact_root / "registry_writeback_copy.json"
        source = PROJECT_ROOT / "examples" / "capability_proof" / "cad_capability_registry.json"
        registry_payload = json.loads(source.read_text(encoding="utf-8"))
        for row in registry_payload["capabilities"]:
            if row["capability_id"] == "primitive.hatch":
                row["claim_level"] = "deferred"
                row["deferred_reason"] = "Test fixture resets hatch to deferred before exercising writeback."
                row.pop("evidence", None)
                break
        registry_copy_path.write_text(json.dumps(registry_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        report_path = self.artifact_root / "hatch_probe_report.json"
        report_path.write_text(
            json.dumps(
                {
                    **readback_geometry_verified_payload(handle="H1"),
                    "status": "cad_capability_verified",
                    "evidence_state": EVIDENCE_CAD_CAPABILITY_VERIFIED,
                    "geometry_accuracy": GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE,
                    "screenshot_role": "not_applicable",
                }
            ),
            encoding="utf-8",
        )
        rel_report = str(report_path.relative_to(PROJECT_ROOT)).replace("\\", "/")

        dry = run_registry_writeback(
            PROJECT_ROOT,
            registry_path=registry_copy_path,
            requests=[
                WritebackRequest(
                    capability_id="primitive.hatch",
                    report_path=rel_report,
                )
            ],
            dry_run=True,
        )
        self.assertEqual(dry.status, "pass")
        self.assertEqual(dry.applied_count, 1)

        applied = run_registry_writeback(
            PROJECT_ROOT,
            registry_path=registry_copy_path,
            requests=[
                WritebackRequest(
                    capability_id="primitive.hatch",
                    report_path=rel_report,
                )
            ],
            dry_run=False,
            save_registry_file=True,
        )
        self.assertEqual(applied.status, "pass")
        saved = load_capability_registry(registry_copy_path, project_root=PROJECT_ROOT)
        before = build_capability_coverage_report(
            registry_payload,
            registry_path=source,
            project_root=PROJECT_ROOT,
            generated_at="2026-05-27T00:00:00Z",
        )
        after = build_capability_coverage_report(
            saved,
            registry_path=registry_copy_path,
            project_root=PROJECT_ROOT,
            generated_at="2026-05-27T00:00:01Z",
        )
        before_verified = before["summary"]["verified_count"]
        self.assertGreaterEqual(after["summary"]["verified_count"], before_verified)
        if dry.applied_count:
            self.assertEqual(after["summary"]["verified_count"], before_verified + dry.applied_count)
        self.assertGreater(after["summary"]["cad_proof_coverage_rate"], 0.0)

    def test_suggest_writebacks_from_regression_output(self) -> None:
        run_dir = self.artifact_root / "regression_run"
        case_dir = run_dir / "baseline_cad_validation"
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "readback_report.json").write_text(
            json.dumps(readback_geometry_verified_payload()),
            encoding="utf-8",
        )
        (case_dir / "report.json").write_text(json.dumps({"status": "pass", "steps": []}), encoding="utf-8")

        suggestions = suggest_writebacks_from_regression_output(PROJECT_ROOT, output_dir=run_dir)
        capability_ids = {item.capability_id for item in suggestions}
        self.assertIn(capability_id_for_regression_case("baseline_cad_validation"), capability_ids)

    def test_extract_geometry_evidence_from_validation_step(self) -> None:
        triplet, reason = extract_geometry_evidence_from_report(
            {
                "status": "pass",
                "steps": [
                    {
                        "id": "inspect_readback",
                        "status": "pass",
                        "evidence_state": "readback_geometry_verified",
                        "geometry_accuracy": "verified_by_cad_readback",
                        "screenshot_role": "visual_aid_only",
                    }
                ],
            }
        )
        self.assertEqual(reason, "")
        self.assertIsNotNone(triplet)
        assert triplet is not None
        self.assertEqual(triplet["evidence_state"], "readback_geometry_verified")

    def test_extract_geometry_evidence_from_real_cad_suite_summary(self) -> None:
        triplet, reason = extract_geometry_evidence_from_report(
            {
                "status": "pass",
                "evidence_summary": {
                    "geometry_verified_count": 8,
                    "non_cad_only": False,
                    "evidence_state": "readback_geometry_verified",
                    "geometry_accuracy": "verified_by_cad_readback",
                },
            }
        )
        self.assertEqual(reason, "")
        self.assertIsNotNone(triplet)
        assert triplet is not None
        self.assertEqual(triplet["evidence_state"], "readback_geometry_verified")

    def test_rejects_no_cad_suite_summary_for_writeback(self) -> None:
        triplet, reason = extract_geometry_evidence_from_report(
            {
                "status": "pass",
                "evidence_summary": {
                    "geometry_verified_count": 0,
                    "non_cad_only": True,
                    "evidence_state": "dry_run_valid_plan_only",
                    "geometry_accuracy": "not_verified_without_cad_readback",
                },
            }
        )
        self.assertIsNone(triplet)
        self.assertIn("geometry-verified", reason)


if __name__ == "__main__":
    unittest.main()
