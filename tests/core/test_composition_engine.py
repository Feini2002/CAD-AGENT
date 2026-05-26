from __future__ import annotations

import unittest

from tests.helpers import artifact_path

from core.composition_engine.templates import (
    composition_to_cad_plans,
    create_composition_spec,
    write_composition_preview_svg,
)
from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import validate_plan


class CompositionEngineTests(unittest.TestCase):
    def test_bedroom_bed_rug_composition_creates_plan_ready_parts(self) -> None:
        composition = create_composition_spec(
            "bedroom_bed_rug",
            persona_role="interior_designer",
            request_text="生成一个床铺加地毯的卧室组合",
        )

        self.assertEqual(composition["composition_id"], "bedroom_bed_rug")
        self.assertEqual(composition["persona_role"], "interior_designer")
        self.assertEqual([item["type"] for item in composition["objects"]], ["rug", "bed"])
        self.assertEqual({item["role"] for item in composition["objects"]}, {"soft_zone", "primary_bed"})
        self.assertEqual(composition["bbox"], {"min": [0, 0], "max": [2400, 1900]})

        plans = composition_to_cad_plans(composition)

        self.assertEqual(len(plans), 2)
        for plan in plans:
            self.assertFalse(plan["drawing"]["include_label"])
            self.assertFalse(plan["drawing"]["include_dimensions"])
        for plan in plans:
            with self.subTest(object_type=plan["object"]["type"]):
                self.assertEqual(validate_plan(plan), [])
                self.assertEqual(create_dry_run_report(plan)["status"], "valid")

    def test_composition_keeps_explicit_label_and_dimension_capability(self) -> None:
        composition = create_composition_spec("bedroom_bed_rug", persona_role="interior_designer")
        composition["objects"][0]["include_label"] = True
        composition["objects"][0]["include_dimensions"] = True

        plans = composition_to_cad_plans(composition)

        self.assertTrue(plans[0]["drawing"]["include_label"])
        self.assertTrue(plans[0]["drawing"]["include_dimensions"])
        self.assertEqual(validate_plan(plans[0]), [])

    def test_dining_and_office_compositions_cover_expected_roles(self) -> None:
        dining = create_composition_spec("dining_table_set", persona_role="home_designer")
        office = create_composition_spec("office_desk_combo", persona_role="office_planner")

        self.assertEqual([item["type"] for item in dining["objects"]].count("chair"), 4)
        self.assertTrue({"dining_surface", "dining_seat"}.issubset({item["role"] for item in dining["objects"]}))
        self.assertTrue({"work_surface", "task_seat", "screen_zone"}.issubset({item["role"] for item in office["objects"]}))

    def test_office_micro_scene_compositions_expose_bindings_and_clearance(self) -> None:
        pair = create_composition_spec("single_desk_chair_pair", persona_role="office_planner")
        back_cabinet = create_composition_spec("desk_with_back_cabinet", persona_role="office_planner")
        shared_aisle = create_composition_spec("two_workstations_shared_aisle", persona_role="office_planner")
        entry = create_composition_spec("entry_reception_clearance", persona_role="office_planner")

        self.assertEqual(len(pair["bindings"]), 1)
        self.assertEqual(pair["clearance_refs"][0]["role"], "chair_pullback_clearance")
        self.assertEqual(len(back_cabinet["clearance_refs"]), 2)
        self.assertEqual(shared_aisle["circulation"][0]["role"], "main_aisle")
        self.assertEqual(entry["clearance_refs"][0]["role"], "entry_clearance")

        for composition in (pair, back_cabinet, shared_aisle, entry):
            plans = composition_to_cad_plans(composition)
            self.assertEqual(len(plans), len(composition["objects"]))
            for plan in plans:
                self.assertEqual(validate_plan(plan), [])
                self.assertEqual(create_dry_run_report(plan)["status"], "valid")

    def test_composition_preview_svg_is_visual_aid_artifact(self) -> None:
        composition = create_composition_spec("office_desk_combo", persona_role="office_planner")
        plans = composition_to_cad_plans(composition)
        preview_path = artifact_path("composition_engine", "office_desk_combo.svg")

        result = write_composition_preview_svg(composition, plans, preview_path)

        self.assertEqual(result["status"], "written")
        self.assertEqual(result["screenshot_role"], "visual_aid_only")
        self.assertTrue(preview_path.exists())
        content = preview_path.read_text(encoding="utf-8")
        self.assertIn("<svg", content)
        self.assertIn("Desk", content)
        self.assertIn("Monitor", content)


if __name__ == "__main__":
    unittest.main()
