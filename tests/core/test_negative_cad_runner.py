from __future__ import annotations

import json
import unittest

from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path

from core.verification.negative_cad_runner import run_negative_cad_runner


class NegativeCadRunnerTests(unittest.TestCase):
    def test_fake_driver_negative_runner_proves_no_handles_or_saves(self) -> None:
        output_dir = artifact_path("negative_cad_runner", "fake")
        report = run_negative_cad_runner(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            use_real_cad=False,
        )

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["evidence_state"], "negative_guard_verified")
        self.assertEqual(report["created_handles"], [])
        self.assertEqual(report["negative_cad_plans"]["status"], "pass")
        self.assertEqual(report["write_guard"]["status"], "pass")
        self.assertEqual(report["safety"]["saved_dwg"], False)
        self.assertEqual(report["safety"]["deleted_entities"], False)
        self.assertEqual(report["safety"]["modified_formal_layers"], False)
        self.assertEqual(report["session_guard"]["comparison"]["preview_layer_entity_delta"], 0)
        self.assertEqual(report["session_guard"]["comparison"]["modelspace_entity_delta"], 0)

        saved = output_dir / "negative_cad_runner_report.json"
        self.assertTrue(saved.is_file())
        on_disk = json.loads(saved.read_text(encoding="utf-8"))
        self.assertEqual(on_disk["suite_id"], "negative_cad_runner")


if __name__ == "__main__":
    unittest.main()
