#!/usr/bin/env python
"""Preview what a first-version CAD_PLAN would draw."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run a CAD_PLAN JSON file.")
    parser.add_argument("plan", type=Path, help="Path to CAD_PLAN JSON.")
    args = parser.parse_args()

    with args.plan.open("r", encoding="utf-8") as file:
        plan = json.load(file)

    obj = plan["object"]
    placement = plan["placement"]
    drawing = plan["drawing"]
    base_point = placement.get("base_point", [0, 0, 0])
    width = obj.get("width", 0)
    depth = obj.get("depth", 0)

    print("CAD_PLAN DRY RUN")
    print(f"- intent: {plan['intent']}")
    print(f"- object: {obj.get('name')} ({obj.get('type')})")
    print(f"- size: {width} x {depth} mm")
    print(f"- placement: {placement.get('mode')} at {base_point}")
    print(f"- layer: {drawing.get('layer')}")
    print(f"- include_label: {drawing.get('include_label', False)}")
    print(f"- include_dimensions: {drawing.get('include_dimensions', False)}")
    print("- entities to create: rectangle, optional text, optional linear dimensions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

