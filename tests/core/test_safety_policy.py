from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.safety.policy import assert_plan_is_safe, evaluate_plan_safety


def sample_plan(*, layer: str = "CODEX_PREVIEW", needs_confirmation: bool = False, intent: str = "draw_object") -> dict[str, object]:
    return {
        "version": "0.1",
        "domain": "generic",
        "intent": intent,
        "object": {"type": "cabinet", "name": "Safe Cabinet", "width": 1800, "depth": 600},
        "placement": {"mode": "absolute", "base_point": [0, 0, 0]},
        "drawing": {"layer": layer, "include_label": True, "include_dimensions": True},
        "confidence": 0.9,
        "needs_confirmation": needs_confirmation,
    }


class SafetyPolicyTests(unittest.TestCase):
    def test_preview_plan_is_allowed_by_default(self) -> None:
        decision = evaluate_plan_safety(sample_plan())

        self.assertTrue(decision["allowed"])
        self.assertEqual(decision["violations"], [])
        self.assertIn("CODEX_PREVIEW", decision["summary"])

    def test_formal_layer_requires_explicit_approval(self) -> None:
        decision = evaluate_plan_safety(sample_plan(layer="A-FURN"))

        self.assertFalse(decision["allowed"])
        self.assertIn("formal_layer_requires_approval", decision["violations"])

        approved = evaluate_plan_safety(
            sample_plan(layer="A-FURN"),
            approval={"allow_formal_layer": True, "approved_by": "user"},
        )
        self.assertTrue(approved["allowed"])

    def test_unconfirmed_plan_is_blocked_without_approval(self) -> None:
        decision = evaluate_plan_safety(sample_plan(needs_confirmation=True))

        self.assertFalse(decision["allowed"])
        self.assertIn("plan_needs_confirmation", decision["violations"])

    def test_delete_or_save_operations_are_blocked_by_default(self) -> None:
        delete_decision = evaluate_plan_safety(sample_plan(intent="delete_object"))
        save_decision = evaluate_plan_safety(sample_plan(), requested_operation="save")

        self.assertIn("delete_requires_approval", delete_decision["violations"])
        self.assertIn("save_requires_approval", save_decision["violations"])

    def test_assert_plan_is_safe_raises_readable_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "formal_layer_requires_approval"):
            assert_plan_is_safe(sample_plan(layer="A-FURN"))


if __name__ == "__main__":
    unittest.main()
