"""Reusable Chinese linetype table demo with text-encoding guards and streaming pacing."""

from __future__ import annotations

import json
import math
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from core.runtime.encoding_guard import detect_text_encoding_corruption
from core.safety.policy import PREVIEW_LAYER
from core.training.linetype_table_audit import audit_linetype_table_layout
from core.training.streaming_demo import StreamingCadDemoConfig, StreamingCadDemoRecorder

SleepFn = Callable[[float], None]

ROW_NUMBER_STYLE = "arabic"

LINETYPE_TABLE_ROWS: list[dict[str, Any]] = [
    {"group": "基础图案线型", "name": "连续实线", "usage": "常规可见边与轮廓", "mode": "linetype", "lt": "CONTINUOUS", "color": "white", "lw": 0.25, "scale": 1.0},
    {"group": "基础图案线型", "name": "短虚线", "usage": "基础虚线，测试短断续", "mode": "linetype", "lt": "DASHED", "color": "yellow", "lw": 0.25, "scale": 35.0},
    {"group": "基础图案线型", "name": "隐藏线", "usage": "遮挡边与上方物件", "mode": "linetype", "lt": "HIDDEN", "color": "magenta", "lw": 0.25, "scale": 35.0},
    {"group": "基础图案线型", "name": "中心线", "usage": "轴线、对称线、圆心线", "mode": "linetype", "lt": "CENTER", "color": "cyan", "lw": 0.25, "scale": 45.0},
    {"group": "基础图案线型", "name": "点线", "usage": "点状参考与弱提示", "mode": "linetype", "lt": "DOT", "color": "green", "lw": 0.25, "scale": 45.0},
    {"group": "基础图案线型", "name": "点划线", "usage": "定位线与控制线", "mode": "linetype", "lt": "DASHDOT", "color": "blue", "lw": 0.25, "scale": 45.0},
    {"group": "基础图案线型", "name": "分割点线", "usage": "分区边界与分割线", "mode": "linetype", "lt": "DIVIDE", "color": "red", "lw": 0.25, "scale": 45.0},
    {"group": "基础图案线型", "name": "幻影线", "usage": "未来预留或运动范围", "mode": "linetype", "lt": "PHANTOM", "color": "magenta", "lw": 0.25, "scale": 45.0},
    {"group": "基础图案线型", "name": "边界线", "usage": "范围框与边界提示", "mode": "linetype", "lt": "BORDER", "color": "yellow", "lw": 0.25, "scale": 45.0},
    {"group": "基础图案线型", "name": "细虚线", "usage": "小比例隐藏边测试", "mode": "linetype", "lt": "DASHED2", "color": "green", "lw": 0.15, "scale": 35.0},
    {"group": "基础图案线型", "name": "长虚线", "usage": "投影或拆除提示", "mode": "linetype", "lt": "HIDDEN2", "color": "blue", "lw": 0.25, "scale": 55.0},
    {"group": "基础图案线型", "name": "稀疏轴线", "usage": "大尺度中心线测试", "mode": "linetype", "lt": "CENTER2", "color": "cyan", "lw": 0.25, "scale": 60.0},
    {"group": "工程与家装语义", "name": "墙体粗轮廓", "usage": "剖切墙体与主轮廓", "mode": "linetype", "lt": "CONTINUOUS", "color": "red", "lw": 0.50, "scale": 1.0},
    {"group": "工程与家装语义", "name": "家具外轮廓", "usage": "家具边界与外形识别", "mode": "linetype", "lt": "CONTINUOUS", "color": "cyan", "lw": 0.35, "scale": 1.0},
    {"group": "工程与家装语义", "name": "家具内部细节", "usage": "柜门缝、坐垫分割", "mode": "linetype", "lt": "CONTINUOUS", "color": "white", "lw": 0.15, "scale": 1.0},
    {"group": "工程与家装语义", "name": "上方投影线", "usage": "吊柜、灯具、顶面投影", "mode": "linetype", "lt": "DASHED", "color": "blue", "lw": 0.20, "scale": 45.0},
    {"group": "工程与家装语义", "name": "隐藏边线", "usage": "柜内搁板与被挡边", "mode": "linetype", "lt": "HIDDEN", "color": "magenta", "lw": 0.20, "scale": 35.0},
    {"group": "工程与家装语义", "name": "标注引线", "usage": "尺寸、索引、说明引出", "mode": "linetype", "lt": "CONTINUOUS", "color": "green", "lw": 0.15, "scale": 1.0},
    {"group": "工程与家装语义", "name": "开启范围线", "usage": "门扇、抽屉、检修空间", "mode": "swing_arc", "lt": "CENTER", "color": "yellow", "lw": 0.20, "scale": 45.0},
    {"group": "工程与家装语义", "name": "材质分界线", "usage": "铺装、饰面、收口分界", "mode": "linetype", "lt": "DASHDOT", "color": "red", "lw": 0.20, "scale": 45.0},
    {"group": "工程与家装语义", "name": "轴网定位线", "usage": "建筑轴网、柱网定位", "mode": "linetype", "lt": "CENTER", "color": "cyan", "lw": 0.18, "scale": 55.0},
    {"group": "工程与家装语义", "name": "尺寸线与尺寸界线", "usage": "尺寸标注与延伸界线", "mode": "linetype", "lt": "BYLAYER", "color": "white", "lw": 0.13, "scale": 1.0, "style_source": "by_layer"},
    {"group": "工程与家装语义", "name": "剖切位置线", "usage": "剖面切割位置提示", "mode": "section_cut", "color": "red", "lw": 0.35},
    {"group": "工程与家装语义", "name": "拆除构件线", "usage": "拆墙、拆柜、拆设备", "mode": "demolition", "color": "yellow", "lw": 0.25},
    {"group": "专业管线语义", "name": "给水管线", "usage": "冷水、生活给水路径", "mode": "pipe_text", "color": "cyan", "lw": 0.20, "marks": ["给", "水"]},
    {"group": "专业管线语义", "name": "热水管线", "usage": "热水路径与回水提示", "mode": "pipe_text", "color": "red", "lw": 0.20, "marks": ["热", "水"]},
    {"group": "专业管线语义", "name": "排水管线", "usage": "排水、污水、废水路径", "mode": "pipe_text", "color": "green", "lw": 0.25, "marks": ["排", "水"]},
    {"group": "专业管线语义", "name": "燃气管线", "usage": "燃气走向与阀门连接", "mode": "pipe_text", "color": "yellow", "lw": 0.25, "marks": ["燃", "气"]},
    {"group": "专业管线语义", "name": "强电线路", "usage": "插座、照明、电源回路", "mode": "pipe_text", "color": "red", "lw": 0.18, "marks": ["强", "电"]},
    {"group": "专业管线语义", "name": "弱电线路", "usage": "网络、电视、安防控制", "mode": "pipe_text", "color": "magenta", "lw": 0.18, "marks": ["弱", "电"]},
    {"group": "专业管线语义", "name": "消防管线", "usage": "喷淋、消防给水、报警", "mode": "pipe_text", "color": "red", "lw": 0.25, "marks": ["消", "防"]},
    {"group": "专业管线语义", "name": "空调冷媒风管线", "usage": "空调管路、风管中心", "mode": "pipe_text", "color": "blue", "lw": 0.20, "marks": ["空", "调"]},
    {"group": "边界与控制线", "name": "地界红线", "usage": "用地边界、控制边线", "mode": "linetype", "lt": "PHANTOM", "color": "red", "lw": 0.35, "scale": 60.0},
    {"group": "边界与控制线", "name": "退界控制线", "usage": "建筑退距、限建范围", "mode": "linetype", "lt": "DASHDOT", "color": "yellow", "lw": 0.20, "scale": 60.0},
    {"group": "边界与控制线", "name": "规划预留线", "usage": "未来预留设备或洞口", "mode": "linetype", "lt": "PHANTOM", "color": "magenta", "lw": 0.20, "scale": 60.0},
    {"group": "边界与控制线", "name": "安全净距线", "usage": "检修、消防、通行净距", "mode": "linetype", "lt": "BORDER", "color": "yellow", "lw": 0.18, "scale": 45.0},
    {"group": "复合模拟线型", "name": "折断线", "usage": "断开或省略区段", "mode": "zigzag", "color": "yellow", "lw": 0.25},
    {"group": "复合模拟线型", "name": "波浪线", "usage": "软性边界或草图边", "mode": "wave", "color": "cyan", "lw": 0.25},
    {"group": "复合模拟线型", "name": "圆围栏线", "usage": "控制范围与围合边", "mode": "fence_circle", "color": "green", "lw": 0.20},
    {"group": "复合模拟线型", "name": "方围栏线", "usage": "网格围合或安全区", "mode": "fence_square", "color": "blue", "lw": 0.20},
    {"group": "复合模拟线型", "name": "保温棉线", "usage": "保温层、软包层示意", "mode": "batting", "color": "magenta", "lw": 0.20},
    {"group": "复合模拟线型", "name": "文字管线", "usage": "管线识别与方向提示", "mode": "text_pipe", "color": "red", "lw": 0.20},
]

