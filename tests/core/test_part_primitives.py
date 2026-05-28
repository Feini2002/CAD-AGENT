from __future__ import annotations

import unittest


class PartPrimitiveTests(unittest.TestCase):
    def test_rounded_rect_closed_returns_closed_line_arc_sequence(self) -> None:
        from core.drawing.part_primitives import rounded_rect_closed

        primitives = rounded_rect_closed(0, 0, 100, 50, radius=10, part_id="seat_left")

        self.assertEqual(len(primitives), 8)
        self.assertEqual({item["part_id"] for item in primitives}, {"seat_left"})
        self.assertTrue(all(item["closed_component"] for item in primitives))
        self.assertEqual([item["primitive"] for item in primitives].count("line"), 4)
        self.assertEqual([item["primitive"] for item in primitives].count("arc"), 4)

    def test_pill_horizontal_closed_rejects_vertical_shape(self) -> None:
        from core.drawing.part_primitives import pill_horizontal_closed

        with self.assertRaisesRegex(ValueError, "pill_horizontal requires width > height"):
            pill_horizontal_closed(0, 0, 50, 100, part_id="bad_pill")


if __name__ == "__main__":
    unittest.main()
