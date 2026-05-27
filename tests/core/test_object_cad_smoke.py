from __future__ import annotations

import unittest

from core.verification.fake_cad_driver import FakeCadDriver
from core.verification.object_cad_smoke import load_object_cad_smoke_manifest, run_object_cad_smoke
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class ObjectCadSmokeTests(unittest.TestCase):
    def test_manifest_has_fourteen_object_types(self) -> None:
        path = PROJECT_ROOT / "examples" / "capability_proof" / "object_cad_smoke_manifest.json"
        manifest = load_object_cad_smoke_manifest(path)
        self.assertEqual(len(manifest["objects"]), 14)

    def test_fake_cad_smoke_geometry_verified(self) -> None:
        output_dir = artifact_path("object_cad_smoke", "fake")
        report = run_object_cad_smoke(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            no_cad=False,
            driver=FakeCadDriver(),
        )
        self.assertEqual(report["status"], "geometry_verified")
        self.assertEqual(report["geometry_verified_object_count"], 14)


if __name__ == "__main__":
    unittest.main()
