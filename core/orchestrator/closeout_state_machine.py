"""Deterministic closeout state classification for delivery claims."""

from __future__ import annotations

from typing import Any


STATE_MACHINE_VERSION = "closeout-state-machine/v1"
PREVIEW_LAYER = "CODEX_PREVIEW"
FAKE_DRIVER_MODES = {"fake", "fake_driver", "fake_preview", "fake_driver_preflight"}


def _is_false(value: Any) -> bool:
    return value is False or str(value).casefold() in {"false", "no", "0", "fail", "missing", "not_ok", "not_verified"}


def evaluate_closeout_state(
    *,
    model_ok: bool = True,
    schema_valid: bool = True,
    model_required: bool = False,
    validation_ok: bool = True,
    dry_run_ok: bool = True,
    readback_ok: bool = False,
    target_layer: str = PREVIEW_LAYER,
    saved_current_dwg: bool = False,
    driver_mode: str = "",
    cadGeometryVerified: bool | None = None,
    visual_acceptance_ok: bool = False,
    visual_required: bool = True,
    neighbor_protection_ok: bool = True,
    neighbor_protection_required: bool = True,
) -> dict[str, Any]:
    """Map local evidence booleans to a stable delivery state."""

    required = [
        "schemaValid=true when model output is required",
        "validate_plan=pass",
        "dry_run=pass",
        "created_handles_readback=ok",
        f"targetLayer={PREVIEW_LAYER}",
        "savedCurrentDwg=false",
    ]
    if visual_required:
        required.append("visual_acceptance_review=pass")
    if neighbor_protection_required:
        required.append("neighbor_protection=pass")

    missing: list[str] = []
    if model_required and (not model_ok or not schema_valid):
        missing.append("schemaValid=true when model output is required")
    if not validation_ok:
        missing.append("validate_plan=pass")
    if not dry_run_ok:
        missing.append("dry_run=pass")
    if not readback_ok:
        missing.append("created_handles_readback=ok")
    if target_layer != PREVIEW_LAYER:
        missing.append(f"targetLayer={PREVIEW_LAYER}")
    if saved_current_dwg is not False:
        missing.append("savedCurrentDwg=false")
    if str(driver_mode or "").casefold() in FAKE_DRIVER_MODES or _is_false(cadGeometryVerified):
        if "real CAD geometry verified" not in missing:
            missing.append("real CAD geometry verified")
    if visual_required and not visual_acceptance_ok:
        missing.append("visual_acceptance_review=pass")
    if neighbor_protection_required and not neighbor_protection_ok:
        missing.append("neighbor_protection=pass")

    if model_required and "schemaValid=true when model output is required" in missing:
        state = "closeout_blocked"
    elif any(item in missing for item in ["validate_plan=pass", "dry_run=pass", "created_handles_readback=ok", f"targetLayer={PREVIEW_LAYER}", "savedCurrentDwg=false", "real CAD geometry verified"]):
        state = "cad_evidence_missing"
    elif "visual_acceptance_review=pass" in missing or "neighbor_protection=pass" in missing:
        state = "visual_evidence_missing"
    else:
        state = "ready_for_user_review"

    return {
        "stateMachineVersion": STATE_MACHINE_VERSION,
        "state": state,
        "requiredEvidence": required,
        "missingEvidence": list(dict.fromkeys(missing)),
        "deliveryAllowed": state == "ready_for_user_review",
        "evidenceBoundary": [
            "closeout state machine only classifies recorded local evidence",
            "ready_for_user_review does not prove user acceptance or table C capability increase",
        ],
    }
