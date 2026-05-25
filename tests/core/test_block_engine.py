from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.block_engine.block_library import load_block_library
from core.block_engine.block_placement import create_block_insertion_intent
from core.block_engine.block_selector import select_block_candidate


class BlockEngineTests(unittest.TestCase):
    def test_example_block_library_covers_multiple_generic_categories(self) -> None:
        categories = {block["category"] for block in load_block_library()["blocks"]}

        self.assertGreaterEqual(len(categories), 4)
        self.assertTrue({"cabinet", "table", "shelf", "chair"}.issubset(categories))

    def test_select_block_candidate_scores_domain_and_tags(self) -> None:
        result = select_block_candidate(
            load_block_library(),
            category="cabinet",
            domain="retail",
            tags=["preview"],
            max_width=2000,
        )

        self.assertEqual(result["status"], "selected")
        self.assertEqual(result["selected_block"]["block_id"], "block-cabinet-1800")
        self.assertGreater(result["score"], 0)

    def test_missing_block_returns_fallback_object_spec(self) -> None:
        result = select_block_candidate(load_block_library(), category="cabinet", domain="office", max_width=500)

        self.assertEqual(result["status"], "fallback")
        self.assertEqual(result["fallback_object_spec"]["type"], "cabinet")

    def test_block_insertion_intent_does_not_touch_cad(self) -> None:
        library = load_block_library()
        result = select_block_candidate(library, category="table", domain="generic")
        intent = create_block_insertion_intent(result["selected_block"], base_point=[100, 200, 0])

        self.assertEqual(intent["operation"], "insert_block_preview_intent")
        self.assertFalse(intent["executes_cad"])
        self.assertEqual(intent["base_point"], [100, 200, 0])

    def test_block_insertion_intent_accounts_for_insertion_point_and_right_angle_rotation(self) -> None:
        block = {
            "block_id": "block-offset",
            "name": "Offset Block",
            "size": {"width": 1000, "depth": 400},
            "insertion_point": [100, 50, 0],
            "rotation_allowed": True,
        }

        intent = create_block_insertion_intent(block, base_point=[500, 500, 0], rotation=90)

        self.assertEqual(intent["bbox"], {"min": [450, 400], "max": [850, 1400]})
        self.assertIn("right_angle_rotation_bbox", intent["warnings"])

    def test_block_insertion_intent_rejects_rotation_when_not_allowed(self) -> None:
        block = {
            "block_id": "block-fixed",
            "name": "Fixed Block",
            "size": {"width": 1000, "depth": 400},
            "insertion_point": [0, 0, 0],
            "rotation_allowed": False,
        }

        with self.assertRaisesRegex(ValueError, "rotation"):
            create_block_insertion_intent(block, base_point=[0, 0, 0], rotation=90)


if __name__ == "__main__":
    unittest.main()
