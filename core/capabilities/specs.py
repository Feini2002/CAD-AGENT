"""Metadata catalog for Core capabilities."""

from __future__ import annotations

from typing import Any

from core.capabilities import runners


CAPABILITIES: dict[str, dict[str, Any]] = {
    "drawing_analysis.load_shell_model": {
        "capability_id": "drawing_analysis.load_shell_model",
        "title": "Load manual SHELL_MODEL",
        "summary": "Normalize hand-authored shell annotations into a validated SHELL_MODEL input.",
        "risk_level": "read_only",
        "requires_cad": False,
        "input_schema": {
            "type": "object",
            "required": ["shell_path"],
            "additionalProperties": False,
            "properties": {"shell_path": {"type": "string"}},
        },
        "output_contract": {"model_type": "shell_model", "schema": "core/schemas/shell_model.schema.json"},
        "verification_commands": [
            "& $py -m unittest tests.core.test_shell_loader",
            "& $py -m core.schemas.validator core\\schemas\\shell_model.schema.json examples\\shell_models\\retail_blank_shell.json",
        ],
        "runner": runners._drawing_analysis_load_shell_model,
    },
    "project_model.build": {
        "capability_id": "project_model.build",
        "title": "Build PROJECT_MODEL",
        "summary": "Combine DESIGN_BRIEF and DRAWING_MODEL into a minimal PROJECT_MODEL.",
        "risk_level": "read_only",
        "requires_cad": False,
        "input_schema": {
            "type": "object",
            "required": ["brief", "drawing_model"],
            "additionalProperties": False,
            "properties": {
                "brief": {"type": "object"},
                "drawing_model": {"type": "object"},
                "shell_model": {"type": "object"},
            },
        },
        "input_model_schemas": {
            "brief": "core/schemas/design_brief.schema.json",
            "drawing_model": "core/schemas/drawing_model.schema.json",
            "shell_model": "core/schemas/shell_model.schema.json",
        },
        "output_contract": {"model_type": "project_model", "schema": "core/schemas/project_model.schema.json"},
        "verification_commands": [
            "& $py -m unittest tests.core.test_project_model",
            "& $py -m core.schemas.validator core\\schemas\\project_model.schema.json examples\\project_models\\minimal_cabinet_project.json",
        ],
        "runner": runners._project_model_build,
    },
    "layout.create_candidates": {
        "capability_id": "layout.create_candidates",
        "title": "Create layout candidates",
        "summary": "Generate deterministic LAYOUT_PROPOSAL candidates from project and object models.",
        "risk_level": "read_only",
        "requires_cad": False,
        "input_schema": {
            "type": "object",
            "required": ["project_model", "object_specs"],
            "additionalProperties": False,
            "properties": {
                "project_model": {"type": "object"},
                "object_specs": {"type": "array", "items": {"type": "object"}, "minItems": 1},
                "preferences": {"type": "object"},
            },
        },
        "output_contract": {"model_type": "layout_proposal", "schema": "core/schemas/layout_proposal.schema.json"},
        "verification_commands": ["& $py -m unittest tests.core.test_layout_engine"],
        "runner": runners._layout_create_candidates,
    },
    "layout.generate_circulation_candidates": {
        "capability_id": "layout.generate_circulation_candidates",
        "title": "Generate circulation candidates",
        "summary": "Generate straight, L-shaped and along-wall circulation path candidates from PROJECT_MODEL shell context.",
        "risk_level": "read_only",
        "requires_cad": False,
        "input_schema": {
            "type": "object",
            "required": ["project_model"],
            "additionalProperties": False,
            "properties": {
                "project_model": {"type": "object"},
                "preferences": {"type": "object"},
            },
        },
        "input_model_schemas": {"project_model": "core/schemas/project_model.schema.json"},
        "output_contract": {"model_type": "circulation_model_list", "schema": "core/schemas/circulation_model.schema.json"},
        "verification_commands": [
            "& $py -m unittest tests.core.test_circulation_generation",
            "& $py -m core.schemas.validator core\\schemas\\circulation_model.schema.json examples\\circulation_models\\retail_straight_spine.json",
        ],
        "runner": runners._layout_generate_circulation_candidates,
    },
    "layout.split_function_zones": {
        "capability_id": "layout.split_function_zones",
        "title": "Split function zones",
        "summary": "Split bbox shell space around a circulation path into FUNCTION_ZONE candidates.",
        "risk_level": "read_only",
        "requires_cad": False,
        "input_schema": {
            "type": "object",
            "required": ["shell_model", "circulation_model"],
            "additionalProperties": False,
            "properties": {
                "shell_model": {"type": "object"},
                "circulation_model": {"type": "object"},
                "constraints": {"type": "object"},
            },
        },
        "input_model_schemas": {
            "shell_model": "core/schemas/shell_model.schema.json",
            "circulation_model": "core/schemas/circulation_model.schema.json",
        },
        "output_contract": {"model_type": "function_zone_list", "schema": "core/schemas/function_zone.schema.json"},
        "verification_commands": [
            "& $py -m unittest tests.core.test_zone_splitter",
            "& $py -m core.schemas.validator core\\schemas\\function_zone.schema.json examples\\function_zones\\retail_zone_left.json",
        ],
        "runner": runners._layout_split_function_zones,
    },
    "layout.create_zone_placements": {
        "capability_id": "layout.create_zone_placements",
        "title": "Create zone placements",
        "summary": "Place generic objects inside FUNCTION_ZONE candidates using block metadata or parametric fallback specs.",
        "risk_level": "read_only",
        "requires_cad": False,
        "input_schema": {
            "type": "object",
            "required": ["zones", "object_types"],
            "additionalProperties": False,
            "properties": {
                "zones": {"type": "array", "items": {"type": "object"}, "minItems": 1},
                "object_types": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                "block_library": {"type": "object"},
                "preferences": {"type": "object"},
                "path_surfaces": {"type": "array", "items": {"type": "object"}},
                "fixed_obstacles": {"type": "array", "items": {"type": "object"}},
            },
        },
        "output_contract": {"model_type": "placement_list", "schema": ""},
        "verification_commands": [
            "& $py -m unittest tests.core.test_placement_engine",
            "& $py -m unittest tests.core.test_object_engine tests.core.test_block_engine",
        ],
        "runner": runners._layout_create_zone_placements,
    },
    "plan.model_to_plans": {
        "capability_id": "plan.model_to_plans",
        "title": "Convert models to CAD_PLAN envelopes",
        "summary": "Turn OBJECT_SPEC/LAYOUT_PROPOSAL/DESIGN_PROPOSAL into safe CAD_PLAN envelopes without touching CAD.",
        "risk_level": "preview_only",
        "requires_cad": False,
        "input_schema": {
            "type": "object",
            "required": [],
            "additionalProperties": True,
            "properties": {
                "object_spec": {"type": "object"},
                "object_specs": {"type": "array", "items": {"type": "object"}},
                "layout_proposal": {"type": "object"},
                "design_proposal": {"type": "object"},
                "confirmed": {"type": "boolean"},
            },
        },
        "output_contract": {"model_type": "cad_plan_envelope_list", "schema": "core/schemas/cad_plan.schema.json"},
        "verification_commands": [
            "& $py -m unittest tests.core.test_plan_engine",
            "& $py scripts\\validate_plan.py examples\\plans\\draw_test_cabinet.json",
            "& $py scripts\\dry_run_plan.py examples\\plans\\draw_test_cabinet.json",
        ],
        "runner": runners._plan_model_to_plans,
    },
    "object.explain": {
        "capability_id": "object.explain",
        "title": "Explain OBJECT_SPEC provenance",
        "summary": "Explain object size sources, components and style evidence before drawing.",
        "risk_level": "read_only",
        "requires_cad": False,
        "input_schema": {
            "type": "object",
            "required": ["object_spec"],
            "additionalProperties": False,
            "properties": {
                "object_spec": {"type": "object"},
                "style_profile": {"type": "object"},
            },
        },
        "output_contract": {"model_type": "object_explanation", "schema": ""},
        "verification_commands": ["& $py -m unittest tests.core.test_object_explainer"],
        "runner": runners._object_explain,
    },
    "proposal.compare_layout_candidates": {
        "capability_id": "proposal.compare_layout_candidates",
        "title": "Compare layout candidates",
        "summary": "Rank layout candidates and expose tradeoffs before DESIGN_PROPOSAL/CAD_PLAN decisions.",
        "risk_level": "read_only",
        "requires_cad": False,
        "input_schema": {
            "type": "object",
            "required": ["layout_proposal"],
            "additionalProperties": False,
            "properties": {"layout_proposal": {"type": "object"}},
        },
        "output_contract": {"model_type": "proposal_comparison", "schema": ""},
        "verification_commands": ["& $py -m unittest tests.core.test_proposal_comparison"],
        "runner": runners._proposal_compare_layout_candidates,
    },
    "verification.no_cad_report": {
        "capability_id": "verification.no_cad_report",
        "title": "Build no-CAD verification report",
        "summary": "Produce an unverified VERIFICATION_REPORT shell from a CAD_PLAN without connecting to CAD.",
        "risk_level": "read_only",
        "requires_cad": False,
        "input_schema": {
            "type": "object",
            "required": ["plan_path"],
            "additionalProperties": False,
            "properties": {"plan_path": {"type": "string"}},
        },
        "output_contract": {
            "model_type": "verification_report",
            "schema": "core/schemas/verification_report.schema.json",
        },
        "verification_commands": [
            "& $py -m unittest tests.core.test_verification_report",
            "& $py scripts\\inspect_dwg.py --plan examples\\plans\\draw_test_cabinet.json --format json --no-cad",
        ],
        "runner": runners._verification_no_cad_report,
    },
    "workflow.artifact_graph": {
        "capability_id": "workflow.artifact_graph",
        "title": "Build workflow artifact graph",
        "summary": "Resolve workflow artifacts into dependency order, path checks and a machine-readable artifact index.",
        "risk_level": "read_only",
        "requires_cad": False,
        "input_schema": {
            "type": "object",
            "required": ["workflow_path"],
            "additionalProperties": False,
            "properties": {"workflow_path": {"type": "string"}},
        },
        "output_contract": {"model_type": "artifact_graph", "schema": ""},
        "verification_commands": ["& $py -m unittest tests.core.test_artifact_graph"],
        "runner": runners._workflow_artifact_graph,
    },
    "workflow.blank_shell_pipeline": {
        "capability_id": "workflow.blank_shell_pipeline",
        "title": "Run blank-shell pipeline",
        "summary": "Run SHELL_MODEL -> circulation -> zones -> placements -> proposal -> CAD_PLAN without touching CAD.",
        "risk_level": "read_only",
        "requires_cad": False,
        "input_schema": {
            "type": "object",
            "required": ["workflow_path"],
            "additionalProperties": False,
            "properties": {
                "workflow_path": {"type": "string"},
                "output_dir": {"type": "string"},
            },
        },
        "output_contract": {"model_type": "blank_shell_pipeline_report", "schema": ""},
        "verification_commands": [
            "& $py -m unittest tests.core.test_blank_shell_pipeline",
            "& $py scripts\\run_blank_shell_pipeline.py examples\\workflows\\blank_shell_layout_loop.json --output-dir output\\test_artifacts\\blank_shell_pipeline\\manual",
        ],
        "runner": runners._workflow_blank_shell_pipeline,
    },
    "benchmark.non_cad_suite": {
        "capability_id": "benchmark.non_cad_suite",
        "title": "Run non-CAD benchmark suite",
        "summary": "Run repeatable non-CAD benchmark cases and return pass/fail summaries.",
        "risk_level": "read_only",
        "requires_cad": False,
        "input_schema": {
            "type": "object",
            "required": ["suite_path"],
            "additionalProperties": False,
            "properties": {
                "suite_path": {"type": "string"},
                "output_root": {"type": "string"},
            },
        },
        "output_contract": {"model_type": "benchmark_report", "schema": ""},
        "verification_commands": ["& $py -m unittest tests.core.test_benchmarks"],
        "runner": runners._benchmark_non_cad_suite,
    },
}


