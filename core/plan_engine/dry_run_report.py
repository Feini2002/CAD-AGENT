"""Machine-readable dry-run reports for CAD_PLAN files and dictionaries."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.plan_engine.validate_plan import load_json, validate_plan
from core.verification.geometry_checks import expected_bbox_from_plan


def _point3(point: list[Any]) -> list[Any]:
    return point if len(point) == 3 else [point[0], point[1], 0]


def create_dry_run_report(plan: dict[str, Any] | Path) -> dict[str, Any]:
    if isinstance(plan, Path):
        plan = load_json(plan)
    errors = validate_plan(plan)
    if errors:
        return {
            "version": "0.1",
            "status": "invalid",
            "validation_errors": errors,
            "entities": [],
            "human_summary": "INVALID CAD_PLAN",
        }

    if plan["intent"] == "insert_block_alpha":
        from core.plan_engine.block_alpha_plan import create_insert_block_alpha_dry_run_report

        return create_insert_block_alpha_dry_run_report(plan)

    if plan["intent"] == "draw_symbol_glyph":
        from core.plan_engine.symbol_glyph_plan import create_draw_symbol_glyph_dry_run_report

        return create_draw_symbol_glyph_dry_run_report(plan)

    obj = plan["object"]
    drawing = plan["drawing"]
    base = _point3(plan["placement"]["base_point"])
    bbox = expected_bbox_from_plan(plan)
    entities: list[dict[str, Any]] = [
        {
            "type": "rectangle",
            "layer": drawing["layer"],
            "bbox": bbox,
        }
    ]
    if drawing.get("include_label"):
        entities.append(
            {
                "type": "text",
                "layer": drawing["layer"],
                "text": obj["name"],
                "position": [base[0] + obj["width"] / 2, base[1] + obj["depth"] / 2, base[2]],
            }
        )
    if drawing.get("include_dimensions"):
        entities.extend(
            [
                {"type": "dimension", "layer": drawing["layer"], "axis": "x"},
                {"type": "dimension", "layer": drawing["layer"], "axis": "y"},
            ]
        )

    human_summary = "\n".join(
        [
            "CAD_PLAN DRY RUN",
            f"- intent: {plan['intent']}",
            f"- object: {obj.get('name')} ({obj.get('type')})",
            f"- size: {obj.get('width')} x {obj.get('depth')} mm",
            f"- placement: {plan['placement'].get('mode')} at {base}",
            f"- layer: {drawing.get('layer')}",
        ]
    )
    return {
        "version": "0.1",
        "status": "valid",
        "validation_errors": [],
        "intent": plan["intent"],
        "layer": drawing["layer"],
        "bbox": bbox,
        "entities": entities,
        "human_summary": human_summary,
    }
