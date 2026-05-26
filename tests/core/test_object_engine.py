from __future__ import annotations

import unittest


from tests.bootstrap import PROJECT_ROOT

from core.object_engine.object_to_plan import object_to_plan
from core.object_engine.detail_plan import object_spec_to_detail_cad_plans
from core.object_engine.parametric_objects import apply_style_to_object_spec, create_object_spec
from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import validate_plan
from core.style_engine.style_profile import load_style_profile


class ObjectEngineTests(unittest.TestCase):
    def test_style_tokens_add_explainable_components(self) -> None:
        spec = create_object_spec("cabinet", width=1800, depth=600)
        styled = apply_style_to_object_spec(spec, load_style_profile("european"))

        roles = {component["role"] for component in styled["components"]}
        self.assertIn("ornament", roles)
        self.assertIn("style-european", styled["style_profile_id"])

    def test_object_to_plan_is_safe_preview_only(self) -> None:
        spec = create_object_spec("table", width=1200, depth=700)

        plan = object_to_plan(spec, base_point=[100, 200, 0])

        self.assertEqual(plan["drawing"]["layer"], "CODEX_PREVIEW")
        self.assertEqual(plan["placement"]["base_point"], [100, 200, 0])
        self.assertFalse(plan["drawing"]["include_label"])
        self.assertFalse(plan["drawing"]["include_dimensions"])
        self.assertEqual(validate_plan(plan), [])

    def test_object_to_plan_keeps_explicit_label_and_dimension_capability(self) -> None:
        spec = create_object_spec("table", width=1200, depth=700)

        plan = object_to_plan(spec, include_label=True, include_dimensions=True)

        self.assertTrue(plan["drawing"]["include_label"])
        self.assertTrue(plan["drawing"]["include_dimensions"])
        self.assertEqual(validate_plan(plan), [])

    def test_primary_object_types_have_expected_component_roles(self) -> None:
        cabinet_roles = {component["role"] for component in create_object_spec("cabinet")["components"]}
        shelf_roles = {component["role"] for component in create_object_spec("shelf")["components"]}
        table_roles = {component["role"] for component in create_object_spec("table")["components"]}

        self.assertTrue({"body", "front_panel", "shelf", "kickboard", "top_rail"}.issubset(cabinet_roles))
        self.assertTrue({"upright", "storage_level", "back_panel"}.issubset(shelf_roles))
        self.assertTrue({"top", "support", "clearance_zone"}.issubset(table_roles))

    def test_expanded_object_types_have_plan_ready_specs(self) -> None:
        expected_roles = {
            "desk": {"worktop", "support", "clearance_zone"},
            "chair": {"seat", "back", "support"},
            "bed": {"sleep_surface", "base"},
            "sofa": {"seat", "back", "arm"},
            "counter": {"worktop", "front_panel", "base"},
            "display_unit": {"display_surface", "storage_level", "base"},
        }

        for object_type, roles in expected_roles.items():
            with self.subTest(object_type=object_type):
                spec = create_object_spec(object_type)
                self.assertEqual(spec["type"], object_type)
                self.assertTrue(roles.issubset({component["role"] for component in spec["components"]}))
                self.assertGreater(spec["size"]["width"], 0)
                self.assertGreater(spec["size"]["depth"], 0)

    def test_detailed_table_plan_expands_into_component_level_preview_plans(self) -> None:
        spec = create_object_spec("table", width=1600, depth=900)

        plans = object_spec_to_detail_cad_plans(spec, base_point=[100, 200, 0])

        roles = {plan["object"]["component_role"] for plan in plans}
        self.assertIn("top", roles)
        self.assertGreaterEqual(sum(1 for plan in plans if plan["object"]["component_role"] == "support"), 4)
        self.assertGreaterEqual(len(plans), 5)
        for plan in plans:
            with self.subTest(role=plan["object"]["component_role"]):
                self.assertEqual(plan["drawing"]["layer"], "CODEX_PREVIEW")
                self.assertFalse(plan["drawing"]["include_label"])
                self.assertFalse(plan["drawing"]["include_dimensions"])
                self.assertEqual(validate_plan(plan), [])
                self.assertEqual(create_dry_run_report(plan)["status"], "valid")

    def test_detailed_furniture_plans_cover_bed_chair_and_sofa_components(self) -> None:
        expected_roles = {
            "bed": {"sleep_surface", "base"},
            "chair": {"seat", "back", "support"},
            "sofa": {"seat", "back", "arm"},
        }

        for object_type, roles in expected_roles.items():
            with self.subTest(object_type=object_type):
                spec = create_object_spec(object_type)
                plans = object_spec_to_detail_cad_plans(spec)
                actual_roles = {plan["object"]["component_role"] for plan in plans}
                self.assertTrue(roles.issubset(actual_roles))
                self.assertGreaterEqual(len(plans), len(roles))
                for plan in plans:
                    self.assertEqual(validate_plan(plan), [])


if __name__ == "__main__":
    unittest.main()
