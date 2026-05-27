from __future__ import annotations

import unittest

from core.drawing_standard.drawing_standard_boundary import (
    DRAW_01_BOUNDARY_DOC,
    DRAW_01_PACKAGE_ID,
    assert_drawing_standard_boundary_contract,
    drawing_standard_boundary_status_summary,
)
from core.verification.drawing_standard_beta_suite import (
    default_suite_path,
    run_drawing_standard_beta_suite,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Draw01DrawingStandardBoundaryTests(unittest.TestCase):
    def test_draw_01_boundary_contract(self) -> None:
        assert_drawing_standard_boundary_contract(project_root=PROJECT_ROOT)

    def test_draw_01_status_summary(self) -> None:
        summary = drawing_standard_boundary_status_summary(project_root=PROJECT_ROOT)
        self.assertTrue(summary["docs_present"])
        self.assertEqual(summary["package_id"], DRAW_01_PACKAGE_ID)
        self.assertEqual(summary["case_count"], 6)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / DRAW_01_BOUNDARY_DOC).read_text(encoding="utf-8")
        required_phrases = [
            "DRAW-01",
            "preview_only",
            "CODEX_PREVIEW",
            "V-PROOF-44",
            "RCAD-23",
            "geometry_verified",
            "不得声称",
            "assert_drawing_standard_boundary_contract",
            "drawing-standard-beta-04",
            "beta_cad_block_04_boundaries.md",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_draw_01_no_cad_beta_suite(self) -> None:
        result = run_drawing_standard_beta_suite(
            default_suite_path(PROJECT_ROOT),
            output_root=artifact_path("draw_01", "drawing_standard_no_cad"),
        )
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 6, "passed": 6, "failed": 0})
        self.assertTrue(result["evidence_summary"].get("non_cad_only"))


if __name__ == "__main__":
    unittest.main()
