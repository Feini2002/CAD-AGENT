"""Expand object specs into component-level safe preview CAD plans."""

from __future__ import annotations

from typing import Any


PREVIEW_LAYER = "CODEX_PREVIEW"


def _point3(point: list[float | int] | None) -> list[float | int]:
    if point is None:
        return [0, 0, 0]
    if len(point) == 2:
        return [point[0], point[1], 0]
    return [point[0], point[1], point[2]]


def _component_plan(
    spec: dict[str, Any],
    *,
    component_id: str,
    role: str,
    base_point: list[float | int],
    width: float | int,
    depth: float | int,
    layer: str,
    domain: str,
) -> dict[str, Any]:
    height = spec.get("size", {}).get("height", 0)
    return {
        "version": "0.1",
        "domain": domain,
        "intent": "draw_object",
        "object": {
            "type": spec["type"],
            "name": f"{spec['name']} {role}",
            "width": width,
            "depth": depth,
            "height": height,
            "object_spec_id": spec["object_id"],
            "component_id": component_id,
            "component_role": role,
        },
        "placement": {
            "mode": "absolute",
            "base_point": base_point,
        },
        "drawing": {
            "layer": layer,
            "include_label": False,
            "include_dimensions": False,
        },
        "confidence": 0.88,
        "needs_confirmation": False,
    }


def _rect(base: list[float | int], dx: float | int, dy: float | int) -> list[float | int]:
    return [base[0] + dx, base[1] + dy, base[2]]


def object_spec_to_detail_cad_plans(
    spec: dict[str, Any],
    *,
    base_point: list[float | int] | None = None,
    domain: str = "generic",
    layer: str = PREVIEW_LAYER,
) -> list[dict[str, Any]]:
    """Create component-level CAD_PLAN rectangles for a reusable object spec."""

    base = _point3(base_point)
    size = spec["size"]
    width = size["width"]
    depth = size["depth"]
    object_type = spec["type"]
    builders = {
        "table": _table_plans,
        "bed": _bed_plans,
        "chair": _chair_plans,
        "sofa": _sofa_plans,
        "desk": _desk_plans,
    }
    builder = builders.get(object_type, _fallback_plans)
    return builder(spec, base=base, width=width, depth=depth, domain=domain, layer=layer)


def _table_plans(
    spec: dict[str, Any],
    *,
    base: list[float | int],
    width: float | int,
    depth: float | int,
    domain: str,
    layer: str,
) -> list[dict[str, Any]]:
    leg = min(max(min(width, depth) * 0.08, 60), 120)
    inset = max(50, leg)
    plans = [
        _component_plan(
            spec,
            component_id="table-top",
            role="top",
            base_point=base,
            width=width,
            depth=depth,
            layer=layer,
            domain=domain,
        )
    ]
    for index, point in enumerate(
        [
            _rect(base, inset, inset),
            _rect(base, width - inset - leg, inset),
            _rect(base, inset, depth - inset - leg),
            _rect(base, width - inset - leg, depth - inset - leg),
        ],
        start=1,
    ):
        plans.append(
            _component_plan(
                spec,
                component_id=f"table-leg-{index}",
                role="support",
                base_point=point,
                width=leg,
                depth=leg,
                layer=layer,
                domain=domain,
            )
        )
    return plans


def _bed_plans(
    spec: dict[str, Any],
    *,
    base: list[float | int],
    width: float | int,
    depth: float | int,
    domain: str,
    layer: str,
) -> list[dict[str, Any]]:
    inset = min(max(min(width, depth) * 0.04, 50), 100)
    headboard_depth = min(max(depth * 0.08, 80), 160)
    return [
        _component_plan(
            spec,
            component_id="bed-base",
            role="base",
            base_point=base,
            width=width,
            depth=depth,
            layer=layer,
            domain=domain,
        ),
        _component_plan(
            spec,
            component_id="bed-sleep-surface",
            role="sleep_surface",
            base_point=_rect(base, inset, headboard_depth),
            width=width - inset * 2,
            depth=depth - headboard_depth - inset,
            layer=layer,
            domain=domain,
        ),
        _component_plan(
            spec,
            component_id="bed-headboard",
            role="base",
            base_point=base,
            width=width,
            depth=headboard_depth,
            layer=layer,
            domain=domain,
        ),
    ]


