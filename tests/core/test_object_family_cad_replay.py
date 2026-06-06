from __future__ import annotations

import json
import unittest

from core.assets.object_family_cad_replay import run_object_family_cad_replay
from core.verification.evidence_contract import EVIDENCE_READBACK_GEOMETRY_VERIFIED
from core.verification.fake_cad_driver import FakeCadDriver
from tests.helpers import temporary_artifact_dir


class ObjectFamilyCadReplayTests(unittest.TestCase):
    def test_sofa_replay_verifies_fake_cad_readback(self) -> None:
        with temporary_artifact_dir("object_family_cad_replay") as output_dir:
            report = run_object_family_cad_replay(
                "sofa object family replay",
                driver_factory=FakeCadDriver,
                output_dir=output_dir,
                base_point=[62000.0, 36000.0, 0.0],
            )

            self.assertEqual(report["status"], "geometry_verified", report)
            self.assertTrue(report["geometry_verified"])
            self.assertEqual(report["evidence_state"], EVIDENCE_READBACK_GEOMETRY_VERIFIED)
            self.assertEqual(report["layer"], "CODEX_PREVIEW")
            self.assertEqual(report["created_handle_count"], 17)
            self.assertEqual(report["actual"]["entity_count"], 17)
            self.assertEqual(report["actual"]["type_counts"], {"line": 17})
            self.assertEqual(report["actual"]["layer_counts"], {"CODEX_PREVIEW": 17})
            self.assertEqual(len(report["actual"]["entities"]), 17)
            self.assertEqual(report["execution_summary"]["target_bbox"]["min"], [62000.0, 36100.0])
            self.assertEqual(report["screenshot_role"], "not_applicable")
            self.assertFalse(report["savedCurrentDwg"])

            summary_path = output_dir / "execution_summary.json"
            replay_path = output_dir / "object_family_cad_replay_report.json"
            self.assertTrue(summary_path.is_file())
            self.assertTrue(replay_path.is_file())
            persisted = json.loads(replay_path.read_text(encoding="utf-8"))
            self.assertEqual(persisted["status"], "geometry_verified")

    def test_replay_reports_cad_connection_blocker(self) -> None:
        def blocked_driver() -> FakeCadDriver:
            raise RuntimeError("no active cad")

        with temporary_artifact_dir("object_family_cad_blocked") as output_dir:
            report = run_object_family_cad_replay(
                "sofa object family replay",
                driver_factory=blocked_driver,
                output_dir=output_dir,
            )

            self.assertEqual(report["status"], "external_blocker")
            self.assertEqual(report["failure_category"], "cad_connection_failed")
            self.assertFalse(report["geometry_verified"])
            self.assertEqual(report["created_handles"], [])
            self.assertTrue((output_dir / "object_family_cad_replay_report.json").is_file())


if __name__ == "__main__":
    unittest.main()
