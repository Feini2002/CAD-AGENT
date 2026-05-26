from __future__ import annotations

import json
import unittest

from core.symbol_engine.readability import (
    READABILITY_STATUSES,
    build_symbol_readability_report,
    evaluate_object_spec_readability,
)
from tests.bootstrap import PROJECT_ROOT


class SymbolReadabilityTests(unittest.TestCase):
    def test_surface_desk_symbol_is_symbol_readable(self) -> None:
        spec = json.loads(
            (PROJECT_ROOT / "examples/symbol_specs/surface_desk_plan.json").read_text(encoding="utf-8")
        )
        report = build_symbol_readability_report(spec)
        self.assertEqual(report["readability_status"], "symbol_readable")
        self.assertEqual(report["failed_check_count"], 0)
        self.assertFalse(report["geometry_verified"])

    def test_outline_only_symbol_readable_spec_is_not_symbol_readable(self) -> None:
        spec = json.loads(
            (PROJECT_ROOT / "examples/symbol_specs/surface_desk_plan.json").read_text(encoding="utf-8")
        )
        spec["parts"] = [{"part_id": "only-outline", "kind": "outline"}]
        report = build_symbol_readability_report(spec)
        self.assertIn(
            report["readability_status"],
            {"visual_review_required", "fallback_bbox_placeholder"},
        )
        self.assertGreater(report["failed_check_count"], 0)

    def test_counter_object_maps_to_deferred_readability(self) -> None:
        object_spec = {
            "version": "0.1",
            "object_id": "object-counter-01",
            "type": "counter",
            "name": "Counter",
            "size": {"width": 2400, "depth": 600, "height": 900},
            "components": [{"component_id": "counter-top", "role": "worktop", "count": 1}],
            "drawing_intent": "plan_preview",
        }
        report = evaluate_object_spec_readability(object_spec)
        self.assertEqual(report["readability_status"], "deferred_unsupported_symbol")
        self.assertEqual(report["mapping_status"], "deferred")

    def test_declared_bbox_fallback_maps_to_fallback_bbox_placeholder(self) -> None:
        spec = json.loads(
            (PROJECT_ROOT / "examples/symbol_specs/surface_desk_plan.json").read_text(encoding="utf-8")
        )
        spec["parts"] = [{"part_id": "bbox-only", "kind": "outline"}]
        spec["readability_constraints"]["min_part_count"] = 1
        spec["readability_constraints"]["requires_non_bbox_parts"] = False
        spec["fallback_policy"] = {
            "mode": "fallback_bbox_placeholder",
            "bbox_fallback_declared": True,
            "reason": "explicit bbox placeholder",
        }
        report = build_symbol_readability_report(spec)
        self.assertEqual(report["readability_status"], "fallback_bbox_placeholder")

    def test_elevation_object_spec_maps_to_component_preview_readability(self) -> None:
        object_spec = json.loads(
            (PROJECT_ROOT / "examples/object_specs/desk_1400x700.json").read_text(encoding="utf-8")
        )
        object_spec["drawing_intent"] = "elevation_preview"
        report = evaluate_object_spec_readability(object_spec)
        self.assertEqual(report["readability_status"], "fallback_component_preview")
        self.assertEqual(report["mapping_status"], "fallback_explicit")

    def test_all_readability_statuses_are_registered(self) -> None:
        self.assertEqual(
            set(READABILITY_STATUSES),
            {
                "symbol_readable",
                "visual_review_required",
                "fallback_component_preview",
                "fallback_bbox_placeholder",
                "deferred_unsupported_symbol",
            },
        )


if __name__ == "__main__":
    unittest.main()
