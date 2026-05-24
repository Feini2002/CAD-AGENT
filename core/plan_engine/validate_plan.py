#!/usr/bin/env python
"""Validate a first-version CAD_PLAN without external dependencies."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = [
    "version",
    "domain",
    "intent",
    "object",
    "placement",
    "drawing",
    "confidence",
    "needs_confirmation",
]

ALLOWED_DOMAINS = {
    "generic",
    "residential",
    "retail",
    "office",
    "restaurant",
    "exhibition",
    "hotel",
    "education",
    "healthcare",
    "industrial",
    "custom",
}
ALLOWED_INTENTS = {"draw_object", "draw_annotation", "modify_object", "delete_object"}
ALLOWED_PLACEMENT_MODES = {"absolute", "space_reference", "relative_to_object"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        value = json.load(file)
    if not isinstance(value, dict):
        raise ValueError("CAD_PLAN must be a JSON object.")
    return value


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_plan(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for key in REQUIRED_TOP_LEVEL:
        require(key in plan, f"Missing top-level field: {key}", errors)
    if errors:
        return errors

    require(plan["version"] == "0.1", "version must be '0.1'.", errors)
    require(plan["domain"] in ALLOWED_DOMAINS, "domain is not supported.", errors)
    require(plan["intent"] in ALLOWED_INTENTS, "intent is not supported.", errors)
    require(isinstance(plan["object"], dict), "object must be an object.", errors)
    require(isinstance(plan["placement"], dict), "placement must be an object.", errors)
    require(isinstance(plan["drawing"], dict), "drawing must be an object.", errors)
    require(isinstance(plan["needs_confirmation"], bool), "needs_confirmation must be boolean.", errors)
    require(isinstance(plan["confidence"], (int, float)), "confidence must be a number.", errors)
    if isinstance(plan["confidence"], (int, float)):
        require(0 <= plan["confidence"] <= 1, "confidence must be between 0 and 1.", errors)

    obj = plan["object"]
    placement = plan["placement"]
    drawing = plan["drawing"]

    require(bool(obj.get("type")), "object.type is required.", errors)
    require(bool(obj.get("name")), "object.name is required.", errors)

    for size_key in ["width", "depth"]:
        if size_key in obj:
            require(isinstance(obj[size_key], (int, float)), f"object.{size_key} must be a number.", errors)
            if isinstance(obj[size_key], (int, float)):
                require(obj[size_key] > 0, f"object.{size_key} must be greater than 0.", errors)

    require(placement.get("mode") in ALLOWED_PLACEMENT_MODES, "placement.mode is not supported.", errors)
    if placement.get("mode") == "absolute":
        base_point = placement.get("base_point")
        require(isinstance(base_point, list), "placement.base_point is required for absolute placement.", errors)
        if isinstance(base_point, list):
            require(len(base_point) in (2, 3), "placement.base_point must contain 2 or 3 numbers.", errors)
            require(all(isinstance(v, (int, float)) for v in base_point), "placement.base_point values must be numbers.", errors)

    require(bool(drawing.get("layer")), "drawing.layer is required.", errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a CAD_PLAN JSON file.")
    parser.add_argument("plan", type=Path, help="Path to CAD_PLAN JSON.")
    args = parser.parse_args()

    try:
        plan = load_json(args.plan)
        errors = validate_plan(plan)
    except Exception as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1

    if errors:
        print("INVALID CAD_PLAN")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALID CAD_PLAN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
