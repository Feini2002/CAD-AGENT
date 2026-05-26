"""Unified REQUEST_CONTEXT model and gate evaluation for Core Orchestrator."""

from __future__ import annotations

from typing import Any


REQUEST_KINDS = (
    "draw",
    "layout",
    "project_sample",
    "cad_validation",
    "proposal",
    "read_drawing",
    "general",
)

INPUT_KEYS = (
    "design_brief",
    "object_spec",
    "cad_plan",
    "project_sample_manifest",
    "shell_model",
    "project_model",
    "block_library",
    "layout_proposal",
    "design_proposal",
)

GATE_STATUS_READY = "ready"
GATE_STATUS_BLOCKED = "blocked"
GATE_STATUS_NEEDS_CLARIFICATION = "needs_clarification"

CAD_EXECUTION_KINDS = frozenset({"draw", "cad_validation", "project_sample"})
STRUCTURED_INPUT_KEYS = frozenset(
    {
        "design_brief",
        "object_spec",
        "cad_plan",
        "project_sample_manifest",
        "shell_model",
        "project_model",
        "layout_proposal",
        "design_proposal",
    }
)

KIND_REQUIRED_INPUTS: dict[str, frozenset[str]] = {
    "draw": frozenset({"design_brief", "object_spec", "cad_plan"}),
    "layout": frozenset({"shell_model", "project_model", "layout_proposal"}),
    "project_sample": frozenset({"project_sample_manifest"}),
    "cad_validation": frozenset({"cad_plan", "project_sample_manifest"}),
    "proposal": frozenset({"design_proposal", "layout_proposal", "project_model"}),
    "read_drawing": frozenset({"shell_model", "project_sample_manifest"}),
    "general": frozenset(),
}


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_request_context(context: dict[str, Any]) -> list[str]:
    """Semantic validation beyond JSON Schema."""

    errors: list[str] = []
    _require(isinstance(context, dict), "context must be an object.", errors)
    if not isinstance(context, dict):
        return errors

    _require(str(context.get("version", "")) == "0.1", "version must be 0.1.", errors)
    _require(bool(str(context.get("context_id", "")).strip()), "context_id is required.", errors)

    request_kind = str(context.get("request_kind", ""))
    _require(request_kind in REQUEST_KINDS, f"request_kind must be one of {REQUEST_KINDS}.", errors)

    inputs = context.get("inputs", {})
    _require(isinstance(inputs, dict), "inputs must be an object.", errors)
    if isinstance(inputs, dict):
        available = inputs.get("available", [])
        _require(isinstance(available, list), "inputs.available must be an array.", errors)
        if isinstance(available, list):
            for index, key in enumerate(available):
                _require(
                    key in INPUT_KEYS,
                    f"inputs.available[{index}] is not a supported input key.",
                    errors,
                )
        paths = inputs.get("paths", {})
        _require(paths is None or isinstance(paths, dict), "inputs.paths must be an object.", errors)
        if isinstance(paths, dict) and isinstance(available, list):
            for path_key in paths:
                if path_key not in available:
                    errors.append(f"inputs.paths.{path_key} is set but {path_key} is not listed in inputs.available.")

    cad_policy = context.get("cad_policy", {})
    _require(isinstance(cad_policy, dict), "cad_policy must be an object.", errors)
    if isinstance(cad_policy, dict) and cad_policy.get("allow_cad") and not cad_policy.get("preview_only", True):
        errors.append("cad_policy.preview_only must stay true unless formal-layer approval is recorded elsewhere.")

    clarification = context.get("clarification", {})
    _require(isinstance(clarification, dict), "clarification must be an object.", errors)
    if isinstance(clarification, dict) and clarification.get("needs_clarification"):
        questions = clarification.get("questions", [])
        _require(
            isinstance(questions, list) and len(questions) > 0,
            "clarification.questions must be non-empty when needs_clarification is true.",
            errors,
        )

    return errors


