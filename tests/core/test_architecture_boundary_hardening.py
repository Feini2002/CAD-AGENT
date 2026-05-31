from __future__ import annotations

import unittest

from tests.bootstrap import PROJECT_ROOT


BOUNDARY_DOC = PROJECT_ROOT / "docs" / "architecture" / "current-module-boundaries.md"


class ArchitectureBoundaryHardeningTests(unittest.TestCase):
    def test_boundary_snapshot_is_discoverable(self) -> None:
        readme = (PROJECT_ROOT / "docs" / "architecture" / "README.md").read_text(
            encoding="utf-8"
        )

        self.assertTrue(BOUNDARY_DOC.is_file())
        self.assertIn("current-module-boundaries.md", readme)

    def test_boundary_snapshot_declares_three_code_buckets(self) -> None:
        text = BOUNDARY_DOC.read_text(encoding="utf-8")

        for marker in [
            "ARCH-BOUNDARY-HARDENING-01",
            "Stable Core",
            "Training Experiments",
            "Case-Only",
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_boundary_snapshot_covers_requested_split_maps(self) -> None:
        text = BOUNDARY_DOC.read_text(encoding="utf-8")

        for marker in [
            "Verification Split Map",
            "report contract",
            "runner",
            "registry writeback",
            "visual audit",
            "Capability Map Split Map",
            "data generator",
            "page shell",
            "display configuration",
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_boundary_snapshot_names_asset_trial_and_case_promotion_gate(self) -> None:
        text = BOUNDARY_DOC.read_text(encoding="utf-8")

        for marker in [
            "Object Asset Trial",
            "residential_sofa_2seat_20260528",
            "raw reference -> knowledge summary -> candidate -> executable check -> system asset -> CAD_PLAN -> readback",
            "Case-Run Promotion Gate",
            "projects/.../runs",
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_openspec_change_does_not_become_second_roadmap(self) -> None:
        text = BOUNDARY_DOC.read_text(encoding="utf-8")

        self.assertIn("CORE_RESTRUCTURE_PLAN.md", text)
        self.assertIn("not a second roadmap", text)
