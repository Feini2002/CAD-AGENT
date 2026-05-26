from __future__ import annotations

import unittest

from core.verification.cad_capability_probe import EXPECTED_TYPE_COUNTS
from core.verification.primitive_matrix import PRIMITIVE_TYPES, run_primitive_matrix
from tests.helpers import artifact_path


class PrimitiveMatrixTests(unittest.TestCase):
    def test_no_cad_primitive_matrix_passes_on_fake_driver(self) -> None:
        output_dir = artifact_path("primitive_matrix", "no_cad")
        report = run_primitive_matrix(output_dir=output_dir, no_cad=True)

        self.assertEqual(report["status"], "pass")
        self.assertTrue(report["no_cad"])
        self.assertFalse(report["geometry_verified"])
        self.assertEqual(report["expected_type_counts"], EXPECTED_TYPE_COUNTS)
        self.assertEqual(report["actual_type_counts"], EXPECTED_TYPE_COUNTS)
        self.assertEqual(tuple(report["primitive_types"]), PRIMITIVE_TYPES)