def build_request_context(
    *,
    context_id: str,
    request_kind: str,
    user_request: str = "",
    scene_hint: str = "no_scene",
    available_inputs: list[str] | None = None,
    input_paths: dict[str, str] | None = None,
    allow_cad: bool = False,
    preview_only: bool = True,
    cad_environment_available: bool | None = None,
    needs_clarification: bool = False,
    clarification_questions: list[str] | None = None,
    project_manifest: dict[str, str] | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    """Build a normalized REQUEST_CONTEXT dictionary."""

    cad_policy: dict[str, Any] = {
        "allow_cad": bool(allow_cad),
        "preview_only": bool(preview_only),
    }
    if cad_environment_available is not None:
        cad_policy["cad_environment_available"] = bool(cad_environment_available)

    context: dict[str, Any] = {
        "version": "0.1",
        "context_id": context_id,
        "request_kind": request_kind,
        "user_request": user_request,
        "scene_hint": scene_hint,
        "inputs": {
            "available": list(available_inputs or []),
            "paths": dict(input_paths or {}),
        },
        "cad_policy": cad_policy,
        "clarification": {
            "needs_clarification": bool(needs_clarification),
            "questions": list(clarification_questions or []),
        },
    }
    if project_manifest:
        context["project_manifest"] = dict(project_manifest)
    if notes:
        context["notes"] = list(notes)
    return context


def _available_input_set(context: dict[str, Any]) -> set[str]:
    inputs = context.get("inputs", {})
    if not isinstance(inputs, dict):
        return set()
    available = inputs.get("available", [])
    if not isinstance(available, list):
        return set()
    return {str(key) for key in available if key in INPUT_KEYS}


def _has_actionable_request(context: dict[str, Any], available: set[str]) -> bool:
    user_request = str(context.get("user_request", "")).strip()
    if user_request:
        return True
    return bool(available.intersection(STRUCTURED_INPUT_KEYS))


def evaluate_request_gate(context: dict[str, Any]) -> dict[str, Any]:
    """Evaluate whether orchestrator may dispatch workflows or execute CAD."""

    schema_errors = validate_request_context(context)
    available = _available_input_set(context)
    request_kind = str(context.get("request_kind", "general"))
    cad_policy = context.get("cad_policy", {}) if isinstance(context.get("cad_policy"), dict) else {}
    clarification = context.get("clarification", {}) if isinstance(context.get("clarification"), dict) else {}

    blocked_reasons: list[str] = list(schema_errors)
    checks: list[dict[str, str]] = []

    if schema_errors:
        checks.append(
            {
                "name": "request_context_semantics",
                "status": "fail",
                "message": "; ".join(schema_errors[:3]),
            }
        )
    else:
        checks.append(
            {
                "name": "request_context_semantics",
                "status": "pass",
                "message": "REQUEST_CONTEXT semantic validation passed.",
            }
        )

    if clarification.get("needs_clarification"):
        blocked_reasons.append("clarification required before workflow dispatch")
        checks.append(
            {
                "name": "clarification_gate",
                "status": "fail",
                "message": "needs_clarification is true.",
            }
        )
    else:
        checks.append(
            {
                "name": "clarification_gate",
                "status": "pass",
                "message": "no pending clarification.",
            }
        )

    if not _has_actionable_request(context, available):
        blocked_reasons.append("missing user_request and structured inputs")
        checks.append(
            {
                "name": "actionable_request",
                "status": "fail",
                "message": "Provide user_request text or at least one structured input.",
            }
        )
    else:
        checks.append(
            {
                "name": "actionable_request",
                "status": "pass",
                "message": "user_request or structured inputs present.",
            }
        )

    required_for_kind = KIND_REQUIRED_INPUTS.get(request_kind, frozenset())
    if required_for_kind and not available.intersection(required_for_kind):
        blocked_reasons.append(
            f"request_kind={request_kind!r} requires one of: {', '.join(sorted(required_for_kind))}"
        )
        checks.append(
            {
                "name": "request_kind_inputs",
                "status": "fail",
                "message": f"Missing required inputs for {request_kind}.",
            }
        )
    else:
        checks.append(
            {
                "name": "request_kind_inputs",
                "status": "pass",
                "message": f"Inputs satisfy request_kind={request_kind}.",
            }
        )

    wants_cad = request_kind in CAD_EXECUTION_KINDS
    allow_cad = bool(cad_policy.get("allow_cad"))
    if wants_cad and not allow_cad:
        blocked_reasons.append(f"request_kind={request_kind!r} requires cad_policy.allow_cad=true")
        checks.append(
            {
                "name": "cad_policy_allow",
                "status": "fail",
                "message": "CAD execution requested but allow_cad is false.",
            }
        )
    else:
        checks.append(
            {
                "name": "cad_policy_allow",
                "status": "pass",
                "message": "CAD policy compatible with request_kind.",
            }
        )

    if clarification.get("needs_clarification"):
        status = GATE_STATUS_NEEDS_CLARIFICATION
    elif blocked_reasons:
        status = GATE_STATUS_BLOCKED
    else:
        status = GATE_STATUS_READY

    may_execute_cad = status == GATE_STATUS_READY and allow_cad and wants_cad
    may_dispatch_workflow = status == GATE_STATUS_READY

    return {
        "version": "0.1",
        "context_id": context.get("context_id"),
        "status": status,
        "blocked_reasons": blocked_reasons,
        "checks": checks,
        "may_execute_cad": may_execute_cad,
        "may_dispatch_workflow": may_dispatch_workflow,
        "may_generate_cad_plan": may_dispatch_workflow,
        "request_kind": request_kind,
        "available_inputs": sorted(available),
    }


def gate_blocks_cad_execution(gate_report: dict[str, Any]) -> bool:
    """Return True when CAD execution must not proceed."""

    return not bool(gate_report.get("may_execute_cad"))
