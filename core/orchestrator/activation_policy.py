"""Scene activation policy: when to enable a scene module vs stay on no_scene."""

from __future__ import annotations

from typing import Any

from core.orchestrator.scene_registry import (
    DEFAULT_SCENE_ID,
    get_scene,
    match_trigger_terms,
    scene_is_registered,
)


ACTIVATION_NO_SCENE = "no_scene"
ACTIVATION_SCENE_ACTIVE = "scene_active"
ACTIVATION_MANIFEST_SPECIFIED = "manifest_specified"
ACTIVATION_HINT_SPECIFIED = "hint_specified"
ACTIVATION_NEEDS_CLARIFICATION = "needs_clarification"
ACTIVATION_BLOCKED = "blocked"


def _check(name: str, status: str, message: str) -> dict[str, str]:
    return {"name": name, "status": status, "message": message}


def _manifest_scene_id(request_context: dict[str, Any]) -> str | None:
    manifest = request_context.get("project_manifest")
    if not isinstance(manifest, dict):
        return None
    scene_id = manifest.get("scene_id")
    if isinstance(scene_id, str) and scene_id.strip():
        return scene_id.strip()
    return None


def _scene_hint(request_context: dict[str, Any]) -> str:
    hint = str(request_context.get("scene_hint", DEFAULT_SCENE_ID)).strip()
    return hint or DEFAULT_SCENE_ID


