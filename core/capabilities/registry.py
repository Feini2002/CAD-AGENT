"""Public facade for the Core capability catalog and guarded runtime."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.capabilities.specs import CAPABILITIES
from core.capabilities.validation import validate_capability_registry, validate_payload


def _public_spec(spec: dict[str, Any]) -> dict[str, Any]:
    data = {key: value for key, value in spec.items() if key != "runner"}
    data.pop("input_model_schemas", None)
    return deepcopy(data)


def list_capabilities() -> list[dict[str, Any]]:
    """Return the public machine-readable Core capability catalog."""

    return [_public_spec(CAPABILITIES[key]) for key in sorted(CAPABILITIES)]


def get_capability(capability_id: str) -> dict[str, Any]:
    """Return one public capability spec by id."""

    if capability_id not in CAPABILITIES:
        raise KeyError(f"Unknown Core capability: {capability_id}")
    return _public_spec(CAPABILITIES[capability_id])


def run_capability(capability_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Validate inputs, run a Core capability, and wrap the result."""

    if capability_id not in CAPABILITIES:
        return {"status": "unknown_capability", "capability_id": capability_id, "errors": [f"Unknown Core capability: {capability_id}"]}
    spec = CAPABILITIES[capability_id]
    errors = validate_payload(spec, payload)
    if errors:
        return {
            "status": "invalid_input",
            "capability_id": capability_id,
            "errors": errors,
            "output_model_type": spec["output_contract"]["model_type"],
            "output": {},
        }

    try:
        output = spec["runner"](payload)
    except Exception as exc:  # pragma: no cover - kept as a runtime safety wrapper
        return {
            "status": "failed",
            "capability_id": capability_id,
            "errors": [str(exc)],
            "output_model_type": spec["output_contract"]["model_type"],
            "output": {},
        }

    return {
        "status": "ok",
        "capability_id": capability_id,
        "errors": [],
        "output_model_type": spec["output_contract"]["model_type"],
        "output": output,
        "evidence": {
            "requires_cad": spec["requires_cad"],
            "risk_level": spec["risk_level"],
            "verification_commands": list(spec["verification_commands"]),
        },
    }
