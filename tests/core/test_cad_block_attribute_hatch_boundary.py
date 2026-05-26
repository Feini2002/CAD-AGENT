from __future__ import annotations

import unittest
from pathlib import Path

from core.verification.cad_block_attribute_hatch_boundary import (
    REQUIRED_CAPABILITY_IDS,
    assert_cad_block_attribute_hatch_boundary_contract,
    load_cad_block_attribute_hatch_boundary,
    summarize_capability_matrix,
    validate_cad_block_attribute_hatch_boundary,
)
from core.schemas.validator import validate_json
from tests.bootstrap import PROJECT_ROOT


class CadBlockAttributeHatchBoundaryTests(unittest.TestCase):
    def test_boundary_fixture_validates_against_schema(self) -> None:
        path = PROJECT_ROOT / "examples/cad_regression/cad_block_attribute_hatch_boundary.json"
        errors = validate_json(
            PROJECT_ROOT / "core/schemas/cad_block_attribute_hatch_boundary.schema.json",
            path,
        )
        self.assertEqual(errors, [])

    def test_contract_verified_vs_deferred(self) -> None:
        boundary = load_cad_block_attribute_hatch_boundary()
        assert_cad_block_attribute_hatch_boundary_contract(boundary)
        ids = {item["id"] for item in boundary["capabilities"]}
        self.assertEqual(ids, REQUIRED_CAPABILITY_IDS)

    def test_hatch_is_deferred_in_matrix_summary(self) -> None:
        rows = summarize_capability_matrix()
        hatch = next(row for row in rows if row["id"] == "hatch_write_readback")
        self.assertEqual(hatch["status"], "deferred")
        self.assertEqual(hatch["geometry_verified"], "no")

    def test_block_evidence_paths_exist(self) -> None:
        boundary = load_cad_block_attribute_hatch_boundary()
        block = next(item for item in boundary["capabilities"] if item["id"] == "insert_block_alpha_controlled")
        for rel in block["evidence"]:
            self.assertTrue((PROJECT_ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
