from __future__ import annotations

import json
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.model_loop.reference_checker import load_workflow_index, validate_references, validate_workflow_schemas


class ModelLoopReferenceTests(unittest.TestCase):
    def test_minimal_workflow_paths_and_schemas_validate(self) -> None:
        workflow = load_workflow_index(PROJECT_ROOT / "examples" / "workflows" / "minimal_cabinet_loop.json")

        self.assertEqual(validate_workflow_schemas(workflow), [])

    def test_reference_checker_detects_style_mismatch(self) -> None:
        workflow = load_workflow_index(PROJECT_ROOT / "examples" / "workflows" / "minimal_cabinet_loop.json")

        errors = validate_references(workflow)

        self.assertEqual(errors, [])

        workflow.artifacts["style_profile"].data["style_id"] = "style-minimal"
        errors = validate_references(workflow)

        self.assertIn("object style_profile_id", "\n".join(errors))

    def test_unknown_workflow_model_type_is_reported(self) -> None:
        workflow = load_workflow_index(PROJECT_ROOT / "examples" / "workflows" / "minimal_cabinet_loop.json")
        artifact = workflow.artifacts.pop("design_brief")
        artifact.model_type = "design_breif"
        workflow.artifacts["design_breif"] = artifact

        errors = validate_workflow_schemas(workflow)

        self.assertIn("Unknown model type", "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
