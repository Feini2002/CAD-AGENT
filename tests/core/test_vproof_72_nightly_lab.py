from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest import mock

from core.verification.capability_coverage import build_capability_coverage_report
from core.verification.capability_registry import validate_capability_registry
from core.verification.capability_lab import (
    LAB_NIGHTLY_ROLLUP_CAPABILITY_ID,
    VPROOF_72_BOUNDARY_DOC,
    VPROOF_72_PACKAGE_ID,
    VPROOF_72_RUNBOOK_DOC,
    assert_vproof_72_nightly_lab_contract,
    build_nightly_lab_registry_rows,
    get_tier_spec,
    load_nightly_lab_manifest,
    merge_nightly_lab_registry_rows,
    run_capability_lab,
    run_vproof_72_nightly_lab_sync,
    validate_capability_lab_report,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Vproof72NightlyLabTests(unittest.TestCase):
    def test_manifest_defines_l0_and_l1(self) -> None:
        manifest = load_nightly_lab_manifest(project_root=PROJECT_ROOT)
        self.assertIn("L0", manifest["tiers"])
        l1 = get_tier_spec(manifest, "L1")
        self.assertFalse(l1["requires_real_cad"])
        self.assertGreaterEqual(len(l1["steps"]), 6)

    def test_boundary_and_runbook_docs(self) -> None:
        for rel, phrases in (
            (
                VPROOF_72_BOUNDARY_DOC,
                ("V-PROOF-72", "lab.nightly", "不得声称", "geometry_verified", "L1"),
            ),
            (
                VPROOF_72_RUNBOOK_DOC,
                ("run_capability_lab", "--tier L1", "no-CAD", "RCAD"),
            ),
        ):
            text = (PROJECT_ROOT / rel).read_text(encoding="utf-8")
            for phrase in phrases:
                with self.subTest(rel=rel, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_lab_dry_run_builds_valid_report(self) -> None:
        output_dir = artifact_path("vproof_72", "lab_dry_run")
        report = run_capability_lab(
            project_root=PROJECT_ROOT,
            tier="L1",
            output_dir=output_dir,
            dry_run=True,
        )
        self.assertEqual(report["status"], "pass")
        self.assertEqual(validate_capability_lab_report(report, project_root=PROJECT_ROOT), [])
        self.assertEqual(report["summary"]["step_count"], 6)
        self.assertTrue(all(step["status"] == "dry_run" for step in report["steps"]))

    def test_l0_single_step_dry_run(self) -> None:
        output_dir = artifact_path("vproof_72", "l0_dry_run")
        report = run_capability_lab(
            project_root=PROJECT_ROOT,
            tier="L0",
            output_dir=output_dir,
            dry_run=True,
        )
        self.assertEqual(report["summary"]["step_count"], 1)

    @mock.patch("core.verification.capability_lab.subprocess.run")
    def test_sync_with_mocked_passing_steps(self, mock_run: mock.MagicMock) -> None:
        mock_run.return_value = mock.MagicMock(returncode=0, stdout="", stderr="")

        output_dir = artifact_path("vproof_72", "sync_mock")
        output_dir.mkdir(parents=True, exist_ok=True)
        registry = json.loads(
            (PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8")
        )
        minimal_registry = {"capabilities": registry["capabilities"][:5]}
        coverage_report = build_capability_coverage_report(
            minimal_registry,
            registry_path=PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json",
            project_root=PROJECT_ROOT,
        )
        coverage_path = output_dir / "cad_capability_coverage.json"
        coverage_path.write_text(json.dumps(coverage_report, indent=2), encoding="utf-8")

        summary = run_vproof_72_nightly_lab_sync(
            project_root=PROJECT_ROOT,
            output_dir=output_dir,
            tier="L1",
            dry_run=True,
            lab_dry_run=False,
        )
        self.assertEqual(summary["package_id"], VPROOF_72_PACKAGE_ID)
        self.assertEqual(summary["lab_status"], "pass")
        self.assertEqual(summary["writeback_rejected_count"], 0)

    def test_registry_rows_merge(self) -> None:
        registry = json.loads(
            (PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8")
        )
        merge_nightly_lab_registry_rows(registry, build_nightly_lab_registry_rows(output_root="fixture"))
        self.assertEqual(validate_capability_registry(registry), [])

    def test_live_registry_contract_when_rows_present(self) -> None:
        registry = json.loads(
            (PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8")
        )
        index = {row["capability_id"]: row for row in registry.get("capabilities", [])}
        if LAB_NIGHTLY_ROLLUP_CAPABILITY_ID not in index:
            self.skipTest("registry rows not synced yet")
        assert_vproof_72_nightly_lab_contract(project_root=PROJECT_ROOT)


if __name__ == "__main__":
    unittest.main()
