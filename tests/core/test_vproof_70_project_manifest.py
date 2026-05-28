from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.verification.capability_registry import validate_capability_registry
from core.verification.project_regression_manifest import (
    REGRESSION_MANIFEST_CAPABILITY_ID,
    VPROOF_70_BOUNDARY_DOC,
    VPROOF_70_PACKAGE_ID,
    assert_project_regression_manifest_consistency,
    assert_vproof_70_project_manifest_contract,
    build_project_regression_registry_rows,
    capability_id_for_project_regression_sample,
    load_project_regression_manifest,
    merge_project_regression_registry_rows,
    run_vproof_70_project_manifest_sync,
    submittable_samples,
    validate_project_regression_manifest,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Vproof70ProjectManifestTests(unittest.TestCase):
    def test_manifest_schema_and_submittable_count(self) -> None:
        manifest = load_project_regression_manifest(project_root=PROJECT_ROOT)
        errors = validate_project_regression_manifest(manifest, project_root=PROJECT_ROOT)
        self.assertEqual(errors, [])
        self.assertGreaterEqual(len(submittable_samples(manifest)), 2)

    def test_consistency_with_projects_and_rollup(self) -> None:
        manifest = load_project_regression_manifest(project_root=PROJECT_ROOT)
        assert_project_regression_manifest_consistency(manifest, project_root=PROJECT_ROOT)

    def test_build_registry_rows(self) -> None:
        manifest = load_project_regression_manifest(project_root=PROJECT_ROOT)
        rows = build_project_regression_registry_rows(
            project_root=PROJECT_ROOT,
            manifest=manifest,
            output_root="output/validation_runs/vproof-70-project-manifest",
        )
        self.assertEqual(len(rows), 1 + len(manifest["samples"]))
        self.assertEqual(rows[0]["capability_id"], REGRESSION_MANIFEST_CAPABILITY_ID)
        sample_row_ids = {
            capability_id_for_project_regression_sample(str(row["sample_id"]))
            for row in manifest["samples"]
            if isinstance(row, dict)
        }
        self.assertIn("project.regression.sample.sample_blank_shell", sample_row_ids)
        self.assertIn("project.regression.sample.sample_blank_shell_too_small", sample_row_ids)
        for row in submittable_samples(manifest):
            self.assertIn(
                capability_id_for_project_regression_sample(str(row["sample_id"])),
                sample_row_ids,
            )

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / VPROOF_70_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "V-PROOF-70",
            "project.regression.manifest",
            "PROJ-02",
            "claim_level",
            "smoke",
            "不得声称",
            "geometry_verified",
            "submittable",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_merge_and_sync_dry_run(self) -> None:
        output_dir = artifact_path("vproof_70", "sync_dry_run")
        summary = run_vproof_70_project_manifest_sync(
            project_root=PROJECT_ROOT,
            output_dir=output_dir,
            dry_run=True,
        )
        self.assertEqual(summary["package_id"], VPROOF_70_PACKAGE_ID)
        self.assertEqual(summary["audit_status"], "pass")
        self.assertGreaterEqual(summary["submittable_count"], 2)
        self.assertEqual(summary["writeback_rejected_count"], 0)
        audit_path = output_dir / "project_regression_manifest_audit.json"
        self.assertTrue(audit_path.is_file())

    def test_registry_merge_validates(self) -> None:
        manifest = load_project_regression_manifest(project_root=PROJECT_ROOT)
        registry = json.loads(
            (PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8")
        )
        rows = build_project_regression_registry_rows(
            project_root=PROJECT_ROOT,
            manifest=manifest,
            output_root="output/validation_runs/vproof-70-fixture",
        )
        merge_project_regression_registry_rows(registry, rows)
        self.assertEqual(validate_capability_registry(registry), [])

    def test_live_registry_contract_when_rows_present(self) -> None:
        registry_path = PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        index = {row["capability_id"]: row for row in registry.get("capabilities", [])}
        if REGRESSION_MANIFEST_CAPABILITY_ID not in index:
            self.skipTest("registry rows not synced yet")
        assert_vproof_70_project_manifest_contract(project_root=PROJECT_ROOT)


if __name__ == "__main__":
    unittest.main()
