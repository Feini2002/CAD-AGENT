from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.capabilities.registry import get_capability, list_capabilities, run_capability, validate_capability_registry
from core.schemas.validator import validate_value


def load_json(path: str) -> dict[str, object]:
    return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))


class CapabilityRuntimeTests(unittest.TestCase):
    def test_core_capability_catalog_is_machine_discoverable(self) -> None:
        catalog = list_capabilities()
        ids = {item["capability_id"] for item in catalog}

        self.assertIn("project_model.build", ids)
        self.assertIn("layout.create_candidates", ids)
        self.assertIn("plan.model_to_plans", ids)
        self.assertIn("verification.no_cad_report", ids)
        self.assertIn("workflow.artifact_graph", ids)
        self.assertIn("benchmark.non_cad_suite", ids)
        self.assertIn("object.explain", ids)
        self.assertIn("proposal.compare_layout_candidates", ids)
        for item in catalog:
            self.assertIn(item["risk_level"], {"read_only", "preview_only", "requires_approval"})
            self.assertIn("input_schema", item)
            self.assertIn("output_contract", item)
            self.assertIsInstance(item["requires_cad"], bool)

    def test_project_model_capability_builds_schema_valid_output(self) -> None:
        brief = load_json("examples/design_briefs/minimal_cabinet_brief.json")
        drawing = load_json("examples/drawing_models/minimal_empty_room.json")

        result = run_capability("project_model.build", {"brief": brief, "drawing_model": drawing})

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["capability_id"], "project_model.build")
        self.assertEqual(result["output_model_type"], "project_model")
        schema = load_json("core/schemas/project_model.schema.json")
        self.assertEqual(validate_value(result["output"], schema), [])

    def test_capability_rejects_invalid_input_before_running(self) -> None:
        result = run_capability("project_model.build", {"brief": {}, "drawing_model": {}})

        self.assertEqual(result["status"], "invalid_input")
        self.assertTrue(result["errors"])

    def test_capability_spec_exposes_verification_commands(self) -> None:
        spec = get_capability("plan.model_to_plans")

        self.assertFalse(spec["requires_cad"])
        self.assertIn("tests.core.test_plan_engine", " ".join(spec["verification_commands"]))

    def test_capability_registry_validates_its_own_contracts(self) -> None:
        self.assertEqual(validate_capability_registry(), [])

    def test_artifact_graph_capability_returns_ordered_index(self) -> None:
        result = run_capability(
            "workflow.artifact_graph",
            {"workflow_path": "examples/workflows/minimal_cabinet_loop.json"},
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output"]["path_checks"]["status"], "ok")
        self.assertLess(
            result["output"]["dependency_order"].index("design_brief"),
            result["output"]["dependency_order"].index("cad_plan"),
        )

    def test_object_explain_capability_returns_provenance(self) -> None:
        object_spec = load_json("examples/object_specs/minimal_cabinet_object.json")
        style_profile = load_json("libraries/styles/european.json")

        result = run_capability("object.explain", {"object_spec": object_spec, "style_profile": style_profile})

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output"]["status"], "ok")
        self.assertEqual(result["output"]["evidence"]["style_profile_id"], "style-european")


if __name__ == "__main__":
    unittest.main()
