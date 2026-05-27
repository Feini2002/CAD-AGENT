from __future__ import annotations

import unittest
from pathlib import Path

from core.safety.policy import PREVIEW_LAYER
from core.safety.write_guard import CadWriteGuardViolation
from core.verification.fake_cad_driver import FakeCadDriver


class HatchComDeferredBoundaryTests(unittest.TestCase):
    def test_fake_driver_hatch_returns_deferred_and_creates_no_entities(self) -> None:
        driver = FakeCadDriver()

        result = driver.draw_hatch(
            boundary_points=[[0, 0], [120, 0], [120, 80], [0, 80]],
            pattern="ANSI31",
            layer=PREVIEW_LAYER,
            layer_role="preview",
        )

        self.assertEqual(result["primitive"], "hatch")
        self.assertEqual(result["status"], "deferred")
        self.assertEqual(result["failure_category"], "hatch_unverified")
        self.assertEqual(result["created_handles"], [])
        self.assertIs(result["geometry_verified"], False)
        self.assertEqual(driver.entities, {})

    def test_fake_driver_hatch_still_uses_preview_write_guard(self) -> None:
        driver = FakeCadDriver()

        with self.assertRaises(CadWriteGuardViolation):
            driver.draw_hatch(
                boundary_points=[[0, 0], [120, 0], [120, 80], [0, 80]],
                layer="WALL",
            )

        self.assertEqual(driver.entities, {})

    def test_boundary_doc_names_structured_deferred_contract(self) -> None:
        text = Path("docs/verification/hatch_com_deferred_boundary.md").read_text(encoding="utf-8")

        required_terms = [
            "LCAD-12-HATCH-COM",
            "draw_hatch",
            "structured deferred",
            "hatch_unverified",
            "created_handles=[]",
            "geometry_verified=false",
            "V-PROOF-53",
        ]
        for term in required_terms:
            self.assertIn(term, text)


if __name__ == "__main__":
    unittest.main()
