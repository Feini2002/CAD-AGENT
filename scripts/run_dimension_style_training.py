#!/usr/bin/env python3
"""Run focused CAD training for 10 Chinese dimension styles."""

from __future__ import annotations

import argparse
import ctypes
import json
import sys
import time
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.training.dimension_style_training import TRAINING_ID, run_dimension_style_training  # noqa: E402
from core.safety.policy import PREVIEW_LAYER  # noqa: E402


DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "training_queues" / TRAINING_ID


def _switch_to_input_desktop() -> dict[str, Any]:
    if sys.platform != "win32":
        return {"status": "not_required", "reason": "non-Windows platform"}

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    access = 0x0001 | 0x0002 | 0x0040 | 0x0080 | 0x0100
    input_desktop = user32.OpenInputDesktop(0, False, access)
    if not input_desktop:
        return {"status": "fail", "api": "OpenInputDesktop", "lastError": int(kernel32.GetLastError())}
    ok = bool(user32.SetThreadDesktop(input_desktop))
    return {
        "status": "pass" if ok else "fail",
        "api": "SetThreadDesktop",
        "lastError": int(kernel32.GetLastError()),
        "reason": "AutoCAD COM runs on the interactive Default desktop.",
    }


def _driver(fake_cad: bool) -> Any:
    if fake_cad:
        from core.verification.fake_cad_driver import FakeCadDriver

        return FakeCadDriver()
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


def _normalized_document_path(value: str) -> str:
    try:
        return str(Path(value).resolve()).casefold()
    except Exception:
        return str(value).strip().casefold()


def _target_document_from_cleanup_report(report_path: Path | None) -> str | None:
    if report_path is None:
        return None
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    active_document = data.get("activeDocument")
    if not isinstance(active_document, dict):
        return None
    full_name = active_document.get("fullName")
    if isinstance(full_name, str) and full_name.strip():
        return full_name
    name = active_document.get("name")
    return name if isinstance(name, str) and name.strip() else None


def _style_token(value: Any) -> str:
    return str(value or "").strip().casefold()


def _style_aliases(row: dict[str, Any]) -> set[str]:
    return {
        _style_token(row.get("styleId")),
        _style_token(row.get("cadStyleName")),
        _style_token(row.get("visibleTitle")),
        _style_token(row.get("styleName")),
        _style_token(row.get("dimensionKind")),
        _style_token(row.get("chainRole")),
        _style_token(row.get("sample")),
    } - {""}


def _style_matches(row: dict[str, Any], requested: str | None) -> bool:
    requested_token = _style_token(requested)
    if not requested_token:
        return True
    aliases = _style_aliases(row)
    return requested_token in aliases or any(requested_token in alias or alias in requested_token for alias in aliases)


def _report_style_aliases(data: dict[str, Any], requested: str | None) -> set[str]:
    aliases = {_style_token(requested)}
    for key in ("dimensionStyleSpecs", "styleReports"):
        rows = data.get(key)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if isinstance(row, dict) and _style_matches(row, requested):
                aliases.update(_style_aliases(row))
    audit = data.get("audit")
    if isinstance(audit, dict):
        rows = audit.get("rows")
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict) and _style_matches(row, requested):
                    aliases.update(_style_aliases(row))
    return {alias for alias in aliases if alias}


def _style_keyed_value(
    data: dict[str, Any],
    bucket_name: str,
    requested: str | None,
) -> tuple[str | None, Any, list[str]]:
    bucket = data.get(bucket_name)
    if not isinstance(bucket, dict):
        return None, None, []
    available = [str(key) for key in bucket.keys()]
    if not requested:
        return None, None, available
    aliases = _report_style_aliases(data, requested)
    keyed = {_style_token(key): str(key) for key in bucket.keys()}
    for alias in aliases:
        key = keyed.get(alias)
        if key is not None:
            return key, bucket[key], available
    for key in available:
        key_token = _style_token(key)
        if any(alias in key_token or key_token in alias for alias in aliases):
            return key, bucket[key], available
    return None, None, available


