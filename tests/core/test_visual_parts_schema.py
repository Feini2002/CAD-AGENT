from __future__ import annotations

import json
import unittest

from tests.bootstrap import PROJECT_ROOT

from core.schemas.registry import MODEL_SCHEMAS, infer_model_type
from core.schemas.validator import validate_value


class VisualPartsSchemaTests(unittest.TestCase):
    def test_visual_parts_schema_is_registered_and_validates_minimal_example(self) -> None:
        self.assertEqual(MODEL_SCHEMAS["visual_parts"], "visual_parts.schema.json")
        schema = json.loads((PROJECT_ROOT / "core/schemas/visual_parts.schema.json").read_text(encoding="utf-8"))
        data = json.loads(
            (PROJECT_ROOT / "examples/visual_parts/minimal_sofa_visual_parts.json").read_text(encoding="utf-8")
        )

        self.assertEqual(validate_value(data, schema), [])
        self.assertEqual(infer_model_type(data), "visual_parts")

    def test_visual_parts_schema_rejects_missing_required_part_fields(self) -> None:
        schema = json.loads((PROJECT_ROOT / "core/schemas/visual_parts.schema.json").read_text(encoding="utf-8"))
        invalid = {
            "schema_version": 1,
            "object": "sofa_plan",
            "parts": [{"id": "seat_left", "shape": "pill_horizontal"}],
            "layout": {"assembly": "open"},
            "forbidden": [],
            "sizing": {"target_width_mm": 1870},
        }

        errors = validate_value(invalid, schema)

        self.assertIn("$.parts[0].role is required.", errors)
        self.assertIn("$.parts[0].closed is required.", errors)


if __name__ == "__main__":
    unittest.main()
