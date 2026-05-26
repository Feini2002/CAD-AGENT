from __future__ import annotations

import unittest

from core.agents.commercial_fitout_block_mapping import (
    assert_block_mapping_contract,
    assert_block_name_allowed,
    load_commercial_fitout_block_mapping,
    load_fitout_block_library,
    resolve_catalog_object_render,
    validate_commercial_fitout_block_mapping,
)
from core.agents.commercial_fitout_catalog import catalog_entry_to_object_specs, catalog_index
from core.block_engine.block_library import load_block_library, validate_block_library
from core.schemas.validator import validate_json
from tests.bootstrap import PROJECT_ROOT


class CommercialFitoutBlockMappingTests(unittest.TestCase):
    def test_block_mapping_and_library_validate(self) -> None:
        mapping_path = PROJECT_ROOT / "agents" / "commercial_fitout" / "capabilities" / "block_mapping.json"
        library_path = PROJECT_ROOT / "libraries" / "blocks" / "commercial_fitout_block_library.json"
        self.assertEqual(
            validate_json(
                PROJECT_ROOT / "core" / "schemas" / "commercial_fitout_block_mapping.schema.json",
                mapping_path,
            ),
            [],
        )
        self.assertEqual(validate_json(PROJECT_ROOT / "core/schemas/block_library.schema.json", library_path), [])
        self.assertEqual(validate_block_library(load_block_library(library_path)), [])

    def test_mapping_contract_covers_catalog_and_rejects_arbitrary_names(self) -> None:
        assert_block_mapping_contract()

    def test_desk_resolves_to_controlled_block(self) -> None:
        catalog = catalog_index()
        entry = catalog["desk"]
        spec = catalog_entry_to_object_specs(entry)[0]
        result = resolve_catalog_object_render("desk", spec)
        self.assertEqual(result["render_tier"], "block")
        self.assertEqual(result["block_reference"]["block_id"], "fitout-desk-1400")
        assert_block_name_allowed(result["block_reference"]["cad_identity"]["block_name"])

    def test_arbitrary_block_name_raises(self) -> None:
        library = load_fitout_block_library()
        with self.assertRaises(ValueError) as ctx:
            assert_block_name_allowed("ACME_RANDOM_BLOCK_XYZ", library=library)
        self.assertIn("arbitrary_block_name", str(ctx.exception))

    def test_missing_allowlist_block_falls_back_to_object_spec(self) -> None:
        mapping = load_commercial_fitout_block_mapping()
        generic = load_block_library()
        catalog = catalog_index()
        spec = catalog_entry_to_object_specs(catalog["desk"])[0]
        broken_mapping = {
            **mapping,
            "entries": [
                {
                    **mapping["entries"][1],
                    "primary_block_id": "nonexistent-fitout-block",
                }
            ],
        }
        result = resolve_catalog_object_render(
            "desk",
            spec,
            mapping=broken_mapping,
            library=generic,
        )
        self.assertEqual(result["render_tier"], "object_spec")
        self.assertIsNone(result["block_reference"])
        self.assertIsNotNone(result["object_spec"])

    def test_workstation_cluster_bundle_reports_member_results(self) -> None:
        entry = catalog_index()["workstation_cluster"]
        specs = catalog_entry_to_object_specs(entry)
        self.assertEqual(len(specs), 2)
        result = resolve_catalog_object_render("workstation_cluster", specs[0])
        self.assertEqual(result["status"], "bundle")
        self.assertEqual(len(result["member_results"]), 2)

    def test_validate_rejects_arbitrary_block_policy(self) -> None:
        mapping = load_commercial_fitout_block_mapping()
        broken = {
            **mapping,
            "policy": {**mapping["policy"], "allow_arbitrary_block_names": True},
        }
        errors = validate_commercial_fitout_block_mapping(broken)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
