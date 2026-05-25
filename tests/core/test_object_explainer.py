from __future__ import annotations

import json
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.object_engine.object_explainer import explain_object_spec


def load_json(path: str) -> dict[str, object]:
    return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))


class ObjectExplainerTests(unittest.TestCase):
    def test_object_explanation_names_size_sources_and_components(self) -> None:
        object_spec = load_json("examples/object_specs/minimal_cabinet_object.json")
        style_profile = load_json("libraries/styles/european.json")

        explanation = explain_object_spec(object_spec, style_profile=style_profile)

        self.assertEqual(explanation["status"], "ok")
        self.assertEqual(explanation["object_id"], "object-cabinet-1800")
        self.assertIn("width", {item["field"] for item in explanation["size_sources"]})
        self.assertIn("cabinet-body", {item["component_id"] for item in explanation["component_rationale"]})
        self.assertEqual(explanation["evidence"]["style_profile_id"], "style-european")


if __name__ == "__main__":
    unittest.main()
