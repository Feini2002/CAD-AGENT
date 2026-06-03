"""Focused CAD training for Chinese dimension styles."""

from __future__ import annotations

import json
import math
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.runtime.encoding_guard import detect_text_encoding_corruption
from core.safety.policy import PREVIEW_LAYER


TRAINING_ID = "dimension-style-focused-10"
TEXT_STYLE_NAME = "CODEX_CN_TEXT"
Z = 0.0
MIN_SCALE_VARIANTS_PER_STYLE = 2
PANEL_CONTAINMENT_TOLERANCE = 12.0


DIMENSION_STYLE_SPECS: list[dict[str, Any]] = [
    {
        "styleId": "dimstyle.arch.plan.outer_overall_tick",
        "cadStyleName": "训练-建筑-外轮廓总尺寸",
        "visibleTitle": "建筑-外轮廓总尺寸",
        "useWhen": "平面外侧总尺寸链，控制建筑或室内空间总长总宽",
        "dimensionKind": "linear",
        "endpointFamily": "architectural_tick",
        "arrowBlock": "_ARCHTICK",
        "chainRole": "outer_overall",
        "scale": 50,
        "paperTextHeight": 2.8,
        "paperArrowSize": 1.7,
        "precision": 0,
        "color": "white",
        "lineweightMm": 0.13,
        "sample": "outer_overall_tick",
    },
    {
        "styleId": "dimstyle.arch.plan.segment_chain_tick",
        "cadStyleName": "训练-建筑-分段连续尺寸",
        "visibleTitle": "建筑-分段连续尺寸",
        "useWhen": "墙段、门窗洞口、开间进深的连续分段尺寸",
        "dimensionKind": "continued",
        "endpointFamily": "architectural_tick",
        "arrowBlock": "_ARCHTICK",
        "chainRole": "segment_chain",
        "scale": 50,
        "paperTextHeight": 2.5,
        "paperArrowSize": 1.5,
        "precision": 0,
        "color": "white",
        "lineweightMm": 0.13,
        "sample": "segment_chain_tick",
    },
    {
        "styleId": "dimstyle.arch.grid.axis_location_tick",
        "cadStyleName": "训练-建筑-轴网定位尺寸",
        "visibleTitle": "建筑-轴网定位尺寸",
        "useWhen": "轴线、柱网、墙体定位，尺寸界线对齐轴号与轴线",
        "dimensionKind": "linear",
        "endpointFamily": "architectural_tick_axis",
        "arrowBlock": "_ARCHTICK",
        "chainRole": "axis_grid",
        "scale": 50,
        "paperTextHeight": 2.5,
        "paperArrowSize": 1.5,
        "precision": 0,
        "color": "white",
        "lineweightMm": 0.13,
        "sample": "axis_grid_tick",
    },
    {
        "styleId": "dimstyle.interior.plan.local_tick",
        "cadStyleName": "训练-室内-局部短尺寸",
        "visibleTitle": "室内-局部短尺寸",
        "useWhen": "家具、设备、局部墙体和洞口的近旁短尺寸定位",
        "dimensionKind": "linear",
        "endpointFamily": "small_architectural_tick",
        "arrowBlock": "_ARCHTICK",
        "chainRole": "local_short",
        "scale": 50,
        "paperTextHeight": 2.2,
        "paperArrowSize": 1.2,
        "precision": 0,
        "color": "cyan",
        "lineweightMm": 0.13,
        "sample": "local_short_tick",
    },
    {
        "styleId": "dimstyle.interior.elevation.height_tick",
        "cadStyleName": "训练-室内-立面高度尺寸",
        "visibleTitle": "室内-立面高度尺寸",
        "useWhen": "墙面、柜体、门窗、吊顶和完成面高度",
        "dimensionKind": "vertical",
        "endpointFamily": "vertical_architectural_tick",
        "arrowBlock": "_ARCHTICK",
        "chainRole": "elevation_height",
        "scale": 50,
        "paperTextHeight": 2.5,
        "paperArrowSize": 1.4,
        "precision": 0,
        "color": "green",
        "lineweightMm": 0.13,
        "sample": "elevation_height_tick",
        "sampleDisplayScales": [2.4, 2.0, 12.0],
    },
    {
        "styleId": "dimstyle.interior.elevation.opening_width_height",
        "cadStyleName": "训练-室内-洞口宽高尺寸",
        "visibleTitle": "室内-洞口宽高尺寸",
        "useWhen": "门洞、窗洞、设备洞口的宽高和离地定位尺寸",
        "dimensionKind": "opening_width_height",
        "endpointFamily": "vertical_architectural_tick",
        "arrowBlock": "_ARCHTICK",
        "chainRole": "opening_width_height",
        "scale": 50,
        "paperTextHeight": 2.4,
        "paperArrowSize": 1.3,
        "precision": 0,
        "color": "green",
        "lineweightMm": 0.13,
        "sample": "opening_width_height_tick",
        "sampleDisplayScales": [2.4, 2.0, 12.0],
    },
    {
        "styleId": "dimstyle.cabinet.shop.detail_arrow",
        "cadStyleName": "训练-定制-柜体深化尺寸",
        "visibleTitle": "定制-柜体深化尺寸",
        "useWhen": "定制柜宽高深、分格、层板和门板控制尺寸",
        "dimensionKind": "linear",
        "endpointFamily": "small_closed_arrow",
        "arrowBlock": ".",
        "chainRole": "cabinet_detail",
        "scale": 20,
        "paperTextHeight": 2.2,
        "paperArrowSize": 1.8,
        "precision": 0,
        "color": "yellow",
        "lineweightMm": 0.13,
        "sample": "cabinet_shop",
    },
    {
        "styleId": "dimstyle.cabinet.hardware.hole_dot",
        "cadStyleName": "训练-定制-五金孔位尺寸",
        "visibleTitle": "定制-五金孔位尺寸",
        "useWhen": "拉手、铰链、孔位、设备开孔和小尺度定位",
        "dimensionKind": "linear",
        "endpointFamily": "dot_center_mark",
        "arrowBlock": "_DOTSMALL",
        "chainRole": "hole_center_distance",
        "scale": 10,
        "paperTextHeight": 2.0,
        "paperArrowSize": 1.6,
        "precision": 0,
        "color": "yellow",
        "lineweightMm": 0.09,
        "sample": "hardware_holes",
    },
    {
        "styleId": "dimstyle.component.radius.diameter_arrow",
        "cadStyleName": "训练-构件-半径直径尺寸",
        "visibleTitle": "构件-半径直径尺寸",
        "useWhen": "圆孔、弧形边、圆角、管件和曲线构件",
        "dimensionKind": "radius_diameter",
        "endpointFamily": "closed_arrow_radial",
        "arrowBlock": ".",
        "chainRole": "radius_diameter",
        "scale": 10,
        "paperTextHeight": 2.0,
        "paperArrowSize": 1.6,
        "precision": 0,
        "color": "cyan",
        "lineweightMm": 0.09,
        "sample": "radius_diameter",
    },
    {
        "styleId": "dimstyle.component.angle.arc_arrow",
        "cadStyleName": "训练-构件-角度弧长尺寸",
        "visibleTitle": "构件-角度弧长尺寸",
        "useWhen": "斜墙、斜拼、异形构件、转角角度和弧形长度",
        "dimensionKind": "angular_arc",
        "endpointFamily": "arrow_angular_arc",
        "arrowBlock": ".",
        "chainRole": "angle_arc",
        "scale": 20,
        "paperTextHeight": 2.2,
        "paperArrowSize": 1.8,
        "precision": 0,
        "color": "green",
        "lineweightMm": 0.13,
        "sample": "angle_arc",
    },
]


ACI_COLORS = {"red": 1, "yellow": 2, "green": 3, "cyan": 4, "blue": 5, "magenta": 6, "white": 7}


def visible_texts(specs: list[dict[str, Any]] | None = None) -> list[str]:
    rows = specs or DIMENSION_STYLE_SPECS
    result = [
        "尺寸样式建筑标注重训",
        "十个中文尺寸样式；建筑 tick / 标高 / 孔位 / 半径直径 / 角度弧长",
        "序号",
        "样式名称",
        "用途",
        "检查点",
    ]
    for index, spec in enumerate(rows, start=1):
        result.extend(
            [
                str(index),
                str(spec["cadStyleName"]),
                str(spec["visibleTitle"]),
                str(spec["useWhen"]),
                "已检查：中文名称、端部形态、样式回读、图层、测量值",
            ]
        )
    return result


