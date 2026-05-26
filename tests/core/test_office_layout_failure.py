from __future__ import annotations

import unittest

from core.composition_engine.templates import create_composition_spec
from core.layout_engine.office_layout_failure import (
    evaluate_blank_shell_layout_expectation,
    evaluate_composition_layout_failure,
)


class OfficeLayoutFailureTests(unittest.TestCase):
    def test_door_clearance_conflict_is_blocked(self) -> None:
        composition = create_composition_spec("door_clearance_conflict")
        result = evaluate_composition_layout_failure(composition)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["failure_category"], "entry_clearance_conflict")
        self.assertTrue(any("entry_clearance_conflict" in item for item in result["blocked_reasons"]))

    def test_cabinet_pullback_conflict_is_blocked(self) -> None:
        composition = create_composition_spec("cabinet_pullback_conflict")
        result = evaluate_composition_layout_failure(composition)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["failure_category"], "clearance_conflict")
        self.assertTrue(any("clearance_conflict" in item for item in result["blocked_reasons"]))

    def test_require_all_placed_expectation_blocks_partial_layout(self) -> None:
        workflow = {
            "layout_expectation": {
                "mode": "require_all_placed",
                "failure_category": "insufficient_space",
            }
        }
        placements = [
            {"status": "placed", "failure_reasons": []},
            {
                "status": "blocked",
                "failure_reasons": ["insufficient remaining zone space for placement."],
            },
        ]
        result = evaluate_blank_shell_layout_expectation(workflow, placements=placements)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["failure_category"], "insufficient_space")


if __name__ == "__main__":
    unittest.main()
