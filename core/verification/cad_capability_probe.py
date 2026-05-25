"""Probe real AutoCAD COM drawing and readback capability on CODEX_PREVIEW."""

from __future__ import annotations

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


PREVIEW_LAYER = "CODEX_PREVIEW"
EXPECTED_TYPE_COUNTS = {"arc": 1, "circle": 1, "dimension": 2, "line": 5, "polyline": 1, "text": 1}
PROBE_BASE_POINT = [2400, 1200, 0]
PROBE_SIZE = [900, 450]


DriverFactory = Callable[[], Any]


def _default_driver_factory() -> Any:
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


def _check(name: str, status: str, message: str) -> dict[str, str]:
    return {"name": name, "status": status, "message": message}


def _collect_handles(result: object) -> list[str]:
    if result is None:
        return []
    if isinstance(result, str):
        return [result]
    if isinstance(result, list):
        return [str(item) for item in result]
    if isinstance(result, dict):
        if isinstance(result.get("handles"), list):
            return [str(handle) for handle in result["handles"]]
        if result.get("handle"):
            return [str(result["handle"])]
    return []


def _type_counts(entities: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entity in entities:
        entity_type = str(entity.get("type", "unknown"))
        counts[entity_type] = counts.get(entity_type, 0) + 1
    return dict(sorted(counts.items()))


def _layer_counts(entities: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entity in entities:
        layer = str(entity.get("layer", ""))
        counts[layer] = counts.get(layer, 0) + 1
    return dict(sorted(counts.items()))


def _bbox_from_entities(entities: list[dict[str, Any]]) -> dict[str, Any] | None:
    points: list[list[float]] = []
    for entity in entities:
        for key in ("start_point", "end_point"):
            value = entity.get(key)
            if isinstance(value, list) and len(value) >= 2:
                points.append([float(value[0]), float(value[1])])
        for value in entity.get("points", []):
            if isinstance(value, list) and len(value) >= 2:
                points.append([float(value[0]), float(value[1])])
        bbox = entity.get("bbox")
        if isinstance(bbox, dict):
            for key in ("min", "max"):
                value = bbox.get(key)
                if isinstance(value, list) and len(value) >= 2:
                    points.append([float(value[0]), float(value[1])])
    if not points:
        return None
    min_x = min(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_x = max(point[0] for point in points)
    max_y = max(point[1] for point in points)
    return {
        "min": [min_x, min_y],
        "max": [max_x, max_y],
        "size": [max_x - min_x, max_y - min_y],
    }


def _write_report(output_dir: Path | None, report: dict[str, Any]) -> None:
    if output_dir is None:
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "cad_capability_probe.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _empty_report(*, layer: str, output_dir: Path | None) -> dict[str, Any]:
    return {
        "status": "failed",
        "failure_category": "",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "active_document": "",
        "layer": layer,
        "output_dir": str(output_dir) if output_dir else "",
        "expected": {
            "type_counts": EXPECTED_TYPE_COUNTS,
            "base_point": PROBE_BASE_POINT,
            "size": PROBE_SIZE,
        },
        "created_handles": [],
        "actual": {
            "entity_count": 0,
            "type_counts": {},
            "layer_counts": {},
            "bbox": None,
        },
        "checks": [],
        "safety": {
            "writes_only_preview_layer": layer == PREVIEW_LAYER,
            "saves_dwg": False,
            "deletes_entities": False,
            "modifies_formal_layers": False,
        },
    }


def run_cad_capability_probe(
    *,
    driver_factory: DriverFactory | None = None,
    output_dir: Path | None = None,
    layer: str = PREVIEW_LAYER,
) -> dict[str, Any]:
    """Create a tiny preview-only probe and verify it through handle readback."""

    report = _empty_report(layer=layer, output_dir=output_dir)
    if layer != PREVIEW_LAYER:
        report["failure_category"] = "safety_policy_failed"
        report["checks"].append(_check("layer_policy", "fail", f"Only {PREVIEW_LAYER} is allowed."))
        _write_report(output_dir, report)
        return report

    try:
        driver = (driver_factory or _default_driver_factory)()
    except Exception as exc:
        report["status"] = "external_blocker"
        report["failure_category"] = "cad_connection_failed"
        report["error"] = str(exc)
        report["checks"].append(_check("cad_connection", "fail", str(exc)))
        _write_report(output_dir, report)
        return report

    active_document = str(getattr(getattr(driver, "doc", None), "Name", ""))
    report["active_document"] = active_document
    report["checks"].append(
        _check(
            "active_document_read",
            "pass" if active_document else "fail",
            active_document or "ActiveDocument.Name is empty.",
        )
    )
    report["checks"].append(_check("layer_policy", "pass", f"Probe layer is {PREVIEW_LAYER}."))

    try:
        if hasattr(driver, "ensure_layer"):
            driver.ensure_layer(layer)
        report["checks"].append(_check("layer_ensure", "pass", f"Layer {layer} is available."))

        x0, y0, z0 = PROBE_BASE_POINT
        width, depth = PROBE_SIZE
        rectangle = driver.draw_rectangle(
            corner1=[x0, y0, z0],
            corner2=[x0 + width, y0 + depth, z0],
            layer=layer,
            color="cyan",
        )
        rectangle_handles = _collect_handles(rectangle)
        report["checks"].append(
            _check("rectangle_handles", "pass" if len(rectangle_handles) == 4 else "fail", f"{len(rectangle_handles)} line handles returned.")
        )

        line = driver.draw_line(
            start_point=[x0 + 120, y0 + 90, z0],
            end_point=[x0 + width - 120, y0 + depth - 90, z0],
            layer=layer,
            color="cyan",
        )
        line_handles = _collect_handles(line)
        report["checks"].append(_check("line_handle", "pass" if len(line_handles) == 1 else "fail", f"{len(line_handles)} line handles returned."))

        circle = driver.draw_circle(
            center=[x0 + 270, y0 + depth / 2, z0],
            radius=90,
            layer=layer,
            color="cyan",
        )
        circle_handles = _collect_handles(circle)
        report["checks"].append(_check("circle_handle", "pass" if len(circle_handles) == 1 else "fail", f"{len(circle_handles)} circle handles returned."))

        arc = driver.draw_arc(
            center=[x0 + 570, y0 + depth / 2, z0],
            radius=100,
            start_angle=15,
            end_angle=150,
            layer=layer,
            color="cyan",
        )
        arc_handles = _collect_handles(arc)
        report["checks"].append(_check("arc_handle", "pass" if len(arc_handles) == 1 else "fail", f"{len(arc_handles)} arc handles returned."))

        polyline = driver.draw_polyline(
            points=[
                [x0 + 120, y0 + 110, z0],
                [x0 + 220, y0 + 210, z0],
                [x0 + 360, y0 + 110, z0],
            ],
            closed=True,
            layer=layer,
            color="cyan",
        )
        polyline_handles = _collect_handles(polyline)
        report["checks"].append(
            _check("polyline_handle", "pass" if len(polyline_handles) == 1 else "fail", f"{len(polyline_handles)} polyline handles returned.")
        )

        text = driver.draw_text(
            text="CAD_CAPABILITY_PROBE",
            position=[x0 + width / 2, y0 + depth / 2, z0],
            height=90,
            layer=layer,
            color="cyan",
        )
        text_handles = _collect_handles(text)
        report["checks"].append(_check("text_handle", "pass" if len(text_handles) == 1 else "fail", f"{len(text_handles)} text handles returned."))

        dimensions: list[str] = []
        dimensions.extend(
            _collect_handles(
                driver.add_dimension(
                    start_point=[x0, y0, z0],
                    end_point=[x0 + width, y0, z0],
                    text_position=[x0 + width / 2, y0 - 160, z0],
                    layer=layer,
                    color="cyan",
                )
            )
        )
        dimensions.extend(
            _collect_handles(
                driver.add_dimension(
                    start_point=[x0, y0, z0],
                    end_point=[x0, y0 + depth, z0],
                    text_position=[x0 - 160, y0 + depth / 2, z0],
                    layer=layer,
                    color="cyan",
                )
            )
        )
        report["checks"].append(_check("dimension_handles", "pass" if len(dimensions) == 2 else "fail", f"{len(dimensions)} dimension handles returned."))
        report["created_handles"] = rectangle_handles + line_handles + circle_handles + arc_handles + polyline_handles + text_handles + dimensions
    except Exception as exc:
        report["failure_category"] = "execution_failed"
        report["error"] = str(exc)
        report["checks"].append(_check("cad_write_operations", "fail", str(exc)))
        _write_report(output_dir, report)
        return report

    try:
        entities = driver.snapshot_handles(handles=report["created_handles"], layer=layer)
        entities = [entity for entity in entities if isinstance(entity, dict)]
    except Exception as exc:
        report["failure_category"] = "readback_failed"
        report["error"] = str(exc)
        report["checks"].append(_check("handle_readback", "fail", str(exc)))
        _write_report(output_dir, report)
        return report

    read_handles = {str(entity.get("handle")) for entity in entities}
    missing_handles = [handle for handle in report["created_handles"] if handle not in read_handles]
    report["actual"] = {
        "entity_count": len(entities),
        "type_counts": _type_counts(entities),
        "layer_counts": _layer_counts(entities),
        "bbox": _bbox_from_entities(entities),
    }
    report["checks"].append(
        _check(
            "handle_readback_count",
            "pass" if not missing_handles and len(entities) == len(report["created_handles"]) else "fail",
            "Readback covers created handles." if not missing_handles else f"Missing handles: {missing_handles}",
        )
    )
    report["checks"].append(
        _check(
            "readback_layer_scope",
            "pass" if report["actual"]["layer_counts"] == {layer: len(entities)} else "fail",
            f"Layer counts: {report['actual']['layer_counts']}",
        )
    )
    report["checks"].append(
        _check(
            "readback_type_counts",
            "pass" if report["actual"]["type_counts"] == EXPECTED_TYPE_COUNTS else "fail",
            f"Type counts: {report['actual']['type_counts']}",
        )
    )
    bbox = report["actual"]["bbox"]
    bbox_status = "fail"
    bbox_message = "No line bbox available."
    if isinstance(bbox, dict):
        size = bbox.get("size")
        if isinstance(size, list) and len(size) == 2:
            width_ok = abs(float(size[0]) - PROBE_SIZE[0]) <= 0.01
            depth_ok = abs(float(size[1]) - PROBE_SIZE[1]) <= 0.01
            bbox_status = "pass" if width_ok and depth_ok else "fail"
            bbox_message = f"bbox size {size}, expected {PROBE_SIZE}."
    report["checks"].append(_check("readback_bbox", bbox_status, bbox_message))
    report["checks"].append(
        _check(
            "safety_preview_only",
            "pass",
            "Probe does not save DWG, delete entities, overwrite files, or target formal layers.",
        )
    )

    failed_checks = [check for check in report["checks"] if check["status"] != "pass"]
    if failed_checks:
        report["status"] = "failed"
        if not report["failure_category"]:
            report["failure_category"] = "readback_failed"
    else:
        report["status"] = "cad_capability_verified"
        report["failure_category"] = ""
    _write_report(output_dir, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a preview-only real CAD COM capability probe.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output") / "validation_runs" / f"cad-capability-probe-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    )
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    report = run_cad_capability_probe(output_dir=output_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] == "cad_capability_verified":
        return 0
    if report["status"] == "external_blocker":
        return 2
    return 1
