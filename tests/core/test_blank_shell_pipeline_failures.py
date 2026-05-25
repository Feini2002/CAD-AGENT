from __future__ import annotations

import json
import unittest

from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path
from core.workflows.blank_shell_pipeline import run_blank_shell_pipeline


class BlankShellPipelineFailureTests(unittest.TestCase):
    def test_missing_workflow_input_returns_invalid_result(self) -> None:
        workflow_path = artifact_path("pipeline_failures", "missing_shell_workflow.json")
        workflow_path.write_text(
            json.dumps(
                {
                    "workflow_id": "missing-shell",
                    "inputs": {
                        "design_brief": "examples/design_briefs/blank_shell_layout_brief.json",
                        "drawing_model": "examples/drawing_models/minimal_empty_room.json",
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        result = run_blank_shell_pipeline(workflow_path, output_dir=artifact_path("pipeline_failures", "out"))

        self.assertEqual(result["status"], "invalid")
        self.assertIn("inputs.shell_model is required", result["errors"])
        self.assertEqual(result["artifacts"], {})

    def test_invalid_object_types_return_invalid_result(self) -> None:
        source = PROJECT_ROOT / "examples" / "workflows" / "blank_shell_layout_loop.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        data["object_types"] = []
        workflow_path = artifact_path("pipeline_failures", "empty_object_types.json")
        workflow_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        result = run_blank_shell_pipeline(
            workflow_path,
            output_dir=artifact_path("pipeline_failures", "empty_object_types_out"),
        )

        self.assertEqual(result["status"], "invalid")
        self.assertIn("object_types must be a non-empty list", result["errors"])

    def test_non_string_workflow_input_paths_return_invalid_result(self) -> None:
        source = PROJECT_ROOT / "examples" / "workflows" / "blank_shell_layout_loop.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        data["inputs"]["shell_model"] = []
        data["inputs"]["preferences"] = 42
        workflow_path = artifact_path("pipeline_failures", "bad_input_types.json")
        workflow_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        result = run_blank_shell_pipeline(
            workflow_path,
            output_dir=artifact_path("pipeline_failures", "bad_input_types_out"),
        )

        self.assertEqual(result["status"], "invalid")
        self.assertIn("inputs.shell_model must be a non-empty string path", result["errors"])
        self.assertIn("inputs.preferences must be a non-empty string path when provided", result["errors"])

    def test_workflow_input_path_must_stay_under_project_root(self) -> None:
        source = PROJECT_ROOT / "examples" / "workflows" / "blank_shell_layout_loop.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        data["inputs"]["shell_model"] = "../outside.json"
        workflow_path = artifact_path("pipeline_failures", "outside_input.json")
        workflow_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        result = run_blank_shell_pipeline(
            workflow_path,
            output_dir=artifact_path("pipeline_failures", "outside_input_out"),
        )

        self.assertEqual(result["status"], "invalid")
        self.assertIn("inputs.shell_model must stay under project root", result["errors"])

    def test_missing_workflow_file_returns_invalid_result(self) -> None:
        workflow_path = artifact_path("pipeline_failures", "missing_workflow.json")

        result = run_blank_shell_pipeline(
            workflow_path,
            output_dir=artifact_path("pipeline_failures", "missing_workflow_out"),
        )

        self.assertEqual(result["status"], "invalid")
        self.assertIn("workflow file does not exist", result["errors"])

    def test_bad_workflow_json_returns_invalid_result(self) -> None:
        workflow_path = artifact_path("pipeline_failures", "bad_json_workflow.json")
        workflow_path.write_text("{not json", encoding="utf-8")

        result = run_blank_shell_pipeline(
            workflow_path,
            output_dir=artifact_path("pipeline_failures", "bad_json_out"),
        )

        self.assertEqual(result["status"], "invalid")
        self.assertTrue(any("workflow JSON is invalid" in error for error in result["errors"]))

    def test_output_dir_must_stay_under_output_root(self) -> None:
        source = PROJECT_ROOT / "examples" / "workflows" / "blank_shell_layout_loop.json"

        result = run_blank_shell_pipeline(
            source,
            output_dir=PROJECT_ROOT.parent / "outside-output",
        )

        self.assertEqual(result["status"], "invalid")
        self.assertIn("output_dir must stay under project output directory", result["errors"])


if __name__ == "__main__":
    unittest.main()
