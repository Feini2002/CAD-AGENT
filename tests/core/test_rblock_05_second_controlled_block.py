from __future__ import annotations

import unittest

from core.block_engine.second_controlled_block_boundary import (
    RBLOCK_05_BOUNDARY_DOC,
    RBLOCK_05_PACKAGE_ID,
    SECOND_CONTROLLED_BLOCK_ID,
    SECOND_CONTROLLED_BLOCK_NAME,
    assert_insert_block_alpha_accepts_second_controlled_block,
    assert_second_controlled_block_contract,
    default_manifest_path,
    load_second_controlled_block_manifest,
    second_controlled_block_status_summary,
)
from core.block_engine.block_library import load_block_library, object_spec_to_block_reference
from tests.bootstrap import PROJECT_ROOT


class Rblock05SecondControlledBlockTests(unittest.TestCase):
    def test_rblock_05_contract(self) -> None:
        assert_second_controlled_block_contract(project_root=PROJECT_ROOT)

    def test_manifest_ids(self) -> None:
        manifest = load_second_controlled_block_manifest(default_manifest_path(PROJECT_ROOT))
        self.assertEqual(manifest["manifest_id"], "second-controlled-block-01")
        self.assertEqual(manifest["second_controlled_block_id"], SECOND_CONTROLLED_BLOCK_ID)

    def test_library_has_two_controlled_blocks(self) -> None:
        library = load_block_library()
        controlled = [
            block
            for block in library["blocks"]
            if str(block.get("source", {}).get("type")) == "controlled_test_block"
        ]
        self.assertEqual(len(controlled), 2)
        ids = {block["block_id"] for block in controlled}
        self.assertEqual(
            ids,
            {"controlled-test-block-001", SECOND_CONTROLLED_BLOCK_ID},
        )

    def test_object_spec_prefers_second_block_ref(self) -> None:
        library = load_block_library()
        result = object_spec_to_block_reference(
            {
                "object_id": "desk-002",
                "type": "desk",
                "name": "Desk",
                "size": {"width": 600, "depth": 300},
                "preferred_block_refs": [SECOND_CONTROLLED_BLOCK_ID],
            },
            library,
        )
        self.assertEqual(result["status"], "selected")
        self.assertEqual(result["block_reference"]["cad_identity"]["block_name"], SECOND_CONTROLLED_BLOCK_NAME)

    def test_insert_block_alpha_accepts_second_block_after_vproof_41(self) -> None:
        assert_insert_block_alpha_accepts_second_controlled_block()

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / RBLOCK_05_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "RBLOCK-05",
            "second-controlled-block-01",
            "controlled-test-block-002",
            "CODEX_TEST_BLOCK_002",
            "controlled-test-block-001",
            "V-PROOF-41",
            "geometry_verified",
            "不得声称",
            "assert_second_controlled_block_contract",
            "metadata_only",
            "insert_block_alpha",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_status_summary(self) -> None:
        summary = second_controlled_block_status_summary(project_root=PROJECT_ROOT)
        self.assertEqual(summary["package_id"], RBLOCK_05_PACKAGE_ID)
        self.assertEqual(summary["controlled_test_block_count"], 2)

    def test_handoff_indexes_rblock_05(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("RBLOCK-05", handoff)
        self.assertIn("rblock_05_second_controlled_block.md", handoff)


if __name__ == "__main__":
    unittest.main()
