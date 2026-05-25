from __future__ import annotations

import unittest


from tests.bootstrap import PROJECT_ROOT

from core.proposal_engine.proposal_comparison import compare_layout_candidates


class ProposalComparisonTests(unittest.TestCase):
    def test_layout_candidate_comparison_ranks_and_explains_tradeoffs(self) -> None:
        layout_proposal = {
            "layout_id": "layout-test",
            "candidates": [
                {
                    "candidate_id": "candidate-tight",
                    "score": 0.42,
                    "checks": [{"name": "clearance", "status": "fail"}],
                },
                {
                    "candidate_id": "candidate-clear",
                    "score": 0.91,
                    "checks": [{"name": "clearance", "status": "pass"}],
                },
            ],
        }

        comparison = compare_layout_candidates(layout_proposal)

        self.assertEqual(comparison["status"], "ok")
        self.assertEqual(comparison["recommendation_id"], "candidate-clear")
        self.assertEqual([item["candidate_id"] for item in comparison["ranked_candidates"]], ["candidate-clear", "candidate-tight"])
        self.assertEqual(comparison["ranked_candidates"][1]["failed_checks"], ["clearance"])


if __name__ == "__main__":
    unittest.main()
