from __future__ import annotations

import json
import unittest

from core.proposal_engine.candidate_scoring import (
    build_layout_ranking_reasons,
    build_score_breakdown,
    enrich_ranked_layout_candidate,
    validate_candidate_scoring,
)
from core.proposal_engine.design_proposal import create_design_proposal
from core.proposal_engine.proposal_comparison import compare_layout_candidates
from core.schemas.validator import validate_value
from tests.bootstrap import PROJECT_ROOT


def load_example(path: str) -> dict[str, object]:
    return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))


class ProposalCandidateScoringTests(unittest.TestCase):
    def test_beta_proposal_01_layout_comparison_exposes_score_and_reasons(self) -> None:
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
        comparison = compare_layout_candidates(
            layout_proposal,
            preferences={
                "candidate_weights": {"candidate-tight": 0.5},
                "weight_source": "agents/test/preferences.json",
            },
        )
        top = comparison["ranked_candidates"][0]
        self.assertEqual(top["candidate_id"], "candidate-tight")
        self.assertIn("score_breakdown", top)
        self.assertEqual(top["score_breakdown"]["rank"], 1)
        self.assertGreater(top["score_breakdown"]["components"]["preference_boost"], 0)
        reason_codes = {reason["code"] for reason in top["ranking_reasons"]}
        self.assertIn("highest_weighted_score", reason_codes)
        self.assertIn("scene_preference_boost", reason_codes)
        self.assertEqual(validate_candidate_scoring(top), [])

    def test_beta_proposal_01_design_proposal_candidates_assertable(self) -> None:
        layout = {
            "version": "0.1",
            "layout_id": "layout-multi",
            "project_id": "project-minimal-cabinet",
            "candidates": [
                {
                    "candidate_id": "candidate-a",
                    "score": 0.5,
                    "placements": [],
                    "checks": [{"name": "clearance", "status": "fail"}],
                },
                {
                    "candidate_id": "candidate-b",
                    "score": 0.9,
                    "placements": [],
                    "checks": [{"name": "clearance", "status": "pass"}],
                },
            ],
        }
        proposal = create_design_proposal(
            brief=load_example("examples/design_briefs/minimal_cabinet_brief.json"),
            project_model=load_example("examples/project_models/minimal_cabinet_project.json"),
            object_spec=load_example("examples/object_specs/minimal_cabinet_object.json"),
            layout_proposal=layout,
        )
        schema = load_example("core/schemas/design_proposal.schema.json")
        self.assertEqual(validate_value(proposal, schema), [])

        winner = next(item for item in proposal["candidates"] if item["candidate_id"] == "candidate-b")
        self.assertEqual(winner["score_breakdown"]["rank"], 1)
        reason_codes = {reason["code"] for reason in winner["ranking_reasons"]}
        self.assertIn("highest_weighted_score", reason_codes)
        self.assertIn("no_failed_checks", reason_codes)

        loser = next(item for item in proposal["candidates"] if item["candidate_id"] == "candidate-a")
        loser_codes = {reason["code"] for reason in loser["ranking_reasons"]}
        self.assertIn("failed_checks_present", loser_codes)

    def test_enrich_ranked_layout_candidate_round_trip(self) -> None:
        enriched = enrich_ranked_layout_candidate(
            {
                "rank": 2,
                "candidate_id": "candidate-x",
                "score": 0.6,
                "scene_weight": 0.0,
                "weighted_score": 0.6,
                "weight_source": "default",
                "failed_checks": ["door_clearance"],
            }
        )
        breakdown = build_score_breakdown(
            rank=2,
            base_score=0.6,
            scene_weight=0.0,
            weighted_score=0.6,
            weight_source="default",
            check_penalty=-0.35,
        )
        self.assertEqual(enriched["score_breakdown"]["components"], breakdown["components"])
        reasons = build_layout_ranking_reasons(enriched)
        self.assertTrue(any(item["code"] == "failed_checks_present" for item in reasons))


if __name__ == "__main__":
    unittest.main()
