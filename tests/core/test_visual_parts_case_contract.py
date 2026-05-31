from __future__ import annotations

import json
import math
import unittest
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS = PROJECT_ROOT / "projects" / "residential_sofa_2seat_20260528" / "runs"


class FakeDriver:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self._next = 1

    def draw_line(self, **kwargs: Any) -> dict[str, str]:
        return self._record("line", kwargs)

    def draw_arc(self, **kwargs: Any) -> dict[str, str]:
        return self._record("arc", kwargs)

    def _record(self, primitive: str, kwargs: dict[str, Any]) -> dict[str, str]:
        handle = f"H{self._next}"
        self._next += 1
        self.calls.append({"primitive": primitive, "handle": handle, **kwargs})
        return {"handle": handle}


class VisualPartsCaseContractTests(unittest.TestCase):
    def test_render_round12_visual_parts_creates_handles_for_each_declared_part(self) -> None:
        from projects.residential_sofa_2seat_20260528.runs.part_renderer import render_visual_parts

        visual_parts = json.loads((RUNS / "round12_visual_parts.json").read_text(encoding="utf-8"))
        style_target = RUNS.parents[0] / visual_parts["style_target"]
        evidence = visual_parts["style_target_evidence"]

        self.assertTrue(style_target.is_file())
        self.assertEqual(visual_parts["style_target_source"], "reference_crop")
        self.assertFalse(evidence["generated"])
        self.assertTrue(evidence["derived_from_real_cad_screenshot"])
        self.assertTrue((RUNS.parents[0] / evidence["source_image"]).is_file())
        driver = FakeDriver()

        report = render_visual_parts(
            driver,
            visual_parts,
            origin=[1000.0, 2000.0, 0.0],
            width=1870.0,
            height=960.0,
        )

        part_ids = {part["id"] for part in visual_parts["parts"]}
        self.assertEqual(set(report["part_handles"]), part_ids)
        self.assertTrue(all(report["part_handles"][part_id] for part_id in part_ids))
        self.assertEqual(report["created_count"], sum(len(v) for v in report["part_handles"].values()))
        self.assertEqual(len(driver.calls), report["created_count"])
        self.assertGreaterEqual(report["created_count"], 20)
        line_lengths = [
            math.hypot(
                call["end_point"][0] - call["start_point"][0],
                call["end_point"][1] - call["start_point"][1],
            )
            for call in driver.calls
            if call["primitive"] == "line"
        ]
        self.assertGreaterEqual(min(line_lengths), 8.0)
        calls_by_handle = {call["handle"]: call for call in driver.calls}

        def bbox_for(part_id: str) -> tuple[float, float, float, float]:
            xs: list[float] = []
            ys: list[float] = []
            for handle in report["part_handles"][part_id]:
                call = calls_by_handle[handle]
                if call["primitive"] == "line":
                    xs.extend([call["start_point"][0], call["end_point"][0]])
                    ys.extend([call["start_point"][1], call["end_point"][1]])
                else:
                    cx, cy = call["center"][0], call["center"][1]
                    r = call["radius"]
                    xs.extend([cx - r, cx + r])
                    ys.extend([cy - r, cy + r])
            return min(xs), min(ys), max(xs), max(ys)

        seat_bbox = bbox_for("seat_left")
        back_bbox = bbox_for("back_left")
        self.assertLessEqual(seat_bbox[3] - seat_bbox[1], 960.0 * 0.25)
        self.assertGreaterEqual(back_bbox[3] - back_bbox[1], 960.0 * 0.55)

    def test_renderer_rejects_undeclared_required_part(self) -> None:
        from projects.residential_sofa_2seat_20260528.runs.part_renderer import render_visual_parts

        visual_parts = json.loads((RUNS / "round12_visual_parts.json").read_text(encoding="utf-8"))
        visual_parts["parts"] = [part for part in visual_parts["parts"] if part["id"] != "back_right"]

        with self.assertRaisesRegex(ValueError, "missing required visual parts"):
            render_visual_parts(
                FakeDriver(),
                visual_parts,
                origin=[0.0, 0.0, 0.0],
                width=1870.0,
                height=960.0,
            )

    def test_style_compare_and_agent_review_artifacts_are_component_level(self) -> None:
        compare = (RUNS / "round12_style_compare.md").read_text(encoding="utf-8")
        review = json.loads((RUNS / "round12_agent_review.json").read_text(encoding="utf-8"))

        for part_id in [
            "arm_left",
            "arm_right",
            "seat_left",
            "seat_right",
            "back_left",
            "back_right",
            "base_rail",
        ]:
            with self.subTest(part=part_id):
                self.assertIn(part_id, compare)
                self.assertIn(part_id, review["component_checks"])

        self.assertFalse(review["delivery_allowed"])
        self.assertFalse(review["agent_review_all_pass"])
        self.assertEqual(review["blocked_reason"], "user_feedback_fail_audit_chain_calibrated")
        self.assertFalse(review["checks"]["visual_match_brief"]["pass"])
        self.assertFalse(review["checks"]["same_product_family_as_reference"]["pass"])
        self.assertFalse(review["checks"]["no_schematic_shortcut"]["pass"])
        self.assertEqual(review["visual_parts"], "round12_visual_parts.json")
        self.assertEqual(review["style_target_source"], "reference_crop")
        self.assertNotIn("pending execution", compare.lower())
        self.assertIn("- [ ] Machine audit reports `audit_pass=true`.", compare)
        self.assertIn("User review failed round12", compare)
        self.assertIn("real AutoCAD screenshot", compare)


if __name__ == "__main__":
    unittest.main()