def _chair_plans(
    spec: dict[str, Any],
    *,
    base: list[float | int],
    width: float | int,
    depth: float | int,
    domain: str,
    layer: str,
) -> list[dict[str, Any]]:
    back_depth = min(max(depth * 0.16, 60), 110)
    support = min(max(min(width, depth) * 0.09, 40), 80)
    plans = [
        _component_plan(
            spec,
            component_id="chair-seat",
            role="seat",
            base_point=base,
            width=width,
            depth=depth - back_depth,
            layer=layer,
            domain=domain,
        ),
        _component_plan(
            spec,
            component_id="chair-back",
            role="back",
            base_point=_rect(base, 0, depth - back_depth),
            width=width,
            depth=back_depth,
            layer=layer,
            domain=domain,
        ),
    ]
    for index, point in enumerate(
        [
            _rect(base, support, support),
            _rect(base, width - support * 2, support),
            _rect(base, support, depth - back_depth - support * 2),
            _rect(base, width - support * 2, depth - back_depth - support * 2),
        ],
        start=1,
    ):
        plans.append(
            _component_plan(
                spec,
                component_id=f"chair-support-{index}",
                role="support",
                base_point=point,
                width=support,
                depth=support,
                layer=layer,
                domain=domain,
            )
        )
    return plans


def _sofa_plans(
    spec: dict[str, Any],
    *,
    base: list[float | int],
    width: float | int,
    depth: float | int,
    domain: str,
    layer: str,
) -> list[dict[str, Any]]:
    arm_width = min(max(width * 0.08, 120), 220)
    back_depth = min(max(depth * 0.16, 100), 180)
    return [
        _component_plan(
            spec,
            component_id="sofa-seat",
            role="seat",
            base_point=_rect(base, arm_width, 0),
            width=width - arm_width * 2,
            depth=depth - back_depth,
            layer=layer,
            domain=domain,
        ),
        _component_plan(
            spec,
            component_id="sofa-back",
            role="back",
            base_point=_rect(base, 0, depth - back_depth),
            width=width,
            depth=back_depth,
            layer=layer,
            domain=domain,
        ),
        _component_plan(
            spec,
            component_id="sofa-left-arm",
            role="arm",
            base_point=base,
            width=arm_width,
            depth=depth,
            layer=layer,
            domain=domain,
        ),
        _component_plan(
            spec,
            component_id="sofa-right-arm",
            role="arm",
            base_point=_rect(base, width - arm_width, 0),
            width=arm_width,
            depth=depth,
            layer=layer,
            domain=domain,
        ),
    ]


def _desk_plans(
    spec: dict[str, Any],
    *,
    base: list[float | int],
    width: float | int,
    depth: float | int,
    domain: str,
    layer: str,
) -> list[dict[str, Any]]:
    support_width = min(max(width * 0.08, 80), 140)
    return [
        _component_plan(
            spec,
            component_id="desk-worktop",
            role="worktop",
            base_point=base,
            width=width,
            depth=depth,
            layer=layer,
            domain=domain,
        ),
        _component_plan(
            spec,
            component_id="desk-left-support",
            role="support",
            base_point=base,
            width=support_width,
            depth=depth,
            layer=layer,
            domain=domain,
        ),
        _component_plan(
            spec,
            component_id="desk-right-support",
            role="support",
            base_point=_rect(base, width - support_width, 0),
            width=support_width,
            depth=depth,
            layer=layer,
            domain=domain,
        ),
    ]


def _fallback_plans(
    spec: dict[str, Any],
    *,
    base: list[float | int],
    width: float | int,
    depth: float | int,
    domain: str,
    layer: str,
) -> list[dict[str, Any]]:
    body_role = next(
        (
            str(component.get("role"))
            for component in spec.get("components", [])
            if isinstance(component, dict) and component.get("role") in {"body", "base", "worktop"}
        ),
        "body",
    )
    return [
        _component_plan(
            spec,
            component_id=f"{spec['type']}-{body_role}",
            role=body_role,
            base_point=base,
            width=width,
            depth=depth,
            layer=layer,
            domain=domain,
        )
    ]
