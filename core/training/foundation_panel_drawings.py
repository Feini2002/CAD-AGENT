"""Panel drawing helpers for CAD foundation batch training."""

from __future__ import annotations

from typing import Any

from core.plan_engine.block_alpha_plan import CONTROLLED_BLOCK_ID, CONTROLLED_BLOCK_NAME
from core.safety.policy import PREVIEW_LAYER
from core.training.streaming_demo import StreamingCadDemoRecorder


PANEL_WIDTH = 2200.0
PANEL_HEIGHT = 1180.0
PANEL_GAP = 260.0
PANEL_COLUMNS = 3

PANEL_TITLE_OVERRIDES = {
    "cad-handle-bbox-report": "句柄与边界框报告",
}

DEFAULT_HATCH_SAMPLES = [
    ("ANSI31", 0.45, "斜线细"),
    ("ANSI31", 1.1, "斜线粗"),
    ("ANSI32", 0.8, "斜交线"),
    ("ANSI37", 0.75, "网格线"),
    ("AR-CONC", 0.7, "混凝土"),
    ("BRICK", 0.65, "砖纹"),
    ("GRAVEL", 0.55, "碎石"),
    ("EARTH", 0.6, "土壤"),
]

SOLID_HATCH_SAMPLES = [
    ("SOLID", 1.0, "全填充一"),
    ("SOLID", 1.0, "全填充二"),
    ("SOLID", 1.0, "全填充三"),
    ("SOLID", 1.0, "全填充四"),
    ("SOLID", 1.0, "全填充五"),
    ("SOLID", 1.0, "全填充六"),
    ("SOLID", 1.0, "全填充七"),
    ("SOLID", 1.0, "全填充八"),
]

LINEWEIGHT_STANDARD_SAMPLES = [
    {
        "label": "粗线墙体",
        "lineweight": 70,
        "linetype": "Continuous",
        "linetype_scale": 1.0,
        "note": "零点七毫米 连续线",
    },
    {
        "label": "中线家具",
        "lineweight": 35,
        "linetype": "CENTER",
        "linetype_scale": 25.0,
        "note": "零点三五毫米 中心线",
    },
    {
        "label": "细线标注",
        "lineweight": 13,
        "linetype": "DASHED",
        "linetype_scale": 25.0,
        "note": "零点一三毫米 虚线",
    },
]


def _handles_from_result(result: Any) -> list[str]:
    if not isinstance(result, dict):
        return []
    handles: list[str] = []
    for key in ("created_handles", "handles", "boundary_handles"):
        value = result.get(key)
        if isinstance(value, list):
            handles.extend(str(item) for item in value if item)
    handle = result.get("handle")
    if handle:
        handles.append(str(handle))
    return list(dict.fromkeys(handles))


