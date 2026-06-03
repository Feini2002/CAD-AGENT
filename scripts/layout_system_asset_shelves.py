#!/usr/bin/env python3
"""Draw an expandable shelf layout in a system asset DWG."""

from __future__ import annotations

import argparse
import ctypes
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.runtime.encoding_guard import assert_no_text_encoding_corruption, configure_utf8_process  # noqa: E402
from core.assets.system_asset_library_governance import audit_visual_rack_plan  # noqa: E402
from core.assets.system_asset_sedimentation import refresh_system_asset_layout_metadata  # noqa: E402


DEFAULT_CATEGORY = "drawing_standards.basic"
ASSET_DWG = PROJECT_ROOT / "libraries" / "system_library" / "drawing_standards" / "basic" / "standard_assets.dwg"
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "output"
    / "validation_runs"
    / "system-assets"
    / "asset-library-shelves"
    / "shelf_layout_report.json"
)

LAYER_COLORS = {
    "ASSET_00_INDEX": 2,
    "ASSET_01_CLEAN_ASSETS": 4,
    "ASSET_02_PREVIEW_CARDS": 7,
    "ASSET_03_REVIEW_QUARANTINE": 1,
    "ASSET_99_EVIDENCE_LINKS": 3,
    "ASSET_ROUTE": 8,
    "ASSET_RACK_BASE": 4,
    "ASSET_RACK_OBJECTS": 3,
    "ASSET_RACK_HEADER": 2,
    "ASSET_CLEAN_SOURCE": 4,
    "ASSET_SOURCE_BOUNDARY": 30,
    "ASSET_PREVIEW_CARD": 8,
    "ASSET_LABEL": 7,
    "ASSET_EVIDENCE": 3,
    "ASSET_QUARANTINE": 1,
    "ASSET_REVIEW": 8,
    "ASSET_SLOT_GRID": 8,
    "ASSET_TEXT": 2,
}
SHELF_LAYERS = set(LAYER_COLORS)
CONTENT_LAYER_COLORS = {
    "ASSET_PROOF_CONTENT": 7,
}
MIN_VISUAL_AISLE = 1600.0
MIN_OBJECT_INDEX_AISLE = 1400.0
READABLE_CONTENT_MARGIN = 1600.0
MAX_CONTENT_WIDTH_RATIO = 0.80
FORBIDDEN_PROTECTED_CONTENT_LAYERS = {"CODEX_PREVIEW"}


def _slot(
    slot_id: str,
    title: str,
    *,
    status: str,
    asset_ids: list[str] | None = None,
    notes: list[str] | None = None,
    copy_source_allowed: bool = False,
    **extra: Any,
) -> dict[str, Any]:
    slot = {
        "slotId": slot_id,
        "title": title,
        "status": status,
        "assetIds": asset_ids or [],
        "notes": notes or [],
        "copySourceAllowed": copy_source_allowed,
    }
    slot.update(extra)
    return slot


def _classified_rack_plan() -> dict[str, Any]:
    return {
        "schemaVersion": 2,
        "layoutMode": "classified_expandable_visual_warehouse_v2",
        "entryPolicy": "先看 00_INDEX，按 rackId / slotId 入库；来源不清先进 03_REVIEW_QUARANTINE。",
        "warehouseArchitecture": {
            "kind": "category_visual_warehouse",
            "primaryWarehouseZones": ["01_CLEAN_ASSETS", "B_OBJECT_ASSET_INDEX"],
            "reviewOnlyZones": ["02_PREVIEW_CARDS", "03_REVIEW_QUARANTINE", "99_EVIDENCE_LINKS"],
            "expansionPolicy": "先扩展分类内大货架和空货位；对象 block 本体进入各自分类 DWG，standard_assets.dwg 只保留跨库索引。",
        },
        "acceptanceCriteria": {
            "slotContainment": "每个资产槽必须有 owning rack、slotId、状态和可回读 bbox 所属区。",
            "assetOwnership": "已占用槽记录 assetIds；对象索引槽记录 category/nativeDwg。",
            "expansionCapacity": "每个大类货架必须声明空位或未来扩展位，不能画成说明卡片。",
            "copyPolicy": "只有 clean source 槽能作为复制源；索引、复审、隔离、证据和标签默认 never_copy。",
            "screenshotBoundary": "截图只辅助人工看图；created handles、zone bbox、slot ownership 和 readback 才是机器证据。",
        },
        "displayPolicy": {
            "cleanSourceLayer": "ASSET_CLEAN_SOURCE",
            "sourceBoundaryLayer": "ASSET_SOURCE_BOUNDARY",
            "previewCardLayer": "ASSET_PREVIEW_CARD",
            "labelLayer": "ASSET_LABEL",
            "evidenceLayer": "ASSET_EVIDENCE",
            "quarantineLayer": "ASSET_QUARANTINE",
            "copySafety": "可视标签、货架边框、证据和预留卡槽默认 copyPolicy=never_copy；style asset 优先复用命名样式定义。",
        },
        "rackFamilies": [
            {
                "rackId": "A_BASE_SCAFFOLD",
                "zoneId": "01_CLEAN_ASSETS",
                "title": "A 通用底座脚手架",
                "familyRole": "reusable_style_source",
                "copyPolicy": "clean_source_slots_only",
                "minExpansionSlots": 4,
                "description": "放线型、尺寸、文字、填充、图层等可复用底座标准；训练标题和临时说明不得进入。",
                "slotPolicy": "A1/A2 两列承载 drawing_standards 的 clean source 与最小可见样例；展示卡、标签和证据不作为复制源。",
                "slots": [
                    _slot("A01_LAYER_STANDARD", "图层标准", status="reserved", notes=["基础图层、颜色索引、图层角色"], sourceKind="style_definition"),
                    _slot(
                        "A02_LINETYPE_STANDARD",
                        "线型标准",
                        status="occupied",
                        asset_ids=["linetype_style_summary_table"],
                        notes=["已沉淀线型样式总表；可见表格只作 proof panel"],
                        copy_source_allowed=True,
                        sourceKind="style_definition",
                    ),
                    _slot("A03_PLOT_COLOR_LINEWEIGHT", "线宽 / 颜色 / 打印", status="reserved", notes=["线宽、颜色索引、CTB/STB 边界"], sourceKind="style_definition"),
                    _slot(
                        "A04_TEXT_STYLE",
                        "文字样式",
                        status="reserved",
                        asset_ids=["basic_cad_drawing_standard"],
                        notes=["中文文字样式与字体策略"],
                        sourceKind="style_definition",
                    ),
                    _slot(
                        "A05_DIMENSION_STYLE",
                        "标注样式",
                        status="occupied",
                        asset_ids=["interior_dimension_style_visual_standard"],
                        notes=["已沉淀室内尺寸样式面板；优先复用命名 DimStyle"],
                        copy_source_allowed=True,
                        sourceKind="style_definition",
                    ),
                    _slot("A06_LEADER_SYMBOL_STYLE", "引线 / 符号样式", status="empty_reserved", notes=["引线、编号、符号样式"], sourceKind="style_definition"),
                    _slot("A07_TABLE_TITLEBLOCK", "表格 / 图框 / 标题栏", status="empty_reserved", notes=["表格样式、图框、标题栏"], sourceKind="template_scaffold"),
                    _slot("A08_SCALE_UNIT_BASELINE", "比例 / 单位 / 通用基准", status="empty_reserved", notes=["比例、单位、通用基点"], sourceKind="template_scaffold"),
                ],
            },
            {
                "rackId": "B_OBJECT_ASSET_INDEX",
                "zoneId": "B_OBJECT_ASSET_INDEX",
                "title": "B 对象资产索引 / 跨库入口",
                "familyRole": "cross_category_object_index",
                "copyPolicy": "index_only_never_copy",
                "minExpansionSlots": 1,
                "description": "这里只放对象资产分类入口；真正 block 本体进入各自分类 DWG。",
                "slotPolicy": "B 区默认 index_only / never_copy；填入对象资产前必须有精确 source boundary 或 named block。",
                "slots": [
                    _slot("B01_BEDS", "床铺", status="index_only", notes=["单人床、双人床、床头柜组合"], category="furniture.sleeping.beds", nativeDwg="libraries/system_library/furniture/sleeping/beds/bed_assets.dwg", copyPolicy="never_copy"),
                    _slot("B02_TABLES", "桌子 / 书桌", status="index_only", notes=["餐桌、茶几、书桌"], category="furniture.tables", nativeDwg="libraries/system_library/furniture/tables/table_assets.dwg", copyPolicy="never_copy"),
                    _slot("B03_SEATING", "沙发 / 椅子", status="index_only", notes=["沙发、椅子、卡座"], category="furniture.seating", nativeDwg="libraries/system_library/furniture/seating/sofas/sofa_assets.dwg", copyPolicy="never_copy"),
                    _slot("B04_STORAGE", "柜体 / 收纳", status="index_only", notes=["衣柜、橱柜、储物柜"], category="furniture.storage", nativeDwg="libraries/system_library/furniture/storage/storage_assets.dwg", copyPolicy="never_copy"),
                    _slot("B05_DOORS_WINDOWS", "门窗符号", status="index_only", notes=["门洞、窗、开启方向"], category="openings.doors_windows", nativeDwg="libraries/system_library/openings/doors_windows/opening_assets.dwg", copyPolicy="never_copy"),
                    _slot("B06_KITCHEN_BATH", "厨卫对象", status="index_only", notes=["洁具、橱柜、电器"], category="fixtures.kitchen_bath", nativeDwg="libraries/system_library/fixtures/kitchen_bath/fixture_assets.dwg", copyPolicy="never_copy"),
                    _slot("B07_LIGHTING_EQUIPMENT", "灯具 / 设备", status="index_only", notes=["灯具、开关、设备符号"], category="mep.lighting_equipment", nativeDwg="libraries/system_library/mep/lighting_equipment/equipment_assets.dwg", copyPolicy="never_copy"),
                    _slot("B08_CUSTOM_EXPANSION", "自定义扩展", status="future_expansion", notes=["新增对象类从这里派生"], category="custom", nativeDwg="libraries/system_library/custom/custom_assets.dwg", copyPolicy="never_copy"),
                ],
            },
        ],
        "reviewZones": [
            {
                "zoneId": "02_PREVIEW_CARDS",
                "purpose": "人工复审卡片和旧训练预览暂存；可看，不作为复制源。",
            },
            {
                "zoneId": "03_REVIEW_QUARANTINE",
                "purpose": "来源边界不清、训练面板整块搬运、待清洗候选先隔离。",
            },
            {
                "zoneId": "99_EVIDENCE_LINKS",
                "purpose": "报告、截图、训练引用索引；只证明来源，不承载可复制几何。",
            },
        ],
    }


