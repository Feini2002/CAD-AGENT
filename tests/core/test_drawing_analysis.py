from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.drawing_analysis.manual_model import build_manual_drawing_model
from core.drawing_analysis.entity_summary import summarize_entities
from core.schemas.validator import validate_value


class DrawingAnalysisTests(unittest.TestCase):
    def test_manual_drawing_model_accepts_spaces_and_uncertainties(self) -> None:
        drawing = build_manual_drawing_model(
            drawing_id="drawing-manual",
            units="mm",
            spaces=[
                {
                    "space_id": "space-1",
                    "name": "Room",
                    "boundary": {"min": [0, 0], "max": [3000, 2000]},
                }
            ],
            uncertainties=["manual boundary"],
        )

        schema = json.loads((PROJECT_ROOT / "core" / "schemas" / "drawing_model.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_value(drawing, schema), [])
        self.assertEqual(drawing["entities_summary"]["line_count"], 0)

    def test_sample_blank_shell_manual_input_validates(self) -> None:
        schema = json.loads((PROJECT_ROOT / "core" / "schemas" / "drawing_model.schema.json").read_text(encoding="utf-8"))
        shell = json.loads(
            (PROJECT_ROOT / "projects" / "sample_blank_shell" / "input" / "shell.manual.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(validate_value(shell, schema), [])
        self.assertTrue(shell["spaces"][0]["avoid_zones"])

    def test_summarize_entities_counts_layers_and_types(self) -> None:
        summary = summarize_entities(
            [
                {"type": "line", "layer": "A-WALL"},
                {"type": "line", "layer": "A-WALL"},
                {"type": "text", "layer": "A-TEXT"},
                {"type": "block", "layer": "A-FURN"},
                {"type": "dimension", "layer": "A-DIMS"},
            ]
        )

        self.assertEqual(summary["entities_summary"]["line_count"], 2)
        self.assertEqual(summary["entities_summary"]["text_count"], 1)
        self.assertEqual(summary["layers"][0]["entity_count"], 2)


if __name__ == "__main__":
    unittest.main()
