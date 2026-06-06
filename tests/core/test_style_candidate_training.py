from __future__ import annotations

import unittest

from core.training.style_candidate_training import run_style_candidate_training
from core.verification.fake_cad_driver import FakeCadDriver
from tests.helpers import temporary_artifact_dir


class StyleCandidateTrainingTests(unittest.TestCase):
    def test_training_generates_executes_and_reviews_new_abc_dimension_style_candidates(self) -> None:
        with temporary_artifact_dir("style_candidate_training") as root:
            report = run_style_candidate_training(
                driver=FakeCadDriver(),
                output_dir=root,
                generated_at="2026-06-05T00:00:00Z",
            )

            self.assertEqual(report["status"], "needs_user_choice")
            self.assertEqual(report["scope"]["mode"], "focused")
            self.assertEqual(report["styleCandidateCount"], 3)
            self.assertEqual(report["styleCandidateIds"], ["A", "B", "C"])
            self.assertEqual(report["legacyStyleReuse"]["reusedLegacyStyleCount"], 0)
            self.assertEqual(report["execution"]["status"], "executed")
            self.assertEqual(report["readback"]["status"], "pass")
            self.assertEqual(report["designReview"]["status"], "pass")
            self.assertTrue(report["designReview"]["needsUserChoice"])
            self.assertEqual(report["askUserToChoose"]["options"], ["A", "B", "C"])
            self.assertFalse(report["safety"]["savedCurrentDwg"])
            self.assertTrue((root / "style_candidates.json").is_file())
            self.assertTrue((root / "style_candidate_training_report.json").is_file())


if __name__ == "__main__":
    unittest.main()
