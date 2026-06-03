from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.bootstrap import PROJECT_ROOT
from tests.core.cad_validation_payloads import (
    execution_summary_payload,
    readback_geometry_verified_payload,
)
from tests.helpers import artifact_path

from core.verification.capability_coverage import run_capability_coverage
from core.verification.capability_evidence_audit import audit_capability_evidence
from core.verification.evidence_contract import EVIDENCE_READBACK_GEOMETRY_VERIFIED
from core.verification.table_c_evidence_gate import run_table_c_evidence_gate
from core.verification.visual_cad_review import run_visual_cad_review


def _rel(path: Path) -> str:
    return str(path.resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")


def _write_json(path: Path, payload: dict[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _registry(report_path: Path) -> dict[str, object]:
    return {
        "version": "0.1",
        "registry_id": "table-c-evidence-gate-test",
        "updated_at": "2026-05-28",
        "capabilities": [
            {
                "capability_id": "test.verified.line",
                "display_name": "Verified line",
                "category": "primitive",
                "claim_level": "verified",
                "ladder_level": "L1",
                "cad_case": {"case_kind": "script", "entrypoint": "unit-test", "command": ["unit-test"]},
                "evidence": {
                    "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
                    "geometry_accuracy": "verified_by_cad_readback",
                    "screenshot_role": "visual_aid_only",
                    "report_path": _rel(report_path),
                },
            }
        ],
    }


class TableCEvidenceGateTests(unittest.TestCase):
    def test_audit_passes_for_verified_readback_report(self) -> None:
        report_path = artifact_path("table_c_evidence_gate", "valid_readback.json")
        _write_json(report_path, readback_geometry_verified_payload(handle="A1"))
        registry_path = artifact_path("table_c_evidence_gate", "valid_registry.json")
        _write_json(registry_path, _registry(report_path))

        audit = audit_capability_evidence(
            PROJECT_ROOT,
            registry_path=registry_path,
            output_path=artifact_path("table_c_evidence_gate", "valid_audit.json"),
        )

        self.assertEqual(audit["status"], "pass")
        self.assertEqual(audit["summary"]["audited_count"], 1)
        self.assertEqual(audit["summary"]["failed_count"], 0)

    def test_audit_fails_missing_report_path(self) -> None:
        missing_report = PROJECT_ROOT / "output" / "test_artifacts" / "table_c_evidence_gate" / "missing.json"
        registry_path = artifact_path("table_c_evidence_gate", "missing_registry.json")
        _write_json(registry_path, _registry(missing_report))

        audit = audit_capability_evidence(
            PROJECT_ROOT,
            registry_path=registry_path,
            output_path=artifact_path("table_c_evidence_gate", "missing_audit.json"),
        )

        self.assertEqual(audit["status"], "fail")
        self.assertEqual(audit["summary"]["failed_count"], 1)
        self.assertEqual(audit["rows"][0]["failure_category"], "report_path_missing")

    def test_audit_fails_fake_geometry_without_created_handles(self) -> None:
        report_path = artifact_path("table_c_evidence_gate", "fake_readback.json")
        payload = readback_geometry_verified_payload(handle="A2")
        payload["actual"] = {"entities": [{"handle": "A2", "type": "line", "layer": "CODEX_PREVIEW"}]}
        _write_json(report_path, payload)
        registry_path = artifact_path("table_c_evidence_gate", "fake_registry.json")
        _write_json(registry_path, _registry(report_path))

        audit = audit_capability_evidence(PROJECT_ROOT, registry_path=registry_path)

        self.assertEqual(audit["status"], "fail")
        self.assertIn("created_handles", audit["rows"][0]["message"])

    def test_visual_review_passes_with_screenshot_and_geometry_readback(self) -> None:
        output_dir = artifact_path("table_c_evidence_gate", "visual_pass", "placeholder").parent
        screenshot_path = output_dir / "cad-window.png"
        screenshot_path.write_bytes(b"fake-png")
        execution_path = _write_json(output_dir / "execution_summary.json", execution_summary_payload(handles=["V1"]))
        readback_path = _write_json(output_dir / "readback_report.json", readback_geometry_verified_payload(handle="V1", screenshot=screenshot_path))

        review = run_visual_cad_review(
            PROJECT_ROOT,
            output_dir=output_dir,
            execution_summary_path=execution_path,
            readback_report_path=readback_path,
            screenshot_path=screenshot_path,
        )

        self.assertEqual(review["status"], "pass")
        self.assertTrue(review["writeback_allowed"])
        self.assertEqual(review["screenshot_role"], "visual_aid_only")
        self.assertTrue((output_dir / "visual_review_report.json").exists())

    @patch("core.verification.visual_cad_review.prepare_autocad_for_capture", create=True)
    def test_visual_review_capture_uses_execution_summary_for_task_scoped_preview(self, mock_capture) -> None:
        output_dir = artifact_path("table_c_evidence_gate", "visual_capture_summary", "placeholder").parent
        execution_path = _write_json(output_dir / "execution_summary.json", execution_summary_payload(handles=["V3"]))
        readback_path = _write_json(
            output_dir / "readback_report.json",
            readback_geometry_verified_payload(handle="V3", screenshot=output_dir / "cad-visual-review.png"),
        )

        def capture(output: Path, **kwargs: object) -> dict[str, object]:
            output.write_bytes(b"fake-png")
            return {
                "status": "captured",
                "output": str(output),
                "mode": "autocad_window_printwindow",
                "occlusion_safe": True,
                "focus": {"status": "zoomed_to_bbox", "source": "execution_summary.created_handles", "handle_count": 1},
            }

        mock_capture.side_effect = capture

        review = run_visual_cad_review(
            PROJECT_ROOT,
            output_dir=output_dir,
            execution_summary_path=execution_path,
            readback_report_path=readback_path,
            capture=True,
        )

        self.assertEqual(review["status"], "pass", review)
        mock_capture.assert_called_once()
        self.assertEqual(mock_capture.call_args.kwargs["execution_summary"], execution_path.resolve())
        self.assertEqual(review["capture_result"]["focus"]["source"], "execution_summary.created_handles")
        self.assertEqual(review["visualPreview"]["role"], "visual_aid_only")
        self.assertEqual(review["screenshotDecision"]["focusSource"], "execution_summary.created_handles")
        self.assertTrue(review["screenshotDecision"]["visualAidOnly"])
        self.assertEqual(review["visualPreview"]["screenshotDecision"]["focusSource"], "execution_summary.created_handles")

    def test_visual_review_failure_blocks_writeback_when_screenshot_missing(self) -> None:
        output_dir = artifact_path("table_c_evidence_gate", "visual_fail", "placeholder").parent
        execution_path = _write_json(output_dir / "execution_summary.json", execution_summary_payload(handles=["V2"]))
        readback_path = _write_json(output_dir / "readback_report.json", readback_geometry_verified_payload(handle="V2"))

        review = run_visual_cad_review(
            PROJECT_ROOT,
            output_dir=output_dir,
            execution_summary_path=execution_path,
            readback_report_path=readback_path,
            screenshot_path=output_dir / "missing.png",
        )

        self.assertEqual(review["status"], "fail")
        self.assertFalse(review["writeback_allowed"])
        self.assertEqual(review["failure_category"], "visual_review_failed")

    def test_table_c_gate_blocks_writeback_when_visual_review_fails(self) -> None:
        output_dir = artifact_path("table_c_evidence_gate", "gate_visual_fail", "placeholder").parent
        audit_path = _write_json(
            output_dir / "evidence_audit_report.json",
            {"status": "pass", "summary": {"failed_count": 0}},
        )
        visual_path = _write_json(
            output_dir / "visual_review_report.json",
            {"status": "fail", "writeback_allowed": False, "failure_category": "visual_review_failed"},
        )

        gate = run_table_c_evidence_gate(
            PROJECT_ROOT,
            output_path=output_dir / "table_c_evidence_gate_report.json",
            evidence_audit_report_path=audit_path,
            visual_review_report_path=visual_path,
        )

        self.assertEqual(gate["status"], "fail")
        self.assertFalse(gate["writeback_allowed"])
        self.assertEqual(gate["coverage"]["status"], "skipped")

    def test_coverage_can_require_evidence_audit_pass(self) -> None:
        missing_report = PROJECT_ROOT / "output" / "test_artifacts" / "table_c_evidence_gate" / "coverage_missing.json"
        registry_path = artifact_path("table_c_evidence_gate", "coverage_registry.json")
        _write_json(registry_path, _registry(missing_report))

        coverage = run_capability_coverage(
            PROJECT_ROOT,
            registry_path=registry_path,
            output_path=artifact_path("table_c_evidence_gate", "coverage.json"),
            require_evidence_audit_pass=True,
        )

        self.assertEqual(coverage["status"], "fail")
        self.assertEqual(coverage["evidence_audit"]["status"], "fail")


if __name__ == "__main__":
    unittest.main()
