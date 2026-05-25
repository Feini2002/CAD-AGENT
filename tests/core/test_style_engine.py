from __future__ import annotations

import unittest


from tests.bootstrap import PROJECT_ROOT

from core.object_engine.parametric_objects import apply_style_to_object_spec, create_object_spec
from core.style_engine.style_profile import label_policy, load_style_profile


class StyleEngineTests(unittest.TestCase):
    def test_style_profiles_drive_distinct_object_components(self) -> None:
        spec = create_object_spec("cabinet", width=1800, depth=600)

        modern = apply_style_to_object_spec(spec, load_style_profile("modern"))
        european = apply_style_to_object_spec(spec, load_style_profile("european"))
        minimal = apply_style_to_object_spec(spec, load_style_profile("minimal"))

        modern_roles = {component["role"] for component in modern["components"]}
        european_roles = {component["role"] for component in european["components"]}
        minimal_roles = {component["role"] for component in minimal["components"]}

        self.assertIn("front_panel", modern_roles)
        self.assertIn("ornament", european_roles)
        self.assertIn("simplified_panel", minimal_roles)
        self.assertNotIn("ornament", minimal_roles)
        self.assertGreater(len(european["components"]), len(minimal["components"]))

    def test_label_policy_helper_defaults_safely(self) -> None:
        self.assertEqual(label_policy(load_style_profile("european")), "object_and_size")
        self.assertEqual(label_policy({"tokens": {"label_policy": 123}}), "object_name")


if __name__ == "__main__":
    unittest.main()
