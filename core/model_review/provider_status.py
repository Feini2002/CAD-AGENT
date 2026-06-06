"""Shared provider status and route policy for model-backed reviewers."""

from __future__ import annotations

from typing import Any


PASS_STATUSES = {"pass", "ready", "ok", "complete", "complete_for_current_scope"}
DEFAULT_MODEL_REVIEW_ROUTE = "codex_cli_local"
MODEL_REVIEW_ROUTE_POLICIES: dict[str, dict[str, Any]] = {
    "codex_cli_local": {
        "route": "codex_cli_local",
        "label": "本机 Codex CLI / GPT-5.5 Medium",
        "transport": "local_cli",
        "externalData": False,
        "requiresUserAuthorization": False,
        "allowsImages": True,
        "notes": ["默认模型策略为 gpt-5.5 + model_reasoning_effort=medium；依赖本机 Codex 登录态、模型权限和额度。"],
    },
    "local_model": {
        "route": "local_model",
        "label": "本地模型",
        "transport": "local_provider",
        "externalData": False,
        "requiresUserAuthorization": False,
        "allowsImages": True,
        "notes": ["Provider 未接入前只能作为候选路线。"],
    },
    "remote_summary_only": {
        "route": "remote_summary_only",
        "label": "远端 summary-only",
        "transport": "remote_api",
        "externalData": True,
        "requiresUserAuthorization": True,
        "allowsImages": False,
        "notes": ["只允许摘要，不外发截图；仍需用户授权。"],
    },
    "remote_full_visual": {
        "route": "remote_full_visual",
        "label": "远端完整视觉",
        "transport": "remote_api",
        "externalData": True,
        "requiresUserAuthorization": True,
        "allowsImages": True,
        "notes": ["外发截图或报告前必须取得用户明确授权。"],
    },
}


def route_policy(route: str | None = None) -> dict[str, Any]:
    """Return a copy of the route policy, falling back to local Codex CLI."""

    key = str(route or DEFAULT_MODEL_REVIEW_ROUTE)
    policy = MODEL_REVIEW_ROUTE_POLICIES.get(key, MODEL_REVIEW_ROUTE_POLICIES[DEFAULT_MODEL_REVIEW_ROUTE])
    return dict(policy)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _schema_valid(validation: dict[str, Any] | None) -> bool:
    if not isinstance(validation, dict):
        return False
    if str(validation.get("status") or "").casefold() not in PASS_STATUSES:
        return False
    return not validation.get("missingFields") and not validation.get("issues")


def build_model_provider_status(
    review: dict[str, Any] | None = None,
    *,
    validation: dict[str, Any] | None = None,
    required: bool = True,
    provider: str = "model_review",
    route: str | None = None,
    reason: str = "",
) -> dict[str, Any]:
    """Normalize invocation, availability, schema, and route state."""

    payload = _dict(review)
    route_name = str(payload.get("modelRoute") or payload.get("providerRoute") or route or DEFAULT_MODEL_REVIEW_ROUTE)
    provider_name = str(payload.get("modelProvider") or provider)
    raw_invoked = payload.get("modelInvoked")
    review_status = str(payload.get("status") or "").casefold()
    model_invoked = bool(raw_invoked) if raw_invoked is not None else bool(payload) and review_status != "unavailable"
    schema_valid = _schema_valid(validation)
    model_unavailable = model_invoked is False or (review_status == "unavailable" and not schema_valid)
    status = "unavailable" if model_unavailable else "schema_valid" if schema_valid else "schema_invalid"
    normalized_reason = str(reason or payload.get("reason") or "")
    return_code = payload.get("returnCode")
    from core.orchestrator.error_taxonomy import classify_error_category

    error_category = classify_error_category(
        review=payload,
        validation=validation,
        stderr=str(payload.get("stderr") or ""),
        return_code=return_code if isinstance(return_code, int) else None,
        reason=normalized_reason,
    )
    return {
        "status": status,
        "provider": provider_name,
        "route": route_name,
        "routePolicy": route_policy(route_name),
        "required": bool(required),
        "modelInvoked": model_invoked,
        "modelUnavailable": model_unavailable,
        "schemaValid": schema_valid,
        "blocking": bool(required and (model_unavailable or not schema_valid)),
        "reason": normalized_reason,
        "errorCategory": error_category,
    }


def with_model_provider_status(
    report: dict[str, Any],
    *,
    validation: dict[str, Any] | None = None,
    required: bool = True,
    provider: str = "model_review",
    route: str | None = None,
    reason: str = "",
) -> dict[str, Any]:
    """Attach normalized provider status while preserving legacy fields."""

    payload = dict(report)
    provider_status = build_model_provider_status(
        payload,
        validation=validation,
        required=required,
        provider=provider,
        route=route,
        reason=reason,
    )
    payload["modelProviderStatus"] = provider_status
    payload.setdefault("modelInvoked", provider_status["modelInvoked"])
    payload.setdefault("modelUnavailable", provider_status["modelUnavailable"])
    payload.setdefault("schemaValid", provider_status["schemaValid"])
    return payload
