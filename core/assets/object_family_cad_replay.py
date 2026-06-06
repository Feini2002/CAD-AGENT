"""Real-CAD replay runner for object-family asset-intelligence trials."""

from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from core.assets.local_rag import PROJECT_ROOT
from core.assets.object_family_trial import build_object_family_trial
from core.execution.execute_plan import execute_plan_file
from core.execution.symbol_glyph_execute import expected_readback_type_counts
from core.path_safety import resolve_under_project_output
from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import validate_plan
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
from core.verification.preview_only_audit import preview_only_audit_check


PREVIEW_LAYER = "CODEX_PREVIEW"
DEFAULT_BRIEF = "sofa object family replay"
DEFAULT_BASE_POINT = [62000.0, 36000.0, 0.0]
DriverFactory = Callable[[], Any]


def _default_driver_factory() -> Any:
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _point3(point: list[Any]) -> list[float]:
    values = list(point)
    if len(values) == 2:
        values.append(0.0)
    return [float(values[0]), float(values[1]), float(values[2])]


def _offset_point(point: list[Any], base: list[float]) -> list[float]:
    p = _point3(point)
    return [p[0] + base[0], p[1] + base[1], p[2] + base[2]]


def _translate_primitive(item: dict[str, Any], base: list[float]) -> dict[str, Any]:
    translated = dict(item)
    primitive = str(item.get("primitive", ""))
    if primitive == "rectangle":
        translated["corner1"] = _offset_point(list(item["corner1"]), base)
        translated["corner2"] = _offset_point(list(item["corner2"]), base)
    elif primitive == "line":
        translated["start_point"] = _offset_point(list(item["start_point"]), base)
        translated["end_point"] = _offset_point(list(item["end_point"]), base)
    elif primitive == "polyline":
        translated["points"] = [_offset_point(list(point), base) for point in item.get("points", [])]
    elif primitive in {"circle", "arc"}:
        translated["center"] = _offset_point(list(item["center"]), base)
    return translated


def _plan_for_replay(plan: dict[str, Any], *, base_point: list[float]) -> dict[str, Any]:
    translated = copy.deepcopy(plan)
    base = _point3(base_point)
    glyphs = translated["object"]["glyph_primitives"]
    translated["object"]["glyph_primitives"] = [
        _translate_primitive(item, base) for item in glyphs if isinstance(item, dict)
    ]
    translated["placement"]["base_point"] = base
    translated["placement"]["placement_phrase"] = "object family real CAD replay target"
    return translated


def _expected_bbox_from_dry_run(dry_run: dict[str, Any]) -> dict[str, Any] | None:
    bbox = dry_run.get("bbox")
    if not isinstance(bbox, list) or len(bbox) != 4:
        return None
    min_x, min_y, max_x, max_y = [float(value) for value in bbox]
    return {
        "min": [min_x, min_y],
        "max": [max_x, max_y],
        "size": [max_x - min_x, max_y - min_y],
    }


def _bbox_matches(actual: dict[str, Any] | None, expected: dict[str, Any] | None, *, tolerance: float = 1.0) -> bool:
    if not actual or not expected:
        return False
    for key in ("min", "max"):
        actual_point = actual.get(key)
        expected_point = expected.get(key)
        if not isinstance(actual_point, list) or not isinstance(expected_point, list):
            return False
        if len(actual_point) < 2 or len(expected_point) < 2:
            return False
        if abs(float(actual_point[0]) - float(expected_point[0])) > tolerance:
            return False
        if abs(float(actual_point[1]) - float(expected_point[1])) > tolerance:
            return False
    return True


def _empty_report(*, output_dir: Path, brief: str, base_point: list[float]) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "kind": "object_family_cad_replay",
        "replayId": f"object-family.sofa.replay.{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "status": "failed",
        "failure_category": "",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "objectFamily": "sofa",
        "brief": brief,
        "base_point": _point3(base_point),
        "active_document": "",
        "layer": PREVIEW_LAYER,
        "output_dir": str(output_dir),
        "targetLayer": PREVIEW_LAYER,
        "savedCurrentDwg": False,
        "geometry_verified": False,
        "created_handles": [],
        "created_handle_count": 0,
        "expected": {"type_counts": {}, "bbox": None},
        "actual": {
            "entity_count": 0,
            "type_counts": {},
            "layer_counts": {},
            "bbox": None,
        },
        "checks": [],
        "artifacts": {},
        "evidenceBoundary": {
            "checked": [
                "cad_plan_validation",
                "dry_run_plan",
                "preview_layer_write",
                "created_handles_readback",
                "bbox_readback",
                "preview_only_audit",
            ],
            "notChecked": ["user_visual_acceptance", "asset_verified_reuse_replay"],
        },
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
    }


