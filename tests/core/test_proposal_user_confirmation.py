from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.proposal_engine.design_proposal import create_design_proposal
from core.proposal_engine.proposal_to_plan import proposal_to_plans
from core.proposal_engine.user_confirmation import (
    apply_user_confirmation,
    build_user_confirmation,
    confirmation_round_trip,
    load_user_confirmation,
    save_user_confirmation,
    validate_confirmation_against_proposal,
    validate_confirmation_document,
)
from core.schemas.validator import validate_json, validate_value
from tests.bootstrap import PROJECT_ROOT
from tests.core.test_proposal_multi_candidate import load_example, multi_layout


class ProposalUserConfirmationTests(unittest.TestCase):
    def test_beta_proposal_03_example_validates_against_schema(self) -> None:
        for rel in (
            "examples/confirmations/minimal_cabinet_confirmation.json",
            "examples/confirmations/blank_shell_retail_confirmation.json",
        ):
            errors = validate_json(
                PROJECT_ROOT / "core/schemas/proposal_user_confirmation.schema.json",
                PROJECT_ROOT / rel,
            )
            self.assertEqual(errors, [], rel)

    def test_beta_proposal_03_round_trip_updates_proposal(self) -> None:
        proposal = create_design_proposal(
            brief=load_example("examples/design_briefs/minimal_cabinet_brief.json"),
            project_model=load_example("examples/project_models/minimal_cabinet_project.json"),
            object_spec=load_example("examples/object_specs/minimal_cabinet_object.json"),
            layout_proposal=multi_layout(),
        )
        proposal["needs_confirmation"] = True

        confirmation, updated = confirmation_round_trip(
            proposal,
            selected_candidate_id="candidate-b",
            rejected_candidates=[
                {
                    "candidate_id": "candidate-a",
                    "reason_code": "clearance_conflict",
                    "reason_note": "Clearance fail on candidate-a.",
                }
            ],
        )

        self.assertEqual(confirmation["selected_candidate_id"], "candidate-b")
        self.assertEqual(updated["confirmed_candidate_id"], "candidate-b")
        self.assertFalse(updated["needs_confirmation"])
        self.assertIn("user_confirmation", updated)
        self.assertEqual(validate_confirmation_against_proposal(confirmation, proposal), [])

    def test_apply_confirmation_enables_proposal_to_plans(self) -> None:
        proposal = load_example("examples/design_proposals/minimal_cabinet_proposal.json")
        proposal["needs_confirmation"] = True
        confirmation = load_example("examples/confirmations/minimal_cabinet_confirmation.json")
        updated = apply_user_confirmation(proposal, confirmation)

        object_spec = load_example("examples/object_specs/minimal_cabinet_object.json")
        layout = load_example("examples/layout_proposals/minimal_cabinet_layout.json")
        plans = proposal_to_plans(updated, object_spec=object_spec, layout_proposal=layout, confirmed=True)
        self.assertEqual(len(plans), 1)

    def test_reject_all_keeps_needs_confirmation(self) -> None:
        proposal = create_design_proposal(
            brief=load_example("examples/design_briefs/minimal_cabinet_brief.json"),
            project_model=load_example("examples/project_models/minimal_cabinet_project.json"),
            object_spec=load_example("examples/object_specs/minimal_cabinet_object.json"),
            layout_proposal=multi_layout(),
        )
        confirmation = build_user_confirmation(
            proposal=proposal,
            selected_candidate_id="",
            action="reject_all",
            rejected_candidates=[
                {"candidate_id": "candidate-a", "reason_code": "user_rejected"},
                {"candidate_id": "candidate-b", "reason_code": "user_rejected"},
            ],
        )
        updated = apply_user_confirmation(proposal, confirmation)
        self.assertEqual(updated["confirmed_candidate_id"], "")
        self.assertTrue(updated["needs_confirmation"])

    def test_save_and_load_round_trip_file(self) -> None:
        confirmation = load_example("examples/confirmations/blank_shell_retail_confirmation.json")
        path = PROJECT_ROOT / "output/test_artifacts/proposal_confirmations/beta_proposal_03_roundtrip.json"
        save_user_confirmation(path, confirmation)
        loaded = load_user_confirmation(path)
        self.assertEqual(loaded["confirmation_id"], confirmation["confirmation_id"])
        schema = json.loads(
            (PROJECT_ROOT / "core/schemas/proposal_user_confirmation.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(validate_value(loaded, schema), [])

    def test_invalid_fixture_fails_schema_or_semantics(self) -> None:
        invalid = json.loads(
            (
                PROJECT_ROOT / "tests/fixtures/invalid_models/proposal_user_confirmation.invalid.json"
            ).read_text(encoding="utf-8")
        )
        errors = validate_confirmation_document(invalid)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
