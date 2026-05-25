from __future__ import annotations

import json
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.block_engine.block_library import fallback_object_spec, load_block_library, select_blocks
from core.layout_engine.basic_layout import bboxes_overlap, create_single_object_layout
from core.object_engine.parametric_objects import create_object_spec, object_spec_to_cad_plan
from core.plan_engine.validate_plan import validate_plan
from core.proposal_engine.design_proposal import create_design_proposal, proposal_to_plan
from core.schemas.validator import validate_value
from core.style_engine.style_profile import UnknownStyleError, load_style_profile


def json_load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


class ObjectStyleBlockLayoutProposalTests(unittest.TestCase):
    def test_object_spec_converts_to_valid_preview_cad_plan(self) -> None:
        spec = create_object_spec(
            "cabinet",
            name="European Preview Cabinet",
            width=1800,
            depth=600,
            height=2400,
            style_profile_id="style-european",
        )

        plan = object_spec_to_cad_plan(spec)

        self.assertEqual(spec["size"]["height"], 2400)
        schema = json_load(PROJECT_ROOT / "core" / "schemas" / "object_spec.schema.json")
        self.assertEqual(validate_value(spec, schema), [])
        self.assertEqual(plan["drawing"]["layer"], "CODEX_PREVIEW")
        self.assertEqual(validate_plan(plan), [])

    def test_style_profiles_load_and_unknown_style_is_explicit(self) -> None:
        profile = load_style_profile("european")

        self.assertEqual(profile["style_id"], "style-european")
        with self.assertRaises(UnknownStyleError):
            load_style_profile("unknown-style")

    def test_block_selection_and_fallback_object(self) -> None:
        library = load_block_library()

        blocks = select_blocks(library, category="cabinet", domain="retail", max_width=2000)
        fallback = fallback_object_spec("cabinet", width=1500, depth=500)

        self.assertEqual(blocks[0]["block_id"], "block-cabinet-1800")
        self.assertEqual(fallback["type"], "cabinet")

    def test_basic_layout_checks_boundary_and_overlap(self) -> None:
        project_model = {
            "version": "0.1",
            "project_id": "project-test",
            "domain": "generic",
            "units": "mm",
            "brief_id": "brief-test",
            "spaces": [
                {
                    "space_id": "space-1",
                    "name": "Space",
                    "boundary": {"min": [0, 0], "max": [3000, 1800]},
                }
            ],
            "requirements": [],
            "pending_questions": [],
        }
        spec = create_object_spec("table", width=1200, depth=700)

        layout = create_single_object_layout(project_model=project_model, object_spec=spec)

        schema = json_load(PROJECT_ROOT / "core" / "schemas" / "layout_proposal.schema.json")
        self.assertEqual(validate_value(layout, schema), [])
        self.assertEqual(layout["candidates"][0]["checks"][0]["status"], "pass")
        first = {"min": [0, 0], "max": [500, 500]}
        second = {"min": [400, 400], "max": [900, 900]}
        self.assertTrue(bboxes_overlap(first, second))

    def test_design_proposal_separates_evidence_and_converts_to_plan(self) -> None:
        brief = {
            "brief_id": "brief-test",
            "user_request": "Draw a cabinet preview.",
            "needs_confirmation": False,
        }
        project_model = {
            "version": "0.1",
            "project_id": "project-test",
            "domain": "generic",
            "units": "mm",
            "brief_id": "brief-test",
            "spaces": [
                {
                    "space_id": "space-1",
                    "name": "Space",
                    "boundary": {"min": [0, 0], "max": [3000, 1800]},
                }
            ],
            "requirements": [],
            "pending_questions": [],
        }
        spec = create_object_spec("cabinet", width=1800, depth=600)
        layout = {
            "candidates": [
                {
                    "candidate_id": "candidate-001",
                    "score": 0.9,
                    "placements": [{"object_id": spec["object_id"], "base_point": [0, 0, 0]}],
                    "checks": [{"name": "inside_boundary", "status": "pass"}],
                }
            ]
        }

        proposal = create_design_proposal(
            brief=brief,
            project_model=project_model,
            object_spec=spec,
            layout_proposal=layout,
        )
        plan = proposal_to_plan(proposal, object_spec=spec, layout_proposal=layout)

        self.assertIn("from_user", proposal["evidence"])
        self.assertIn("from_library", proposal["evidence"])
        schema = json_load(PROJECT_ROOT / "core" / "schemas" / "design_proposal.schema.json")
        self.assertEqual(validate_value(proposal, schema), [])
        self.assertFalse(proposal["needs_confirmation"])
        self.assertEqual(validate_plan(plan), [])

    def test_design_proposal_requires_confirmation_before_failed_layout_becomes_plan(self) -> None:
        brief = {
            "brief_id": "brief-test",
            "user_request": "Draw a cabinet preview.",
            "needs_confirmation": False,
        }
        project_model = {
            "project_id": "project-test",
            "spaces": [{"space_id": "space-1"}],
        }
        spec = create_object_spec("cabinet", width=1800, depth=600)
        layout = {
            "candidates": [
                {
                    "candidate_id": "candidate-001",
                    "score": 0.1,
                    "placements": [{"object_id": spec["object_id"], "base_point": [0, 0, 0]}],
                    "checks": [{"name": "inside_boundary", "status": "fail"}],
                }
            ]
        }

        proposal = create_design_proposal(
            brief=brief,
            project_model=project_model,
            object_spec=spec,
            layout_proposal=layout,
        )

        self.assertTrue(proposal["needs_confirmation"])
        with self.assertRaisesRegex(ValueError, "needs confirmation"):
            proposal_to_plan(proposal, object_spec=spec, layout_proposal=layout)


if __name__ == "__main__":
    unittest.main()