def _panel_bounds_from_cleanup_report(report_path: Path | None, only_style: str | None) -> dict[str, Any]:
    if report_path is None or not only_style:
        return {"status": "not_run"}
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "fail", "reason": f"cleanup report is unreadable: {exc}", "report": str(report_path)}
    style_key, bounds, available = _style_keyed_value(data, "panelBoundsByStyle", only_style)
    if not isinstance(bounds, dict):
        return {
            "status": "fail",
            "reason": "cleanup report has no panelBoundsByStyle entry for requested style",
            "report": str(report_path),
            "requestedStyle": only_style,
            "availableStyles": available,
        }
    return {
        "status": "pass",
        "report": str(report_path),
        "requestedStyle": only_style,
        "styleKey": style_key,
        "bounds": bounds,
    }


def _iter_documents(documents: Any) -> list[Any]:
    item = getattr(documents, "Item", None)
    if item is not None:
        try:
            count = int(getattr(documents, "Count", 0))
        except Exception:
            count = 0
        result: list[Any] = []
        seen: set[int] = set()
        for index in range(count):
            for candidate in (index, index + 1):
                try:
                    document = item(candidate)
                except Exception:
                    continue
                marker = id(document)
                if marker in seen:
                    continue
                seen.add(marker)
                result.append(document)
                break
        if result:
            return result
    try:
        return list(documents)
    except Exception:
        return []


def _activate_target_document(driver: Any, target_document: str | None) -> dict[str, Any]:
    if not target_document:
        return {"status": "not_run", "reason": "no target document requested"}
    app = getattr(driver, "app", None)
    documents = getattr(app, "Documents", None)
    if documents is None:
        return {"status": "fail", "reason": "driver app has no Documents collection", "targetDocument": target_document}

    target_key = _normalized_document_path(target_document)
    seen: list[str] = []
    for document in _iter_documents(documents):
        full_name = ""
        try:
            full_name = str(getattr(document, "FullName", "") or getattr(document, "Name", ""))
        except Exception as exc:
            seen.append(f"<unreadable: {exc}>")
            continue
        seen.append(full_name)
        if _normalized_document_path(full_name) != target_key:
            continue
        try:
            document.Activate()
        except Exception:
            pass
        resolved_document = document
        resolved_full_name = full_name
        model_space = None
        model_space_error = ""
        for attempt in range(3):
            candidates = [resolved_document]
            try:
                active_document = app.ActiveDocument
                active_full_name = str(getattr(active_document, "FullName", "") or getattr(active_document, "Name", ""))
                if _normalized_document_path(active_full_name) == target_key:
                    candidates.insert(0, active_document)
            except Exception:
                pass
            for candidate_document in candidates:
                try:
                    candidate_model_space = candidate_document.ModelSpace
                except Exception as exc:
                    model_space_error = str(exc)
                    continue
                try:
                    candidate_full_name = str(
                        getattr(candidate_document, "FullName", "") or getattr(candidate_document, "Name", "")
                    )
                except Exception:
                    candidate_full_name = resolved_full_name
                resolved_document = candidate_document
                resolved_full_name = candidate_full_name
                model_space = candidate_model_space
                break
            if model_space is not None:
                break
            if attempt < 2:
                time.sleep(0.2)
        if model_space is None:
            return {
                "status": "fail",
                "reason": f"target document has no ModelSpace: {model_space_error}",
                "targetDocument": target_document,
                "matchedDocument": full_name,
            }
        driver.doc = resolved_document
        driver.model_space = model_space
        return {"status": "pass", "targetDocument": target_document, "matchedDocument": resolved_full_name}

    return {"status": "fail", "reason": "target document is not open", "targetDocument": target_document, "openDocuments": seen}