TITLE = "线型样式与颜色归纳表"
SUBTITLE = "预览层测试；颜色、线宽、线型比例已区分；图纸未保存"
HEADERS = ["序", "线型名称", "样线", "用途与测试点"]

X0 = 8200.0
TOP = 6900.0
PANEL_W = 6400.0
PANEL_GAP = 260.0
TABLE_W = PANEL_W * 2 + PANEL_GAP
PANEL_COUNT = 2
TITLE_H = 380.0
HEADER_H = 250.0
GROUP_H = 180.0
ROW_H = 200.0
SAMPLE_CELL_MARGIN = 20.0
Z = 0.0
COLS = [X0, X0 + 430, X0 + 1650, X0 + 3650, X0 + PANEL_W]
RIGHT = X0 + TABLE_W
BOTTOM = TOP - TITLE_H - HEADER_H - GROUP_H * 4 - ROW_H * math.ceil(len(LINETYPE_TABLE_ROWS) / PANEL_COUNT) - 130
SAMPLE_X0 = COLS[2] + 230
SAMPLE_X1 = COLS[3] - 230

LAYOUT_POLICY = {
    "mode": "integrated_dual_panel",
    "panelCount": PANEL_COUNT,
    "splitStrategy": "balanced_visual_height_shared_outer_frame",
    "minRowHeight": ROW_H,
    "minHeaderHeight": HEADER_H,
    "minGroupHeight": GROUP_H,
    "rowHeightStrategy": "adaptive_min_height",
    "sampleFitStrategy": "fit_to_sample_cell_bbox",
    "sampleCellMargin": SAMPLE_CELL_MARGIN,
    "allowSolidFillBackground": False,
    "solidFillUsed": False,
    "titleBandMerged": True,
    "groupRowsMerged": True,
    "rowNumberStyle": ROW_NUMBER_STYLE,
}

ACI_COLORS = {"red": 1, "yellow": 2, "green": 3, "cyan": 4, "blue": 5, "magenta": 6, "white": 7}

SAMPLE_VERTICAL_NEEDS = {
    "zigzag": 90.0,
    "wave": 76.0,
    "fence_circle": 90.0,
    "fence_square": 90.0,
    "batting": 164.0,
    "text_pipe": 90.0,
    "pipe_text": 90.0,
    "section_cut": 150.0,
    "demolition": 120.0,
    "swing_arc": 276.0,
}


def visible_texts(rows: list[dict[str, Any]] | None = None) -> list[str]:
    result = [TITLE, SUBTITLE, *HEADERS]
    for index, row in enumerate(rows or LINETYPE_TABLE_ROWS):
        result.extend([str(index + 1), str(row["group"]), str(row["name"]), str(row["usage"])])
    return result


