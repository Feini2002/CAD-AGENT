from __future__ import annotations

import json
import unittest

from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import validate_plan
from core.plan_engine.block_alpha_plan import CONTROLLED_BLOCK_ID
from core.symbol_engine.fallback_policy import (
    detect_silent_degradation,
    resolve_symbol_render_resolution,
    tier_evidence_state,
)
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
)
from tests.bootstrap import PROJECT_ROOT


def _controlled_verified_library() -> dict:
    return {
        "version": "0.2",
        "library_id": "test-controlled",
        "units": "mm",
        "blocks": [
            {
                "block_id": CONTROLLED_BLOCK_ID,
                "name": "Controlled Test Block",
                "category": "test_fixture",
                "domain": "generic",
                "tags": ["controlled"],
                "size": {"width": 900, "depth": 450, "height": 750},
                "insertion_point": [0, 0, 0],
                "rotation_allowed": True,
                "cad_identity": {
                    "block_name": "CODEX_TEST_BLOCK_001",
                    "definition_name": "CODEX_TEST_BLOCK_001",
                    "expected_entity_type": "block_reference",
                },
                "validation": {"status": "cad_insertion_verified", "tolerance_mm": 2.0},
            }
        ],
    }


class SymbolFallbackPolicyTests(unittest.TestCase):
    def test_desk_resolves_to_symbol_glyph_with_dry_run_evidence(self) -> None:
        spec = json.loads((PROJECT_ROOT / "examples/object_specs/desk_1400x700.json").read_text(encoding="utf-8"))
        report = resolve_symbol_render_resolution(spec, base_point=[1000.0, 1000.0, 0.0])

        self.assertEqual(report["selected_render_path"], "symbol_glyph")
        self.assertEqual(report["selected_cad_intent"], "draw_symbol_glyph")
        self.assertEqual(report["selected_evidence_state"], EVIDENCE_DRY_RUN_VALID_PLAN_ONLY)
        self.assertFalse(report["silent_degradation"])
        self.assertEqual(report["silent_degradation_errors"], [])
        self.assertEqual(report["symbol_readability_status"], "symbol_readable")
        plan = report["cad_plan"]
        self.assertIsNotNone(plan)
        self.assertEqual(validate_plan(plan), [])
        self.assertEqual(create_dry_run_report(plan)["status"], "valid")

    def test_controlled_verified_block_wins_over_symbol_glyph(self) -> None:
        spec = json.loads((PROJECT_ROOT / "examples/object_specs/desk_1400x700.json").read_text(encoding="utf-8"))
        spec["preferred_block_refs"] = [CONTROLLED_BLOCK_ID]
        library = _controlled_verified_library()
        report = resolve_symbol_render_resolution(spec, block_library=library, base_point=[0.0, 0.0, 0.0])

        self.assertEqual(report["selected_render_path"], "block")
        self.assertEqual(report["selected_cad_intent"], "insert_block_alpha")
        self.assertFalse(report["silent_degradation"])
        plan = report["cad_plan"]
        self.assertEqual(plan["intent"], "insert_block_alpha")
        self.assertEqual(validate_plan(plan), [])

    def test_elevation_uses_component_preview_not_symbol_glyph(self) -> None:
        spec = json.loads((PROJECT_ROOT / "examples/object_specs/desk_1400x700.json").read_text(encoding="utf-8"))
        spec["drawing_intent"] = "elevation_preview"
        report = resolve_symbol_render_resolution(spec)

        self.assertEqual(report["declared_fallback_mode"], "fallback_component_preview")
        self.assertEqual(report["selected_render_path"], "component_preview")
        symbol_tier = next(item for item in report["tier_assessments"] if item["tier"] == "symbol_glyph")
        self.assertFalse(symbol_tier["available"])
        self.assertGreater(report["cad_plan_count"], 0)
        self.assertFalse(report["silent_degradation"])

    def test_unsupported_counter_defers_without_silent_degradation(self) -> None:
        spec = {
            "version": "0.1",
            "object_id": "object-counter-01",
            "type": "counter",
            "name": "Counter",
            "size": {"width": 2400, "depth": 600, "height": 900},
            "drawing_intent": "plan_preview",
        }
        report = resolve_symbol_render_resolution(spec)

        self.assertEqual(report["selected_render_path"], "deferred")
        self.assertEqual(report["selected_evidence_state"], EVIDENCE_DEFERRED_CAD_READBACK)
        self.assertEqual(report["cad_plan_count"], 0)
        self.assertFalse(report["silent_degradation"])

    def test_detect_silent_degradation_when_symbol_skipped_for_bbox(self) -> None:
        spec = json.loads((PROJECT_ROOT / "examples/object_specs/desk_1400x700.json").read_text(encoding="utf-8"))
        report = resolve_symbol_render_resolution(spec)
        report["selected_render_path"] = "bbox_placeholder"
        report["declared_fallback_mode"] = "symbol_readable"
        report["mapping_status"] = "symbol_mapped"
        errors = detect_silent_degradation(report)
        self.assertTrue(errors)

    def test_tier_evidence_state_deferred(self) -> None:
        self.assertEqual(tier_evidence_state("deferred"), EVIDENCE_DEFERRED_CAD_READBACK)


if __name__ == "__main__":
    unittest.main()
