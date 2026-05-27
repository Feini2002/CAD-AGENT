from __future__ import annotations

import unittest
from pathlib import Path

from core.agents.commercial_fitout_scope import PRIMARY_SUBSCENE_IDS
from core.agents.fitout_sample_specs import fitout_subscene_to_sample_id
from core.verification.fake_cad_driver import FakeCadDriver
from core.verification.fitout_subscene_object_cad_smoke import (
    assert_fitout_subscene_object_manifest_contract,
    load_fitout_subscene_object_cad_smoke_manifest,
    run_fitout_subscene_object_cad_smoke,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Cfit12FitoutSubsceneObjectCadSmokeTests(unittest.TestCase):
    def test_manifest_contract(self) -> None:
        manifest_path = (
            PROJECT_ROOT / "examples/capability_proof/fitout_subscene_object_cad_smoke_manifest.json"
        )
        manifest = load_fitout_subscene_object_cad_smoke_manifest(manifest_path)
        assert_fitout_subscene_object_manifest_contract(manifest)

    def test_manifest_samples_align_with_fitout_specs(self) -> None:
        manifest_path = (
            PROJECT_ROOT / "examples/capability_proof/fitout_subscene_object_cad_smoke_manifest.json"
        )
        manifest = load_fitout_subscene_object_cad_smoke_manifest(manifest_path)
        mapping = fitout_subscene_to_sample_id()
        for row in manifest["subscenes"]:
            subscene_id = row["subscene_id"]
            self.assertIn(subscene_id, PRIMARY_SUBSCENE_IDS)
            self.assertEqual(row["sample_id"], mapping[subscene_id])

    def test_fake_cad_smoke_meeting_room(self) -> None:
        output_dir = artifact_path("cfit_12", "meeting_room_fake")
        report = run_fitout_subscene_object_cad_smoke(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            driver=FakeCadDriver(),
            subscene_ids=["meeting_room"],
        )
        self.assertEqual(report["geometry_verified_object_count"], 2, report)
        self.assertTrue(report["subscenes"][0]["geometry_verified"])

    def test_fake_cad_smoke_reception(self) -> None:
        output_dir = artifact_path("cfit_12", "reception_fake")
        report = run_fitout_subscene_object_cad_smoke(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            driver=FakeCadDriver(),
            subscene_ids=["reception"],
        )
        self.assertEqual(report["geometry_verified_object_count"], 2, report)
        self.assertTrue(report["subscenes"][0]["geometry_verified"])

    def test_fake_cad_smoke_all_subscenes_four_of_four(self) -> None:
        output_dir = artifact_path("cfit_12", "all_subscenes_fake")
        report = run_fitout_subscene_object_cad_smoke(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            driver=FakeCadDriver(),
        )
        self.assertEqual(report["status"], "geometry_verified", report)
        self.assertEqual(report["geometry_verified_object_count"], 4)
        self.assertEqual(report["geometry_verified_subscene_count"], 2)

    def test_boundary_doc_names_cfit_12_contract(self) -> None:
        text = Path("docs/verification/cfit_12_fitout_subscene_object_cad_smoke_boundary.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("CFIT-12-FITOUT-SUBSCENE-OBJECT-CAD-SMOKE", text)
        self.assertIn("meeting_table", text)
        self.assertIn("RCAD-18", text)


if __name__ == "__main__":
    unittest.main()
