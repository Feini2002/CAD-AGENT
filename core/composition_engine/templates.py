"""Template-backed object compositions for persona delivery benchmarks."""

from __future__ import annotations

from typing import Any

from core.composition_engine.composition_template_catalog import COMPOSITION_TEMPLATES
from core.composition_engine.drawing_policy import resolve_composition_object_drawing_flags
from core.composition_engine.preview import write_composition_preview_svg
from core.object_engine.parametric_objects import create_object_spec, object_spec_to_cad_plan
from core.verification.evidence_contract import NON_CAD_GEOMETRY_ACCURACY, SCREENSHOT_VISUAL_AID_ONLY

__all__ = [
    "COMPOSITION_TEMPLATES",
    "composition_micro_scene_metrics",
    "composition_to_cad_plans",
    "create_composition_spec",
    "write_composition_preview_svg",
]


def _point3(point: list[Any]) -> list[float | int]:
    if len(point) == 2:
        return [point[0], point[1], 0]
    return [point[0], point[1], point[2]]


def _bbox_from_objects(objects: list[dict[str, Any]]) -> dict[str, list[float | int]]:
    mins: list[list[float | int]] = []
    maxes: list[list[float | int]] = []
    for item in objects:
        base = _point3(item["base_point"])
        size = item["size"]
        mins.append([base[0], base[1]])
        maxes.append([base[0] + size["width"], base[1] + size["depth"]])
    return {
        "min": [min(point[0] for point in mins), min(point[1] for point in mins)],
        "max": [max(point[0] for point in maxes), max(point[1] for point in maxes)],
    }


def _copy_template_list(items: list[Any] | None) -> list[dict[str, Any]]:
    if not items:
        return []
    return [dict(item) if isinstance(item, dict) else item for item in items]


def create_composition_spec(
    composition_id: str,
    *,
    persona_role: str = "simulated_user",
    request_text: str = "",
) -> dict[str, Any]:
    if composition_id not in COMPOSITION_TEMPLATES:
        raise ValueError(f"Unsupported composition_id: {composition_id}")
    template = COMPOSITION_TEMPLATES[composition_id]
    objects = [dict(item, size=dict(item["size"]), base_point=list(item["base_point"])) for item in template["objects"]]
    spec: dict[str, Any] = {
        "version": "0.1",
        "composition_id": composition_id,
        "name": template["name"],
        "domain": template["domain"],
        "persona_role": persona_role,
        "request_text": request_text,
        "objects": objects,
        "bbox": _bbox_from_objects(objects),
        "evidence": {
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY,
        },
    }
    bindings = _copy_template_list(template.get("bindings"))
    if bindings:
        spec["bindings"] = bindings
    clearance_refs = _copy_template_list(template.get("clearance_refs"))
    if clearance_refs:
        spec["clearance_refs"] = clearance_refs
    circulation = _copy_template_list(template.get("circulation"))
    if circulation:
        spec["circulation"] = circulation
    layout_notes = template.get("layout_notes")
    if isinstance(layout_notes, list) and layout_notes:
        spec["layout_notes"] = list(layout_notes)
    layout_constraints = template.get("layout_constraints")
    if isinstance(layout_constraints, dict) and layout_constraints:
        spec["layout_constraints"] = dict(layout_constraints)
    return spec


def composition_micro_scene_metrics(composition: dict[str, Any]) -> dict[str, Any]:
    """Extract benchmark-friendly binding / clearance / circulation metrics from a composition spec."""
    clearance_refs = composition.get("clearance_refs", [])
    circulation = composition.get("circulation", [])
    bindings = composition.get("bindings", [])
    return {
        "clearance_refs": clearance_refs,
        "clearance_ref_roles": sorted(
            {
                str(ref.get("role"))
                for ref in clearance_refs
                if isinstance(ref, dict) and ref.get("role")
            }
        ),
        "binding_relations": sorted(
            {
                str(binding.get("relation"))
                for binding in bindings
                if isinstance(binding, dict) and binding.get("relation")
            }
        ),
        "circulation_roles": sorted(
            {
                str(zone.get("role"))
                for zone in circulation
                if isinstance(zone, dict) and zone.get("role")
            }
        ),
    }


def composition_to_cad_plans(
    composition: dict[str, Any],
    *,
    layer: str = "CODEX_PREVIEW",
) -> list[dict[str, Any]]:
    plans: list[dict[str, Any]] = []
    for item in composition["objects"]:
        size = item["size"]
        include_label, include_dimensions = resolve_composition_object_drawing_flags(item)
        spec = create_object_spec(
            item["type"],
            name=item["name"],
            width=size["width"],
            depth=size["depth"],
            height=size.get("height"),
        )
        plan = object_spec_to_cad_plan(
            spec,
            base_point=_point3(item["base_point"]),
            domain=composition.get("domain", "generic"),
            layer=layer,
            include_dimensions=include_dimensions,
            include_label=include_label,
        )
        plan["object"]["instance_id"] = item["instance_id"]
        plan["object"]["role"] = item["role"]
        plan["object"]["composition_id"] = composition["composition_id"]
        plans.append(plan)
    return plans
