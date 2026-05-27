from __future__ import annotations

import unittest
from pathlib import Path

from core.agents.commercial_fitout_product_boundary import (
    assert_fitout_three_sample_rollup_sync,
    assert_product_boundary_contract,
    load_product_alpha_boundary,
)
from core.agents.commercial_fitout_scope import PRIMARY_SUBSCENE_IDS
from core.agents.fitout_sample_specs import FITOUT_SAMPLE_SPECS, fitout_subscene_to_sample_id
from core.project_samples.project_sample_cad_rollup import (
    load_project_sample_cad_manifest,
    run_project_sample_cad_rollup,
)
from core.verification.fake_cad_driver import FakeCadDriver
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Cfit11ThreeSampleBoundarySyncTests(unittest.TestCase):
    def test_fitout_specs_align_with_primary_subscenes(self) -> None:
        mapping = fitout_subscene_to_sample_id()
        self.assertEqual(set(mapping), PRIMARY_SUBSCENE_IDS)
        self.assertEqual(len(FITOUT_SAMPLE_SPECS), 3)

    def test_product_boundary_three_sample_rollup_sync(self) -> None:
        boundary = load_product_alpha_boundary()
        assert_fitout_three_sample_rollup_sync(boundary=boundary, project_root=PROJECT_ROOT)
        assert_product_boundary_contract(boundary)

    def test_manifest_lists_all_fitout_samples(self) -> None:
        manifest = load_project_sample_cad_manifest(project_root=PROJECT_ROOT)
        manifest_ids = {entry["sample_id"] for entry in manifest["samples"]}
        for spec in FITOUT_SAMPLE_SPECS.values():
            self.assertIn(spec.sample_id, manifest_ids)

    def test_rollup_fake_four_of_four_geometry_verified(self) -> None:
        output_dir = artifact_path("cfit_11", "rollup_fake_sync")
        rollup = run_project_sample_cad_rollup(
            output_dir,
            project_root=PROJECT_ROOT,
            driver=FakeCadDriver(),
        )
        self.assertEqual(rollup["geometry_verified_count"], 4, rollup)
        self.assertTrue(rollup["geometry_verified"])

    def test_boundary_doc_names_cfit_11_contract(self) -> None:
        text = Path("docs/verification/cfit_11_three_sample_product_boundary_sync.md").read_text(encoding="utf-8")
        self.assertIn("CFIT-11-THREE-SAMPLE-BOUNDARY-SYNC", text)
        self.assertIn("deidentified_project_samples", text)
        self.assertIn("RCAD-10", text)


if __name__ == "__main__":
    unittest.main()
