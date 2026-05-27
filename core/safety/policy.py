"""Callable safety policy for preview-first CAD Agent operations."""

from __future__ import annotations

from typing import Any


PREVIEW_LAYER = "CODEX_PREVIEW"
DIAGNOSTIC_LAYER = "CODEX_DIAGNOSTIC"
PREVIEW_ALLOWED_LAYERS = frozenset({PREVIEW_LAYER, DIAGNOSTIC_LAYER})
DESTRUCTIVE_INTENTS = {"delete_object"}
WRITE_OPERATIONS = {"save", "overwrite", "delete"}


def _approval_allows(approval: dict[str, Any] | None, key: str) -> bool:
    return bool(approval and approval.get(key) is True)


def evaluate_plan_safety(
    plan: dict[str, Any],
    *,
    approval: dict[str, Any] | None = None,
    requested_operation: str = "execute",
) -> dict[str, Any]:
    """Evaluate whether a CAD plan can proceed under conservative defaults."""

    violations: list[str] = []
    warnings: list[str] = []
    drawing = plan.get("drawing", {}) if isinstance(plan.get("drawing"), dict) else {}
    layer = drawing.get("layer")
    intent = plan.get("intent")

    if layer != PREVIEW_LAYER and not _approval_allows(approval, "allow_formal_layer"):
        violations.append("formal_layer_requires_approval")

    if plan.get("needs_confirmation") and not _approval_allows(approval, "allow_unconfirmed"):
        violations.append("plan_needs_confirmation")

    if intent in DESTRUCTIVE_INTENTS and not _approval_allows(approval, "allow_delete"):
        violations.append("delete_requires_approval")

    if requested_operation in {"save", "overwrite"} and not _approval_allows(approval, "allow_save"):
        violations.append(f"{requested_operation}_requires_approval")
    if requested_operation == "delete" and not _approval_allows(approval, "allow_delete"):
        violations.append("delete_requires_approval")

    if approval and not approval.get("approved_by"):
        warnings.append("approval_missing_approved_by")

    allowed = not violations
    summary = (
        f"Allowed preview execution on {PREVIEW_LAYER}."
        if allowed and layer == PREVIEW_LAYER
        else "Plan requires explicit approval before execution."
    )
    return {
        "allowed": allowed,
        "summary": summary,
        "violations": violations,
        "warnings": warnings,
        "layer": layer,
        "intent": intent,
        "requested_operation": requested_operation,
        "approval": approval or {},
    }


def assert_plan_is_safe(
    plan: dict[str, Any],
    *,
    approval: dict[str, Any] | None = None,
    requested_operation: str = "execute",
) -> dict[str, Any]:
    decision = evaluate_plan_safety(plan, approval=approval, requested_operation=requested_operation)
    if not decision["allowed"]:
        readable = {
            "plan_needs_confirmation": "needs confirmation",
            "formal_layer_requires_approval": "formal layer requires approval",
            "delete_requires_approval": "delete requires approval",
            "save_requires_approval": "save requires approval",
            "overwrite_requires_approval": "overwrite requires approval",
        }
        details = [f"{code} ({readable.get(code, code)})" for code in decision["violations"]]
        raise ValueError("CAD safety policy blocked plan: " + ", ".join(details))
    return decision
