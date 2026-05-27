from __future__ import annotations

import unittest

from core.block_engine.block_matrix_manifest import (
    default_manifest_path,
    run_block_insert_matrix_manifest,
)
from core.block_engine.block_p5_wave import (
    P5_ACCEPTANCE_DOC,
    P5_BOUNDARY_DOCS,
    P5_WAVE_PACKAGE_IDS,
    assert_block_p5_wave_contract,
    block_p5_wave_status_summary,
)
from core.verification.block_alpha_beta_suite import default_suite_path, run_block_alpha_beta_suite
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Rblock08P5WaveParentRollupTests(unittest.TestCase):
    def test_p5_wave_contract(self) -> None:
        assert_block_p5_wave_contract(project_root=PROJECT_ROOT)

    def test_p5_wave_status_summary(self) -> None:
        summary = block_p5_wave_status_summary(project_root=PROJECT_ROOT)
        self.assertTrue(summary["docs_present"])
        self.assertEqual(summary["child_package_count"], 5)
        self.assertEqual(len(summary["package_ids"]), 5)

    def test_acceptance_doc_closes_p5_wave(self) -> None:
        text = (PROJECT_ROOT / P5_ACCEPTANCE_DOC).read_text(encoding="utf-8")
        for short_id in ("RBLOCK-03", "RBLOCK-04", "RBLOCK-05", "RBLOCK-06", "RBLOCK-07", "RBLOCK-08"):
            with self.subTest(short_id=short_id):
                self.assertIn(short_id, text)
        for phrase in (
            "RBLOCK-08",
            "assert_block_p5_wave_contract",
            "block-insert-matrix-01",
            "block.insert_block_alpha.matrix",
            "V-PROOF-40",
            "V-PROOF-41",
            "geometry_verified",
            "不得声称",
            "dry_run_valid_plan_only",
            "BETA-CAD-BLOCK-02",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_all_boundary_docs_exist(self) -> None:
        for rel in P5_BOUNDARY_DOCS:
            with self.subTest(doc=rel):
                self.assertTrue((PROJECT_ROOT / rel).is_file())

    def test_p5_no_cad_beta_and_matrix_rerun(self) -> None:
        beta = run_block_alpha_beta_suite(
            default_suite_path(PROJECT_ROOT),
            output_root=artifact_path("rblock_08", "beta_no_cad"),
        )
        self.assertEqual(beta["status"], "pass")
        self.assertEqual(beta["summary"], {"total": 8, "passed": 8, "failed": 0})

        matrix = run_block_insert_matrix_manifest(
            default_manifest_path(PROJECT_ROOT),
            output_root=artifact_path("rblock_08", "matrix_no_cad"),
        )
        self.assertEqual(matrix["status"], "pass")
        self.assertEqual(matrix["summary"]["passed"], matrix["summary"]["total"])

    def test_handoff_indexes_rblock_08(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("RBLOCK-08", handoff)
        self.assertIn("block_p5_wave_acceptance.md", handoff)


if __name__ == "__main__":
    unittest.main()
