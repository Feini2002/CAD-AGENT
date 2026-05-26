from __future__ import annotations

import json
import shutil
import unittest

from core.verification.cad_beta_evidence_rollup import (
    PARENT_PACKAGE_ID,
    VERIFICATION_DOC_NAMES,
    run_cad_beta_evidence_rollup,
)
from core.verification.evidence_contract import NON_CAD_GEOMETRY_ACCURACY
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class CadBetaBlockAcceptanceTests(unittest.TestCase):
    def test_beta_cad_block_05_verification_doc_bundle_exists(self) -> None:
        verification_root = PROJECT_ROOT / "docs" / "verification"
        for name in VERIFICATION_DOC_NAMES:
            with self.subTest(doc=name):
                self.assertTrue((verification_root / name).is_file(), name)

    def test_beta_cad_block_05_acceptance_doc_states_claims_and_limits(self) -> None:
        text = (PROJECT_ROOT / "docs" / "verification" / "beta_cad_block_acceptance.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("现在可以声称什么", text)
        self.assertIn("不能声称什么", text)
        self.assertIn("geometry_verified", text)
        self.assertIn("BETA-CAD-BLOCK-01", text)

    def test_beta_cad_block_05_rollup_all_subpackages_pass_non_cad_only(self) -> None:
        output_root = artifact_path("cad_beta_evidence", "beta_cad_block_05")
        report = run_cad_beta_evidence_rollup(PROJECT_ROOT, output_root=output_root)

        self.assertEqual(report["parent_package_id"], PARENT_PACKAGE_ID)
        self.assertEqual(report["status"], "pass", report)
        self.assertEqual(report["summary"]["subpackage_passed"], 5)
        self.assertEqual(report["summary"]["subpackage_failed"], 0)

        evidence = report["evidence_summary"]
        self.assertEqual(evidence["geometry_verified_count"], 0)
        self.assertEqual(evidence["readback_geometry_verified_count"], 0)
        self.assertTrue(evidence["non_cad_only"])
        self.assertEqual(evidence["geometry_accuracy"], NON_CAD_GEOMETRY_ACCURACY)

        sub_ids = {item["subpackage_id"] for item in report["subpackages"]}
        self.assertEqual(
            sub_ids,
            {
                "BETA-CAD-BLOCK-01",
                "BETA-CAD-BLOCK-02",
                "BETA-CAD-BLOCK-03",
                "BETA-CAD-BLOCK-04",
                "BETA-CAD-BLOCK-05",
            },
        )
        self.assertTrue(all(item["status"] == "pass" for item in report["subpackages"]))

        rollup_path = output_root / "cad_beta_evidence_rollup.json"
        self.assertTrue(rollup_path.is_file())
        saved = json.loads(rollup_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "pass")
        self.assertGreater(len(saved["claims"]["forbidden"]), 0)

    def test_beta_cad_block_05_rejects_output_root_outside_project_output(self) -> None:
        output_root = PROJECT_ROOT / "tests" / "outside_cad_beta_rollup"
        try:
            with self.assertRaisesRegex(ValueError, "output_root"):
                run_cad_beta_evidence_rollup(PROJECT_ROOT, output_root=output_root)
        finally:
            if output_root.exists():
                shutil.rmtree(output_root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
