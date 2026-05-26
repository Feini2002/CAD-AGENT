"""Template-backed object compositions for persona delivery benchmarks."""

from __future__ import annotations

from typing import Any

from core.composition_engine.preview import write_composition_preview_svg
from core.object_engine.parametric_objects import create_object_spec, object_spec_to_cad_plan
from core.verification.evidence_contract import NON_CAD_GEOMETRY_ACCURACY, SCREENSHOT_VISUAL_AID_ONLY


COMPOSITION_TEMPLATES: dict[str, dict[str, Any]] = {
    "bedroom_bed_rug": {
        "name": "Bedroom Bed + Rug Set",
        "domain": "residential",
        "objects": [
            {
                "instance_id": "rug-01",
                "type": "rug",
                "name": "Area Rug",
                "role": "soft_zone",
                "base_point": [0, 0, 0],
                "size": {"width": 2400, "depth": 1900, "height": 20},
                "include_dimensions": False,
                "include_label": False,
            },
            {
                "instance_id": "bed-01",
                "type": "bed",
                "name": "Bed",
                "role": "primary_bed",
                "base_point": [200, 200, 0],
                "size": {"width": 2000, "depth": 1500, "height": 600},
                "include_dimensions": True,
            },
        ],
    },
    "dining_table_set": {
        "name": "Dining Table Set",
        "domain": "residential",
        "objects": [
            {
                "instance_id": "table-01",
                "type": "table",
                "name": "Dining Table",
                "role": "dining_surface",
                "base_point": [600, 600, 0],
                "size": {"width": 1600, "depth": 900, "height": 750},
                "include_dimensions": True,
            },
            {
                "instance_id": "chair-01",
                "type": "chair",
                "name": "Chair",
                "role": "dining_seat",
                "base_point": [900, 50, 0],
                "size": {"width": 500, "depth": 500, "height": 850},
                "include_dimensions": False,
            },
            {
                "instance_id": "chair-02",
                "type": "chair",
                "name": "Chair",
                "role": "dining_seat",
                "base_point": [1400, 50, 0],
                "size": {"width": 500, "depth": 500, "height": 850},
                "include_dimensions": False,
            },
            {
                "instance_id": "chair-03",
                "type": "chair",
                "name": "Chair",
                "role": "dining_seat",
                "base_point": [900, 1600, 0],
                "size": {"width": 500, "depth": 500, "height": 850},
                "include_dimensions": False,
            },
            {
                "instance_id": "chair-04",
                "type": "chair",
                "name": "Chair",
                "role": "dining_seat",
                "base_point": [1400, 1600, 0],
                "size": {"width": 500, "depth": 500, "height": 850},
                "include_dimensions": False,
            },
        ],
    },
    "single_desk_chair_pair": {
        "name": "Single Desk Chair Pair",
        "domain": "office",
        "objects": [
            {
                "instance_id": "desk-01",
                "type": "desk",
                "name": "Office Desk",
                "role": "work_surface",
                "base_point": [0, 800, 0],
                "size": {"width": 1400, "depth": 700, "height": 750},
                "include_dimensions": True,
            },
            {
                "instance_id": "chair-01",
                "type": "chair",
                "name": "Task Chair",
                "role": "seating_for_desk",
                "base_point": [450, 0, 0],
                "size": {"width": 500, "depth": 500, "height": 850},
                "include_dimensions": False,
            },
        ],
        "bindings": [
            {"from_instance_id": "chair-01", "to_instance_id": "desk-01", "relation": "seating_for_desk"}
        ],
        "clearance_refs": [
            {
                "role": "chair_pullback_clearance",
                "bound_to": "chair-01",
                "behind_depth_mm": 800,
                "side_margin_mm": 150,
            }
        ],
    },
    "desk_with_back_cabinet": {
        "name": "Desk With Back Cabinet",
        "domain": "office",
        "objects": [
            {
                "instance_id": "desk-01",
                "type": "desk",
                "name": "Office Desk",
                "role": "work_surface",
                "base_point": [0, 600, 0],
                "size": {"width": 1400, "depth": 700, "height": 750},
                "include_dimensions": True,
            },
            {
                "instance_id": "chair-01",
                "type": "chair",
                "name": "Task Chair",
                "role": "seating_for_desk",
                "base_point": [450, 0, 0],
                "size": {"width": 500, "depth": 500, "height": 850},
                "include_dimensions": False,
            },
            {
                "instance_id": "cabinet-01",
                "type": "cabinet",
                "name": "Back Cabinet",
                "role": "general_storage",
                "base_point": [200, 1600, 0],
                "size": {"width": 1800, "depth": 600, "height": 2400},
                "include_dimensions": False,
            },
        ],
        "bindings": [
            {"from_instance_id": "chair-01", "to_instance_id": "desk-01", "relation": "seating_for_desk"},
            {"from_instance_id": "cabinet-01", "to_instance_id": "desk-01", "relation": "storage_behind_desk"},
        ],
        "clearance_refs": [
            {
                "role": "chair_pullback_clearance",
                "bound_to": "chair-01",
                "behind_depth_mm": 800,
                "side_margin_mm": 150,
            },
            {
                "role": "cabinet_front_clearance",
                "bound_to": "cabinet-01",
                "front_depth_mm": 800,
            },
        ],
        "layout_notes": ["chair_pullback_and_cabinet_front_clearance_explicit"],
    },
    "two_workstations_shared_aisle": {
        "name": "Two Workstations Shared Aisle",
        "domain": "office",
        "objects": [
            {
                "instance_id": "desk-01",
                "type": "desk",
                "name": "Workstation Desk A",
                "role": "work_surface",
                "base_point": [0, 0, 0],
                "size": {"width": 1400, "depth": 700, "height": 750},
                "include_dimensions": True,
            },
            {
                "instance_id": "chair-01",
                "type": "chair",
                "name": "Task Chair A",
                "role": "seating_for_desk",
                "base_point": [450, -700, 0],
                "size": {"width": 500, "depth": 500, "height": 850},
                "include_dimensions": False,
            },
            {
                "instance_id": "desk-02",
                "type": "desk",
                "name": "Workstation Desk B",
                "role": "work_surface",
                "base_point": [2200, 0, 0],
                "size": {"width": 1400, "depth": 700, "height": 750},
                "include_dimensions": False,
            },
            {
                "instance_id": "chair-02",
                "type": "chair",
                "name": "Task Chair B",
                "role": "seating_for_desk",
                "base_point": [2650, -700, 0],
                "size": {"width": 500, "depth": 500, "height": 850},
                "include_dimensions": False,
            },
        ],
        "bindings": [
            {"from_instance_id": "chair-01", "to_instance_id": "desk-01", "relation": "seating_for_desk"},
            {"from_instance_id": "chair-02", "to_instance_id": "desk-02", "relation": "seating_for_desk"},
        ],
        "circulation": [
            {
                "zone_id": "main-aisle-01",
                "role": "main_aisle",
                "min_width_mm": 1100,
                "target_width_mm": 1100,
                "continuity_required": True,
                "connects": ["desk-01", "desk-02"],
            }
        ],
    },
    "entry_reception_clearance": {
        "name": "Entry Reception Clearance",
        "domain": "office",
        "objects": [
            {
                "instance_id": "desk-reception",
                "type": "desk",
                "name": "Reception Desk",
                "role": "reception_surface",
                "base_point": [1400, 0, 0],
                "size": {"width": 1400, "depth": 700, "height": 750},
                "include_dimensions": True,
            },
        ],
        "clearance_refs": [
            {
                "role": "entry_clearance",
                "opening_id": "entry-01",
                "clear_depth_mm": 1200,
                "clear_width_mm": 1200,
            }
        ],
        "layout_notes": ["reception_desk_outside_entry_clearance"],
    },
    "door_clearance_conflict": {
        "name": "Door Clearance Conflict",
        "domain": "office",
        "objects": [
            {
                "instance_id": "desk-entry-blocked",
                "type": "desk",
                "name": "Entry Blocking Desk",
                "role": "work_surface",
                "base_point": [300, 300, 0],
                "size": {"width": 1400, "depth": 700, "height": 750},
                "include_dimensions": False,
            },
        ],
        "clearance_refs": [
            {
                "role": "entry_clearance",
                "opening_id": "entry-main",
                "clear_depth_mm": 1200,
                "clear_width_mm": 1200,
            }
        ],
        "layout_notes": ["desk_intentionally_overlaps_entry_clearance_for_failure_benchmark"],
    },
    "cabinet_pullback_conflict": {
        "name": "Cabinet Pullback Conflict",
        "domain": "office",
        "objects": [
            {
                "instance_id": "desk-01",
                "type": "desk",
                "name": "Office Desk",
                "role": "work_surface",
                "base_point": [0, 700, 0],
                "size": {"width": 1400, "depth": 700, "height": 750},
                "include_dimensions": False,
            },
            {
                "instance_id": "chair-01",
                "type": "chair",
                "name": "Task Chair",
                "role": "seating_for_desk",
                "base_point": [450, 0, 0],
                "size": {"width": 500, "depth": 500, "height": 850},
                "include_dimensions": False,
            },
            {
                "instance_id": "cabinet-01",
                "type": "cabinet",
                "name": "Back Cabinet",
                "role": "general_storage",
                "base_point": [200, 750, 0],
                "size": {"width": 1800, "depth": 600, "height": 2400},
                "include_dimensions": False,
            },
        ],
        "bindings": [
            {"from_instance_id": "chair-01", "to_instance_id": "desk-01", "relation": "seating_for_desk"},
            {"from_instance_id": "cabinet-01", "to_instance_id": "desk-01", "relation": "storage_behind_desk"},
        ],
        "clearance_refs": [
            {
                "role": "chair_pullback_clearance",
                "bound_to": "chair-01",
                "behind_depth_mm": 800,
                "side_margin_mm": 150,
            },
            {
                "role": "cabinet_front_clearance",
                "bound_to": "cabinet-01",
                "front_depth_mm": 800,
            },
        ],
        "layout_notes": ["chair_pullback_and_cabinet_front_clearance_intentionally_overlap"],
    },
    "office_desk_combo": {
        "name": "Office Desk Combo",
        "domain": "office",
        "objects": [
            {
                "instance_id": "desk-01",
                "type": "desk",
                "name": "Desk",
                "role": "work_surface",
                "base_point": [0, 600, 0],
                "size": {"width": 1400, "depth": 700, "height": 750},
                "include_dimensions": True,
            },
            {
                "instance_id": "chair-01",
                "type": "chair",
                "name": "Task Chair",
                "role": "task_seat",
                "base_point": [450, 0, 0],
                "size": {"width": 500, "depth": 500, "height": 850},
                "include_dimensions": False,
            },
            {
                "instance_id": "monitor-01",
                "type": "monitor",
                "name": "Monitor",
                "role": "screen_zone",
                "base_point": [525, 1120, 0],
                "size": {"width": 350, "depth": 80, "height": 320},
                "include_dimensions": False,
            },
        ],
    },
}


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
            include_dimensions=bool(item.get("include_dimensions", False)),
            include_label=bool(item.get("include_label", True)),
        )
        plan["object"]["instance_id"] = item["instance_id"]
        plan["object"]["role"] = item["role"]
        plan["object"]["composition_id"] = composition["composition_id"]
        plans.append(plan)
    return plans