class PanelDrawer:
    def __init__(
        self,
        driver: Any,
        streaming_recorder: StreamingCadDemoRecorder | None = None,
    ) -> None:
        self.driver = driver
        self.streaming_recorder = streaming_recorder
        self.handles: list[str] = []

    def add(self, result: Any, *, operation: str) -> Any:
        before = set(self.handles)
        self.handles.extend(_handles_from_result(result))
        self.handles = list(dict.fromkeys(self.handles))
        created_handles = [handle for handle in self.handles if handle not in before]
        if self.streaming_recorder is not None:
            self.streaming_recorder.after_operation(
                operation=operation,
                created_handles=created_handles,
            )
        return result

    def line(self, start: list[float], end: list[float], **kwargs: Any) -> Any:
        return self.add(
            self.driver.draw_line(start_point=start, end_point=end, layer=PREVIEW_LAYER, **kwargs),
            operation="line",
        )

    def rect(self, p1: list[float], p2: list[float], **kwargs: Any) -> Any:
        return self.add(
            self.driver.draw_rectangle(corner1=p1, corner2=p2, layer=PREVIEW_LAYER, **kwargs),
            operation="rect",
        )

    def circle(self, center: list[float], radius: float, **kwargs: Any) -> Any:
        return self.add(
            self.driver.draw_circle(center=center, radius=radius, layer=PREVIEW_LAYER, **kwargs),
            operation="circle",
        )

    def arc(self, center: list[float], radius: float, start: float, end: float, **kwargs: Any) -> Any:
        return self.add(
            self.driver.draw_arc(
                center=center,
                radius=radius,
                start_angle=start,
                end_angle=end,
                layer=PREVIEW_LAYER,
                **kwargs,
            ),
            operation="arc",
        )

    def polyline(self, points: list[list[float]], *, closed: bool = False, **kwargs: Any) -> Any:
        return self.add(
            self.driver.draw_polyline(points=points, closed=closed, layer=PREVIEW_LAYER, **kwargs),
            operation="polyline",
        )

    def text(self, text: str, position: list[float], *, height: float = 90.0, **kwargs: Any) -> Any:
        return self.add(
            self.driver.draw_text(text=text, position=position, height=height, layer=PREVIEW_LAYER, **kwargs),
            operation="text",
        )

    def dimension(self, start: list[float], end: list[float], text_position: list[float], **kwargs: Any) -> Any:
        return self.add(
            self.driver.add_dimension(
                start_point=start,
                end_point=end,
                text_position=text_position,
                layer=PREVIEW_LAYER,
                **kwargs,
            ),
            operation="dimension",
        )

    def hatch(self, boundary: list[list[float]], *, pattern: str = "ANSI31", scale: float = 1.0) -> Any:
        result = self.driver.draw_hatch(boundary_points=boundary, pattern=pattern, scale=scale, layer=PREVIEW_LAYER)
        self.add(result, operation="hatch")
        if not _handles_from_result(result):
            self.polyline(boundary, closed=True)
        return result

    def block(self, base_point: list[float], *, rotation: float = 0, scale: list[float] | None = None) -> Any:
        return self.add(
            self.driver.insert_block_alpha(
                block_id=CONTROLLED_BLOCK_ID,
                block_name=CONTROLLED_BLOCK_NAME,
                base_point=base_point,
                rotation=rotation,
                scale=scale or [0.42, 0.42, 0.42],
                layer=PREVIEW_LAYER,
            ),
            operation="block",
        )


def _hatch_samples(options: dict[str, Any] | None = None) -> list[tuple[str, float, str]]:
    options = options or {}
    if options.get("hatch_full_fill"):
        return list(SOLID_HATCH_SAMPLES)
    pattern_focus = str(options.get("hatch_pattern_focus") or "").strip()
    raw_scales = options.get("hatch_scales")
    if pattern_focus and isinstance(raw_scales, list) and raw_scales:
        samples: list[tuple[str, float, str]] = []
        for sample_index, raw_scale in enumerate(raw_scales[:10], start=1):
            samples.append((pattern_focus, float(raw_scale), f"比例{sample_index}"))
        return samples
    return list(DEFAULT_HATCH_SAMPLES)


