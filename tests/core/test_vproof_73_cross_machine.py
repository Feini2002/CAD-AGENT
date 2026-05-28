from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

from core.verification.capability_registry import validate_capability_registry
from core.verification.cross_machine_proof import (
    CROSS_MACHINE_COVERAGE_RECALC_CAPABILITY_ID,
    CROSS_MACHINE_PLAYBOOK_CAPABILITY_ID,
    VPROOF_73_BOUNDARY_DOC,
    VPROOF_73_PACKAGE_ID,
    assert_vproof_73_cross_machine_contract,
    build_cross_machine_registry_rows,
    build_cross_machine_report,
    compare_coverage_to_baseline,
    load_cross_machine_playbook_manifest,
    merge_cross_machine_registry_rows,
    run_vproof_73_cross_machine_sync,
    validate_cross_machine_report,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Vproof73CrossMachineTests(unittest.TestCase):
    def test_playbook_manifest_has_user_gate_steps(self) -> None:
        manifest = load_cross_machine_playbook_manifest(project_root=PROJECT_ROOT)
        self.assertGreaterEqual(len(manifest.get("no_cad_steps", [])), 4)
        self.assertGreaterEqual(len(manifest.get("user_gate_steps", [])), 3)

    def test_coverage_compare_within_tolerance(self) -> None:
        baseline = {"cad_strength_headline_percent": 9.21, "total_count": 315}
        current = {"cad_strength_headline_percent": 9.21, "total_count": 315}
        recalc = compare_coverage_to_baseline(current_summary=current, baseline_summary=baseline)
        self.assertEqual(recalc["status"], "pass")

    def test_boundary_doc(self) -> None:
        text = (PROJECT_ROOT / VPROOF_73_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "V-PROOF-73",
            "project.cross_machine",
            "user_gate",
            "migration-checklist",
            "不得声称",
            "geometry_verified",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    @mock.patch("core.verification.cross_machine_proof._run_self_check", return_value=0)
    @mock.patch("core.verification.cross_machine_proof._run_git_version", return_value=("git version 2.x", 0))
    @mock.patch("core.verification.cross_machine_proof._cad_mcp_python", return_value=Path(sys.executable))
    @mock.patch("core.verification.cross_machine_proof.run_capability_coverage")
    def test_build_report_pass(
        self,
        mock_coverage: mock.MagicMock,
        *_mocks: object,
    ) -> None:
        baseline = json.loads(
            (PROJECT_ROOT / "examples/capability_proof/cross_machine_coverage_baseline.json").read_text(
                encoding="utf-8"
            )
        )
        mock_coverage.return_value = {
            "status": "pass",
            "summary": baseline["summary"],
        }

        output_dir = artifact_path("vproof_73", "report_fixture")
        report = build_cross_machine_report(project_root=PROJECT_ROOT, output_dir=output_dir)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(validate_cross_machine_report(report, project_root=PROJECT_ROOT), [])
        self.assertEqual(report["user_gate"]["status"], "pending")

    def test_registry_merge(self) -> None:
        registry = json.loads(
            (PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8")
        )
        merge_cross_machine_registry_rows(registry, build_cross_machine_registry_rows(output_root="fixture"))
        self.assertEqual(validate_capability_registry(registry), [])

    def test_sync_dry_run(self) -> None:
        output_dir = artifact_path("vproof_73", "sync_dry_run")
        with (
            mock.patch("core.verification.cross_machine_proof._run_self_check", return_value=0),
            mock.patch("core.verification.cross_machine_proof._run_git_version", return_value=("git", 0)),
            mock.patch("core.verification.cross_machine_proof._cad_mcp_python", return_value=Path(sys.executable)),
            mock.patch("core.verification.cross_machine_proof.run_capability_coverage") as mock_cov,
        ):
            baseline = json.loads(
                (PROJECT_ROOT / "examples/capability_proof/cross_machine_coverage_baseline.json").read_text(
                    encoding="utf-8"
                )
            )
            mock_cov.return_value = {"status": "pass", "summary": baseline["summary"]}
            summary = run_vproof_73_cross_machine_sync(
                project_root=PROJECT_ROOT,
                output_dir=output_dir,
                dry_run=True,
            )
        self.assertEqual(summary["package_id"], VPROOF_73_PACKAGE_ID)
        self.assertEqual(summary["report_status"], "pass")

    def test_live_registry_contract_when_rows_present(self) -> None:
        registry = json.loads(
            (PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8")
        )
        index = {row["capability_id"]: row for row in registry.get("capabilities", [])}
        if CROSS_MACHINE_PLAYBOOK_CAPABILITY_ID not in index:
            self.skipTest("registry rows not synced yet")
        assert_vproof_73_cross_machine_contract(project_root=PROJECT_ROOT)


if __name__ == "__main__":
    unittest.main()
