from __future__ import annotations

import unittest

from core.p4_core_wave import (
    P4_ACCEPTANCE_DOC,
    P4_BOUNDARY_DOCS,
    P4_WAVE_PACKAGE_IDS,
    assert_p4_core_wave_contract,
    p4_core_wave_status_summary,
)
from core.symbol_engine.block_first_tier import (
    default_manifest_path as block_first_manifest_path,
    run_block_first_tier_smoke,
)
from core.verification.drawing_standard_beta_suite import default_suite_path, run_drawing_standard_beta_suite
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class P4CoreWaveParentRollupTests(unittest.TestCase):
    def test_p4_wave_contract(self) -> None:
        assert_p4_core_wave_contract(project_root=PROJECT_ROOT)

    def test_p4_wave_status_summary(self) -> None:
        summary = p4_core_wave_status_summary(project_root=PROJECT_ROOT)
        self.assertTrue(summary["docs_present"])
        self.assertEqual(summary["child_package_count"], 4)
        self.assertEqual(len(summary["package_ids"]), 4)

    def test_acceptance_doc_closes_p4_wave(self) -> None:
        text = (PROJECT_ROOT / P4_ACCEPTANCE_DOC).read_text(encoding="utf-8")
        for short_id in ("DRAW-01", "DRAW-02", "SYMBOL-08", "SYMBOL-09", "CORE-P4"):
            with self.subTest(short_id=short_id):
                self.assertIn(short_id, text)
        for phrase in (
            "CORE-P4-WAVE-PARENT-ROLLUP",
            "assert_p4_core_wave_contract",
            "symbol-fallback-policy-01",
            "dry_run_valid_plan_only",
            "V-PROOF-44",
            "V-PROOF-34",
            "V-PROOF-35",
            "geometry_verified",
            "不得声称",
            "silent_degradation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_all_boundary_docs_exist(self) -> None:
        for rel in P4_BOUNDARY_DOCS:
            with self.subTest(doc=rel):
                self.assertTrue((PROJECT_ROOT / rel).is_file())

    def test_p4_no_cad_draw_and_block_first_rerun(self) -> None:
        draw = run_drawing_standard_beta_suite(
            default_suite_path(PROJECT_ROOT),
            output_root=artifact_path("p4_core", "draw_beta_no_cad"),
        )
        self.assertEqual(draw["status"], "pass")
        self.assertEqual(draw["summary"], {"total": 6, "passed": 6, "failed": 0})

        block_first = run_block_first_tier_smoke(
            block_first_manifest_path(PROJECT_ROOT),
            output_root=artifact_path("p4_core", "block_first_no_cad"),
        )
        self.assertEqual(block_first["status"], "pass")
        self.assertEqual(block_first["summary"]["passed"], 3)

    def test_handoff_indexes_p4_core_wave(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("CORE-P4", handoff)
        self.assertIn("p4_core_wave_acceptance.md", handoff)


if __name__ == "__main__":
    unittest.main()
