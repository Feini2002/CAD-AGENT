from __future__ import annotations

import json
import unittest
from pathlib import Path

from projects.residential_sofa_2seat_20260528.runs import part_renderer
from projects.residential_sofa_2seat_20260528.runs import semantic_clean_two_seater


class FakeDriver:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self._next = 1

    def draw_line(self, **kwargs: object) -> dict[str, str]:
        return self._record("line", kwargs)

    def draw_arc(self, **kwargs: object) -> dict[str, str]:
        return self._record("arc", kwargs)

    def _record(self, primitive: str, kwargs: dict[str, object]) -> dict[str, str]:
        handle = f"H{self._next}"
        self._next += 1
        self.calls.append({"primitive": primitive, "handle": handle, **kwargs})
        return {"handle": handle}


class ResidentialSofaPartRendererTests(unittest.TestCase):
    def _exact_vertical_segments(self, driver: FakeDriver) -> list[tuple[float, float, float]]:
        segments: list[tuple[float, float, float]] = []
        for call in driver.calls:
            if call["primitive"] != "line":
                continue
            sp = call["start_point"]
            ep = call["end_point"]
            if not isinstance(sp, list) or not isinstance(ep, list):
                continue
            x0, y0 = float(sp[0]), float(sp[1])
            x1, y1 = float(ep[0]), float(ep[1])
            if abs(x0 - x1) < 0.01:
                segments.append((round(x0, 3), round(min(y0, y1), 3), round(max(y0, y1), 3)))
        return segments

    def test_round12_renderer_exposes_visual_audit_summary(self) -> None:
        summary_fn = getattr(part_renderer, "summarize_visual_parts_for_audit", None)
        self.assertIsNotNone(summary_fn)
        if summary_fn is None:
            return

        visual_parts = json.loads(
            Path("projects/residential_sofa_2seat_20260528/runs/round12_visual_parts.json").read_text(
                encoding="utf-8"
            )
        )

        summary = summary_fn(visual_parts, origin=[0, 0, 0], width=1870, height=960)

        self.assertEqual(summary["required_part_count"], 7)
        self.assertEqual(summary["closed_part_count"], 7)
        self.assertEqual(summary["seat_cushion_count"], 2)
        self.assertEqual(summary["back_cushion_count"], 2)
        self.assertEqual(summary["rounded_rect_family_count"], 7)
        self.assertEqual(summary["distinct_shape_family_count"], 1)
        self.assertGreater(summary["part_gap_count"], 0)
        self.assertGreater(summary["part_overlap_count"], 0)

    def test_round_script_merges_render_audit_summary_into_checklist(self) -> None:
        merge_fn = getattr(semantic_clean_two_seater, "merge_render_audit_summary", None)
        self.assertIsNotNone(merge_fn)
        if merge_fn is None:
            return

        checklist = {
            "checks": {
                "semantic": {
                    "visual_parts_summary": {
                        "required_part_count": 7,
                        "closed_part_count": 7,
                    }
                }
            }
        }
        render_report = {
            "audit_summary": {
                "rounded_rect_family_count": 7,
                "distinct_shape_family_count": 1,
                "part_gap_count": 2,
                "part_overlap_count": 1,
            }
        }

        merged = merge_fn(checklist, render_report)
        summary = merged["checks"]["semantic"]["visual_parts_summary"]

        self.assertEqual(summary["closed_part_count"], 7)
        self.assertEqual(summary["rounded_rect_family_count"], 7)
        self.assertEqual(summary["distinct_shape_family_count"], 1)
        self.assertEqual(summary["part_gap_count"], 2)
        self.assertEqual(summary["part_overlap_count"], 1)
        self.assertNotIn("rounded_rect_family_count", checklist["checks"]["semantic"]["visual_parts_summary"])

    def test_round13_visual_parts_are_curved_and_connected(self) -> None:
        summary_fn = getattr(part_renderer, "summarize_visual_parts_for_audit", None)
        self.assertIsNotNone(summary_fn)
        if summary_fn is None:
            return
        visual_parts = json.loads(
            Path("projects/residential_sofa_2seat_20260528/runs/round13_visual_parts.json").read_text(
                encoding="utf-8"
            )
        )

        summary = summary_fn(visual_parts, origin=[1000.0, 2000.0, 0.0], width=1870.0, height=960.0)

        self.assertEqual(summary["required_part_count"], 7)
        self.assertEqual(summary["closed_part_count"], 7)
        self.assertGreaterEqual(summary["distinct_shape_family_count"], 4)
        self.assertLess(summary["rounded_rect_family_count"], 7)
        self.assertEqual(summary["part_gap_count"], 0)
        self.assertEqual(summary["part_overlap_count"], 0)

    def test_round13_renderer_supports_curved_shape_family(self) -> None:
        visual_parts = json.loads(
            Path("projects/residential_sofa_2seat_20260528/runs/round13_visual_parts.json").read_text(
                encoding="utf-8"
            )
        )
        driver = FakeDriver()

        report = part_renderer.render_visual_parts(
            driver,
            visual_parts,
            origin=[1000.0, 2000.0, 0.0],
            width=1870.0,
            height=960.0,
        )

        self.assertEqual(report["round"], "round13")
        self.assertEqual(set(report["part_handles"]), part_renderer.REQUIRED_PART_IDS)
        self.assertGreaterEqual(report["created_count"], 45)
        self.assertGreaterEqual(sum(1 for call in driver.calls if call["primitive"] == "arc"), 20)
        for call in driver.calls:
            if call["primitive"] == "arc":
                sweep = abs(float(call["end_angle"]) - float(call["start_angle"]))
                self.assertLessEqual(sweep, 120.0)
        self.assertEqual(report["audit_summary"]["part_gap_count"], 0)
        self.assertEqual(report["audit_summary"]["part_overlap_count"], 0)

    def test_renderer_deduplicates_shared_vertical_edges_that_create_bright_center_lines(self) -> None:
        visual_parts = json.loads(
            Path("projects/residential_sofa_2seat_20260528/runs/round13_visual_parts.json").read_text(
                encoding="utf-8"
            )
        )
        driver = FakeDriver()

        report = part_renderer.render_visual_parts(
            driver,
            visual_parts,
            origin=[1000.0, 2000.0, 0.0],
            width=1870.0,
            height=960.0,
        )

        segments = self._exact_vertical_segments(driver)
        self.assertEqual(len(segments), len(set(segments)))
        self.assertGreater(report["deduped_line_count"], 0)

    def test_sofa_layer_order_accepts_user_corrected_plan_orientation(self) -> None:
        visual_parts = {
            "parts": [
                {
                    "id": "base_rail",
                    "role": "hard_back",
                    "shape": "base_curved_rail",
                    "closed": True,
                    "bounds_ratio": [0.0, 0.0, 1.0, 0.06],
                },
                {
                    "id": "arm_left",
                    "role": "arm",
                    "shape": "curved_arm",
                    "closed": True,
                    "bounds_ratio": [0.0, 0.06, 0.064171, 1.0],
                },
                {
                    "id": "back_left",
                    "role": "back_cushion",
                    "shape": "back_soft_panel",
                    "closed": True,
                    "bounds_ratio": [0.064171, 0.08, 0.5, 0.24],
                },
                {
                    "id": "back_right",
                    "role": "back_cushion",
                    "shape": "back_soft_panel",
                    "closed": True,
                    "bounds_ratio": [0.5, 0.08, 0.935829, 0.24],
                },
                {
                    "id": "seat_left",
                    "role": "seat_cushion",
                    "shape": "seat_bow_cushion",
                    "closed": True,
                    "bounds_ratio": [0.064171, 0.24, 0.5, 1.0],
                },
                {
                    "id": "seat_right",
                    "role": "seat_cushion",
                    "shape": "seat_bow_cushion",
                    "closed": True,
                    "bounds_ratio": [0.5, 0.24, 0.935829, 1.0],
                },
                {
                    "id": "arm_right",
                    "role": "arm",
                    "shape": "curved_arm",
                    "closed": True,
                    "bounds_ratio": [0.935829, 0.06, 1.0, 1.0],
                },
            ],
            "visual_semantics": {
                "plan_view_front_direction": "+Y",
                "layer_order_back_to_front": ["hard_back", "back_cushion", "seat_cushion"],
            },
        }

        summary = part_renderer.summarize_visual_parts_for_audit(
            visual_parts,
            origin=[1000.0, 2000.0, 0.0],
            width=1870.0,
            height=960.0,
        )

        self.assertEqual(summary["hard_back_count"], 1)
        self.assertEqual(summary["sofa_layer_order_pass"], 1)

    def test_connection_summary_uses_declared_semantic_connection_pairs(self) -> None:
        visual_parts = {
            "parts": [
                {
                    "id": "base_rail",
                    "role": "hard_back",
                    "shape": "base_curved_rail",
                    "closed": True,
                    "bounds_ratio": [0.0, 0.0, 1.0, 0.06],
                },
                {
                    "id": "arm_left",
                    "role": "arm",
                    "shape": "curved_arm",
                    "closed": True,
                    "bounds_ratio": [0.0, 0.06, 0.064171, 1.0],
                },
                {
                    "id": "back_left",
                    "role": "back_cushion",
                    "shape": "back_soft_panel",
                    "closed": True,
                    "bounds_ratio": [0.064171, 0.06, 0.5, 0.24],
                },
                {
                    "id": "seat_left",
                    "role": "seat_cushion",
                    "shape": "seat_bow_cushion",
                    "closed": True,
                    "bounds_ratio": [0.064171, 0.24, 0.5, 1.0],
                },
                {
                    "id": "seat_right",
                    "role": "seat_cushion",
                    "shape": "seat_bow_cushion",
                    "closed": True,
                    "bounds_ratio": [0.5, 0.24, 0.935829, 1.0],
                },
                {
                    "id": "back_right",
                    "role": "back_cushion",
                    "shape": "back_soft_panel",
                    "closed": True,
                    "bounds_ratio": [0.5, 0.06, 0.935829, 0.24],
                },
                {
                    "id": "arm_right",
                    "role": "arm",
                    "shape": "curved_arm",
                    "closed": True,
                    "bounds_ratio": [0.935829, 0.06, 1.0, 1.0],
                },
            ],
            "layout": {
                "connection_pairs": [
                    ["arm_left", "seat_left", "x"],
                    ["seat_right", "arm_right", "x"],
                    ["base_rail", "back_left", "y"],
                    ["base_rail", "back_right", "y"],
                    ["back_left", "seat_left", "y"],
                    ["back_right", "seat_right", "y"],
                ]
            },
        }

        summary = part_renderer.summarize_visual_parts_for_audit(
            visual_parts,
            origin=[1000.0, 2000.0, 0.0],
            width=1870.0,
            height=960.0,
        )

        self.assertEqual(summary["part_gap_count"], 0)
        self.assertEqual(summary["part_overlap_count"], 0)

    def test_round13_visual_parts_record_inverted_sofa_direction(self) -> None:
        visual_parts = json.loads(
            Path("projects/residential_sofa_2seat_20260528/runs/round13_visual_parts.json").read_text(
                encoding="utf-8"
            )
        )

        summary = part_renderer.summarize_visual_parts_for_audit(
            visual_parts,
            origin=[1000.0, 2000.0, 0.0],
            width=1870.0,
            height=960.0,
        )

        self.assertEqual(summary["sofa_layer_order_pass"], 0)


if __name__ == "__main__":
    unittest.main()
