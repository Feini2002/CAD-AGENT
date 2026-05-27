"""Visual CAD smoke: annotated room plan with doors, windows, furniture, and dimensions."""

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
from core.verification.visual_room_plan_scene import (
    PREVIEW_LAYER,
    ROOM_PLAN_BASE_POINT,
    ROOM_PLAN_EXPECTED_TYPE_COUNTS,
    ROOM_PLAN_REQUIRED_GROUPS,
    ROOM_PLAN_SIZE,
    _draw_room_plan,
)

DriverFactory = Callable[[], Any]


def resolve_room_plan_output_dir(output_dir: Path, *, project_root: Path | None = None) -> Path:
    root = project_root or find_project_root(Path(__file__))
    return resolve_under_project_output(root, output_dir, label="output_dir")


def _default_driver_factory() -> Any:
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


def _empty_report(*, layer: str, output_dir: Path | None, base_point: list[float]) -> dict[str, Any]:
    return {
        "version": "0.1",
        "suite_id": "visual_room_plan_smoke",
        "status": "failed",
        "failure_category": "",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "active_document": "",
        "layer": layer,
        "output_dir": str(output_dir) if output_dir else "",
        "expected": {
            "base_point": base_point,
            "room_size": ROOM_PLAN_SIZE,
            "type_counts": ROOM_PLAN_EXPECTED_TYPE_COUNTS,
            "min_created_handles": 80,
            "min_visual_detail_score_percent": 85,
            "required_visual_groups": list(ROOM_PLAN_REQUIRED_GROUPS),
        },
        "visual_goal": "annotated room plan: segmented walls, door swing, window symbol, dimensions, labels, and furniture cluster",
        "visual_detail_score_percent": 0,
        "geometry_verified": False,
        "created_handles": [],
        "created_handle_count": 0,
        "required_visual_groups": {"hit_counts": {}, "missed": list(ROOM_PLAN_REQUIRED_GROUPS)},
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
    (output_dir / "visual_room_plan_smoke_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if visual_intent is not None:
        (output_dir / "visual_room_plan_intent.json").write_text(
            json.dumps(visual_intent, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    summary = {
        "status": "executed" if report.get("created_handles") else report.get("status"),
        "intent": "visual_room_plan_smoke",
        "layer": report.get("layer"),
        "visual_goal": report.get("visual_goal"),
        "created_handles": report.get("created_handles", []),
        "created_handle_count": report.get("created_handle_count", 0),
        "required_visual_groups": report.get("required_visual_groups"),
        "expected_type_counts": report.get("expected", {}).get("type_counts", {}),
        "visual_detail_score_percent": report.get("visual_detail_score_percent", 0),
        "safety": report.get("safety"),
    }
    (output_dir / "visual_room_plan_execution_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _required_group_summary(draw_log: list[dict[str, Any]]) -> dict[str, Any]:
    hit_counts: dict[str, int] = {group: 0 for group in ROOM_PLAN_REQUIRED_GROUPS}
    for record in draw_log:
        group = str(record.get("visual_group", ""))
        if group in hit_counts:
            hit_counts[group] += len(record.get("handles", []))
    missed = [group for group, count in hit_counts.items() if count <= 0]
    return {"hit_counts": hit_counts, "missed": missed}


def _visual_detail_score(type_counts: dict[str, int], *, created_handle_count: int, required_groups: dict[str, Any]) -> int:
    score = 0
    if created_handle_count >= 90:
        score += 30
    elif created_handle_count >= 80:
        score += 25
    elif created_handle_count >= 60:
        score += 15
    if all(type_counts.get(kind, 0) > 0 for kind in ("line", "polyline", "circle", "arc", "text", "dimension")):
        score += 30
    if type_counts.get("line", 0) >= 60 and type_counts.get("text", 0) >= 5 and type_counts.get("dimension", 0) >= 2:
        score += 25
    if not required_groups.get("missed"):
        score += 15
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
    report["checks"].append(_check("real_cad_visual_room_plan", "not_run", "no-cad run; visual CAD readback deferred"))
    _write_outputs(output_dir, report)
    return report


def run_visual_room_plan_smoke(
    *,
    driver_factory: DriverFactory | None = None,
    output_dir: Path | None = None,
    layer: str = PREVIEW_LAYER,
    include_cad: bool = True,
    base_point: list[float | int] | None = None,
) -> dict[str, Any]:
    """Draw and verify an annotated CAD room plan through created handles."""

    resolved_base = [float(value) for value in (base_point or ROOM_PLAN_BASE_POINT)]
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
    report["checks"].append(_check("layer_policy", "pass", f"Visual room plan layer is {PREVIEW_LAYER}."))

    visual_intent: dict[str, Any] | None = None
    try:
        if hasattr(driver, "ensure_layer"):
            driver.ensure_layer(layer)
        report["checks"].append(_check("layer_ensure", "pass", f"Layer {layer} is available."))
        created_handles, draw_log, visual_intent = _draw_room_plan(driver, base_point=resolved_base, layer=layer)
        report["created_handles"] = created_handles
        report["created_handle_count"] = len(created_handles)
        report["draw_log"] = draw_log
        report["required_visual_groups"] = _required_group_summary(draw_log)
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
        required_groups=report["required_visual_groups"],
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
            "pass" if type_counts == ROOM_PLAN_EXPECTED_TYPE_COUNTS else "fail",
            f"expected={ROOM_PLAN_EXPECTED_TYPE_COUNTS} actual={type_counts}",
        )
    )
    report["checks"].append(
        _check(
            "required_visual_groups",
            "pass" if not report["required_visual_groups"].get("missed") else "fail",
            f"missed={report['required_visual_groups'].get('missed')}",
        )
    )
    report["checks"].append(
        _check(
            "visual_detail_score",
            "pass" if report["visual_detail_score_percent"] >= 85 else "fail",
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
    parser = argparse.ArgumentParser(description="Run VCAD-02 visual room plan smoke.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output") / "validation_runs" / f"visual-room-plan-smoke-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    )
    parser.add_argument("--base-x", type=float, default=ROOM_PLAN_BASE_POINT[0])
    parser.add_argument("--base-y", type=float, default=ROOM_PLAN_BASE_POINT[1])
    parser.add_argument("--no-cad", action="store_true", help="Emit a deferred report without connecting to AutoCAD.")
    args = parser.parse_args()

    output_dir = resolve_room_plan_output_dir(args.output_dir)
    report = run_visual_room_plan_smoke(
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
