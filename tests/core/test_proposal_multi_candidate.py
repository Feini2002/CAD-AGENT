from __future__ import annotations

import json
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.proposal_engine.design_proposal import create_design_proposal
from core.proposal_engine.proposal_comparison import build_blank_shell_comparison_detail, compare_layout_candidates
from core.workflows.blank_shell_pipeline import build_blank_shell_candidate_sets
from core.layout_engine.path_generation import generate_circulation_candidates
from core.project_model.project_builder import build_project_model
from core.drawing_analysis.shell_loader import load_manual_shell
from core.block_engine.block_library import load_block_library
from core.proposal_engine.proposal_to_plan import proposal_to_plans
from core.schemas.validator import validate_value


def load_example(path: str) -> dict[str, object]:
    return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))


def multi_layout() -> dict[str, object]:
    return {
        "version": "0.1",
        "layout_id": "layout-multi",
        "project_id": "project-minimal-cabinet",
        "candidates": [
            {
                "candidate_id": "candidate-a",
                "score": 0.5,
                "placements": [{"object_id": "object-cabinet-1800", "base_point": [0, 0, 0]}],
                "checks": [{"name": "clearance", "status": "fail"}],
            },
            {
                "candidate_id": "candidate-b",
                "score": 0.9,
                "placements": [{"object_id": "object-cabinet-1800", "base_point": [1000, 0, 0]}],
                "checks": [{"name": "clearance", "status": "pass"}],
            },
        ],
    }


class ProposalMultiCandidateTests(unittest.TestCase):
    def test_create_design_proposal_wraps_multiple_candidates(self) -> None:
        proposal = create_design_proposal(
            brief=load_example("examples/design_briefs/minimal_cabinet_brief.json"),
            project_model=load_example("examples/project_models/minimal_cabinet_project.json"),
            object_spec=load_example("examples/object_specs/minimal_cabinet_object.json"),
            layout_proposal=multi_layout(),
        )

        self.assertEqual(len(proposal["candidates"]), 2)
        self.assertEqual(proposal["candidates"][0]["candidate_id"], "candidate-a")
        for candidate in proposal["candidates"]:
            self.assertIn("summary", candidate)
            self.assertIn("strengths", candidate)
            self.assertIn("risks", candidate)
            self.assertIn("failed_checks", candidate)
            self.assertIn("applicable_scenarios", candidate)
            self.assertIn("confirmation_questions", candidate)
        schema = load_example("core/schemas/design_proposal.schema.json")
        self.assertEqual(validate_value(proposal, schema), [])

    def test_proposal_to_plans_uses_confirmed_candidate_id(self) -> None:
        proposal = load_example("examples/design_proposals/minimal_cabinet_proposal.json")
        proposal["confirmed_candidate_id"] = "candidate-b"
        object_spec = load_example("examples/object_specs/minimal_cabinet_object.json")

        plans = proposal_to_plans(proposal, object_spec=object_spec, layout_proposal=multi_layout(), confirmed=True)

        self.assertEqual(plans[0]["placement"]["base_point"], [1000, 0, 0])

    def test_blank_shell_comparison_detail_is_structured_and_assertable(self) -> None:
        workflow = load_example("examples/workflows/blank_shell_layout_loop.json")
        inputs = workflow["inputs"]
        brief = load_example(inputs["design_brief"])
        drawing = load_example(inputs["drawing_model"])
        shell = load_manual_shell(PROJECT_ROOT / inputs["shell_model"])
        project_model = build_project_model(brief, drawing, shell_model=shell).project_model
        circulation_candidates = generate_circulation_candidates(project_model, {})
        candidate_sets, *_ = build_blank_shell_candidate_sets(
            shell=shell,
            circulation_candidates=circulation_candidates,
            object_types=workflow.get("object_types", []),
            block_library=load_block_library(),
            placement_preferences={},
        )
        layout = {
            "version": "0.1",
            "layout_id": "layout-test",
            "project_id": project_model["project_id"],
            "candidates": [
                {
                    "candidate_id": "candidate-blank-shell-zone-placement",
                    "score": 1.0,
                    "placements": [],
                    "checks": [{"name": "placement:desk", "status": "pass"}],
                }
            ],
        }
        proposal = create_design_proposal(
            brief=brief,
            project_model=project_model,
            object_spec=load_example("examples/object_specs/minimal_cabinet_object.json"),
            layout_proposal=layout,
            candidate_sets=candidate_sets,
            object_types=workflow.get("object_types", []),
        )
        detail = proposal["comparison_detail"]
        self.assertGreaterEqual(detail["metrics"]["circulation_branch_count"], 2)
        self.assertGreaterEqual(detail["metrics"]["zone_placement_candidate_count"], 2)
        self.assertIn("object_coverage_rate", detail["metrics"])
        self.assertIn("failed_reason_distribution", detail["metrics"])
        self.assertIn(detail["circulation_continuity"]["continuity"], {"pass", "degraded", "blocked", "unknown"})
        self.assertGreaterEqual(len(detail["ranking_reasons"]), 2)
        self.assertEqual(proposal["comparison_summary"], detail["narrative"])
        self.assertFalse(proposal["needs_confirmation"])
        self.assertGreaterEqual(len(proposal["candidates"]), 2)

    def test_comparison_records_scene_weight_source(self) -> None:
        comparison = compare_layout_candidates(
            multi_layout(),
            preferences={
                "candidate_weights": {"candidate-a": 0.6},
                "weight_source": "agents/test/preferences.json",
            },
        )

        self.assertEqual(comparison["recommendation_id"], "candidate-a")
        self.assertEqual(comparison["ranked_candidates"][0]["weight_source"], "agents/test/preferences.json")
        self.assertGreater(comparison["ranked_candidates"][0]["weighted_score"], comparison["ranked_candidates"][1]["weighted_score"])


if __name__ == "__main__":
    unittest.main()