ALLOWED_MATURITY = {"scaffold", "prototype", "alpha_ready", "blocked_by_cad", "blocked", "not_started"}

CAPABILITY_TRUTH: dict[str, dict[str, Any]] = {
    "project_model.build": {
        "maturity": "prototype",
        "known_limits": [
            "Builds a minimal PROJECT_MODEL from structured inputs only.",
            "Does not infer shell constraints from arbitrary DWG or PDF files.",
        ],
    },
    "drawing_analysis.load_shell_model": {
        "maturity": "prototype",
        "known_limits": [
            "Loads hand-authored shell JSON only.",
            "Does not infer shell geometry from arbitrary DWG or PDF sources.",
        ],
    },
    "layout.create_candidates": {
        "maturity": "prototype",
        "known_limits": [
            "Uses deterministic bbox, clearance and simple scoring checks.",
            "Does not yet consume SHELL_MODEL, circulation candidates or function zones as the primary layout input.",
        ],
    },
    "layout.generate_circulation_candidates": {
        "maturity": "prototype",
        "known_limits": [
            "Generates deterministic straight, L-shaped and along-wall candidates from declared shell context only.",
            "Does not solve full pathfinding or robust obstacle avoidance; blocked candidates keep structured reasons.",
        ],
    },
    "layout.split_function_zones": {
        "maturity": "prototype",
        "known_limits": [
            "Splits bbox shell candidates around the first circulation path surface only.",
            "Uses conservative no-place-zone subtraction and records uncertainty instead of robust polygon zoning.",
        ],
    },
    "layout.create_zone_placements": {
        "maturity": "prototype",
        "known_limits": [
            "Places objects with conservative bbox rules driven by zone geometry and object defaults.",
            "Does not yet optimize dense arrangements or produce final construction-grade furniture layouts.",
        ],
    },
    "plan.model_to_plans": {
        "maturity": "prototype",
        "known_limits": [
            "Produces safe CAD_PLAN envelopes without executing CAD.",
            "Does not prove geometry accuracy without validate, dry-run and readback evidence.",
        ],
    },
    "object.explain": {
        "maturity": "prototype",
        "known_limits": [
            "Explains an existing OBJECT_SPEC and optional style profile.",
            "Does not generate new object geometry or choose placement.",
        ],
    },
    "proposal.compare_layout_candidates": {
        "maturity": "prototype",
        "known_limits": [
            "Ranks existing layout candidates and exposes tradeoffs.",
            "Does not yet build a full multi-candidate DESIGN_PROPOSAL confirmation flow.",
        ],
    },
    "verification.no_cad_report": {
        "maturity": "prototype",
        "known_limits": [
            "Produces an unverified report shell without connecting to CAD.",
            "Cannot upgrade to geometry_verified without scoped entity readback evidence.",
        ],
    },
    "workflow.artifact_graph": {
        "maturity": "prototype",
        "known_limits": [
            "Checks declared workflow artifact ordering and paths.",
            "Does not validate every artifact payload against its model schema.",
        ],
    },
    "workflow.blank_shell_pipeline": {
        "maturity": "prototype",
        "known_limits": [
            "Runs hand-authored blank-shell workflow inputs only.",
            "Produces unverified non-CAD reports until real CAD execution and readback evidence are available.",
        ],
    },
    "benchmark.non_cad_suite": {
        "maturity": "prototype",
        "known_limits": [
            "Runs repeatable non-CAD benchmark cases.",
            "Current benchmark coverage is still minimal and does not represent blank-shell Alpha acceptance.",
        ],
    },
}

for _capability_id, _truth in CAPABILITY_TRUTH.items():
    if _capability_id in CAPABILITIES:
        CAPABILITIES[_capability_id].update(_truth)

