from __future__ import annotations

import json
import unittest

from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import validate_plan
from core.symbol_engine.object_to_symbol import (
    OBJECT_TYPE_TO_ARCHETYPE,
    object_spec_to_symbol_spec,
)
from core.symbol_engine.primitives import symbol_spec_to_cad_plan
from core.symbol_engine.symbol_spec import validate_symbol_spec
from tests.bootstrap import PROJECT_ROOT


MAPPING_FIXTURES = {
    "table": "examples/object_specs/table_1600x800.json",
    "desk": "examples/object_specs/desk_1400x700.json",
    "chair": "examples/object_specs/chair_520x520.json",
    "sofa": "examples/object_specs/sofa_2200x900.json",
    "bed": "examples/object_specs/bed_1800x2000.json",
    "cabinet": "examples/object_specs/minimal_cabinet_object.json",
}


class ObjectToSymbolTests(unittest.TestCase):
    def test_core_object_types_have_archetype_mapping(self) -> None:
        self.assertEqual(
            set(OBJECT_TYPE_TO_ARCHETYPE),
            {"table", "desk", "chair", "sofa", "bed", "cabinet", "shelf", "display_unit"},
        )

    def test_mapped_object_types_produce_valid_symbol_specs(self) -> None:
        for object_type, path in MAPPING_FIXTURES.items():
            with self.subTest(object_type=object_type):
                spec = json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))
                result = object_spec_to_symbol_spec(spec)
                self.assertEqual(result.mapping_status, "symbol_mapped")
                self.assertEqual(result.archetype, OBJECT_TYPE_TO_ARCHETYPE[object_type])
                self.assertEqual(result.symbol_spec["object_type"], object_type)
                self.assertEqual(validate_symbol_spec(result.symbol_spec), [])

    def test_mapped_objects_produce_valid_symbol_glyph_cad_plans(self) -> None:
        for object_type, path in MAPPING_FIXTURES.items():
            with self.subTest(object_type=object_type):
                spec = json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))
                result = object_spec_to_symbol_spec(spec)
                plan = symbol_spec_to_cad_plan(result.symbol_spec, base_point=[2000.0, 2000.0, 0.0])
                self.assertEqual(validate_plan(plan), [])
                dry_run = create_dry_run_report(plan)
                self.assertEqual(dry_run["status"], "valid")

    def test_unsupported_object_type_returns_deferred_fallback(self) -> None:
        spec = {
            "version": "0.1",
            "object_id": "object-counter-01",
            "type": "counter",
            "name": "Counter",
            "size": {"width": 2400, "depth": 600, "height": 900},
            "components": [{"component_id": "counter-top", "role": "worktop", "count": 1}],
            "drawing_intent": "plan_preview",
        }
        result = object_spec_to_symbol_spec(spec)
        self.assertEqual(result.mapping_status, "deferred")
        self.assertEqual(result.fallback_mode, "deferred_unsupported_symbol")
        self.assertEqual(result.symbol_spec["fallback_policy"]["mode"], "deferred_unsupported_symbol")

    def test_elevation_intent_returns_component_preview_fallback(self) -> None:
        spec = json.loads((PROJECT_ROOT / MAPPING_FIXTURES["desk"]).read_text(encoding="utf-8"))
        spec["drawing_intent"] = "elevation_preview"
        result = object_spec_to_symbol_spec(spec)
        self.assertEqual(result.mapping_status, "fallback_explicit")
        self.assertEqual(result.fallback_mode, "fallback_component_preview")


if __name__ == "__main__":
    unittest.main()
