"""RCAD-06: controlled hatch COM smoke with created-handle readback."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from core.path_safety import find_project_root, resolve_under_project_output
from core.safety.policy import PREVIEW_LAYER
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.verification.inspect_dwg import snapshot_entities_by_handles

RCAD_06_PACKAGE_ID = "RCAD-06-HATCH"
V_PROOF_53_PACKAGE_ID = "V-PROOF-53-HATCH-ROW"
HATCH_BOUNDARY_POINTS = [
    [0.0, 0.0, 0.0],
    [100.0, 0.0, 0.0],
    [100.0, 80.0, 0.0],
    [0.0, 80.0, 0.0],
]

DriverFactory = Callable[[], Any]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _type_counts(entities: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entity in entities:
        entity_type = str(entity.get("type", "unknown"))
        counts[entity_type] = counts.get(entity_type, 0) + 1
    return dict(sorted(counts.items()))


def _hatch_pattern(entities: list[dict[str, Any]]) -> str:
    for entity in entities:
        if entity.get("type") == "hatch":
            return str(entity.get("pattern", ""))
    return ""


def _deferred_report(*, output_dir: Path, reason: str) -> dict[str, Any]:
    return {
        "version": "0.1",
        "package_id": RCAD_06_PACKAGE_ID,
        "paired_package_id": V_PROOF_53_PACKAGE_ID,
        "status": "deferred",
        "failure_category": "hatch_unverified",
        "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        "output_dir": str(output_dir),
        "geometry_verified": False,
        "created_handles": [],
        "created_handle_count": 0,
        "actual": {"type_counts": {}, "hatch_pattern": ""},
        "checks": [
            {
                "name": "hatch_cad_smoke",
                "status": "deferred",
                "message": reason,
                "failure_category": "hatch_unverified",
            }
        ],
        "safety": {
            "layer": PREVIEW_LAYER,
            "saved_dwg": False,
            "deleted_entities": False,
            "modified_formal_layers": False,
        },
    }


def run_hatch_cad_smoke(
    *,
    output_dir: Path,
    root: Path | None = None,
    no_cad: bool = False,
    driver_factory: DriverFactory | None = None,
) -> dict[str, Any]:
    root = (root or find_project_root(Path(__file__))).resolve()
    output_dir = resolve_under_project_output(root, output_dir, label="output_dir")

    if no_cad:
        report = _deferred_report(output_dir=output_dir, reason="no-cad run; hatch readback deferred")
        _write_json(output_dir / "hatch_cad_smoke_report.json", report)
        return report

    if driver_factory is None:
        from core.cad_io.autocad_com import AutoCADComDriver

        driver_factory = lambda: AutoCADComDriver(connect_existing_only=True)

    try:
        driver = driver_factory()
        if hasattr(driver, "ensure_layer"):
            driver.ensure_layer(PREVIEW_LAYER)
        draw_result = driver.draw_hatch(
            boundary_points=HATCH_BOUNDARY_POINTS,
            pattern="ANSI31",
            layer=PREVIEW_LAYER,
            layer_role="preview",
        )
        created_handles = [str(handle) for handle in draw_result.get("created_handles", []) if str(handle)]
        entities = snapshot_entities_by_handles(driver, created_handles, layer=PREVIEW_LAYER)
    except Exception as exc:
        report = _deferred_report(output_dir=output_dir, reason=str(exc))
        report["status"] = "external_blocker"
        report["failure_category"] = "cad_connection_or_write_failed"
        report["error"] = str(exc)
        _write_json(output_dir / "hatch_cad_smoke_report.json", report)
        return report

    type_counts = _type_counts(entities)
    pattern = _hatch_pattern(entities)
    geometry_verified = (
        len(created_handles) >= 2
        and type_counts.get("hatch") == 1
        and type_counts.get("polyline") == 1
        and pattern.upper() == "ANSI31"
    )
    report = {
        "version": "0.1",
        "package_id": RCAD_06_PACKAGE_ID,
        "paired_package_id": V_PROOF_53_PACKAGE_ID,
        "status": "geometry_verified" if geometry_verified else "failed",
        "failure_category": "" if geometry_verified else "hatch_readback_mismatch",
        "evidence_state": (
            EVIDENCE_READBACK_GEOMETRY_VERIFIED if geometry_verified else EVIDENCE_DEFERRED_CAD_READBACK
        ),
        "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK if geometry_verified else NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        "output_dir": str(output_dir),
        "layer": PREVIEW_LAYER,
        "geometry_verified": geometry_verified,
        "created_handles": created_handles,
        "created_handle_count": len(created_handles),
        "actual": {
            "entity_count": len(entities),
            "type_counts": type_counts,
            "hatch_pattern": pattern,
            "entities": entities,
        },
        "checks": [
            {
                "name": "created_handles",
                "status": "pass" if len(created_handles) >= 2 else "fail",
                "message": f"{len(created_handles)} handle(s) returned.",
            },
            {
                "name": "hatch_readback",
                "status": "pass" if type_counts.get("hatch") == 1 else "fail",
                "message": f"type_counts={type_counts}",
            },
            {
                "name": "boundary_readback",
                "status": "pass" if type_counts.get("polyline") == 1 else "fail",
                "message": f"type_counts={type_counts}",
            },
            {
                "name": "hatch_pattern",
                "status": "pass" if pattern.upper() == "ANSI31" else "fail",
                "message": f"pattern={pattern!r}",
            },
        ],
        "safety": {
            "layer": PREVIEW_LAYER,
            "saved_dwg": False,
            "deleted_entities": False,
            "modified_formal_layers": False,
        },
        "limitations": [
            "RCAD-06 only proves one controlled ANSI31 hatch smoke in CODEX_PREVIEW.",
            "It does not prove arbitrary hatch boundaries, formal layers, or project hatch standards.",
        ],
    }
    _write_json(output_dir / "hatch_cad_smoke_report.json", report)
    return report
