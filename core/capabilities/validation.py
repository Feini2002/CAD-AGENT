"""Validation helpers for the Core capability catalog."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.capabilities.specs import ALLOWED_MATURITY, CAPABILITIES
from core.schemas.validator import load_json, validate_value


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_schema(relative_path: str) -> dict[str, Any]:
    schema = load_json(PROJECT_ROOT / relative_path)
    if not isinstance(schema, dict):
        raise ValueError(f"Schema must be a JSON object: {relative_path}")
    return schema


def validate_capability_registry() -> list[str]:
    """Validate registry metadata without running capability implementations."""

    errors: list[str] = []
    seen_ids: set[str] = set()
    for capability_id, spec in sorted(CAPABILITIES.items()):
        if capability_id in seen_ids:
            errors.append(f"Duplicate capability id: {capability_id}")
        seen_ids.add(capability_id)
        if capability_id != spec.get("capability_id"):
            errors.append(f"{capability_id}: capability_id does not match registry key.")
        if not callable(spec.get("runner")):
            errors.append(f"{capability_id}: runner must be callable.")
        if spec.get("risk_level") not in {"read_only", "preview_only", "requires_approval"}:
            errors.append(f"{capability_id}: invalid risk_level.")
        if spec.get("maturity") not in ALLOWED_MATURITY:
            errors.append(f"{capability_id}: invalid maturity.")
        known_limits = spec.get("known_limits")
        if not isinstance(known_limits, list) or not known_limits or not all(isinstance(item, str) and item for item in known_limits):
            errors.append(f"{capability_id}: known_limits must be a non-empty list of strings.")
        if not isinstance(spec.get("requires_cad"), bool):
            errors.append(f"{capability_id}: requires_cad must be boolean.")
        input_schema = spec.get("input_schema")
        if not isinstance(input_schema, dict) or input_schema.get("type") != "object":
            errors.append(f"{capability_id}: input_schema must be an object schema.")
        output_contract = spec.get("output_contract")
        if not isinstance(output_contract, dict) or not output_contract.get("model_type"):
            errors.append(f"{capability_id}: output_contract.model_type is required.")
        schema_path = output_contract.get("schema") if isinstance(output_contract, dict) else ""
        if schema_path and not (PROJECT_ROOT / str(schema_path)).exists():
            errors.append(f"{capability_id}: output schema does not exist: {schema_path}")
        commands = spec.get("verification_commands")
        if not isinstance(commands, list) or not commands:
            errors.append(f"{capability_id}: verification_commands must be a non-empty list.")
    return errors


def validate_payload(spec: dict[str, Any], payload: dict[str, Any]) -> list[str]:
    errors = validate_value(payload, spec["input_schema"])
    for field, schema_path in spec.get("input_model_schemas", {}).items():
        if field in payload and isinstance(payload[field], dict):
            field_errors = validate_value(payload[field], load_schema(schema_path))
            errors.extend(
                f"{field}{error[1:]}" if error.startswith("$") else f"{field}: {error}"
                for error in field_errors
            )
    return errors
