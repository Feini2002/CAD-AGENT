from __future__ import annotations

import unittest
import json
from pathlib import Path


from tests.bootstrap import PROJECT_ROOT

from core.workflows.non_cad_pipeline import run_non_cad_pipeline
from core.model_loop.reference_checker import load_workflow_index, validate_references, validate_workflow_schemas
from core.plan_engine.validate_plan import validate_plan
from core.schemas.registry import get_schema_path
from core.schemas.validator import validate_json
from tests.helpers import artifact_path


class NonCadPipelineTests(unittest.TestCase):
    def test_pipeline_outputs_core_artifacts_and_unverified_report(self) -> None:
        output_dir = artifact_path("non_cad_pipeline", "run")

        result = run_non_cad_pipeline(
            PROJECT_ROOT / "examples" / "workflows" / "full_non_cad_core_loop.json",
            output_dir=output_dir,
        )

        self.assertEqual(result["status"], "ok")
        for key in [
            "project_model",
            "object_spec",
            "layout_proposal",
            "design_proposal",
            "cad_plan",
            "dry_run_report",
            "verification_report",
        ]:
            self.assertTrue(Path(result["artifacts"][key]).exists(), key)
        self.assertEqual(result["verification_report"]["status"], "unverified")
        self.assertEqual(result["dry_run_report"]["status"], "valid")
        self.assertEqual(result["preferences"]["scenario"], "commercial_fitout")

        object_spec = json.loads(Path(result["artifacts"]["object_spec"]).read_text(encoding="utf-8"))
        roles = {component["role"] for component in object_spec["components"]}
        self.assertIn("ornament", roles)

        layout = json.loads(Path(result["artifacts"]["layout_proposal"]).read_text(encoding="utf-8"))
        clearance_checks = [
            check for check in layout["candidates"][0]["checks"] if check["name"] == "clearance"
        ]
        self.assertTrue(clearance_checks)

        schema_pairs = {
            "object_spec": "object_spec",
            "project_model": "project_model",
            "layout_proposal": "layout_proposal",
            "design_proposal": "design_proposal",
            "verification_report": "verification_report",
        }
        for artifact_key, model_type in schema_pairs.items():
            with self.subTest(artifact=artifact_key):
                self.assertEqual(
                    validate_json(get_schema_path(model_type), Path(result["artifacts"][artifact_key])),
                    [],
                )
        cad_plan = json.loads(Path(result["artifacts"]["cad_plan"]).read_text(encoding="utf-8"))
        self.assertEqual(validate_plan(cad_plan), [])

    def test_pipeline_workflow_schemas_and_references_validate(self) -> None:
        workflow = load_workflow_index(PROJECT_ROOT / "examples" / "workflows" / "minimal_cabinet_loop.json")

        self.assertEqual(validate_workflow_schemas(workflow), [])
        self.assertEqual(validate_references(workflow), [])


if __name__ == "__main__":
    unittest.main()
