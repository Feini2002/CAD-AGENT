"""Build verification reports from CAD_PLAN expectations and readback evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.plan_engine.validate_plan import load_json, validate_plan
from core.verification.created_handle_scope import (
    analyze_created_handle_scope,
    created_handle_scope_check,
    created_handle_scope_ok,
    filter_entities_to_created_handles,
)
from core.verification.evidence_contract import apply_readback_report_contract


DEFAULT_TOLERANCE_MM = 1.0


def expected_from_plan(plan_path: Path) -> dict[str, Any]:
    plan = load_json(plan_path)
    errors = validate_plan(plan)
    if errors:
        raise ValueError("Invalid CAD_PLAN: " + "; ".join(errors))

    obj = plan["object"]
    placement = plan["placement"]
    base = placement.get("base_point", [0, 0, 0])
    if len(base) == 2:
        base = [base[0], base[1], 0]
    return {
        "layer": plan["drawing"]["layer"],
        "object_name": obj["name"],
        "object_type": obj["type"],
        "object_size": [obj.get("width"), obj.get("depth")],
        "base_point": base,
        "include_label": plan["drawing"].get("include_label", False),
        "include_dimensions": plan["drawing"].get("include_dimensions", False),
    }


def layer_counts(entities: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entity in entities:
        layer = str(entity.get("layer", ""))
        counts[layer] = counts.get(layer, 0) + 1
    return counts


def _entity_identity(entity: dict[str, Any]) -> str:
    handle = entity.get("handle")
    if handle is not None:
        return f"handle:{handle}"
    stable_parts = [
        str(entity.get("type", "")),
        str(entity.get("layer", "")),
        str(entity.get("text", "")),
        str(entity.get("start_point", "")),
        str(entity.get("end_point", "")),
        str(entity.get("position", "")),
    ]
    return "signature:" + "|".join(stable_parts)


def _handle_list(entities: list[dict[str, Any]]) -> list[str]:
    return sorted(str(entity["handle"]) for entity in entities if entity.get("handle") is not None)


def snapshot_diff(
    *,
    before_entities: list[dict[str, Any]],
    after_entities: list[dict[str, Any]],
) -> dict[str, Any]:
    before_by_key = {_entity_identity(entity): entity for entity in before_entities}
    after_by_key = {_entity_identity(entity): entity for entity in after_entities}
    before_keys = set(before_by_key)
    after_keys = set(after_by_key)
    added = [after_by_key[key] for key in sorted(after_keys - before_keys)]
    removed = [before_by_key[key] for key in sorted(before_keys - after_keys)]
    return {
        "before_count": len(before_entities),
        "after_count": len(after_entities),
        "added_count": len(added),
        "removed_count": len(removed),
        "unchanged_count": len(before_keys & after_keys),
        "added_handles": _handle_list(added),
        "removed_handles": _handle_list(removed),
        "added_entities": added,
        "removed_entities": removed,
    }


def bbox_from_entities(entities: list[dict[str, Any]], *, layer: str | None = None) -> dict[str, list[float]] | None:
    points: list[list[float]] = []
    for entity in entities:
        if layer and entity.get("layer") != layer:
            continue
        for key in ["start_point", "end_point", "position"]:
            value = entity.get(key)
            if isinstance(value, list) and len(value) >= 2:
                points.append([float(value[0]), float(value[1])])
        bbox = entity.get("bbox")
        if isinstance(bbox, dict):
            for key in ["min", "max"]:
                value = bbox.get(key)
                if isinstance(value, list) and len(value) >= 2:
                    points.append([float(value[0]), float(value[1])])
    if not points:
        return None
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return {"min": [min(xs), min(ys)], "max": [max(xs), max(ys)]}


def _near(actual: float, expected: float, tolerance: float) -> bool:
    return abs(actual - expected) <= tolerance


def compare_expected_to_readback(
    expected: dict[str, Any],
    entities: list[dict[str, Any]],
    *,
    tolerance_mm: float = DEFAULT_TOLERANCE_MM,
    entities_are_scoped: bool = False,
) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    counts = layer_counts(entities)
    expected_layer = expected["layer"]
    layer_entities = [entity for entity in entities if entity.get("layer") == expected_layer]
    layer_count = counts.get(expected_layer, 0)
    checks.append(
        {
            "name": "readback_scope",
            "status": "pass" if entities_are_scoped else "warning",
            "message": "Readback is scoped to this run." if entities_are_scoped else "Readback may include previous layer contents.",
        }
    )
    checks.append(
        {
            "name": "layer_entities",
            "status": "pass" if layer_count > 0 else "fail",
            "message": f"{layer_count} entities found on {expected_layer}.",
        }
    )

    bbox = bbox_from_entities(entities, layer=expected_layer)
    width, depth = expected["object_size"]
    if bbox and isinstance(width, (int, float)) and isinstance(depth, (int, float)):
        actual_width = bbox["max"][0] - bbox["min"][0]
        actual_depth = bbox["max"][1] - bbox["min"][1]
        width_ok = _near(actual_width, float(width), tolerance_mm)
        depth_ok = _near(actual_depth, float(depth), tolerance_mm)
        base = expected["base_point"]
        base_ok = _near(bbox["min"][0], float(base[0]), tolerance_mm) and _near(
            bbox["min"][1],
            float(base[1]),
            tolerance_mm,
        )
        checks.append(
            {
                "name": "bbox_size",
                "status": "pass" if width_ok and depth_ok else "fail",
                "message": f"bbox size {actual_width} x {actual_depth}, expected {width} x {depth}.",
            }
        )
        checks.append(
            {
                "name": "base_point",
                "status": "pass" if base_ok else "fail",
                "message": f"bbox min {bbox['min']}, expected base {base[:2]}.",
            }
        )
    else:
        checks.append({"name": "bbox_size", "status": "not_run", "message": "No bbox evidence."})
        checks.append({"name": "base_point", "status": "not_run", "message": "No bbox evidence."})

    if expected.get("include_label"):
        text_values = [str(entity.get("text")) for entity in layer_entities if entity.get("type") == "text"]
        checks.append(
            {
                "name": "label_text",
                "status": "pass" if expected["object_name"] in text_values else "fail",
                "message": f"labels: {text_values}",
            }
        )

    if expected.get("include_dimensions"):
        dimension_count = sum(1 for entity in layer_entities if entity.get("type") == "dimension")
        checks.append(
            {
                "name": "dimension_count",
                "status": "pass" if dimension_count >= 2 else "fail",
                "message": f"{dimension_count} dimension entities found.",
            }
        )

    return checks


def repair_suggestions_for_checks(checks: list[dict[str, str]]) -> list[dict[str, str]]:
    suggestions_by_check = {
        "geometry_readback": "Run CAD readback with scripts/inspect_dwg.py --connect-cad after execution.",
        "readback_scope": "Use an execution summary with created_handles or before/after snapshot diff to scope this run.",
        "untrusted_scope_claim": "Pass created_handles from the execution summary instead of a plain scoped boolean.",
        "created_handles_scope": "Verify the execution summary handles match entities returned by CAD readback.",
        "layer_entities": "Check that execution wrote entities to the expected preview layer.",
        "bbox_size": "Compare object width/depth in CAD_PLAN with the drawn rectangle or block bbox.",
        "base_point": "Check placement.base_point and any block insertion anchor before redrawing.",
        "label_text": "Check preview label generation and target layer filtering.",
        "dimension_count": "Check dimension creation and target layer filtering.",
        "screenshot_evidence": "Capture a new screenshot and pass an existing screenshot path.",
    }
    suggestions: list[dict[str, str]] = []
    seen: set[str] = set()
    for check in checks:
        status = check.get("status")
        name = check.get("name", "unknown")
        if status == "pass" or name in seen:
            continue
        seen.add(name)
        suggestions.append(
            {
                "check": name,
                "suggestion": suggestions_by_check.get(name, "Review this check before claiming the drawing is verified."),
            }
        )
    return suggestions


def summarize_verification_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    failed_report_ids: list[str] = []
    requires_real_cad_count = 0
    for report in reports:
        status = str(report.get("status", "unknown"))
        status_counts[status] = status_counts.get(status, 0) + 1
        if status == "failed":
            failed_report_ids.append(str(report.get("report_id", "")))
        if report.get("requires_real_cad"):
            requires_real_cad_count += 1
    return {
        "total": len(reports),
        "status_counts": status_counts,
        "failed_report_ids": failed_report_ids,
        "requires_real_cad_count": requires_real_cad_count,
        "all_geometry_verified": bool(reports) and status_counts.get("geometry_verified", 0) == len(reports),
    }


def build_verification_report(
    *,
    plan_path: Path,
    entities: list[dict[str, Any]] | None = None,
    screenshot_path: Path | str | None = None,
    execution_summary: dict[str, Any] | None = None,
    before_entities: list[dict[str, Any]] | None = None,
    entities_are_scoped: bool = False,
    created_handles: list[str] | None = None,
) -> dict[str, Any]:
    expected = expected_from_plan(plan_path)
    entities = entities or []
    screenshot = Path(screenshot_path) if screenshot_path is not None else None
    scope_checks: list[dict[str, str]] = []
    scoped_entities = entities
    created_handle_scope: dict[str, Any] | None = None
    if created_handles is not None:
        created_handle_scope = analyze_created_handle_scope(
            input_handles=created_handles,
            readback_entities=entities,
        )
        handle_scope_ok = created_handle_scope_ok(created_handle_scope)
        entities_are_scoped = handle_scope_ok
        scoped_entities = filter_entities_to_created_handles(entities, input_handles=created_handles)
        scope_checks.append(created_handle_scope_check(created_handle_scope))
    elif entities_are_scoped:
        entities_are_scoped = False
        scope_checks.append(
            {
                "name": "untrusted_scope_claim",
                "status": "warning",
                "message": "Scope claims require created_handles evidence.",
            }
        )

    checks = compare_expected_to_readback(expected, scoped_entities, entities_are_scoped=entities_are_scoped) if scoped_entities else [
        {
            "name": "geometry_readback",
            "status": "not_run",
            "message": "No CAD entity readback was provided.",
        }
    ]
    checks.extend(scope_checks)

    screenshot_valid = screenshot is not None and screenshot.exists()
    if screenshot is not None and not screenshot_valid:
        checks.append(
            {
                "name": "screenshot_evidence",
                "status": "warning",
                "message": f"Screenshot file does not exist: {screenshot}",
            }
        )

    failed = any(check["status"] == "fail" for check in checks)
    warning = any(check["status"] == "warning" for check in checks)
    geometry_verified = (
        bool(scoped_entities)
        and entities_are_scoped
        and not failed
        and not warning
        and all(check["status"] != "not_run" for check in checks)
    )
    if failed:
        status = "failed"
    elif geometry_verified:
        status = "geometry_verified"
    elif screenshot_valid:
        status = "screenshot_captured"
    elif execution_summary is not None:
        status = "executed_only"
    else:
        status = "unverified"

    actual_entities = scoped_entities if created_handles is not None else entities
    actual = {
        "entities": actual_entities,
        "layer_counts": layer_counts(actual_entities),
        "readback_available": bool(actual_entities),
        "created_handles": created_handles or [],
    }
    if created_handle_scope is not None:
        actual["created_handle_scope"] = created_handle_scope
    if before_entities is not None:
        actual["snapshot_diff"] = snapshot_diff(before_entities=before_entities, after_entities=entities)
    bbox = bbox_from_entities(scoped_entities, layer=expected["layer"])
    if bbox is not None:
        actual["bbox"] = bbox

    repair_suggestions = repair_suggestions_for_checks(checks)
    report = {
        "version": "0.1",
        "report_id": f"verification-{plan_path.stem}",
        "status": status,
        "plan_path": str(plan_path),
        "expected": expected,
        "actual": actual,
        "checks": checks,
        "evidence": {
            "execution_summary": execution_summary or {},
            "screenshot": str(screenshot) if screenshot_valid else "",
            "readback_source": "provided_entities" if entities else "none",
        },
        "limitations": [] if geometry_verified else ["Geometry has not been fully verified from CAD readback."],
        "requires_real_cad": [] if entities else ["ModelSpace entity enumeration", "dimension measurement readback"],
        "repair_suggestions": repair_suggestions,
    }
    return apply_readback_report_contract(
        report,
        screenshot_path=str(screenshot) if screenshot_valid else None,
    )
