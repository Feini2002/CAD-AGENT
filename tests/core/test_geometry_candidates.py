from __future__ import annotations

import json
import unittest

from core.drawing_analysis.geometry_candidates import (
    extract_geometry_candidates,
    read_geometry_candidates_from_fixture,
)
from core.drawing_analysis.dwg_read_only import read_entity_summary_from_fixture
from core.schemas.validator import validate_value
from tests.bootstrap import PROJECT_ROOT


class GeometryCandidatesTests(unittest.TestCase):
    def test_beta_drawing_read_02_fixture_schema_and_counts(self) -> None:
        fixture = PROJECT_ROOT / "examples/drawing_read/sample_geometry_feature_fixture.json"
        candidates = read_geometry_candidates_from_fixture(fixture)
        schema = json.loads(
            (PROJECT_ROOT / "core/schemas/dwg_geometry_candidates.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(validate_value(candidates, schema), [])
        self.assertTrue(candidates["read_only"])
        self.assertEqual(candidates["counts"]["wall_segments"], 4)
        self.assertEqual(candidates["counts"]["door_openings"], 1)
        self.assertEqual(candidates["counts"]["columns"], 1)
        self.assertEqual(candidates["counts"]["no_place_zones"], 1)
        door = candidates["door_opening_candidates"][0]
        self.assertEqual(door["geometry"]["block_name"], "DOOR_SINGLE_900")
        self.assertGreaterEqual(door["confidence"], 0.8)

    def test_read_01_summary_walls_from_sample_modelspace(self) -> None:
        fixture = PROJECT_ROOT / "examples/drawing_read/sample_modelspace_entities.json"
        summary = read_entity_summary_from_fixture(fixture)
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        candidates = extract_geometry_candidates(payload["entities"], summary=summary)
        self.assertEqual(candidates["counts"]["wall_segments"], 4)
        self.assertEqual(candidates["counts"]["door_openings"], 0)

    def test_no_place_requires_layer_hint(self) -> None:
        candidates = extract_geometry_candidates(
            [
                {
                    "handle": "X1",
                    "layer": "A-FURN",
                    "type": "block_reference",
                    "block_name": "DESK",
                    "insertion_point": [0, 0, 0],
                    "bbox": {"min": [0, 0], "max": [100, 100]},
                }
            ]
        )
        self.assertEqual(candidates["counts"]["no_place_zones"], 0)


if __name__ == "__main__":
    unittest.main()
