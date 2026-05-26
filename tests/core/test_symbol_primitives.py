from __future__ import annotations

import json
import unittest

from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import validate_plan
from core.symbol_engine.primitives import (
    FootprintContext,
    SUPPORTED_PART_KINDS,
    render_symbol_part,
    symbol_spec_to_cad_plan,
)
from tests.bootstrap import PROJECT_ROOT


class SymbolPrimitiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = json.loads(
            (PROJECT_ROOT / "examples" / "symbol_specs" / "surface_desk_plan.json").read_text(encoding="utf-8")
        )
        self.ctx = FootprintContext.from_symbol_spec(self.spec, [1000.0, 2000.0, 0.0])

    def test_supported_part_kinds_cover_step_two_primitives(self) -> None:
        expected = {
            "outline",
            "inner_offset",
            "thick_band",
            "split_line",
            "leg_marker",
            "arc_marker",
            "orientation_marker",
        }
        self.assertTrue(expected.issubset(set(SUPPORTED_PART_KINDS)))

    def test_each_step_two_part_kind_renders_geometry(self) -> None:
        samples = {
            "outline": {"part_id": "o", "kind": "outline"},
            "inner_offset": {"part_id": "i", "kind": "inner_offset", "params": {"inset_mm": 30}},
            "thick_band": {"part_id": "b", "kind": "thick_band", "params": {"band_width_mm": 35}},
            "split_line": {"part_id": "s", "kind": "split_line", "params": {"axis": "x"}},
            "leg_marker": {"part_id": "l", "kind": "leg_marker", "params": {"marker_size_mm": 50}},
            "arc_marker": {"part_id": "a", "kind": "arc_marker", "params": {"marker_size_mm": 80}},
        }
        for kind, part in samples.items():
            with self.subTest(kind=kind):
                items = render_symbol_part(part, self.ctx)
                self.assertGreaterEqual(len(items), 1)
                self.assertEqual(items[0]["kind"], kind)

    def test_surface_desk_symbol_spec_produces_valid_cad_plan(self) -> None:
        plan = symbol_spec_to_cad_plan(self.spec, base_point=[5000.0, 5000.0, 0.0])
        self.assertEqual(plan["intent"], "draw_symbol_glyph")
        self.assertFalse(plan["drawing"]["include_label"])
        self.assertFalse(plan["drawing"]["include_dimensions"])
        self.assertEqual(validate_plan(plan), [])
        dry_run = create_dry_run_report(plan)
        self.assertEqual(dry_run["status"], "valid")
        self.assertGreaterEqual(len(dry_run["entities"]), 4)
        entity_types = {entity["type"] for entity in dry_run["entities"]}
        self.assertIn("rectangle", entity_types)
        self.assertIn("circle", entity_types)
        self.assertIn("line", entity_types)

    def test_symbol_glyph_rejects_text_like_primitives(self) -> None:
        plan = symbol_spec_to_cad_plan(self.spec, base_point=[0.0, 0.0, 0.0])
        plan["object"]["glyph_primitives"].append(
            {
                "part_id": "bad-text",
                "kind": "outline",
                "primitive": "text",
                "position": [0, 0, 0],
                "text": "label",
            }
        )
        errors = validate_plan(plan)
        self.assertTrue(any("primitive is not supported" in error for error in errors))

    def test_include_label_is_rejected_for_symbol_glyph(self) -> None:
        with self.assertRaisesRegex(ValueError, "must not enable labels"):
            symbol_spec_to_cad_plan(self.spec, include_label=True)


if __name__ == "__main__":
    unittest.main()
