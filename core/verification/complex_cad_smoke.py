"""Complex mixed-primitive CAD smoke test for real CODEX_PREVIEW readback."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from core.path_safety import find_project_root, resolve_under_project_output
from core.safety.policy import DIAGNOSTIC_LAYER
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.verification.created_handle_scope import analyze_created_handle_scope, created_handle_scope_check
from core.verification.inspect_dwg import snapshot_entities_by_handles
from core.verification.preview_only_audit import (
    build_preview_only_audit,
    preview_only_audit_check,
    with_legacy_safety_aliases,
)


PREVIEW_LAYER = "CODEX_PREVIEW"
BASE_POINT = [52000.0, 28000.0, 0.0]
SIZE = [3600.0, 2200.0]
EXPECTED_TYPE_COUNTS = {
    "arc": 2,
    "circle": 3,
    "dimension": 2,
    "line": 11,
    "polyline": 1,
    "text": 4,
}

DriverFactory = Callable[[], Any]


def resolve_complex_output_dir(output_dir: Path, *, project_root: Path | None = None) -> Path:
    """Resolve CLI output under the repository output directory."""

    root = project_root or find_project_root(Path(__file__))
    return resolve_under_project_output(root, output_dir, label="output_dir")


def _default_driver_factory() -> Any:
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


def _check(name: str, status: str, message: str) -> dict[str, str]:
    return {"name": name, "status": status, "message": message}


def _collect_handles(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, dict):
        if isinstance(value.get("handles"), list):
            return [str(handle) for handle in value["handles"]]
        if value.get("handle"):
            return [str(value["handle"])]
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


def _type_counts_for_layer(entities: list[dict[str, Any]], layer: str) -> dict[str, int]:
    return _type_counts([entity for entity in entities if entity.get("layer") == layer])


def _bbox_from_entities(entities: list[dict[str, Any]]) -> dict[str, Any] | None:
    points: list[list[float]] = []
    for entity in entities:
        for key in ("start_point", "end_point", "position", "center"):
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


def _empty_report(*, layer: str, output_dir: Path | None) -> dict[str, Any]:
    return {
        "version": "0.1",
        "status": "failed",
        "failure_category": "",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "active_document": "",
        "layer": layer,
        "diagnostic_layer": DIAGNOSTIC_LAYER,
        "output_dir": str(output_dir) if output_dir else "",
        "expected": {
            "base_point": BASE_POINT,
            "size": SIZE,
            "type_counts": EXPECTED_TYPE_COUNTS,
        },
        "geometry_verified": False,
        "created_handles": [],
        "created_handle_count": 0,
        "actual": {
            "entity_count": 0,
            "type_counts": {},
            "layer_counts": {},
            "preview_type_counts": {},
            "diagnostic_type_counts": {},
            "bbox": None,
        },
        "checks": [],
        "safety": with_legacy_safety_aliases(build_preview_only_audit(layer=layer)),
    }


def _write_outputs(output_dir: Path | None, report: dict[str, Any]) -> None:
    if output_dir is None:
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "complex_cad_smoke_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    layer = str(report.get("layer", PREVIEW_LAYER))
    summary = {
        "status": "executed" if report.get("created_handles") else report.get("status"),
        "intent": "complex_cad_smoke",
        "layer": layer,
        "created_handles": report.get("created_handles", []),
        "created_handle_count": report.get("created_handle_count", 0),
        "expected_type_counts": report.get("expected", {}).get("type_counts", {}),
        "safety": report.get("safety") or with_legacy_safety_aliases(build_preview_only_audit(layer=layer)),
    }
    (output_dir / "complex_cad_execution_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _draw_complex_geometry(driver: Any, *, layer: str) -> tuple[list[str], list[dict[str, Any]]]:
    x0, y0, z0 = BASE_POINT
    width, height = SIZE
    handles: list[str] = []
    draw_log: list[dict[str, Any]] = []

    def add_group(group: str, value: object) -> list[str]:
        group_handles = _collect_handles(value)
        handles.extend(group_handles)
        draw_log.append({"group": group, "handles": group_handles})
        return group_handles

    add_group(
        "outer_frame",
        driver.draw_rectangle(
            corner1=[x0, y0, z0],
            corner2=[x0 + width, y0 + height, z0],
            layer=layer,
            color="cyan",
        ),
    )
    for index, dx in enumerate([900, 1800, 2700], start=1):
        add_group(
            f"grid_vertical_{index}",
            driver.draw_line(
                start_point=[x0 + dx, y0, z0],
                end_point=[x0 + dx, y0 + height, z0],
                layer=layer,
                color="cyan",
            ),
        )
    for index, dy in enumerate([550, 1100, 1650], start=1):
        add_group(
            f"grid_horizontal_{index}",
            driver.draw_line(
                start_point=[x0, y0 + dy, z0],
                end_point=[x0 + width, y0 + dy, z0],
                layer=layer,
                color="cyan",
            ),
        )
    add_group(
        "diagonal_reference",
        driver.draw_line(
            start_point=[x0 + 300, y0 + 300, z0],
            end_point=[x0 + width - 300, y0 + height - 300, z0],
            layer=layer,
            color="yellow",
        ),
    )
    route_points = [
        [x0 + 300, y0 + 450, z0],
        [x0 + 1050, y0 + 1450, z0],
        [x0 + 2100, y0 + 850, z0],
        [x0 + 3300, y0 + 1750, z0],
    ]
    add_group(
        "circulation_polyline",
        driver.draw_polyline(points=route_points, closed=False, layer=layer, color="green"),
    )
    for index, center in enumerate(
        [
            [x0 + 700, y0 + 700, z0],
            [x0 + 1800, y0 + 1200, z0],
            [x0 + 2900, y0 + 1500, z0],
        ],
        start=1,
    ):
        add_group(
            f"node_circle_{index}",
            driver.draw_circle(center=center, radius=180, layer=layer, color="magenta"),
        )
    add_group(
        "arc_sweep_1",
        driver.draw_arc(center=[x0 + 900, y0 + 1650, z0], radius=320, start_angle=210, end_angle=330, layer=layer, color="yellow"),
    )
    add_group(
        "arc_sweep_2",
        driver.draw_arc(center=[x0 + 2700, y0 + 650, z0], radius=300, start_angle=30, end_angle=160, layer=layer, color="yellow"),
    )
    text_specs = [
        ("COMPLEX_CAD_SMOKE", [x0 + 120, y0 + height - 260, z0], 160),
        ("ZONE-A", [x0 + 520, y0 + 1010, z0], 120),
        ("ROUTE", [x0 + 1550, y0 + 1280, z0], 120),
        ("NODE-C", [x0 + 2720, y0 + 1700, z0], 120),
    ]
    for index, (text, position, text_height) in enumerate(text_specs, start=1):
        add_group(
            f"text_{index}",
            driver.draw_text(
                text=text,
                position=position,
                height=text_height,
                layer=DIAGNOSTIC_LAYER,
                layer_role="diagnostic",
                color="white",
            ),
        )
    add_group(
        "dimension_width",
        driver.add_dimension(
            start_point=[x0, y0, z0],
            end_point=[x0 + width, y0, z0],
            text_position=[x0 + width / 2, y0 - 260, z0],
            layer=DIAGNOSTIC_LAYER,
            layer_role="diagnostic",
            color="cyan",
        ),
    )
    add_group(
        "dimension_height",
        driver.add_dimension(
            start_point=[x0, y0, z0],
            end_point=[x0, y0 + height, z0],
            text_position=[x0 - 260, y0 + height / 2, z0],
            layer=DIAGNOSTIC_LAYER,
            layer_role="diagnostic",
            color="cyan",
        ),
    )
    return handles, draw_log


def _deferred_report(*, layer: str, output_dir: Path | None) -> dict[str, Any]:
    report = _empty_report(layer=layer, output_dir=output_dir)
    report.update(
        {
            "status": "deferred",
            "failure_category": "",
            "geometry_verified": False,
            "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
            "deferred_reason": "no_cad",
        }
    )
    report["checks"].append(_check("real_cad_complex_smoke", "not_run", "no-cad run; complex CAD readback deferred"))
    _write_outputs(output_dir, report)
    return report


def run_complex_cad_smoke(
    *,
    driver_factory: DriverFactory | None = None,
    output_dir: Path | None = None,
    layer: str = PREVIEW_LAYER,
    include_cad: bool = True,
) -> dict[str, Any]:
    """Draw a mixed-primitive test graphic and verify it through created handles."""

    if not include_cad:
        return _deferred_report(layer=layer, output_dir=output_dir)

    report = _empty_report(layer=layer, output_dir=output_dir)
    if layer != PREVIEW_LAYER:
        report["failure_category"] = "safety_policy_failed"
        report["checks"].append(_check("layer_policy", "fail", f"Only {PREVIEW_LAYER} is allowed."))
        _write_outputs(output_dir, report)
        return report

    try:
        driver = (driver_factory or _default_driver_factory)()
    except Exception as exc:
        report["status"] = "external_blocker"
        report["failure_category"] = "cad_connection_failed"
        report["error"] = str(exc)
        report["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
        report["geometry_accuracy"] = NON_CAD_GEOMETRY_ACCURACY
        report["screenshot_role"] = SCREENSHOT_NOT_APPLICABLE
        report["checks"].append(_check("cad_connection", "fail", str(exc)))
        _write_outputs(output_dir, report)
        return report

    active_document = str(getattr(getattr(driver, "doc", None), "Name", ""))
    report["active_document"] = active_document
    report["checks"].append(_check("active_document_read", "pass" if active_document else "fail", active_document or "empty ActiveDocument.Name"))
    report["checks"].append(_check("layer_policy", "pass", f"Smoke layer is {PREVIEW_LAYER}."))

    try:
        if hasattr(driver, "ensure_layer"):
            driver.ensure_layer(layer)
            driver.ensure_layer(DIAGNOSTIC_LAYER, layer_role="diagnostic")
        report["checks"].append(_check("layer_ensure", "pass", f"Layer {layer} is available."))
        created_handles, draw_log = _draw_complex_geometry(driver, layer=layer)
        report["created_handles"] = created_handles
        report["created_handle_count"] = len(created_handles)
        report["draw_log"] = draw_log
    except Exception as exc:
        report["failure_category"] = "execution_failed"
        report["error"] = str(exc)
        report["checks"].append(_check("cad_write_operations", "fail", str(exc)))
        _write_outputs(output_dir, report)
        return report

    for group, expected_count in (
        ("outer_frame", 4),
        ("grid_vertical_1", 1),
        ("grid_vertical_2", 1),
        ("grid_vertical_3", 1),
        ("grid_horizontal_1", 1),
        ("grid_horizontal_2", 1),
        ("grid_horizontal_3", 1),
        ("diagonal_reference", 1),
        ("circulation_polyline", 1),
        ("node_circle_1", 1),
        ("node_circle_2", 1),
        ("node_circle_3", 1),
        ("arc_sweep_1", 1),
        ("arc_sweep_2", 1),
        ("text_1", 1),
        ("text_2", 1),
        ("text_3", 1),
        ("text_4", 1),
        ("dimension_width", 1),
        ("dimension_height", 1),
    ):
        record = next((item for item in report["draw_log"] if item["group"] == group), {})
        handles = record.get("handles", [])
        report["checks"].append(
            _check(f"{group}_handles", "pass" if len(handles) == expected_count else "fail", f"{len(handles)} handle(s) returned.")
        )

    try:
        entities = snapshot_entities_by_handles(driver, report["created_handles"], layer=None)
        entities = [entity for entity in entities if isinstance(entity, dict)]
    except Exception as exc:
        report["failure_category"] = "readback_failed"
        report["error"] = str(exc)
        report["checks"].append(_check("handle_readback", "fail", str(exc)))
        _write_outputs(output_dir, report)
        return report

    created_handle_scope = analyze_created_handle_scope(
        input_handles=report["created_handles"],
        readback_entities=entities,
    )
    report["created_handle_scope"] = created_handle_scope
    report["actual"] = {
        "entity_count": len(entities),
        "type_counts": _type_counts(entities),
        "layer_counts": _layer_counts(entities),
        "preview_type_counts": _type_counts_for_layer(entities, layer),
        "diagnostic_type_counts": _type_counts_for_layer(entities, DIAGNOSTIC_LAYER),
        "bbox": _bbox_from_entities(entities),
        "created_handles": [str(entity.get("handle")) for entity in entities],
        "created_handle_scope": created_handle_scope,
    }
    report["checks"].append(created_handle_scope_check(created_handle_scope))
    report["checks"].append(
        _check(
            "handle_readback_count",
            "pass" if created_handle_scope.get("miss_count", 0) == 0 else "fail",
            f"hit={created_handle_scope.get('hit_count')} miss={created_handle_scope.get('miss_handles')}",
        )
    )
    report["checks"].append(
        _check(
            "readback_layer_scope",
            "pass"
            if report["actual"]["layer_counts"] == {DIAGNOSTIC_LAYER: 6, layer: len(entities) - 6}
            else "fail",
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

    report["checks"].append(preview_only_audit_check(report.get("safety")))

    failed_checks = [check for check in report["checks"] if check["status"] != "pass"]
    if failed_checks:
        report["status"] = "failed"
        report["failure_category"] = report["failure_category"] or "readback_failed"
        report["geometry_verified"] = False
        report["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
        report["geometry_accuracy"] = NON_CAD_GEOMETRY_ACCURACY
    else:
        report["status"] = "geometry_verified"
        report["failure_category"] = ""
        report["geometry_verified"] = True
        report["evidence_state"] = EVIDENCE_READBACK_GEOMETRY_VERIFIED
        report["geometry_accuracy"] = GEOMETRY_VERIFIED_BY_READBACK
    report["screenshot_role"] = SCREENSHOT_NOT_APPLICABLE
    _write_outputs(output_dir, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a complex mixed-primitive CAD smoke test.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output") / "validation_runs" / f"complex-cad-smoke-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    )
    parser.add_argument("--no-cad", action="store_true", help="Emit a deferred report without connecting to AutoCAD.")
    args = parser.parse_args()

    output_dir = resolve_complex_output_dir(args.output_dir)
    report = run_complex_cad_smoke(output_dir=output_dir, include_cad=not args.no_cad)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] in {"geometry_verified", "deferred"}:
        return 0
    if report["status"] == "external_blocker":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
