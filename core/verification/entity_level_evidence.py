"""Entity-level write/readback evidence for CAD capability probes (BETA-CAD-BLOCK-03)."""

from __future__ import annotations

from typing import Any

from core.drawing_standard.drawing_standard_profile import (
    layer_mapping_resolution,
    load_drawing_standard_profile,
)

PREVIEW_LAYER = "CODEX_PREVIEW"
FAILURE_HATCH_UNVERIFIED = "hatch_unverified"
POINT_TOLERANCE_MM = 1.0


def _check(name: str, status: str, message: str, *, failure_category: str = "") -> dict[str, str]:
    payload: dict[str, str] = {"name": name, "status": status, "message": message}
    if failure_category:
        payload["failure_category"] = failure_category
    return payload


def _points_close(left: list[list[float]], right: list[list[float]], tolerance: float) -> bool:
    if len(left) != len(right):
        return False
    for a, b in zip(left, right):
        if len(a) < 2 or len(b) < 2:
            return False
        if abs(float(a[0]) - float(b[0])) > tolerance or abs(float(a[1]) - float(b[1])) > tolerance:
            return False
    return True


def layer_mapping_check(
    *,
    write_layer: str,
    layer_role: str,
    readback_layer: str,
    profile: dict | None = None,
) -> dict[str, str]:
    resolved = layer_mapping_resolution(
        profile=profile or load_drawing_standard_profile(),
        layer_role=layer_role,
        readback_layer=readback_layer,
    )
    if resolved["status"] == "pass" and write_layer != readback_layer:
        return _check(
            "layer_mapping",
            "fail",
            f"write layer {write_layer!r} != readback layer {readback_layer!r}",
            failure_category="layer_mismatch",
        )
    return _check(
        "layer_mapping",
        resolved["status"],
        resolved["message"],
        failure_category=str(resolved.get("failure_category", "")),
    )


def compare_polyline_entity(write: dict[str, Any], entity: dict[str, Any]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    expected_points = write.get("points", [])
    actual_points = entity.get("points", [])
    if isinstance(expected_points, list) and isinstance(actual_points, list):
        checks.append(
            _check(
                "points",
                "pass" if _points_close(expected_points, actual_points, POINT_TOLERANCE_MM) else "fail",
                f"expected {len(expected_points)} points, readback {len(actual_points)} points",
                failure_category="geometry_mismatch",
            )
        )
    expected_closed = bool(write.get("closed", False))
    actual_closed = bool(entity.get("closed", False))
    checks.append(
        _check(
            "closed",
            "pass" if expected_closed == actual_closed else "fail",
            f"expected closed={expected_closed}, readback closed={actual_closed}",
            failure_category="closed_mismatch",
        )
    )
    checks.append(
        layer_mapping_check(
            write_layer=str(write.get("layer", "")),
            layer_role=str(write.get("layer_role", "preview")),
            readback_layer=str(entity.get("layer", "")),
        )
    )
    return checks


def build_hatch_deferred_entry(write: dict[str, Any]) -> dict[str, Any]:
    return {
        "primitive": "hatch",
        "handle": "",
        "status": "deferred",
        "failure_category": FAILURE_HATCH_UNVERIFIED,
        "write": write,
        "readback": {},
        "checks": [
            _check(
                "hatch_write_readback",
                "deferred",
                "hatch COM write/readback is deferred in BETA-CAD-BLOCK-03; entity-level slot reserved",
                failure_category=FAILURE_HATCH_UNVERIFIED,
            ),
            layer_mapping_check(
                write_layer=str(write.get("layer", PREVIEW_LAYER)),
                layer_role=str(write.get("layer_role", "preview")),
                readback_layer="",
            ),
        ],
    }


def assess_entity_level_evidence(
    *,
    write_records: list[dict[str, Any]],
    entities_by_handle: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build per-primitive entity evidence from probe write log and readback entities."""

    evidence: list[dict[str, Any]] = []
    for record in write_records:
        primitive = str(record.get("primitive", ""))
        if record.get("status") == "deferred":
            entry = dict(record)
            if "checks" not in entry:
                entry["checks"] = [
                    _check(
                        f"{primitive}_probe",
                        "deferred",
                        str(record.get("message", "deferred")),
                        failure_category=str(record.get("failure_category", FAILURE_HATCH_UNVERIFIED)),
                    )
                ]
            evidence.append(entry)
            continue

        handle = str(record.get("handle", ""))
        write = record.get("write", {})
        if not handle or not isinstance(write, dict):
            continue
        entity = entities_by_handle.get(handle, {})
        checks: list[dict[str, str]] = []
        if primitive == "polyline":
            checks = compare_polyline_entity(write, entity)
        elif primitive == "line":
            checks.append(
                layer_mapping_check(
                    write_layer=str(write.get("layer", "")),
                    layer_role=str(write.get("layer_role", "preview")),
                    readback_layer=str(entity.get("layer", "")),
                )
            )
            if isinstance(write.get("start_point"), list) and isinstance(entity.get("start_point"), list):
                start_ok = _points_close([write["start_point"]], [entity["start_point"]], POINT_TOLERANCE_MM)
                checks.append(
                    _check(
                        "start_point",
                        "pass" if start_ok else "fail",
                        f"write {write['start_point']} vs readback {entity.get('start_point')}",
                        failure_category="geometry_mismatch",
                    )
                )
        else:
            checks.append(
                layer_mapping_check(
                    write_layer=str(write.get("layer", "")),
                    layer_role=str(write.get("layer_role", "preview")),
                    readback_layer=str(entity.get("layer", "")),
                )
            )

        status = "pass" if checks and all(check.get("status") == "pass" for check in checks) else "fail"
        if not entity:
            status = "fail"
            checks.insert(
                0,
                _check("readback_entity", "fail", f"no entity for handle {handle}", failure_category="readback_missing"),
            )
        evidence.append(
            {
                "primitive": primitive,
                "handle": handle,
                "status": status,
                "write": write,
                "readback": entity,
                "checks": checks,
            }
        )
    return evidence


def minimal_verified_entity_evidence() -> list[dict[str, Any]]:
    """Minimal entity_evidence payload for cad_capability_verified gate tests."""

    return [
        {"primitive": "polyline", "status": "pass", "handle": "PROBE_POLY"},
        {"primitive": "hatch", "status": "deferred", "failure_category": FAILURE_HATCH_UNVERIFIED},
    ]


def entity_level_evidence_allows_probe_pass(entity_evidence: list[dict[str, Any]]) -> bool:
    if not entity_evidence:
        return False
    for entry in entity_evidence:
        status = str(entry.get("status", ""))
        if status == "deferred":
            continue
        if status != "pass":
            return False
    has_polyline = any(entry.get("primitive") == "polyline" and entry.get("status") == "pass" for entry in entity_evidence)
    has_hatch = any(entry.get("primitive") == "hatch" for entry in entity_evidence)
    return has_polyline and has_hatch
