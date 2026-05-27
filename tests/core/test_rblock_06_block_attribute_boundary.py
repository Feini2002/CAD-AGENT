from __future__ import annotations

import unittest

from core.block_engine.block_attribute_boundary import (
    RBLOCK_06_BOUNDARY_DOC,
    RBLOCK_06_PACKAGE_ID,
    assert_block_attribute_boundary_contract,
    block_attribute_boundary_status_summary,
    default_manifest_path,
    load_block_attribute_probe_manifest,
    run_block_attribute_probe_smoke,
)
from core.block_engine.block_matrix_manifest import run_attribute_probe_case
from tests.bootstrap import PROJECT_ROOT


class Rblock06BlockAttributeBoundaryTests(unittest.TestCase):
    def test_rblock_06_contract(self) -> None:
        assert_block_attribute_boundary_contract(project_root=PROJECT_ROOT)

    def test_manifest_ids(self) -> None:
        manifest = load_block_attribute_probe_manifest(default_manifest_path(PROJECT_ROOT))
        self.assertEqual(manifest["manifest_id"], "block-attribute-probe-01")
        self.assertEqual(manifest["registry_capability_id"], "block.insert_block_alpha.attributes")

    def test_attribute_probe_smoke(self) -> None:
        manifest = load_block_attribute_probe_manifest(default_manifest_path(PROJECT_ROOT))
        smoke = run_block_attribute_probe_smoke(project_root=PROJECT_ROOT, manifest=manifest)
        self.assertEqual(smoke["status"], "pass")
        self.assertEqual(smoke["deferred_failure_category"], "attribute_unverified")

    def test_matrix_attribute_dimension_still_passes(self) -> None:
        result = run_attribute_probe_case(
            project_root=PROJECT_ROOT,
            case_id="attribute_probe_codex",
        )
        self.assertEqual(result["status"], "pass", result)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / RBLOCK_06_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "RBLOCK-06",
            "block-attribute-probe-01",
            "insert_block_alpha_attribute_probe",
            "attribute_readback_probe",
            "attribute_unverified",
            "BETA-CAD-BLOCK-02",
            "block.insert_block_alpha.attributes",
            "geometry_verified",
            "不得声称",
            "assert_block_attribute_boundary_contract",
            "dry_run_valid_plan_only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_status_summary(self) -> None:
        summary = block_attribute_boundary_status_summary(project_root=PROJECT_ROOT)
        self.assertEqual(summary["package_id"], RBLOCK_06_PACKAGE_ID)
        self.assertEqual(summary["expected_probe_tags"], ["ROOM", "DESK_ID"])

    def test_handoff_indexes_rblock_06(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("RBLOCK-06", handoff)
        self.assertIn("rblock_06_block_attribute_boundary.md", handoff)


if __name__ == "__main__":
    unittest.main()