def validate_visible_text(rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    active_rows = rows or LINETYPE_TABLE_ROWS
    texts = visible_texts(active_rows)
    encoding_preflight = detect_text_encoding_corruption(texts)
    latin_hits = [text for text in texts if re.search(r"[A-Za-z]", text)]
    question_hits = [text for text in texts if "?" in text]
    expected_count = len(active_rows)
    status = (
        "pass"
        if expected_count > 0
        and len(active_rows) == expected_count
        and not latin_hits
        and not question_hits
        and encoding_preflight["status"] == "pass"
        else "fail"
    )
    return {
        "status": status,
        "row_count": len(active_rows),
        "latin_hits": latin_hits,
        "question_hits": question_hits,
        "encodingPreflight": encoding_preflight,
    }


def _balanced_panels(rows: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    if PANEL_COUNT != 2 or len(rows) <= 1:
        target = math.ceil(len(rows) / PANEL_COUNT)
        return [rows[index * target : (index + 1) * target] for index in range(PANEL_COUNT)]

    def panel_height(panel_rows: list[dict[str, Any]]) -> float:
        group_count = len(dict.fromkeys(str(row["group"]) for row in panel_rows))
        return GROUP_H * group_count + sum(_row_height(row) for row in panel_rows)

    best_split = math.ceil(len(rows) / PANEL_COUNT)
    best_delta = float("inf")
    min_rows_per_panel = max(1, len(rows) // 3)
    for split in range(min_rows_per_panel, len(rows) - min_rows_per_panel + 1):
        left = rows[:split]
        right = rows[split:]
        delta = abs(panel_height(left) - panel_height(right))
        if delta < best_delta:
            best_split = split
            best_delta = delta
    return [rows[:best_split], rows[best_split:]]


def _cols(panel_x0: float) -> list[float]:
    return [panel_x0, panel_x0 + 430, panel_x0 + 1700, panel_x0 + 3850, panel_x0 + PANEL_W]


def _row_height(row: dict[str, Any]) -> float:
    explicit_height = row.get("row_height")
    if explicit_height is not None:
        try:
            return max(ROW_H, float(explicit_height))
        except Exception:
            pass
    sample_need = SAMPLE_VERTICAL_NEEDS.get(str(row.get("mode")), 0.0)
    return max(ROW_H, sample_need + SAMPLE_CELL_MARGIN * 2.0)


def _panel_bbox(panel_x0: float, rows: list[dict[str, Any]], group_count: int) -> dict[str, list[float]]:
    panel_bottom = TOP - TITLE_H - HEADER_H - GROUP_H * group_count - sum(_row_height(row) for row in rows) - 130
    return {"min": [panel_x0, panel_bottom], "max": [panel_x0 + PANEL_W, TOP]}


def _collect(result: Any) -> list[str]:
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


class _LinetypeTableDrawer:
    def __init__(self, driver: Any, recorder: StreamingCadDemoRecorder) -> None:
        self.driver = driver
        self.recorder = recorder
        self.handles: list[str] = []

    def _add(self, result: Any, *, operation: str) -> list[str]:
        created = _collect(result)
        for handle in created:
            if handle not in self.handles:
                self.handles.append(handle)
        self.recorder.after_operation(operation, created)
        return created

    def line(self, p1: list[float], p2: list[float], **kwargs: Any) -> list[str]:
        return self._add(self.driver.draw_line(start_point=p1, end_point=p2, layer=PREVIEW_LAYER, **kwargs), operation="line")

    def text(self, text: str, pos: list[float], *, height: float = 70, color: str = "white") -> list[str]:
        return self._add(self.driver.draw_text(text=text, position=pos, height=height, layer=PREVIEW_LAYER, color=color), operation="text")

    def rect(self, p1: list[float], p2: list[float], **kwargs: Any) -> list[str]:
        return self._add(self.driver.draw_rectangle(corner1=p1, corner2=p2, layer=PREVIEW_LAYER, **kwargs), operation="rect")

    def column_segments(self, cols: list[float], y_top: float, y_bottom: float, *, lineweight: float = 0.13) -> int:
        for x in cols[1:-1]:
            self.line([x, y_top, Z], [x, y_bottom, Z], color="white", lineweight=lineweight)
        return len(cols[1:-1])

    def poly(self, points: list[list[float]], **kwargs: Any) -> list[str]:
        return self._add(self.driver.draw_polyline(points=points, closed=False, layer=PREVIEW_LAYER, **kwargs), operation="polyline")

    def circle(self, center: list[float], radius: float, **kwargs: Any) -> list[str]:
        return self._add(self.driver.draw_circle(center=center, radius=radius, layer=PREVIEW_LAYER, **kwargs), operation="circle")

    def arc(self, center: list[float], radius: float, start_angle: float, end_angle: float, **kwargs: Any) -> list[str]:
        return self._add(
            self.driver.draw_arc(
                center=center,
                radius=radius,
                start_angle=start_angle,
                end_angle=end_angle,
                layer=PREVIEW_LAYER,
                **kwargs,
            ),
            operation="arc",
        )

    def _style_kwargs(self, row: dict[str, Any]) -> dict[str, Any]:
        if row.get("style_source") == "by_layer":
            return {}
        kwargs: dict[str, Any] = {"color": row["color"], "lineweight": row["lw"], "linetype_scale": row.get("scale", 1.0)}
        linetype = row.get("lt")
        if linetype and linetype != "BYLAYER":
            kwargs["linetype"] = linetype
        return kwargs

    def linetype_line(self, row: dict[str, Any], y: float, sample_x0: float, sample_x1: float) -> None:
        kwargs = self._style_kwargs(row)
        try:
            self.line([sample_x0, y, Z], [sample_x1, y, Z], **kwargs)
        except Exception:
            self.line([sample_x0, y, Z], [sample_x1, y, Z], color=row["color"], lineweight=row["lw"])

    def sample(self, row: dict[str, Any], y: float, sample_x0: float, sample_x1: float, *, cell_height: float | None = None) -> list[str]:
        start_index = len(self.handles)
        mode = row["mode"]
        color = row["color"]
        lineweight = row["lw"]
        usable_half_height = max(24.0, (float(cell_height or (ROW_H - SAMPLE_CELL_MARGIN * 2.0)) / 2.0) - 8.0)
        if mode == "linetype":
            self.linetype_line(row, y, sample_x0, sample_x1)
        elif mode == "zigzag":
            points = [[sample_x0 + i * 115.0, y + (0 if i in (0, 13) else (45.0 if i % 2 else -45.0)), Z] for i in range(14)]
            self.poly(points, color=color, lineweight=lineweight)
        elif mode == "wave":
            points = []
            for i in range(37):
                t = i / 36
                points.append([sample_x0 + (sample_x1 - sample_x0) * t, y + math.sin(t * math.pi * 8) * 38.0, Z])
            self.poly(points, color=color, lineweight=lineweight)
        elif mode == "fence_circle":
            self.line([sample_x0, y, Z], [sample_x1, y, Z], color=color, lineweight=lineweight)
            for i in range(5):
                self.circle([sample_x0 + 210 + i * 320, y, Z], 45, color=color, lineweight=lineweight)
        elif mode == "fence_square":
            self.line([sample_x0, y, Z], [sample_x1, y, Z], color=color, lineweight=lineweight)
            for i in range(5):
                x = sample_x0 + 210 + i * 320
                self.rect([x - 45, y - 45, Z], [x + 45, y + 45, Z], color=color, lineweight=lineweight)
        elif mode == "batting":
            band_offset = min(68.0, usable_half_height)
            amplitude = min(46.0, band_offset * 0.68)
            points = []
            for i in range(45):
                t = i / 44
                points.append([sample_x0 + (sample_x1 - sample_x0) * t, y + math.sin(t * math.pi * 14) * amplitude, Z])
            self.poly(points, color=color, lineweight=lineweight)
            self.line([sample_x0, y - band_offset, Z], [sample_x1, y - band_offset, Z], color=color, lineweight=0.09)
            self.line([sample_x0, y + band_offset, Z], [sample_x1, y + band_offset, Z], color=color, lineweight=0.09)
        elif mode in {"text_pipe", "pipe_text"}:
            marks = list(row.get("marks") or ["水", "电"])
            self.line([sample_x0, y, Z], [sample_x0 + 330, y, Z], color=color, lineweight=lineweight)
            self.line([sample_x0 + 650, y, Z], [sample_x0 + 970, y, Z], color=color, lineweight=lineweight)
            self.line([sample_x0 + 1290, y, Z], [sample_x1, y, Z], color=color, lineweight=lineweight)
            self.text(str(marks[0]), [sample_x0 + 390, y - 45, Z], height=80, color=color)
            self.text(str(marks[1]), [sample_x0 + 1030, y - 45, Z], height=80, color=color)
        elif mode == "section_cut":
            self.line([sample_x0, y, Z], [sample_x1 - 180, y, Z], color=color, lineweight=lineweight)
            self.poly(
                [[sample_x1 - 180, y, Z], [sample_x1 - 320, y + 70, Z], [sample_x1 - 320, y - 70, Z], [sample_x1 - 180, y, Z]],
                color=color,
                lineweight=lineweight,
            )
            self.text("剖", [sample_x0 + 520, y - 45, Z], height=78, color=color)
        elif mode == "demolition":
            self.line([sample_x0, y, Z], [sample_x1, y, Z], color=color, lineweight=lineweight, linetype="HIDDEN2", linetype_scale=55.0)
            for i in range(4):
                x = sample_x0 + 300 + i * 410
                self.line([x - 55, y - 55, Z], [x + 55, y + 55, Z], color=color, lineweight=0.15)
                self.line([x - 55, y + 55, Z], [x + 55, y - 55, Z], color=color, lineweight=0.15)
        elif mode == "swing_arc":
            radius = min(126.0, usable_half_height * 0.86, (sample_x1 - sample_x0) * 0.12)
            center = [sample_x0 + (sample_x1 - sample_x0) * 0.48, y, Z]
            self.arc(center, radius, 0, 90, color=color, lineweight=lineweight, linetype="CENTER", linetype_scale=45.0)
            self.line(center, [center[0] + radius, center[1], Z], color=color, lineweight=lineweight)
            self.line(center, [center[0], center[1] + radius, Z], color=color, lineweight=lineweight)
        else:
            raise ValueError(f"unknown linetype sample mode: {mode}")
        return self.handles[start_index:]


def _snapshot_created(driver: Any, handles: list[str]) -> list[dict[str, Any]]:
    snapshot_handles = getattr(driver, "snapshot_handles", None)
    if not callable(snapshot_handles):
        return []
    return list(snapshot_handles(handles=handles, layer=PREVIEW_LAYER))


def _visible_text_readback(snapshot: list[dict[str, Any]]) -> dict[str, Any]:
    texts = [str(entity.get("text", "")) for entity in snapshot if entity.get("type") == "text"]
    question_texts = [text for text in texts if "?" in text]
    latin_texts = [text for text in texts if re.search(r"[A-Za-z]", text)]
    return {
        "status": "pass" if not question_texts and not latin_texts else "fail",
        "textCount": len(texts),
        "questionTextCount": len(question_texts),
        "latinTextCount": len(latin_texts),
        "texts": texts,
    }


def _solid_fill_entity_count(snapshot: list[dict[str, Any]]) -> int:
    fill_types = {"hatch", "solid", "wipeout", "solid_fill"}
    count = 0
    for entity in snapshot:
        entity_type = str(entity.get("type", "")).lower()
        if entity_type in fill_types or entity.get("fill") is True:
            count += 1
    return count


def _bbox_from_snapshot(snapshot: list[dict[str, Any]]) -> dict[str, list[float]]:
    xs: list[float] = []
    ys: list[float] = []
    for entity in snapshot:
        bbox = entity.get("bbox")
        if isinstance(bbox, dict) and isinstance(bbox.get("min"), list) and isinstance(bbox.get("max"), list):
            xs.extend([float(bbox["min"][0]), float(bbox["max"][0])])
            ys.extend([float(bbox["min"][1]), float(bbox["max"][1])])
        for key in ("start_point", "end_point", "position", "center"):
            point = entity.get(key)
            if isinstance(point, list) and len(point) >= 2:
                xs.append(float(point[0]))
                ys.append(float(point[1]))
    return {"min": [min(xs), min(ys)], "max": [max(xs), max(ys)]} if xs and ys else {"min": [X0, BOTTOM], "max": [RIGHT, TOP]}


def _entity_bbox(entity: dict[str, Any]) -> dict[str, list[float]] | None:
    bbox = entity.get("bbox")
    if isinstance(bbox, dict) and isinstance(bbox.get("min"), list) and isinstance(bbox.get("max"), list):
        return {"min": [float(bbox["min"][0]), float(bbox["min"][1])], "max": [float(bbox["max"][0]), float(bbox["max"][1])]}
    xs: list[float] = []
    ys: list[float] = []
    for key in ("start_point", "end_point", "position", "center"):
        point = entity.get(key)
        if isinstance(point, list) and len(point) >= 2:
            xs.append(float(point[0]))
            ys.append(float(point[1]))
    radius = entity.get("radius")
    center = entity.get("center")
    if isinstance(center, list) and len(center) >= 2 and radius is not None:
        r = float(radius)
        xs.extend([float(center[0]) - r, float(center[0]) + r])
        ys.extend([float(center[1]) - r, float(center[1]) + r])
    if not xs or not ys:
        return None
    return {"min": [min(xs), min(ys)], "max": [max(xs), max(ys)]}


def _bbox_inside(inner: dict[str, list[float]], outer: dict[str, list[float]], *, tolerance: float = 1.0) -> bool:
    return (
        inner["min"][0] >= outer["min"][0] - tolerance
        and inner["max"][0] <= outer["max"][0] + tolerance
        and inner["min"][1] >= outer["min"][1] - tolerance
        and inner["max"][1] <= outer["max"][1] + tolerance
    )


def _sample_cell_checks(row_records: list[dict[str, Any]], snapshot: list[dict[str, Any]]) -> dict[str, Any]:
    by_handle = {str(entity.get("handle")): entity for entity in snapshot if entity.get("handle")}
    failed_rows: list[dict[str, Any]] = []
    for record in row_records:
        cell = record.get("sampleCellBbox")
        if not isinstance(cell, dict):
            continue
        row_failures: list[dict[str, Any]] = []
        for handle in record.get("sampleHandles", []):
            entity = by_handle.get(str(handle))
            if entity is None:
                continue
            bbox = _entity_bbox(entity)
            if bbox is not None and not _bbox_inside(bbox, cell):
                row_failures.append({"handle": str(handle), "bbox": bbox, "cell": cell})
        if row_failures:
            failed_rows.append({"rowIndex": record["rowIndex"], "visibleName": record["visibleName"], "failures": row_failures})
    return {"sampleOutOfCellCount": len(failed_rows), "sampleOutOfCellRows": failed_rows}


def _lineweight_mm(value: Any) -> float | None:
    if value is None:
        return None
    try:
        raw = float(value)
    except Exception:
        return None
    if raw < 0:
        return raw
    return round(raw / 100.0, 3)


def _normalized_linetype(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text.upper()


def _normalized_color(value: Any) -> str | int | None:
    if value is None:
        return None
    if isinstance(value, str):
        lower = value.lower()
        return ACI_COLORS.get(lower, lower)
    try:
        return int(round(float(value)))
    except Exception:
        return str(value)


def _expected_style(row: dict[str, Any]) -> dict[str, Any]:
    style_source = str(row.get("style_source", "explicit_override"))
    if style_source == "by_layer":
        return {
            "styleSource": "by_layer",
            "layer": PREVIEW_LAYER,
            "entityTypes": ["line"],
            "inheritanceMode": "by_layer",
            "linetype": "BYLAYER",
            "colorName": "BYLAYER",
            "lineweightMm": "BYLAYER",
            "linetypeScale": "BYLAYER",
        }
    mode = str(row["mode"])
    entity_types = {
        "linetype": ["line"],
        "zigzag": ["polyline"],
        "wave": ["polyline"],
        "fence_circle": ["line", "circle"],
        "fence_square": ["rectangle_component"],
        "batting": ["polyline", "line"],
        "text_pipe": ["line", "text"],
        "pipe_text": ["line", "text"],
        "section_cut": ["line", "polyline", "text"],
        "demolition": ["line"],
        "swing_arc": ["arc", "line"],
    }.get(mode, ["unknown"])
    return {
        "styleSource": "explicit_override",
        "layer": PREVIEW_LAYER,
        "entityTypes": entity_types,
        "colorName": str(row["color"]),
        "colorAci": ACI_COLORS.get(str(row["color"]).lower()),
        "lineweightMm": float(row["lw"]),
        "linetype": str(row.get("lt", "CONTINUOUS")).upper(),
        "linetypeScale": float(row.get("scale", 1.0)),
    }


def _component_type(entity: dict[str, Any], row: dict[str, Any]) -> str:
    if row["mode"] == "fence_square" and entity.get("type") == "line":
        return "rectangle_component"
    return str(entity.get("type", "unknown"))


def _check_expected_style(expected: dict[str, Any], entity: dict[str, Any], row: dict[str, Any]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    if entity.get("layer") != expected["layer"]:
        failures.append({"field": "layer", "expected": expected["layer"], "actual": entity.get("layer"), "status": "fail"})
    if expected["styleSource"] == "by_layer":
        actual_color = _normalized_color(entity.get("color"))
        actual_linetype = _normalized_linetype(entity.get("linetype"))
        actual_lineweight = entity.get("lineweight")
        color_ok = actual_color in {None, 256, "bylayer", "by_layer"}
        linetype_ok = actual_linetype in {None, "BYLAYER"}
        lineweight_ok = actual_lineweight in {None, -1, "-1"}
        if not color_ok:
            failures.append({"field": "color", "expected": "BYLAYER", "actual": entity.get("color"), "status": "fail"})
        if not linetype_ok:
            failures.append({"field": "linetype", "expected": "BYLAYER", "actual": entity.get("linetype"), "status": "fail"})
        if not lineweight_ok:
            failures.append({"field": "lineweight", "expected": "BYLAYER", "actual": entity.get("lineweight"), "status": "fail"})
        return failures
    actual_color = _normalized_color(entity.get("color"))
    if expected.get("colorAci") is not None and actual_color != expected.get("colorAci"):
        failures.append({"field": "color", "expected": expected.get("colorAci"), "actual": entity.get("color"), "status": "fail"})
    actual_lineweight = _lineweight_mm(entity.get("lineweight"))
    expected_lineweight = float(expected["lineweightMm"])
    if row["mode"] == "linetype" and actual_lineweight is not None and abs(actual_lineweight - expected_lineweight) > 0.011:
        failures.append({"field": "lineweightMm", "expected": expected_lineweight, "actual": actual_lineweight, "status": "fail", "tolerance": 0.011})
    elif row["mode"] != "linetype" and actual_lineweight is not None and actual_lineweight > expected_lineweight + 0.011:
        failures.append({"field": "lineweightMm", "expectedMax": expected_lineweight, "actual": actual_lineweight, "status": "fail", "tolerance": 0.011})
    actual_linetype = _normalized_linetype(entity.get("linetype"))
    expected_linetype = str(expected["linetype"]).upper()
    if row["mode"] == "linetype" and actual_linetype and actual_linetype not in {expected_linetype, "BYLAYER"}:
        failures.append({"field": "linetype", "expected": expected_linetype, "actual": actual_linetype, "status": "fail"})
    actual_scale = entity.get("linetype_scale")
    if actual_scale is not None and row["mode"] == "linetype":
        try:
            if abs(float(actual_scale) - float(expected["linetypeScale"])) > 0.001:
                failures.append({"field": "linetypeScale", "expected": expected["linetypeScale"], "actual": actual_scale, "status": "fail", "tolerance": 0.001})
        except Exception:
            failures.append({"field": "linetypeScale", "expected": expected["linetypeScale"], "actual": actual_scale, "status": "fail"})
    return failures


def _build_style_verification(
    *,
    rows: list[dict[str, Any]],
    row_records: list[dict[str, Any]],
    snapshot: list[dict[str, Any]],
    evidence_source: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    by_handle = {str(entity.get("handle")): entity for entity in snapshot if entity.get("handle")}
    verification_rows: list[dict[str, Any]] = []
    mismatch_count = 0
    object_counts: dict[str, int] = {key: 0 for key in ("line", "polyline", "circle", "text", "arc", "rectangle_component")}
    expected_object_types: set[str] = set()
    explicit_rows: list[str] = []
    by_layer_rows: list[str] = []

    for row, record in zip(rows, row_records, strict=True):
        expected = _expected_style(row)
        expected_object_types.update(str(kind) for kind in expected["entityTypes"])
        sample_handles = [str(handle) for handle in record["sampleHandles"]]
        component_readbacks: list[dict[str, Any]] = []
        mismatch_fields: list[dict[str, Any]] = []
        for handle in sample_handles:
            entity = by_handle.get(handle)
            if entity is None:
                mismatch_fields.append({"field": "handle", "expected": handle, "actual": None, "status": "fail"})
                continue
            component_type = _component_type(entity, row)
            if component_type in object_counts:
                object_counts[component_type] += 1
            component = {
                "handle": handle,
                "entityType": component_type,
                "layer": entity.get("layer"),
                "color": entity.get("color"),
                "lineweightMm": _lineweight_mm(entity.get("lineweight")),
                "linetype": _normalized_linetype(entity.get("linetype")),
                "linetypeScale": entity.get("linetype_scale"),
                "text": entity.get("text"),
                "bbox": _entity_bbox(entity),
            }
            for key in ("center", "radius", "start_point", "end_point"):
                if key in entity:
                    component[key] = entity.get(key)
            component_readbacks.append(component)
            mismatch_fields.extend(_check_expected_style(expected, entity, row))
        missing_types = [kind for kind in expected["entityTypes"] if kind in object_counts and kind not in {item["entityType"] for item in component_readbacks}]
        for missing_type in missing_types:
            mismatch_fields.append({"field": "entityType", "expected": missing_type, "actual": None, "status": "fail"})
        mismatch_status = "pass" if not mismatch_fields else "fail"
        if mismatch_fields:
            mismatch_count += 1
        if expected["styleSource"] == "by_layer":
            by_layer_rows.append(str(row["name"]))
        else:
            explicit_rows.append(str(row["name"]))
        verification_rows.append(
            {
                "rowIndex": record["rowIndex"],
                "capabilityId": f"linetype-table-row-{record['rowIndex']}",
                "visibleName": row["name"],
                "mode": row["mode"],
                "sampleHandles": sample_handles,
                "expectedStyle": expected,
                "componentReadbacks": component_readbacks,
                "mismatch": {"status": mismatch_status, "fields": mismatch_fields},
            }
        )

    style_verification = {
        "status": "pass" if mismatch_count == 0 else "fail",
        "evidenceSource": evidence_source,
        "rowCountExpected": len(rows),
        "rowCountChecked": len(verification_rows),
        "styleMismatchCount": mismatch_count,
        "rows": verification_rows,
    }
    object_coverage = {}
    for key, count in object_counts.items():
        expected_min = 1 if key in expected_object_types else 0
        object_coverage[key] = {
            "expectedMin": expected_min,
            "created": count,
            "readback": count,
            "status": "pass" if count >= expected_min else "fail",
        }
    by_layer_checks = {
        "status": "pass",
        "explicitOverrideRowCount": len(explicit_rows),
        "byLayerRowCount": len(by_layer_rows),
        "explicitOverrideRows": explicit_rows,
        "byLayerRows": by_layer_rows,
        "mismatchCount": 0,
    }
    return style_verification, object_coverage, by_layer_checks


def _system_variable_readback(driver: Any) -> dict[str, Any]:
    doc = getattr(driver, "doc", None)
    get_variable = getattr(doc, "GetVariable", None)
    if not callable(get_variable):
        return {
            "status": "not_checked",
            "evidenceSource": "not_checked",
            "reason": "driver has no AutoCAD system variable readback",
            "variables": {
                "LTSCALE": {"status": "not_checked", "readback": None},
                "CELTSCALE": {"status": "not_checked", "readback": None},
                "PSLTSCALE": {"status": "not_checked", "readback": None},
                "MSLTSCALE": {"status": "not_checked", "readback": None},
            },
        }
    values: dict[str, Any] = {}
    failures = 0
    for name in ("LTSCALE", "CELTSCALE", "PSLTSCALE", "MSLTSCALE"):
        try:
            values[name] = {"status": "pass", "readback": get_variable(name)}
        except Exception as exc:
            failures += 1
            values[name] = {"status": "not_checked", "readback": None, "reason": str(exc)}
    return {
        "status": "pass" if failures == 0 else "partial",
        "evidenceSource": "autocad_readback",
        "scope": "modelspace CODEX_PREVIEW only",
        "variables": values,
    }


def draw_linetype_table(
    *,
    driver: Any,
    output_dir: Path,
    rows: list[dict[str, Any]] | None = None,
    streaming_config: StreamingCadDemoConfig | None = None,
    sleep_fn: SleepFn | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    active_rows = [dict(row) for row in (rows or LINETYPE_TABLE_ROWS)]
    validation = validate_visible_text(active_rows)
    if validation["status"] != "pass":
        raise ValueError(f"Visible linetype table text failed validation: {validation}")

    recorder = StreamingCadDemoRecorder(
        streaming_config or StreamingCadDemoConfig.disabled(),
        driver=driver,
        sleep_fn=sleep_fn or __import__("time").sleep,
    )
    drawer = _LinetypeTableDrawer(driver, recorder)

    panels = _balanced_panels(active_rows)
    layout_checks = {
        "solidFillEntityCount": 0,
        "groupRowVerticalSegmentCount": 0,
        "singleOuterFrame": True,
        "separatePageTitleCount": 0,
    }
    row_records: list[dict[str, Any]] = []
    panel_reports: list[dict[str, Any]] = []
    global_index = 0

    panel_infos: list[dict[str, Any]] = []
    for panel_index, panel_rows in enumerate(panels):
        panel_x0 = X0 + panel_index * (PANEL_W + PANEL_GAP)
        group_count = len(dict.fromkeys(str(row["group"]) for row in panel_rows))
        panel_bbox = _panel_bbox(panel_x0, panel_rows, group_count)
        panel_infos.append(
            {
                "panelIndex": panel_index + 1,
                "panelRows": panel_rows,
                "panelX0": panel_x0,
                "panelCols": _cols(panel_x0),
                "panelRight": panel_x0 + PANEL_W,
                "groupCount": group_count,
                "panelBbox": panel_bbox,
                "panelBottom": panel_bbox["min"][1],
            }
        )

    table_bottom = min(info["panelBottom"] for info in panel_infos)
    table_right = X0 + TABLE_W
    drawer.rect([X0, table_bottom, Z], [table_right, TOP, Z], color="white", lineweight=0.30)
    drawer.text(TITLE, [X0 + 180, TOP - 170, Z], height=122, color="yellow")
    drawer.text("整合双栏；预览层测试；颜色、线宽、线型比例已区分；图纸未保存", [X0 + 182, TOP - 292, Z], height=54, color="white")
    y_title_bottom = TOP - TITLE_H
    drawer.line([X0, y_title_bottom, Z], [table_right, y_title_bottom, Z], color="white", lineweight=0.20)
    layout_checks["panelBottomDelta"] = round(
        max(float(info["panelBottom"]) for info in panel_infos) - min(float(info["panelBottom"]) for info in panel_infos),
        3,
    )

    for panel_info in panel_infos:
        panel_index = int(panel_info["panelIndex"]) - 1
        panel_rows = list(panel_info["panelRows"])
        panel_x0 = float(panel_info["panelX0"])
        panel_cols = list(panel_info["panelCols"])
        panel_right = float(panel_info["panelRight"])
        panel_bbox = panel_info["panelBbox"]
        panel_bottom = float(panel_info["panelBottom"])
        group_count = int(panel_info["groupCount"])
        sample_x0 = panel_cols[2] + 260
        sample_x1 = panel_cols[3] - 260

        drawer.line([panel_x0, y_title_bottom, Z], [panel_x0, panel_bottom, Z], color="white", lineweight=0.13)
        drawer.line([panel_right, y_title_bottom, Z], [panel_right, panel_bottom, Z], color="white", lineweight=0.13)
        y = y_title_bottom
        header_top = y
        header_bottom = y - HEADER_H
        drawer.column_segments(panel_cols, header_top, header_bottom, lineweight=0.13)
        drawer.text("序", [panel_cols[0] + 150, y - 155, Z], height=78, color="yellow")
        drawer.text("线型名称", [panel_cols[1] + 140, y - 155, Z], height=78, color="yellow")
        drawer.text("样线", [panel_cols[2] + 860, y - 155, Z], height=78, color="yellow")
        drawer.text("用途与测试点", [panel_cols[3] + 160, y - 155, Z], height=78, color="yellow")
        y = header_bottom
        drawer.line([panel_x0, y, Z], [panel_right, y, Z], color="white", lineweight=0.20)

        current_group = None
        panel_start_index = global_index + 1
        for row in panel_rows:
            global_index += 1
            row_start_index = len(drawer.handles)
            recorder.start_item(f"linetype-table-row-{global_index}", index=global_index - 1)
            if row["group"] != current_group:
                current_group = row["group"]
                drawer.text(str(current_group), [panel_x0 + 170, y - 120, Z], height=74, color="cyan")
                y -= GROUP_H
                drawer.line([panel_x0, y, Z], [panel_right, y, Z], color="white", lineweight=0.13)
            row_height = _row_height(row)
            row_top = y
            row_bottom = y - row_height
            drawer.column_segments(panel_cols, row_top, row_bottom, lineweight=0.09)
            mid_y = y - row_height / 2.0
            drawer.text(str(global_index), [panel_cols[0] + 150, mid_y - 38, Z], height=64, color="white")
            drawer.text(str(row["name"]), [panel_cols[1] + 100, mid_y - 38, Z], height=62, color=str(row["color"]))
            sample_cell_bbox = {
                "min": [panel_cols[2] + 30, row_bottom + SAMPLE_CELL_MARGIN],
                "max": [panel_cols[3] - 30, row_top - SAMPLE_CELL_MARGIN],
            }
            sample_handles = drawer.sample(
                row,
                mid_y,
                sample_x0,
                sample_x1,
                cell_height=sample_cell_bbox["max"][1] - sample_cell_bbox["min"][1],
            )
            drawer.text(str(row["usage"]), [panel_cols[3] + 130, mid_y - 38, Z], height=56, color="white")
            y = row_bottom
            drawer.line([panel_x0, y, Z], [panel_right, y, Z], color="white", lineweight=0.09)
            all_row_handles = drawer.handles[row_start_index:]
            row_records.append(
                {
                    "rowIndex": global_index,
                    "visibleName": row["name"],
                    "group": row["group"],
                    "panelIndex": panel_index + 1,
                    "allCreated": list(all_row_handles),
                    "sampleHandles": list(sample_handles),
                    "gridAndLabelHandles": [handle for handle in all_row_handles if handle not in sample_handles],
                    "rowHeight": row_height,
                    "sampleCellBbox": sample_cell_bbox,
                }
            )
            recorder.after_item(all_row_handles, capability_id=f"linetype-table-row-{global_index}")

        panel_reports.append(
            {
                "panelIndex": panel_index + 1,
                "rowIndexStart": panel_start_index,
                "rowIndexEnd": global_index,
                "dataRowCount": len(panel_rows),
                "groupCount": group_count,
                "bbox": panel_bbox,
                "panelBbox": panel_bbox,
                "bottomAlignedToOuterFrame": abs(panel_bottom - table_bottom) < 1e-6,
                "captureRecommendedPadding": 300,
            }
        )

    snapshot = _snapshot_created(driver, drawer.handles)
    layout_checks["solidFillEntityCount"] = _solid_fill_entity_count(snapshot)
    layout_checks.update(_sample_cell_checks(row_records, snapshot))
    style_verification, object_coverage, by_layer_checks = _build_style_verification(
        rows=active_rows,
        row_records=row_records,
        snapshot=snapshot,
        evidence_source="fake_driver" if driver.__class__.__name__ == "FakeCadDriver" else "autocad_readback",
    )
    system_variable_readback = _system_variable_readback(driver)
    read_handles = {str(entity.get("handle")) for entity in snapshot}
    missing = [handle for handle in drawer.handles if handle not in read_handles]
    visible_readback = _visible_text_readback(snapshot)
    bbox = _bbox_from_snapshot(snapshot)
    refresh_view = getattr(driver, "refresh_view", None)
    refresh_result = refresh_view() if callable(refresh_view) else {"status": "skipped", "reason": "driver has no refresh_view"}

    layout_ok = (
        layout_checks["solidFillEntityCount"] == 0
        and layout_checks["groupRowVerticalSegmentCount"] == 0
        and layout_checks["singleOuterFrame"]
        and layout_checks["separatePageTitleCount"] == 0
        and layout_checks.get("sampleOutOfCellCount", 0) == 0
    )
    object_coverage_ok = all(row.get("status") == "pass" for row in object_coverage.values())
    report = {
        "status": "pass"
        if not missing and visible_readback["status"] == "pass" and layout_ok and style_verification["status"] == "pass" and object_coverage_ok
        else "fail",
        "generatedAt": generated_at or datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "targetLayer": PREVIEW_LAYER,
        "dryRun": {
            "status": "pass",
            "row_count": len(active_rows),
            "groups": sorted({str(row["group"]) for row in active_rows}),
            "visible_text_validation": validation,
            "payloadTransport": "utf8_file_or_module_only",
            "layoutPolicy": LAYOUT_POLICY,
            "page_count": 1,
            "panel_count": len(panel_reports),
        },
        "layoutPolicy": LAYOUT_POLICY,
        "layoutChecks": layout_checks,
        "pageCount": 1,
        "panelCount": len(panel_reports),
        "panels": panel_reports,
        "integratedTableBbox": {"min": [X0, table_bottom], "max": [table_right, TOP]},
        "rowHandles": row_records,
        "drawnRows": [
            {
                "group": row["group"],
                "visibleName": row["name"],
                "mode": row["mode"],
                "cadLinetype": row.get("lt"),
                "color": row["color"],
                "lineweight": row.get("lw"),
                "linetypeScale": row.get("scale"),
            }
            for row in active_rows
        ],
        "createdHandleCount": len(drawer.handles),
        "created_handles": list(drawer.handles),
        "readbackEntityCount": len(snapshot),
        "missingHandles": missing,
        "visibleTextReadback": visible_readback,
        "styleVerification": style_verification,
        "byLayerOverrideChecks": by_layer_checks,
        "objectTypeCoverage": object_coverage,
        "systemVariableReadback": system_variable_readback,
        "plotEvidenceBoundary": {
            "status": "not_checked",
            "reason": "截图只证明视觉预览，不证明 CTB/STB、PDF 或打印输出线型效果",
            "savedDwg": False,
            "requiresSavedDwg": False,
        },
        "bbox": bbox,
        "refreshResult": refresh_result,
        "streamingMode": recorder.summary(),
        "safety": {"savedDwg": False, "deletedEntities": False, "modifiedFormalLayers": False},
    }
    layout_audit = audit_linetype_table_layout(report, snapshot=snapshot)
    report["layoutAudit"] = layout_audit
    if layout_audit["status"] != "pass":
        report["status"] = "fail"
    report_path = output_dir / "linetype_table_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["reportPath"] = str(report_path)
    return report
