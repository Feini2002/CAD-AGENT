"""No-CAD adaptive replay planner for CAD foundation training."""

from __future__ import annotations

from typing import Any

from core.safety.policy import PREVIEW_LAYER
from core.training.capability_growth_profile import VALID_REPLAY_MODES


def _safety_boundaries() -> dict[str, Any]:
    return {
        "cadExecution": {
            "status": "preview_only",
            "targetLayer": PREVIEW_LAYER,
            "saveCurrentDwg": False,
            "deleteEntities": False,
            "modifyFormalLayers": False,
            "requiresValidateAndDryRun": True,
            "role": "deterministic_runner_unchanged",
        },
        "worker": {
            "status": "not_required",
            "deployRequired": False,
            "allowedRole": "future_trace_summary_only",
            "forbidden": [
                "local_shell_execution",
                "cad_mcp_execution",
                "autocad_control",
                "current_dwg_save",
                "full_prompt_or_full_cad_upload",
            ],
        },
        "dataBloat": {
            "status": "guarded",
            "factSourceWriteAllowed": False,
            "workbenchSyncAllowed": False,
            "derivedArtifactsAreFactSources": False,
        },
        "modelAndAtoA": {
            "status": "guarded",
            "modelMayExecuteTools": False,
            "unregisteredAgentsMayPassGate": False,
        },
    }


def route_adaptive_training_request(
    *,
    request_kind: str,
    capability_ids: list[str],
    explicit_minimal_smoke: bool = False,
    has_standard_source: bool = False,
    durable_promotion_requested: bool = False,
) -> dict[str, Any]:
    requested_ids = [str(capability_id) for capability_id in capability_ids]
    kind = str(request_kind)
    if explicit_minimal_smoke or kind in {"quick_trial", "smoke", "smoke_replay", "api_probe"}:
        replay_mode = "smoke_replay"
        route = "quick_trial"
        accepted_low = True
        promotion_level = "observation"
    elif has_standard_source or kind in {"standard_replay", "source_spec", "style_standard", "asset_source"}:
        replay_mode = "standard_replay"
        route = "focused_retraining" if requested_ids else "standard_replay"
        accepted_low = False
        promotion_level = "candidate"
    elif kind == "project_execution":
        replay_mode = "growth_replay"
        route = "project_execution"
        accepted_low = False
        promotion_level = "observation"
    else:
        replay_mode = "growth_replay"
        route = "focused_retraining" if kind in {"focused_retraining", "only", "single_capability"} else "formal_acceptance"
        accepted_low = False
        promotion_level = "candidate" if route == "focused_retraining" else "systemized"

    formal_acceptance_required = bool(durable_promotion_requested or kind in {"formal_acceptance", "workbench_acceptance"})
    if kind == "all-31" and not durable_promotion_requested:
        formal_acceptance_required = False
        route = "focused_retraining" if len(requested_ids) == 1 else "batch_replay"

    return {
        "schemaVersion": "adaptive-training-route/v1",
        "status": "pass",
        "requestKind": kind,
        "route": route,
        "replayMode": replay_mode,
        "promotionLevel": promotion_level,
        "acceptedLowExpression": accepted_low,
        "acceptedLowExpressionReason": "explicit minimal smoke request" if accepted_low else "",
        "formalAcceptanceRequired": formal_acceptance_required,
        "scope": {
            "mode": "focused" if len(requested_ids) == 1 and route != "quick_trial" else ("quick_trial" if route == "quick_trial" else "batch"),
            "requestedCapabilityIds": requested_ids,
            "fullBatchAllowed": route in {"formal_acceptance", "batch_replay"} and not len(requested_ids) == 1,
        },
        "cadExecution": {
            "cadExecutionAllowed": route != "quick_trial",
            "deterministicProofRequired": True,
            "profilesAreUpstreamContextOnly": route == "project_execution",
            "targetLayer": PREVIEW_LAYER,
            "savedCurrentDwg": False,
        },
        "safetyBoundaries": _safety_boundaries(),
    }


