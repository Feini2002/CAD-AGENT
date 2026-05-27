from __future__ import annotations

import unittest

from core.block_engine.block_alpha_boundary import (
    RBLOCK_03_BOUNDARY_DOC,
    RBLOCK_03_PACKAGE_ID,
    assert_block_alpha_boundary_contract,
    block_alpha_boundary_status_summary,
)
from core.verification.block_alpha_beta_suite import default_suite_path, run_block_alpha_beta_suite
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Rblock03BlockAlphaBoundaryTests(unittest.TestCase):
    def test_rblock_03_boundary_contract(self) -> None:
        assert_block_alpha_boundary_contract(project_root=PROJECT_ROOT)

    def test_status_summary(self) -> None:
        summary = block_alpha_boundary_status_summary(project_root=PROJECT_ROOT)
        self.assertTrue(summary["docs_present"])
        self.assertEqual(summary["package_id"], RBLOCK_03_PACKAGE_ID)
        self.assertEqual(summary["case_count"], 8)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / RBLOCK_03_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "RBLOCK-03",
            "controlled-test-block-001",
            "CODEX_TEST_BLOCK_001",
            "block-alpha-beta-01",
            "CODEX_PREVIEW",
            "V-PROOF-40",
            "geometry_verified",
            "不得声称",
            "assert_block_alpha_boundary_contract",
            "dry_run_valid_plan_only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_cad_beta_suite_eight_cases(self) -> None:
        result = run_block_alpha_beta_suite(
            default_suite_path(PROJECT_ROOT),
            output_root=artifact_path("rblock_03", "beta_no_cad"),
        )
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 8, "passed": 8, "failed": 0})

    def test_handoff_indexes_rblock_03(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("RBLOCK-03", handoff)
        self.assertIn("rblock_03_block_alpha_boundary.md", handoff)


if __name__ == "__main__":
    unittest.main()
