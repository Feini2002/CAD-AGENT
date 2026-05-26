"""SVG preview helpers for composition specs."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from core.verification.evidence_contract import NON_CAD_GEOMETRY_ACCURACY, SCREENSHOT_VISUAL_AID_ONLY


def _point3(point: list[Any]) -> list[float | int]:
    if len(point) == 2:
        return [point[0], point[1], 0]
    return [point[0], point[1], point[2]]


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
        "cabinet": "#8B7355",
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
