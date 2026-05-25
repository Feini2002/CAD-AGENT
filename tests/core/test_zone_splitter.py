from __future__ import annotations

import json
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.layout_engine.zone_splitter import split_zones
from core.schemas.validator import validate_value


def load_example(path: str) -> dict[str, object]:
    return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))


class ZoneSplitterTests(unittest.TestCase):
    def test_split_zones_from_bbox_shell_and_straight_spine(self) -> None:
        shell = load_example("examples/shell_models/retail_blank_shell.json")
        circulation = load_example("examples/circulation_models/retail_straight_spine.json")
        schema = load_example("core/schemas/function_zone.schema.json")

        zones = split_zones(shell, circulation, constraints={})

        self.assertGreaterEqual(len(zones), 2)
        self.assertEqual({zone["side_of_path"] for zone in zones}, {"left", "right"})
        for zone in zones:
            with self.subTest(zone=zone["zone_id"]):
                self.assertIn("geometry", zone)
                self.assertGreater(zone["area"], 0)
                self.assertGreater(zone["depth"], 0)
                self.assertGreater(zone["frontage"], 0)
                self.assertTrue(zone["candidate_functions"])
                self.assertEqual(validate_value(zone, schema), [])

    def test_no_place_zone_subtraction_adds_uncertainty_and_lowers_score(self) -> None:
        shell = {
            "version": "0.1",
            "shell_id": "shell-zone-subtract",
            "units": "mm",
            "boundary": {"type": "bbox", "min": [0, 0], "max": [4000, 4000]},
            "no_place_zones": [
                {"zone_id": "middle-block", "bbox": {"min": [1000, 2200], "max": [3000, 4000]}}
            ],
        }
        circulation = {
            "version": "0.1",
            "circulation_id": "circulation-zone-subtract",
            "shell_id": "shell-zone-subtract",
            "strategy": "straight_spine",
            "status": "pass",
            "score": 1.0,
            "paths": [
                {
                    "path_id": "path-main",
                    "type": "main",
                    "width_mm": 400,
                    "start": [0, 2000],
                    "end": [4000, 2000],
                    "polyline": [[0, 2000], [4000, 2000]],
                    "connects": ["entry", "deep-shell"],
                    "path_surface": [{"min": [0, 1800], "max": [4000, 2200]}],
                    "blocked_reasons": [],
                    "score": 1.0,
                }
            ],
        }

        zones = split_zones(shell, circulation, constraints={})
        upper = next(zone for zone in zones if zone["side_of_path"] == "left")
        lower = next(zone for zone in zones if zone["side_of_path"] == "right")

        self.assertTrue(upper["uncertainties"])
        self.assertIn("no_place_zone", upper["uncertainties"][0])
        self.assertLess(upper["score"], lower["score"])

    def test_function_zone_examples_validate_against_schema(self) -> None:
        schema = load_example("core/schemas/function_zone.schema.json")

        for example in [
            "examples/function_zones/retail_zone_left.json",
            "examples/function_zones/office_zone_desk_band.json",
        ]:
            with self.subTest(example=example):
                zone = load_example(example)
                self.assertEqual(validate_value(zone, schema), [])


if __name__ == "__main__":
    unittest.main()
