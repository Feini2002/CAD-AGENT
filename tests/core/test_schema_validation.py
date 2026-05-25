from __future__ import annotations

import json
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.schemas.validator import validate_json, validate_value
from core.schemas.registry import MODEL_SCHEMAS, get_schema_path


SCHEMA_EXAMPLES = {
    "design_brief.schema.json": "examples/design_briefs/minimal_cabinet_brief.json",
    "drawing_model.schema.json": "examples/drawing_models/minimal_empty_room.json",
    "project_model.schema.json": "examples/project_models/minimal_cabinet_project.json",
    "object_spec.schema.json": "examples/object_specs/minimal_cabinet_object.json",
    "style_profile.schema.json": "examples/style_profiles/minimal_modern_style.json",
    "block_library.schema.json": "examples/block_libraries/minimal_builtin_blocks.json",
    "layout_proposal.schema.json": "examples/layout_proposals/minimal_cabinet_layout.json",
    "design_proposal.schema.json": "examples/design_proposals/minimal_cabinet_proposal.json",
    "verification_report.schema.json": "examples/verification_reports/minimal_cabinet_verification.json",
    "shell_model.schema.json": "examples/shell_models/minimal_shell_model.json",
    "circulation_model.schema.json": "examples/circulation_models/minimal_circulation_model.json",
    "function_zone.schema.json": "examples/function_zones/minimal_function_zone.json",
}


