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
            "name": "Phase 9 preview bundle table",
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


class Phase9PreviewBundleTests(unittest.TestCase):
    def test_bundle_materializes_manifest_summary_and_relative_artifacts(self) -> None:
        from core.contracts.phase9_preview import run_phase9_single_preview
        from core.contracts.preview_bundle import build_phase9_preview_bundle
        from core.verification.fake_cad_driver import FakeCadDriver

        with temporary_artifact_dir("phase9_preview_bundle") as root:
            preview = run_phase9_single_preview(
                cad_plan=_phase9_plan(),
                output_dir=root,
                driver_factory=FakeCadDriver,
                driver_backend="fake_driver_preflight",
            )

            bundle = build_phase9_preview_bundle(run_dir=root)

            bundle_root = root / "preview_bundle"
            manifest = json.loads((bundle_root / "manifest.json").read_text(encoding="utf-8"))
            summary = json.loads((bundle_root / "summary.json").read_text(encoding="utf-8"))
            copied_report_exists = (bundle_root / manifest["artifacts"]["phase9_preview_report"]["path"]).is_file()

        self.assertEqual(bundle["schemaVersion"], "phase9-preview-bundle-result/v1")
        self.assertEqual(bundle["manifestPath"], str(bundle_root / "manifest.json"))
        self.assertEqual(manifest["schemaVersion"], "phase9-preview-bundle/v1")
        self.assertEqual(manifest["sourceRunDir"], ".")
        self.assertEqual(manifest["summary"], "summary.json")
        self.assertEqual(summary["status"], preview.status)
        self.assertEqual(summary["verificationStatus"], "not_verified")
        self.assertFalse(summary["cadGeometryVerified"])
        self.assertEqual(summary["targetLayer"], "CODEX_PREVIEW")
        self.assertIn("real_cad_readback", summary["missingEvidence"])
        self.assertEqual(summary["completionBoundary"], "preview_bundle_is_read_only_not_readback_evidence")
        self.assertIn("phase9_preview_report", manifest["artifacts"])
        self.assertEqual(
            manifest["artifacts"]["phase9_preview_report"]["path"],
            "artifacts/phase9_preview_report.json",
        )
        self.assertFalse(manifest["artifacts"]["phase9_preview_report"]["path"].startswith(str(PROJECT_ROOT)))
        self.assertTrue(copied_report_exists)
        self.assertEqual(
            summary["evidencePackageRef"],
            manifest["artifacts"]["phase9_single_preview_evidence_package"]["sourceRef"],
        )

    def test_bundle_warns_when_report_artifact_source_is_not_traceable(self) -> None:
        from core.contracts.phase9_preview import run_phase9_single_preview
        from core.contracts.preview_bundle import build_phase9_preview_bundle
        from core.verification.fake_cad_driver import FakeCadDriver

        with temporary_artifact_dir("phase9_preview_bundle_untraceable_artifact") as root:
            run_phase9_single_preview(
                cad_plan=_phase9_plan(),
                output_dir=root,
                driver_factory=FakeCadDriver,
                driver_backend="fake_driver_preflight",
            )
            report_path = root / "phase9_preview_report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["artifacts"]["evidencePackage"] = str(PROJECT_ROOT / "README.md")
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            bundle = build_phase9_preview_bundle(run_dir=root)

            bundle_root = root / "preview_bundle"
            manifest = json.loads((bundle_root / "manifest.json").read_text(encoding="utf-8"))
            summary = json.loads((bundle_root / "summary.json").read_text(encoding="utf-8"))

        self.assertNotIn("phase9_single_preview_evidence_package", manifest["artifacts"])
        self.assertIn("artifact_source_not_traceable:evidencePackage", bundle["warnings"])
        self.assertIn("artifact_source_not_traceable:evidencePackage", manifest["warnings"])
        self.assertIn("artifact_source_not_traceable:evidencePackage", summary["bundleWarnings"])

    def test_harness_bundle_command_keeps_fake_backend_not_verified(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        with temporary_artifact_dir("cad_agent_harness_bundle") as root:
            preview = run_harness_command(
                "preview",
                cad_plan=_phase9_plan(),
                output_dir=root,
                backend="fake-driver",
            )
            result = run_harness_command("bundle", run_dir=root)
            manifest = json.loads((root / "preview_bundle" / "manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(result["schemaVersion"], "cad-agent-harness-result/v1")
        self.assertEqual(result["command"], "bundle")
        self.assertEqual(result["status"], preview["status"])
        self.assertEqual(result["verificationStatus"], "not_verified")
        self.assertFalse(result["cadGeometryVerified"])
        self.assertIn("real_cad_readback", result["missingEvidence"])
        self.assertEqual(result["artifacts"]["previewBundleManifest"], str(root / "preview_bundle" / "manifest.json"))
        self.assertEqual(manifest["summary"], "summary.json")

    def test_script_bundle_outputs_json_result(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        script = PROJECT_ROOT / "scripts" / "cad_agent_harness.py"
        with temporary_artifact_dir("cad_agent_harness_bundle_script") as root:
            run_harness_command(
                "preview",
                cad_plan=_phase9_plan(),
                output_dir=root,
                backend="fake-driver",
            )
            completed = subprocess.run(
                [sys.executable, str(script), "bundle", "--run-dir", str(root), "--json"],
                cwd=PROJECT_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)

        self.assertEqual(result["schemaVersion"], "cad-agent-harness-result/v1")
        self.assertEqual(result["command"], "bundle")
        self.assertEqual(result["verificationStatus"], "not_verified")
        self.assertTrue(result["artifacts"]["previewBundleSummary"].endswith("summary.json"))


if __name__ == "__main__":
    unittest.main()
