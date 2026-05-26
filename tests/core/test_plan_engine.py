from __future__ import annotations

import json
import unittest


from tests.bootstrap import PROJECT_ROOT

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

    def test_insert_block_alpha_example_plan_validates(self) -> None:
        plan = load_example("examples/plans/insert_block_alpha_test.json")

        self.assertEqual(validate_plan(plan), [])

    def test_insert_block_alpha_invalid_cases_are_rejected(self) -> None:
        base = load_example("examples/plans/insert_block_alpha_test.json")

        missing_block_name = json.loads(json.dumps(base))
        missing_block_name["object"]["cad_identity"] = {}
        self.assertIn("block_name", "; ".join(validate_plan(missing_block_name)))

        arbitrary_block_id = json.loads(json.dumps(base))
        arbitrary_block_id["object"]["block_id"] = "project-block-999"
        self.assertIn("controlled-test-block-001", "; ".join(validate_plan(arbitrary_block_id)))

        arbitrary_block_name = json.loads(json.dumps(base))
        arbitrary_block_name["object"]["cad_identity"]["block_name"] = "PROJECT_REAL_BLOCK"
        self.assertIn("CODEX_TEST_BLOCK_001", "; ".join(validate_plan(arbitrary_block_name)))

        formal_layer = json.loads(json.dumps(base))
        formal_layer["drawing"]["layer"] = "A-FURN"
        self.assertIn("CODEX_PREVIEW", "; ".join(validate_plan(formal_layer)))

        illegal_scale = json.loads(json.dumps(base))
        illegal_scale["placement"]["scale"] = [1, 0, 1]
        self.assertIn("scale", "; ".join(validate_plan(illegal_scale)))

        non_uniform_scale = json.loads(json.dumps(base))
        non_uniform_scale["placement"]["scale"] = [1, 2, 1]
        self.assertIn("uniform scale", "; ".join(validate_plan(non_uniform_scale)))

        missing_base_point = json.loads(json.dumps(base))
        missing_base_point["placement"].pop("base_point")
        self.assertIn("base_point", "; ".join(validate_plan(missing_base_point)))

    def test_insert_block_alpha_dry_run_marks_geometry_unverified(self) -> None:
        plan = load_example("examples/plans/insert_block_alpha_test.json")

        report = create_dry_run_report(plan)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["intent"], "insert_block_alpha")
        self.assertEqual(report["evidence_state"], "dry_run_valid_plan_only")
        self.assertEqual(report["geometry_accuracy"], "not_verified_without_cad_readback")
        self.assertEqual(report["entities"][0]["type"], "block_reference")
        self.assertEqual(report["entities"][0]["block_name"], "CODEX_TEST_BLOCK_001")
        self.assertIn("bbox", report)

    def test_insert_block_alpha_dry_run_applies_uniform_scale_to_bbox(self) -> None:
        plan = load_example("examples/plans/insert_block_alpha_test.json")
        plan["placement"]["scale"] = [2, 2, 2]

        report = create_dry_run_report(plan)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["bbox"], {"min": [1200, 800], "max": [3000.0, 1700.0]})

    def test_dry_run_report_is_machine_readable(self) -> None:
        plan = load_example("examples/plans/draw_test_cabinet.json")

        report = create_dry_run_report(plan)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["entities"][0]["type"], "rectangle")
        self.assertEqual(report["bbox"], {"min": [0, 0], "max": [1800, 600]})
        self.assertIn("CAD_PLAN DRY RUN", report["human_summary"])


if __name__ == "__main__":
    unittest.main()
