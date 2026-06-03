#!/usr/bin/env python
"""Inspect active CAD entities and produce a verification report."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from core.verification.verification_report import build_verification_report


def normalize_com_entity(entity: Any) -> dict[str, Any]:
    """Convert a small subset of COM-like CAD entities into plain data."""

    object_name = str(getattr(entity, "ObjectName", getattr(entity, "object_name", "")))
    layer = str(getattr(entity, "Layer", getattr(entity, "layer", "")))
    handle = str(getattr(entity, "Handle", getattr(entity, "handle", "")))
    result: dict[str, Any] = {
        "handle": handle,
        "object_name": object_name,
        "layer": layer,
        "type": "unknown",
    }
    lineweight = _int(getattr(entity, "Lineweight", getattr(entity, "lineweight", None)))
    if lineweight is not None:
        result["lineweight"] = lineweight
    linetype = str(getattr(entity, "Linetype", getattr(entity, "linetype", ""))).strip()
    if linetype:
        result["linetype"] = linetype
    linetype_scale = _float(getattr(entity, "LinetypeScale", getattr(entity, "linetype_scale", None)))
    if linetype_scale is not None:
        result["linetype_scale"] = linetype_scale
    color = _color(getattr(entity, "Color", getattr(entity, "color", None)))
    if color is not None:
        result["color"] = color

    lowered = object_name.lower()
    if "dim" in lowered:
        result["type"] = "dimension"
        result["text"] = str(getattr(entity, "TextOverride", getattr(entity, "text", "")))
        style_name = str(getattr(entity, "StyleName", getattr(entity, "style_name", ""))).strip()
        if style_name:
            result["style_name"] = style_name
        measurement = _float(getattr(entity, "Measurement", getattr(entity, "measurement", None)))
        if measurement is not None:
            result["measurement"] = measurement
        text_height = _float(getattr(entity, "TextHeight", getattr(entity, "text_height", None)))
        if text_height is not None:
            result["text_height"] = text_height
        text_position = _point(getattr(entity, "TextPosition", getattr(entity, "text_position", [])))
        if text_position:
            result["text_position"] = text_position
        xline1 = _point(getattr(entity, "XLine1Point", getattr(entity, "xline1_point", [])))
        if xline1:
            result["xline1_point"] = xline1
        xline2 = _point(getattr(entity, "XLine2Point", getattr(entity, "xline2_point", [])))
        if xline2:
            result["xline2_point"] = xline2
        bbox = _bounding_box_from_com_entity(entity)
        if bbox is not None:
            result["bbox"] = bbox
    elif "polyline" in lowered:
        points = _polyline_points(getattr(entity, "Coordinates", getattr(entity, "coordinates", [])))
        result["type"] = "polyline"
        result["points"] = points
        result["closed"] = bool(getattr(entity, "Closed", getattr(entity, "closed", False)))
        bbox = _bbox_from_points(points)
        if bbox:
            result["bbox"] = bbox
    elif "circle" in lowered:
        center = _point(getattr(entity, "Center", getattr(entity, "center", [])))
        radius = _float(getattr(entity, "Radius", getattr(entity, "radius", None)))
        result["type"] = "circle"
        result["center"] = center
        result["radius"] = radius
        if len(center) >= 2 and radius is not None:
            result["bbox"] = {
                "min": [center[0] - radius, center[1] - radius],
                "max": [center[0] + radius, center[1] + radius],
            }
    elif "arc" in lowered:
        center = _point(getattr(entity, "Center", getattr(entity, "center", [])))
        radius = _float(getattr(entity, "Radius", getattr(entity, "radius", None)))
        result["type"] = "arc"
        result["center"] = center
        result["radius"] = radius
        result["start_angle"] = _float(getattr(entity, "StartAngle", getattr(entity, "start_angle", None)))
        result["end_angle"] = _float(getattr(entity, "EndAngle", getattr(entity, "end_angle", None)))
        if len(center) >= 2 and radius is not None:
            result["bbox"] = {
                "min": [center[0] - radius, center[1] - radius],
                "max": [center[0] + radius, center[1] + radius],
            }
    elif "line" in lowered:
        result["type"] = "line"
        result["start_point"] = _point(getattr(entity, "StartPoint", getattr(entity, "start_point", [])))
        result["end_point"] = _point(getattr(entity, "EndPoint", getattr(entity, "end_point", [])))
    elif "text" in lowered:
        result["type"] = "text"
        result["text"] = str(getattr(entity, "TextString", getattr(entity, "text", "")))
        result["position"] = _point(getattr(entity, "InsertionPoint", getattr(entity, "position", [])))
    elif "hatch" in lowered:
        result["type"] = "hatch"
        result["pattern"] = str(getattr(entity, "PatternName", getattr(entity, "pattern", "")))
        pattern_scale = _float(getattr(entity, "PatternScale", getattr(entity, "scale", None)))
        if pattern_scale is not None:
            result["scale"] = pattern_scale
        bbox = _bounding_box_from_com_entity(entity)
        if bbox is not None:
            result["bbox"] = bbox
    elif "blockreference" in lowered:
        result["type"] = "block_reference"
        result["block_name"] = str(
            getattr(entity, "EffectiveName", getattr(entity, "Name", getattr(entity, "block_name", "")))
        )
        result["insertion_point"] = _point(getattr(entity, "InsertionPoint", getattr(entity, "insertion_point", [])))
        rotation = _float(getattr(entity, "Rotation", getattr(entity, "rotation", None)))
        if rotation is not None:
            result["rotation"] = math.degrees(rotation)
        xscale = _float(getattr(entity, "XScaleFactor", getattr(entity, "xscale", None)))
        yscale = _float(getattr(entity, "YScaleFactor", getattr(entity, "yscale", None)))
        zscale = _float(getattr(entity, "ZScaleFactor", getattr(entity, "zscale", None)))
        if xscale is not None and yscale is not None and zscale is not None:
            result["scale"] = [xscale, yscale, zscale]
        bbox = _bounding_box_from_com_entity(entity)
        if bbox is not None:
            result["bbox"] = bbox
        attributes = _attributes_from_com_entity(entity)
        if attributes:
            result["attributes"] = attributes
    return result


def _point(value: Any) -> list[float]:
    try:
        return [float(value[0]), float(value[1]), float(value[2] if len(value) > 2 else 0)]
    except Exception:
        return []


def _float(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def _int(value: Any) -> int | None:
    try:
        return int(round(float(value)))
    except Exception:
        return None


def _color(value: Any) -> int | str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    try:
        return int(round(float(value)))
    except Exception:
        return str(value)


def _polyline_points(value: Any) -> list[list[float]]:
    if value is None:
        return []
    try:
        values = list(value)
    except Exception:
        return []
    if not values:
        return []
    first = values[0]
    if isinstance(first, (list, tuple)):
        return [_point(point) for point in values]
    points: list[list[float]] = []
    for index in range(0, len(values) - 1, 2):
        points.append([float(values[index]), float(values[index + 1]), 0.0])
    return points


def _bounding_box_from_com_entity(entity: Any) -> dict[str, list[float]] | None:
    try:
        minimum, maximum = entity.GetBoundingBox()
        min_point = _point(minimum)
        max_point = _point(maximum)
        if len(min_point) >= 2 and len(max_point) >= 2:
            return {"min": min_point[:2], "max": max_point[:2]}
    except Exception:
        pass
    return None


def _attributes_from_com_entity(entity: Any) -> dict[str, str]:
    attributes: dict[str, str] = {}
    get_attributes = getattr(entity, "GetAttributes", None)
    if not callable(get_attributes):
        return attributes
    try:
        for attribute in get_attributes():
            tag = str(getattr(attribute, "TagString", getattr(attribute, "Tag", ""))).strip()
            if not tag:
                continue
            text = str(getattr(attribute, "TextString", getattr(attribute, "Text", "")))
            attributes[tag] = text
    except Exception:
        return {}
    return attributes


def _bbox_from_points(points: list[list[float]]) -> dict[str, list[float]] | None:
    if not points:
        return None
    xs = [point[0] for point in points if len(point) >= 2]
    ys = [point[1] for point in points if len(point) >= 2]
    if not xs or not ys:
        return None
    return {"min": [min(xs), min(ys)], "max": [max(xs), max(ys)]}


def snapshot_entities(driver: Any, *, layer: str | None = None) -> list[dict[str, Any]]:
    if hasattr(driver, "snapshot_modelspace"):
        entities = driver.snapshot_modelspace(layer=layer)
        return [entity for entity in entities if isinstance(entity, dict)]

    model_space = getattr(driver, "model_space", None)
    if model_space is None:
        return []
    result = [normalize_com_entity(entity) for entity in model_space]
    if layer:
        result = [entity for entity in result if entity.get("layer") == layer]
    return result


def snapshot_entities_by_handles(driver: Any, handles: list[str], *, layer: str | None = None) -> list[dict[str, Any]]:
    if not handles:
        return []

    if hasattr(driver, "snapshot_handles"):
        entities = driver.snapshot_handles(handles=handles, layer=layer)
        return [entity for entity in entities if isinstance(entity, dict)]

    doc = getattr(driver, "doc", None)
    if doc is None or not hasattr(doc, "HandleToObject"):
        return []

    entities: list[dict[str, Any]] = []
    for handle in handles:
        try:
            entity = doc.HandleToObject(str(handle))
        except Exception:
            continue
        normalized = normalize_com_entity(entity)
        if layer and normalized.get("layer") != layer:
            continue
        entities.append(normalized)
    return entities


def load_execution_summary(path: Path | None) -> tuple[dict[str, Any] | None, list[str] | None]:
    if path is None:
        return None, None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Execution summary must be a JSON object.")
    handles = value.get("created_handles")
    if isinstance(handles, list):
        return value, [str(handle) for handle in handles]
    return value, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a DWG or active CAD document.")
    parser.add_argument("--dwg", type=Path, help="Optional DWG path.")
    parser.add_argument("--plan", type=Path, help="CAD_PLAN to compare against.")
    parser.add_argument("--layer", default="CODEX_PREVIEW", help="Layer to inspect.")
    parser.add_argument("--screenshot", type=Path, help="Optional screenshot evidence path.")
    parser.add_argument("--execution-summary", type=Path, help="Optional execute_plan JSON summary with created_handles.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument(
        "--no-cad",
        action="store_true",
        help="Do not connect to AutoCAD; emit an unverified report shell.",
    )
    parser.add_argument(
        "--connect-cad",
        action="store_true",
        help="Connect to the active AutoCAD document and read ModelSpace entities.",
    )
    args = parser.parse_args()
    execution_summary, created_handles = load_execution_summary(args.execution_summary)

    entities: list[dict[str, Any]] = []
    if args.connect_cad and not args.no_cad:
        try:
            from core.cad_io.autocad_com import AutoCADComDriver

            driver = AutoCADComDriver(connect_existing_only=True)
            if created_handles:
                entities = snapshot_entities_by_handles(driver, created_handles, layer=args.layer)
            else:
                entities = snapshot_entities(driver, layer=args.layer)
        except Exception as exc:
            if args.format == "json" and args.plan:
                report = build_verification_report(plan_path=args.plan, screenshot_path=args.screenshot)
                report["limitations"].append(f"CAD readback failed: {exc}")
                print(json.dumps(report, ensure_ascii=False, indent=2))
                return 0
            print(f"inspect_dwg.py: CAD readback unavailable: {exc}")

    if args.plan:
        report = build_verification_report(
            plan_path=args.plan,
            entities=entities,
            screenshot_path=args.screenshot,
            execution_summary=execution_summary,
            created_handles=created_handles,
        )
        if args.dwg:
            report["limitations"].append("--dwg path is recorded only; opening a DWG file is not implemented yet.")
        if args.format == "json":
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print("DWG INSPECTION REPORT")
            print(f"- status: {report['status']}")
            print(f"- plan: {report['plan_path']}")
            print(f"- layer: {args.layer}")
            print(f"- entities: {len(entities)}")
            for check in report["checks"]:
                print(f"- {check['name']}: {check['status']} ({check.get('message', '')})")
        return 0

    print("DWG INSPECTION")
    print(f"- dwg: {args.dwg if args.dwg else 'active CAD document'}")
    print(f"- layer: {args.layer}")
    print(f"- entities: {len(entities)}")
    if not entities:
        print("- status: no readback evidence available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
