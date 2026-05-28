#!/usr/bin/env python
"""Execute a CAD_PLAN in a safe preview-first way."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Protocol

try:
    from core.plan_engine.validate_plan import load_json, validate_plan
    from core.safety.policy import assert_plan_is_safe
    from core.verification.preview_only_audit import attach_preview_only_audit
except ImportError:  # pragma: no cover - compatibility for direct execution.
    from scripts.validate_plan import load_json, validate_plan
    from core.safety.policy import assert_plan_is_safe
    from core.verification.preview_only_audit import attach_preview_only_audit


PREVIEW_LAYER = "CODEX_PREVIEW"


class CadPreviewDriver(Protocol):
    def draw_rectangle(self, **kwargs: object) -> object:
        ...

    def draw_line(self, **kwargs: object) -> object:
        ...

    def draw_polyline(self, **kwargs: object) -> object:
        ...

    def draw_circle(self, **kwargs: object) -> object:
        ...

    def draw_arc(self, **kwargs: object) -> object:
        ...

    def draw_text(self, **kwargs: object) -> object:
        ...

    def add_dimension(self, **kwargs: object) -> object:
        ...

    def insert_block_alpha(self, **kwargs: object) -> object:
        ...


def point3(values: list[Any]) -> list[float | int]:
    if len(values) == 2:
        return [values[0], values[1], 0]
    return [values[0], values[1], values[2]]


def _collect_handles(result: object) -> list[str]:
    if result is None:
        return []
    if isinstance(result, str):
        return [result]
    if isinstance(result, dict):
        if "handles" in result and isinstance(result["handles"], list):
            return [str(handle) for handle in result["handles"]]
        if "handle" in result:
            return [str(result["handle"])]
    if isinstance(result, list):
        return [str(item) for item in result]
    return []


def execute_plan_file(
    plan_path: Path,
    *,
    driver: CadPreviewDriver,
    preview_only: bool = True,
    allow_unconfirmed: bool = False,
    allow_destructive: bool = False,
) -> dict[str, object]:
    plan = load_json(plan_path)
    errors = validate_plan(plan)
    if errors:
        raise ValueError("Invalid CAD_PLAN: " + "; ".join(errors))

    intent = str(plan.get("intent", ""))
    assert_plan_is_safe(
        plan,
        approval={
            "allow_formal_layer": not preview_only,
            "allow_unconfirmed": allow_unconfirmed,
            "allow_delete": allow_destructive or intent == "delete_object",
            "approved_by": "execute_plan_file_options",
        },
    )

    if plan.get("needs_confirmation") and not allow_unconfirmed:
        raise ValueError("CAD_PLAN needs confirmation before execution.")

    if plan["intent"] == "insert_block_alpha":
        return _execute_insert_block_alpha(
            plan,
            plan_path=plan_path,
            driver=driver,
            preview_only=preview_only,
        )

    if plan["intent"] == "draw_symbol_glyph":
        return _execute_draw_symbol_glyph(
            plan,
            plan_path=plan_path,
            driver=driver,
            preview_only=preview_only,
        )

    if plan["intent"] == "draw_annotation":
        from core.execution.intent_extended_execute import execute_draw_annotation_plan

        return execute_draw_annotation_plan(
            plan,
            plan_path=plan_path,
            driver=driver,  # type: ignore[arg-type]
            preview_only=preview_only,
        )

    if plan["intent"] == "modify_object":
        from core.execution.intent_extended_execute import execute_modify_object_plan

        return execute_modify_object_plan(
            plan,
            plan_path=plan_path,
            driver=driver,  # type: ignore[arg-type]
            preview_only=preview_only,
        )

    if plan["intent"] == "delete_object":
        from core.execution.intent_extended_execute import execute_delete_object_plan

        return execute_delete_object_plan(
            plan,
            plan_path=plan_path,
            driver=driver,  # type: ignore[arg-type]
            preview_only=preview_only,
        )

    if plan["intent"] != "draw_object":
        raise ValueError(
            "execute_plan.py currently supports draw_object, draw_symbol_glyph, insert_block_alpha, "
            "draw_annotation, modify_object, and delete_object only."
        )
    obj = plan["object"]
    placement = plan["placement"]
    drawing = plan["drawing"]

    if placement.get("mode") != "absolute":
        raise ValueError("execute_plan.py currently supports absolute placement only.")

    layer = drawing["layer"]
    if preview_only and layer != PREVIEW_LAYER:
        raise ValueError(f"Preview execution only allows layer={PREVIEW_LAYER}.")

    width = obj.get("width")
    depth = obj.get("depth")
    if not isinstance(width, (int, float)) or not isinstance(depth, (int, float)):
        raise ValueError("object.width and object.depth are required for preview drawing.")

    base = point3(placement["base_point"])
    x0, y0, z0 = base
    corner2 = [x0 + width, y0 + depth, z0]
    color = "yellow"
    created_handles: list[str] = []

    created_handles.extend(
        _collect_handles(
            driver.draw_rectangle(
                corner1=base,
                corner2=corner2,
                layer=layer,
                color=color,
            )
        )
    )

    if drawing.get("include_label", False):
        label_height = max(80, min(min(width, depth) * 0.2, 160))
        created_handles.extend(
            _collect_handles(
                driver.draw_text(
                    text=obj["name"],
                    position=[x0 + width / 2, y0 + depth / 2, z0],
                    height=label_height,
                    layer=layer,
                    color=color,
                )
            )
        )

    if drawing.get("include_dimensions", False):
        dimension_offset = max(120, min(width, depth) * 0.3)
        created_handles.extend(
            _collect_handles(
                driver.add_dimension(
                    start_point=base,
                    end_point=[x0 + width, y0, z0],
                    text_position=[x0 + width / 2, y0 - dimension_offset, z0],
                    layer=layer,
                    color=color,
                )
            )
        )
        created_handles.extend(
            _collect_handles(
                driver.add_dimension(
                    start_point=base,
                    end_point=[x0, y0 + depth, z0],
                    text_position=[x0 - dimension_offset, y0 + depth / 2, z0],
                    layer=layer,
                    color=color,
                )
            )
        )

    return attach_preview_only_audit(
        {
            "status": "executed",
            "plan": str(plan_path),
            "intent": plan["intent"],
            "object_type": obj["type"],
            "object_name": obj["name"],
            "object_size": [width, depth],
            "base_point": base,
            "layer": layer,
            "preview_only": preview_only,
            "entities": {
                "rectangle": 1,
                "text": 1 if drawing.get("include_label", False) else 0,
                "dimensions": 2 if drawing.get("include_dimensions", False) else 0,
            },
            "created_handles": created_handles,
        },
        layer=layer,
    )


def _execute_draw_symbol_glyph(
    plan: dict[str, Any],
    *,
    plan_path: Path,
    driver: CadPreviewDriver,
    preview_only: bool,
) -> dict[str, object]:
    from core.execution.symbol_glyph_execute import execute_glyph_primitive, expected_readback_type_counts

    obj = plan["object"]
    placement = plan["placement"]
    drawing = plan["drawing"]
    layer = drawing["layer"]
    if preview_only and layer != PREVIEW_LAYER:
        raise ValueError(f"Preview execution only allows layer={PREVIEW_LAYER}.")

    if placement.get("mode") != "absolute":
        raise ValueError("draw_symbol_glyph only supports absolute placement.")

    glyphs = obj.get("glyph_primitives", [])
    if not isinstance(glyphs, list) or not glyphs:
        raise ValueError("draw_symbol_glyph requires non-empty object.glyph_primitives.")

    created_handles: list[str] = []
    entity_counts: dict[str, int] = {}
    for item in glyphs:
        if not isinstance(item, dict):
            raise ValueError("glyph_primitives entries must be objects.")
        primitive = str(item.get("primitive", ""))
        created_handles.extend(execute_glyph_primitive(driver, item, layer=layer))
        entity_counts[primitive] = entity_counts.get(primitive, 0) + 1

    base = point3(placement["base_point"])
    return attach_preview_only_audit(
        {
            "status": "executed",
            "plan": str(plan_path),
            "intent": plan["intent"],
            "object_type": obj.get("type", "symbol_glyph"),
            "object_name": obj.get("name", obj.get("symbol_id", "symbol_glyph")),
            "symbol_id": obj.get("symbol_id"),
            "archetype": obj.get("archetype"),
            "base_point": base,
            "layer": layer,
            "preview_only": preview_only,
            "geometry_accuracy": "not_verified_without_cad_readback",
            "glyph_primitive_count": len(glyphs),
            "glyph_primitive_types": entity_counts,
            "expected_readback_type_counts": expected_readback_type_counts(glyphs),
            "entities": entity_counts,
            "created_handles": created_handles,
        },
        layer=layer,
    )


def _execute_insert_block_alpha(
    plan: dict[str, Any],
    *,
    plan_path: Path,
    driver: CadPreviewDriver,
    preview_only: bool,
) -> dict[str, object]:
    from core.plan_engine.block_alpha_plan import _block_dict_from_plan

    obj = plan["object"]
    placement = plan["placement"]
    drawing = plan["drawing"]
    layer = drawing["layer"]
    if preview_only and layer != PREVIEW_LAYER:
        raise ValueError(f"Preview execution only allows layer={PREVIEW_LAYER}.")

    if placement.get("mode") != "absolute":
        raise ValueError("insert_block_alpha only supports absolute placement.")

    base = point3(placement["base_point"])
    rotation = placement.get("rotation", 0)
    scale = placement.get("scale", [1, 1, 1])
    cad_identity = obj.get("cad_identity", {})
    block_name = str(cad_identity.get("block_name", ""))
    block = _block_dict_from_plan(plan)

    insert_result = driver.insert_block_alpha(
        block_id=str(obj["block_id"]),
        block_name=block_name,
        base_point=base,
        rotation=rotation,
        scale=scale,
        layer=layer,
        attributes=obj.get("attributes"),
        cad_identity=cad_identity,
    )
    created_handles = _collect_handles(insert_result)

    return attach_preview_only_audit(
        {
            "status": "executed",
            "plan": str(plan_path),
            "intent": plan["intent"],
            "object_type": obj.get("type", "block_reference"),
            "object_name": obj.get("name", block_name),
            "block_id": obj.get("block_id"),
            "block_name": block_name,
            "base_point": base,
            "rotation": rotation,
            "scale": scale,
            "layer": layer,
            "preview_only": preview_only,
            "geometry_accuracy": "not_verified_without_cad_readback",
            "entities": {"insert_block_alpha": 1},
            "created_handles": created_handles,
        },
        layer=layer,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute a CAD_PLAN JSON file.")
    parser.add_argument("plan", type=Path, help="Path to CAD_PLAN JSON.")
    parser.add_argument(
        "--allow-formal-layer",
        action="store_true",
        help="Allow drawing to a non-preview layer. Use only with explicit user approval.",
    )
    parser.add_argument(
        "--allow-unconfirmed",
        action="store_true",
        help="Allow execution when CAD_PLAN.needs_confirmation is true. Use only with explicit approval.",
    )
    args = parser.parse_args()

    try:
        from core.cad_io.autocad_com import AutoCADComDriver
    except ImportError:  # pragma: no cover - compatibility with legacy layout.
        from drivers.autocad_com import AutoCADComDriver

    result = execute_plan_file(
        args.plan,
        driver=AutoCADComDriver(),
        preview_only=not args.allow_formal_layer,
        allow_unconfirmed=args.allow_unconfirmed,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
