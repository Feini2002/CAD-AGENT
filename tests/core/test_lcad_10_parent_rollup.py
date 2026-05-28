from __future__ import annotations

import unittest

from tests.bootstrap import PROJECT_ROOT


class Lcad10ParentRollupTests(unittest.TestCase):
    def test_lcad_10_parent_rollup_document_closes_negative_safety_package(self) -> None:
        path = PROJECT_ROOT / "docs" / "verification" / "negative_cad_safety_acceptance.md"

        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")

        required_phrases = [
            "LCAD-10-NEGATIVE-SAFETY",
            "LCAD-10.1",
            "LCAD-10.2",
            "LCAD-10.3",
            "LCAD-10.4",
            "LCAD-10.5",
            "run_negative_cad_plan_suite.py",
            "run_write_guard_cad_runner.py",
            "run_negative_cad_runner.py",
            "negative_cad_safety_boundaries.md",
            "negative_guard_verified",
            "created_handles=[]",
            "RCAD-20",
            "V-PROOF-50",
            "V-PROOF-51",
            "不新增真实 CAD 几何结论",
            "不计入几何证明",
            "LCAD-11.1",
            "父包已于 2026-05-28 收口",
        ]

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_lcad_10_parent_rollup_is_indexed_from_handoff(self) -> None:
        handoff = (PROJECT_ROOT / "docs" / "handoffs" / "CURSOR_PACKAGE_HANDOFFS.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("LCAD-10.5", handoff)
        self.assertIn("negative_cad_safety_acceptance.md", handoff)


if __name__ == "__main__":
    unittest.main()
