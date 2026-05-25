from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.proposal_engine.proposal_to_plan import proposal_to_plans


def load_example(path: str) -> dict[str, object]:
    return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))


class ProposalEngineTests(unittest.TestCase):
    def test_proposal_to_plans_is_pure_and_returns_plan_list(self) -> None:
        proposal = load_example("examples/design_proposals/minimal_cabinet_proposal.json")
        object_spec = load_example("examples/object_specs/minimal_cabinet_object.json")
        layout = load_example("examples/layout_proposals/minimal_cabinet_layout.json")
        original_next_plans = list(proposal["next_cad_plans"])

        plans = proposal_to_plans(proposal, object_spec=object_spec, layout_proposal=layout)

        self.assertEqual(len(plans), 1)
        self.assertEqual(proposal["next_cad_plans"], original_next_plans)

    def test_proposal_to_plans_blocks_unconfirmed_proposal(self) -> None:
        proposal = load_example("examples/design_proposals/minimal_cabinet_proposal.json")
        object_spec = load_example("examples/object_specs/minimal_cabinet_object.json")
        layout = load_example("examples/layout_proposals/minimal_cabinet_layout.json")
        proposal["needs_confirmation"] = True

        with self.assertRaisesRegex(ValueError, "needs confirmation"):
            proposal_to_plans(proposal, object_spec=object_spec, layout_proposal=layout)

    def test_proposal_to_plans_rejects_mismatched_layout_placement(self) -> None:
        proposal = load_example("examples/design_proposals/minimal_cabinet_proposal.json")
        object_spec = load_example("examples/object_specs/minimal_cabinet_object.json")
        layout = load_example("examples/layout_proposals/minimal_cabinet_layout.json")
        layout["candidates"][0]["placements"][0]["object_id"] = "object-from-another-layout"

        with self.assertRaisesRegex(ValueError, "No placement found"):
            proposal_to_plans(proposal, object_spec=object_spec, layout_proposal=layout)


if __name__ == "__main__":
    unittest.main()
