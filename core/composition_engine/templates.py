"""Template-backed object compositions for persona delivery benchmarks."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from core.object_engine.parametric_objects import create_object_spec, object_spec_to_cad_plan


NON_CAD_GEOMETRY_ACCURACY = "not_verified_without_cad_readback"
SCREENSHOT_VISUAL_AID_ONLY = "visual_aid_only"


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
    return {
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


def write_composition_preview_svg(
    composition: dict[str, Any],
    cad_plans: list[dict[str, Any]],
    output: Path,
) -> dict[str, Any]:
    bbox = composition["bbox"]
    min_x, min_y = bbox["min"]
    max_x, max_y = bbox["max"]
    width = max(max_x - min_x, 1)
    depth = max(max_y - min_y, 1)
    margin = 40
    header_height = 64
    scale = min(720 / width, 520 / depth)
    canvas_width = int(width * scale + margin * 2)
    canvas_height = int(depth * scale + margin * 2 + header_height)

    colors = {
        "bed": "#88A3B8",
        "rug": "#D4B483",
        "table": "#9A7B4F",
        "chair": "#6F8F72",
        "desk": "#7C8FA3",
        "monitor": "#30363D",
    }
    rects: list[str] = []
    for plan in cad_plans:
        obj = plan["object"]
        base = _point3(plan["placement"]["base_point"])
        x = margin + (base[0] - min_x) * scale
        y = header_height + margin + (max_y - base[1] - obj["depth"]) * scale
        rect_w = obj["width"] * scale
        rect_h = obj["depth"] * scale
        fill = colors.get(str(obj["type"]), "#AAB2BD")
        label = escape(str(obj["name"]))
        rects.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{rect_w:.2f}" height="{rect_h:.2f}" '
            f'rx="2" fill="{fill}" stroke="#1F2933" stroke-width="1.5" />'
        )
        rects.append(
            f'<text x="{x + rect_w / 2:.2f}" y="{y + rect_h / 2:.2f}" '
            'font-family="Arial, sans-serif" font-size="13" text-anchor="middle" '
            'dominant-baseline="middle" fill="#111827">'
            f"{label}</text>"
        )

    title = escape(str(composition["name"]))
    request = escape(str(composition.get("request_text", "")))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "\n".join(
            [
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" height="{canvas_height}" viewBox="0 0 {canvas_width} {canvas_height}">',
                '<rect width="100%" height="100%" fill="#F8FAFC" />',
                f'<text x="{margin}" y="24" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#111827">{title}</text>',
                f'<text x="{margin}" y="44" font-family="Arial, sans-serif" font-size="11" fill="#4B5563">{request}</text>',
                *rects,
                "</svg>",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "status": "written",
        "output": str(output),
        "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
    }