def evaluate_scene_activation(
    request_context: dict[str, Any],
    registry: dict[str, Any],
    *,
    explicit_scene_id: str | None = None,
) -> dict[str, Any]:
    """Resolve which scene module may be activated for a REQUEST_CONTEXT."""

    checks: list[dict[str, str]] = []
    blocked_reasons: list[str] = []
    candidate_scene_ids: list[str] = []
    match_reason = ""
    confidence = 1.0
    activation_status = ACTIVATION_NO_SCENE
    activated_scene_id = DEFAULT_SCENE_ID

    manifest_scene = _manifest_scene_id(request_context)
    if manifest_scene:
        if scene_is_registered(registry, manifest_scene):
            activated_scene_id = manifest_scene
            activation_status = ACTIVATION_MANIFEST_SPECIFIED
            match_reason = f"project_manifest.scene_id={manifest_scene}"
            checks.append(_check("manifest_scene", "pass", match_reason))
        else:
            activation_status = ACTIVATION_BLOCKED
            activated_scene_id = DEFAULT_SCENE_ID
            reason = f"project_manifest.scene_id={manifest_scene!r} is not registered"
            blocked_reasons.append(reason)
            match_reason = reason
            checks.append(_check("manifest_scene", "fail", reason))
    elif explicit_scene_id and explicit_scene_id != DEFAULT_SCENE_ID:
        if scene_is_registered(registry, explicit_scene_id):
            activated_scene_id = explicit_scene_id
            activation_status = ACTIVATION_SCENE_ACTIVE
            match_reason = f"explicit_scene_id={explicit_scene_id}"
            checks.append(_check("explicit_scene", "pass", match_reason))
        else:
            activation_status = ACTIVATION_BLOCKED
            blocked_reasons.append(f"explicit_scene_id={explicit_scene_id!r} is not registered")
            checks.append(_check("explicit_scene", "fail", blocked_reasons[-1]))
    else:
        hint = _scene_hint(request_context)
        if hint != DEFAULT_SCENE_ID and scene_is_registered(registry, hint):
            activated_scene_id = hint
            activation_status = ACTIVATION_HINT_SPECIFIED
            match_reason = f"scene_hint={hint}"
            checks.append(_check("scene_hint", "pass", match_reason))
        else:
            user_request = str(request_context.get("user_request", ""))
            matches = match_trigger_terms(registry, user_request)
            candidate_scene_ids = [str(scene["scene_id"]) for scene in matches]
            if len(matches) == 0:
                activation_status = ACTIVATION_NO_SCENE
                activated_scene_id = DEFAULT_SCENE_ID
                match_reason = "no scene trigger match; default no_scene"
                checks.append(_check("trigger_match", "pass", match_reason))
            elif len(matches) == 1:
                activated_scene_id = str(matches[0]["scene_id"])
                activation_status = ACTIVATION_SCENE_ACTIVE
                match_reason = f"single trigger match for {activated_scene_id}"
                checks.append(_check("trigger_match", "pass", match_reason))
            else:
                activation_status = ACTIVATION_NEEDS_CLARIFICATION
                activated_scene_id = DEFAULT_SCENE_ID
                confidence = 0.4
                match_reason = f"ambiguous triggers: {', '.join(candidate_scene_ids)}"
                blocked_reasons.append("multiple scene trigger matches; clarification required")
                checks.append(_check("trigger_match", "fail", match_reason))

    scene_record = get_scene(registry, activated_scene_id) if activated_scene_id != DEFAULT_SCENE_ID else get_scene(
        registry, DEFAULT_SCENE_ID
    )
    may_use_scene_module = activated_scene_id != DEFAULT_SCENE_ID and activation_status in {
        ACTIVATION_SCENE_ACTIVE,
        ACTIVATION_MANIFEST_SPECIFIED,
        ACTIVATION_HINT_SPECIFIED,
    }
    must_use_core_workflow = True
    may_bypass_core = bool(scene_record.get("may_bypass_core")) if isinstance(scene_record, dict) else False
    if may_bypass_core:
        activation_status = ACTIVATION_BLOCKED
        activated_scene_id = DEFAULT_SCENE_ID
        may_use_scene_module = False
        blocked_reasons.append("scene module may_bypass_core is forbidden")
        checks.append(_check("core_only_execution", "fail", "scene may not bypass Core"))

    checks.append(
        _check(
            "core_only_execution",
            "pass" if must_use_core_workflow and not may_bypass_core else "fail",
            "scene modules must route through Core workflows",
        )
    )

    return {
        "version": "0.1",
        "context_id": request_context.get("context_id"),
        "activation_status": activation_status,
        "activated_scene_id": activated_scene_id,
        "confidence": confidence,
        "candidate_scene_ids": candidate_scene_ids,
        "match_reason": match_reason,
        "may_use_scene_module": may_use_scene_module,
        "must_use_core_workflow": must_use_core_workflow,
        "blocked_reasons": blocked_reasons,
        "checks": checks,
        "clarification_required": activation_status == ACTIVATION_NEEDS_CLARIFICATION,
    }


def merge_activation_into_request_gate(
    request_context: dict[str, Any],
    gate_report: dict[str, Any],
    activation_report: dict[str, Any],
) -> dict[str, Any]:
    """Apply scene activation outcomes onto a request gate report."""

    merged = dict(gate_report)
    merged["scene_activation"] = activation_report
    merged["activated_scene_id"] = activation_report.get("activated_scene_id", DEFAULT_SCENE_ID)

    if activation_report.get("activation_status") == ACTIVATION_NEEDS_CLARIFICATION:
        merged["status"] = "needs_clarification"
        merged["may_dispatch_workflow"] = False
        merged["may_execute_cad"] = False
        merged["may_generate_cad_plan"] = False
        reasons = list(merged.get("blocked_reasons", []))
        reasons.extend(activation_report.get("blocked_reasons", []))
        merged["blocked_reasons"] = reasons
    elif activation_report.get("activation_status") == ACTIVATION_BLOCKED:
        merged["status"] = "blocked"
        merged["may_dispatch_workflow"] = False
        merged["may_execute_cad"] = False
        merged["may_generate_cad_plan"] = False
        reasons = list(merged.get("blocked_reasons", []))
        reasons.extend(activation_report.get("blocked_reasons", []))
        merged["blocked_reasons"] = reasons

    return merged
