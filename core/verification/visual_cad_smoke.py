"""Visual CAD smoke: a readable office corner, not a coverage-number runner."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from core.path_safety import find_project_root, resolve_under_project_output
from core.verification.complex_cad_smoke import _bbox_from_entities, _check, _layer_counts, _type_counts
from core.verification.created_handle_scope import analyze_created_handle_scope, created_handle_scope_check
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.verification.inspect_dwg import snapshot_entities_by_handles
from core.verification.preview_only_audit import (
    build_preview_only_audit,
    preview_only_audit_check,
    with_legacy_safety_aliases,
)


PREVIEW_LAYER = "CODEX_PREVIEW"
BASE_POINT = [180000.0, 90000.0, 0.0]
ROOM_SIZE = [7200.0, 4200.0]
EXPECTED_TYPE_COUNTS = {
    "arc": 3,
    "circle": 6,
    "line": 42,
    "polyline": 3,
}

DriverFactory = Callable[[], Any]


def resolve_visual_output_dir(output_dir: Path, *, project_root: Path | None = None) -> Path:
    root = project_root or find_project_root(Path(__file__))
    return resolve_under_project_output(root, output_dir, label="output_dir")


def _default_driver_factory() -> Any:
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


def _collect_handles(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, dict):
        handles = value.get("handles")
        if isinstance(handles, list):
            return [str(handle) for handle in handles]
        handle = value.get("handle")
        if handle:
            return [str(handle)]
    return []


def _empty_report(*, layer: str, output_dir: Path | None, base_point: list[float]) -> dict[str, Any]:
    return {
        "version": "0.1",
        "suite_id": "visual_cad_smoke",
        "status": "failed",
        "failure_category": "",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "active_document": "",
        "layer": layer,
        "output_dir": str(output_dir) if output_dir else "",
        "expected": {
            "base_point": base_point,
            "room_size": ROOM_SIZE,
            "type_counts": EXPECTED_TYPE_COUNTS,
            "min_created_handles": 50,
            "min_visual_detail_score_percent": 70,
        },
        "visual_goal": "readable office corner: double-line walls, door swing, two detailed workstations, storage drawers, clearance cue",
        "visual_detail_score_percent": 0,
        "geometry_verified": False,
        "created_handles": [],
        "created_handle_count": 0,
        "actual": {
            "entity_count": 0,
            "type_counts": {},
            "layer_counts": {},
            "bbox": None,
        },
        "checks": [],
        "safety": with_legacy_safety_aliases(build_preview_only_audit(layer=layer)),
    }


def _write_outputs(output_dir: Path | None, report: dict[str, Any], *, visual_intent: dict[str, Any] | None = None) -> None:
    if output_dir is None:
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "visual_cad_smoke_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if visual_intent is not None:
        (output_dir / "visual_scene_intent.json").write_text(
            json.dumps(visual_intent, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    summary = {
        "status": "executed" if report.get("created_handles") else report.get("status"),
        "intent": "visual_cad_smoke",
        "layer": report.get("layer"),
        "visual_goal": report.get("visual_goal"),
        "created_handles": report.get("created_handles", []),
        "created_handle_count": report.get("created_handle_count", 0),
        "expected_type_counts": report.get("expected", {}).get("type_counts", {}),
        "visual_detail_score_percent": report.get("visual_detail_score_percent", 0),
        "safety": report.get("safety"),
    }
    (output_dir / "visual_cad_execution_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _point(base: list[float], x: float, y: float) -> list[float]:
    return [base[0] + x, base[1] + y, base[2]]


def _rect(driver: Any, *, base: list[float], x: float, y: float, w: float, d: float, layer: str, color: str) -> object:
    return driver.draw_rectangle(
        corner1=_point(base, x, y),
        corner2=_point(base, x + w, y + d),
        layer=layer,
        color=color,
    )


def _line(driver: Any, *, base: list[float], start: tuple[float, float], end: tuple[float, float], layer: str, color: str) -> object:
    return driver.draw_line(
        start_point=_point(base, start[0], start[1]),
        end_point=_point(base, end[0], end[1]),
        layer=layer,
        color=color,
    )


def _circle(driver: Any, *, base: list[float], center: tuple[float, float], radius: float, layer: str, color: str) -> object:
    return driver.draw_circle(center=_point(base, center[0], center[1]), radius=radius, layer=layer, color=color)


def _arc(
    driver: Any,
    *,
    base: list[float],
    center: tuple[float, float],
    radius: float,
    start_angle: float,
    end_angle: float,
    layer: str,
    color: str,
) -> object:
    return driver.draw_arc(
        center=_point(base, center[0], center[1]),
        radius=radius,
        start_angle=start_angle,
        end_angle=end_angle,
        layer=layer,
        color=color,
    )


def _draw_workstation(
    driver: Any,
    *,
    base: list[float],
    x: float,
    y: float,
    layer: str,
    facing: str,
) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []

    def add(group: str, value: object) -> None:
        groups.append({"group": group, "handles": _collect_handles(value)})

    add(f"{facing}_desk_outline", _rect(driver, base=base, x=x, y=y + 520, w=1500, d=760, layer=layer, color="yellow"))
    add(f"{facing}_desk_inner", _rect(driver, base=base, x=x + 70, y=y + 590, w=1360, d=620, layer=layer, color="yellow"))
    add(f"{facing}_modesty_panel", _line(driver, base=base, start=(x + 180, y + 700), end=(x + 1320, y + 700), layer=layer, color="yellow"))
    add(f"{facing}_monitor", _rect(driver, base=base, x=x + 565, y=y + 920, w=370, d=190, layer=layer, color="cyan"))
    add(f"{facing}_keyboard", _line(driver, base=base, start=(x + 470, y + 830), end=(x + 1030, y + 830), layer=layer, color="cyan"))
    add(f"{facing}_chair_seat", _circle(driver, base=base, center=(x + 750, y + 250), radius=235, layer=layer, color="yellow"))
    add(f"{facing}_chair_split", _line(driver, base=base, start=(x + 550, y + 285), end=(x + 950, y + 285), layer=layer, color="yellow"))
    add(f"{facing}_chair_back_arc", _arc(driver, base=base, center=(x + 750, y + 360), radius=330, start_angle=205, end_angle=335, layer=layer, color="yellow"))
    add(f"{facing}_chair_wheel_left", _circle(driver, base=base, center=(x + 570, y + 80), radius=42, layer=layer, color="yellow"))
    add(f"{facing}_chair_wheel_right", _circle(driver, base=base, center=(x + 930, y + 80), radius=42, layer=layer, color="yellow"))
    return groups


def _draw_visual_office_corner(driver: Any, *, base_point: list[float], layer: str) -> tuple[list[str], list[dict[str, Any]], dict[str, Any]]:
    handles: list[str] = []
    draw_log: list[dict[str, Any]] = []

    def add(group: str, value: object) -> None:
        group_handles = _collect_handles(value)
        handles.extend(group_handles)
        draw_log.append({"group": group, "handles": group_handles})

    visual_intent = {
        "version": "0.1",
        "intent": "visual_cad_smoke",
        "base_point": base_point,
        "layer": layer,
        "scene": "office_corner_visual_upgrade",
        "requirements": [
            "double-line room shell",
            "door leaf and swing arc",
            "two detailed workstation symbols",
            "storage cabinet with drawer lines",
            "clearance/working area cue",
        ],
    }

    room_w, room_d = ROOM_SIZE
    add(
        "room_outer_wall",
        driver.draw_polyline(
            points=[
                _point(base_point, 0, 0),
                _point(base_point, room_w, 0),
                _point(base_point, room_w, room_d),
                _point(base_point, 0, room_d),
            ],
            closed=True,
            layer=layer,
            color="cyan",
        ),
    )
    add(
        "room_inner_wall",
        driver.draw_polyline(
            points=[
                _point(base_point, 150, 150),
                _point(base_point, room_w - 150, 150),
                _point(base_point, room_w - 150, room_d - 150),
                _point(base_point, 150, room_d - 150),
            ],
            closed=True,
            layer=layer,
            color="cyan",
        ),
    )
    add("door_leaf", _line(driver, base=base_point, start=(150, 0), end=(1050, 0), layer=layer, color="green"))
    add("door_swing", _arc(driver, base=base_point, center=(150, 150), radius=900, start_angle=0, end_angle=90, layer=layer, color="green"))
    add("door_jamb_left", _line(driver, base=base_point, start=(150, 0), end=(150, 380), layer=layer, color="cyan"))
    add("door_jamb_right", _line(driver, base=base_point, start=(1050, 0), end=(1050, 150), layer=layer, color="cyan"))

    for item in _draw_workstation(driver, base=base_point, x=1250, y=700, layer=layer, facing="left"):
        handles.extend(item["handles"])
        draw_log.append(item)
    for item in _draw_workstation(driver, base=base_point, x=3550, y=700, layer=layer, facing="right"):
        handles.extend(item["handles"])
        draw_log.append(item)

    add("storage_outline", _rect(driver, base=base_point, x=5750, y=2450, w=980, d=520, layer=layer, color="yellow"))
    for index, y in enumerate([2550, 2650, 2750, 2850], start=1):
        add(f"storage_drawer_{index}", _line(driver, base=base_point, start=(5850, y), end=(6630, y), layer=layer, color="yellow"))
    add("storage_pull", _line(driver, base=base_point, start=(6140, 2920), end=(6340, 2920), layer=layer, color="yellow"))
    add(
        "clearance_polyline",
        driver.draw_polyline(
            points=[
                _point(base_point, 1050, 540),
                _point(base_point, 5650, 540),
                _point(base_point, 5650, 1650),
                _point(base_point, 1050, 1650),
            ],
            closed=True,
            layer=layer,
            color="green",
        ),
    )
    return handles, draw_log, visual_intent


def _visual_detail_score(type_counts: dict[str, int], *, created_handle_count: int) -> int:
    score = 0
    if created_handle_count >= 50:
        score += 35
    elif created_handle_count >= 35:
        score += 25
    elif created_handle_count >= 20:
        score += 15
    if all(type_counts.get(kind, 0) > 0 for kind in ("line", "polyline", "circle", "arc")):
        score += 25
    if type_counts.get("line", 0) >= 35 and type_counts.get("circle", 0) >= 4:
        score += 20
    if type_counts.get("arc", 0) >= 3 and type_counts.get("polyline", 0) >= 3:
        score += 20
    return min(score, 100)


def _deferred_report(*, layer: str, output_dir: Path | None, base_point: list[float]) -> dict[str, Any]:
    report = _empty_report(layer=layer, output_dir=output_dir, base_point=base_point)
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
    report["checks"].append(_check("real_cad_visual_smoke", "not_run", "no-cad run; visual CAD readback deferred"))
    _write_outputs(output_dir, report)
    return report


def run_visual_cad_smoke(
    *,
    driver_factory: DriverFactory | None = None,
    output_dir: Path | None = None,
    layer: str = PREVIEW_LAYER,
    include_cad: bool = True,
    base_point: list[float | int] | None = None,
) -> dict[str, Any]:
    """Draw a visually richer office corner and verify it through created handles."""

    resolved_base = [float(value) for value in (base_point or BASE_POINT)]
    if len(resolved_base) == 2:
        resolved_base.append(0.0)
    if not include_cad:
        return _deferred_report(layer=layer, output_dir=output_dir, base_point=resolved_base)

    report = _empty_report(layer=layer, output_dir=output_dir, base_point=resolved_base)
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
    report["checks"].append(_check("layer_policy", "pass", f"Visual smoke layer is {PREVIEW_LAYER}."))

    visual_intent: dict[str, Any] | None = None
    try:
        if hasattr(driver, "ensure_layer"):
            driver.ensure_layer(layer)
        report["checks"].append(_check("layer_ensure", "pass", f"Layer {layer} is available."))
        created_handles, draw_log, visual_intent = _draw_visual_office_corner(
            driver,
            base_point=resolved_base,
            layer=layer,
        )
        report["created_handles"] = created_handles
        report["created_handle_count"] = len(created_handles)
        report["draw_log"] = draw_log
    except Exception as exc:
        report["failure_category"] = "execution_failed"
        report["error"] = str(exc)
        report["checks"].append(_check("cad_write_operations", "fail", str(exc)))
        _write_outputs(output_dir, report, visual_intent=visual_intent)
        return report

    try:
        entities = snapshot_entities_by_handles(driver, report["created_handles"], layer=layer)
        entities = [entity for entity in entities if isinstance(entity, dict)]
    except Exception as exc:
        report["failure_category"] = "readback_failed"
        report["error"] = str(exc)
        report["checks"].append(_check("handle_readback", "fail", str(exc)))
        _write_outputs(output_dir, report, visual_intent=visual_intent)
        return report

    created_handle_scope = analyze_created_handle_scope(
        input_handles=report["created_handles"],
        readback_entities=entities,
    )
    type_counts = _type_counts(entities)
    report["created_handle_scope"] = created_handle_scope
    report["visual_detail_score_percent"] = _visual_detail_score(
        type_counts,
        created_handle_count=int(report["created_handle_count"]),
    )
    report["actual"] = {
        "entity_count": len(entities),
        "type_counts": type_counts,
        "layer_counts": _layer_counts(entities),
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
            "pass" if report["actual"]["layer_counts"] == {layer: len(entities)} else "fail",
            f"Layer counts: {report['actual']['layer_counts']}",
        )
    )
    report["checks"].append(
        _check(
            "readback_type_counts",
            "pass" if type_counts == EXPECTED_TYPE_COUNTS else "fail",
            f"expected={EXPECTED_TYPE_COUNTS} actual={type_counts}",
        )
    )
    report["checks"].append(
        _check(
            "visual_detail_score",
            "pass" if report["visual_detail_score_percent"] >= 70 else "fail",
            f"visual_detail_score_percent={report['visual_detail_score_percent']}",
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
        report["status"] = "visual_geometry_verified"
        report["failure_category"] = ""
        report["geometry_verified"] = True
        report["evidence_state"] = EVIDENCE_READBACK_GEOMETRY_VERIFIED
        report["geometry_accuracy"] = GEOMETRY_VERIFIED_BY_READBACK
    report["screenshot_role"] = SCREENSHOT_NOT_APPLICABLE
    _write_outputs(output_dir, report, visual_intent=visual_intent)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a visual CAD smoke test focused on drawing appearance.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output") / "validation_runs" / f"visual-cad-smoke-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    )
    parser.add_argument("--base-x", type=float, default=BASE_POINT[0])
    parser.add_argument("--base-y", type=float, default=BASE_POINT[1])
    parser.add_argument("--no-cad", action="store_true", help="Emit a deferred report without connecting to AutoCAD.")
    args = parser.parse_args()

    output_dir = resolve_visual_output_dir(args.output_dir)
    report = run_visual_cad_smoke(
        output_dir=output_dir,
        include_cad=not args.no_cad,
        base_point=[args.base_x, args.base_y, 0.0],
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] in {"visual_geometry_verified", "deferred"}:
        return 0
    if report["status"] == "external_blocker":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
