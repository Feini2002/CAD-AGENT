"""Core orchestrator: request context, routing, and workflow dispatch."""

from core.orchestrator.a_to_a_task_contract import build_a_to_a_task_contract
from core.orchestrator.route_audit_report import build_route_audit_report, write_route_audit_report
from core.orchestrator.workflow_dispatch import (
    DISPATCH_BLOCKED,
    DISPATCH_DEFERRED,
    DISPATCH_READY,
    execute_workflow_dispatch,
    load_workflow_routes,
    orchestrate_request,
    resolve_workflow_route,
)
from core.orchestrator.activation_policy import (
    ACTIVATION_MANIFEST_SPECIFIED,
    ACTIVATION_NEEDS_CLARIFICATION,
    ACTIVATION_NO_SCENE,
    ACTIVATION_SCENE_ACTIVE,
    evaluate_scene_activation,
    merge_activation_into_request_gate,
)
from core.orchestrator.scene_registry import (
    DEFAULT_SCENE_ID,
    load_scene_registry,
    match_trigger_terms,
    scene_is_registered,
    validate_scene_registry,
)
from core.orchestrator.request_context import (
    GATE_STATUS_BLOCKED,
    GATE_STATUS_NEEDS_CLARIFICATION,
    GATE_STATUS_READY,
    REQUEST_KINDS,
    build_request_context,
    evaluate_request_gate,
    validate_request_context,
)

__all__ = [
    "ACTIVATION_MANIFEST_SPECIFIED",
    "ACTIVATION_NEEDS_CLARIFICATION",
    "ACTIVATION_NO_SCENE",
    "ACTIVATION_SCENE_ACTIVE",
    "DEFAULT_SCENE_ID",
    "DISPATCH_BLOCKED",
    "DISPATCH_DEFERRED",
    "DISPATCH_READY",
    "GATE_STATUS_BLOCKED",
    "GATE_STATUS_NEEDS_CLARIFICATION",
    "GATE_STATUS_READY",
    "REQUEST_KINDS",
    "build_a_to_a_task_contract",
    "build_request_context",
    "build_route_audit_report",
    "evaluate_scene_activation",
    "evaluate_request_gate",
    "execute_workflow_dispatch",
    "load_scene_registry",
    "load_workflow_routes",
    "merge_activation_into_request_gate",
    "orchestrate_request",
    "resolve_workflow_route",
    "match_trigger_terms",
    "scene_is_registered",
    "validate_request_context",
    "validate_scene_registry",
    "write_route_audit_report",
]