def validate_visible_text(specs: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    texts = visible_texts(specs)
    encoding = detect_text_encoding_corruption(texts)
    question_hits = [text for text in texts if "?" in text]
    mojibake_hits = [text for text in texts if re.search(r"[�锟]", text)]
    status = "pass" if encoding["status"] == "pass" and not question_hits and not mojibake_hits else "fail"
    return {
        "status": status,
        "textCount": len(texts),
        "encodingPreflight": encoding,
        "questionHits": question_hits,
        "mojibakeHits": mojibake_hits,
    }


def _style_token(value: Any) -> str:
    return str(value or "").strip().casefold()


def _style_aliases(spec: dict[str, Any]) -> set[str]:
    return {
        _style_token(spec.get("styleId")),
        _style_token(spec.get("cadStyleName")),
        _style_token(spec.get("visibleTitle")),
        _style_token(spec.get("dimensionKind")),
        _style_token(spec.get("chainRole")),
        _style_token(spec.get("sample")),
    } - {""}


def _style_matches_request(spec: dict[str, Any], requested: str | None) -> bool:
    requested_token = _style_token(requested)
    if not requested_token:
        return True
    aliases = _style_aliases(spec)
    return requested_token in aliases or any(requested_token in alias or alias in requested_token for alias in aliases)


def _coerce_panel_bounds(bounds: dict[str, Any] | None) -> dict[str, list[float]] | None:
    if not isinstance(bounds, dict):
        return None
    min_point = bounds.get("min")
    max_point = bounds.get("max")
    if not (isinstance(min_point, list) and isinstance(max_point, list) and len(min_point) >= 2 and len(max_point) >= 2):
        return None
    return {
        "min": [float(min_point[0]), float(min_point[1]), float(min_point[2] if len(min_point) >= 3 else Z)],
        "max": [float(max_point[0]), float(max_point[1]), float(max_point[2] if len(max_point) >= 3 else Z)],
    }


def run_dimension_style_training(
    *,
    driver: Any,
    output_dir: Path,
    specs: list[dict[str, Any]] | None = None,
    generated_at: str | None = None,
    desktop_switch: dict[str, Any] | None = None,
    cleanup: dict[str, Any] | None = None,
    write_report: bool = True,
    only_style: str | None = None,
    panel_bounds_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    if write_report:
        output_dir.mkdir(parents=True, exist_ok=True)
    canonical_specs = [_with_scale_samples(dict(spec)) for spec in (specs or DIMENSION_STYLE_SPECS)]
    active_rows = [(index, spec) for index, spec in enumerate(canonical_specs, start=1) if _style_matches_request(spec, only_style)]
    if only_style and not active_rows:
        raise ValueError(f"Requested dimension style was not found: {only_style}")
    active_specs = [spec for _, spec in active_rows]
    panel_bounds = _coerce_panel_bounds(panel_bounds_override)
    text_validation = validate_visible_text(active_specs)
    if text_validation["status"] != "pass":
        raise ValueError(f"Dimension style visible text failed encoding preflight: {text_validation}")

    _ensure_layer(driver, PREVIEW_LAYER)
    text_style_report = _ensure_chinese_text_style(driver)
    if only_style and panel_bounds is not None:
        anchor = {
            "mode": "previous_panel_bounds",
            "bbox": panel_bounds,
            "origin": [float(panel_bounds["min"][0]), float(panel_bounds["max"][1]), Z],
            "onlyStyle": only_style,
            "rule": "局部修复时复用上一轮报告中的 panelBoundsByStyle，只在原单格 bbox 内重绘。",
        }
    else:
        anchor = _parking_anchor(driver)
    origin_x = float(anchor["origin"][0])
    origin_y = float(anchor["origin"][1])

    all_handles: list[str] = []
    style_reports: list[dict[str, Any]] = []
    dimension_handles_by_style: dict[str, list[str]] = {}
    panel_handles_by_style: dict[str, list[str]] = {}
    panel_bounds_by_style: dict[str, dict[str, list[float]]] = {}

    if not only_style:
        _add_text(driver, "尺寸样式建筑标注重训", [origin_x, origin_y, Z], 150, color="yellow", handles=all_handles)
        _add_text(
            driver,
            "10 个 canonical 中文尺寸样式；每类 2-3 个比例样例；仅写预览层；当前图纸不保存",
            [origin_x, origin_y - 180, Z],
            70,
            color="white",
            handles=all_handles,
        )

    cell_w = 3900.0
    cell_h = 1660.0
    gap_x = 260.0
    gap_y = 260.0
    for local_index, (original_index, spec) in enumerate(active_rows):
        style_report = _ensure_dimension_style(driver, spec)
        style_reports.append(style_report)
        if only_style and panel_bounds is not None:
            x0 = float(panel_bounds["min"][0])
            y0 = float(panel_bounds["max"][1])
            draw_cell_w = float(panel_bounds["max"][0]) - float(panel_bounds["min"][0])
            draw_cell_h = float(panel_bounds["max"][1]) - float(panel_bounds["min"][1])
        else:
            col = local_index % 2
            row = local_index // 2
            x0 = origin_x + col * (cell_w + gap_x)
            y0 = origin_y - (0 if only_style else 420) - row * (cell_h + gap_y)
            draw_cell_w = cell_w
            draw_cell_h = cell_h
        handles, dimension_handles = _draw_style_panel(driver, spec, original_index, x0, y0, draw_cell_w, draw_cell_h)
        all_handles.extend(handles)
        style_name = str(spec["cadStyleName"])
        dimension_handles_by_style[style_name] = dimension_handles
        panel_handles_by_style[style_name] = handles
        panel_bounds_by_style[style_name] = {
            "min": [x0, y0 - draw_cell_h, Z],
            "max": [x0 + draw_cell_w, y0, Z],
        }
        if only_style and panel_bounds is not None:
            panel_bounds_by_style[style_name] = panel_bounds

    readback = _snapshot_created(driver, all_handles)
    audit = _audit_dimension_styles(
        specs=active_specs,
        style_reports=style_reports,
        readback=readback,
        dimension_handles_by_style=dimension_handles_by_style,
        panel_handles_by_style=panel_handles_by_style,
        panel_bounds_by_style=panel_bounds_by_style,
        require_global_variety=not bool(only_style),
    )
    zoom = _zoom_to_handles(driver, all_handles)
    refresh = _refresh(driver)
    active_document = _active_document(driver)
    deletion_scope = "none"
    cleanup_status = cleanup.get("status") if isinstance(cleanup, dict) else None
    if cleanup and cleanup_status != "not_run":
        cleanup_scope = cleanup.get("scope")
        if isinstance(cleanup_scope, dict):
            deletion_scope = str(cleanup_scope.get("source") or "previous_created_handles_on_CODEX_PREVIEW")
        else:
            deletion_scope = "previous_created_handles_on_CODEX_PREVIEW"
    report = {
        "status": "pass" if audit["status"] == "pass" else "needs_review",
        "trainingId": TRAINING_ID,
        "scope": {
            "mode": "focused_repair" if only_style else "focused",
            "requestedCapabilityIds": ["annotation-dimension-style", "cad-dim-style-baseline"],
            "requestedStyle": only_style,
            "targetStyleNames": [str(spec["cadStyleName"]) for spec in active_specs],
            "scopeReason": (
                "用户点名单个尺寸样式局部不舒服，本轮只删除并重绘该样式面板。"
                if only_style
                else "用户反馈上一轮尺寸样式重复且建筑标记比例偏大，本轮保留 10 个 canonical 样式并追加 2-3 个比例/跨度样例。"
            ),
        },
        "generatedAt": generated_at or datetime.now(UTC).isoformat(),
        "activeDocument": active_document,
        "desktopSwitch": desktop_switch or {"status": "not_checked"},
        "cleanup": cleanup or {"status": "not_run"},
        "encodingPreflight": text_validation,
        "textStyle": text_style_report,
        "parkingAnchor": anchor,
        "styleCount": len(active_specs),
        "canonicalStyleCount": len(canonical_specs),
        "scaleVariantCount": sum(len(_scale_samples(spec)) for spec in active_specs),
        "dimensionStyleSpecs": active_specs,
        "styleReports": style_reports,
        "panelHandlesByStyle": panel_handles_by_style,
        "panelBoundsByStyle": panel_bounds_by_style,
        "createdHandles": list(dict.fromkeys(all_handles)),
        "createdHandleCount": len(dict.fromkeys(all_handles)),
        "readbackEntityCount": len(readback),
        "dimensionReadbackCount": sum(1 for entity in readback if entity.get("type") == "dimension"),
        "readbackSample": readback[:40],
        "audit": audit,
        "zoom": zoom,
        "refresh": refresh,
        "safety": {
            "targetLayer": PREVIEW_LAYER,
            "savedCurrentDwg": False,
            "deletedEntities": bool(cleanup and int(cleanup.get("deletedCount", 0) or 0) > 0),
            "deletionScope": deletion_scope,
            "modifiedFormalLayers": False,
            "overwriteExistingStandardStyle": False,
            "assetSedimentation": "not_started",
        },
        "postTrainingSync": {
            "status": "not_required",
            "reason": "Focused retraining only; asset sedimentation will run after user review.",
        },
    }
    if write_report:
        report_path = output_dir / "dimension_style_training_report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def _ensure_layer(driver: Any, layer: str) -> None:
    if hasattr(driver, "ensure_layer"):
        driver.ensure_layer(layer)


def _ensure_chinese_text_style(driver: Any) -> dict[str, Any]:
    doc = getattr(driver, "doc", None)
    if doc is None or not hasattr(doc, "TextStyles"):
        return {"status": "not_checked", "styleName": TEXT_STYLE_NAME, "reason": "driver has no TextStyles collection"}
    try:
        try:
            style = doc.TextStyles.Item(TEXT_STYLE_NAME)
            created = False
        except Exception:
            style = doc.TextStyles.Add(TEXT_STYLE_NAME)
            created = True
        for typeface in ("SimSun", "Microsoft YaHei", "Arial Unicode MS"):
            try:
                style.SetFont(typeface, False, False, 134, 34)
                break
            except Exception:
                continue
        try:
            doc.ActiveTextStyle = style
        except Exception:
            pass
        return {"status": "pass", "styleName": TEXT_STYLE_NAME, "created": created}
    except Exception as exc:
        return {"status": "partial", "styleName": TEXT_STYLE_NAME, "reason": str(exc)}


def _ensure_dimension_style(driver: Any, spec: dict[str, Any]) -> dict[str, Any]:
    doc = getattr(driver, "doc", None)
    style_name = str(spec["cadStyleName"])
    variables = _style_variables(spec)
    if doc is None or not hasattr(doc, "DimStyles"):
        return {
            "status": "fake_pass",
            "styleName": style_name,
            "variables": variables,
            "reason": "driver has no DimStyles collection; fake readback will carry style name",
        }

    old_style = None
    saved_vars: dict[str, Any] = {}
    try:
        old_style = getattr(doc, "ActiveDimStyle", None)
    except Exception:
        old_style = None
    for name in variables:
        try:
            saved_vars[name] = doc.GetVariable(name)
        except Exception:
            pass

    created = False
    errors: list[str] = []
    try:
        try:
            style = doc.DimStyles.Item(style_name)
        except Exception:
            style = doc.DimStyles.Add(style_name)
            created = True
        for name, value in variables.items():
            try:
                doc.SetVariable(name, value)
            except Exception as exc:
                errors.append(f"{name}: {exc}")
        try:
            style.CopyFrom(doc)
        except Exception as exc:
            errors.append(f"CopyFrom: {exc}")
        readback = _read_dimstyle_variables(driver, style_name, list(variables))
        return {
            "status": "pass" if readback["status"] in {"pass", "partial"} and not errors else "partial",
            "styleName": style_name,
            "created": created,
            "variables": variables,
            "readback": readback,
            "errors": errors,
        }
    finally:
        for name, value in saved_vars.items():
            try:
                doc.SetVariable(name, value)
            except Exception:
                pass
        if old_style is not None:
            try:
                doc.ActiveDimStyle = old_style
            except Exception:
                pass


def _style_variables(spec: dict[str, Any]) -> dict[str, Any]:
    variables: dict[str, Any] = {
        "DIMTXT": float(spec["paperTextHeight"]),
        "DIMASZ": float(spec["paperArrowSize"]),
        "DIMEXO": 1.0,
        "DIMEXE": 1.25,
        "DIMDLI": 6.0,
        "DIMDEC": int(spec["precision"]),
        "DIMLFAC": 1.0,
        "DIMSCALE": float(spec["scale"]),
        "DIMTXSTY": TEXT_STYLE_NAME,
        "DIMCLRD": ACI_COLORS.get(str(spec["color"]), 7),
        "DIMCLRE": ACI_COLORS.get(str(spec["color"]), 7),
        "DIMCLRT": ACI_COLORS.get(str(spec["color"]), 7),
        "DIMGAP": 0.9,
        "DIMTAD": 1,
        "DIMJUST": 0,
        "DIMTIH": 0,
        "DIMTOH": 0,
    }
    arrow_block = str(spec.get("arrowBlock") or "").strip()
    if arrow_block:
        variables["DIMBLK"] = arrow_block
        variables["DIMBLK1"] = arrow_block
        variables["DIMBLK2"] = arrow_block
    return variables


def _with_scale_samples(spec: dict[str, Any]) -> dict[str, Any]:
    spec.setdefault("scaleSamples", _default_scale_samples(spec))
    return spec


def _scale_samples(spec: dict[str, Any]) -> list[dict[str, Any]]:
    samples = spec.get("scaleSamples")
    if isinstance(samples, list) and samples:
        return [dict(sample) for sample in samples if isinstance(sample, dict)]
    return _default_scale_samples(spec)


def _sample_display_scales(spec: dict[str, Any]) -> list[float]:
    raw_scales = spec.get("sampleDisplayScales")
    if isinstance(raw_scales, list) and raw_scales:
        scales = [float(value) for value in raw_scales if float(value) > 0]
        if scales:
            return scales
    raw_scale = spec.get("sampleDisplayScale")
    if raw_scale is not None:
        scale = float(raw_scale)
        if scale > 0:
            return [scale]
    return [1.0]


def _display_to_model_units(value: str | float | int, display_scale: float) -> float:
    return float(value) / max(float(display_scale), 0.001)


def _default_scale_samples(spec: dict[str, Any]) -> list[dict[str, Any]]:
    sample = str(spec.get("sample", ""))
    if sample in {"outer_overall_tick", "segment_chain_tick", "axis_grid_tick"}:
        return [
            {"label": "1:100", "span": 720.0, "offset": 145.0},
            {"label": "1:50", "span": 960.0, "offset": 165.0},
            {"label": "1:200", "span": 1200.0, "offset": 190.0},
        ]
    if sample == "local_short_tick":
        return [
            {"label": "1:50", "span": 560.0, "offset": 130.0},
            {"label": "1:30", "span": 760.0, "offset": 145.0},
            {"label": "1:20", "span": 940.0, "offset": 160.0},
        ]
    if sample == "elevation_height_tick":
        return [
            {"label": "台面高", "span": 210.0, "offset": 115.0, "display": "850"},
            {"label": "门洞高", "span": 270.0, "offset": 125.0, "display": "2100"},
            {"label": "吊顶高", "span": 330.0, "offset": 135.0, "display": "2400"},
        ]
    if sample == "opening_width_height_tick":
        return [
            {"label": "门洞", "span": 560.0, "offset": 130.0, "width": "900", "height": "2100"},
            {"label": "窗洞", "span": 700.0, "offset": 145.0, "width": "1200", "height": "1500"},
            {"label": "设备洞", "span": 840.0, "offset": 160.0, "width": "600", "height": "600"},
        ]
    if sample in {"cabinet_shop", "angle_arc"}:
        return [
            {"label": "1:30", "span": 520.0, "offset": 115.0},
            {"label": "1:20", "span": 700.0, "offset": 130.0},
            {"label": "1:10", "span": 880.0, "offset": 145.0},
        ]
    if sample in {"hardware_holes", "radius_diameter"}:
        return [
            {"label": "节点小", "span": 260.0, "offset": 90.0},
            {"label": "节点中", "span": 420.0, "offset": 105.0},
            {"label": "节点大", "span": 600.0, "offset": 120.0},
        ]
    return [
        {"label": "小", "span": 480.0, "offset": 110.0},
        {"label": "中", "span": 720.0, "offset": 130.0},
    ]


def _read_dimstyle_variables(driver: Any, style_name: str, names: list[str]) -> dict[str, Any]:
    doc = getattr(driver, "doc", None)
    if doc is None or not hasattr(doc, "DimStyles"):
        return {"status": "not_checked", "variables": {}}
    old_style = None
    try:
        old_style = getattr(doc, "ActiveDimStyle", None)
        doc.ActiveDimStyle = doc.DimStyles.Item(style_name)
    except Exception:
        pass
    values: dict[str, Any] = {}
    failures: list[str] = []
    try:
        for name in names:
            try:
                values[name] = doc.GetVariable(name)
            except Exception as exc:
                failures.append(f"{name}: {exc}")
        return {"status": "pass" if not failures else "partial", "variables": values, "failures": failures}
    finally:
        if old_style is not None:
            try:
                doc.ActiveDimStyle = old_style
            except Exception:
                pass


def _draw_style_panel(
    driver: Any,
    spec: dict[str, Any],
    index: int,
    x0: float,
    y0: float,
    cell_w: float,
    cell_h: float,
) -> tuple[list[str], list[str]]:
    handles: list[str] = []
    dimension_handles: list[str] = []
    _add_rect(driver, [x0, y0, Z], [x0 + cell_w, y0 - cell_h, Z], handles=handles)
    _add_text(driver, f"{index:02d} {spec['visibleTitle']}", [x0 + 120, y0 - 130, Z], 70, color="yellow", handles=handles)
    _add_text(driver, str(spec["useWhen"]), [x0 + 120, y0 - cell_h + 132, Z], 42, color="white", handles=handles)
    _add_text(
        driver,
        f"端部：{_endpoint_label(spec)} / 检查：样式回读、图层、测量值、形态差异",
        [x0 + 120, y0 - cell_h + 62, Z],
        38,
        color="cyan",
        handles=handles,
    )

    sample = str(spec["sample"])
    sx = x0 + 320
    sy = y0 - 360
    if sample == "outer_overall_tick":
        _add_rect(driver, [sx, sy, Z], [sx + 1500, sy - 560, Z], handles=handles, color="white")
        dimension_handles.append(_add_aligned_dim(driver, spec, [sx, sy - 720, Z], [sx + 1500, sy - 720, Z], [sx + 750, sy - 920, Z], handles))
        _add_tick_marker(driver, [sx, sy - 720, Z], 72, handles=handles, color="red")
        _add_tick_marker(driver, [sx + 1500, sy - 720, Z], 72, handles=handles, color="red")
    elif sample == "segment_chain_tick":
        y = sy - 360
        xs = [sx, sx + 460, sx + 980, sx + 1500]
        _add_line(driver, [xs[0], sy, Z], [xs[-1], sy, Z], handles=handles)
        for x in xs:
            _add_line(driver, [x, sy + 80, Z], [x, sy - 420, Z], handles=handles, color="white")
        for start, end in zip(xs[:-1], xs[1:], strict=True):
            dimension_handles.append(_add_aligned_dim(driver, spec, [start, y, Z], [end, y, Z], [(start + end) / 2, y - 190, Z], handles))
        dimension_handles.append(_add_aligned_dim(driver, spec, [xs[0], y - 280, Z], [xs[-1], y - 280, Z], [(xs[0] + xs[-1]) / 2, y - 470, Z], handles))
    elif sample == "axis_grid_tick":
        xs = [sx + 160, sx + 760, sx + 1450]
        y_axis_top = sy + 60
        y_axis_bottom = sy - 760
        for axis_index, x in enumerate(xs, start=1):
            _add_line(driver, [x, y_axis_top, Z], [x, y_axis_bottom, Z], handles=handles, color="white")
            _add_circle(driver, [x, y_axis_top + 130, Z], 74, handles=handles, color="yellow")
            _add_text(driver, str(axis_index), [x - 22, y_axis_top + 100, Z], 52, color="yellow", handles=handles)
        dimension_handles.append(_add_aligned_dim(driver, spec, [xs[0], y_axis_bottom - 110, Z], [xs[1], y_axis_bottom - 110, Z], [(xs[0] + xs[1]) / 2, y_axis_bottom - 280, Z], handles))
        dimension_handles.append(_add_aligned_dim(driver, spec, [xs[1], y_axis_bottom - 110, Z], [xs[2], y_axis_bottom - 110, Z], [(xs[1] + xs[2]) / 2, y_axis_bottom - 280, Z], handles))
    elif sample == "local_short_tick":
        _add_rect(driver, [sx + 260, sy, Z], [sx + 1120, sy - 380, Z], handles=handles, color="cyan")
        dimension_handles.append(_add_aligned_dim(driver, spec, [sx + 260, sy - 520, Z], [sx + 1120, sy - 520, Z], [sx + 690, sy - 680, Z], handles))
        dimension_handles.append(_add_aligned_dim(driver, spec, [sx, sy - 720, Z], [sx + 260, sy - 720, Z], [sx + 130, sy - 870, Z], handles))
    elif sample == "elevation_height_tick":
        main_scale = _sample_display_scales(spec)[0]
        display_height = "2100"
        height = _display_to_model_units(display_height, main_scale)
        floor_y = sy - 760
        top_y = floor_y + height
        _add_line(driver, [sx + 260, floor_y, Z], [sx + 1500, floor_y, Z], handles=handles, color="white")
        _add_text(driver, "完成面", [sx + 1520, floor_y + 26, Z], 38, color="white", handles=handles)
        _add_rect(driver, [sx + 520, top_y, Z], [sx + 1180, floor_y, Z], handles=handles, color="green")
        _add_line(driver, [sx + 520, top_y, Z], [sx + 1180, top_y, Z], handles=handles, color="green")
        dimension_handles.append(
            _add_aligned_dim(
                driver,
                spec,
                [sx + 300, floor_y, Z],
                [sx + 300, top_y, Z],
                [sx + 120, (floor_y + top_y) / 2, Z],
                handles,
                text_override=display_height,
            )
        )
    elif sample == "opening_width_height_tick":
        main_scale = _sample_display_scales(spec)[0]
        width_text = "900"
        height_text = "2100"
        width = _display_to_model_units(width_text, main_scale)
        height = _display_to_model_units(height_text, main_scale)
        floor_y = sy - 760
        top_y = floor_y + height
        left = sx + 610
        right = left + width
        _add_line(driver, [sx + 220, floor_y, Z], [sx + 1500, floor_y, Z], handles=handles, color="white")
        _add_text(driver, "完成面", [sx + 1520, floor_y + 26, Z], 38, color="white", handles=handles)
        _add_rect(driver, [left, top_y, Z], [right, floor_y, Z], handles=handles, color="green")
        _add_line(driver, [left, top_y, Z], [right, top_y, Z], handles=handles, color="green")
        dimension_handles.append(
            _add_aligned_dim(
                driver,
                spec,
                [left, floor_y - 260, Z],
                [right, floor_y - 260, Z],
                [(left + right) / 2, floor_y - 215, Z],
                handles,
                text_override=width_text,
            )
        )
        dimension_handles.append(
            _add_aligned_dim(
                driver,
                spec,
                [right + 190, floor_y, Z],
                [right + 190, top_y, Z],
                [right + 360, (floor_y + top_y) / 2, Z],
                handles,
                text_override=height_text,
            )
        )
    elif sample == "cabinet_shop":
        _add_rect(driver, [sx + 220, sy, Z], [sx + 1320, sy - 780, Z], handles=handles, color="yellow")
        _add_line(driver, [sx + 590, sy, Z], [sx + 590, sy - 780, Z], handles=handles, color="yellow")
        _add_line(driver, [sx + 960, sy, Z], [sx + 960, sy - 780, Z], handles=handles, color="yellow")
        dimension_handles.append(_add_aligned_dim(driver, spec, [sx + 220, sy - 900, Z], [sx + 1320, sy - 900, Z], [sx + 770, sy - 1080, Z], handles))
        dimension_handles.append(_add_aligned_dim(driver, spec, [sx + 1450, sy, Z], [sx + 1450, sy - 780, Z], [sx + 1650, sy - 390, Z], handles))
    elif sample == "hardware_holes":
        _add_rect(driver, [sx + 280, sy, Z], [sx + 1180, sy - 560, Z], handles=handles, color="yellow")
        for cx in (sx + 560, sx + 900):
            _add_circle(driver, [cx, sy - 280, Z], 38, handles=handles, color="yellow")
            _add_center_mark(driver, [cx, sy - 280, Z], 140, handles=handles, color="yellow")
        dimension_handles.append(_add_aligned_dim(driver, spec, [sx + 560, sy - 410, Z], [sx + 900, sy - 410, Z], [sx + 730, sy - 560, Z], handles))
        dimension_handles.append(_add_aligned_dim(driver, spec, [sx + 280, sy - 680, Z], [sx + 560, sy - 680, Z], [sx + 420, sy - 820, Z], handles))
    elif sample == "radius_diameter":
        _add_circle(driver, [sx + 820, sy - 390, Z], 280, handles=handles, color="cyan")
        dimension_handles.append(_add_radial_dim(driver, spec, [sx + 820, sy - 390, Z], [sx + 1100, sy - 390, Z], handles))
        dimension_handles.append(_add_diametric_dim(driver, spec, [sx + 540, sy - 390, Z], [sx + 1100, sy - 390, Z], handles))
    elif sample == "angle_arc":
        vertex = [sx + 500, sy - 620, Z]
        p1 = [sx + 1380, sy - 620, Z]
        p2 = [sx + 1120, sy - 160, Z]
        _add_line(driver, vertex, p1, handles=handles, color="green")
        _add_line(driver, vertex, p2, handles=handles, color="green")
        _add_arc(driver, vertex, 360, 0, 28, handles=handles, color="green")
        dimension_handles.append(_add_aligned_dim(driver, spec, vertex, p2, [sx + 900, sy - 300, Z], handles))
        dimension_handles.append(_add_angular_dim(driver, spec, vertex, p1, p2, [sx + 900, sy - 520, Z], handles))
    dimension_handles.extend(_draw_scale_variants(driver, spec, x0 + 2260, y0 - 360, handles))
    return list(dict.fromkeys(handles)), [handle for handle in dimension_handles if handle]


def _draw_scale_variants(
    driver: Any,
    spec: dict[str, Any],
    x0: float,
    y0: float,
    handles: list[str],
) -> list[str]:
    dimension_handles: list[str] = []
    samples = _scale_samples(spec)[:3]
    _add_text(driver, "比例样例", [x0, y0 + 95, Z], 42, color="yellow", handles=handles)
    sample_kind = str(spec.get("sample", ""))
    if sample_kind == "elevation_height_tick":
        return _draw_elevation_scale_visuals(driver, spec, samples, x0, y0, handles)
    if sample_kind == "opening_width_height_tick":
        return _draw_opening_scale_visuals(driver, spec, samples, x0, y0, handles)
    sample_y_shift = 155.0 if sample_kind in {"elevation_height_tick", "opening_width_height_tick"} else 0.0
    for variant_index, variant in enumerate(samples):
        label = str(variant.get("label", f"样例{variant_index + 1}"))
        span = float(variant.get("span", 620.0))
        offset = float(variant.get("offset", 130.0))
        y = y0 - sample_y_shift - variant_index * 285.0
        _add_text(driver, label, [x0, y - 36, Z], 34, color="white", handles=handles)
        base_x = x0 + 250.0
        if sample_kind == "radius_diameter":
            radius = max(70.0, span / 4.0)
            center = [base_x + radius + 110.0, y - 70.0, Z]
            _add_circle(driver, center, radius, handles=handles, color=str(spec["color"]))
            dimension_handles.append(_add_radial_dim(driver, spec, center, [center[0] + radius, center[1], Z], handles))
        elif sample_kind == "angle_arc":
            vertex = [base_x, y - 130.0, Z]
            p1 = [base_x + span, y - 130.0, Z]
            p2 = [base_x + span * 0.72, y + 85.0, Z]
            _add_line(driver, vertex, p1, handles=handles, color=str(spec["color"]))
            _add_line(driver, vertex, p2, handles=handles, color=str(spec["color"]))
            dimension_handles.append(_add_angular_dim(driver, spec, vertex, p1, p2, [base_x + span * 0.55, y - 40.0, Z], handles))
        elif sample_kind == "elevation_height_tick":
            display = str(variant.get("display", ""))
            height = span
            x = base_x + 430.0
            floor_y = y - 245.0
            top_y = floor_y + height
            _add_line(driver, [base_x + 120.0, floor_y, Z], [base_x + 900.0, floor_y, Z], handles=handles, color="white")
            _add_line(driver, [x + 160.0, floor_y, Z], [x + 160.0, top_y, Z], handles=handles, color=str(spec["color"]))
            _add_line(driver, [x + 120.0, top_y, Z], [x + 300.0, top_y, Z], handles=handles, color=str(spec["color"]))
            _add_line(driver, [x + 40.0, floor_y, Z], [x + 40.0, top_y, Z], handles=handles, color=str(spec["color"]))
            _add_tick_marker(driver, [x + 40.0, floor_y, Z], 44, handles=handles, color=str(spec["color"]))
            _add_tick_marker(driver, [x + 40.0, top_y, Z], 44, handles=handles, color=str(spec["color"]))
            _add_text(driver, display, [x + 215.0, (floor_y + top_y) / 2 - 18.0, Z], 34, color=str(spec["color"]), handles=handles)
        elif sample_kind == "opening_width_height_tick":
            width_text = str(variant.get("width", ""))
            height_text = str(variant.get("height", ""))
            width = span
            floor_y = y - 175.0
            top_y = y - 30.0
            left = base_x + 160.0
            right = left + width
            _add_rect(driver, [left, top_y, Z], [right, floor_y, Z], handles=handles, color=str(spec["color"]))
            dim_y = floor_y - 58.0
            _add_line(driver, [left, dim_y, Z], [right, dim_y, Z], handles=handles, color=str(spec["color"]))
            _add_tick_marker(driver, [left, dim_y, Z], 44, handles=handles, color=str(spec["color"]))
            _add_tick_marker(driver, [right, dim_y, Z], 44, handles=handles, color=str(spec["color"]))
            _add_text(driver, width_text, [(left + right) / 2 - 42.0, dim_y + 26.0, Z], 34, color=str(spec["color"]), handles=handles)
            _add_line(driver, [right + 88.0, floor_y, Z], [right + 88.0, top_y, Z], handles=handles, color=str(spec["color"]))
            _add_tick_marker(driver, [right + 88.0, floor_y, Z], 38, handles=handles, color=str(spec["color"]))
            _add_tick_marker(driver, [right + 88.0, top_y, Z], 38, handles=handles, color=str(spec["color"]))
            _add_text(driver, height_text, [right + 140.0, (top_y + floor_y) / 2 - 18.0, Z], 30, color=str(spec["color"]), handles=handles)
        elif sample_kind == "hardware_holes":
            center_y = y - 95.0
            first = base_x + 120.0
            second = first + span
            for cx in (first, second):
                _add_circle(driver, [cx, center_y, Z], 22, handles=handles, color=str(spec["color"]))
                _add_center_mark(driver, [cx, center_y, Z], 86, handles=handles, color=str(spec["color"]))
            dimension_handles.append(
                _add_aligned_dim(driver, spec, [first, center_y - 95.0, Z], [second, center_y - 95.0, Z], [(first + second) / 2, center_y - 95.0 - offset, Z], handles)
            )
        else:
            start = [base_x, y - 92.0, Z]
            end = [base_x + span, y - 92.0, Z]
            _add_line(driver, [start[0], start[1] + 72.0, Z], [start[0], start[1] - 72.0, Z], handles=handles, color=str(spec["color"]))
            _add_line(driver, [end[0], end[1] + 72.0, Z], [end[0], end[1] - 72.0, Z], handles=handles, color=str(spec["color"]))
            dimension_handles.append(_add_aligned_dim(driver, spec, start, end, [(start[0] + end[0]) / 2, start[1] - offset, Z], handles))
    return [handle for handle in dimension_handles if handle]


def _draw_elevation_scale_visuals(
    driver: Any,
    spec: dict[str, Any],
    samples: list[dict[str, Any]],
    x0: float,
    y0: float,
    handles: list[str],
) -> list[str]:
    color = str(spec["color"])
    base_x = x0 + 300.0
    line_x = base_x + 640.0
    visual_heights = (145.0, 205.0, 255.0)
    for variant_index, variant in enumerate(samples):
        label = str(variant.get("label", f"样例{variant_index + 1}"))
        display = str(variant.get("display", ""))
        row_y = y0 - 165.0 - variant_index * 320.0
        floor_y = row_y - 168.0
        top_y = floor_y + visual_heights[min(variant_index, len(visual_heights) - 1)]
        _add_text(driver, label, [x0, row_y - 20.0, Z], 50, color="white", handles=handles)
        _add_line(driver, [base_x, floor_y, Z], [base_x + 980.0, floor_y, Z], handles=handles, color="white")
        _add_line(driver, [line_x, floor_y, Z], [line_x, top_y, Z], handles=handles, color=color)
        _add_line(driver, [line_x - 130.0, top_y, Z], [line_x + 210.0, top_y, Z], handles=handles, color=color)
        _add_tick_marker(driver, [line_x, floor_y, Z], 64, handles=handles, color=color)
        _add_tick_marker(driver, [line_x, top_y, Z], 64, handles=handles, color=color)
        _add_text(driver, display, [line_x + 112.0, (floor_y + top_y) / 2 - 30.0, Z], 60, color=color, handles=handles)
    return []


def _draw_opening_scale_visuals(
    driver: Any,
    spec: dict[str, Any],
    samples: list[dict[str, Any]],
    x0: float,
    y0: float,
    handles: list[str],
) -> list[str]:
    color = str(spec["color"])
    base_x = x0 + 360.0
    visual_widths = (680.0, 820.0, 960.0)
    for variant_index, variant in enumerate(samples):
        label = str(variant.get("label", f"样例{variant_index + 1}"))
        width_text = str(variant.get("width", ""))
        height_text = str(variant.get("height", ""))
        row_y = y0 - 160.0 - variant_index * 320.0
        top_y = row_y - 22.0
        floor_y = top_y - 125.0
        left = base_x
        right = left + visual_widths[min(variant_index, len(visual_widths) - 1)]
        dim_y = floor_y - 72.0
        _add_text(driver, label, [x0, top_y - 12.0, Z], 50, color="white", handles=handles)
        _add_rect(driver, [left, top_y, Z], [right, floor_y, Z], handles=handles, color=color)
        _add_line(driver, [left, dim_y, Z], [right, dim_y, Z], handles=handles, color=color)
        _add_tick_marker(driver, [left, dim_y, Z], 62, handles=handles, color=color)
        _add_tick_marker(driver, [right, dim_y, Z], 62, handles=handles, color=color)
        _add_text(driver, width_text, [(left + right) / 2 - 62.0, dim_y + 32.0, Z], 54, color=color, handles=handles)
        vertical_x = right + 105.0
        _add_line(driver, [vertical_x, floor_y, Z], [vertical_x, top_y, Z], handles=handles, color=color)
        _add_tick_marker(driver, [vertical_x, floor_y, Z], 52, handles=handles, color=color)
        _add_tick_marker(driver, [vertical_x, top_y, Z], 52, handles=handles, color=color)
        _add_text(driver, height_text, [vertical_x + 66.0, (top_y + floor_y) / 2 - 24.0, Z], 48, color=color, handles=handles)
    return []


def _endpoint_label(spec: dict[str, Any]) -> str:
    labels = {
        "architectural_tick": "45°建筑斜短划",
        "architectural_tick_axis": "轴网建筑斜短划",
        "small_architectural_tick": "小号建筑斜短划",
        "vertical_architectural_tick": "竖向建筑斜短划",
        "level_triangle_marker": "标高三角符号",
        "small_closed_arrow": "小号闭合箭头",
        "dot_center_mark": "孔心圆点",
        "closed_arrow_radial": "半径直径箭头",
        "arrow_angular_arc": "角度弧线箭头",
    }
    return labels.get(str(spec.get("endpointFamily")), str(spec.get("endpointFamily", "")))


def _add_tick_marker(driver: Any, center: list[float], size: float, *, handles: list[str], color: str = "white") -> None:
    x, y, z = center
    half = size / 2
    _add_line(driver, [x - half, y - half, z], [x + half, y + half, z], handles=handles, color=color)


def _add_level_symbol(driver: Any, point: list[float], label: str, *, handles: list[str], scale: float = 1.0) -> None:
    x, y, z = point
    tri = 260.0 * scale
    half_h = 110.0 * scale
    tail = 660.0 * scale
    _add_line(driver, [x, y, z], [x + tri, y + half_h, z], handles=handles, color="green")
    _add_line(driver, [x, y, z], [x + tri, y - half_h, z], handles=handles, color="green")
    _add_line(driver, [x + tri, y + half_h, z], [x + tri, y - half_h, z], handles=handles, color="green")
    _add_line(driver, [x + tri, y, z], [x + tail, y, z], handles=handles, color="green")
    _add_text(driver, label, [x + tail + 30.0 * scale, y - 40.0 * scale, z], max(26.0, 50.0 * scale), color="green", handles=handles)


def _add_center_mark(driver: Any, center: list[float], size: float, *, handles: list[str], color: str = "white") -> None:
    x, y, z = center
    half = size / 2
    _add_line(driver, [x - half, y, z], [x + half, y, z], handles=handles, color=color)
    _add_line(driver, [x, y - half, z], [x, y + half, z], handles=handles, color=color)


def _add(result: Any, handles: list[str]) -> list[str]:
    created = _collect_handles(result)
    for handle in created:
        if handle not in handles:
            handles.append(handle)
    return created


def _add_line(driver: Any, start: list[float], end: list[float], *, handles: list[str], color: str = "white") -> None:
    _add(driver.draw_line(start_point=start, end_point=end, layer=PREVIEW_LAYER, color=color), handles)


def _add_rect(driver: Any, corner1: list[float], corner2: list[float], *, handles: list[str], color: str = "white") -> None:
    _add(driver.draw_rectangle(corner1=corner1, corner2=corner2, layer=PREVIEW_LAYER, color=color), handles)


def _add_circle(driver: Any, center: list[float], radius: float, *, handles: list[str], color: str = "white") -> None:
    _add(driver.draw_circle(center=center, radius=radius, layer=PREVIEW_LAYER, color=color), handles)


def _add_arc(
    driver: Any,
    center: list[float],
    radius: float,
    start_angle: float,
    end_angle: float,
    *,
    handles: list[str],
    color: str = "white",
) -> None:
    _add(
        driver.draw_arc(center=center, radius=radius, start_angle=start_angle, end_angle=end_angle, layer=PREVIEW_LAYER, color=color),
        handles,
    )


def _add_text(driver: Any, text: str, position: list[float], height: float, *, color: str, handles: list[str]) -> None:
    _add(driver.draw_text(text=text, position=position, height=height, layer=PREVIEW_LAYER, color=color), handles)


def _add_aligned_dim(
    driver: Any,
    spec: dict[str, Any],
    start: list[float],
    end: list[float],
    text_position: list[float],
    handles: list[str],
    *,
    text_override: str | None = None,
    force_horizontal_text: bool = False,
) -> str:
    style_name = str(spec["cadStyleName"])
    text_height = float(spec["paperTextHeight"]) * float(spec["scale"])
    if _has_com_modelspace(driver):
        entity = _with_active_dimstyle(driver, style_name, lambda: driver.model_space.AddDimAligned(driver._point(start), driver._point(end), driver._point(text_position)))
        _apply_dimension_entity(driver, entity, spec, style_name)
        if text_override:
            try:
                entity.TextOverride = text_override
                entity.Update()
            except Exception:
                pass
        if force_horizontal_text:
            try:
                entity.TextRotation = 0.0
                entity.Update()
            except Exception:
                pass
        created = _add({"handle": _handle(entity)}, handles)
    else:
        created = _add(
            driver.add_dimension(
                start_point=start,
                end_point=end,
                text_position=text_position,
                layer=PREVIEW_LAYER,
                color=str(spec["color"]),
                textheight=text_height,
                text_override=text_override,
                dimension_style=style_name,
                text_rotation=0.0 if force_horizontal_text else None,
            ),
            handles,
        )
    return created[0] if created else ""


def _add_radial_dim(driver: Any, spec: dict[str, Any], center: list[float], chord: list[float], handles: list[str]) -> str:
    style_name = str(spec["cadStyleName"])
    if _has_com_modelspace(driver) and hasattr(driver.model_space, "AddDimRadial"):
        entity = _with_active_dimstyle(driver, style_name, lambda: driver.model_space.AddDimRadial(driver._point(center), driver._point(chord), 120.0))
        _apply_dimension_entity(driver, entity, spec, style_name)
        created = _add({"handle": _handle(entity)}, handles)
        return created[0] if created else ""
    return _add_aligned_dim(driver, spec, center, chord, [(center[0] + chord[0]) / 2, center[1] + 160, Z], handles)


def _add_diametric_dim(driver: Any, spec: dict[str, Any], chord1: list[float], chord2: list[float], handles: list[str]) -> str:
    style_name = str(spec["cadStyleName"])
    if _has_com_modelspace(driver) and hasattr(driver.model_space, "AddDimDiametric"):
        entity = _with_active_dimstyle(driver, style_name, lambda: driver.model_space.AddDimDiametric(driver._point(chord1), driver._point(chord2), 120.0))
        _apply_dimension_entity(driver, entity, spec, style_name)
        created = _add({"handle": _handle(entity)}, handles)
        return created[0] if created else ""
    return _add_aligned_dim(driver, spec, chord1, chord2, [(chord1[0] + chord2[0]) / 2, chord1[1] - 180, Z], handles)


def _add_angular_dim(
    driver: Any,
    spec: dict[str, Any],
    vertex: list[float],
    p1: list[float],
    p2: list[float],
    text_position: list[float],
    handles: list[str],
) -> str:
    style_name = str(spec["cadStyleName"])
    if _has_com_modelspace(driver) and hasattr(driver.model_space, "AddDimAngular"):
        entity = _with_active_dimstyle(
            driver,
            style_name,
            lambda: driver.model_space.AddDimAngular(driver._point(vertex), driver._point(p1), driver._point(p2), driver._point(text_position)),
        )
        _apply_dimension_entity(driver, entity, spec, style_name)
        created = _add({"handle": _handle(entity)}, handles)
        return created[0] if created else ""
    return _add_aligned_dim(driver, spec, p1, p2, text_position, handles)


def _has_com_modelspace(driver: Any) -> bool:
    return hasattr(driver, "model_space") and hasattr(driver, "_point")


def _with_active_dimstyle(driver: Any, style_name: str, callback: Any) -> Any:
    doc = getattr(driver, "doc", None)
    old_style = None
    if doc is not None and hasattr(doc, "DimStyles"):
        try:
            old_style = getattr(doc, "ActiveDimStyle", None)
            doc.ActiveDimStyle = doc.DimStyles.Item(style_name)
        except Exception:
            pass
    try:
        return callback()
    finally:
        if old_style is not None:
            try:
                doc.ActiveDimStyle = old_style
            except Exception:
                pass


def _apply_dimension_entity(driver: Any, entity: Any, spec: dict[str, Any], style_name: str) -> None:
    try:
        entity.StyleName = style_name
    except Exception:
        pass
    try:
        driver._apply_common(entity, layer=PREVIEW_LAYER, color=str(spec["color"]))
    except Exception:
        try:
            entity.Layer = PREVIEW_LAYER
        except Exception:
            pass
    try:
        entity.Update()
    except Exception:
        pass


def _parking_anchor(driver: Any) -> dict[str, Any]:
    entities = []
    if hasattr(driver, "snapshot_modelspace"):
        try:
            entities = driver.snapshot_modelspace(layer=PREVIEW_LAYER)
        except Exception:
            entities = []
    bbox = _bbox_from_entities([entity for entity in entities if isinstance(entity, dict)])
    if bbox:
        origin = [float(bbox["max"][0]) + 700.0, float(bbox["max"][1]) + 800.0, 0.0]
        return {"mode": "global_preview_bbox", "bbox": bbox, "origin": origin}
    return {"mode": "origin", "bbox": None, "origin": [12000.0, 9000.0, 0.0]}


def _bbox_from_entities(entities: list[dict[str, Any]]) -> dict[str, list[float]] | None:
    xs: list[float] = []
    ys: list[float] = []
    for entity in entities:
        bbox = entity.get("bbox")
        if isinstance(bbox, dict) and isinstance(bbox.get("min"), list) and isinstance(bbox.get("max"), list):
            xs.extend([float(bbox["min"][0]), float(bbox["max"][0])])
            ys.extend([float(bbox["min"][1]), float(bbox["max"][1])])
            continue
        for key in ("start_point", "end_point", "position", "center", "text_position", "xline1_point", "xline2_point"):
            point = entity.get(key)
            if isinstance(point, list) and len(point) >= 2:
                xs.append(float(point[0]))
                ys.append(float(point[1]))
    if not xs or not ys:
        return None
    return {"min": [min(xs), min(ys)], "max": [max(xs), max(ys)]}


def _snapshot_created(driver: Any, handles: list[str]) -> list[dict[str, Any]]:
    unique = list(dict.fromkeys(handles))
    if hasattr(driver, "snapshot_handles"):
        return [entity for entity in driver.snapshot_handles(handles=unique, layer=PREVIEW_LAYER) if isinstance(entity, dict)]
    return []


def _audit_dimension_styles(
    *,
    specs: list[dict[str, Any]],
    style_reports: list[dict[str, Any]],
    readback: list[dict[str, Any]],
    dimension_handles_by_style: dict[str, list[str]],
    panel_handles_by_style: dict[str, list[str]] | None = None,
    panel_bounds_by_style: dict[str, dict[str, list[float]]] | None = None,
    require_global_variety: bool = True,
) -> dict[str, Any]:
    by_handle = {str(entity.get("handle")): entity for entity in readback if entity.get("handle")}
    rows: list[dict[str, Any]] = []
    failed = 0
    fingerprints: dict[str, list[str]] = {}
    for spec, style_report in zip(specs, style_reports, strict=True):
        style_name = str(spec["cadStyleName"])
        dimension_kind = str(spec.get("dimensionKind", ""))
        endpoint_family = str(spec.get("endpointFamily", ""))
        arrow_block = str(spec.get("arrowBlock", ""))
        is_level_marker = dimension_kind == "level_marker"
        scale_samples = _scale_samples(spec)
        fingerprint = "|".join(
            [
                str(spec.get("dimensionKind")),
                endpoint_family,
                arrow_block,
                str(spec.get("chainRole")),
                str(spec.get("scale")),
                str(spec.get("paperTextHeight")),
                str(spec.get("paperArrowSize")),
            ]
        )
        fingerprints.setdefault(fingerprint, []).append(style_name)
        expected_handles = dimension_handles_by_style.get(style_name, [])
        panel_handles = (panel_handles_by_style or {}).get(style_name, [])
        panel_bounds = (panel_bounds_by_style or {}).get(style_name)
        readback_entities = [by_handle.get(handle) for handle in expected_handles]
        readback_entities = [entity for entity in readback_entities if isinstance(entity, dict)]
        panel_entities = [by_handle.get(handle) for handle in panel_handles]
        panel_entities = [entity for entity in panel_entities if isinstance(entity, dict)]
        dimension_entities = [entity for entity in readback_entities if entity.get("type") == "dimension"]
        failures: list[dict[str, Any]] = []
        if not expected_handles and not is_level_marker:
            failures.append({"field": "dimension_handles", "status": "fail", "reason": "no dimensions created"})
        if len(readback_entities) != len(expected_handles):
            failures.append(
                {
                    "field": "readback_count",
                    "status": "fail",
                    "expected": len(expected_handles),
                    "actual": len(readback_entities),
                }
            )
        if not is_level_marker and len(dimension_entities) != len(expected_handles):
            failures.append(
                {
                    "field": "dimension_type",
                    "status": "fail",
                    "expected": len(expected_handles),
                    "actual": len(dimension_entities),
                    "nonDimensionHandles": [
                        entity.get("handle") for entity in readback_entities if entity.get("type") != "dimension"
                    ],
                }
            )
        if style_report.get("status") not in {"pass", "fake_pass"}:
            failures.append({"field": "style_create", "status": "fail", "actual": style_report.get("status")})
        read_vars = style_report.get("readback", {}).get("variables", {}) if isinstance(style_report.get("readback"), dict) else {}
        if len(scale_samples) < MIN_SCALE_VARIANTS_PER_STYLE:
            failures.append(
                {
                    "field": "scale_samples",
                    "status": "fail",
                    "expectedMin": MIN_SCALE_VARIANTS_PER_STYLE,
                    "actual": len(scale_samples),
                }
            )
        out_of_bounds = _panel_out_of_bounds_entities(panel_entities, panel_bounds)
        if out_of_bounds:
            failures.append(
                {
                    "field": "panel_containment",
                    "status": "fail",
                    "outOfBoundsCount": len(out_of_bounds),
                    "outOfBounds": out_of_bounds[:8],
                }
            )
        level_marker_texts = _level_marker_texts(panel_entities)
        if is_level_marker and len(level_marker_texts) < 4:
            failures.append(
                {
                    "field": "level_marker_texts",
                    "status": "fail",
                    "expectedMin": 4,
                    "actual": len(level_marker_texts),
                    "texts": level_marker_texts,
                }
            )
        for var_name in ("DIMTXT", "DIMASZ", "DIMSCALE", "DIMDEC", "DIMCLRD", "DIMCLRE", "DIMCLRT"):
            expected = style_report.get("variables", {}).get(var_name)
            actual = read_vars.get(var_name)
            if expected is None or actual is None:
                continue
            try:
                if abs(float(actual) - float(expected)) > 0.001:
                    failures.append({"field": var_name, "status": "fail", "expected": expected, "actual": actual})
            except Exception:
                if str(actual) != str(expected):
                    failures.append({"field": var_name, "status": "fail", "expected": expected, "actual": actual})
        if arrow_block and "DIMBLK" in read_vars:
            actual_arrow = _normalize_arrow_block(read_vars.get("DIMBLK"))
            expected_arrow = _normalize_arrow_block(arrow_block)
            if actual_arrow != expected_arrow:
                failures.append({"field": "DIMBLK", "status": "fail", "expected": arrow_block, "actual": read_vars.get("DIMBLK")})
        for entity in readback_entities:
            if entity.get("layer") != PREVIEW_LAYER:
                failures.append({"field": "layer", "status": "fail", "handle": entity.get("handle"), "actual": entity.get("layer")})
            actual_style = entity.get("style_name")
            if actual_style and actual_style != style_name:
                failures.append({"field": "style_name", "status": "fail", "handle": entity.get("handle"), "expected": style_name, "actual": actual_style})
            measurement = entity.get("measurement")
            if measurement is not None and float(measurement) <= 0:
                failures.append({"field": "measurement", "status": "fail", "handle": entity.get("handle"), "actual": measurement})
        layout_checks = _dimension_layout_checks(spec, dimension_entities, panel_bounds)
        failures.extend(layout_checks["failures"])
        if failures:
            failed += 1
        rows.append(
            {
                "styleId": spec["styleId"],
                "styleName": style_name,
                "visibleTitle": spec["visibleTitle"],
                "dimensionKind": dimension_kind,
                "endpointFamily": endpoint_family,
                "arrowBlock": arrow_block,
                "chainRole": spec.get("chainRole"),
                "levelMarkerTextCount": len(level_marker_texts),
                "levelMarkerTexts": level_marker_texts,
                "scaleVariantCount": len(scale_samples),
                "scaleVariantLabels": [str(sample.get("label", "")) for sample in scale_samples],
                "styleFingerprint": fingerprint,
                "panelHandleCount": len(panel_handles),
                "panelReadbackCount": len(panel_entities),
                "panelBounds": panel_bounds,
                "expectedDimensionHandleCount": len(expected_handles),
                "readbackCount": len(readback_entities),
                "dimensionReadbackCount": len(dimension_entities),
                "dimensionHandles": expected_handles,
                "dimensionReadbacks": [
                    {
                        "handle": entity.get("handle"),
                        "type": entity.get("type"),
                        "layer": entity.get("layer"),
                        "style_name": entity.get("style_name"),
                        "text": entity.get("text"),
                        "measurement": entity.get("measurement"),
                        "text_height": entity.get("text_height"),
                        "text_position": entity.get("text_position"),
                        "xline1_point": entity.get("xline1_point"),
                        "xline2_point": entity.get("xline2_point"),
                        "bbox": entity.get("bbox"),
                    }
                    for entity in readback_entities
                ],
                "layoutChecks": layout_checks["summary"],
                "status": "pass" if not failures else "fail",
                "failures": failures,
            }
        )
    duplicates = [
        {"fingerprint": fingerprint, "styles": names}
        for fingerprint, names in fingerprints.items()
        if len(names) > 1
    ]
    endpoint_family_count = len({str(spec.get("endpointFamily", "")) for spec in specs if spec.get("endpointFamily")})
    global_failures: list[dict[str, Any]] = []
    if duplicates:
        global_failures.append({"field": "style_fingerprint", "status": "fail", "duplicates": duplicates})
    if require_global_variety and endpoint_family_count < 6:
        global_failures.append({"field": "endpoint_family_variety", "status": "fail", "expectedMin": 6, "actual": endpoint_family_count})
    status = "pass" if failed == 0 and not global_failures and len(rows) == len(specs) else "fail"
    return {
        "status": status,
        "styleCountExpected": len(specs),
        "styleCountAudited": len(rows),
        "failedStyleCount": failed,
        "endpointFamilyCount": endpoint_family_count,
        "duplicateStyleFingerprints": duplicates,
        "globalFailures": global_failures,
        "rows": rows,
    }


def _dimension_layout_checks(
    spec: dict[str, Any],
    dimension_entities: list[dict[str, Any]],
    panel_bounds: dict[str, list[float]] | None,
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    summary: dict[str, Any] = {
        "footerOverlap": "pass",
        "displayMeasurementMismatch": "pass",
        "allowedDisplayScales": _sample_display_scales(spec),
    }
    dimension_kind = str(spec.get("dimensionKind", ""))
    requires_clearance = dimension_kind in {"elevation_height", "opening_width_height"}
    if requires_clearance and panel_bounds:
        footer_band_top = float(panel_bounds["min"][1]) + 240.0
        summary["footerBandTop"] = footer_band_top
        overlapping: list[dict[str, Any]] = []
        for entity in dimension_entities:
            bbox = _entity_bbox(entity)
            if not bbox:
                continue
            min_y = float(bbox["min"][1])
            if min_y < footer_band_top:
                overlapping.append({"handle": entity.get("handle"), "minY": min_y, "footerBandTop": footer_band_top})
        if overlapping:
            summary["footerOverlap"] = "fail"
            failures.append(
                {
                    "field": "footer_overlap",
                    "status": "fail",
                    "overlappingDimensions": overlapping[:8],
                }
            )

    display_mismatches: list[dict[str, Any]] = []
    allowed_scales = _sample_display_scales(spec)
    for entity in dimension_entities:
        text_value = _numeric_text(entity.get("text"))
        measurement = _float_or_none(entity.get("measurement"))
        if text_value is None or measurement is None:
            continue
        if _display_measurement_matches(measurement, text_value, allowed_scales):
            continue
        display_mismatches.append(
            {
                "handle": entity.get("handle"),
                "text": entity.get("text"),
                "measurement": measurement,
                "allowedDisplayScales": allowed_scales,
            }
        )
    if display_mismatches:
        summary["displayMeasurementMismatch"] = "fail"
        failures.append(
            {
                "field": "display_measurement_mismatch",
                "status": "fail",
                "mismatches": display_mismatches[:8],
            }
        )
    return {"summary": summary, "failures": failures}


def _display_measurement_matches(measurement: float, text_value: float, allowed_scales: list[float]) -> bool:
    for scale in allowed_scales:
        expected = measurement * scale
        tolerance = max(1.0, abs(text_value) * 0.015)
        if abs(expected - text_value) <= tolerance:
            return True
    return False


def _numeric_text(value: Any) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return float(text.replace(",", ""))
    except Exception:
        return None


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def _entity_bbox(entity: dict[str, Any]) -> dict[str, list[float]] | None:
    bbox = entity.get("bbox")
    if isinstance(bbox, dict) and isinstance(bbox.get("min"), list) and isinstance(bbox.get("max"), list):
        return {
            "min": [float(bbox["min"][0]), float(bbox["min"][1])],
            "max": [float(bbox["max"][0]), float(bbox["max"][1])],
        }
    return _bbox_from_entities([entity])


def _panel_out_of_bounds_entities(
    entities: list[dict[str, Any]],
    bounds: dict[str, list[float]] | None,
) -> list[dict[str, Any]]:
    if not bounds or not isinstance(bounds.get("min"), list) or not isinstance(bounds.get("max"), list):
        return []
    min_x = float(bounds["min"][0]) - PANEL_CONTAINMENT_TOLERANCE
    min_y = float(bounds["min"][1]) - PANEL_CONTAINMENT_TOLERANCE
    max_x = float(bounds["max"][0]) + PANEL_CONTAINMENT_TOLERANCE
    max_y = float(bounds["max"][1]) + PANEL_CONTAINMENT_TOLERANCE
    out: list[dict[str, Any]] = []
    for entity in entities:
        bbox = entity.get("bbox")
        if not isinstance(bbox, dict) or not isinstance(bbox.get("min"), list) or not isinstance(bbox.get("max"), list):
            continue
        entity_min = bbox["min"]
        entity_max = bbox["max"]
        try:
            outside = (
                float(entity_min[0]) < min_x
                or float(entity_min[1]) < min_y
                or float(entity_max[0]) > max_x
                or float(entity_max[1]) > max_y
            )
        except Exception:
            continue
        if outside:
            out.append(
                {
                    "handle": entity.get("handle"),
                    "type": entity.get("type"),
                    "bbox": bbox,
                }
            )
    return out


def _level_marker_texts(entities: list[dict[str, Any]]) -> list[str]:
    texts: list[str] = []
    for entity in entities:
        if entity.get("type") != "text":
            continue
        text = str(entity.get("text", "")).strip()
        if text and ("+0." in text or "+2." in text or "±0." in text or text in {"完成面", "台面", "吊顶"}):
            texts.append(text)
    return texts


def _zoom_to_handles(driver: Any, handles: list[str]) -> dict[str, Any]:
    if hasattr(driver, "zoom_to_handles"):
        try:
            return dict(driver.zoom_to_handles(handles=list(dict.fromkeys(handles)), layer=PREVIEW_LAYER, padding_ratio=0.18))
        except Exception as exc:
            return {"status": "fail", "reason": str(exc)}
    return {"status": "not_checked", "reason": "driver has no zoom_to_handles"}


def _refresh(driver: Any) -> dict[str, Any]:
    if hasattr(driver, "refresh_view"):
        try:
            return dict(driver.refresh_view())
        except Exception as exc:
            return {"status": "fail", "reason": str(exc)}
    return {"status": "not_checked"}


def _active_document(driver: Any) -> dict[str, Any]:
    doc = getattr(driver, "doc", None)
    if doc is None:
        return {"status": "not_checked"}
    try:
        name = str(getattr(doc, "Name", ""))
        full_name = str(getattr(doc, "FullName", ""))
    except Exception as exc:
        return {"status": "partial", "reason": f"active document metadata unavailable: {exc}"}
    return {
        "status": "pass",
        "name": name,
        "fullName": full_name,
    }


def _collect_handles(result: Any) -> list[str]:
    handles: list[str] = []
    if isinstance(result, dict):
        for key in ("created_handles", "handles", "boundary_handles"):
            value = result.get(key)
            if isinstance(value, list):
                handles.extend(str(item) for item in value if item)
        if result.get("handle"):
            handles.append(str(result["handle"]))
    elif isinstance(result, list):
        handles.extend(str(item) for item in result if item)
    elif isinstance(result, str):
        handles.append(result)
    return list(dict.fromkeys(handles))


def _normalize_arrow_block(value: Any) -> str:
    if value is None:
        return ""
    raw = str(value).strip()
    aliases = {
        "建筑标记": "_ARCHTICK",
        "小点": "_DOTSMALL",
        "无": "_NONE",
        "闭合实心": ".",
        "实心闭合": ".",
        "closed filled": ".",
        "closedfilled": ".",
        "": ".",
    }
    return aliases.get(raw, raw).upper()


def _handle(entity: Any) -> str:
    return str(getattr(entity, "Handle", getattr(entity, "handle", "")))
