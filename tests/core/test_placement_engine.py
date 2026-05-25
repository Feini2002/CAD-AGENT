from __future__ import annotations

import json
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.block_engine.block_library import load_block_library
from core.layout_engine.placement import create_zone_placements


def load_example(path: str) -> dict[str, object]:
    return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))


class PlacementEngineTests(unittest.TestCase):
    def test_zone_places_desk_with_required_fields(self) -> None:
        zone = load_example("examples/function_zones/office_zone_desk_band.json")

        placements = create_zone_placements(
            [zone],
            object_types=["desk"],
            block_library=load_block_library(),
            preferences={"clearance_mm": 100},
        )

        self.assertEqual(len(placements), 1)
        placement = placements[0]
        self.assertEqual(placement["zone_id"], zone["zone_id"])
        self.assertEqual(placement["status"], "placed")
        self.assertIn("object_id", placement)
        self.assertIn("base_point", placement)
        self.assertIn("rotation", placement)
        self.assertIn("bbox", placement)
        self.assertIn("clearance_bbox", placement)
        self.assertIn("source", placement)

    def test_placement_keeps_failure_reason_when_it_overlaps_path_surface(self) -> None:
        zone = {
            **load_example("examples/function_zones/office_zone_desk_band.json"),
            "geometry": {"min": [0, 0], "max": [2000, 1000]},
            "boundary": {"min": [0, 0], "max": [2000, 1000]},
        }
        path_surface = [{"min": [0, 0], "max": [2000, 1000]}]

        placements = create_zone_placements(
            [zone],
            object_types=["desk"],
            block_library=load_block_library(),
            path_surfaces=path_surface,
        )

        self.assertEqual(placements[0]["status"], "blocked")
        self.assertTrue(placements[0]["failure_reasons"])
        self.assertIn("path_surface", placements[0]["failure_reasons"][0])

    def test_placement_uses_parametric_fallback_when_block_is_missing(self) -> None:
        zone = load_example("examples/function_zones/retail_zone_left.json")
        empty_library = {"version": "0.1", "library_id": "empty", "blocks": []}

        placements = create_zone_placements([zone], object_types=["sofa"], block_library=empty_library)

        self.assertEqual(placements[0]["source"]["type"], "object_spec_fallback")
        self.assertEqual(placements[0]["source"]["object_spec"]["type"], "sofa")

    def test_placement_blocks_cleanly_when_no_remaining_zone_width_exists(self) -> None:
        zone = {
            **load_example("examples/function_zones/retail_zone_left.json"),
            "geometry": {"min": [0, 0], "max": [1800, 1200]},
            "boundary": {"min": [0, 0], "max": [1800, 1200]},
        }

        placements = create_zone_placements(
            [zone],
            object_types=["cabinet", "chair"],
            block_library=load_block_library(),
            preferences={"placement_spacing_mm": 300},
        )

        self.assertEqual(placements[0]["status"], "placed")
        self.assertEqual(placements[1]["status"], "blocked")
        self.assertIn("insufficient remaining zone", placements[1]["failure_reasons"][0])


if __name__ == "__main__":
    unittest.main()
