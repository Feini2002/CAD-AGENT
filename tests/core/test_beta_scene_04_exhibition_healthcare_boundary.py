from __future__ import annotations

import unittest
from pathlib import Path

from core.agents.exhibition_scene_beta import run_exhibition_scene_beta_benchmark
from core.agents.healthcare_scene_beta import run_healthcare_scene_beta_benchmark
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class BetaScene04ExhibitionHealthcareBoundaryTests(unittest.TestCase):
    def test_beta_scene_04_package_rollup_passes(self) -> None:
        exhibition = run_exhibition_scene_beta_benchmark(
            project_root=PROJECT_ROOT,
            output_root=artifact_path("benchmarks", "beta_scene_04_boundary_exhibition"),
        )
        healthcare = run_healthcare_scene_beta_benchmark(
            project_root=PROJECT_ROOT,
            output_root=artifact_path("benchmarks", "beta_scene_04_boundary_healthcare"),
        )
        self.assertEqual(exhibition["status"], "pass", exhibition)
        self.assertEqual(healthcare["status"], "pass", healthcare)
        self.assertEqual(exhibition["evidence_summary"]["non_cad_only"], True)
        self.assertEqual(healthcare["evidence_summary"]["non_cad_only"], True)

    def test_beta_scene_04_boundary_doc_exists(self) -> None:
        doc = PROJECT_ROOT / "docs/verification/beta_scene_04_exhibition_healthcare_boundaries.md"
        self.assertTrue(doc.is_file(), f"missing boundary doc: {doc}")
        text = doc.read_text(encoding="utf-8")
        self.assertIn("BETA-SCENE-04", text)
        self.assertIn("exhibition", text)
        self.assertIn("healthcare", text)


if __name__ == "__main__":
  unittest.main()
