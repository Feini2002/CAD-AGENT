from __future__ import annotations

import unittest

from core.verification.fake_cad_driver import FakeCadDriver
from core.verification.intent_lab_cad import run_intent_lab_cad_suite
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class IntentLabCadTests(unittest.TestCase):
    def test_fake_cad_executes_cad_enabled_intents(self) -> None:
        output_dir = artifact_path("intent_lab_cad", "fake")
        report = run_intent_lab_cad_suite(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            no_cad=False,
            driver_factory=FakeCadDriver,
        )
        self.assertEqual(report["status"], "geometry_verified")
        cad_rows = [row for row in report["intents"] if row.get("cad_execution_status") == "executed"]
        self.assertGreaterEqual(len(cad_rows), 3)
        glyph = next(row for row in report["intents"] if row["intent"] == "draw_symbol_glyph")
        self.assertEqual(glyph["cad_execution_status"], "executed")


if __name__ == "__main__":
    unittest.main()
