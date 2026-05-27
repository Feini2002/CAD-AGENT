from __future__ import annotations

import unittest

from tests.bootstrap import PROJECT_ROOT


class EvidenceTrendBoundariesDocTests(unittest.TestCase):
    def test_lcad_11_5_boundary_document_exists_and_states_claim_limits(self) -> None:
        path = PROJECT_ROOT / "docs" / "verification" / "evidence_trend_boundaries.md"

        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")

        required_phrases = [
            "LCAD-11.5",
            "LCAD-11.1",
            "LCAD-11.2",
            "LCAD-11.3",
            "LCAD-11.4",
            "local_cad_regression_trend.json",
            "cad_validation_trend_index.json",
            "capability_coverage_trend.json",
            "snapshot.metrics",
            "cad_proof_coverage_rate",
            "geometry_verified",
            "created-handle readback",
            "不得声称",
            "不能替代",
            "V-PROOF-71",
            "output/validation_runs/lcad-11-4-coverage-trend-hook/evidence_trend/capability_coverage_trend.json",
        ]

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
