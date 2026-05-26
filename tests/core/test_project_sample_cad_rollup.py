from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.project_samples.project_sample_cad_rollup import (
    REQUIRED_SAMPLE_IDS,
    assert_project_sample_cad_rollup_contract,
    load_project_sample_cad_manifest,
    run_project_sample_cad_rollup,
    validate_project_sample_cad_manifest,
)
from core.schemas.validator import validate_value
from core.verification.fake_cad_driver import FakeCadDriver
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class ProjectSampleCadRollupTests(unittest.TestCase):
    def test_manifest_validates(self) -> None:
        manifest = load_project_sample_cad_manifest(project_root=PROJECT_ROOT)
        self.assertEqual(validate_project_sample_cad_manifest(manifest, project_root=PROJECT_ROOT), [])
        ids = {entry["sample_id"] for entry in manifest["samples"]}
        self.assertEqual(ids, REQUIRED_SAMPLE_IDS)

    def test_rollup_fake_driver_geometry_verified_both_samples(self) -> None:
        output_dir = artifact_path("project_samples", "lcad_08_rollup_fake")
        rollup = run_project_sample_cad_rollup(
            output_dir,
            project_root=PROJECT_ROOT,
            driver=FakeCadDriver(),
        )
        self.assertEqual(rollup["status"], "geometry_verified", rollup)
        self.assertTrue(rollup["geometry_verified"])
        self.assertEqual(rollup["geometry_verified_count"], 2)
        assert_project_sample_cad_rollup_contract(rollup)

        schema = json.loads(
            (PROJECT_ROOT / "core/schemas/project_sample_cad_rollup_report.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(validate_value(rollup, schema), [])

        report_path = output_dir / "project_sample_cad_rollup_report.json"
        self.assertTrue(report_path.is_file())

    def test_rollup_no_cad_deferred(self) -> None:
        output_dir = artifact_path("project_samples", "lcad_08_rollup_deferred")
        rollup = run_project_sample_cad_rollup(
            output_dir,
            project_root=PROJECT_ROOT,
            no_cad=True,
        )
        self.assertEqual(rollup["status"], "deferred")
        self.assertFalse(rollup["geometry_verified"])
        self.assertEqual(rollup["deferred_count"], 2)


if __name__ == "__main__":
    unittest.main()
