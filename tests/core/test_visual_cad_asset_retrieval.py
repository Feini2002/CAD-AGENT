from __future__ import annotations

import unittest

from core.visual_retrieval import parse_visual_query_profile, retrieve_visual_blocks


def _block(handle: str, name: str, layer: str, bbox: dict[str, list[float]]) -> dict[str, object]:
    return {
        "handle": handle,
        "type": "block_reference",
        "block_name": name,
        "layer": layer,
        "bbox": bbox,
    }


class VisualCadAssetRetrievalTests(unittest.TestCase):
    def test_parse_sofa_screenshot_profile(self) -> None:
        profile = parse_visual_query_profile("根据截图找到三人沙发对应图块")

        self.assertEqual(profile.object_category, "sofa")
        self.assertEqual(profile.seat_count, 3)
        self.assertEqual(profile.visual_input_mode, "screenshot_profile")
        self.assertTrue(profile.plan_view)
        self.assertIn("three_seat_divisions", profile.expected_parts)

    def test_visual_first_ranking_prefers_wide_source_sofa_shape(self) -> None:
        report = retrieve_visual_blocks(
            query="根据截图找到三人沙发对应图块",
            entities=[
                _block(
                    "4A2",
                    "5S03232",
                    "产品图框",
                    {"min": [2173.35, 1178.26], "max": [4973.35, 2138.26]},
                ),
                _block(
                    "2C4B",
                    "CODEX_TEST_BLOCK_001",
                    "CODEX_PREVIEW",
                    {"min": [13162.81, 8971.38], "max": [13540.81, 9160.38]},
                ),
            ],
        )

        self.assertEqual(report.status, "pass")
        self.assertIsNotNone(report.best_match)
        assert report.best_match is not None
        self.assertEqual(report.best_match.candidate.handle, "4A2")
        self.assertIn("visual_ratio_match=2.92", report.best_match.reasons)
        self.assertIn("source_layer_not_preview", report.best_match.reasons)

    def test_optional_block_summary_boosts_sofa_construction_without_requiring_it(self) -> None:
        report = retrieve_visual_blocks(
            query="找截图里的三座沙发",
            entities=[
                _block("4A2", "5S03232", "产品图框", {"min": [0, 0], "max": [2800, 960]}),
            ],
            block_definition_summaries={
                "5S03232": {
                    "type_counts": {"line": 343, "arc": 12, "polyline": 2},
                    "long_vertical_line_count": 6,
                    "long_horizontal_line_count": 5,
                }
            },
        )

        assert report.best_match is not None
        self.assertGreater(report.best_match.score, 10)
        self.assertIn("rounded_part_arcs=12", report.best_match.reasons)
        self.assertIn("seat_division_lines=6", report.best_match.reasons)


if __name__ == "__main__":
    unittest.main()
