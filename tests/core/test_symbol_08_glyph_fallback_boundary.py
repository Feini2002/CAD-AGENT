from __future__ import annotations

import unittest

from core.symbol_engine.fallback_policy import FALLBACK_RENDER_TIERS
from core.symbol_engine.symbol_fallback_boundary import (
    GLYPH_FALLBACK_TIERS,
    SYMBOL_08_BOUNDARY_DOC,
    SYMBOL_08_PACKAGE_ID,
    assert_symbol_glyph_fallback_boundary_contract,
    symbol_fallback_boundary_status_summary,
)
from tests.bootstrap import PROJECT_ROOT


class Symbol08GlyphFallbackBoundaryTests(unittest.TestCase):
    def test_symbol_08_boundary_contract(self) -> None:
        assert_symbol_glyph_fallback_boundary_contract(project_root=PROJECT_ROOT)

    def test_glyph_fallback_tiers_match_policy_module(self) -> None:
        self.assertEqual(GLYPH_FALLBACK_TIERS, FALLBACK_RENDER_TIERS[:4])

    def test_status_summary(self) -> None:
        summary = symbol_fallback_boundary_status_summary(project_root=PROJECT_ROOT)
        self.assertTrue(summary["docs_present"])
        self.assertEqual(summary["package_id"], SYMBOL_08_PACKAGE_ID)
        self.assertEqual(summary["benchmark_case_count"], 3)
        self.assertEqual(summary["registry_benchmark_row_count"], 3)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / SYMBOL_08_BOUNDARY_DOC).read_text(encoding="utf-8")
        required_phrases = [
            "SYMBOL-08",
            "symbol_glyph",
            "component_preview",
            "bbox_placeholder",
            "silent_degradation",
            "detect_silent_degradation",
            "V-PROOF-35",
            "geometry_verified",
            "不得声称",
            "dry_run_valid_plan_only",
            "symbol-fallback-policy-01",
            "assert_symbol_glyph_fallback_boundary_contract",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_handoff_indexes_symbol_08(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("SYMBOL-08", handoff)
        self.assertIn("symbol_08_glyph_fallback_boundary.md", handoff)


if __name__ == "__main__":
    unittest.main()
