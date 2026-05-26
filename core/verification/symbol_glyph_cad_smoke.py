"""Representative symbol glyph CAD smoke: CODEX_PREVIEW write + created handles readback."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from core.execution.execute_plan import execute_plan_file
from core.execution.symbol_glyph_execute import expected_readback_type_counts
from core.path_safety import find_project_root, resolve_under_project_output
from core.symbol_engine.primitives import symbol_spec_to_cad_plan
from core.symbol_engine.readability import build_symbol_readability_report
from core.verification.complex_cad_smoke import (
    _bbox_from_entities,
    _check,
    _layer_counts,
    _type_counts,
)
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
DEFAULT_SYMBOL_SPEC = "examples/symbol_specs/surface_desk_plan.json"
BASE_POINT = [54200.0, 30200.0, 0.0]

DriverFactory = Callable[[], Any]


def resolve_symbol_glyph_output_dir(output_dir: Path, *, project_root: Path | None = None) -> Path:
    root = project_root or find_project_root(Path(__file__))
    return resolve_under_project_output(root, output_dir, label="output_dir")


def _default_driver_factory() -> Any:
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


def default_symbol_spec_path(*, project_root: Path | None = None) -> Path:
    root = project_root or find_project_root(Path(__file__))
    return root / DEFAULT_SYMBOL_SPEC


def load_symbol_spec(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_desk_glyph_plan(
    spec: dict[str, Any],
    *,
    base_point: list[float] | None = None,
    layer: str = PREVIEW_LAYER,
) -> dict[str, Any]:
    return symbol_spec_to_cad_plan(spec, base_point=base_point or BASE_POINT, layer=layer)


def _empty_report(*, layer: str, output_dir: Path | None, symbol_id: str = "") -> dict[str, Any]:
    return {
        "version": "0.1",
        "status": "failed",
        "failure_category": "",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "active_document": "",
        "layer": layer,
        "output_dir": str(output_dir) if output_dir else "",
        "symbol_id": symbol_id,
        "symbol_readability_status": "",
        "symbol_readability_report": {},
        "expected": {"base_point": BASE_POINT, "type_counts": {}},
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


def _write_outputs(output_dir: Path | None, report: dict[str, Any], *, execution_summary: dict[str, Any] | None = None) -> None:
    if output_dir is None:
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "symbol_glyph_cad_smoke_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    summary = execution_summary or {
        "status": report.get("status"),
        "intent": "draw_symbol_glyph",
        "symbol_id": report.get("symbol_id"),
        "layer": report.get("layer"),
        "created_handles": report.get("created_handles", []),
        "created_handle_count": report.get("created_handle_count", 0),
        "expected_type_counts": report.get("expected", {}).get("type_counts", {}),
        "safety": report.get("safety"),
    }
    (output_dir / "symbol_glyph_execution_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _deferred_report(
    *,
    layer: str,
    output_dir: Path | None,
    symbol_id: str,
    readability_report: dict[str, Any],
) -> dict[str, Any]:
    report = _empty_report(layer=layer, output_dir=output_dir, symbol_id=symbol_id)
    report.update(
        {
            "status": "deferred",
            "symbol_readability_status": readability_report.get("readability_status", ""),
            "symbol_readability_report": readability_report,
            "geometry_verified": False,
            "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
            "deferred_reason": "no_cad",
        }
    )
    report["checks"].append(_check("real_cad_symbol_glyph_smoke", "not_run", "no-cad run; symbol glyph readback deferred"))
    _write_outputs(output_dir, report)
    return report


def run_symbol_glyph_cad_smoke(
    *,
    symbol_spec_path: Path | None = None,
    base_point: list[float] | None = None,
    driver_factory: DriverFactory | None = None,
    output_dir: Path | None = None,
    layer: str = PREVIEW_LAYER,
    include_cad: bool = True,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Execute a representative desk glyph on CODEX_PREVIEW and verify created handles."""

    root = project_root or find_project_root(Path(__file__))
    spec_path = symbol_spec_path or default_symbol_spec_path(project_root=root)
    spec = load_symbol_spec(spec_path)
    readability_report = build_symbol_readability_report(spec)
    symbol_id = str(spec.get("symbol_id", ""))
    plan = build_desk_glyph_plan(spec, base_point=base_point, layer=layer)
    expected_type_counts = expected_readback_type_counts(plan["object"]["glyph_primitives"])
    placement = list(base_point or BASE_POINT)

    if not include_cad:
        report = _deferred_report(
            layer=layer,
            output_dir=output_dir,
            symbol_id=symbol_id,
            readability_report=readability_report,
        )
        report["expected"] = {"base_point": placement, "type_counts": expected_type_counts}
        return report

    report = _empty_report(layer=layer, output_dir=output_dir, symbol_id=symbol_id)
    report["symbol_readability_status"] = readability_report.get("readability_status", "")
    report["symbol_readability_report"] = readability_report
    report["expected"] = {"base_point": placement, "type_counts": expected_type_counts, "glyph_primitive_count": len(plan["object"]["glyph_primitives"])}

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

    plan_path = (output_dir or Path.cwd()) / "symbol_glyph_smoke_plan.json"
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    try:
        if hasattr(driver, "ensure_layer"):
            driver.ensure_layer(layer)
        report["checks"].append(_check("layer_ensure", "pass", f"Layer {layer} is available."))
        execution_summary = execute_plan_file(plan_path, driver=driver, preview_only=True)
        created_handles = [str(handle) for handle in execution_summary.get("created_handles", [])]
        report["created_handles"] = created_handles
        report["created_handle_count"] = len(created_handles)
        report["execution_summary"] = execution_summary
    except Exception as exc:
        report["failure_category"] = "execution_failed"
        report["error"] = str(exc)
        report["checks"].append(_check("cad_write_operations", "fail", str(exc)))
        _write_outputs(output_dir, report, execution_summary={"status": "failed", "error": str(exc)})
        return report

    report["checks"].append(
        _check(
            "glyph_primitive_handles",
            "pass" if report["created_handle_count"] > 0 else "fail",
            f"{report['created_handle_count']} handle(s) returned from execute_plan.",
        )
    )

    try:
        entities = snapshot_entities_by_handles(driver, report["created_handles"], layer=layer)
        entities = [entity for entity in entities if isinstance(entity, dict)]
    except Exception as exc:
        report["failure_category"] = "readback_failed"
        report["error"] = str(exc)
        report["checks"].append(_check("handle_readback", "fail", str(exc)))
        _write_outputs(output_dir, report, execution_summary=execution_summary)
        return report

    created_handle_scope = analyze_created_handle_scope(
        input_handles=report["created_handles"],
        readback_entities=entities,
    )
    report["created_handle_scope"] = created_handle_scope
    actual_type_counts = _type_counts(entities)
    report["actual"] = {
        "entity_count": len(entities),
        "type_counts": actual_type_counts,
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
            "pass" if actual_type_counts == expected_type_counts else "fail",
            f"expected={expected_type_counts} actual={actual_type_counts}",
        )
    )
    forbidden = {key: value for key, value in actual_type_counts.items() if key in {"text", "dimension"}}
    report["checks"].append(
        _check(
            "no_text_or_dimension_entities",
            "pass" if not forbidden else "fail",
            f"forbidden entities present: {forbidden}",
        )
    )
    report["checks"].append(
        _check(
            "symbol_readability_status",
            "pass" if report["symbol_readability_status"] == "symbol_readable" else "fail",
            f"readability_status={report['symbol_readability_status']}",
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
        readability_report["geometry_verified"] = True
        readability_report["evidence_state"] = EVIDENCE_READBACK_GEOMETRY_VERIFIED
    report["screenshot_role"] = SCREENSHOT_NOT_APPLICABLE
    _write_outputs(output_dir, report, execution_summary=execution_summary)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run representative symbol glyph CAD smoke (desk plan view).")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output") / "validation_runs" / f"symbol-glyph-cad-smoke-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    )
    parser.add_argument("--symbol-spec", type=Path, default=None, help="Path to SYMBOL_SPEC JSON (default desk plan).")
    parser.add_argument("--no-cad", action="store_true", help="Emit a deferred report without connecting to AutoCAD.")
    args = parser.parse_args()

    output_dir = resolve_symbol_glyph_output_dir(args.output_dir)
    report = run_symbol_glyph_cad_smoke(
        symbol_spec_path=args.symbol_spec,
        output_dir=output_dir,
        include_cad=not args.no_cad,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] in {"geometry_verified", "deferred"}:
        return 0
    if report["status"] == "external_blocker":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
