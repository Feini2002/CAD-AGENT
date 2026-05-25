from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.project_model.project_builder import ProjectModelError, build_project_model
from core.schemas.validator import validate_value


def load_example(path: str) -> dict[str, object]:
    return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))


class ProjectModelBuilderTests(unittest.TestCase):
    def test_project_model_examples_cover_multiple_domains(self) -> None:
        schema = load_example("core/schemas/project_model.schema.json")
        examples = list((PROJECT_ROOT / "examples/project_models").glob("*.json"))
        models = [json.loads(path.read_text(encoding="utf-8")) for path in examples]
        domains = {model["domain"] for model in models}

        self.assertTrue({"generic", "retail", "residential", "office"}.issubset(domains))
        for model in models:
            self.assertEqual(validate_value(model, schema), [])

    def test_builds_project_model_from_brief_and_manual_drawing(self) -> None:
        brief = load_example("examples/design_briefs/minimal_cabinet_brief.json")
        drawing = load_example("examples/drawing_models/minimal_empty_room.json")

        result = build_project_model(brief, drawing)

        project_model = result.project_model
        self.assertEqual(project_model["brief_id"], brief["brief_id"])
        self.assertEqual(project_model["drawing_model_id"], drawing["drawing_id"])
        self.assertEqual(project_model["domain"], brief["domain"])
        self.assertEqual(project_model["units"], drawing["units"])
        self.assertEqual(project_model["spaces"][0]["space_id"], "space-preview")
        self.assertIn("default_preview_space", result.provenance[0]["source"])

        schema = load_example("core/schemas/project_model.schema.json")
        self.assertEqual(validate_value(project_model, schema), [])

    def test_uses_manual_drawing_spaces_when_present(self) -> None:
        brief = load_example("examples/design_briefs/minimal_cabinet_brief.json")
        drawing = load_example("examples/drawing_models/minimal_empty_room.json")
        drawing["spaces"] = [
            {
                "space_id": "space-manual",
                "name": "Manual Room",
                "boundary": {"min": [100, 200], "max": [4100, 2200]},
            }
        ]

        result = build_project_model(brief, drawing)

        self.assertEqual(result.project_model["spaces"][0]["space_id"], "space-manual")
        self.assertEqual(result.pending_questions, [])

    def test_invalid_boundary_is_rejected(self) -> None:
        brief = load_example("examples/design_briefs/minimal_cabinet_brief.json")
        drawing = load_example("examples/drawing_models/minimal_empty_room.json")
        drawing["spaces"] = [
            {
                "space_id": "space-bad",
                "name": "Bad Space",
                "boundary": {"min": [1000, 1000], "max": [100, 100]},
            }
        ]

        with self.assertRaisesRegex(ProjectModelError, "boundary"):
            build_project_model(brief, drawing)

    def test_invalid_space_items_are_rejected(self) -> None:
        brief = load_example("examples/design_briefs/minimal_cabinet_brief.json")
        drawing = load_example("examples/drawing_models/minimal_empty_room.json")
        drawing["spaces"] = ["bad"]

        with self.assertRaisesRegex(ProjectModelError, "space"):
            build_project_model(brief, drawing)


if __name__ == "__main__":
    unittest.main()
