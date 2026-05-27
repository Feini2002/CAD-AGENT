from __future__ import annotations

import unittest
from pathlib import Path

from core.agents.commercial_fitout_p2_wave import (
    P2_ACCEPTANCE_DOC,
    P2_BOUNDARY_DOCS,
    P2_WAVE_PACKAGE_IDS,
    assert_commercial_fitout_p2_wave_contract,
    p2_wave_status_summary,
)
from core.verification.fitout_subscene_object_cad_smoke import (
    run_fitout_subscene_object_cad_smoke,
)
from core.verification.fake_cad_driver import FakeCadDriver
from core.project_samples.project_sample_cad_rollup import run_project_sample_cad_rollup
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Cfit13P2WaveParentRollupTests(unittest.TestCase):
    def test_p2_wave_contract(self) -> None:
        assert_commercial_fitout_p2_wave_contract(project_root=PROJECT_ROOT)

    def test_p2_wave_status_summary(self) -> None:
        summary = p2_wave_status_summary(project_root=PROJECT_ROOT)
        self.assertTrue(summary["docs_present"])
        self.assertEqual(summary["fitout_sample_count"], 3)
        self.assertEqual(len(summary["package_ids"]), 4)

    def test_acceptance_doc_closes_p2_wave(self) -> None:
        text = (PROJECT_ROOT / P2_ACCEPTANCE_DOC).read_text(encoding="utf-8")
        for short_id in ("CFIT-09", "CFIT-10", "CFIT-11", "CFIT-12", "CFIT-13"):
            with self.subTest(short_id=short_id):
                self.assertIn(short_id, text)
        for phrase in (
            "CFIT-13",
            "assert_commercial_fitout_p2_wave_contract",
            "不得声称",
            "V-PROOF-25",
            "RCAD-18",
            "RCAD-19",
            "geometry_verified",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_all_boundary_docs_exist(self) -> None:
        for rel in P2_BOUNDARY_DOCS:
            with self.subTest(doc=rel):
                self.assertTrue((PROJECT_ROOT / rel).is_file())

    def test_p2_no_cad_rollup_and_subscene_smoke(self) -> None:
        rollup = run_project_sample_cad_rollup(
            artifact_path("cfit_13", "rollup_no_cad"),
            project_root=PROJECT_ROOT,
            driver=FakeCadDriver(),
        )
        self.assertTrue(rollup["geometry_verified"])
        self.assertEqual(rollup["geometry_verified_count"], 4)

        smoke = run_fitout_subscene_object_cad_smoke(
            root=PROJECT_ROOT,
            output_dir=artifact_path("cfit_13", "subscene_smoke_no_cad"),
            driver=FakeCadDriver(),
        )
        self.assertTrue(smoke["geometry_verified"])
        self.assertEqual(smoke["geometry_verified_object_count"], 4)

    def test_handoff_indexes_cfit_13(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("CFIT-13", handoff)
        self.assertIn("commercial_fitout_p2_wave_acceptance.md", handoff)


if __name__ == "__main__":
    unittest.main()
