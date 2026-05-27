from __future__ import annotations

import unittest

from core.verification.commercial_fitout_catalog_manifest import (
    load_commercial_fitout_catalog_manifest,
    run_commercial_fitout_catalog_inventory,
    validate_commercial_fitout_catalog_manifest,
)
from tests.bootstrap import PROJECT_ROOT


class CommercialFitoutCatalogManifestTests(unittest.TestCase):
    def test_manifest_matches_object_catalog(self) -> None:
        manifest_path = PROJECT_ROOT / "examples" / "capability_proof" / "commercial_fitout_catalog_manifest.json"
        catalog_path = PROJECT_ROOT / "agents" / "commercial_fitout" / "capabilities" / "object_catalog.json"
        manifest = load_commercial_fitout_catalog_manifest(manifest_path)
        errors = validate_commercial_fitout_catalog_manifest(manifest, object_catalog_path=catalog_path)
        self.assertEqual(errors, [])
        self.assertEqual(len(manifest["catalog_entries"]), 14)

    def test_inventory_runner_passes(self) -> None:
        report = run_commercial_fitout_catalog_inventory(root=PROJECT_ROOT)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["catalog_entry_count"], 14)


if __name__ == "__main__":
    unittest.main()
