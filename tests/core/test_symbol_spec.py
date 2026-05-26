from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.schemas.registry import get_schema_path
from core.schemas.validator import validate_json, validate_value
from core.symbol_engine.symbol_spec import load_symbol_graph, load_symbol_spec, validate_symbol_spec
from tests.bootstrap import PROJECT_ROOT


class SymbolSpecTests(unittest.TestCase):
    def test_example_symbol_spec_validates_against_schema(self) -> None:
        example = PROJECT_ROOT / "examples" / "symbol_specs" / "surface_desk_plan.json"
        errors = validate_json(get_schema_path("symbol_spec"), example)
        self.assertEqual(errors, [])
        self.assertEqual(validate_symbol_spec(json.loads(example.read_text(encoding="utf-8"))), [])

    def test_example_symbol_graph_validates_against_schema(self) -> None:
        example = PROJECT_ROOT / "examples" / "symbol_graphs" / "single_desk_placement.json"
        errors = validate_json(get_schema_path("symbol_graph"), example)
        self.assertEqual(errors, [])

    def test_invalid_fixture_fails_schema(self) -> None:
        fixture = json.loads(
            (PROJECT_ROOT / "tests" / "fixtures" / "invalid_models" / "symbol_spec.invalid.json").read_text(
                encoding="utf-8"
            )
        )
        schema = json.loads(get_schema_path("symbol_spec").read_text(encoding="utf-8"))
        self.assertTrue(validate_value(fixture["data"], schema))

    def test_symbol_readable_rejects_outline_only_silent_bbox(self) -> None:
        spec = json.loads(
            (PROJECT_ROOT / "examples" / "symbol_specs" / "surface_desk_plan.json").read_text(encoding="utf-8")
        )
        spec["parts"] = [{"part_id": "only-outline", "kind": "outline"}]
        errors = validate_symbol_spec(spec)
        self.assertTrue(any("outline-only" in error for error in errors))

    def test_bbox_fallback_requires_explicit_declaration(self) -> None:
        spec = json.loads(
            (PROJECT_ROOT / "examples" / "symbol_specs" / "surface_desk_plan.json").read_text(encoding="utf-8")
        )
        spec["fallback_policy"] = {"mode": "fallback_bbox_placeholder"}
        errors = validate_symbol_spec(spec)
        self.assertTrue(any("bbox_fallback_declared" in error for error in errors))

    def test_declared_bbox_fallback_placeholder_is_allowed(self) -> None:
        spec = json.loads(
            (PROJECT_ROOT / "examples" / "symbol_specs" / "surface_desk_plan.json").read_text(encoding="utf-8")
        )
        spec["parts"] = [{"part_id": "bbox-only", "kind": "outline"}]
        spec["readability_constraints"]["min_part_count"] = 1
        spec["readability_constraints"]["requires_non_bbox_parts"] = False
        spec["fallback_policy"] = {
            "mode": "fallback_bbox_placeholder",
            "bbox_fallback_declared": True,
            "reason": "explicit placeholder while symbol primitives are deferred",
        }
        self.assertEqual(validate_symbol_spec(spec), [])

    def test_loaders_accept_valid_examples(self) -> None:
        spec = load_symbol_spec(PROJECT_ROOT / "examples" / "symbol_specs" / "surface_desk_plan.json")
        graph = load_symbol_graph(PROJECT_ROOT / "examples" / "symbol_graphs" / "single_desk_placement.json")
        self.assertEqual(spec["symbol_id"], "symbol-desk-1400-plan")
        self.assertEqual(graph["graph_id"], "graph-single-desk-01")


if __name__ == "__main__":
    unittest.main()
