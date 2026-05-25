from __future__ import annotations

import json
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.capabilities.registry import get_capability, list_capabilities, run_capability, validate_capability_registry
from core.capabilities.specs import ALLOWED_MATURITY
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
        self.assertIn("drawing_analysis.load_shell_model", ids)
        self.assertIn("layout.generate_circulation_candidates", ids)
        self.assertIn("layout.split_function_zones", ids)
        self.assertIn("layout.create_zone_placements", ids)
        self.assertIn("workflow.blank_shell_pipeline", ids)
        for item in catalog:
            self.assertIn(item["risk_level"], {"read_only", "preview_only", "requires_approval"})
            self.assertIn("input_schema", item)
            self.assertIn("output_contract", item)
            self.assertIsInstance(item["requires_cad"], bool)

    def test_capability_specs_expose_maturity_and_known_limits(self) -> None:
        catalog = list_capabilities()

        self.assertTrue(catalog)
        for item in catalog:
            self.assertIn(item["maturity"], ALLOWED_MATURITY)
            self.assertIsInstance(item["known_limits"], list)
            self.assertTrue(item["known_limits"])

    def test_project_model_capability_builds_schema_valid_output(self) -> None:
        brief = load_json("examples/design_briefs/minimal_cabinet_brief.json")
        drawing = load_json("examples/drawing_models/minimal_empty_room.json")

        result = run_capability("project_model.build", {"brief": brief, "drawing_model": drawing})

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["capability_id"], "project_model.build")
        self.assertEqual(result["output_model_type"], "project_model")
        schema = load_json("core/schemas/project_model.schema.json")
        self.assertEqual(validate_value(result["output"], schema), [])

    def test_project_model_capability_accepts_shell_model_input(self) -> None:
        brief = load_json("examples/design_briefs/minimal_cabinet_brief.json")
        drawing = load_json("examples/drawing_models/minimal_empty_room.json")
        shell_result = run_capability(
            "drawing_analysis.load_shell_model",
            {"shell_path": "projects/sample_blank_shell/input/shell.manual.json"},
        )

        result = run_capability(
            "project_model.build",
            {
                "brief": brief,
                "drawing_model": drawing,
                "shell_model": shell_result["output"],
            },
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output"]["shell_id"], "shell-sample-blank-shell")
        self.assertEqual(result["output"]["spaces"][0]["source"], "shell_model.boundary")
        self.assertIn("shell_context", result["output"])

    def test_circulation_capability_returns_candidate_list(self) -> None:
        brief = load_json("examples/design_briefs/minimal_cabinet_brief.json")
        drawing = load_json("examples/drawing_models/minimal_empty_room.json")
        shell = run_capability(
            "drawing_analysis.load_shell_model",
            {"shell_path": "examples/shell_models/retail_blank_shell.json"},
        )["output"]
        project_model = run_capability(
            "project_model.build",
            {"brief": brief, "drawing_model": drawing, "shell_model": shell},
        )["output"]

        result = run_capability(
            "layout.generate_circulation_candidates",
            {"project_model": project_model, "preferences": {"main_aisle_width_mm": 1200}},
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output_model_type"], "circulation_model_list")
        self.assertGreaterEqual(len(result["output"]), 2)
        self.assertIn("paths", result["output"][0])

    def test_zone_splitter_capability_returns_function_zones(self) -> None:
        shell = run_capability(
            "drawing_analysis.load_shell_model",
            {"shell_path": "examples/shell_models/retail_blank_shell.json"},
        )["output"]
        circulation = load_json("examples/circulation_models/retail_straight_spine.json")

        result = run_capability(
            "layout.split_function_zones",
            {"shell_model": shell, "circulation_model": circulation, "constraints": {}},
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output_model_type"], "function_zone_list")
        self.assertGreaterEqual(len(result["output"]), 2)
        self.assertIn("candidate_functions", result["output"][0])

    def test_placement_capability_returns_zone_placements(self) -> None:
        zone = load_json("examples/function_zones/office_zone_desk_band.json")
        block_library = load_json("libraries/blocks/block_library.example.json")

        result = run_capability(
            "layout.create_zone_placements",
            {"zones": [zone], "object_types": ["desk"], "block_library": block_library},
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output_model_type"], "placement_list")
        self.assertEqual(result["output"][0]["status"], "placed")
        self.assertEqual(result["output"][0]["zone_id"], zone["zone_id"])

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

    def test_blank_shell_pipeline_capability_runs_non_cad_workflow(self) -> None:
        result = run_capability(
            "workflow.blank_shell_pipeline",
            {
                "workflow_path": "examples/workflows/blank_shell_layout_loop.json",
                "output_dir": "output/test_artifacts/capabilities/blank_shell_pipeline",
            },
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output_model_type"], "blank_shell_pipeline_report")
        self.assertEqual(result["output"]["status"], "ok")
        self.assertEqual(result["output"]["metrics"]["cad_plans"], 5)

    def test_object_explain_capability_returns_provenance(self) -> None:
        object_spec = load_json("examples/object_specs/minimal_cabinet_object.json")
        style_profile = load_json("libraries/styles/european.json")

        result = run_capability("object.explain", {"object_spec": object_spec, "style_profile": style_profile})

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output"]["status"], "ok")
        self.assertEqual(result["output"]["evidence"]["style_profile_id"], "style-european")


if __name__ == "__main__":
    unittest.main()