class SchemaValidationTests(unittest.TestCase):
    def test_high_level_examples_validate_against_core_schemas(self) -> None:
        self.assertIn("shell_model", MODEL_SCHEMAS)
        self.assertIn("circulation_model", MODEL_SCHEMAS)
        self.assertIn("function_zone", MODEL_SCHEMAS)
        for schema_name, example_path in SCHEMA_EXAMPLES.items():
            with self.subTest(schema=schema_name):
                errors = validate_json(
                    PROJECT_ROOT / "core" / "schemas" / schema_name,
                    PROJECT_ROOT / example_path,
                )
                self.assertEqual(errors, [])

    def test_each_registered_model_has_invalid_fixture(self) -> None:
        fixture_root = PROJECT_ROOT / "tests/fixtures/invalid_models"
        fixture_paths = list(fixture_root.glob("*.invalid.json"))
        covered_model_types = set()
        for fixture_path in fixture_paths:
            with self.subTest(fixture=fixture_path.name):
                fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
                model_type = fixture["model_type"]
                covered_model_types.add(model_type)
                schema = json.loads(get_schema_path(model_type).read_text(encoding="utf-8"))
                errors = validate_value(fixture["data"], schema)
                self.assertTrue(errors)

        self.assertEqual(covered_model_types, set(MODEL_SCHEMAS))

    def test_missing_required_field_fails_with_readable_path(self) -> None:
        errors = validate_json(
            PROJECT_ROOT / "core" / "schemas" / "design_brief.schema.json",
            PROJECT_ROOT / "examples" / "drawing_models" / "minimal_empty_room.json",
        )

        self.assertIn("$.brief_id is required.", errors)

    def test_validator_rejects_additional_properties_nested_items_and_ranges(self) -> None:
        schema = {
            "type": "object",
            "required": ["items"],
            "properties": {
                "items": {
                    "type": "array",
                    "minItems": 2,
                    "items": {
                        "type": "object",
                        "required": ["kind", "size"],
                        "properties": {
                            "kind": {"type": "string", "enum": ["cabinet", "table"]},
                            "size": {"type": "number", "exclusiveMinimum": 0, "maximum": 3000},
                        },
                        "additionalProperties": False,
                    },
                }
            },
            "additionalProperties": False,
        }

        errors = validate_value(
            {
                "items": [
                    {"kind": "chair", "size": -1, "cad_layer": "0"},
                ],
                "unexpected": True,
            },
            schema,
        )

        self.assertIn("$.items must contain at least 2 items.", errors)
        self.assertIn("$.items[0].kind must be one of ['cabinet', 'table'].", errors)
        self.assertIn("$.items[0].size must be > 0.", errors)
        self.assertIn("$.items[0].cad_layer is not allowed.", errors)
        self.assertIn("$.unexpected is not allowed.", errors)

    def test_model_responsibility_boundaries_are_enforced(self) -> None:
        design_brief_schema = json.loads(
            (PROJECT_ROOT / "core" / "schemas" / "design_brief.schema.json").read_text(encoding="utf-8")
        )
        cad_plan_schema = json.loads(
            (PROJECT_ROOT / "core" / "schemas" / "cad_plan.schema.json").read_text(encoding="utf-8")
        )

        brief_errors = validate_value(
            {
                "version": "0.1",
                "brief_id": "brief-boundary",
                "domain": "generic",
                "user_request": "Need a preview.",
                "intent": "draw_object",
                "needs_confirmation": False,
                "drawing": {"layer": "CODEX_PREVIEW"},
            },
            design_brief_schema,
        )
        plan_errors = validate_value(
            {
                "version": "0.1",
                "domain": "generic",
                "intent": "draw_object",
                "object": {"type": "cabinet", "name": "Preview Cabinet", "width": 1800, "depth": 600},
                "placement": {"mode": "absolute", "base_point": [0, 0, 0]},
                "drawing": {"layer": "CODEX_PREVIEW", "include_label": True, "include_dimensions": True},
                "confidence": 0.9,
                "needs_confirmation": False,
                "evidence": {"inferred": ["should stay in DESIGN_PROPOSAL"]},
            },
            cad_plan_schema,
        )

        self.assertIn("$.drawing is not allowed.", brief_errors)
        self.assertIn("$.evidence is not allowed.", plan_errors)

    def test_blank_shell_examples_validate_against_shell_model_schema(self) -> None:
        schema = json.loads((PROJECT_ROOT / "core/schemas/shell_model.schema.json").read_text(encoding="utf-8"))

        for example in [
            "examples/shell_models/retail_blank_shell.json",
            "examples/shell_models/office_blank_shell.json",
            "examples/shell_models/office_small_suite_shell.json",
            "examples/shell_models/residential_living_room_shell.json",
            "examples/shell_models/restaurant_small_front_shell.json",
        ]:
            with self.subTest(example=example):
                shell = json.loads((PROJECT_ROOT / example).read_text(encoding="utf-8"))
                self.assertEqual(validate_value(shell, schema), [])

    def test_function_zone_examples_validate_against_schema(self) -> None:
        schema = json.loads((PROJECT_ROOT / "core/schemas/function_zone.schema.json").read_text(encoding="utf-8"))

        for example in [
            "examples/function_zones/retail_zone_left.json",
            "examples/function_zones/office_zone_desk_band.json",
        ]:
            with self.subTest(example=example):
                zone = json.loads((PROJECT_ROOT / example).read_text(encoding="utf-8"))
                self.assertEqual(validate_value(zone, schema), [])

    def test_expanded_object_spec_examples_validate_against_schema(self) -> None:
        schema = json.loads((PROJECT_ROOT / "core/schemas/object_spec.schema.json").read_text(encoding="utf-8"))

        for example in [
            "examples/object_specs/desk_1400x700.json",
            "examples/object_specs/sofa_2200x900.json",
        ]:
            with self.subTest(example=example):
                spec = json.loads((PROJECT_ROOT / example).read_text(encoding="utf-8"))
                self.assertEqual(validate_value(spec, schema), [])

    def test_blank_shell_design_proposal_example_validates(self) -> None:
        schema = json.loads((PROJECT_ROOT / "core/schemas/design_proposal.schema.json").read_text(encoding="utf-8"))
        proposal = json.loads((PROJECT_ROOT / "examples/design_proposals/blank_shell_retail_options.json").read_text(encoding="utf-8"))

        self.assertEqual(validate_value(proposal, schema), [])


if __name__ == "__main__":
    unittest.main()
