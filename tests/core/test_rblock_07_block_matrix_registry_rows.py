from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.block_engine.block_matrix_manifest import default_manifest_path, run_block_insert_matrix_manifest
from core.block_engine.block_matrix_registry import (
    MATRIX_SUITE_CAPABILITY_ID,
    RBLOCK_07_BOUNDARY_DOC,
    RBLOCK_07_PACKAGE_ID,
    apply_block_matrix_registry_binding,
    assert_block_matrix_registry_contract,
    block_matrix_registry_status_summary,
    build_block_matrix_suite_registry_row,
    build_matrix_registry_binding_requests,
    capability_id_for_matrix_dimension,
    run_block_matrix_registry_no_cad_sync,
    sync_block_matrix_registry_from_manifest,
    MatrixRegistryBindingRequest,
)
from core.drawing_standard.drawing_standard_registry import apply_smoke_registry_evidence_writeback, SmokeEvidenceWritebackRequest
from core.verification.capability_registry import load_capability_registry, validate_capability_registry
from core.verification.evidence_vocabulary import EVIDENCE_DRY_RUN_VALID_PLAN_ONLY
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Rblock07BlockMatrixRegistryRowsTests(unittest.TestCase):
    def test_rblock_07_registry_contract(self) -> None:
        assert_block_matrix_registry_contract(project_root=PROJECT_ROOT)

    def test_suite_row_template_is_smoke(self) -> None:
        row = build_block_matrix_suite_registry_row()
        self.assertEqual(row["capability_id"], MATRIX_SUITE_CAPABILITY_ID)
        self.assertEqual(row["claim_level"], "smoke")

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / RBLOCK_07_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "RBLOCK-07",
            "block-insert-matrix-01",
            "block.insert_block_alpha.matrix",
            "apply_block_matrix_registry_binding",
            "sync_block_matrix_registry_from_manifest",
            "dry_run_valid_plan_only",
            "V-PROOF-40",
            "geometry_verified",
            "不得声称",
            "readback_geometry_verified",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_verified_row_binding_does_not_overwrite_evidence(self) -> None:
        registry = load_capability_registry(
            PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json",
            project_root=PROJECT_ROOT,
        )
        index = {row["capability_id"]: row for row in registry["capabilities"]}
        cap_id = capability_id_for_matrix_dimension("anchor")
        before = json.loads(json.dumps(index[cap_id]["evidence"]))
        report_path = artifact_path("rblock_07", "anchor_dim_pass.json")
        report_path.write_text(json.dumps({"status": "pass", "dimension": "anchor"}), encoding="utf-8")
        rel = str(report_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        result = apply_block_matrix_registry_binding(
            registry,
            MatrixRegistryBindingRequest(capability_id=cap_id, dimension="anchor", report_path=rel),
            project_root=PROJECT_ROOT,
            row_index=index,
            dry_run=False,
        )
        self.assertEqual(result.status, "applied")
        self.assertEqual(index[cap_id]["evidence"], before)
        self.assertTrue(
            any(
                ref.get("source_path", "").endswith("block_insert_matrix_manifest.json")
                for ref in index[cap_id]["source_refs"]
                if isinstance(ref, dict)
            )
        )

    def test_smoke_suite_row_writeback(self) -> None:
        registry = {
            "version": "0.1",
            "registry_id": "test",
            "capabilities": [build_block_matrix_suite_registry_row()],
        }
        report_path = artifact_path("rblock_07", "matrix_suite_pass.json")
        report_path.write_text(json.dumps({"status": "pass", "manifest_id": "block-insert-matrix-01"}), encoding="utf-8")
        rel = str(report_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        result = apply_smoke_registry_evidence_writeback(
            registry,
            SmokeEvidenceWritebackRequest(
                capability_id=MATRIX_SUITE_CAPABILITY_ID,
                report_path=rel,
            ),
            project_root=PROJECT_ROOT,
            dry_run=False,
        )
        self.assertEqual(result.status, "applied")
        row = registry["capabilities"][0]
        self.assertEqual(row["evidence"]["evidence_state"], EVIDENCE_DRY_RUN_VALID_PLAN_ONLY)
        self.assertEqual(validate_capability_registry(registry), [])

    def test_sync_from_matrix_output_five_bindings(self) -> None:
        output_root = artifact_path("rblock_07", "matrix_sync")
        matrix_result = run_block_insert_matrix_manifest(
            default_manifest_path(PROJECT_ROOT),
            output_root=output_root,
        )
        self.assertEqual(matrix_result["status"], "pass")

        registry = json.loads(
            (
                PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json"
            ).read_text(encoding="utf-8")
        )
        results = sync_block_matrix_registry_from_manifest(
            registry,
            matrix_result,
            output_root=output_root,
            project_root=PROJECT_ROOT,
            dry_run=True,
        )
        self.assertEqual(len(results), 5)
        self.assertTrue(all(item.status == "applied" for item in results))

        requests = build_matrix_registry_binding_requests(
            matrix_result,
            output_root=output_root,
            project_root=PROJECT_ROOT,
        )
        self.assertEqual(len(requests), 5)
        self.assertTrue(
            (output_root / "block_insert_matrix_summary.json").is_file()
        )

    def test_no_cad_sync_accepts_relative_output_dir(self) -> None:
        summary = run_block_matrix_registry_no_cad_sync(
            project_root=PROJECT_ROOT,
            output_dir=Path("output/test_artifacts/rblock_07/relative_matrix_sync"),
            dry_run=True,
        )

        self.assertEqual(summary["matrix_status"], "pass")
        self.assertEqual(summary["binding_applied_count"], 5)
        self.assertEqual(summary["output_root"], "output/test_artifacts/rblock_07/relative_matrix_sync")

    def test_status_summary(self) -> None:
        summary = block_matrix_registry_status_summary(project_root=PROJECT_ROOT)
        self.assertEqual(summary["package_id"], RBLOCK_07_PACKAGE_ID)
        self.assertEqual(summary["dimension_binding_count"], 4)

    def test_handoff_indexes_rblock_07(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("RBLOCK-07", handoff)
        self.assertIn("rblock_07_block_matrix_registry_rows.md", handoff)


if __name__ == "__main__":
    unittest.main()
