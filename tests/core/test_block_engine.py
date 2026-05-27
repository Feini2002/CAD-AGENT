from __future__ import annotations

import json
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.block_engine.block_library import (
    load_block_library,
    normalize_block,
    object_spec_to_block_reference,
    validate_block_library,
)
from core.block_engine.block_placement import create_block_insertion_intent
from core.block_engine.block_selector import select_block_candidate
from core.schemas.validator import validate_json


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

        self.assertEqual(intent["bbox"], {"min": [150.0, 400.0], "max": [550.0, 1400.0]})
        self.assertIn("right_angle_rotation_bbox", intent["warnings"])

    def test_v02_example_library_validates_and_exposes_controlled_test_block(self) -> None:
        raw = json.loads((PROJECT_ROOT / "libraries/blocks/block_library.example.json").read_text(encoding="utf-8"))
        schema_errors = validate_json(
            PROJECT_ROOT / "core/schemas/block_library.schema.json",
            PROJECT_ROOT / "libraries/blocks/block_library.example.json",
        )
        semantic_errors = validate_block_library(raw)
        self.assertEqual(schema_errors, [])
        self.assertEqual(semantic_errors, [])

        library = load_block_library()
        self.assertEqual(library["version"], "0.2")
        self.assertEqual(library["units"], "mm")
        controlled = next(block for block in library["blocks"] if block["block_id"] == "controlled-test-block-001")
        self.assertEqual(controlled["cad_identity"]["block_name"], "CODEX_TEST_BLOCK_001")
        self.assertEqual(controlled["validation"]["status"], "metadata_only")

    def test_v01_minimal_library_still_loads_and_normalizes(self) -> None:
        path = PROJECT_ROOT / "examples/block_libraries/minimal_builtin_blocks.json"
        errors = validate_json(PROJECT_ROOT / "core/schemas/block_library.schema.json", path)
        self.assertEqual(errors, [])

        library = load_block_library(path)
        block = normalize_block(library["blocks"][0])
        self.assertEqual(block["validation"]["status"], "symbol_fallback")
        self.assertEqual(block["anchor_points"]["insert"], [0, 0, 0])

    def test_selector_filters_validation_status(self) -> None:
        library = load_block_library()
        deferred = {
            "block_id": "deferred-block",
            "name": "Deferred",
            "category": "cabinet",
            "domain": "generic",
            "size": {"width": 800, "depth": 400},
            "insertion_point": [0, 0, 0],
            "rotation_allowed": True,
            "clearance_mm": 100,
            "tags": ["preview"],
            "validation": {"status": "deferred_cad_readback"},
        }
        library = {
            **library,
            "blocks": [*library["blocks"], deferred],
        }

        result = select_block_candidate(library, category="cabinet", domain="generic", max_width=2000)
        self.assertEqual(result["status"], "selected")
        self.assertNotEqual(result["selected_block"]["block_id"], "deferred-block")

    def test_object_spec_to_block_reference_prefers_controlled_block_ref(self) -> None:
        library = load_block_library()
        object_spec = {
            "object_id": "desk-001",
            "type": "desk",
            "name": "Desk",
            "size": {"width": 1400, "depth": 700},
            "preferred_block_refs": ["controlled-test-block-001"],
        }

        result = object_spec_to_block_reference(object_spec, library)

        self.assertEqual(result["status"], "selected")
        self.assertEqual(result["block_reference"]["block_id"], "controlled-test-block-001")
        self.assertEqual(result["block_reference"]["cad_identity"]["block_name"], "CODEX_TEST_BLOCK_001")
        self.assertIsNone(result["fallback_object_spec"])

    def test_object_spec_to_block_reference_falls_back_when_no_block_matches(self) -> None:
        library = load_block_library()
        object_spec = {
            "object_id": "cabinet-tiny",
            "type": "cabinet",
            "name": "Tiny Cabinet",
            "size": {"width": 200, "depth": 200},
        }

        result = object_spec_to_block_reference(object_spec, library, domain="office")

        self.assertEqual(result["status"], "fallback")
        self.assertIsNone(result["block_reference"])
        self.assertEqual(result["fallback_object_spec"]["type"], "cabinet")

    def test_validate_block_library_reports_structured_errors_for_invalid_v02(self) -> None:
        invalid = {
            "version": "0.2",
            "library_id": "bad",
            "units": "mm",
            "blocks": [
                {
                    "block_id": "x",
                    "name": "X",
                    "category": "cabinet",
                    "domain": "generic",
                    "size": {"width": 100, "depth": 100},
                    "insertion_point": [0, 0, 0],
                    "rotation_allowed": True,
                    "clearance_mm": 0,
                    "tags": [],
                }
            ],
        }

        errors = validate_block_library(invalid)
        self.assertTrue(errors)

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
