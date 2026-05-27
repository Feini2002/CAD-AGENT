from __future__ import annotations

import json
import unittest

from tests.helpers import artifact_path

from core.verification.fake_cad_driver import FakeCadDriver
from core.verification.visual_cad_smoke import run_visual_cad_smoke


class VisualCadSmokeTests(unittest.TestCase):
    def test_fake_driver_draws_richer_office_corner(self) -> None:
        output_dir = artifact_path("visual_cad_smoke", "fake")
        report = run_visual_cad_smoke(
            output_dir=output_dir,
            driver_factory=FakeCadDriver,
            base_point=[180000, 90000, 0],
        )

        self.assertEqual(report["status"], "visual_geometry_verified")
        self.assertTrue(report["geometry_verified"])
        self.assertGreaterEqual(report["created_handle_count"], 42)
        self.assertGreaterEqual(report["visual_detail_score_percent"], 70)
        self.assertEqual(report["safety"]["layer"], "CODEX_PREVIEW")
        self.assertFalse(report["safety"]["saved_dwg"])
        self.assertFalse(report["safety"]["deleted_entities"])
        self.assertFalse(report["safety"]["modified_formal_layers"])

        type_counts = report["actual"]["type_counts"]
        self.assertGreaterEqual(type_counts.get("line", 0), 28)
        self.assertGreaterEqual(type_counts.get("circle", 0), 2)
        self.assertGreaterEqual(type_counts.get("arc", 0), 1)
        self.assertGreaterEqual(type_counts.get("polyline", 0), 2)

        saved_report = output_dir / "visual_cad_smoke_report.json"
        self.assertTrue(saved_report.is_file())
        self.assertEqual(json.loads(saved_report.read_text(encoding="utf-8"))["status"], "visual_geometry_verified")


if __name__ == "__main__":
    unittest.main()
