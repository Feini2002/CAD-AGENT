"""Semantic asset routing before ordinary CAD workflow dispatch."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.assets.system_asset_reuse import build_system_asset_reuse_workflow
from core.assets.system_asset_sedimentation import PROJECT_ROOT


ASSET_ROUTE_STATUSES = {
    "ready",
    "partial",
    "needs_asset_match",
    "needs_precise_native_source",
    "asset_registry_encoding_failed",
}


def resolve_semantic_asset_route(
    request_context: dict[str, Any],
    *,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Resolve whether a user request should enter system asset reuse before generic CAD planning."""

    phrase = str(request_context.get("user_request", "")).strip()
    if not phrase:
        return {
            "kind": "semantic_asset_route",
            "status": "not_asset_reuse_request",
            "reason": "empty user_request",
            "fallback": "ordinary_workflow_dispatch",
            "workflow": {},
        }
    workflow = build_system_asset_reuse_workflow(phrase, project_root=project_root)
    status = str(workflow.get("status", ""))
    if status in ASSET_ROUTE_STATUSES:
        route_status = status
        fallback = "system_asset_reuse_workflow"
        reason = "semantic asset workflow resolved before ordinary CAD_PLAN"
    else:
        route_status = "not_asset_reuse_request"
        fallback = "ordinary_workflow_dispatch"
        reason = "no strong system asset signal; ordinary CAD planning may proceed"
    return {
        "kind": "semantic_asset_route",
        "status": route_status,
        "reason": reason,
        "fallback": fallback,
        "workflow": workflow,
        "savedCurrentDwg": False,
    }
