from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.object_engine.object_to_plan import object_to_plan
from core.object_engine.parametric_objects import apply_style_to_object_spec, create_object_spec
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
        self.assertEqual(validate_plan(plan), [])

    def test_primary_object_types_have_expected_component_roles(self) -> None:
        cabinet_roles = {component["role"] for component in create_object_spec("cabinet")["components"]}
        shelf_roles = {component["role"] for component in create_object_spec("shelf")["components"]}
        table_roles = {component["role"] for component in create_object_spec("table")["components"]}

        self.assertTrue({"body", "front_panel", "shelf", "kickboard", "top_rail"}.issubset(cabinet_roles))
        self.assertTrue({"upright", "storage_level", "back_panel"}.issubset(shelf_roles))
        self.assertTrue({"top", "support", "clearance_zone"}.issubset(table_roles))


if __name__ == "__main__":
    unittest.main()
