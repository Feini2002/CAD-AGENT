from __future__ import annotations

import json
import unittest

from core.verification.drawing_standard_cad_smoke import (
    DRAWING_STANDARD_BLOCK_CASE_ID,
    RCAD_23_PACKAGE_ID,
    V_PROOF_44_PACKAGE_ID,
    materialize_drawing_standard_block_plan,
    run_drawing_standard_cad_smoke,
)
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
)
from core.verification.geometry_checks import expected_block_reference_from_plan
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class _DrawingStandardCadSmokeDriver:
    def insert_block_alpha(self, **_: object) -> dict[str, str]:
        return {"handle": "DS23"}

    def snapshot_handles(self, *, handles: list[str], layer: str | None = None) -> list[dict[str, object]]:
        plan = materialize_drawing_standard_block_plan(root=PROJECT_ROOT)
        expected = expected_block_reference_from_plan(plan)
        return [
            {
                "handle": handle,
                "type": "block_reference",
                "layer": layer or "CODEX_PREVIEW",
                **expected,
            }
            for handle in handles
        ]


class DrawingStandardCadSmokeTests(unittest.TestCase):
    def test_materialized_plan_applies_preview_profile(self) -> None:
        plan = materialize_drawing_standard_block_plan(root=PROJECT_ROOT)
        self.assertEqual(plan["intent"], "insert_block_alpha")
        self.assertEqual(plan["drawing"]["layer"], "CODEX_PREVIEW")
        self.assertEqual(plan["drawing"]["layer_role"], "preview")
        self.assertEqual(plan["placement"]["base_point"], [1800, 900, 0])

    def test_no_cad_report_is_deferred_and_does_not_upgrade_cases(self) -> None:
        output_dir = artifact_path("rcad_23", "no_cad")
        report = run_drawing_standard_cad_smoke(root=PROJECT_ROOT, output_dir=output_dir, no_cad=True)
        self.assertEqual(report["package_id"], RCAD_23_PACKAGE_ID)
        self.assertEqual(report["paired_package_id"], V_PROOF_44_PACKAGE_ID)
        self.assertEqual(report["status"], "deferred")
        self.assertEqual(report["evidence_state"], EVIDENCE_DEFERRED_CAD_READBACK)
        self.assertEqual(report["geometry_accuracy"], NON_CAD_GEOMETRY_ACCURACY)
        self.assertFalse(report["geometry_verified"])
        self.assertEqual(report["verified_capability_ids"], [])
        self.assertEqual(len(report["non_cad_cases_not_upgraded"]), 5)

    def test_real_cad_report_contract_with_controlled_driver(self) -> None:
        output_dir = artifact_path("rcad_23", "controlled_driver")
        report = run_drawing_standard_cad_smoke(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            driver_factory=_DrawingStandardCadSmokeDriver,
        )
        self.assertEqual(report["status"], "geometry_verified")
        self.assertEqual(report["evidence_state"], EVIDENCE_READBACK_GEOMETRY_VERIFIED)
        self.assertEqual(report["geometry_accuracy"], GEOMETRY_VERIFIED_BY_READBACK)
        self.assertEqual(report["block_case_id"], DRAWING_STANDARD_BLOCK_CASE_ID)
        self.assertIn("drawing_standard.beta.drawing_standard_beta_04", report["verified_capability_ids"])
        self.assertIn("drawing_standard.beta.block_insert_plan_resolution", report["verified_capability_ids"])
        self.assertNotIn("drawing_standard.beta.primitive_text_style", report["verified_capability_ids"])

        saved = json.loads((output_dir / "drawing_standard_cad_smoke_report.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "geometry_verified")
        self.assertTrue((output_dir / "block_alpha_report.json").is_file())


if __name__ == "__main__":
    unittest.main()
