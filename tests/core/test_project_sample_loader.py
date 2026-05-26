from __future__ import annotations

import json
import unittest
import uuid
from pathlib import Path

from core.project_samples.loader import (
    ProjectSampleLoadError,
    build_sample_project_model,
    compare_project_model_to_expected,
    load_sample_inputs,
    load_sample_shell,
)
from core.schemas.validator import validate_json, validate_value
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


SAMPLE_ID = "sample_blank_shell"


class ProjectSampleLoaderTests(unittest.TestCase):
    def test_beta_project_sample_02_loads_shell_from_manifest(self) -> None:
        shell = load_sample_shell(SAMPLE_ID, projects_root=PROJECT_ROOT / "projects")

        self.assertEqual(shell["shell_id"], "shell-sample-blank-shell")
        schema = json.loads(
            (PROJECT_ROOT / "core/schemas/shell_model.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(validate_value(shell, schema), [])

    def test_beta_project_sample_02_loads_all_manifest_inputs(self) -> None:
        inputs = load_sample_inputs(SAMPLE_ID, projects_root=PROJECT_ROOT / "projects")

        self.assertEqual(inputs["manifest"]["sample_id"], SAMPLE_ID)
        self.assertIn("design_brief", inputs)
        self.assertIn("drawing_model", inputs)
        self.assertIn("shell_model", inputs)
        self.assertEqual(inputs["design_brief"]["brief_id"], "brief-sample-blank-shell")

    def test_beta_project_sample_02_builds_project_model_matching_expected(self) -> None:
        result = build_sample_project_model(SAMPLE_ID, projects_root=PROJECT_ROOT / "projects")
        expected_path = (
            PROJECT_ROOT / "projects/sample_blank_shell/expected/project_model.expected.json"
        )
        expected = json.loads(expected_path.read_text(encoding="utf-8"))

        diffs = compare_project_model_to_expected(result.project_model, expected)
        self.assertEqual(diffs, [], diffs)
        self.assertEqual(result.project_model, expected)

        schema = json.loads(
            (PROJECT_ROOT / "core/schemas/project_model.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(validate_value(result.project_model, schema), [])

    def test_beta_project_sample_02_fixture_files_validate_against_schemas(self) -> None:
        root = PROJECT_ROOT / "projects/sample_blank_shell"
        checks = [
            ("shell_model.schema.json", root / "input/shell.manual.json"),
            ("design_brief.schema.json", root / "fixtures/design_brief.json"),
            ("drawing_model.schema.json", root / "fixtures/drawing_model.json"),
            ("project_model.schema.json", root / "expected/project_model.expected.json"),
        ]
        for schema_name, data_path in checks:
            with self.subTest(schema=schema_name):
                errors = validate_json(PROJECT_ROOT / "core/schemas" / schema_name, data_path)
                self.assertEqual(errors, [], errors)

    def test_unknown_sample_raises(self) -> None:
        with self.assertRaises(ProjectSampleLoadError):
            load_sample_shell("missing-sample", projects_root=PROJECT_ROOT / "projects")

    def test_manifest_input_path_must_stay_inside_sample_directory(self) -> None:
        root = self._artifact_root("loader-path-escape")
        sample = root / "escape_sample"
        self._write_minimal_sample(sample, input_path="../outside.json")
        (root / "outside.json").write_text('{"brief_id": "outside"}', encoding="utf-8")

        with self.assertRaises(ProjectSampleLoadError):
            load_sample_inputs("escape_sample", projects_root=root)

    def _artifact_root(self, prefix: str) -> Path:
        marker = artifact_path("project_sample_loader", f"{prefix}-{uuid.uuid4().hex}", ".keep")
        return marker.parent

    def _write_minimal_sample(self, sample: Path, *, input_path: str) -> None:
        (sample / "input").mkdir(parents=True)
        (sample / "expected").mkdir()
        (sample / "README.md").write_text(
            "\n".join(["## 样本标识", "## 输入说明", "## 预期输出", "## 不可声称"]),
            encoding="utf-8",
        )
        (sample / "expected/expected_notes.md").write_text("# notes\n", encoding="utf-8")
        manifest = {
            "version": "0.1",
            "sample_id": sample.name,
            "display_name": "Escape Sample",
            "domain": "generic",
            "deidentified": True,
            "cad_policy": {
                "preview_layer_only": True,
                "allow_formal_layers": False,
                "allow_save_dwg": False,
            },
            "input_files": [{"role": "design_brief", "path": input_path, "schema": "design_brief"}],
            "expected_artifacts": ["project_model"],
            "evidence_claim": "non_cad_pipeline_only",
        }
        (sample / "sample.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
