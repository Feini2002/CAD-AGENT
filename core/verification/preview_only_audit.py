"""Canonical preview-only safety audit fields for CAD execution summaries and reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.safety.policy import PREVIEW_LAYER


PREVIEW_ONLY_AUDIT_KEYS = (
    "layer",
    "saved_dwg",
    "deleted_entities",
    "modified_formal_layers",
)

PREVIEW_ONLY_AUDIT_EXPECTED: dict[str, Any] = {
    "layer": PREVIEW_LAYER,
    "saved_dwg": False,
    "deleted_entities": False,
    "modified_formal_layers": False,
}


def build_preview_only_audit(*, layer: str = PREVIEW_LAYER) -> dict[str, Any]:
    return {
        "layer": layer,
        "saved_dwg": False,
        "deleted_entities": False,
        "modified_formal_layers": False,
    }


def with_legacy_safety_aliases(audit: dict[str, Any]) -> dict[str, Any]:
    """Return audit dict including legacy keys still used by older reports and tests."""

    merged = dict(audit)
    layer = str(merged.get("layer", ""))
    merged.setdefault("writes_only_preview_layer", layer == PREVIEW_LAYER)
    merged.setdefault("saves_dwg", bool(merged.get("saved_dwg", False)))
    merged.setdefault("deletes_entities", bool(merged.get("deleted_entities", False)))
    merged.setdefault("modifies_formal_layers", bool(merged.get("modified_formal_layers", False)))
    return merged


def validate_preview_only_audit(audit: Any, *, path: str = "$.safety") -> list[str]:
    if not isinstance(audit, dict):
        return [f"{path} must be an object"]

    errors: list[str] = []
    for key in PREVIEW_ONLY_AUDIT_KEYS:
        if key not in audit:
            errors.append(f"{path}.{key} is required")

    if errors:
        return errors

    layer = audit.get("layer")
    if layer != PREVIEW_LAYER:
        errors.append(f"{path}.layer must be {PREVIEW_LAYER}, got {layer!r}")

    for key in ("saved_dwg", "deleted_entities", "modified_formal_layers"):
        if audit.get(key) is not False:
            errors.append(f"{path}.{key} must be false")

    return errors


def preview_only_audit_check(audit: Any) -> dict[str, str]:
    errors = validate_preview_only_audit(audit)
    return {
        "name": "preview_only_audit",
        "status": "pass" if not errors else "fail",
        "message": "Preview-only safety audit fields are present and valid." if not errors else "; ".join(errors),
    }


def attach_preview_only_audit(summary: dict[str, Any], *, layer: str) -> dict[str, Any]:
    summary["safety"] = with_legacy_safety_aliases(build_preview_only_audit(layer=layer))
    return summary


def execution_summary_audit_errors(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["execution summary must be a JSON object"]

    layer = str(payload.get("layer", ""))
    if not layer and isinstance(payload.get("safety"), dict):
        layer = str(payload["safety"].get("layer", ""))

    safety = payload.get("safety")
    if not isinstance(safety, dict):
        return ["$.safety is required"]

    return validate_preview_only_audit(safety)


def execution_summary_gate_failure(*, stdout: str = "", path: Path | None = None) -> str:
    payload: Any | None = None
    if stdout.strip():
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as exc:
            return f"execution summary is not valid JSON: {exc}"
    elif path is not None:
        if not path.is_file():
            return f"execution summary missing: {path}"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return f"execution summary is not valid JSON: {exc}"
    else:
        return "execution summary payload unavailable"

    errors = execution_summary_audit_errors(payload)
    if errors:
        return "execution summary preview-only audit failed: " + "; ".join(errors)
    return ""