def _cleanup_previous_handles(driver: Any, report_path: Path | None, *, only_style: str | None = None) -> dict[str, Any]:
    if report_path is None:
        return {"status": "not_run"}
    data = json.loads(report_path.read_text(encoding="utf-8"))
    style_key = None
    if only_style:
        style_key, handles, available_styles = _style_keyed_value(data, "panelHandlesByStyle", only_style)
        if not isinstance(handles, list):
            return {
                "status": "fail",
                "reason": "cleanup report has no panelHandlesByStyle entry for requested style",
                "report": str(report_path),
                "requestedStyle": only_style,
                "availableStyles": available_styles,
                "scope": {"layer": PREVIEW_LAYER, "source": "previous_panelHandlesByStyle"},
            }
        cleanup_source = "previous_panelHandlesByStyle"
    else:
        handles = data.get("createdHandles")
        cleanup_source = "previous_createdHandles"
    if not isinstance(handles, list):
        return {"status": "fail", "reason": "cleanup report has no createdHandles", "report": str(report_path)}
    doc = getattr(driver, "doc", None)
    if doc is None or not hasattr(doc, "HandleToObject"):
        return {"status": "fail", "reason": "driver does not support HandleToObject", "report": str(report_path)}
    deleted: list[str] = []
    skipped: list[dict[str, Any]] = []
    for handle in [str(item) for item in handles if item]:
        try:
            entity = doc.HandleToObject(handle)
        except Exception as exc:
            skipped.append({"handle": handle, "reason": f"not_found: {exc}"})
            continue
        layer = str(getattr(entity, "Layer", ""))
        if layer != PREVIEW_LAYER:
            skipped.append({"handle": handle, "reason": "layer_not_preview", "layer": layer})
            continue
        try:
            entity.Delete()
            deleted.append(handle)
        except Exception as exc:
            skipped.append({"handle": handle, "reason": f"delete_failed: {exc}", "layer": layer})
    try:
        doc.Regen(1)
    except Exception:
        pass
    return {
        "status": "pass",
        "report": str(report_path),
        "requestedHandleCount": len(handles),
        "deletedCount": len(deleted),
        "deletedHandles": deleted,
        "skippedCount": len(skipped),
        "skipped": skipped[:40],
        "scope": {
            "layer": PREVIEW_LAYER,
            "source": cleanup_source,
            "requestedStyle": only_style,
            "styleKey": style_key,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create and audit 10 Chinese dimension styles in CAD.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--fake-cad", action="store_true", help="Use the in-memory fake CAD driver.")
    parser.add_argument("--cleanup-report", type=Path, help="Delete previous createdHandles on CODEX_PREVIEW before drawing.")
    parser.add_argument("--only-style", help="Repair only one style panel; matches styleId, CAD style name, or visible title.")
    parser.add_argument("--summary-only", action="store_true", help="Print a compact summary while still writing the full report.")
    args = parser.parse_args()

    desktop_switch = {"status": "skipped", "reason": "fake CAD driver"} if args.fake_cad else _switch_to_input_desktop()
    driver = _driver(args.fake_cad)
    target_document_switch = (
        {"status": "skipped", "reason": "fake CAD driver"}
        if args.fake_cad
        else _activate_target_document(driver, _target_document_from_cleanup_report(args.cleanup_report))
    )
    if target_document_switch.get("status") == "fail":
        print(json.dumps({"status": "fail", "targetDocumentSwitch": target_document_switch}, ensure_ascii=False, indent=2))
        return 1
    panel_bounds = _panel_bounds_from_cleanup_report(args.cleanup_report, args.only_style)
    if panel_bounds.get("status") == "fail":
        print(json.dumps({"status": "fail", "panelBounds": panel_bounds}, ensure_ascii=False, indent=2))
        return 1
    cleanup = _cleanup_previous_handles(driver, args.cleanup_report, only_style=args.only_style)
    if args.only_style and cleanup.get("status") == "fail":
        print(json.dumps({"status": "fail", "cleanup": cleanup}, ensure_ascii=False, indent=2))
        return 1
    report = run_dimension_style_training(
        driver=driver,
        output_dir=args.output_dir,
        desktop_switch={**desktop_switch, "targetDocumentSwitch": target_document_switch},
        cleanup=cleanup,
        only_style=args.only_style,
        panel_bounds_override=panel_bounds.get("bounds") if panel_bounds.get("status") == "pass" else None,
    )
    if args.summary_only:
        summary = {
            "status": report.get("status"),
            "outputDir": str(args.output_dir),
            "activeDocument": report.get("activeDocument"),
            "cleanup": {
                "status": report.get("cleanup", {}).get("status"),
                "deletedCount": report.get("cleanup", {}).get("deletedCount"),
            },
            "createdHandleCount": report.get("createdHandleCount"),
            "dimensionReadbackCount": report.get("dimensionReadbackCount"),
            "failedStyleCount": report.get("audit", {}).get("failedStyleCount"),
            "savedCurrentDwg": report.get("safety", {}).get("savedCurrentDwg"),
            "styleCount": report.get("styleCount"),
            "deletionScope": report.get("safety", {}).get("deletionScope"),
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
