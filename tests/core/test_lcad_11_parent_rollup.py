from __future__ import annotations

import unittest

from tests.bootstrap import PROJECT_ROOT


class Lcad11ParentRollupTests(unittest.TestCase):
    def test_lcad_11_parent_rollup_document_closes_evidence_trend_package(self) -> None:
        path = PROJECT_ROOT / "docs" / "verification" / "evidence_trend_acceptance.md"

        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")

        required_phrases = [
            "LCAD-11-EVIDENCE-TREND-ROLLUP",
            "LCAD-11.1",
            "LCAD-11.2",
            "LCAD-11.3",
            "LCAD-11.4",
            "LCAD-11.5",
            "evidence_trend.py",
            "local_cad_regression_trend.json",
            "cad_validation_trend_index.json",
            "capability_coverage_trend.json",
            "evidence_trend_boundaries.md",
            "V-PROOF-71",
            "RCAD-27",
            "geometry_verified",
            "不新增真实 CAD 几何结论",
            "deferred_cad_readback_required",
            "negative_guard_verified",
        ]

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_lcad_11_parent_rollup_references_boundary_doc(self) -> None:
        boundaries = (
            PROJECT_ROOT / "docs" / "verification" / "evidence_trend_boundaries.md"
        ).read_text(encoding="utf-8")
        self.assertIn("LCAD-11.1", boundaries)
        self.assertIn("LCAD-11.5", boundaries)

    def test_lcad_11_parent_rollup_is_indexed_from_handoff(self) -> None:
        handoff = (PROJECT_ROOT / "docs" / "handoffs" / "CURSOR_PACKAGE_HANDOFFS.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("LCAD-11", handoff)
        self.assertIn("evidence_trend_acceptance.md", handoff)


if __name__ == "__main__":
    unittest.main()
