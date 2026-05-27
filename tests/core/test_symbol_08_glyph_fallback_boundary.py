from __future__ import annotations

import unittest

from core.symbol_engine.fallback_policy import FALLBACK_RENDER_TIERS
from core.symbol_engine.symbol_fallback_boundary import (
    GLYPH_FALLBACK_TIERS,
    SYMBOL_08_BOUNDARY_DOC,
    SYMBOL_08_PACKAGE_ID,
    VPROOF_35_PACKAGE_ID,
    VPROOF_35_REGISTRY_TIER_IDS,
    assert_symbol_glyph_fallback_boundary_contract,
    symbol_fallback_boundary_status_summary,
)
from core.verification.capability_registry import index_capability_rows, load_capability_registry
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
        self.assertEqual(summary["vproof_35_package_id"], VPROOF_35_PACKAGE_ID)
        self.assertEqual(summary["vproof_35_registry_tier_count"], 5)

    def test_vproof_35_fallback_tier_rows_are_registered_without_geometry_claims(self) -> None:
        registry = load_capability_registry(
            PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json",
            project_root=PROJECT_ROOT,
        )
        index = index_capability_rows(registry)
        self.assertEqual(len(VPROOF_35_REGISTRY_TIER_IDS), 5)
        for capability_id in VPROOF_35_REGISTRY_TIER_IDS:
            with self.subTest(capability_id=capability_id):
                row = index[capability_id]
                self.assertIn("V-PROOF-35", row.get("tags", []))
                self.assertNotIn(row["claim_level"], {"verified", "showcase"})
                self.assertEqual(row["evidence"]["geometry_accuracy"], "not_verified_without_cad_readback")

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
