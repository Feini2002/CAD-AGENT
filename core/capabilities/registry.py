"""Capability catalog and guarded runtime for reusable Core functions.

The registry is intentionally small and explicit. It gives future agents a
machine-readable way to discover what Core can do, what risk level each action
has, which inputs are expected, and which verification commands protect it.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from core.layout_engine.basic_layout import create_layout_candidates
from core.layout_engine.path_generation import generate_circulation_candidates
from core.layout_engine.placement import create_zone_placements
from core.layout_engine.zone_splitter import split_zones
from core.benchmarks.runner import run_benchmark_suite
from core.drawing_analysis.shell_loader import load_manual_shell
from core.object_engine.object_explainer import explain_object_spec
from core.plan_engine.model_to_plan import model_to_plans
from core.project_model.project_builder import build_project_model
from core.proposal_engine.proposal_comparison import compare_layout_candidates
from core.schemas.validator import load_json, validate_value
from core.verification.verification_report import build_verification_report
from core.workflows.artifact_graph import build_artifact_graph_from_workflow
from core.workflows.blank_shell_pipeline import run_blank_shell_pipeline


CapabilityRunner = Callable[[dict[str, Any]], Any]

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_schema(relative_path: str) -> dict[str, Any]:
    schema = load_json(PROJECT_ROOT / relative_path)
    if not isinstance(schema, dict):
        raise ValueError(f"Schema must be a JSON object: {relative_path}")
    return schema


def _project_model_build(payload: dict[str, Any]) -> dict[str, Any]:
    return build_project_model(
        payload["brief"],
        payload["drawing_model"],
        shell_model=payload.get("shell_model"),
    ).project_model


def _layout_create_candidates(payload: dict[str, Any]) -> dict[str, Any]:
    return create_layout_candidates(
        project_model=payload["project_model"],
        object_specs=payload["object_specs"],
        preferences=payload.get("preferences", {}),
    )


def _layout_generate_circulation_candidates(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return generate_circulation_candidates(
        payload["project_model"],
        preferences=payload.get("preferences", {}),
    )


def _layout_split_function_zones(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return split_zones(
        payload["shell_model"],
        payload["circulation_model"],
        payload.get("constraints", {}),
    )


def _layout_create_zone_placements(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return create_zone_placements(
        payload["zones"],
        object_types=payload["object_types"],
        block_library=payload.get("block_library"),
        preferences=payload.get("preferences", {}),
        path_surfaces=payload.get("path_surfaces", []),
        fixed_obstacles=payload.get("fixed_obstacles", []),
    )


def _plan_model_to_plans(payload: dict[str, Any]) -> dict[str, Any]:
    return model_to_plans(
        object_spec=payload.get("object_spec"),
        object_specs=payload.get("object_specs"),
        layout_proposal=payload.get("layout_proposal"),
        design_proposal=payload.get("design_proposal"),
        confirmed=bool(payload.get("confirmed", False)),
    )


def _object_explain(payload: dict[str, Any]) -> dict[str, Any]:
    return explain_object_spec(payload["object_spec"], style_profile=payload.get("style_profile"))


def _proposal_compare_layout_candidates(payload: dict[str, Any]) -> dict[str, Any]:
    return compare_layout_candidates(payload["layout_proposal"])


def _verification_no_cad_report(payload: dict[str, Any]) -> dict[str, Any]:
    plan_path = Path(payload["plan_path"])
    if not plan_path.is_absolute():
        plan_path = PROJECT_ROOT / plan_path
    return build_verification_report(plan_path=plan_path)


def _workflow_artifact_graph(payload: dict[str, Any]) -> dict[str, Any]:
    workflow_path = Path(payload["workflow_path"])
    if not workflow_path.is_absolute():
        workflow_path = PROJECT_ROOT / workflow_path
    graph = build_artifact_graph_from_workflow(workflow_path)
    return {
        "dependency_order": graph.dependency_order(),
        "artifacts": graph.to_index(),
        "path_checks": graph.validate_paths(PROJECT_ROOT),
    }


def _workflow_blank_shell_pipeline(payload: dict[str, Any]) -> dict[str, Any]:
    workflow_path = Path(payload["workflow_path"])
    output_dir = Path(payload.get("output_dir", "output/test_artifacts/capabilities/blank_shell_pipeline"))
    if not workflow_path.is_absolute():
        workflow_path = PROJECT_ROOT / workflow_path
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir
    return run_blank_shell_pipeline(workflow_path, output_dir=output_dir)


def _benchmark_non_cad_suite(payload: dict[str, Any]) -> dict[str, Any]:
    suite_path = Path(payload["suite_path"])
    output_root = Path(payload.get("output_root", "output/test_artifacts/benchmarks/capability"))
    if not suite_path.is_absolute():
        suite_path = PROJECT_ROOT / suite_path
    if not output_root.is_absolute():
        output_root = PROJECT_ROOT / output_root
    return run_benchmark_suite(suite_path, output_root=output_root)


def _drawing_analysis_load_shell_model(payload: dict[str, Any]) -> dict[str, Any]:
    shell_path = Path(payload["shell_path"])
    if not shell_path.is_absolute():
        shell_path = PROJECT_ROOT / shell_path
    return load_manual_shell(shell_path)


_CAPABILITIES: dict[str, dict[str, Any]] = {
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
        "runner": _drawing_analysis_load_shell_model,
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
        "runner": _project_model_build,
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
        "runner": _layout_create_candidates,
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
        "runner": _layout_generate_circulation_candidates,
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
        "runner": _layout_split_function_zones,
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
        "runner": _layout_create_zone_placements,
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
        "runner": _plan_model_to_plans,
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
        "runner": _object_explain,
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
        "runner": _proposal_compare_layout_candidates,
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
        "runner": _verification_no_cad_report,
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
        "runner": _workflow_artifact_graph,
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
        "runner": _workflow_blank_shell_pipeline,
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
        "runner": _benchmark_non_cad_suite,
    },
}


_ALLOWED_MATURITY = {"prototype", "alpha_ready", "blocked_by_cad", "not_started"}

_CAPABILITY_TRUTH: dict[str, dict[str, Any]] = {
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

for _capability_id, _truth in _CAPABILITY_TRUTH.items():
    if _capability_id in _CAPABILITIES:
        _CAPABILITIES[_capability_id].update(_truth)


def _public_spec(spec: dict[str, Any]) -> dict[str, Any]:
    data = {key: value for key, value in spec.items() if key != "runner"}
    data.pop("input_model_schemas", None)
    return deepcopy(data)


def list_capabilities() -> list[dict[str, Any]]:
    """Return the public machine-readable Core capability catalog."""

    return [_public_spec(_CAPABILITIES[key]) for key in sorted(_CAPABILITIES)]


def get_capability(capability_id: str) -> dict[str, Any]:
    """Return one public capability spec by id."""

    if capability_id not in _CAPABILITIES:
        raise KeyError(f"Unknown Core capability: {capability_id}")
    return _public_spec(_CAPABILITIES[capability_id])


def validate_capability_registry() -> list[str]:
    """Validate registry metadata without running capability implementations."""

    errors: list[str] = []
    seen_ids: set[str] = set()
    for capability_id, spec in sorted(_CAPABILITIES.items()):
        if capability_id in seen_ids:
            errors.append(f"Duplicate capability id: {capability_id}")
        seen_ids.add(capability_id)
        if capability_id != spec.get("capability_id"):
            errors.append(f"{capability_id}: capability_id does not match registry key.")
        if spec.get("risk_level") not in {"read_only", "preview_only", "requires_approval"}:
            errors.append(f"{capability_id}: invalid risk_level.")
        if spec.get("maturity") not in _ALLOWED_MATURITY:
            errors.append(f"{capability_id}: invalid maturity.")
        known_limits = spec.get("known_limits")
        if not isinstance(known_limits, list) or not known_limits or not all(isinstance(item, str) and item for item in known_limits):
            errors.append(f"{capability_id}: known_limits must be a non-empty list of strings.")
        if not isinstance(spec.get("requires_cad"), bool):
            errors.append(f"{capability_id}: requires_cad must be boolean.")
        input_schema = spec.get("input_schema")
        if not isinstance(input_schema, dict) or input_schema.get("type") != "object":
            errors.append(f"{capability_id}: input_schema must be an object schema.")
        output_contract = spec.get("output_contract")
        if not isinstance(output_contract, dict) or not output_contract.get("model_type"):
            errors.append(f"{capability_id}: output_contract.model_type is required.")
        schema_path = output_contract.get("schema") if isinstance(output_contract, dict) else ""
        if schema_path and not (PROJECT_ROOT / str(schema_path)).exists():
            errors.append(f"{capability_id}: output schema does not exist: {schema_path}")
        commands = spec.get("verification_commands")
        if not isinstance(commands, list) or not commands:
            errors.append(f"{capability_id}: verification_commands must be a non-empty list.")
    return errors


def _validate_payload(spec: dict[str, Any], payload: dict[str, Any]) -> list[str]:
    errors = validate_value(payload, spec["input_schema"])
    for field, schema_path in spec.get("input_model_schemas", {}).items():
        if field in payload and isinstance(payload[field], dict):
            field_errors = validate_value(payload[field], _load_schema(schema_path))
            errors.extend(
                f"{field}{error[1:]}" if error.startswith("$") else f"{field}: {error}"
                for error in field_errors
            )
    return errors


def run_capability(capability_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Validate inputs, run a Core capability, and wrap the result."""

    if capability_id not in _CAPABILITIES:
        return {"status": "unknown_capability", "capability_id": capability_id, "errors": [f"Unknown Core capability: {capability_id}"]}
    spec = _CAPABILITIES[capability_id]
    errors = _validate_payload(spec, payload)
    if errors:
        return {
            "status": "invalid_input",
            "capability_id": capability_id,
            "errors": errors,
            "output_model_type": spec["output_contract"]["model_type"],
            "output": {},
        }

    try:
        output = spec["runner"](payload)
    except Exception as exc:  # pragma: no cover - kept as a runtime safety wrapper
        return {
            "status": "failed",
            "capability_id": capability_id,
            "errors": [str(exc)],
            "output_model_type": spec["output_contract"]["model_type"],
            "output": {},
        }

    return {
        "status": "ok",
        "capability_id": capability_id,
        "errors": [],
        "output_model_type": spec["output_contract"]["model_type"],
        "output": output,
        "evidence": {
            "requires_cad": spec["requires_cad"],
            "risk_level": spec["risk_level"],
            "verification_commands": list(spec["verification_commands"]),
        },
    }
