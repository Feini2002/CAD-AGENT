from __future__ import annotations

import unittest

from tests.bootstrap import PROJECT_ROOT


class NegativeCadSafetyBoundariesDocTests(unittest.TestCase):
    def test_lcad_10_4_boundary_document_exists_and_states_claim_limits(self) -> None:
        path = PROJECT_ROOT / "docs" / "verification" / "negative_cad_safety_boundaries.md"

        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")

        required_phrases = [
            "LCAD-10.4",
            "LCAD-10.1",
            "LCAD-10.2",
            "LCAD-10.3",
            "failure_category",
            "negative_guard_verified",
            "created_handles=[]",
            "CODEX_PREVIEW",
            "RCAD-20",
            "V-PROOF-50",
            "V-PROOF-51",
            "geometry_verified",
            "不计入几何证明",
            "不得声称",
            "output/validation_runs/neg-cad-proof-sync/negative-runner-fake-final/negative_cad_runner_report.json",
        ]

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
