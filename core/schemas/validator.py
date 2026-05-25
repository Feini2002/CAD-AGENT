"""Small JSON Schema subset validator used by CAD Agent Core examples.

The project intentionally avoids adding a dependency just to validate the
lightweight model examples. This validator covers the subset used by the
schemas in ``core/schemas`` and reports readable dotted paths.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TYPE_MAP = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _path_join(path: str, child: str) -> str:
    return f"$.{child}" if path == "$" else f"{path}.{child}"


def validate_value(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")

    if expected_type == "number":
        if not _is_number(value):
            return [f"{path} must be number."]
    elif expected_type == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            return [f"{path} must be integer."]
    elif isinstance(expected_type, str) and expected_type in TYPE_MAP:
        if not isinstance(value, TYPE_MAP[expected_type]):
            return [f"{path} must be {expected_type}."]

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path} must be one of {schema['enum']}.")

    if _is_number(value):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path} must be >= {schema['minimum']}.")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path} must be <= {schema['maximum']}.")
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            errors.append(f"{path} must be > {schema['exclusiveMinimum']}.")

    if isinstance(value, list):
        min_items = schema.get("minItems")
        max_items = schema.get("maxItems")
        if isinstance(min_items, int) and len(value) < min_items:
            errors.append(f"{path} must contain at least {min_items} items.")
        if isinstance(max_items, int) and len(value) > max_items:
            errors.append(f"{path} must contain at most {max_items} items.")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(validate_value(item, item_schema, f"{path}[{index}]"))

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{_path_join(path, key)} is required.")

        properties = schema.get("properties", {})
        for key, child_value in value.items():
            child_path = _path_join(path, key)
            child_schema = properties.get(key)
            if isinstance(child_schema, dict):
                errors.extend(validate_value(child_value, child_schema, child_path))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{child_path} is not allowed.")

    return errors


def validate_json(schema_path: Path, data_path: Path) -> list[str]:
    schema = load_json(schema_path)
    data = load_json(data_path)
    if not isinstance(schema, dict):
        return ["Schema file must contain a JSON object."]
    return validate_value(data, schema)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a JSON file against a small schema subset.")
    parser.add_argument("schema", type=Path)
    parser.add_argument("data", type=Path)
    args = parser.parse_args()

    errors = validate_json(args.schema, args.data)
    if errors:
        print("INVALID JSON MODEL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALID JSON MODEL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