def _artifact(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def run_object_family_cad_replay(
    brief: str = DEFAULT_BRIEF,
    *,
    driver_factory: DriverFactory | None = None,
    output_dir: Path | None = None,
    base_point: list[float] | None = None,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Replay the sofa object-family trial in real CAD and verify handle readback."""

    root = project_root.resolve()
    out = resolve_under_project_output(
        root,
        output_dir or Path("output") / "validation_runs" / f"object-family-sofa-replay-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        label="output_dir",
    )
    out.mkdir(parents=True, exist_ok=True)
    base = _point3(base_point or DEFAULT_BASE_POINT)
    report = _empty_report(output_dir=out, brief=brief, base_point=base)

    trial = build_object_family_trial(brief, object_family="sofa", project_root=root)
    _write_json(out / "object_family_trial.json", trial)
    report["artifacts"]["trial"] = _artifact(out / "object_family_trial.json", root)
    if trial.get("status") != "cad_plan_draft_ready":
        report["status"] = "blocked"
        report["failure_category"] = "trial_not_ready"
        report["blockingReasons"] = list(trial.get("blockingReasons", ["object family trial did not produce a ready CAD_PLAN"]))
        _write_json(out / "object_family_cad_replay_report.json", report)
        return report

    cad_plan = _plan_for_replay(dict(trial["cadPlanDraft"]), base_point=base)
    validation_errors = validate_plan(cad_plan)
    dry_run = create_dry_run_report(cad_plan) if not validation_errors else {"status": "invalid", "validation_errors": validation_errors}
    expected_type_counts = expected_readback_type_counts(cad_plan["object"]["glyph_primitives"])
    expected_bbox = _expected_bbox_from_dry_run(dry_run)
    report["expected"] = {
        "type_counts": expected_type_counts,
        "bbox": expected_bbox,
        "glyph_primitive_count": len(cad_plan["object"]["glyph_primitives"]),
    }
    report["checks"].append(_check("cad_plan_validation", "pass" if not validation_errors else "fail", "; ".join(validation_errors) or "valid"))
    report["checks"].append(_check("dry_run_plan", "pass" if dry_run.get("status") == "valid" else "fail", str(dry_run.get("status"))))

    plan_path = out / "sofa_object_family_cad_plan.json"
    dry_run_path = out / "dry_run_report.json"
    _write_json(plan_path, cad_plan)
    _write_json(dry_run_path, dry_run)
    report["artifacts"]["cad_plan"] = _artifact(plan_path, root)
    report["artifacts"]["dry_run"] = _artifact(dry_run_path, root)
    if validation_errors or dry_run.get("status") != "valid":
        report["status"] = "blocked"
        report["failure_category"] = "cad_plan_not_executable"
        _write_json(out / "object_family_cad_replay_report.json", report)
        return report

    try:
        driver = (driver_factory or _default_driver_factory)()
    except Exception as exc:
        report["status"] = "external_blocker"
        report["failure_category"] = "cad_connection_failed"
        report["error"] = str(exc)
        report["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
        report["geometry_accuracy"] = NON_CAD_GEOMETRY_ACCURACY
        report["checks"].append(_check("cad_connection", "fail", str(exc)))
        _write_json(out / "object_family_cad_replay_report.json", report)
        return report

    active_doc = str(getattr(getattr(driver, "doc", None), "Name", ""))
    report["active_document"] = active_doc
    report["checks"].append(_check("cad_connection", "pass", "connected to active CAD driver"))
    report["checks"].append(_check("active_document_read", "pass" if active_doc else "fail", active_doc or "empty ActiveDocument.Name"))
    report["checks"].append(_check("target_layer_policy", "pass", f"targetLayer={PREVIEW_LAYER}"))

    try:
        if hasattr(driver, "ensure_layer"):
            driver.ensure_layer(PREVIEW_LAYER)
        execution_summary = execute_plan_file(
            plan_path,
            driver=driver,
            preview_only=True,
            allow_unconfirmed=True,
        )
        created_handles = [str(handle) for handle in execution_summary.get("created_handles", [])]
        execution_summary["created_handle_count"] = len(created_handles)
        execution_summary["target_bbox"] = expected_bbox
        execution_summary["savedCurrentDwg"] = False
        execution_summary["confirmation_override"] = "preview_only_object_family_replay"
        _write_json(out / "execution_summary.json", execution_summary)
        report["artifacts"]["execution_summary"] = _artifact(out / "execution_summary.json", root)
        report["execution_summary"] = execution_summary
        report["created_handles"] = created_handles
        report["created_handle_count"] = len(created_handles)
    except Exception as exc:
        report["failure_category"] = "execution_failed"
        report["error"] = str(exc)
        report["checks"].append(_check("cad_write_operations", "fail", str(exc)))
        _write_json(out / "object_family_cad_replay_report.json", report)
        return report

    report["checks"].append(
        _check(
            "created_handles",
            "pass" if report["created_handle_count"] > 0 else "fail",
            f"{report['created_handle_count']} handle(s) returned from execute_plan.",
        )
    )

    try:
        entities = snapshot_entities_by_handles(driver, report["created_handles"], layer=PREVIEW_LAYER)
        entities = [entity for entity in entities if isinstance(entity, dict)]
        _write_json(out / "readback_entities.json", {"entities": entities})
        report["artifacts"]["readback_entities"] = _artifact(out / "readback_entities.json", root)
    except Exception as exc:
        report["failure_category"] = "readback_failed"
        report["error"] = str(exc)
        report["checks"].append(_check("handle_readback", "fail", str(exc)))
        _write_json(out / "object_family_cad_replay_report.json", report)
        return report

    created_handle_scope = analyze_created_handle_scope(
        input_handles=report["created_handles"],
        readback_entities=entities,
    )
    actual_type_counts = _type_counts(entities)
    actual_bbox = _bbox_from_entities(entities)
    layer_counts = _layer_counts(entities)
    report["actual"] = {
        "entity_count": len(entities),
        "type_counts": actual_type_counts,
        "layer_counts": layer_counts,
        "bbox": actual_bbox,
        "entities": entities,
        "created_handles": [str(entity.get("handle")) for entity in entities],
        "created_handle_scope": created_handle_scope,
    }
    report["created_handle_scope"] = created_handle_scope
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
            "pass" if layer_counts == {PREVIEW_LAYER: len(entities)} else "fail",
            f"Layer counts: {layer_counts}",
        )
    )
    report["checks"].append(
        _check(
            "readback_type_counts",
            "pass" if actual_type_counts == expected_type_counts else "fail",
            f"expected={expected_type_counts} actual={actual_type_counts}",
        )
    )
    report["checks"].append(
        _check(
            "readback_bbox",
            "pass" if _bbox_matches(actual_bbox, expected_bbox) else "fail",
            f"expected={expected_bbox} actual={actual_bbox}",
        )
    )
    report["checks"].append(preview_only_audit_check(report.get("execution_summary", {}).get("safety")))
    report["checks"].append(_check("current_dwg_not_saved_by_runner", "pass", "runner did not call Save/SaveAs"))
    report["safety"] = report.get("execution_summary", {}).get("safety", {})

    failed_checks = [check for check in report["checks"] if check["status"] != "pass"]
    if failed_checks:
        report["status"] = "failed"
        report["failure_category"] = report["failure_category"] or "readback_failed"
        report["geometry_verified"] = False
        report["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
        report["geometry_accuracy"] = NON_CAD_GEOMETRY_ACCURACY
        report["screenshot_role"] = SCREENSHOT_NOT_APPLICABLE
    else:
        report["status"] = "geometry_verified"
        report["failure_category"] = ""
        report["geometry_verified"] = True
        report["evidence_state"] = EVIDENCE_READBACK_GEOMETRY_VERIFIED
        report["geometry_accuracy"] = GEOMETRY_VERIFIED_BY_READBACK
        report["screenshot_role"] = SCREENSHOT_NOT_APPLICABLE

    _write_json(out / "object_family_cad_replay_report.json", report)
    report["artifacts"]["report"] = _artifact(out / "object_family_cad_replay_report.json", root)
    _write_json(out / "object_family_cad_replay_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run real-CAD sofa object-family replay proof.")
    parser.add_argument("--brief", default=DEFAULT_BRIEF)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--base-x", type=float, default=DEFAULT_BASE_POINT[0])
    parser.add_argument("--base-y", type=float, default=DEFAULT_BASE_POINT[1])
    parser.add_argument("--base-z", type=float, default=DEFAULT_BASE_POINT[2])
    args = parser.parse_args()

    report = run_object_family_cad_replay(
        args.brief,
        output_dir=args.output_dir,
        base_point=[args.base_x, args.base_y, args.base_z],
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] == "geometry_verified":
        return 0
    if report["status"] == "external_blocker":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
