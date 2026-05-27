from __future__ import annotations

import unittest

from core.verification.composition_cad_check import build_case_offsets, DEFAULT_CASE_ORDER


class CompositionCadCaseIdsTests(unittest.TestCase):
    def test_build_case_offsets_accepts_custom_case_list(self) -> None:
        case_ids = ["case_a", "case_b"]
        offsets = build_case_offsets(case_ids, start_x=1000, spacing_x=500)
        self.assertEqual(list(offsets.keys()), case_ids)
        self.assertEqual(offsets["case_a"], [1000, 0, 0])
        self.assertEqual(offsets["case_b"], [1500, 0, 0])

    def test_default_case_order_unchanged(self) -> None:
        self.assertEqual(len(DEFAULT_CASE_ORDER), 3)


if __name__ == "__main__":
    unittest.main()