def disabled_adaptive_replay_plan(replay_mode: str = "smoke_replay") -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "status": "disabled",
        "replayMode": replay_mode,
        "reason": "smoke replay keeps historical runner behavior and records no adaptive growth.",
        "items": [],
        "notChecked": [
            "能力成长画像",
            "经验提炼器",
            "对象训练反哺",
            "工作台同步",
        ],
        "notImplemented": [
            "Worker adaptive trace",
            "profile fact-source promotion",
        ],
        "safetyBoundaries": _safety_boundaries(),
    }


def _profile_map(capability_profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(profile.get("capabilityId", "")): profile
        for profile in capability_profile.get("profiles", [])
        if isinstance(profile, dict)
    }


def _target_level(replay_mode: str, profile: dict[str, Any]) -> str:
    minimum = str(profile.get("minimumExpressionLevel") or profile.get("expressionLevel") or "")
    if minimum:
        return minimum
    if replay_mode == "standard_replay":
        return "standard"
    if replay_mode == "growth_replay":
        return "growth"
    return "smoke"


def build_adaptive_replay_plan(
    *,
    replay_mode: str,
    scope: dict[str, Any],
    capability_profile: dict[str, Any],
    allow_low_expression: bool = False,
) -> dict[str, Any]:
    if replay_mode not in VALID_REPLAY_MODES:
        return {
            "schemaVersion": 1,
            "status": "blocked",
            "replayMode": replay_mode,
            "reason": "unsupported_replay_mode",
            "items": [],
            "safetyBoundaries": _safety_boundaries(),
        }
    if replay_mode == "smoke_replay":
        return disabled_adaptive_replay_plan(replay_mode)
    if capability_profile.get("status") == "blocked":
        return {
            "schemaVersion": 1,
            "status": "blocked",
            "replayMode": replay_mode,
            "reason": str(capability_profile.get("reason") or "capability_profile_blocked"),
            "items": [],
            "safetyBoundaries": _safety_boundaries(),
        }

    profiles = _profile_map(capability_profile)
    requested_ids = [str(capability_id) for capability_id in scope.get("requestedCapabilityIds", [])]
    items = []
    for capability_id in requested_ids:
        profile = profiles.get(capability_id, {})
        lessons = profile.get("transferableLessons", [])
        lesson_ids = [
            str(lesson.get("lessonId"))
            for lesson in lessons
            if isinstance(lesson, dict) and lesson.get("lessonId")
        ]
        target_level = _target_level(replay_mode, profile)
        required_features = list(profile.get("requiredFeatureSet", [])) if isinstance(profile.get("requiredFeatureSet"), list) else []
        items.append(
            {
                "capabilityId": capability_id,
                "targetExpressionLevel": target_level,
                "baselineExpressionLevel": target_level,
                "profileVersionUsed": str(profile.get("profileVersion") or "generated-default-v1"),
                "profileRefs": [ref for ref in profile.get("sourceRefs", []) if isinstance(ref, dict)],
                "consumedLessonIds": lesson_ids,
                "requiredFeatures": required_features,
                "whyExpressionLevelChosen": (
                    f"{replay_mode} consumes capability profile and keeps the minimum expression level at {target_level}."
                ),
                "acceptedLowExpression": bool(allow_low_expression and target_level == "smoke"),
                "acceptedLowExpressionReason": "caller explicitly allowed low expression"
                if allow_low_expression and target_level == "smoke"
                else "",
                "doesNotUpdateProfile": True,
                "allowedExemptions": ["explicit_allow_low_expression"] if allow_low_expression else [],
                "evidenceRequired": [
                    "CAD_PLAN validate pass",
                    "dry-run pass",
                    "CODEX_PREVIEW created handles readback",
                    "preview layer write guard",
                    "expression regression guard pass",
                ],
                "riskLevel": "medium" if replay_mode == "growth_replay" else "high",
                "aToAContractRequired": replay_mode == "standard_replay",
                "workerTraceAllowed": False,
                "cadExecutionAllowed": True,
                "notChecked": [
                    "用户人工视觉验收",
                    "工作台同步",
                    "项目交付准备度",
                ],
                "notImplemented": ["Worker adaptive trace"],
            }
        )

    return {
        "schemaVersion": 1,
        "status": "pass",
        "replayMode": replay_mode,
        "route": "focused_retraining" if scope.get("mode") == "focused" else "formal_acceptance",
        "allowLowExpression": bool(allow_low_expression),
        "items": items,
        "safetyBoundaries": _safety_boundaries(),
    }
