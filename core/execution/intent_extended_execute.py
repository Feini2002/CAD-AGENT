"""Preview CAD execution for draw_annotation, modify_object, and delete_object intents."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from core.verification.preview_only_audit import attach_preview_only_audit

PREVIEW_LAYER = "CODEX_PREVIEW"


class IntentExtendedDriver(Protocol):
    def draw_rectangle(self, **kwargs: object) -> object:
        ...

    def draw_text(self, **kwargs: object) -> object:
        ...

    def set_entity_color_by_handle(self, *, handle: str, color: str) -> None:
        ...

    def delete_entity_by_handle(self, handle: str) -> None:
        ...

    @property
    def write_guard(self) -> Any:
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


def _bootstrap_rectangle(
    driver: IntentExtendedDriver,
    *,
    base: list[float | int],
    width: float | int,
    depth: float | int,
    layer: str,
) -> list[str]:
    x0, y0, z0 = base
    corner2 = [x0 + float(width), y0 + float(depth), z0]
    return _collect_handles(
        driver.draw_rectangle(
            corner1=base,
            corner2=corner2,
            layer=layer,
            color="yellow",
        )
    )


def execute_draw_annotation_plan(
    plan: dict[str, Any],
    *,
    plan_path: Path,
    driver: IntentExtendedDriver,
    preview_only: bool,
) -> dict[str, object]:
    obj = plan["object"]
    placement = plan["placement"]
    drawing = plan["drawing"]
    layer = str(drawing["layer"])
    if preview_only and layer != PREVIEW_LAYER:
        raise ValueError(f"Preview execution only allows layer={PREVIEW_LAYER}.")

    if placement.get("mode") != "absolute":
        raise ValueError("draw_annotation only supports absolute placement.")

    base = point3(placement["base_point"])
    text = str(obj.get("annotation_text") or obj.get("name", "annotation"))
    height = float(obj.get("text_height", 120))
    created_handles = _collect_handles(
        driver.draw_text(
            text=text,
            position=base,
            height=height,
            layer=layer,
            color="cyan",
        )
    )
    if not created_handles:
        raise ValueError("draw_annotation did not create any CAD handles.")

    return attach_preview_only_audit(
        {
            "status": "executed",
            "plan": str(plan_path),
            "intent": plan["intent"],
            "object_type": obj.get("type", "leader_note"),
            "object_name": obj.get("name", text),
            "base_point": base,
            "layer": layer,
            "preview_only": preview_only,
            "entities": {"text": 1},
            "created_handles": created_handles,
        },
        layer=layer,
    )


def execute_modify_object_plan(
    plan: dict[str, Any],
    *,
    plan_path: Path,
    driver: IntentExtendedDriver,
    preview_only: bool,
) -> dict[str, object]:
    obj = plan["object"]
    placement = plan["placement"]
    drawing = plan["drawing"]
    layer = str(drawing["layer"])
    if preview_only and layer != PREVIEW_LAYER:
        raise ValueError(f"Preview execution only allows layer={PREVIEW_LAYER}.")

    if placement.get("mode") != "absolute":
        raise ValueError("modify_object only supports absolute placement.")

    width = obj.get("width")
    depth = obj.get("depth")
    if not isinstance(width, (int, float)) or not isinstance(depth, (int, float)):
        raise ValueError("modify_object requires object.width and object.depth for bootstrap geometry.")

    patch = obj.get("patch", {})
    if not isinstance(patch, dict) or not patch.get("color"):
        raise ValueError("modify_object requires object.patch.color.")

    base = point3(placement["base_point"])
    created_handles = _bootstrap_rectangle(driver, base=base, width=width, depth=depth, layer=layer)
    if not created_handles:
        raise ValueError("modify_object bootstrap geometry did not create handles.")

    target_handle = str(created_handles[0])
    driver.set_entity_color_by_handle(handle=target_handle, color=str(patch["color"]))

    return attach_preview_only_audit(
        {
            "status": "executed",
            "plan": str(plan_path),
            "intent": plan["intent"],
            "object_type": obj.get("type", "property_patch"),
            "object_name": obj.get("name", "modify_object"),
            "base_point": base,
            "layer": layer,
            "preview_only": preview_only,
            "modified_handle": target_handle,
            "patch": patch,
            "entities": {"rectangle": 1},
            "created_handles": created_handles,
        },
        layer=layer,
    )


def execute_delete_object_plan(
    plan: dict[str, Any],
    *,
    plan_path: Path,
    driver: IntentExtendedDriver,
    preview_only: bool,
) -> dict[str, object]:
    obj = plan["object"]
    placement = plan["placement"]
    drawing = plan["drawing"]
    layer = str(drawing["layer"])
    if preview_only and layer != PREVIEW_LAYER:
        raise ValueError(f"Preview execution only allows layer={PREVIEW_LAYER}.")

    if placement.get("mode") != "absolute":
        raise ValueError("delete_object only supports absolute placement.")

    width = obj.get("width")
    depth = obj.get("depth")
    if not isinstance(width, (int, float)) or not isinstance(depth, (int, float)):
        raise ValueError("delete_object requires object.width and object.depth for bootstrap geometry.")

    base = point3(placement["base_point"])
    created_handles = _bootstrap_rectangle(driver, base=base, width=width, depth=depth, layer=layer)
    if not created_handles:
        raise ValueError("delete_object bootstrap geometry did not create handles.")

    guard = driver.write_guard
    previous_allow_delete = bool(getattr(guard, "allow_delete", False))
    guard.allow_delete = True
    deleted_handles: list[str] = []
    try:
        for handle in created_handles:
            driver.delete_entity_by_handle(handle)
            deleted_handles.append(handle)
    finally:
        guard.allow_delete = previous_allow_delete

    remaining = []
    if hasattr(driver, "snapshot_handles"):
        remaining = [
            row.get("handle")
            for row in driver.snapshot_handles(handles=deleted_handles, layer=layer)  # type: ignore[attr-defined]
        ]

    return attach_preview_only_audit(
        {
            "status": "executed",
            "plan": str(plan_path),
            "intent": plan["intent"],
            "object_type": obj.get("type", "entity_reference"),
            "object_name": obj.get("name", "delete_object"),
            "base_point": base,
            "layer": layer,
            "preview_only": preview_only,
            "deleted_handles": deleted_handles,
            "deleted_handle_count": len(deleted_handles),
            "remaining_readback_count": len(remaining),
            "entities": {"rectangle": 1},
            "created_handles": deleted_handles,
        },
        layer=layer,
    )