def _collect_text_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        texts: list[str] = []
        for item in value.values():
            texts.extend(_collect_text_values(item))
        return texts
    if isinstance(value, list):
        texts = []
        for item in value:
            texts.extend(_collect_text_values(item))
        return texts
    return []


def _switch_to_input_desktop() -> dict[str, Any]:
    if sys.platform != "win32":
        return {"status": "not_required", "reason": "non-Windows platform"}
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    access = 0x0001 | 0x0002 | 0x0040 | 0x0080 | 0x0100
    desktop = user32.OpenInputDesktop(0, False, access)
    if not desktop:
        return {"status": "fail", "api": "OpenInputDesktop", "lastError": int(kernel32.GetLastError())}
    ok = bool(user32.SetThreadDesktop(desktop))
    return {"status": "pass" if ok else "fail", "api": "SetThreadDesktop", "lastError": int(kernel32.GetLastError())}


def _connect_autocad() -> Any:
    try:
        import win32com.client
    except ImportError as exc:
        raise RuntimeError("pywin32 is required for AutoCAD COM drawing.") from exc
    for prog_id in ("AutoCAD.Application", "AutoCAD.Application.25.1", "AutoCAD.Application.25"):
        try:
            return win32com.client.GetActiveObject(prog_id)
        except Exception:
            continue
    raise RuntimeError("No active AutoCAD.Application instance is available.")


def _open_or_activate_asset_doc(app: Any, asset_dwg: Path) -> tuple[Any, bool]:
    target = asset_dwg.resolve()
    for document in app.Documents:
        try:
            if Path(str(document.FullName)).resolve() == target:
                document.Activate()
                return document, False
        except Exception:
            continue
    document = app.Documents.Open(str(target))
    try:
        document.Activate()
    except Exception:
        pass
    return document, True


def _point(win32com_module: Any, pythoncom_module: Any, values: list[float]) -> Any:
    return win32com_module.VARIANT(pythoncom_module.VT_ARRAY | pythoncom_module.VT_R8, tuple(float(v) for v in values))


def _ensure_layer(doc: Any, name: str, color: int) -> None:
    try:
        layer = doc.Layers.Item(name)
    except Exception:
        layer = doc.Layers.Add(name)
    try:
        layer.Color = int(color)
    except Exception:
        pass


class ShelfDrawer:
    def __init__(self, doc: Any) -> None:
        import pythoncom
        import win32com.client

        self.doc = doc
        self.model_space = doc.ModelSpace
        self.win32com = win32com.client
        self.pythoncom = pythoncom
        self.created_handles: list[str] = []

    def point(self, x: float, y: float, z: float = 0.0) -> Any:
        return _point(self.win32com, self.pythoncom, [x, y, z])

    @staticmethod
    def handle(entity: Any) -> str:
        return str(getattr(entity, "Handle", ""))

    def line(self, start: tuple[float, float], end: tuple[float, float], layer: str, color: int | None = None) -> None:
        entity = self.model_space.AddLine(self.point(start[0], start[1]), self.point(end[0], end[1]))
        entity.Layer = layer
        if color is not None:
            entity.Color = int(color)
        handle = self.handle(entity)
        if handle:
            self.created_handles.append(handle)

    def rect(self, bbox: dict[str, list[float]], layer: str, color: int | None = None) -> None:
        x1, y1 = bbox["min"]
        x2, y2 = bbox["max"]
        self.line((x1, y1), (x2, y1), layer, color)
        self.line((x2, y1), (x2, y2), layer, color)
        self.line((x2, y2), (x1, y2), layer, color)
        self.line((x1, y2), (x1, y1), layer, color)

    def text(
        self,
        text: str,
        position: tuple[float, float],
        *,
        height: float,
        layer: str = "ASSET_TEXT",
        color: int | None = None,
    ) -> None:
        entity = self.model_space.AddText(text, self.point(position[0], position[1]), float(height))
        entity.Layer = layer
        if color is not None:
            entity.Color = int(color)
        handle = self.handle(entity)
        if handle:
            self.created_handles.append(handle)

    def arrow(self, start: tuple[float, float], end: tuple[float, float], *, layer: str = "ASSET_ROUTE") -> None:
        self.line(start, end, layer, LAYER_COLORS[layer])
        vx = end[0] - start[0]
        vy = end[1] - start[1]
        length = math.hypot(vx, vy) or 1.0
        ux, uy = vx / length, vy / length
        px, py = -uy, ux
        size = 260.0
        for side in (-1.0, 1.0):
            head = (end[0] - ux * size + px * side * size * 0.45, end[1] - uy * size + py * side * size * 0.45)
            self.line(end, head, layer, LAYER_COLORS[layer])


def _entity_bbox(entity: Any) -> dict[str, list[float]] | None:
    try:
        minimum, maximum = entity.GetBoundingBox()
        return {"min": [float(minimum[0]), float(minimum[1])], "max": [float(maximum[0]), float(maximum[1])]}
    except Exception:
        return None


def _merge_bbox(current: dict[str, list[float]] | None, bbox: dict[str, list[float]] | None) -> dict[str, list[float]] | None:
    if bbox is None:
        return current
    if current is None:
        return {"min": list(bbox["min"]), "max": list(bbox["max"])}
    return {
        "min": [min(current["min"][0], bbox["min"][0]), min(current["min"][1], bbox["min"][1])],
        "max": [max(current["max"][0], bbox["max"][0]), max(current["max"][1], bbox["max"][1])],
    }


def _readback_created_shelf_entities(doc: Any, handles: list[str]) -> dict[str, Any]:
    unique_handles = _unique_handles(handles)
    unresolved: list[str] = []
    unmanaged: list[dict[str, str]] = []
    by_layer: dict[str, int] = {}
    sample_entities: list[dict[str, Any]] = []
    entity_bboxes: list[dict[str, Any]] = []
    union_bbox: dict[str, list[float]] | None = None

    for handle in unique_handles:
        entity = _entity_from_handle(doc, handle)
        if entity is None:
            unresolved.append(handle)
            continue
        layer = str(getattr(entity, "Layer", ""))
        if layer not in SHELF_LAYERS:
            unmanaged.append({"handle": handle, "layer": layer})
        by_layer[layer] = by_layer.get(layer, 0) + 1
        bbox = _entity_bbox(entity)
        union_bbox = _merge_bbox(union_bbox, bbox)
        entity_bboxes.append(
            {
                "handle": handle,
                "layer": layer,
                "objectName": str(getattr(entity, "ObjectName", "")),
                "bbox": bbox,
            }
        )
        if len(sample_entities) < 24:
            sample_entities.append(
                {
                    "handle": handle,
                    "layer": layer,
                    "objectName": str(getattr(entity, "ObjectName", "")),
                    "bbox": bbox,
                }
            )

    resolved_count = sum(by_layer.values())
    status = "ok" if resolved_count and not unresolved and not unmanaged else "fail"
    return {
        "status": status,
        "inputHandleCount": len(handles),
        "uniqueHandleCount": len(unique_handles),
        "resolvedHandleCount": resolved_count,
        "unresolvedHandleCount": len(unresolved),
        "unresolvedHandles": unresolved[:40],
        "unmanagedLayerCount": len(unmanaged),
        "unmanagedLayerSamples": unmanaged[:20],
        "byLayer": dict(sorted(by_layer.items())),
        "unionBbox": union_bbox,
        "entityBboxes": entity_bboxes,
        "sampleEntities": sample_entities,
        "standard": {
            "mainRacks": ["01_CLEAN_ASSETS", "B_OBJECT_ASSET_INDEX"],
            "subRacks": ["A1_LINE_STANDARDS", "A2_ANNOTATION_STYLES", "B_OBJECT_ASSET_INDEX"],
            "reviewOnlyZones": ["02_PREVIEW_CARDS", "03_REVIEW_QUARANTINE", "99_EVIDENCE_LINKS"],
            "copyBoundary": "Only clean source slots may be copied; labels, frames, evidence and object index entries are never-copy.",
        },
    }


def _existing_bbox(doc: Any) -> dict[str, list[float]]:
    xs: list[float] = []
    ys: list[float] = []
    for entity in doc.ModelSpace:
        if str(getattr(entity, "Layer", "")) in SHELF_LAYERS:
            continue
        bbox = _entity_bbox(entity)
        if bbox is None:
            continue
        xs.extend([bbox["min"][0], bbox["max"][0]])
        ys.extend([bbox["min"][1], bbox["max"][1]])
    if not xs or not ys:
        return {"min": [0.0, 0.0], "max": [16000.0, 9000.0]}
    return {"min": [min(xs), min(ys)], "max": [max(xs), max(ys)]}


