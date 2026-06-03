from __future__ import annotations

import unittest

from core.verification.fake_cad_driver import FakeCadDriver
from core.visual_retrieval import (
    BlockCandidate,
    build_bbox_dimension_plan,
    execute_dimension_annotation_plan,
)


class VisualDimensionAnnotationTests(unittest.TestCase):
    def test_builds_dimension_plan_from_retrieved_sofa_bbox(self) -> None:
        candidate = BlockCandidate(
            handle="4A2",
            block_name="5S03232",
            layer="source_layer",
            bbox={"min": [2173.35, 1178.26], "max": [4973.35, 2138.26]},
            size=[2800.0, 960.0],
            aspect_ratio=2.916,
            source_entity={},
        )

        plan = build_bbox_dimension_plan(candidate)

        self.assertEqual(plan.target_handle, "4A2")
        self.assertEqual(plan.output_layer, "CODEX_PREVIEW")
        self.assertEqual([item.axis for item in plan.dimensions], ["width", "depth"])
        self.assertEqual([item.text_override for item in plan.dimensions], ["2800", "960"])
        self.assertFalse(plan.safety["modify_target_block"])

    def test_dimension_execution_uses_preview_layer_and_reads_back_dimensions(self) -> None:
        driver = FakeCadDriver()
        candidate = BlockCandidate(
            handle="4A2",
            block_name="5S03232",
            layer="source_layer",
            bbox={"min": [0, 0], "max": [2800, 960]},
            size=[2800.0, 960.0],
            aspect_ratio=2.916,
            source_entity={},
        )

        result = execute_dimension_annotation_plan(driver, build_bbox_dimension_plan(candidate))

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["created_handle_count"], 2)
        self.assertEqual(result["dimension_readback_count"], 2)
        self.assertEqual(result["layer"], "CODEX_PREVIEW")
        self.assertFalse(result["safety"]["modified_target_block"])


if __name__ == "__main__":
    unittest.main()
