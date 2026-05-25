#!/usr/bin/env python
"""Inspect active CAD entities and produce a verification report."""

from __future__ import annotations

import argparse
import json
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

    lowered = object_name.lower()
    if "line" in lowered:
        result["type"] = "line"
        result["start_point"] = _point(getattr(entity, "StartPoint", getattr(entity, "start_point", [])))
        result["end_point"] = _point(getattr(entity, "EndPoint", getattr(entity, "end_point", [])))
    elif "text" in lowered:
        result["type"] = "text"
        result["text"] = str(getattr(entity, "TextString", getattr(entity, "text", "")))
        result["position"] = _point(getattr(entity, "InsertionPoint", getattr(entity, "position", [])))
    elif "dim" in lowered:
        result["type"] = "dimension"
        result["text"] = str(getattr(entity, "TextOverride", getattr(entity, "text", "")))
    return result


def _point(value: Any) -> list[float]:
    try:
        return [float(value[0]), float(value[1]), float(value[2] if len(value) > 2 else 0)]
    except Exception:
        return []


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

            entities = snapshot_entities(AutoCADComDriver(connect_existing_only=True), layer=args.layer)
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
