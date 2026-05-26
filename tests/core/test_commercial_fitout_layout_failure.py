from __future__ import annotations

import unittest

from core.composition_engine.templates import create_composition_spec
from core.layout_engine.commercial_fitout_layout_failure import (
    evaluate_fitout_composition_layout_failure,
    evaluate_main_aisle_conflict,
    evaluate_meeting_seating_conflict,
)


class CommercialFitoutLayoutFailureTests(unittest.TestCase):
    def test_reception_entry_conflict_is_blocked(self) -> None:
        composition = create_composition_spec("fitout_reception_entry_conflict")
        result = evaluate_fitout_composition_layout_failure(composition)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["failure_category"], "entry_clearance_conflict")

    def test_file_cabinet_front_conflict_is_blocked(self) -> None:
        composition = create_composition_spec("fitout_file_cabinet_front_conflict")
        result = evaluate_fitout_composition_layout_failure(composition)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["failure_category"], "clearance_conflict")

    def test_main_aisle_conflict_is_blocked(self) -> None:
        composition = create_composition_spec("fitout_main_aisle_conflict")
        result = evaluate_main_aisle_conflict(composition)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["failure_category"], "circulation_conflict")

    def test_meeting_seating_conflict_is_blocked(self) -> None:
        composition = create_composition_spec("fitout_meeting_seating_conflict")
        result = evaluate_meeting_seating_conflict(composition)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["failure_category"], "insufficient_space")

    def test_open_office_success_is_not_blocked(self) -> None:
        composition = create_composition_spec("fitout_open_office_desk_chair")
        result = evaluate_fitout_composition_layout_failure(composition)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
