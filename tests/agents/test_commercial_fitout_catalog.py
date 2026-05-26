from __future__ import annotations

import unittest

from core.agents.commercial_fitout_catalog import (
    assert_catalog_contract,
    catalog_entry_to_object_specs,
    load_commercial_fitout_object_catalog,
    object_specs_for_subscene,
    validate_commercial_fitout_object_catalog,
)
from core.layout_engine.basic_layout import create_layout_candidates
from core.schemas.validator import validate_json
from tests.bootstrap import PROJECT_ROOT


class CommercialFitoutCatalogTests(unittest.TestCase):
    def test_object_catalog_validates_against_schema(self) -> None:
        catalog_path = PROJECT_ROOT / "agents" / "commercial_fitout" / "capabilities" / "object_catalog.json"
        errors = validate_json(
            PROJECT_ROOT / "core" / "schemas" / "commercial_fitout_object_catalog.schema.json",
            catalog_path,
        )
        self.assertEqual(errors, [])

    def test_catalog_contract_covers_scope_typical_objects(self) -> None:
        assert_catalog_contract()

    def test_workstation_cluster_expands_to_desk_and_chair_specs(self) -> None:
        catalog = load_commercial_fitout_object_catalog()
        entry = next(item for item in catalog["objects"] if item["catalog_object_id"] == "workstation_cluster")
        specs = catalog_entry_to_object_specs(entry)
        self.assertEqual(len(specs), 2)
        types = {spec["type"] for spec in specs}
        self.assertEqual(types, {"desk", "chair"})

    def test_open_office_specs_feed_layout_pipeline(self) -> None:
        specs = object_specs_for_subscene("open_office")
        self.assertGreaterEqual(len(specs), 5)
        project_model = {
            "project_id": "fitout-open-office-layout",
            "spaces": [{"boundary": {"min": [0, 0], "max": [20000, 8000]}}],
        }
        layout = create_layout_candidates(
            project_model=project_model,
            object_specs=specs[:4],
            preferences={"object_spacing_mm": 300, "minimum_clearance_mm": 100},
        )
        self.assertGreaterEqual(len(layout["candidates"]), 1)
        self.assertEqual(len(layout["candidates"][0]["placements"]), 4)

    def test_validate_rejects_empty_objects(self) -> None:
        catalog = load_commercial_fitout_object_catalog()
        broken = {**catalog, "objects": []}
        errors = validate_commercial_fitout_object_catalog(broken)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
