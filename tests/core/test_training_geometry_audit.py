from __future__ import annotations

import unittest
from typing import Any

from core.verification.training_geometry_audit import (
    detect_forbidden_patterns,
    load_training_audit_checklist,
    run_training_geometry_audit,
    _evaluate_reference_profile_match,
)


class TrainingGeometryAuditTests(unittest.TestCase):
    def test_detect_schematic_equal_grid(self) -> None:
        profile = {
            "rounded_rect_shell": True,
            "max_inset_mm": 30.0,
            "arc_count": 20,
            "entity_count": 44,
        }
        hits = detect_forbidden_patterns(profile)
        self.assertIn("schematic_equal_grid", hits)

    def test_detect_closed_outer_shell_and_split_as_backrest(self) -> None:
        profile = {
            "rounded_rect_shell": True,
            "max_inset_mm": 30.0,
            "arc_count": 18,
            "entity_count": 41,
            "seat_front_bow_count": 0,
            "full_width_split_count": 1,
            "back_cushion_count": 0,
            "closed_part_count": 2,
        }

        hits = detect_forbidden_patterns(profile)

        self.assertIn("closed_outer_shell", hits)
        self.assertIn("split_as_backrest", hits)

    def test_detect_missing_required_visual_parts_from_profile(self) -> None:
        profile = {
            "required_part_count": 7,
            "closed_part_count": 5,
            "back_cushion_count": 1,
            "seat_cushion_count": 2,
        }

        hits = detect_forbidden_patterns(profile)

        self.assertIn("missing_required_parts", hits)

    def test_detect_rounded_rect_only_visual_contract(self) -> None:
        profile = {
            "required_part_count": 7,
            "closed_part_count": 7,
            "seat_cushion_count": 2,
            "back_cushion_count": 2,
            "rounded_rect_family_count": 7,
            "distinct_shape_family_count": 1,
        }

        hits = detect_forbidden_patterns(profile)

        self.assertIn("rounded_rect_only_parts", hits)

    def test_detect_part_connection_defects(self) -> None:
        profile = {
            "required_part_count": 7,
            "closed_part_count": 7,
            "seat_cushion_count": 2,
            "back_cushion_count": 2,
            "part_gap_count": 1,
            "part_overlap_count": 1,
        }

        hits = detect_forbidden_patterns(profile)

        self.assertIn("part_connection_defects", hits)

    def test_detect_sofa_direction_semantics_inverted(self) -> None:
        profile = {
            "required_part_count": 7,
            "closed_part_count": 7,
            "seat_cushion_count": 2,
            "back_cushion_count": 2,
            "hard_back_count": 1,
            "sofa_layer_order_pass": 0,
        }

        hits = detect_forbidden_patterns(profile)

        self.assertIn("sofa_direction_semantics_inverted", hits)

    def test_closed_multi_part_visual_contract_is_not_outer_shell_shortcut(self) -> None:
        profile = {
            "rounded_rect_shell": True,
            "max_inset_mm": 30.0,
            "arc_count": 28,
            "entity_count": 56,
            "seat_front_bow_count": 0,
            "required_part_count": 7,
            "closed_part_count": 7,
            "seat_cushion_count": 2,
            "back_cushion_count": 2,
        }

        hits = detect_forbidden_patterns(profile)

        self.assertNotIn("closed_outer_shell", hits)

    def test_reference_profile_match_fail_on_bad_split(self) -> None:
        preview = {"seat_split_ratio": 0.42, "back_band_ratio": 0.58, "arm_width_left_mm": 120, "arm_width_right_mm": 120, "max_inset_mm": 30}
        reference = {"seat_split_ratio": 0.821, "back_band_ratio": 0.179, "arm_width_mm": 120}
        failures: list[str] = []
        deltas: dict[str, float] = {}
        _evaluate_reference_profile_match(
            preview,
            reference,
            {"seat_split_ratio_tol": 0.08, "back_band_ratio_tol": 0.08, "arm_width_tol_mm": 35, "max_inset_mm": 38, "back_band_min": 0.12, "back_band_max": 0.28},
            failures,
            deltas,
        )
        self.assertIn("semantic_seat_split_ratio", failures)
        self.assertIn("semantic_back_band_ratio", failures)

    def test_reference_profile_match_can_skip_legacy_split_when_visual_semantics_own_layer_order(self) -> None:
        preview = {"seat_split_ratio": 0.24, "back_band_ratio": 0.76, "arm_width_left_mm": 120, "arm_width_right_mm": 120, "max_inset_mm": 30}
        reference = {"seat_split_ratio": 0.821, "back_band_ratio": 0.179, "arm_width_mm": 120}
        failures: list[str] = []
        deltas: dict[str, float] = {}
        _evaluate_reference_profile_match(
            preview,
            reference,
            {"check_split_ratios": False, "arm_width_tol_mm": 35, "max_inset_mm": 38},
            failures,
            deltas,
        )
        self.assertNotIn("semantic_seat_split_ratio", failures)
        self.assertNotIn("semantic_back_band_ratio", failures)

    def test_run_audit_with_fake_driver(self) -> None:
        class FakeEnt:
            def __init__(self, layer: str, handle: str = "H1") -> None:
                self.Layer = layer
                self.Handle = handle

        class FakeMs:
            Count = 0

            def Item(self, i: int) -> FakeEnt:
                raise IndexError

        class FakeDriver:
            model_space = FakeMs()

        checklist = {
            "schema_version": 2,
            "case_id": "test",
            "checks": {
                "cleanliness": {"micro_line_count_max": 0, "entity_total_max": 0},
                "semantic": {"min_entity_count": 1},
            },
        }
        audit = run_training_geometry_audit(
            FakeDriver(),  # type: ignore[arg-type]
            checklist,
            preview_bounds={"x0": 0, "x1": 100, "y0": 0, "y1": 50},
        )
        self.assertFalse(audit["audit_pass"])
        self.assertIn("semantic_too_sparse", audit["audit_failures"])

    def test_run_audit_merges_visual_parts_summary_for_forbidden_patterns(self) -> None:
        class FakeEnt:
            def __init__(self) -> None:
                self.Layer = "CODEX_PREVIEW"
                self.Handle = "H1"
                self.StartPoint = [0, 50, 0]
                self.EndPoint = [100, 50, 0]

        class FakeMs:
            Count = 1

            def Item(self, i: int) -> FakeEnt:
                return FakeEnt()

        class FakeDriver:
            model_space = FakeMs()

        checklist = {
            "schema_version": 2,
            "case_id": "test",
            "checks": {
                "semantic": {
                    "forbidden_patterns": [
                        "split_as_backrest",
                        "missing_required_parts",
                        "rounded_rect_only_parts",
                        "part_connection_defects",
                    ],
                    "visual_parts_summary": {
                        "required_part_count": 7,
                        "closed_part_count": 5,
                        "seat_cushion_count": 2,
                        "back_cushion_count": 0,
                        "full_width_split_count": 1,
                        "rounded_rect_family_count": 7,
                        "distinct_shape_family_count": 1,
                        "part_gap_count": 1,
                        "part_overlap_count": 0,
                    },
                },
                "cleanliness": {"entity_total_max": 5},
            },
        }

        audit = run_training_geometry_audit(
            FakeDriver(),  # type: ignore[arg-type]
            checklist,
            preview_bounds={"x0": 0, "x1": 100, "y0": 0, "y1": 100},
        )

        self.assertIn("split_as_backrest", audit["forbidden_pattern_hits"])
        self.assertIn("missing_required_parts", audit["forbidden_pattern_hits"])
        self.assertIn("rounded_rect_only_parts", audit["forbidden_pattern_hits"])
        self.assertIn("part_connection_defects", audit["forbidden_pattern_hits"])
        self.assertIn("forbidden_split_as_backrest", audit["audit_failures"])
        self.assertIn("forbidden_missing_required_parts", audit["audit_failures"])
        self.assertIn("forbidden_rounded_rect_only_parts", audit["audit_failures"])
        self.assertIn("forbidden_part_connection_defects", audit["audit_failures"])

    def test_load_checklist_from_template_shape(self) -> None:
        checklist = load_training_audit_checklist(
            __import__("pathlib").Path("projects/residential_training_template/expected/audit_checklist.template.json")
        )
        self.assertEqual(checklist.get("schema_version"), 2)
        self.assertIn("semantic", checklist.get("checks", {}))


if __name__ == "__main__":
    unittest.main()
