from __future__ import annotations

import unittest

from core.block_engine.block_matrix_manifest import (
    BLOCK_MATRIX_DIMENSIONS,
    RBLOCK_04_REGISTRY_CAPABILITY_IDS,
    assert_block_matrix_manifest_contract,
    block_matrix_manifest_status_summary,
    default_manifest_path,
    load_block_insert_matrix_manifest,
    run_block_insert_matrix_manifest,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Rblock04BlockMatrixManifestTests(unittest.TestCase):
    def test_rblock_04_matrix_contract(self) -> None:
        assert_block_matrix_manifest_contract(project_root=PROJECT_ROOT)

    def test_manifest_has_four_dimensions(self) -> None:
        manifest = load_block_insert_matrix_manifest(default_manifest_path(PROJECT_ROOT))
        self.assertEqual(manifest["manifest_id"], "block-insert-matrix-01")
        self.assertEqual(set(manifest["dimensions"].keys()), set(BLOCK_MATRIX_DIMENSIONS))

    def test_registry_bindings_documented(self) -> None:
        manifest = load_block_insert_matrix_manifest(default_manifest_path(PROJECT_ROOT))
        for dimension in BLOCK_MATRIX_DIMENSIONS:
            cap_id = manifest["dimensions"][dimension]["registry_capability_id"]
            self.assertIn(cap_id, RBLOCK_04_REGISTRY_CAPABILITY_IDS)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (
            PROJECT_ROOT / "docs/verification/rblock_04_block_matrix_manifest.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "RBLOCK-04",
            "block-insert-matrix-01",
            "block.insert_block_alpha.anchor",
            "insert_block_alpha_attribute_probe",
            "V-PROOF-40",
            "geometry_verified",
            "不得声称",
            "assert_block_matrix_manifest_contract",
            "dry_run_valid_plan_only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_cad_matrix_runner(self) -> None:
        result = run_block_insert_matrix_manifest(
            default_manifest_path(PROJECT_ROOT),
            output_root=artifact_path("rblock_04", "matrix_no_cad"),
        )
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["dimension_summary"]["anchor"]["passed"], 3)
        self.assertEqual(result["dimension_summary"]["rotation"]["passed"], 2)
        self.assertEqual(result["dimension_summary"]["scale"]["passed"], 2)
        self.assertEqual(result["dimension_summary"]["attribute"]["passed"], 1)

    def test_status_summary(self) -> None:
        summary = block_matrix_manifest_status_summary(project_root=PROJECT_ROOT)
        self.assertEqual(summary["dimension_count"], 4)
        self.assertEqual(summary["registry_binding_count"], 4)

    def test_handoff_indexes_rblock_04(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("RBLOCK-04", handoff)
        self.assertIn("rblock_04_block_matrix_manifest.md", handoff)


if __name__ == "__main__":
    unittest.main()
