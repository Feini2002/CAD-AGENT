from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import artifact_path
from tests.bootstrap import PROJECT_ROOT

from core.execution.execute_plan import execute_plan_file
from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import validate_plan
from core.placement.designer_view_nearby import (
    audit_nearby_readback,
    collect_cad_view_context,
    resolve_nearby_placement,
    run_nearby_preview_trial,
)
from core.verification.fake_cad_driver import FakeCadDriver, FakeCadEntity


FIXTURES = PROJECT_ROOT / "examples" / "placement" / "designer_view_nearby"


def _fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


class DesignerViewNearbyPlacementTests(unittest.TestCase):
    def test_selected_handle_anchor_places_right_side_inside_current_viewport(self) -> None:
        resolution = resolve_nearby_placement(
            _fixture("selected_handle_right"),
            phrase="右边",
            target_size={"width": 1200, "depth": 600},
        )

        self.assertEqual(resolution["status"], "resolved")
        self.assertEqual(resolution["anchor_source"], "selected_handles")
        self.assertEqual(resolution["selected_slot"]["direction"], "right")
        self.assertEqual(resolution["base_point"], [3300.0, 900.0, 0])
        self.assertTrue(resolution["checks"]["target_in_original_viewport"])
        self.assertTrue(resolution["checks"]["near_anchor"])

    def test_actual_chinese_direction_words_bias_candidate_order(self) -> None:
        left = resolve_nearby_placement(
            _fixture("selected_handle_right"),
            phrase="在左边试一下",
            target_size={"width": 200, "depth": 400},
        )
        top = resolve_nearby_placement(
            _fixture("selected_handle_right"),
            phrase="放到上方旁边看看",
            target_size={"width": 700, "depth": 400},
        )
        bottom = resolve_nearby_placement(
            _fixture("selected_handle_right"),
            phrase="下方附近补一个",
            target_size={"width": 700, "depth": 400},
        )

        self.assertEqual(left["status"], "resolved")
        self.assertEqual(left["phrase_analysis"]["direction_bias"], "left")
        self.assertEqual(left["selected_slot"]["direction"], "left")
        self.assertEqual(left["base_point"], [100.0, 900.0, 0])
        self.assertEqual(top["phrase_analysis"]["direction_bias"], "top")
        self.assertEqual(top["selected_slot"]["direction"], "top")
        self.assertEqual(bottom["phrase_analysis"]["direction_bias"], "bottom")
        self.assertEqual(bottom["selected_slot"]["direction"], "bottom")

    def test_ambiguous_visible_focus_requires_confirmation_without_handles(self) -> None:
        resolution = resolve_nearby_placement(
            _fixture("ambiguous_visible_focus"),
            phrase="在旁边画个测试矩形",
            target_size={"width": 700, "depth": 400},
        )

        self.assertEqual(resolution["status"], "needs_confirmation")
        self.assertEqual(resolution["anchor_source"], "ambiguous_visible_focus")
        self.assertIn("Visible focus is ambiguous", resolution["blocked_reasons"][0])
        self.assertGreaterEqual(len(resolution["anchor_candidates"]), 2)
        self.assertNotIn("base_point", resolution)

    def test_recent_handles_are_used_only_when_visible(self) -> None:
        visible = resolve_nearby_placement(
            _fixture("recent_handle_visible"),
            phrase="旁边",
            target_size={"width": 900, "depth": 500},
        )
        outside = resolve_nearby_placement(
            _fixture("recent_handle_outside_view"),
            phrase="旁边",
            target_size={"width": 900, "depth": 500},
        )

        self.assertEqual(visible["anchor_source"], "recent_created_handles")
        self.assertEqual(outside["anchor_source"], "visible_focus_cluster")
        self.assertEqual(outside["status"], "resolved")

    def test_visible_cluster_fallback_resolves_nearby_without_explicit_handles(self) -> None:
        resolution = resolve_nearby_placement(
            _fixture("visible_cluster"),
            phrase="旁边",
            target_size={"width": 700, "depth": 400},
        )

        self.assertEqual(resolution["status"], "resolved")
        self.assertEqual(resolution["anchor_source"], "visible_focus_cluster")
        self.assertTrue(resolution["selected_slot"]["direction"] in {"right", "top", "bottom", "left"})
        self.assertIn("viewport_bbox_before_draw", resolution)

    def test_missing_viewport_blocks_without_far_fallback(self) -> None:
        resolution = resolve_nearby_placement(
            _fixture("no_viewport"),
            phrase="旁边",
            target_size={"width": 700, "depth": 400},
        )

        self.assertEqual(resolution["status"], "blocked")
        self.assertIn("viewport_bbox is required", resolution["blocked_reasons"][0])
        self.assertNotIn("base_point", resolution)

    def test_crowded_viewport_returns_needs_confirmation_instead_of_far_point(self) -> None:
        resolution = resolve_nearby_placement(
            _fixture("crowded_viewport"),
            phrase="旁边",
            target_size={"width": 900, "depth": 500},
        )

        self.assertEqual(resolution["status"], "needs_confirmation")
        self.assertNotIn("base_point", resolution)
        self.assertTrue(all(slot["status"] == "blocked" for slot in resolution["candidate_slots"]))

    def test_validate_plan_rejects_unresolved_nearby_phrase(self) -> None:
        plan = {
            "version": "0.1",
            "domain": "generic",
            "intent": "draw_object",
            "object": {"type": "sofa", "name": "旁边测试沙发", "width": 1200, "depth": 600},
            "placement": {"mode": "relative_to_object", "phrase": "旁边"},
            "drawing": {"layer": "CODEX_PREVIEW"},
            "confidence": 0.7,
            "needs_confirmation": False,
        }

        errors = validate_plan(plan)

        self.assertIn("nearby placement phrases require deterministic placement_resolution or absolute base_point.", errors)
        self.assertEqual(create_dry_run_report(plan)["status"], "invalid")

    def test_nearby_resolution_produces_deterministic_plan_for_execution(self) -> None:
        driver = FakeCadDriver()
        resolution = resolve_nearby_placement(
            _fixture("selected_handle_right"),
            phrase="右边",
            target_size={"width": 1200, "depth": 600},
        )
        plan_path = artifact_path("designer_view_nearby", "resolved_plan.json")
        plan = {
            "version": "0.1",
            "domain": "generic",
            "intent": "draw_object",
            "object": {"type": "sofa", "name": "旁边测试沙发", "width": 1200, "depth": 600},
            "placement": {
                "mode": "absolute",
                "base_point": resolution["base_point"],
                "placement_resolution": resolution,
            },
            "drawing": {"layer": "CODEX_PREVIEW", "include_label": False, "include_dimensions": False},
            "confidence": 0.9,
            "needs_confirmation": False,
        }
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

        result = execute_plan_file(plan_path, driver=driver)

        self.assertEqual(result["status"], "executed")
        self.assertEqual(result["base_point"], [3300.0, 900.0, 0])
        self.assertEqual(result["layer"], "CODEX_PREVIEW")

    def test_readback_audit_fails_when_created_bbox_outside_original_viewport(self) -> None:
        resolution = resolve_nearby_placement(
            _fixture("selected_handle_right"),
            phrase="右边",
            target_size={"width": 1200, "depth": 600},
        )

        audit = audit_nearby_readback(
            resolution,
            readback_entities=[
                {
                    "handle": "H1",
                    "type": "line",
                    "layer": "CODEX_PREVIEW",
                    "start_point": [20000, 20000, 0],
                    "end_point": [21200, 20000, 0],
                }
            ],
        )

        self.assertEqual(audit["status"], "fail")
        self.assertFalse(audit["geometry_verified"])
        self.assertFalse(audit["checks"]["created_bbox_in_original_viewport"])

    def test_collect_context_filters_visible_entities_and_preview_cluster(self) -> None:
        driver = FakeCadDriver()
        driver.current_viewport_bbox = {"min": [0, 0], "max": [5000, 3000]}
        driver.selected_handles = ["S1"]
        driver.entities["S1"] = FakeCadEntity(
            handle="S1",
            object_name="AcDbBlockReference",
            layer="SOURCE",
            bbox={"min": [500, 500], "max": [1500, 1200]},
        )
        driver.entities["P1"] = FakeCadEntity(
            handle="P1",
            object_name="AcDbLine",
            layer="CODEX_PREVIEW",
            StartPoint=[2500, 500, 0],
            EndPoint=[3000, 500, 0],
        )
        driver.entities["FAR"] = FakeCadEntity(
            handle="FAR",
            object_name="AcDbBlockReference",
            layer="SOURCE",
            bbox={"min": [9000, 9000], "max": [9500, 9500]},
        )

        context = collect_cad_view_context(driver, recent_created_handles=["P1", "MISSING"])

        self.assertEqual(context["viewport_bbox"], {"min": [0.0, 0.0], "max": [5000.0, 3000.0]})
        self.assertEqual(context["selected_handles"], ["S1"])
        self.assertEqual(context["recent_created_handles"], ["P1"])
        self.assertEqual({entity["handle"] for entity in context["visible_entities_summary"]}, {"S1", "P1"})
        self.assertEqual(context["preview_layer"], "CODEX_PREVIEW")

    def test_preview_trial_emits_resolution_and_nearby_audit(self) -> None:
        driver = FakeCadDriver()
        driver.current_viewport_bbox = {"min": [0, 0], "max": [5000, 3000]}
        driver.selected_handles = ["S1"]
        driver.entities["S1"] = FakeCadEntity(
            handle="S1",
            object_name="AcDbBlockReference",
            layer="SOURCE",
            bbox={"min": [500, 800], "max": [2500, 1600]},
        )
        output_dir = artifact_path("designer_view_nearby", "trial")

        report = run_nearby_preview_trial(
            driver,
            phrase="在旁边画个测试矩形",
            object_type="test_rect",
            object_name="旁边测试",
            width=900,
            depth=500,
            output_dir=output_dir,
        )

        self.assertEqual(report["status"], "pass")
        self.assertTrue(report["nearby_audit"]["geometry_verified"])
        self.assertEqual(report["resolution"]["anchor_source"], "selected_handles")
        self.assertTrue((output_dir / "placement_resolution_report.json").exists())
        self.assertTrue((output_dir / "nearby_cad_plan.json").exists())


if __name__ == "__main__":
    unittest.main()
