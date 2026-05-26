from __future__ import annotations

import json
import unittest
import uuid
from pathlib import Path

from core.project_samples.protocol import scan_project_sample, scan_projects_root
from core.schemas.validator import validate_json
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class ProjectSampleProtocolTests(unittest.TestCase):
    def test_manifest_schema_validates_sample_blank_shell(self) -> None:
        manifest_path = PROJECT_ROOT / "projects/sample_blank_shell/sample.manifest.json"
        errors = validate_json(
            PROJECT_ROOT / "core/schemas/project_sample_manifest.schema.json",
            manifest_path,
        )
        self.assertEqual(errors, [])

    def test_beta_project_sample_01_projects_root_scan_passes(self) -> None:
        report = scan_projects_root(PROJECT_ROOT / "projects")

        self.assertEqual(report["status"], "pass", report)
        self.assertGreaterEqual(report["sample_count"], 1)
        sample = next(s for s in report["samples"] if s["sample_id"] == "sample_blank_shell")
        self.assertEqual(sample["status"], "pass", sample)

    def test_scan_fails_when_manifest_missing(self) -> None:
        root = self._artifact_root("missing-manifest")
        sample = root / "bad_sample"
        (sample / "input").mkdir(parents=True)
        (sample / "expected").mkdir()
        (sample / "README.md").write_text(
            "\n".join(
                [
                    "## 样本标识",
                    "## 输入说明",
                    "## 预期输出",
                    "## 不可声称",
                ]
            ),
            encoding="utf-8",
        )
        (sample / "expected/expected_notes.md").write_text("# notes\n", encoding="utf-8")
        (sample / "input/shell.manual.json").write_text("{}", encoding="utf-8")

        result = scan_project_sample(sample, projects_root=root)
        self.assertEqual(result["status"], "fail")
        rules = {v["rule_id"] for v in result["violations"]}
        self.assertIn("required_file", rules)

    def test_scan_fails_when_dwg_present(self) -> None:
        root = self._artifact_root("dwg-present")
        sample = root / "leak_sample"
        (sample / "input").mkdir(parents=True)
        (sample / "expected").mkdir()
        (sample / "source").mkdir()
        (sample / "source/secret.dwg").write_bytes(b"fake")
        manifest = {
            "version": "0.1",
            "sample_id": "leak_sample",
            "display_name": "Leak",
            "domain": "generic",
            "deidentified": True,
            "cad_policy": {
                "preview_layer_only": True,
                "allow_formal_layers": False,
                "allow_save_dwg": False,
            },
            "input_files": [{"role": "shell_model", "path": "input/shell.manual.json", "schema": "shell_model"}],
            "expected_artifacts": ["cad_plan"],
            "evidence_claim": "non_cad_pipeline_only",
        }
        (sample / "sample.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (sample / "input/shell.manual.json").write_text("{}", encoding="utf-8")
        (sample / "expected/expected_notes.md").write_text("# notes\n", encoding="utf-8")
        (sample / "README.md").write_text(
            "\n".join(
                ["## 样本标识", "## 输入说明", "## 预期输出", "## 不可声称"],
            ),
            encoding="utf-8",
        )

        result = scan_project_sample(sample, projects_root=root)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any(v["rule_id"] == "forbidden_source_file" for v in result["violations"]))

    def test_scan_fails_when_manifest_input_escapes_sample_directory(self) -> None:
        root = self._artifact_root("manifest-input-escape")
        sample = root / "escape_sample"
        (sample / "input").mkdir(parents=True)
        (sample / "expected").mkdir()
        (root / "outside.json").write_text("{}", encoding="utf-8")
        manifest = {
            "version": "0.1",
            "sample_id": "escape_sample",
            "display_name": "Escape",
            "domain": "generic",
            "deidentified": True,
            "cad_policy": {
                "preview_layer_only": True,
                "allow_formal_layers": False,
                "allow_save_dwg": False,
            },
            "input_files": [{"role": "design_brief", "path": "../outside.json", "schema": "design_brief"}],
            "expected_artifacts": ["project_model"],
            "evidence_claim": "non_cad_pipeline_only",
        }
        (sample / "sample.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (sample / "expected/expected_notes.md").write_text("# notes\n", encoding="utf-8")
        (sample / "README.md").write_text(
            "\n".join(["## 样本标识", "## 输入说明", "## 预期输出", "## 不可声称"]),
            encoding="utf-8",
        )

        result = scan_project_sample(sample, projects_root=root)

        self.assertEqual(result["status"], "fail")
        self.assertTrue(any(v["rule_id"] == "manifest_input_outside_sample" for v in result["violations"]))

    def _artifact_root(self, prefix: str) -> Path:
        marker = artifact_path("project_sample_protocol", f"{prefix}-{uuid.uuid4().hex}", ".keep")
        return marker.parent


if __name__ == "__main__":
    unittest.main()
