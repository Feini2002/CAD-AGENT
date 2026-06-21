from __future__ import annotations

import json
import subprocess
import sys
import unittest

from tests.helpers import PROJECT_ROOT, temporary_artifact_dir


def _phase9_plan() -> dict[str, object]:
    return {
        "version": "0.1",
        "domain": "generic",
        "intent": "draw_object",
        "object": {
            "type": "table",
            "name": "Phase 9 exit gate table",
            "width": 900,
            "depth": 450,
        },
        "placement": {
            "mode": "absolute",
            "base_point": [72000, 42000, 0],
        },
        "drawing": {
            "layer": "CODEX_PREVIEW",
            "include_label": False,
            "include_dimensions": False,
        },
        "confidence": 0.91,
        "needs_confirmation": False,
    }


class Phase9ExitGateTests(unittest.TestCase):
    def test_exit_gate_blocks_non_empty_missing_evidence_even_if_report_claims_verified(self) -> None:
        from core.contracts.phase9_exit_gate import evaluate_phase9_exit_gate
        from core.contracts.phase9_preview import run_phase9_single_preview
        from core.verification.fake_cad_driver import FakeCadDriver

        with temporary_artifact_dir("phase9_exit_missing_evidence_claim") as root:
            run_phase9_single_preview(
                cad_plan=_phase9_plan(),
                output_dir=root,
                driver_factory=FakeCadDriver,
                driver_backend="autocad_com_existing",
            )
            report_path = root / "phase9_preview_report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["missingEvidence"] = ["real_cad_readback"]
            report["completion"]["missing_evidence"] = ["real_cad_readback"]
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result = evaluate_phase9_exit_gate(run_dir=root)

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["phase10Allowed"])
        self.assertIn("p9_missing_evidence_not_empty", result["blockingReasons"])
        self.assertIn("completion_missing_evidence_not_empty", result["blockingReasons"])

    def test_exit_gate_requires_completion_checked_real_readback_and_no_save_guard(self) -> None:
        from core.contracts.phase9_exit_gate import evaluate_phase9_exit_gate
        from core.contracts.phase9_preview import run_phase9_single_preview
        from core.verification.fake_cad_driver import FakeCadDriver

        with temporary_artifact_dir("phase9_exit_checked_evidence_gap") as root:
            run_phase9_single_preview(
                cad_plan=_phase9_plan(),
                output_dir=root,
                driver_factory=FakeCadDriver,
                driver_backend="autocad_com_existing",
            )
            report_path = root / "phase9_preview_report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["completion"]["checked_evidence"] = ["no_save_guard"]
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result = evaluate_phase9_exit_gate(run_dir=root)

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["phase10Allowed"])
        self.assertIn("completion_checked_evidence_incomplete", result["blockingReasons"])

    def test_exit_gate_blocks_malformed_counts_without_crashing(self) -> None:
        from core.contracts.phase9_exit_gate import evaluate_phase9_exit_gate
        from core.contracts.phase9_preview import run_phase9_single_preview
        from core.verification.fake_cad_driver import FakeCadDriver

        with temporary_artifact_dir("phase9_exit_bad_counts") as root:
            run_phase9_single_preview(
                cad_plan=_phase9_plan(),
                output_dir=root,
                driver_factory=FakeCadDriver,
                driver_backend="autocad_com_existing",
            )
            report_path = root / "phase9_preview_report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["createdHandleCount"] = "many"
            report["readbackEntityCount"] = "many"
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result = evaluate_phase9_exit_gate(run_dir=root)

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["phase10Allowed"])
        self.assertEqual(result["createdHandleCount"], 0)
        self.assertEqual(result["readbackEntityCount"], 0)
        self.assertIn("p9_created_handle_count_invalid", result["blockingReasons"])
        self.assertIn("p9_readback_entity_count_invalid", result["blockingReasons"])

    def test_exit_gate_blocks_fake_backend_even_when_bundle_exists(self) -> None:
        from core.contracts.phase9_exit_gate import evaluate_phase9_exit_gate
        from core.contracts.phase9_preview import run_phase9_single_preview
        from core.contracts.preview_bundle import build_phase9_preview_bundle
        from core.verification.fake_cad_driver import FakeCadDriver

        with temporary_artifact_dir("phase9_exit_fake_blocked") as root:
            run_phase9_single_preview(
                cad_plan=_phase9_plan(),
                output_dir=root,
                driver_factory=FakeCadDriver,
                driver_backend="fake_driver_preflight",
            )
            bundle = build_phase9_preview_bundle(run_dir=root)
            result = evaluate_phase9_exit_gate(run_dir=root, bundle_dir=root / "preview_bundle")

        self.assertEqual(result["schemaVersion"], "phase9-exit-gate-result/v1")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["phase10Allowed"])
        self.assertFalse(result["cadGeometryVerified"])
        self.assertFalse(result["completionCanClaimComplete"])
        self.assertIn("real_cad_readback", result["missingEvidence"])
        self.assertIn("p9a_real_cad_readback_missing", result["blockingReasons"])
        self.assertEqual(result["previewBundleManifest"], bundle["manifestPath"])
        self.assertEqual(result["decisionBoundary"], "phase9_exit_gate_does_not_create_or_upgrade_evidence")

    def test_exit_gate_allows_only_verified_real_backend_report(self) -> None:
        from core.contracts.phase9_exit_gate import evaluate_phase9_exit_gate
        from core.contracts.phase9_preview import run_phase9_single_preview
        from core.verification.fake_cad_driver import FakeCadDriver

        with temporary_artifact_dir("phase9_exit_verified") as root:
            run_phase9_single_preview(
                cad_plan=_phase9_plan(),
                output_dir=root,
                driver_factory=FakeCadDriver,
                driver_backend="autocad_com_existing",
            )
            result = evaluate_phase9_exit_gate(run_dir=root)

        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["phase10Allowed"])
        self.assertTrue(result["cadGeometryVerified"])
        self.assertTrue(result["completionCanClaimComplete"])
        self.assertEqual(result["missingEvidence"], [])
        self.assertEqual(result["blockingReasons"], [])
        self.assertEqual(result["targetLayer"], "CODEX_PREVIEW")
        self.assertFalse(result["savedCurrentDwg"])
        self.assertGreater(result["createdHandleCount"], 0)
        self.assertGreater(result["readbackEntityCount"], 0)

    def test_exit_gate_detects_bundle_report_conflict(self) -> None:
        from core.contracts.phase9_exit_gate import evaluate_phase9_exit_gate
        from core.contracts.phase9_preview import run_phase9_single_preview
        from core.contracts.preview_bundle import build_phase9_preview_bundle
        from core.verification.fake_cad_driver import FakeCadDriver

        with temporary_artifact_dir("phase9_exit_bundle_conflict") as root:
            run_phase9_single_preview(
                cad_plan=_phase9_plan(),
                output_dir=root,
                driver_factory=FakeCadDriver,
                driver_backend="fake_driver_preflight",
            )
            build_phase9_preview_bundle(run_dir=root)
            summary_path = root / "preview_bundle" / "summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["cadGeometryVerified"] = True
            summary["verificationStatus"] = "verified"
            summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result = evaluate_phase9_exit_gate(run_dir=root, bundle_dir=root / "preview_bundle")

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["phase10Allowed"])
        self.assertIn("preview_bundle_conflicts_with_report", result["blockingReasons"])

    def test_harness_exit_gate_command_outputs_json(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        script = PROJECT_ROOT / "scripts" / "cad_agent_harness.py"
        with temporary_artifact_dir("phase9_exit_gate_script") as root:
            run_harness_command(
                "preview",
                cad_plan=_phase9_plan(),
                output_dir=root,
                backend="fake-driver",
            )
            completed = subprocess.run(
                [sys.executable, str(script), "exit-gate", "--run-dir", str(root), "--json"],
                cwd=PROJECT_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(result["schemaVersion"], "cad-agent-harness-result/v1")
        self.assertEqual(result["command"], "exit-gate")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["cadGeometryVerified"])
        self.assertFalse(result["phase10Allowed"])
        self.assertIn("p9a_real_cad_readback_missing", result["blockingReasons"])


if __name__ == "__main__":
    unittest.main()
