from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import validate_plan
from core.symbol_engine.archetypes import ARCHETYPE_GRAMMARS, validate_archetype_grammar
from core.symbol_engine.primitives import symbol_spec_to_cad_plan
from core.symbol_engine.symbol_spec import validate_symbol_spec
from tests.bootstrap import PROJECT_ROOT


ARCHETYPE_EXAMPLES = {
    "surface": "examples/symbol_specs/surface_desk_plan.json",
    "seating": "examples/symbol_specs/seating_chair_plan.json",
    "sleeping": "examples/symbol_specs/sleeping_bed_plan.json",
    "storage": "examples/symbol_specs/storage_cabinet_plan.json",
    "display": "examples/symbol_specs/display_shelf_plan.json",
    "workstation": "examples/symbol_specs/workstation_plan.json",
}


class SymbolArchetypeTests(unittest.TestCase):
    def test_all_six_archetypes_are_registered(self) -> None:
        self.assertEqual(
            set(ARCHETYPE_GRAMMARS),
            {"surface", "seating", "sleeping", "storage", "display", "workstation"},
        )

    def test_archetype_examples_pass_full_symbol_validation(self) -> None:
        for archetype, relative_path in ARCHETYPE_EXAMPLES.items():
            with self.subTest(archetype=archetype):
                spec = json.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))
                self.assertEqual(spec["archetype"], archetype)
                self.assertEqual(validate_symbol_spec(spec), [])
                self.assertEqual(validate_archetype_grammar(spec), [])

    def test_archetype_examples_produce_valid_cad_plans(self) -> None:
        for archetype, relative_path in ARCHETYPE_EXAMPLES.items():
            with self.subTest(archetype=archetype):
                spec = json.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))
                plan = symbol_spec_to_cad_plan(spec, base_point=[1000.0, 1000.0, 0.0])
                self.assertEqual(validate_plan(plan), [])
                dry_run = create_dry_run_report(plan)
                self.assertEqual(dry_run["status"], "valid")

    def test_surface_missing_support_marker_fails_grammar(self) -> None:
        spec = json.loads(
            (PROJECT_ROOT / ARCHETYPE_EXAMPLES["surface"]).read_text(encoding="utf-8")
        )
        spec["parts"] = [part for part in spec["parts"] if part["kind"] not in {"leg_marker", "orientation_marker", "split_line"}]
        errors = validate_archetype_grammar(spec)
        self.assertTrue(any("readable part group" in error for error in errors))

    def test_seating_missing_seat_cue_fails_grammar(self) -> None:
        spec = json.loads(
            (PROJECT_ROOT / ARCHETYPE_EXAMPLES["seating"]).read_text(encoding="utf-8")
        )
        spec["parts"] = [
            part for part in spec["parts"] if part["kind"] not in {"seat_split", "split_line", "thick_band"}
        ]
        errors = validate_archetype_grammar(spec)
        self.assertTrue(any("readable part group" in error for error in errors))

    def test_storage_drawer_spacing_out_of_range_fails_position_rule(self) -> None:
        spec = json.loads(
            (PROJECT_ROOT / ARCHETYPE_EXAMPLES["storage"]).read_text(encoding="utf-8")
        )
        for part in spec["parts"]:
            if part["kind"] == "drawer_line":
                part["params"] = {"line_spacing_mm": 2000}
        errors = validate_archetype_grammar(spec)
        self.assertTrue(any("drawer_line" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
