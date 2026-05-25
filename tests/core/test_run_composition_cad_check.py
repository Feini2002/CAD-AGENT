from __future__ import annotations

import unittest

from scripts.run_composition_cad_check import build_case_offsets


class RunCompositionCadCheckTests(unittest.TestCase):
    def test_build_case_offsets_supports_fresh_cad_regions(self) -> None:
        offsets = build_case_offsets(start_x=25000, start_y=8000, spacing_x=5000)

        self.assertEqual(offsets["interior_designer_bedroom_bed_rug"], [25000, 8000, 0])
        self.assertEqual(offsets["home_designer_dining_table_set"], [30000, 8000, 0])
        self.assertEqual(offsets["office_planner_desk_combo"], [35000, 8000, 0])


if __name__ == "__main__":
    unittest.main()