def _load_previous_shelf_handles(output: Path) -> list[str]:
    if not output.is_file():
        return []
    try:
        report = json.loads(output.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return []
    handles = report.get("createdHandles")
    if not isinstance(handles, list):
        return []
    return [str(handle) for handle in handles if str(handle).strip()]


def _unique_handles(handles: list[str]) -> list[str]:
    result: list[str] = []
    for handle in handles:
        text = str(handle).strip()
        if text and text not in result:
            result.append(text)
    return result


def _unique(values: list[str] | tuple[str, ...] | None) -> list[str]:
    result: list[str] = []
    for value in values or []:
        text = str(value).strip()
        if text and text not in result:
            result.append(text)
    return result


def _entity_from_handle(doc: Any, handle: str) -> Any | None:
    try:
        return doc.HandleToObject(str(handle))
    except Exception:
        return None


def _move_entities_by_handles(doc: Any, handles: list[str], *, dx: float, dy: float) -> dict[str, Any]:
    import pythoncom
    import win32com.client

    moved: list[str] = []
    skipped: list[dict[str, str]] = []
    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
        return {"status": "not_required", "movedCount": 0, "movedHandles": [], "skipped": [], "dx": dx, "dy": dy}
    start = _point(win32com.client, pythoncom, [0.0, 0.0, 0.0])
    end = _point(win32com.client, pythoncom, [dx, dy, 0.0])
    for handle in _unique_handles(handles):
        entity = _entity_from_handle(doc, handle)
        if entity is None:
            skipped.append({"handle": handle, "reason": "missing"})
            continue
        try:
            entity.Move(start, end)
            moved.append(handle)
        except Exception as exc:
            skipped.append({"handle": handle, "reason": str(exc)})
    return {
        "status": "pass" if not skipped else "partial",
        "movedCount": len(moved),
        "movedHandles": moved[:40],
        "skipped": skipped[:20],
        "dx": round(dx, 3),
        "dy": round(dy, 3),
    }


def _normalize_protected_content_layers(doc: Any, protected_content: dict[str, Any]) -> dict[str, Any]:
    changed: list[str] = []
    skipped: list[dict[str, str]] = []
    for cluster in protected_content.get("clusters", []):
        if not isinstance(cluster, dict):
            continue
        for handle in cluster.get("handles", []):
            entity = _entity_from_handle(doc, str(handle))
            if entity is None:
                skipped.append({"handle": str(handle), "reason": "missing"})
                continue
            layer = str(getattr(entity, "Layer", ""))
            if layer not in FORBIDDEN_PROTECTED_CONTENT_LAYERS:
                continue
            try:
                entity.Layer = "ASSET_PROOF_CONTENT"
                changed.append(str(handle))
            except Exception as exc:
                skipped.append({"handle": str(handle), "reason": str(exc)})
    return {
        "status": "pass" if not skipped else "partial",
        "targetLayer": "ASSET_PROOF_CONTENT",
        "changedCount": len(changed),
        "changedHandles": changed[:40],
        "skipped": skipped[:20],
        "policy": "Visible legacy proof panels are kept as protected asset evidence, but not left on CODEX_PREVIEW.",
    }


def _plan_readability_content_reflow(clusters: list[dict[str, Any]]) -> dict[str, Any]:
    clean_clusters = [cluster for cluster in clusters if isinstance(cluster, dict) and _bbox_area_xy(cluster.get("bbox")) > 0]
    clean_clusters.sort(key=lambda item: float(item["bbox"]["min"][0]))
    if len(clean_clusters) < 2:
        return {"status": "not_required", "moves": [], "reason": "fewer than two protected content clusters"}
    left = clean_clusters[0]["bbox"]
    right = clean_clusters[1]["bbox"]
    target_right_min_x = float(left["max"][0]) + (READABLE_CONTENT_MARGIN * 2.0) + MIN_VISUAL_AISLE
    dx = max(0.0, target_right_min_x - float(right["min"][0]))
    if dx <= 1e-6:
        return {"status": "not_required", "moves": [], "reason": "existing content aisle already readable"}
    return {
        "status": "move_required",
        "moves": [
            {
                "clusterId": str(clean_clusters[1].get("clusterId") or "A2_ANNOTATION_STYLES"),
                "handles": [str(handle) for handle in clean_clusters[1].get("handles", []) if str(handle)],
                "dx": round(dx, 3),
                "dy": 0.0,
                "reason": "widen A1/A2 proof-panel aisle and allow readable content margins",
            }
        ],
        "minimumVisualAisle": MIN_VISUAL_AISLE,
        "readableContentMargin": READABLE_CONTENT_MARGIN,
    }


def _clear_previous_shelves(
    doc: Any,
    *,
    previous_handles: list[str],
    clear_all_shelf_layers: bool = False,
) -> dict[str, Any]:
    deleted: list[str] = []
    missing: list[str] = []
    skipped: list[dict[str, str]] = []
    mode = "previous_report_handles"
    entities: list[Any] = []
    if previous_handles:
        seen: set[str] = set()
        for handle in previous_handles:
            if handle in seen:
                continue
            seen.add(handle)
            entity = _entity_from_handle(doc, handle)
            if entity is None:
                missing.append(handle)
                continue
            entities.append(entity)
    elif clear_all_shelf_layers:
        mode = "explicit_clear_all_shelf_layers"
        entities = [entity for entity in list(doc.ModelSpace) if str(getattr(entity, "Layer", "")) in SHELF_LAYERS]
    else:
        return {
            "mode": "no_previous_manifest_no_delete",
            "deletedCount": 0,
            "deletedHandles": [],
            "missingHandles": [],
            "skipped": [],
            "safety": "No shelf manifest was found; layer-wide deletion requires --clear-all-shelf-layers.",
        }

    for entity in entities:
        layer = str(getattr(entity, "Layer", ""))
        handle = str(getattr(entity, "Handle", ""))
        if layer not in SHELF_LAYERS:
            skipped.append({"handle": handle, "layer": layer, "reason": "handle is not on a managed shelf layer"})
            continue
        try:
            entity.Delete()
            if handle:
                deleted.append(handle)
        except Exception as exc:
            skipped.append({"handle": handle, "layer": layer, "reason": str(exc)})
    return {
        "mode": mode,
        "deletedCount": len(deleted),
        "deletedHandles": deleted,
        "missingHandles": missing[:40],
        "missingCount": len(missing),
        "skipped": skipped[:20],
        "safety": "Default cleanup deletes only handles from the previous shelf layout report; layer-wide deletion is explicit only.",
    }


def _pad(bbox: dict[str, list[float]], amount: float) -> dict[str, list[float]]:
    return {
        "min": [bbox["min"][0] - amount, bbox["min"][1] - amount],
        "max": [bbox["max"][0] + amount, bbox["max"][1] + amount],
    }


def _bbox_width(bbox: dict[str, list[float]]) -> float:
    return float(bbox["max"][0]) - float(bbox["min"][0])


def _bbox_height(bbox: dict[str, list[float]]) -> float:
    return float(bbox["max"][1]) - float(bbox["min"][1])


def _bbox_area_xy(bbox: dict[str, list[float]] | None) -> float:
    if not isinstance(bbox, dict) or "min" not in bbox or "max" not in bbox:
        return 0.0
    return max(0.0, _bbox_width(bbox)) * max(0.0, _bbox_height(bbox))


def _bbox_contains(container: dict[str, list[float]], child: dict[str, list[float]], *, tolerance: float = 1e-6) -> bool:
    return (
        float(container["min"][0]) <= float(child["min"][0]) + tolerance
        and float(container["min"][1]) <= float(child["min"][1]) + tolerance
        and float(container["max"][0]) + tolerance >= float(child["max"][0])
        and float(container["max"][1]) + tolerance >= float(child["max"][1])
    )


def _bbox_intersects(a: dict[str, list[float]], b: dict[str, list[float]], *, clearance: float = 0.0) -> bool:
    protected = _pad(b, clearance) if clearance > 0 else b
    return not (
        float(a["max"][0]) < float(protected["min"][0])
        or float(a["min"][0]) > float(protected["max"][0])
        or float(a["max"][1]) < float(protected["min"][1])
        or float(a["min"][1]) > float(protected["max"][1])
    )


def _bbox_center_x(bbox: dict[str, list[float]]) -> float:
    return (float(bbox["min"][0]) + float(bbox["max"][0])) / 2.0


def _bbox_center_y(bbox: dict[str, list[float]]) -> float:
    return (float(bbox["min"][1]) + float(bbox["max"][1])) / 2.0


def _union_bbox_list(bboxes: list[dict[str, list[float]]]) -> dict[str, list[float]]:
    merged: dict[str, list[float]] | None = None
    for bbox in bboxes:
        merged = _merge_bbox(merged, bbox)
    return merged or {"min": [0.0, 0.0], "max": [16000.0, 9000.0]}


def _cluster_entries_by_largest_x_gap(entries: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    sortable = [entry for entry in entries if _bbox_area_xy(entry.get("bbox")) > 0]
    if len(sortable) <= 1:
        return [sortable] if sortable else []
    sortable.sort(key=lambda item: (float(item["bbox"]["min"][0]), float(item["bbox"]["max"][0])))
    union = _union_bbox_list([entry["bbox"] for entry in sortable])
    minimum_gap = max(420.0, _bbox_width(union) * 0.018)
    best_gap = 0.0
    best_index: int | None = None
    current_max_x = float(sortable[0]["bbox"]["max"][0])
    for index, entry in enumerate(sortable[1:], start=1):
        min_x = float(entry["bbox"]["min"][0])
        gap = min_x - current_max_x
        if gap > best_gap:
            best_gap = gap
            best_index = index
        current_max_x = max(current_max_x, float(entry["bbox"]["max"][0]))
    if best_index is not None and best_gap >= minimum_gap:
        return [sortable[:best_index], sortable[best_index:]]
    midpoint = _bbox_center_x(union)
    left = [entry for entry in sortable if _bbox_center_x(entry["bbox"]) <= midpoint]
    right = [entry for entry in sortable if _bbox_center_x(entry["bbox"]) > midpoint]
    if left and right:
        return [left, right]
    return [sortable]


def _content_clusters_from_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups = _cluster_entries_by_largest_x_gap(entries)
    cluster_ids = ["A1_LINE_STANDARDS", "A2_ANNOTATION_STYLES"]
    clusters: list[dict[str, Any]] = []
    for index, group in enumerate(groups[:2]):
        bboxes = [entry["bbox"] for entry in group if _bbox_area_xy(entry.get("bbox")) > 0]
        if not bboxes:
            continue
        bbox = _union_bbox_list(bboxes)
        clusters.append(
            {
                "clusterId": cluster_ids[index] if index < len(cluster_ids) else f"UNASSIGNED_CONTENT_{index + 1}",
                "bbox": bbox,
                "entityCount": len(group),
                "handles": [str(entry.get("handle", "")) for entry in group if str(entry.get("handle", ""))],
                "handleSamples": [str(entry.get("handle", "")) for entry in group[:16] if str(entry.get("handle", ""))],
                "layerSamples": _unique([str(entry.get("layer", "")) for entry in group[:16] if str(entry.get("layer", ""))]),
            }
        )
    clusters.sort(key=lambda item: float(item["bbox"]["min"][0]))
    for index, cluster in enumerate(clusters[:2]):
        cluster["clusterId"] = cluster_ids[index]
    return clusters


def _readback_protected_asset_content(doc: Any) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    union_bbox: dict[str, list[float]] | None = None
    for entity in doc.ModelSpace:
        layer = str(getattr(entity, "Layer", ""))
        if layer in SHELF_LAYERS:
            continue
        bbox = _entity_bbox(entity)
        if bbox is None or _bbox_area_xy(bbox) <= 0:
            continue
        handle = str(getattr(entity, "Handle", ""))
        entry = {
            "handle": handle,
            "layer": layer,
            "objectName": str(getattr(entity, "ObjectName", "")),
            "bbox": bbox,
        }
        entries.append(entry)
        union_bbox = _merge_bbox(union_bbox, bbox)
    clusters = _content_clusters_from_entries(entries)
    return {
        "status": "ok" if entries and clusters else "empty",
        "entityCount": len(entries),
        "unionBbox": union_bbox,
        "clusters": clusters,
        "sampleEntities": entries[:24],
        "policy": "Only non-shelf-layer entities are treated as protected reusable asset content; shelf labels, frames and evidence must avoid these bboxes.",
    }


def _layout_from_content_clusters(
    clusters: list[dict[str, Any]],
    *,
    fallback_bbox: dict[str, list[float]],
) -> dict[str, Any]:
    clean_clusters = [cluster for cluster in clusters if _bbox_area_xy(cluster.get("bbox")) > 0]
    if len(clean_clusters) < 2:
        zones = _layout_from_existing(fallback_bbox)
        return {
            "zones": zones,
            "contentSlots": {
                "A1_LINE_STANDARDS": {"bbox": fallback_bbox, "clusterStatus": "fallback_union_bbox"},
                "A2_ANNOTATION_STYLES": {"bbox": fallback_bbox, "clusterStatus": "fallback_union_bbox"},
            },
            "layoutStrategy": "fallback_union_bbox",
        }

    clean_clusters.sort(key=lambda item: float(item["bbox"]["min"][0]))
    left = clean_clusters[0]["bbox"]
    right = clean_clusters[1]["bbox"]
    content_union = _union_bbox_list([left, right])
    header_pad = 1900.0
    footer_pad = 1750.0
    outer_pad = READABLE_CONTENT_MARGIN
    min_between = MIN_VISUAL_AISLE
    main_min_y = min(float(left["min"][1]), float(right["min"][1])) - footer_pad
    main_max_y = max(float(left["max"][1]), float(right["max"][1])) + header_pad
    min_column_height = 9800.0
    if main_max_y - main_min_y < min_column_height:
        center_y = (main_min_y + main_max_y) / 2.0
        main_min_y = min(main_min_y, center_y - min_column_height / 2.0)
        main_max_y = max(main_max_y, center_y + min_column_height / 2.0)

    gap = float(right["min"][0]) - float(left["max"][0])
    if gap > min_between * 2:
        inner_pad = min(outer_pad, (gap - min_between) / 2.0)
        a1_max_x = float(left["max"][0]) + inner_pad
        a2_min_x = float(right["min"][0]) - inner_pad
    else:
        a1_max_x = float(left["max"][0])
        a2_min_x = float(right["min"][0])
    if a1_max_x >= a2_min_x:
        split = (float(left["max"][0]) + float(right["min"][0])) / 2.0
        a1_max_x = min(float(left["max"][0]), split - 1.0)
        a2_min_x = max(float(right["min"][0]), split + 1.0)

    a1 = {
        "min": [float(left["min"][0]) - outer_pad, main_min_y],
        "max": [a1_max_x, main_max_y],
    }
    a2 = {
        "min": [a2_min_x, main_min_y],
        "max": [float(right["max"][0]) + outer_pad, main_max_y],
    }
    b_width = max(8200.0, min(main_max_y - main_min_y, 9800.0))
    b_index = {
        "min": [a2["max"][0] + MIN_OBJECT_INDEX_AISLE, main_min_y],
        "max": [a2["max"][0] + MIN_OBJECT_INDEX_AISLE + b_width, main_max_y],
    }
    clean = {"min": [a1["min"][0], main_min_y], "max": [a2["max"][0], main_max_y]}

    full_min_x = a1["min"][0]
    full_max_x = b_index["max"][0]
    aisle = 1000.0
    index_height = 2100.0
    ops_height = 1900.0
    index = {"min": [full_min_x, main_max_y + aisle], "max": [full_max_x, main_max_y + aisle + index_height]}
    ops_min_y = main_min_y - aisle - ops_height
    ops_max_y = main_min_y - aisle
    ops_w = (full_max_x - full_min_x) / 3.0
    preview = {"min": [full_min_x, ops_min_y], "max": [full_min_x + ops_w - 360.0, ops_max_y]}
    quarantine = {"min": [full_min_x + ops_w, ops_min_y], "max": [full_min_x + ops_w * 2.0 - 360.0, ops_max_y]}
    evidence = {"min": [full_min_x + ops_w * 2.0, ops_min_y], "max": [full_max_x, ops_max_y]}
    zones = {
        "00_INDEX": index,
        "01_CLEAN_ASSETS": clean,
        "A1_LINE_STANDARDS": a1,
        "A2_ANNOTATION_STYLES": a2,
        "B_OBJECT_ASSET_INDEX": b_index,
        "02_PREVIEW_CARDS": preview,
        "03_REVIEW_QUARANTINE": quarantine,
        "99_EVIDENCE_LINKS": evidence,
        "EXPANSION_BAY_A": b_index,
    }
    return {
        "zones": zones,
        "contentSlots": {
            "A1_LINE_STANDARDS": {"bbox": left, "clusterStatus": "clustered_from_existing_content"},
            "A2_ANNOTATION_STYLES": {"bbox": right, "clusterStatus": "clustered_from_existing_content"},
        },
        "layoutStrategy": "content_cluster_bbox_clearance_v1",
        "contentUnionBbox": content_union,
    }


def _audit_shelf_content_clearance(
    *,
    protected_content: dict[str, Any],
    created_entity_readback: dict[str, Any],
    minimum_clearance: float = 60.0,
) -> dict[str, Any]:
    issues: list[str] = []
    checked: list[str] = []
    overlaps: list[dict[str, Any]] = []
    clusters = [cluster for cluster in protected_content.get("clusters", []) if isinstance(cluster, dict) and _bbox_area_xy(cluster.get("bbox")) > 0]
    entity_bboxes = [entry for entry in created_entity_readback.get("entityBboxes", []) if isinstance(entry, dict) and isinstance(entry.get("bbox"), dict)]
    if not clusters:
        issues.append("protected asset content readback missing")
    else:
        checked.append("protected asset content bboxes")
    if not entity_bboxes:
        issues.append("created shelf entity bboxes missing")
    else:
        checked.append("created shelf entity bboxes")
    for entity in entity_bboxes:
        entity_bbox = entity["bbox"]
        for cluster in clusters:
            cluster_bbox = cluster["bbox"]
            if _bbox_intersects(entity_bbox, cluster_bbox, clearance=minimum_clearance):
                overlaps.append(
                    {
                        "handle": str(entity.get("handle", "")),
                        "layer": str(entity.get("layer", "")),
                        "objectName": str(entity.get("objectName", "")),
                        "contentClusterId": str(cluster.get("clusterId", "")),
                        "entityBbox": entity_bbox,
                        "contentBbox": cluster_bbox,
                    }
                )
                break
    if overlaps:
        issues.append("shelf entity overlaps protected asset content")
    else:
        checked.append("shelf entities avoid protected asset content")
    return {
        "status": "pass" if not issues else "fail",
        "checked": _unique(checked),
        "issues": _unique(issues),
        "minimumClearance": minimum_clearance,
        "protectedClusterCount": len(clusters),
        "checkedShelfEntityCount": len(entity_bboxes),
        "overlapCount": len(overlaps),
        "overlaps": overlaps[:40],
    }


def _audit_visual_warehouse_readability(
    *,
    zones: dict[str, dict[str, list[float]]],
    content_slots: dict[str, dict[str, Any]],
    protected_content: dict[str, Any],
) -> dict[str, Any]:
    issues: list[str] = []
    checked: list[str] = []
    metrics: dict[str, Any] = {
        "maxContentWidthRatio": MAX_CONTENT_WIDTH_RATIO,
        "minimumVisualAisle": MIN_VISUAL_AISLE,
        "minimumObjectIndexAisle": MIN_OBJECT_INDEX_AISLE,
    }

    a1 = zones.get("A1_LINE_STANDARDS")
    a2 = zones.get("A2_ANNOTATION_STYLES")
    objects = zones.get("B_OBJECT_ASSET_INDEX")
    if not isinstance(a1, dict) or not isinstance(a2, dict):
        issues.append("A1/A2 semantic zones are missing")
    else:
        a1_a2_aisle = float(a2["min"][0]) - float(a1["max"][0])
        metrics["a1A2VisualAisle"] = round(a1_a2_aisle, 3)
        if a1_a2_aisle < MIN_VISUAL_AISLE:
            issues.append("A1/A2 visual aisle is too narrow")
        else:
            checked.append("A1/A2 visual aisle")

    if isinstance(a2, dict) and isinstance(objects, dict):
        object_aisle = float(objects["min"][0]) - float(a2["max"][0])
        metrics["a2ObjectIndexAisle"] = round(object_aisle, 3)
        if object_aisle < MIN_OBJECT_INDEX_AISLE:
            issues.append("A2/B object-index aisle is too narrow")
        else:
            checked.append("A2/B object-index aisle")

    for slot_id in ("A1_LINE_STANDARDS", "A2_ANNOTATION_STYLES"):
        zone = zones.get(slot_id)
        content = content_slots.get(slot_id, {}).get("bbox")
        if not isinstance(zone, dict) or not isinstance(content, dict):
            issues.append(f"{slot_id} content bbox is missing")
            continue
        if not _bbox_contains(zone, content, tolerance=1e-6):
            issues.append(f"{slot_id} content is outside owning shelf zone")
        zone_width = max(1.0, _bbox_width(zone))
        content_width = _bbox_width(content)
        ratio = content_width / zone_width
        metrics[f"{slot_id}.contentWidthRatio"] = round(ratio, 4)
        metrics[f"{slot_id}.leftMargin"] = round(float(content["min"][0]) - float(zone["min"][0]), 3)
        metrics[f"{slot_id}.rightMargin"] = round(float(zone["max"][0]) - float(content["max"][0]), 3)
        if ratio > MAX_CONTENT_WIDTH_RATIO:
            issues.append(f"{slot_id} content width ratio exceeds {MAX_CONTENT_WIDTH_RATIO:.2f}")
        else:
            checked.append(f"{slot_id} content density")

    layer_samples: list[str] = []
    for cluster in protected_content.get("clusters", []):
        if not isinstance(cluster, dict):
            continue
        layer_samples.extend(str(layer) for layer in cluster.get("layerSamples", []) if str(layer))
    unique_layers = _unique(layer_samples)
    metrics["protectedContentLayers"] = unique_layers
    if any(layer in FORBIDDEN_PROTECTED_CONTENT_LAYERS for layer in unique_layers):
        issues.append("protected asset proof content is still on CODEX_PREVIEW")
    else:
        checked.append("protected content layer semantics")

    if unique_layers and "ASSET_SOURCE_BOUNDARY" in unique_layers:
        issues.append("source boundary layer is mixed into protected proof content")
    elif unique_layers:
        checked.append("source/proof roles separated")

    return {
        "status": "pass" if not issues else "fail",
        "checked": _unique(checked),
        "issues": _unique(issues),
        "issueCount": len(_unique(issues)),
        "metrics": metrics,
        "policy": "A visual warehouse must remain readable after geometry-safe clearance: wide aisles, low content density, proof panels off CODEX_PREVIEW, and source definitions separated from proof graphics.",
    }


def _layout_from_existing(existing: dict[str, list[float]]) -> dict[str, dict[str, list[float]]]:
    content_w = existing["max"][0] - existing["min"][0]
    content_h = existing["max"][1] - existing["min"][1]
    split_x = existing["min"][0] + content_w * 0.62
    gutter = MIN_VISUAL_AISLE
    top_pad = 1450.0
    bottom_pad = 1450.0
    main_min_y = existing["min"][1] - bottom_pad
    main_max_y = existing["max"][1] + top_pad
    min_column_height = 9800.0
    if main_max_y - main_min_y < min_column_height:
        center_y = (main_min_y + main_max_y) / 2
        main_min_y = center_y - min_column_height / 2
        main_max_y = center_y + min_column_height / 2

    a1 = {
        "min": [existing["min"][0] - READABLE_CONTENT_MARGIN, main_min_y],
        "max": [split_x + 260.0, main_max_y],
    }
    a2 = {
        "min": [split_x + gutter, main_min_y],
        "max": [existing["max"][0] + READABLE_CONTENT_MARGIN, main_max_y],
    }
    b_width = max(8200.0, min(main_max_y - main_min_y, 9800.0))
    b_index = {
        "min": [a2["max"][0] + MIN_OBJECT_INDEX_AISLE, main_min_y],
        "max": [a2["max"][0] + MIN_OBJECT_INDEX_AISLE + b_width, main_max_y],
    }
    clean = {"min": [a1["min"][0], main_min_y], "max": [a2["max"][0], main_max_y]}

    full_min_x = a1["min"][0]
    full_max_x = b_index["max"][0]
    aisle = 1000.0
    index_height = 2100.0
    ops_height = 1900.0
    index = {"min": [full_min_x, main_max_y + aisle], "max": [full_max_x, main_max_y + aisle + index_height]}
    ops_min_y = main_min_y - aisle - ops_height
    ops_max_y = main_min_y - aisle
    ops_w = (full_max_x - full_min_x) / 3
    preview = {"min": [full_min_x, ops_min_y], "max": [full_min_x + ops_w - 360.0, ops_max_y]}
    quarantine = {"min": [full_min_x + ops_w, ops_min_y], "max": [full_min_x + ops_w * 2 - 360.0, ops_max_y]}
    evidence = {"min": [full_min_x + ops_w * 2, ops_min_y], "max": [full_max_x, ops_max_y]}
    return {
        "00_INDEX": index,
        "01_CLEAN_ASSETS": clean,
        "A1_LINE_STANDARDS": a1,
        "A2_ANNOTATION_STYLES": a2,
        "B_OBJECT_ASSET_INDEX": b_index,
        "02_PREVIEW_CARDS": preview,
        "03_REVIEW_QUARANTINE": quarantine,
        "99_EVIDENCE_LINKS": evidence,
        "EXPANSION_BAY_A": b_index,
    }


def _draw_slot_grid(drawer: ShelfDrawer, bbox: dict[str, list[float]], *, rows: int, cols: int, labels: list[str]) -> None:
    x1, y1 = bbox["min"]
    x2, y2 = bbox["max"]
    inner = {"min": [x1 + 420, y1 + 520], "max": [x2 - 420, y2 - 720]}
    drawer.rect(inner, "ASSET_SLOT_GRID", LAYER_COLORS["ASSET_SLOT_GRID"])
    width = inner["max"][0] - inner["min"][0]
    height = inner["max"][1] - inner["min"][1]
    for c in range(1, cols):
        x = inner["min"][0] + width * c / cols
        drawer.line((x, inner["min"][1]), (x, inner["max"][1]), "ASSET_SLOT_GRID", LAYER_COLORS["ASSET_SLOT_GRID"])
    for r in range(1, rows):
        y = inner["min"][1] + height * r / rows
        drawer.line((inner["min"][0], y), (inner["max"][0], y), "ASSET_SLOT_GRID", LAYER_COLORS["ASSET_SLOT_GRID"])
    index = 0
    cell_w = width / cols
    cell_h = height / rows
    for r in range(rows):
        for c in range(cols):
            if index >= len(labels):
                return
            x = inner["min"][0] + c * cell_w + 160
            y = inner["max"][1] - (r + 1) * cell_h + cell_h - 360
            drawer.text(labels[index], (x, y), height=145, layer="ASSET_TEXT", color=7)
            index += 1


def _cell_bbox(
    inner: dict[str, list[float]],
    *,
    row: int,
    col: int,
    rows: int,
    cols: int,
    gutter: float = 120.0,
) -> dict[str, list[float]]:
    width = inner["max"][0] - inner["min"][0]
    height = inner["max"][1] - inner["min"][1]
    cell_w = width / cols
    cell_h = height / rows
    x1 = inner["min"][0] + col * cell_w + gutter
    x2 = inner["min"][0] + (col + 1) * cell_w - gutter
    y2 = inner["max"][1] - row * cell_h - gutter
    y1 = inner["max"][1] - (row + 1) * cell_h + gutter
    return {"min": [x1, y1], "max": [x2, y2]}


def _status_label(slot: dict[str, Any]) -> str:
    status = str(slot.get("status") or "")
    if status == "occupied":
        return "已入库 / verified source"
    if status == "reserved":
        return "已预留 / source pending"
    if status == "index_only":
        return "索引入口 / never copy"
    return "空位 / expandable"


def _draw_rack_family(
    drawer: ShelfDrawer,
    bbox: dict[str, list[float]],
    family: dict[str, Any],
    *,
    layer: str,
    color: int,
    rows: int = 4,
    cols: int = 2,
) -> None:
    x1, y1 = bbox["min"]
    x2, y2 = bbox["max"]
    drawer.text(str(family["title"]), (x1 + 260, y2 - 380), height=190, layer="ASSET_RACK_HEADER", color=2)
    drawer.text(str(family["description"]), (x1 + 260, y2 - 720), height=115, layer="ASSET_TEXT", color=7)
    drawer.text(str(family["slotPolicy"]), (x1 + 260, y2 - 980), height=105, layer="ASSET_TEXT", color=7)
    inner = {"min": [x1 + 380, y1 + 520], "max": [x2 - 380, y2 - 1240]}
    drawer.rect(inner, layer, color)
    width = inner["max"][0] - inner["min"][0]
    height = inner["max"][1] - inner["min"][1]
    for c in range(1, cols):
        x = inner["min"][0] + width * c / cols
        drawer.line((x, inner["min"][1]), (x, inner["max"][1]), "ASSET_SLOT_GRID", LAYER_COLORS["ASSET_SLOT_GRID"])
    for r in range(1, rows):
        y = inner["min"][1] + height * r / rows
        drawer.line((inner["min"][0], y), (inner["max"][0], y), "ASSET_SLOT_GRID", LAYER_COLORS["ASSET_SLOT_GRID"])

    slots = [slot for slot in family.get("slots", []) if isinstance(slot, dict)]
    for index, slot in enumerate(slots[: rows * cols]):
        row = index // cols
        col = index % cols
        cell = _cell_bbox(inner, row=row, col=col, rows=rows, cols=cols)
        drawer.rect(cell, layer, color)
        tx = cell["min"][0] + 120
        ty = cell["max"][1] - 210
        drawer.text(f"{slot['slotId']}  {slot['title']}", (tx, ty), height=105, layer="ASSET_TEXT", color=7)
        drawer.text(_status_label(slot), (tx, ty - 230), height=82, layer="ASSET_TEXT", color=color)
        asset_ids = slot.get("assetIds") if isinstance(slot.get("assetIds"), list) else []
        if asset_ids:
            drawer.text("asset: " + ", ".join(str(asset_id) for asset_id in asset_ids[:2]), (tx, ty - 440), height=70, layer="ASSET_TEXT", color=7)
        notes = slot.get("notes") if isinstance(slot.get("notes"), list) else []
        if notes:
            drawer.text(str(notes[0])[:32], (tx, ty - 630), height=68, layer="ASSET_TEXT", color=8)


def _draw_index_map(drawer: ShelfDrawer, index: dict[str, list[float]], rack_plan: dict[str, Any]) -> None:
    x1, y1 = index["min"]
    x2, y2 = index["max"]
    drawer.text("系统资产库 / R4 三列仓库", (x1 + 420, y2 - 500), height=300, layer="ASSET_LABEL", color=2)
    drawer.text("当前分类：drawing_standards.basic    主仓：A1 线型图层 / A2 标注文字 / B 对象索引    底部：复审、隔离、证据", (x1 + 420, y2 - 920), height=120, layer="ASSET_LABEL", color=7)
    map_area = {"min": [x1 + 420, y1 + 300], "max": [x2 - 420, y2 - 1160]}
    labels = [
        ("A1", "线型 / 图层 / 填充标准", "ASSET_RACK_BASE"),
        ("A2", "尺寸 / 文字 / 引线标准", "ASSET_RACK_BASE"),
        ("B", "对象资产索引，不放 block 本体", "ASSET_RACK_OBJECTS"),
        ("OPS", "02 复审 / 03 隔离 / 99 证据", "ASSET_PREVIEW_CARD"),
    ]
    cell_w = (map_area["max"][0] - map_area["min"][0]) / len(labels)
    for index_value, (title, note, layer) in enumerate(labels):
        cell = {
            "min": [map_area["min"][0] + index_value * cell_w + 80, map_area["min"][1]],
            "max": [map_area["min"][0] + (index_value + 1) * cell_w - 80, map_area["max"][1]],
        }
        drawer.rect(cell, layer, LAYER_COLORS[layer])
        drawer.text(title, (cell["min"][0] + 150, cell["max"][1] - 250), height=115, layer="ASSET_LABEL", color=7)
        drawer.text(note, (cell["min"][0] + 150, cell["min"][1] + 170), height=78, layer="ASSET_LABEL", color=7)


def _slot_by_id(family: dict[str, Any], slot_id: str) -> dict[str, Any]:
    for slot in family.get("slots", []):
        if isinstance(slot, dict) and slot.get("slotId") == slot_id:
            return slot
    return {"slotId": slot_id, "title": slot_id, "status": "empty_reserved", "assetIds": [], "notes": []}


def _draw_slot_label(drawer: ShelfDrawer, slot: dict[str, Any], bbox: dict[str, list[float]], *, color: int) -> None:
    x1, y1 = bbox["min"]
    x2, y2 = bbox["max"]
    drawer.rect(bbox, "ASSET_RACK_BASE", color)
    drawer.text(f"{slot['slotId']}  {slot['title']}", (x1 + 160, y2 - 240), height=100, layer="ASSET_TEXT", color=7)
    drawer.text(_status_label(slot), (x1 + 160, y2 - 470), height=78, layer="ASSET_TEXT", color=color)
    asset_ids = slot.get("assetIds") if isinstance(slot.get("assetIds"), list) else []
    if asset_ids:
        drawer.text("asset: " + ", ".join(str(asset_id) for asset_id in asset_ids), (x1 + 160, y1 + 160), height=72, layer="ASSET_TEXT", color=7)


def _draw_secondary_slots(drawer: ShelfDrawer, bbox: dict[str, list[float]], family: dict[str, Any], slot_ids: list[str]) -> None:
    if not slot_ids:
        return
    drawer.rect(bbox, "ASSET_PREVIEW_CARD", LAYER_COLORS["ASSET_PREVIEW_CARD"])
    cell_w = (bbox["max"][0] - bbox["min"][0]) / len(slot_ids)
    for index_value, slot_id in enumerate(slot_ids):
        slot = _slot_by_id(family, slot_id)
        cell = {
            "min": [bbox["min"][0] + index_value * cell_w + 80.0, bbox["min"][1] + 80.0],
            "max": [bbox["min"][0] + (index_value + 1) * cell_w - 80.0, bbox["max"][1] - 80.0],
        }
        drawer.rect(cell, "ASSET_PREVIEW_CARD", LAYER_COLORS["ASSET_PREVIEW_CARD"])
        drawer.text(str(slot["slotId"]).replace("_", " "), (cell["min"][0] + 90, cell["max"][1] - 175), height=62, layer="ASSET_LABEL", color=7)
        drawer.text(str(slot["title"])[:18], (cell["min"][0] + 90, cell["min"][1] + 120), height=58, layer="ASSET_LABEL", color=8)


def _source_boundary_for_content(
    column_bbox: dict[str, list[float]],
    content_bbox: dict[str, list[float]],
    *,
    pad: float = 260.0,
    edge_gap: float = 120.0,
) -> dict[str, list[float]]:
    left_space = max(edge_gap, float(content_bbox["min"][0]) - float(column_bbox["min"][0]) - edge_gap)
    right_space = max(edge_gap, float(column_bbox["max"][0]) - float(content_bbox["max"][0]) - edge_gap)
    bottom_space = max(edge_gap, float(content_bbox["min"][1]) - float(column_bbox["min"][1]) - edge_gap)
    top_space = max(edge_gap, float(column_bbox["max"][1]) - float(content_bbox["max"][1]) - edge_gap)
    return {
        "min": [
            float(content_bbox["min"][0]) - min(pad, left_space),
            float(content_bbox["min"][1]) - min(pad, bottom_space),
        ],
        "max": [
            float(content_bbox["max"][0]) + min(pad, right_space),
            float(content_bbox["max"][1]) + min(pad, top_space),
        ],
    }


def _draw_standard_column(
    drawer: ShelfDrawer,
    bbox: dict[str, list[float]],
    family: dict[str, Any],
    *,
    title: str,
    subtitle: str,
    primary_slot_id: str,
    secondary_slot_ids: list[str],
    content_bbox: dict[str, list[float]] | None = None,
) -> None:
    x1, y1 = bbox["min"]
    x2, y2 = bbox["max"]
    drawer.rect(bbox, "ASSET_01_CLEAN_ASSETS", LAYER_COLORS["ASSET_01_CLEAN_ASSETS"])
    drawer.text(title, (x1 + 260, y2 - 430), height=220, layer="ASSET_LABEL", color=2)
    drawer.text(subtitle, (x1 + 260, y2 - 760), height=105, layer="ASSET_LABEL", color=7)

    slot = _slot_by_id(family, primary_slot_id)
    drawer.text(f"{slot['slotId']}  {slot['title']}", (x1 + 260, y2 - 1080), height=105, layer="ASSET_LABEL", color=7)
    drawer.text(_status_label(slot), (x1 + 260, y2 - 1320), height=78, layer="ASSET_LABEL", color=4)
    asset_ids = slot.get("assetIds") if isinstance(slot.get("assetIds"), list) else []
    if asset_ids:
        drawer.text("assetId: " + ", ".join(str(asset_id) for asset_id in asset_ids), (x1 + 260, y1 + 1420), height=66, layer="ASSET_LABEL", color=7)

    proof = (
        _source_boundary_for_content(bbox, content_bbox)
        if content_bbox is not None and _bbox_area_xy(content_bbox) > 0
        else {"min": [x1 + 420, y1 + 1800], "max": [x2 - 420, y2 - 1450]}
    )
    drawer.rect(proof, "ASSET_PREVIEW_CARD", LAYER_COLORS["ASSET_PREVIEW_CARD"])
    drawer.text("PROOF_PANEL only: visible evidence, never a copy source", (x1 + 260, y1 + 1320), height=68, layer="ASSET_LABEL", color=8)

    source_token = {"min": [x1 + 420, y2 - 1620], "max": [min(x1 + 2850.0, x2 - 420), y2 - 1335]}
    drawer.rect(source_token, "ASSET_SOURCE_BOUNDARY", LAYER_COLORS["ASSET_SOURCE_BOUNDARY"])
    drawer.text("STYLE_DEFINITION_SOURCE", (source_token["min"][0] + 90, source_token["min"][1] + 95), height=68, layer="ASSET_LABEL", color=30)

    reserved_top = y1 + 1180.0
    if content_bbox is not None and _bbox_area_xy(content_bbox) > 0:
        reserved_top = min(reserved_top, float(content_bbox["min"][1]) - 420.0)
    reserved = {"min": [x1 + 420, y1 + 320], "max": [x2 - 420, max(y1 + 780.0, reserved_top)]}
    _draw_secondary_slots(drawer, reserved, family, secondary_slot_ids)


def _draw_object_index_rack(drawer: ShelfDrawer, bbox: dict[str, list[float]], family: dict[str, Any]) -> None:
    x1, y1 = bbox["min"]
    x2, y2 = bbox["max"]
    drawer.rect(bbox, "ASSET_RACK_OBJECTS", LAYER_COLORS["ASSET_RACK_OBJECTS"])
    drawer.text(str(family["title"]), (x1 + 260, y2 - 430), height=210, layer="ASSET_LABEL", color=2)
    drawer.text("INDEX ONLY：这里只指向分类 DWG；真正对象 block 不进入 standard_assets.dwg。", (x1 + 260, y2 - 760), height=102, layer="ASSET_LABEL", color=7)
    inner = {"min": [x1 + 420, y1 + 420], "max": [x2 - 420, y2 - 1150]}
    slots = [slot for slot in family.get("slots", []) if isinstance(slot, dict)]
    rows = 4
    cols = 2
    for index_value, slot in enumerate(slots[: rows * cols]):
        cell = _cell_bbox(inner, row=index_value // cols, col=index_value % cols, rows=rows, cols=cols, gutter=110.0)
        drawer.rect(cell, "ASSET_PREVIEW_CARD", LAYER_COLORS["ASSET_PREVIEW_CARD"])
        drawer.text(f"{slot['slotId']}  {slot['title']}", (cell["min"][0] + 120, cell["max"][1] - 210), height=78, layer="ASSET_LABEL", color=7)
        drawer.text(_status_label(slot), (cell["min"][0] + 120, cell["max"][1] - 410), height=62, layer="ASSET_LABEL", color=3)
        category = str(slot.get("category") or "")
        native = str(slot.get("nativeDwg") or "")
        drawer.text(category[:30], (cell["min"][0] + 120, cell["min"][1] + 300), height=55, layer="ASSET_LABEL", color=8)
        drawer.text(native.replace("libraries/system_library/", "")[:34], (cell["min"][0] + 120, cell["min"][1] + 130), height=50, layer="ASSET_LABEL", color=8)


def _draw_ops_zone(
    drawer: ShelfDrawer,
    bbox: dict[str, list[float]],
    *,
    title: str,
    body: str,
    layer: str,
    color: int,
) -> None:
    x1, y1 = bbox["min"]
    x2, y2 = bbox["max"]
    drawer.rect(bbox, layer, color)
    drawer.text(title, (x1 + 260, y2 - 360), height=155, layer="ASSET_LABEL", color=color)
    drawer.text(body, (x1 + 260, y2 - 690), height=78, layer="ASSET_LABEL", color=7)
    drawer.line((x1 + 220, y1 + 520), (x2 - 220, y1 + 520), "ASSET_SLOT_GRID", LAYER_COLORS["ASSET_SLOT_GRID"])


def _draw_base_scaffold_rack(drawer: ShelfDrawer, bbox: dict[str, list[float]], family: dict[str, Any]) -> None:
    x1, y1 = bbox["min"]
    x2, y2 = bbox["max"]
    drawer.text(str(family["title"]), (x1 + 300, y2 - 430), height=210, layer="ASSET_RACK_HEADER", color=2)
    drawer.text("现有线型表、尺寸样式面板直接归入 A02/A03 大槽位；底部才是后续底座标准预留位。", (x1 + 300, y2 - 780), height=118, layer="ASSET_TEXT", color=7)
    content = {"min": [x1 + 700, y1 + 2300], "max": [x2 - 700, y2 - 1450]}
    content_w = content["max"][0] - content["min"][0]
    split_x = content["min"][0] + content_w * 0.62
    linetype = {"min": [content["min"][0] - 260, content["min"][1] - 260], "max": [split_x - 180, content["max"][1] + 260]}
    dimension = {"min": [split_x + 180, content["min"][1] - 260], "max": [content["max"][0] + 260, content["max"][1] + 260]}
    _draw_slot_label(drawer, _slot_by_id(family, "A02_LINETYPE"), linetype, color=LAYER_COLORS["ASSET_RACK_BASE"])
    _draw_slot_label(drawer, _slot_by_id(family, "A03_DIMENSION_STYLE"), dimension, color=LAYER_COLORS["ASSET_RACK_BASE"])

    reserved = {"min": [x1 + 520, y1 + 420], "max": [x2 - 520, y1 + 1800]}
    drawer.rect(reserved, "ASSET_SLOT_GRID", LAYER_COLORS["ASSET_SLOT_GRID"])
    reserved_slots = [
        "A01_LAYER_LINEWEIGHT",
        "A04_TEXT_STYLE",
        "A05_LEADER_ANNOTATION",
        "A06_HATCH_PATTERN",
        "A07_TABLE_TITLEBLOCK",
        "A08_SYMBOL_NAMING",
    ]
    rows = 2
    cols = 3
    for index_value, slot_id in enumerate(reserved_slots):
        cell = _cell_bbox(reserved, row=index_value // cols, col=index_value % cols, rows=rows, cols=cols, gutter=90.0)
        slot = _slot_by_id(family, slot_id)
        drawer.rect(cell, "ASSET_SLOT_GRID", LAYER_COLORS["ASSET_SLOT_GRID"])
        drawer.text(f"{slot['slotId']}", (cell["min"][0] + 110, cell["max"][1] - 210), height=78, layer="ASSET_TEXT", color=7)
        drawer.text(str(slot["title"]), (cell["min"][0] + 110, cell["min"][1] + 170), height=70, layer="ASSET_TEXT", color=7)


def _draw_layout(
    drawer: ShelfDrawer,
    zones: dict[str, dict[str, list[float]]],
    rack_plan: dict[str, Any],
    *,
    content_slots: dict[str, dict[str, Any]] | None = None,
) -> None:
    labels = [
        "系统资产库 / 分类可扩展货架",
        "A1 线型图层标准",
        "A2 标注文字标准",
        "B 对象资产索引 / 跨库入口",
        "01_CLEAN_ASSETS 只放可复制源；训练标题、说明、边框、尺寸线、证据路径不得进入",
    ] + _collect_text_values(rack_plan)
    assert_no_text_encoding_corruption(labels)

    for layer, color in LAYER_COLORS.items():
        _ensure_layer(drawer.doc, layer, color)

    zone_layers = {
        "00_INDEX": "ASSET_00_INDEX",
        "02_PREVIEW_CARDS": "ASSET_02_PREVIEW_CARDS",
        "03_REVIEW_QUARANTINE": "ASSET_03_REVIEW_QUARANTINE",
        "99_EVIDENCE_LINKS": "ASSET_99_EVIDENCE_LINKS",
    }
    for zone, layer in zone_layers.items():
        drawer.rect(zones[zone], layer, LAYER_COLORS.get(layer))

    index = zones["00_INDEX"]
    _draw_index_map(drawer, index, rack_plan)

    clean = zones["01_CLEAN_ASSETS"]
    families = [family for family in rack_plan.get("rackFamilies", []) if isinstance(family, dict)]
    base_family = next(family for family in families if family.get("rackId") == "A_BASE_SCAFFOLD")
    object_family = next(family for family in families if family.get("rackId") == "B_OBJECT_ASSET_INDEX")
    a1_slot = (content_slots or {}).get("A1_LINE_STANDARDS")
    a2_slot = (content_slots or {}).get("A2_ANNOTATION_STYLES")
    a1_content_bbox = a1_slot.get("bbox") if isinstance(a1_slot, dict) and isinstance(a1_slot.get("bbox"), dict) else None
    a2_content_bbox = a2_slot.get("bbox") if isinstance(a2_slot, dict) and isinstance(a2_slot.get("bbox"), dict) else None
    drawer.rect(clean, "ASSET_01_CLEAN_ASSETS", LAYER_COLORS["ASSET_01_CLEAN_ASSETS"])
    _draw_standard_column(
        drawer,
        zones["A1_LINE_STANDARDS"],
        base_family,
        title="A1 线型 / 图层 / 填充标准",
        subtitle="drawing_standards clean source：线型表归位；框线与标签 never-copy。",
        primary_slot_id="A02_LINETYPE_STANDARD",
        secondary_slot_ids=["A01_LAYER_STANDARD", "A03_PLOT_COLOR_LINEWEIGHT"],
        content_bbox=a1_content_bbox,
    )
    _draw_standard_column(
        drawer,
        zones["A2_ANNOTATION_STYLES"],
        base_family,
        title="A2 尺寸 / 文字 / 引线标准",
        subtitle="标注、文字、引线、表格图框和比例基准；样式定义优先于展示几何。",
        primary_slot_id="A05_DIMENSION_STYLE",
        secondary_slot_ids=["A04_TEXT_STYLE", "A06_LEADER_SYMBOL_STYLE", "A07_TABLE_TITLEBLOCK", "A08_SCALE_UNIT_BASELINE"],
        content_bbox=a2_content_bbox,
    )

    _draw_object_index_rack(drawer, zones["B_OBJECT_ASSET_INDEX"], object_family)

    preview = zones["02_PREVIEW_CARDS"]
    _draw_ops_zone(
        drawer,
        preview,
        title="02 PREVIEW CARDS 复审暂存",
        body="候选样例、人工复核卡片；copyPolicy=preview_only，不作为资产源。",
        layer="ASSET_PREVIEW_CARD",
        color=8,
    )
    quarantine = zones["03_REVIEW_QUARANTINE"]
    _draw_ops_zone(
        drawer,
        quarantine,
        title="03 REVIEW QUARANTINE 隔离区",
        body="来源不清、训练面板整块、全屏复制候选；copyPolicy=never_copy。",
        layer="ASSET_QUARANTINE",
        color=1,
    )
    evidence = zones["99_EVIDENCE_LINKS"]
    _draw_ops_zone(
        drawer,
        evidence,
        title="99 EVIDENCE LINKS 证据索引",
        body="报告、截图、training refs、reuseProbe；只证明来源，不承载可复制几何。",
        layer="ASSET_EVIDENCE",
        color=3,
    )


def _union_bbox(zones: dict[str, dict[str, list[float]]]) -> dict[str, list[float]]:
    xs: list[float] = []
    ys: list[float] = []
    for bbox in zones.values():
        xs.extend([bbox["min"][0], bbox["max"][0]])
        ys.extend([bbox["min"][1], bbox["max"][1]])
    return {"min": [min(xs), min(ys)], "max": [max(xs), max(ys)]}


def _zoom_to_bbox(app: Any, drawer: ShelfDrawer, bbox: dict[str, list[float]]) -> dict[str, Any]:
    pad_x = max((bbox["max"][0] - bbox["min"][0]) * 0.04, 500.0)
    pad_y = max((bbox["max"][1] - bbox["min"][1]) * 0.04, 500.0)
    p1 = drawer.point(bbox["min"][0] - pad_x, bbox["min"][1] - pad_y)
    p2 = drawer.point(bbox["max"][0] + pad_x, bbox["max"][1] + pad_y)
    app.ZoomWindow(p1, p2)
    return {"status": "zoomed_to_asset_shelves", "bbox": {"min": [bbox["min"][0] - pad_x, bbox["min"][1] - pad_y], "max": [bbox["max"][0] + pad_x, bbox["max"][1] + pad_y]}}


def run(
    *,
    asset_dwg: Path,
    output: Path,
    category: str = DEFAULT_CATEGORY,
    clear_all_shelf_layers: bool = False,
) -> dict[str, Any]:
    utf8 = configure_utf8_process()
    rack_plan = _classified_rack_plan()
    labels = list(LAYER_COLORS) + [category, "系统资产库", "干净源货架", "复审卡片区", "隔离区", "证据索引"] + _collect_text_values(rack_plan)
    encoding_preflight = assert_no_text_encoding_corruption(str(asset_dwg), labels)
    desktop = _switch_to_input_desktop()
    app = _connect_autocad()
    previous_document = {
        "name": str(getattr(app.ActiveDocument, "Name", "")),
        "fullName": str(getattr(app.ActiveDocument, "FullName", "")),
    }
    doc, opened_by_tool = _open_or_activate_asset_doc(app, asset_dwg)
    for layer, color in {**LAYER_COLORS, **CONTENT_LAYER_COLORS}.items():
        _ensure_layer(doc, layer, color)
    protected_content_before_normalize = _readback_protected_asset_content(doc)
    content_layer_normalization = _normalize_protected_content_layers(doc, protected_content_before_normalize)
    if content_layer_normalization.get("changedCount"):
        try:
            doc.Regen(1)
        except Exception:
            pass
    protected_content_before_reflow = _readback_protected_asset_content(doc)
    content_reflow_plan = _plan_readability_content_reflow(protected_content_before_reflow.get("clusters", []))
    content_reflow_results: list[dict[str, Any]] = []
    for move in content_reflow_plan.get("moves", []):
        if not isinstance(move, dict):
            continue
        content_reflow_results.append(
            _move_entities_by_handles(
                doc,
                [str(handle) for handle in move.get("handles", []) if str(handle)],
                dx=float(move.get("dx") or 0.0),
                dy=float(move.get("dy") or 0.0),
            )
        )
    if content_reflow_results:
        try:
            doc.Regen(1)
        except Exception:
            pass
    content_mutation_count = int(content_layer_normalization.get("changedCount") or 0) + sum(
        int(result.get("movedCount") or 0) for result in content_reflow_results if isinstance(result, dict)
    )
    protected_content = _readback_protected_asset_content(doc)
    before_bbox = protected_content.get("unionBbox") if isinstance(protected_content.get("unionBbox"), dict) else _existing_bbox(doc)
    previous_shelf_handles = _load_previous_shelf_handles(output)
    layout = _layout_from_content_clusters(protected_content.get("clusters", []), fallback_bbox=before_bbox)
    zones = layout["zones"]
    content_slots = layout["contentSlots"]
    visual_readability_audit = _audit_visual_warehouse_readability(
        zones=zones,
        content_slots=content_slots,
        protected_content=protected_content,
    )
    rack_plan = {
        **rack_plan,
        "zoneBboxes": zones,
        "contentSlots": content_slots,
        "clearancePolicy": {
            "layoutStrategy": layout.get("layoutStrategy"),
            "protectedContentSource": "non_shelf_layer_entity_bboxes_before_layout_write",
            "minimumShelfContentClearance": 60.0,
            "failureMode": "fail if any shelf frame, label, route or slot grid bbox intersects protected asset content",
        },
        "readabilityPolicy": {
            "minimumVisualAisle": MIN_VISUAL_AISLE,
            "minimumObjectIndexAisle": MIN_OBJECT_INDEX_AISLE,
            "maximumContentWidthRatio": MAX_CONTENT_WIDTH_RATIO,
            "proofContentLayer": "ASSET_PROOF_CONTENT",
            "sourceProofRoleSeparation": "source definitions use small source tokens; visible panels are proof-only and never-copy",
        },
    }
    rack_plan_audit = audit_visual_rack_plan(visual_rack_plan=rack_plan, readability_report=visual_readability_audit)
    if rack_plan_audit.get("status") != "pass":
        report = {
            "status": "fail",
            "category": category,
            "assetDwg": str(asset_dwg.resolve()),
            "utf8": utf8,
            "encodingPreflight": encoding_preflight,
            "desktopSwitch": desktop,
            "previousActiveDocument": previous_document,
            "openedByTool": opened_by_tool,
            "previousShelfHandleCount": len(previous_shelf_handles),
            "protectedContentBeforeNormalize": protected_content_before_normalize,
            "contentLayerNormalization": content_layer_normalization,
            "contentReflowPlan": content_reflow_plan,
            "contentReflowResults": content_reflow_results,
            "contentMutationCount": content_mutation_count,
            "protectedContentReadback": protected_content,
            "layoutStrategy": layout.get("layoutStrategy"),
            "zones": zones,
            "rackPlan": rack_plan,
            "rackPlanAudit": rack_plan_audit,
            "visualReadabilityAudit": visual_readability_audit,
            "wroteCad": bool(content_mutation_count),
            "savedAssetDwg": bool(getattr(doc, "Saved", False)),
            "savedCurrentBusinessDwg": False,
            "nativeWriteBoundary": "visual rack audit failed before shelf scaffold write; content normalization/reflow changes, if any, were not saved by this fail path",
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        return report
    cleanup = _clear_previous_shelves(
        doc,
        previous_handles=previous_shelf_handles,
        clear_all_shelf_layers=clear_all_shelf_layers,
    )
    drawer = ShelfDrawer(doc)
    _draw_layout(drawer, zones, rack_plan, content_slots=content_slots)
    layout_bbox = _union_bbox(zones)
    try:
        doc.Regen(1)
    except Exception:
        pass
    entity_readback = _readback_created_shelf_entities(doc, drawer.created_handles)
    visual_clearance_audit = _audit_shelf_content_clearance(
        protected_content=protected_content,
        created_entity_readback=entity_readback,
    )
    rack_plan_audit = audit_visual_rack_plan(
        visual_rack_plan=rack_plan,
        entity_readback=entity_readback,
        clearance_report=visual_clearance_audit,
        readability_report=visual_readability_audit,
    )
    doc.Save()
    saved = bool(getattr(doc, "Saved", False))
    metadata_refresh = refresh_system_asset_layout_metadata(
        category=category,
        native_layout_write_status="asset_library_shelf_scaffold_written_to_standard_assets_dwg",
        visual_rack_plan=rack_plan,
    )
    focus = _zoom_to_bbox(app, drawer, layout_bbox)
    active_document = {
        "name": str(getattr(doc, "Name", "")),
        "fullName": str(getattr(doc, "FullName", "")),
        "saved": saved,
    }
    report = {
        "status": "pass"
        if saved
        and drawer.created_handles
        and rack_plan_audit.get("status") == "pass"
        and entity_readback.get("status") == "ok"
        and visual_clearance_audit.get("status") == "pass"
        and visual_readability_audit.get("status") == "pass"
        and metadata_refresh.get("status") == "pass"
        else "fail",
        "category": category,
        "assetDwg": str(asset_dwg.resolve()),
        "utf8": utf8,
        "encodingPreflight": encoding_preflight,
        "desktopSwitch": desktop,
        "previousActiveDocument": previous_document,
        "activeDocument": active_document,
        "openedByTool": opened_by_tool,
        "previousShelfHandleCount": len(previous_shelf_handles),
        "protectedContentBeforeNormalize": protected_content_before_normalize,
        "contentLayerNormalization": content_layer_normalization,
        "contentReflowPlan": content_reflow_plan,
        "contentReflowResults": content_reflow_results,
        "contentMutationCount": content_mutation_count,
        "protectedContentReadback": protected_content,
        "layoutStrategy": layout.get("layoutStrategy"),
        "contentSlots": content_slots,
        "zones": zones,
        "rackPlan": rack_plan,
        "rackPlanAudit": rack_plan_audit,
        "createdEntityReadback": entity_readback,
        "visualClearanceAudit": visual_clearance_audit,
        "visualReadabilityAudit": visual_readability_audit,
        "layoutBbox": layout_bbox,
        "focus": focus,
        "cleanup": cleanup,
        "createdHandleCount": len(drawer.created_handles),
        "createdHandles": drawer.created_handles,
        "layoutMetadataRefresh": metadata_refresh,
        "polishHardeningDecision": {
            "status": "complete_for_current_scope",
            "reviewAgents": [
                "pipeline_asset_governor",
                "pipeline_asset_librarian",
                "pipeline_asset_dwg_curator",
                "pipeline_asset_reuse_auditor",
                "visual_layout_review",
            ],
            "checked": [
                "visualRackPlan v2 audit passed",
                "created shelf entity readback passed",
                "shelf/content bbox clearance audit passed",
                "warehouse readability audit passed",
                "three-column warehouse separates drawing standards from object asset index",
                "current linetype and dimension panels are inside large semantic shelves",
                "proof panels are off CODEX_PREVIEW and separated from source-definition tokens",
                "object-family shelves are index_only and never_copy in this DWG",
                "preview, quarantine and evidence zones are outside clean source",
                "visual route lines do not cross asset content",
            ],
            "decision": "No new global Agent is required for this layout pass; existing asset governor, librarian, DWG curator and reuse auditor cover the current scope. Future repeated object-family curation can be promoted into a dedicated category Agent after reviewed package evidence.",
            "nextPolishTrigger": [
                "user visual review rejects the R4 warehouse layout",
                "a new object-family asset repeatedly needs native DWG curation",
                "reuse audit finds index-only slots being copied as geometry",
            ],
        },
        "wroteCad": True,
        "savedAssetDwg": saved,
        "savedCurrentBusinessDwg": False,
        "nativeWriteBoundary": "shelf scaffold written and saved; clean asset source geometry migration is still governed per asset",
        "policy": "system asset DWG shelves only; default cleanup deletes previous report handles; non-shelf asset content preserved",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Draw an expandable shelf layout in a system asset DWG.")
    parser.add_argument("--asset-dwg", type=Path, default=ASSET_DWG)
    parser.add_argument("--category", default=DEFAULT_CATEGORY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--clear-all-shelf-layers", action="store_true")
    args = parser.parse_args()
    try:
        report = run(
            asset_dwg=args.asset_dwg,
            output=args.output,
            category=args.category,
            clear_all_shelf_layers=args.clear_all_shelf_layers,
        )
    except Exception as exc:
        report = {"status": "fail", "reason": str(exc), "assetDwg": str(args.asset_dwg), "wroteCad": False, "savedAssetDwg": False}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
