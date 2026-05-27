from __future__ import annotations

import unittest

from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
)
from core.verification.geometry_checks import expected_block_reference_from_plan
from core.verification.symbol_block_first_cad_smoke import (
    BLOCK_FIRST_VERIFIED_CASE_ID,
    RCAD_25_PACKAGE_ID,
    V_PROOF_34_PACKAGE_ID,
    run_symbol_block_first_cad_smoke,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class _BlockFirstCadSmokeDriver:
    def __init__(self) -> None:
        self.created_handles: list[str] = []

    def insert_block_alpha(self, **_: object) -> dict[str, str]:
        self.created_handles = ["BR25"]
        return {"handle": "BR25"}

    def snapshot_handles(self, *, handles: list[str], layer: str | None = None) -> list[dict[str, object]]:
        plan_path = PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json"
        import json

        plan = json.loads(plan_path.read_text(encoding="utf-8"))
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


class SymbolBlockFirstCadSmokeTests(unittest.TestCase):
    def test_no_cad_report_is_deferred_and_does_not_upgrade_rows(self) -> None:
        output_dir = artifact_path("rcad_25", "no_cad")
        report = run_symbol_block_first_cad_smoke(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            no_cad=True,
        )
        self.assertEqual(report["package_id"], RCAD_25_PACKAGE_ID)
        self.assertEqual(report["paired_package_id"], V_PROOF_34_PACKAGE_ID)
        self.assertEqual(report["status"], "deferred")
        self.assertEqual(report["evidence_state"], EVIDENCE_DEFERRED_CAD_READBACK)
        self.assertEqual(report["geometry_accuracy"], NON_CAD_GEOMETRY_ACCURACY)
        self.assertFalse(report["geometry_verified"])
        self.assertEqual(report["verified_capability_ids"], [])
        self.assertEqual(len(report["fallback_cases_not_upgraded"]), 2)

    def test_real_cad_report_contract_with_controlled_driver(self) -> None:
        output_dir = artifact_path("rcad_25", "controlled_driver")
        report = run_symbol_block_first_cad_smoke(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            driver_factory=_BlockFirstCadSmokeDriver,
        )
        self.assertEqual(report["status"], "geometry_verified")
        self.assertEqual(report["evidence_state"], EVIDENCE_READBACK_GEOMETRY_VERIFIED)
        self.assertEqual(report["geometry_accuracy"], GEOMETRY_VERIFIED_BY_READBACK)
        self.assertEqual(report["block_first_case_id"], BLOCK_FIRST_VERIFIED_CASE_ID)
        self.assertEqual(report["selected_cad_intent"], "insert_block_alpha")
        self.assertIn("symbol.block_first.symbol_block_first_tier_01", report["verified_capability_ids"])
        self.assertIn("symbol.block_first.controlled_block_wins", report["verified_capability_ids"])
        self.assertNotIn(
            "symbol.block_first.metadata_only_block_falls_to_glyph",
            report["verified_capability_ids"],
        )
        self.assertTrue((output_dir / "symbol_block_first_cad_smoke_report.json").is_file())
        self.assertTrue((output_dir / "block_alpha_report.json").is_file())


if __name__ == "__main__":
    unittest.main()
