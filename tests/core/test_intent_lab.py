from __future__ import annotations

import unittest
from pathlib import Path

from tests.bootstrap import PROJECT_ROOT

from core.plan_engine.validate_plan import ALLOWED_INTENTS
from core.verification.intent_lab import run_intent_lab_inventory


class IntentLabTests(unittest.TestCase):
    def test_intent_inventory_covers_all_allowed_intents(self) -> None:
        report = run_intent_lab_inventory(root=PROJECT_ROOT)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(set(report["manifest_intents"]), set(ALLOWED_INTENTS))
        self.assertEqual(len(report["intents"]), len(ALLOWED_INTENTS))

    def test_each_intent_minimal_plan_validates(self) -> None:
        report = run_intent_lab_inventory(root=PROJECT_ROOT)
        for row in report["intents"]:
            with self.subTest(intent=row["intent"]):
                self.assertEqual(row["validate_status"], "pass", msg=row.get("validate_errors"))
