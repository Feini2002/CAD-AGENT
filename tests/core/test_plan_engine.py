from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.model_to_plan import model_to_plans
from core.plan_engine.validate_plan import validate_plan


def load_example(path: str) -> dict[str, object]:
    return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))


class PlanEngineTests(unittest.TestCase):
    def test_object_spec_converts_to_plan_envelope(self) -> None:
        spec = load_example("examples/object_specs/minimal_cabinet_object.json")

        result = model_to_plans(object_spec=spec)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["plans"][0]["source_model_refs"]["object_id"], spec["object_id"])
        self.assertEqual(validate_plan(result["plans"][0]["cad_plan"]), [])

    def test_multiple_object_specs_and_layout_placements_convert_to_plan_list(self) -> None:
        cabinet = load_example("examples/object_specs/minimal_cabinet_object.json")
        table = {
            **cabinet,
            "object_id": "object-table-1200",
            "type": "table",
            "name": "Preview Table",
            "size": {"width": 1200, "depth": 700, "height": 750},
        }
        layout = {
            "layout_id": "layout-many",
            "candidates": [
                {
                    "candidate_id": "candidate-001",
                    "score": 0.9,
                    "placements": [
                        {"object_id": cabinet["object_id"], "base_point": [0, 0, 0], "bbox": {"min": [0, 0], "max": [1800, 600]}},
                        {"object_id": table["object_id"], "base_point": [2100, 0, 0], "bbox": {"min": [2100, 0], "max": [3300, 700]}},
                    ],
                    "checks": [{"name": "inside_boundary", "status": "pass"}],
                }
            ],
        }

        result = model_to_plans(object_specs=[cabinet, table], layout_proposal=layout)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["plans"]), 2)
        self.assertEqual(result["plans"][1]["cad_plan"]["placement"]["base_point"], [2100, 0, 0])

    def test_proposal_requires_confirmation_before_conversion(self) -> None:
        spec = load_example("examples/object_specs/minimal_cabinet_object.json")
        layout = load_example("examples/layout_proposals/minimal_cabinet_layout.json")
        proposal = load_example("examples/design_proposals/minimal_cabinet_proposal.json")
        proposal["needs_confirmation"] = True

        result = model_to_plans(object_spec=spec, layout_proposal=layout, design_proposal=proposal)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("needs confirmation", result["errors"][0])

    def test_model_to_plans_uses_confirmed_candidate_id(self) -> None:
        spec = load_example("examples/object_specs/minimal_cabinet_object.json")
        layout = {
            "layout_id": "layout-many",
            "candidates": [
                {
                    "candidate_id": "candidate-a",
                    "score": 0.5,
                    "placements": [{"object_id": spec["object_id"], "base_point": [0, 0, 0]}],
                    "checks": [],
                },
                {
                    "candidate_id": "candidate-b",
                    "score": 0.9,
                    "placements": [{"object_id": spec["object_id"], "base_point": [1200, 0, 0]}],
                    "checks": [],
                },
            ],
        }
        proposal = {
            "proposal_id": "proposal-many",
            "needs_confirmation": False,
            "confirmed_candidate_id": "candidate-b",
        }

        result = model_to_plans(object_spec=spec, layout_proposal=layout, design_proposal=proposal, confirmed=True)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["plans"][0]["cad_plan"]["placement"]["base_point"], [1200, 0, 0])

    def test_dry_run_report_is_machine_readable(self) -> None:
        plan = load_example("examples/plans/draw_test_cabinet.json")

        report = create_dry_run_report(plan)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["entities"][0]["type"], "rectangle")
        self.assertEqual(report["bbox"], {"min": [0, 0], "max": [1800, 600]})
        self.assertIn("CAD_PLAN DRY RUN", report["human_summary"])


if __name__ == "__main__":
    unittest.main()
