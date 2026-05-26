from __future__ import annotations

import unittest
from pathlib import Path

from core.agents.commercial_fitout_product_boundary import (
    REQUIRED_PACKAGES,
    assert_product_boundary_contract,
    load_product_alpha_boundary,
    summarize_for_status_pages,
    validate_product_alpha_boundary,
)
from core.agents.commercial_fitout_scope import load_commercial_fitout_scope
from core.schemas.validator import validate_json
from tests.bootstrap import PROJECT_ROOT


class CommercialFitoutProductBoundaryTests(unittest.TestCase):
    def test_boundary_fixture_validates_against_schema(self) -> None:
        path = PROJECT_ROOT / "agents/commercial_fitout/capabilities/product_alpha_boundary.json"
        errors = validate_json(
            PROJECT_ROOT / "core/schemas/commercial_fitout_product_alpha_boundary.schema.json",
            path,
        )
        self.assertEqual(errors, [])

    def test_contract_requires_all_c_cfit_packages_and_no_scene_product(self) -> None:
        boundary = load_product_alpha_boundary()
        assert_product_boundary_contract(boundary)
        package_ids = {item["package_id"] for item in boundary["completed_packages"]}
        self.assertEqual(package_ids, REQUIRED_PACKAGES)
        self.assertFalse(boundary["maturity"]["declares_scene_product_complete"])

    def test_scope_fixture_status_matches_boundary(self) -> None:
        scope = load_commercial_fitout_scope()
        boundary = load_product_alpha_boundary()
        self.assertEqual(scope["product_alpha_status"], boundary["maturity"]["product_alpha_status"])
        self.assertEqual(set(scope["primary_subscenes"]), set(boundary["primary_subscenes"]))

    def test_geometry_verified_claims_are_scoped(self) -> None:
        boundary = load_product_alpha_boundary()
        verified = [item for item in boundary["declarable_capabilities"] if item.get("geometry_verified")]
        self.assertEqual(len(verified), 1)
        self.assertIn("commercial_fitout_sample", verified[0].get("geometry_verified_note", ""))

    def test_status_page_summary_non_empty(self) -> None:
        summary = summarize_for_status_pages()
        self.assertIn("Scene Product Alpha", summary["core_status_scene_line"])
        self.assertIn("C-CFIT", summary["cad_agent_status_scene_line"])


if __name__ == "__main__":
    unittest.main()
