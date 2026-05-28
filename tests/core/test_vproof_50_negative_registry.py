from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.verification.capability_registry import validate_capability_registry
from core.verification.negative_plan_registry import (
    NEGATIVE_SUITE_CAPABILITY_ID,
    VPROOF_50_BOUNDARY_DOC,
    VPROOF_50_PACKAGE_ID,
    assert_negative_plan_registry_contract,
    build_negative_plan_registry_rows,
    capability_id_for_negative_failure_category,
    expected_negative_failure_categories,
    merge_negative_plan_registry_rows,
    run_vproof_50_negative_registry_sync,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Vproof50NegativeRegistryTests(unittest.TestCase):
    def test_expected_failure_category_count(self) -> None:
        categories = expected_negative_failure_categories(project_root=PROJECT_ROOT)
        self.assertEqual(len(categories), 8)
        self.assertIn("block_alpha_wrong_layer", categories)

    def test_build_rows_include_suite_and_categories(self) -> None:
        rows = build_negative_plan_registry_rows(project_root=PROJECT_ROOT)
        self.assertEqual(len(rows), 9)
        self.assertEqual(rows[0]["capability_id"], NEGATIVE_SUITE_CAPABILITY_ID)
        ids = {row["capability_id"] for row in rows[1:]}
        self.assertEqual(
            ids,
            {capability_id_for_negative_failure_category(c) for c in expected_negative_failure_categories(project_root=PROJECT_ROOT)},
        )

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / VPROOF_50_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "V-PROOF-50",
            "negative.cad_plan",
            "invalid_configuration",
            "negative_guard_verified",
            "claim_level",
            "smoke",
            "不得声称",
            "geometry_verified",
            "LCAD-10",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_merge_and_sync_dry_run(self) -> None:
        output_dir = artifact_path("vproof_50", "sync_dry_run")
        summary = run_vproof_50_negative_registry_sync(
            project_root=PROJECT_ROOT,
            output_dir=output_dir,
            dry_run=True,
        )
        self.assertEqual(summary["package_id"], VPROOF_50_PACKAGE_ID)
        self.assertEqual(summary["failure_category_count"], 8)
        self.assertEqual(summary["registry_row_count"], 9)
        self.assertEqual(summary["writeback_rejected_count"], 0)

    def test_registry_contract_after_merge_in_temp_registry(self) -> None:
        registry_path = PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        rows = build_negative_plan_registry_rows(project_root=PROJECT_ROOT)
        merge_negative_plan_registry_rows(registry, rows)
        errors = validate_capability_registry(registry)
        self.assertEqual(errors, [])
        for category in expected_negative_failure_categories(project_root=PROJECT_ROOT):
            capability_id = capability_id_for_negative_failure_category(category)
            row = next(item for item in registry["capabilities"] if item["capability_id"] == capability_id)
            self.assertEqual(row["claim_level"], "smoke")

    def test_live_registry_contract_when_rows_present(self) -> None:
        registry_path = PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        if not any(
            str(item.get("capability_id", "")).startswith("negative.cad_plan.")
            for item in registry.get("capabilities", [])
        ):
            self.skipTest("negative registry rows not merged yet; run run_vproof_50_negative_registry_sync.py")
        assert_negative_plan_registry_contract(project_root=PROJECT_ROOT)


if __name__ == "__main__":
    unittest.main()