def draw_foundation_item(
    driver: Any,
    item: dict[str, Any],
    index: int,
    origin: list[float],
    *,
    options: dict[str, Any] | None = None,
    streaming_recorder: StreamingCadDemoRecorder | None = None,
) -> list[str]:
    drawer = PanelDrawer(driver, streaming_recorder=streaming_recorder)
    x, y, z = origin
    cid = item["capabilityId"]
    display_number = int(item.get("displayIndex", index + 11))
    title = f"{display_number:02d} {PANEL_TITLE_OVERRIDES.get(cid, item['name'])}"
    drawer.rect([x, y, z], [x + PANEL_WIDTH, y - PANEL_HEIGHT, z])
    drawer.text(title, [x + 70, y - 150, z], height=95)
    drawer.text("已检查：句柄 / 边界框 / 图层 / 中文标注", [x + 70, y - PANEL_HEIGHT + 150, z], height=62)

    left = x + 180
    top = y - 300
    bottom = y - 860
    if cid == "cad-primitives":
        drawer.line([left, top, z], [left + 520, top - 220, z])
        drawer.rect([left + 660, top, z], [left + 1120, top - 300, z])
        drawer.circle([left + 1450, top - 170, z], 140)
        drawer.arc([left + 1780, top - 220, z], 150, 20, 250)
        drawer.polyline([[left, top - 470, z], [left + 420, top - 650, z], [left + 760, top - 470, z]], closed=False)
        drawer.text("线 / 矩形 / 圆 / 圆弧 / 多段线", [left, bottom, z], height=70)
    elif cid == "cad-selection-edit":
        drawer.rect([left, top, z], [left + 420, top - 280, z])
        drawer.rect([left + 650, top, z], [left + 1070, top - 280, z])
        drawer.line([left + 470, top - 140, z], [left + 610, top - 140, z])
        drawer.rect([left + 1280, top, z], [left + 1680, top - 280, z])
        drawer.line([left + 1280, top - 360, z], [left + 1680, top - 360, z])
        drawer.text("选择 / 移动 / 复制 / 删除边界", [left, bottom, z], height=70)
    elif cid == "cad-transform":
        drawer.rect([left, top, z], [left + 440, top - 280, z])
        drawer.rect([left + 650, top - 80, z], [left + 1080, top - 360, z])
        drawer.line([left + 1240, top, z], [left + 1240, top - 520, z])
        drawer.rect([left + 1340, top, z], [left + 1680, top - 240, z])
        drawer.rect([left + 1780, top, z], [left + 1950, top - 120, z])
        drawer.text("旋转 / 镜像 / 缩放基点", [left, bottom, z], height=70)
    elif cid == "cad-offset-trim":
        drawer.rect([left, top, z], [left + 520, top - 360, z])
        drawer.rect([left + 85, top - 85, z], [left + 435, top - 275, z])
        drawer.line([left + 760, top, z], [left + 1240, top - 420, z])
        drawer.line([left + 760, top - 420, z], [left + 1240, top, z])
        drawer.line([left + 1040, top - 420, z], [left + 1480, top - 420, z])
        drawer.text("偏移 / 修剪 / 延伸后洁净", [left, bottom, z], height=70)
    elif cid == "cad-layer-discipline":
        drawer.rect([left, top, z], [left + 520, top - 340, z])
        drawer.line([left + 700, top, z], [left + 1300, top - 340, z])
        drawer.circle([left + 1600, top - 180, z], 150)
        drawer.text("只写预览图层；正式图层保护", [left, bottom, z], height=70)
    elif cid == "cad-closure-constraints":
        drawer.polyline([[left, top, z], [left + 520, top, z], [left + 520, top - 380, z], [left, top - 380, z]], closed=True)
        drawer.rect([left + 520, top, z], [left + 1040, top - 380, z])
        drawer.line([left + 1200, top - 80, z], [left + 1580, top - 80, z])
        drawer.line([left + 1200, top - 250, z], [left + 1580, top - 250, z])
        drawer.text("闭合 / 对齐 / 共享边去重", [left, bottom, z], height=70)
    elif cid == "cad-readback-audit":
        drawer.rect([left, top, z], [left + 640, top - 360, z])
        drawer.circle([left + 920, top - 180, z], 150)
        drawer.line([left + 1180, top, z], [left + 1650, top - 360, z])
        drawer.text("句柄回读：类型 / 边界框 / 图层", [left, bottom, z], height=70)
    elif cid == "cad-units-scale":
        drawer.rect([left, top, z], [left + 780, top - 360, z])
        drawer.dimension([left, top - 500, z], [left + 780, top - 500, z], [left + 390, top - 650, z])
        drawer.text("毫米单位 / 图纸比例 / 标注边界", [left + 900, top - 260, z], height=66)
    elif cid == "cad-coordinate-input":
        drawer.line([left, top - 520, z], [left + 1250, top - 520, z])
        drawer.line([left, top - 520, z], [left, top, z])
        for offset in (260, 520, 780, 1040):
            drawer.circle([left + offset, top - 520 + (offset % 520) * 0.35, z], 34)
        drawer.text("绝对坐标 / 相对坐标 / 极坐标点", [left + 160, bottom, z], height=70)
    elif cid == "cad-osnap-ortho-polar":
        drawer.line([left, top - 520, z], [left + 900, top - 520, z])
        drawer.line([left + 450, top - 80, z], [left + 450, top - 780, z])
        drawer.circle([left + 450, top - 520, z], 54)
        drawer.line([left + 1040, top - 520, z], [left + 1580, top - 120, z])
        drawer.text("端点捕捉 / 正交 / 极轴方向", [left, bottom, z], height=70)
    elif cid == "cad-polyline-width-cleanup":
        drawer.polyline([[left, top, z], [left + 620, top, z], [left + 620, top - 360, z], [left, top - 360, z]], closed=True)
        drawer.line([left + 760, top, z], [left + 1280, top - 360, z])
        drawer.text("闭合多段线 + 清理后端点", [left, bottom, z], height=70)
    elif cid == "cad-hatch-boundary":
        hatch_samples = _hatch_samples(options)
        cell = 220.0
        gap_x = 135.0
        gap_y = 105.0
        for sample_index, (pattern, scale, label) in enumerate(hatch_samples):
            col = sample_index % 4
            row = sample_index // 4
            x0 = left + col * (cell + gap_x)
            y0 = top - row * (cell + gap_y)
            boundary = [[x0, y0, z], [x0 + cell, y0, z], [x0 + cell, y0 - cell, z], [x0, y0 - cell, z]]
            drawer.hatch(boundary, pattern=pattern, scale=scale)
            drawer.text(label, [x0 + 12, y0 - cell - 38, z], height=38)
        footer = "全填充与闭合边界测试" if options and options.get("hatch_full_fill") else "常用填充图样与比例对比"
        drawer.text(footer, [left + 1500, top - 45, z], height=46)
    elif cid == "cad-boundary-region":
        drawer.polyline([[left, top, z], [left + 760, top, z], [left + 760, top - 420, z], [left, top - 420, z]], closed=True)
        drawer.text("边界 / 面域面积：已检查", [left + 110, top - 235, z], height=64)
    elif cid == "cad-fillet-chamfer":
        drawer.line([left, top, z], [left + 520, top, z])
        drawer.line([left, top, z], [left, top - 420, z])
        drawer.arc([left + 250, top - 240, z], 210, 0, 90)
        drawer.line([left + 780, top, z], [left + 1180, top - 400, z])
        drawer.text("圆角 / 倒角节点清理", [left, bottom, z], height=70)
    elif cid == "cad-stretch-edit":
        drawer.rect([left, top, z], [left + 430, top - 320, z])
        drawer.rect([left + 620, top, z], [left + 1220, top - 320, z])
        drawer.line([left + 480, top - 160, z], [left + 580, top - 160, z])
        drawer.text("拉伸后保持组合关系", [left, bottom, z], height=70)
    elif cid == "cad-block-insert-attribute":
        drawer.block([left, top - 420, z])
        drawer.text("块属性：编号 A-01 / 已检查", [left + 520, top - 260, z], height=70)
    elif cid == "cad-block-rotate-scale":
        drawer.block([left, top - 470, z], rotation=35, scale=[0.55, 0.55, 0.55])
        drawer.block([left + 760, top - 350, z], rotation=90, scale=[0.35, 0.35, 0.35])
        drawer.text("旋转 / 缩放 / 朝向", [left, bottom, z], height=70)
    elif cid == "cad-xref-underlay-protect":
        drawer.rect([left, top, z], [left + 980, top - 500, z])
        drawer.line([left, top, z], [left + 980, top - 500, z])
        drawer.text("底图引用锁定：不改原图", [left + 70, top - 260, z], height=70)
    elif cid == "cad-layout-viewport":
        drawer.rect([left, top, z], [left + 1080, top - 620, z])
        drawer.rect([left + 130, top - 110, z], [left + 940, top - 480, z])
        drawer.text("布局视口 1:50 已锁定", [left + 190, top - 300, z], height=70)
    elif cid == "cad-plot-scale-titleblock":
        drawer.rect([left, top, z], [left + 1220, top - 650, z])
        drawer.rect([left + 760, top - 470, z], [left + 1220, top - 650, z])
        drawer.text("图框 / 比例 / 标题栏", [left + 790, top - 560, z], height=62)
    elif cid == "cad-redline-revision":
        for offset in range(0, 520, 100):
            drawer.arc([left + offset, top - 260, z], 70, 0, 220)
        drawer.text("红线修订云线 版本A", [left + 650, top - 280, z], height=70)
    elif cid == "cad-layer-lineweight-standard":
        for row, sample in enumerate(LINEWEIGHT_STANDARD_SAMPLES):
            y0 = top - row * 160
            drawer.line(
                [left, y0, z],
                [left + 900, y0, z],
                lineweight=sample["lineweight"],
                linetype=sample["linetype"],
                linetype_scale=sample["linetype_scale"],
            )
            drawer.text(f"{sample['label']} {sample['note']}", [left + 980, y0 - 30, z], height=62)
    elif cid == "cad-selection-by-room":
        drawer.rect([left, top, z], [left + 520, top - 420, z])
        drawer.rect([left + 680, top, z], [left + 1200, top - 420, z])
        drawer.text("只选择客厅预览对象", [left + 80, top - 230, z], height=68)
    elif cid == "cad-array-copy-pattern":
        for col in range(4):
            drawer.circle([left + col * 210, top - 230, z], 70)
        drawer.text("阵列间距 210 毫米", [left, bottom, z], height=70)
    elif cid == "cad-measure-distance-area":
        drawer.rect([left, top, z], [left + 780, top - 420, z])
        drawer.dimension([left, top - 520, z], [left + 780, top - 520, z], [left + 390, top - 650, z])
        drawer.text("面积 / 距离一致", [left + 900, top - 240, z], height=70)
    elif cid == "cad-purge-audit-cleanup":
        drawer.line([left, top, z], [left + 880, top, z])
        drawer.line([left, top - 170, z], [left + 880, top - 170, z])
        drawer.text("审计清理：重复线 0", [left, top - 430, z], height=70)
    elif cid == "cad-dim-style-baseline":
        drawer.rect([left, top, z], [left + 820, top - 380, z])
        drawer.dimension([left, top - 500, z], [left + 820, top - 500, z], [left + 410, top - 650, z], textheight=55)
        drawer.text("尺寸样式基线", [left + 940, top - 260, z], height=70)
    elif cid == "cad-text-mleader-style":
        drawer.line([left, top - 210, z], [left + 430, top - 420, z])
        drawer.circle([left + 430, top - 420, z], 55)
        drawer.text("引线说明：已检查 / 未检查", [left + 500, top - 230, z], height=66)
    elif cid == "cad-handle-bbox-report":
        drawer.rect([left, top, z], [left + 760, top - 420, z])
        drawer.text("边界框最小/最大 + 句柄回读", [left + 80, top - 250, z], height=66)
    elif cid == "cad-layer-pollution-check":
        drawer.rect([left, top, z], [left + 900, top - 420, z])
        drawer.text("正式图层写入被拦截", [left + 110, top - 250, z], height=70)
    elif cid == "cad-safe-undo-rollback":
        drawer.line([left, top, z], [left + 900, top - 360, z])
        drawer.text("失败回滚边界：不删正式实体", [left, top - 520, z], height=70)
    else:
        drawer.circle([left + 260, top - 260, z], 180)
        drawer.text("基础操作训练面板", [left + 560, top - 260, z], height=70)
    return list(drawer.handles)
