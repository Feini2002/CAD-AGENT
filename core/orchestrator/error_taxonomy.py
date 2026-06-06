"""Canonical local/model error taxonomy for model-agent orchestration."""

from __future__ import annotations

from typing import Any


PROVIDER_UNAVAILABLE = "provider_unavailable"
NETWORK_UNAVAILABLE = "network_unavailable"
SCHEMA_INVALID = "schema_invalid"
CONTEXT_EXPORT_BLOCKED = "context_export_blocked"
MODEL_BUSINESS_BLOCKED = "model_business_blocked"
HANDOFF_INVALID = "handoff_invalid"
TOOL_CONTRACT_BLOCKED = "tool_contract_blocked"
CAD_EVIDENCE_MISSING = "cad_evidence_missing"
VISUAL_EVIDENCE_MISSING = "visual_evidence_missing"
CLOSEOUT_BLOCKED = "closeout_blocked"

NETWORK_CLUES = (
    "websocket",
    "https",
    "dns",
    "api.openai.com",
    "connection refused",
    "connection reset",
    "network",
    "socket",
    "套接字",
    "访问权限不允许访问套接字",
)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _schema_valid(validation: dict[str, Any] | None) -> bool:
    payload = _dict(validation)
    return (
        str(payload.get("status") or "").casefold() in {"pass", "ready", "ok", "schema_valid"}
        and not payload.get("missingFields")
        and not payload.get("issues")
    )


def _schema_invalid(validation: dict[str, Any] | None) -> bool:
    payload = _dict(validation)
    return bool(payload) and not _schema_valid(payload)


def classify_error_category(
    *,
    review: dict[str, Any] | None = None,
    validation: dict[str, Any] | None = None,
    stderr: str = "",
    return_code: int | None = None,
    reason: str = "",
) -> str:
    """Return the most specific stable error category for a model/local failure."""

    text = " ".join(str(item or "") for item in [stderr, reason, _dict(review).get("reason")]).casefold()
    if any(clue in text for clue in NETWORK_CLUES):
        return NETWORK_UNAVAILABLE
    if "context_export_blocked" in text or "context_leak_blocked" in text or "unauthorized_local_path" in text:
        return CONTEXT_EXPORT_BLOCKED
    if _schema_invalid(validation):
        return SCHEMA_INVALID

    payload = _dict(review)
    status = str(payload.get("status") or "").casefold()
    model_invoked = payload.get("modelInvoked")
    if status == "unavailable" and model_invoked is True and _schema_valid(validation):
        return MODEL_BUSINESS_BLOCKED
    if return_code not in (None, 0):
        return PROVIDER_UNAVAILABLE
    if status == "unavailable" or model_invoked is False:
        return PROVIDER_UNAVAILABLE
    if status in {"fail", "blocked", "needs_more_evidence"}:
        return MODEL_BUSINESS_BLOCKED
    return ""
