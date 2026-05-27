from __future__ import annotations

import unittest
from pathlib import Path

from core.verification.primitive_matrix_cad_manifest import (
    load_primitive_matrix_cad_manifest,
    primitive_inventory_from_manifest,
    validate_primitive_matrix_cad_manifest,
)
from tests.bootstrap import PROJECT_ROOT


class PrimitiveMatrixCadManifestTests(unittest.TestCase):
    def test_default_manifest_validates(self) -> None:
        path = PROJECT_ROOT / "examples" / "capability_proof" / "primitive_matrix_cad_manifest.json"
        manifest = load_primitive_matrix_cad_manifest(path)
        errors = validate_primitive_matrix_cad_manifest(manifest)
        self.assertEqual(errors, [])
        inventory = primitive_inventory_from_manifest(manifest)
        self.assertEqual(len(inventory), 7)
        self.assertIn("hatch", inventory)


if __name__ == "__main__":
    unittest.main()
