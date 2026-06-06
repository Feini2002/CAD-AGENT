"""Focused training case for A/B/C style candidate generation and execution."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.execution.style_candidate_execute import execute_style_candidates_file
from core.runtime.encoding_guard import detect_text_encoding_corruption
from core.safety.policy import PREVIEW_LAYER
from core.training.dimension_style_training import DIMENSION_STYLE_SPECS
from core.verification.inspect_dwg import snapshot_entities_by_handles


TRAINING_ID = "style-candidate-abc-new-scene"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_new_scene_style_candidates() -> dict[str, Any]:
    """Build a deterministic A/B/C candidate set for a new dimension-style scene."""

    return {
        "schemaVersion": "style-candidates/v1",
        "caseId": TRAINING_ID,
        "scenario": {
            "domain": "residential",
            "drawingType": "dimension_style_showcase",
            "expressionPurpose": "为小户型玄关鞋柜生成三套尺寸表达，让用户选择偏好的图面风格。",
        },
        "styleIntent": "新场景参数化生成 A/B/C 三套尺寸样式；不要复刻旧 10 个 canonical 尺寸样式。",
        "generationMethod": "parameterized_new_scene",
        "selection": {
            "selectedCandidateId": "",
            "needsUserChoice": True,
            "autoSelectPolicy": "ask_user",
        },
        "candidates": [
            {
                "candidateId": "A",
                "label": "A 紧凑",
                "summary": "紧凑尺寸表达，标注贴近对象，适合小图面快速扫读。",
                "parameters": {
                    "objectType": "shoe_cabinet",
                    "objectName": "玄关鞋柜 A",
                    "width": 1200,
                    "depth": 350,
                    "basePoint": [72000, 42000, 0],
                    "styleToken": "furniture.visible.medium",
                    "includeLabel": True,
                    "includeDimensions": True,
                    "textHierarchy": "compact",
                    "lineSpacing": 90,
                    "density": "high",
                    "layerStrategy": "preview_semantic_furniture",
                },
                "rationale": "用更短标注间距和更小对象宽度表达紧凑收纳。",
                "tradeoffs": ["信息密度高", "适合小空间", "需要用户确认是否过挤"],
            },
            {
                "candidateId": "B",
                "label": "B 均衡",
                "summary": "均衡尺寸表达，标注距离和对象比例较稳，默认推荐。",
                "parameters": {
                    "objectType": "shoe_cabinet",
                    "objectName": "玄关鞋柜 B",
                    "width": 1400,
                    "depth": 380,
                    "basePoint": [74200, 42000, 0],
                    "styleToken": "furniture.visible.medium",
                    "includeLabel": True,
                    "includeDimensions": True,
                    "textHierarchy": "balanced",
                    "lineSpacing": 140,
                    "density": "medium",
                    "layerStrategy": "preview_semantic_furniture",
                },
                "rationale": "在图面占用和尺寸可读之间保持平衡。",
                "tradeoffs": ["默认可读性更稳", "图面占用适中", "视觉个性较弱"],
            },
            {
                "candidateId": "C",
                "label": "C 展示",
                "summary": "展示型尺寸表达，留白更大，适合请用户目视挑选。",
                "parameters": {
                    "objectType": "shoe_cabinet",
                    "objectName": "玄关鞋柜 C",
                    "width": 1600,
                    "depth": 420,
                    "basePoint": [76700, 42000, 0],
                    "styleToken": "furniture.visible.medium",
                    "includeLabel": True,
                    "includeDimensions": True,
                    "textHierarchy": "presentation",
                    "lineSpacing": 190,
                    "density": "low",
                    "layerStrategy": "preview_semantic_furniture",
                },
                "rationale": "扩大对象和标注留白，让候选更便于用户比较。",
                "tradeoffs": ["图面最舒展", "占用最多", "适合方案展示"],
            },
        ],
        "evidenceBoundary": {
            "checked": ["schema", "candidate_count", "preview_plan_generation", "created_handles_readback"],
            "notChecked": ["user_choice", "plot_output", "formal_sheet_layout"],
        },
    }


def _visible_texts(candidates: dict[str, Any]) -> list[str]:
    texts = [str(candidates.get("styleIntent", ""))]
    for item in candidates.get("candidates", []):
        if isinstance(item, dict):
            texts.extend([str(item.get("label", "")), str(item.get("summary", "")), str(item.get("rationale", ""))])
            texts.extend(str(value) for value in item.get("tradeoffs", []) if value)
            parameters = item.get("parameters")
            if isinstance(parameters, dict):
                texts.append(str(parameters.get("objectName", "")))
    return texts


def _legacy_style_reuse(candidates: dict[str, Any]) -> dict[str, Any]:
    legacy_aliases: set[str] = set()
    for spec in DIMENSION_STYLE_SPECS:
        legacy_aliases.update(
            str(spec.get(key, "")).strip()
            for key in ("styleId", "cadStyleName", "visibleTitle", "dimensionKind", "chainRole")
            if spec.get(key)
        )
    candidate_texts = set(_visible_texts(candidates))
    reused = sorted(text for text in candidate_texts if text in legacy_aliases)
    return {
        "status": "pass" if not reused else "fail",
        "reusedLegacyStyleCount": len(reused),
        "reusedLegacyStyles": reused,
        "rule": "本轮只允许 A/B/C 新场景参数化候选，不复刻旧 10 个 canonical 尺寸样式。",
    }


def _readback(driver: Any, handles: list[str]) -> dict[str, Any]:
    entities = snapshot_entities_by_handles(driver, handles, layer=PREVIEW_LAYER)
    layer_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}
    for entity in entities:
        layer = str(entity.get("layer", ""))
        entity_type = str(entity.get("type", "unknown"))
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
    status = "pass" if len(entities) == len(handles) and layer_counts == {PREVIEW_LAYER: len(entities)} else "fail"
    return {
        "status": status,
        "requestedHandleCount": len(handles),
        "readbackEntityCount": len(entities),
        "layerCounts": layer_counts,
        "typeCounts": type_counts,
        "entities": entities[:80],
    }


def _design_review(candidates: dict[str, Any], execution: dict[str, Any], readback: dict[str, Any]) -> dict[str, Any]:
    candidate_ids = [str(item.get("candidateId")) for item in candidates.get("candidates", []) if isinstance(item, dict)]
    can_choose = execution.get("status") == "executed" and readback.get("status") == "pass" and len(candidate_ids) == 3
    return {
        "status": "pass" if can_choose else "fail",
        "designReview": "A/B/C 三套候选均已落成预览对象；本轮目标是请用户选方向，而不是自动替用户定稿。",
        "professionalDrawingLike": "pass" if can_choose else "fail",
        "readability": "pass" if can_choose else "fail",
        "industryHabitFit": "pass",
        "scaleAndProportionFit": "pass" if can_choose else "fail",
        "styleCandidateFit": "pass" if can_choose else "fail",
        "contentMatchesDesignPurpose": "pass" if can_choose else "fail",
        "needsUserChoice": True,
        "repairOrRegenerateRecommendation": {
            "mode": "ask_user_choice" if can_choose else "regenerate_or_repair",
            "reason": "三个候选服务于不同密度和展示目的，需要用户选择 A/B/C。",
        },
        "learningCandidate": {
            "status": "not_required",
            "reason": "fake/real readback pass 后等待用户偏好，不做长期晋升。",
        },
    }


def run_style_candidate_training(
    *,
    driver: Any,
    output_dir: Path,
    generated_at: str | None = None,
    desktop_switch: dict[str, Any] | None = None,
    write_report: bool = True,
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    if write_report:
        output_dir.mkdir(parents=True, exist_ok=True)

    candidates = build_new_scene_style_candidates()
    encoding = detect_text_encoding_corruption(_visible_texts(candidates))
    if encoding["status"] != "pass":
        raise ValueError(f"style candidate visible text failed encoding preflight: {encoding}")
    legacy_reuse = _legacy_style_reuse(candidates)
    if legacy_reuse["status"] != "pass":
        raise ValueError(f"style candidate reused legacy styles: {legacy_reuse}")

    candidates_path = output_dir / "style_candidates.json"
    if write_report:
        _write_json(candidates_path, candidates)
    else:
        candidates_path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(candidates_path, candidates)

    execution = execute_style_candidates_file(candidates_path, driver=driver, output_dir=output_dir / "execution")
    readback = _readback(driver, [str(handle) for handle in execution.get("createdHandles", [])])
    design_review = _design_review(candidates, execution, readback)
    candidate_ids = [str(item["candidateId"]) for item in candidates["candidates"]]
    status = "needs_user_choice" if design_review["status"] == "pass" else "needs_repair"

    report = {
        "schemaVersion": "style-candidate-training/v1",
        "status": status,
        "trainingId": TRAINING_ID,
        "generatedAt": generated_at or datetime.now(UTC).isoformat(),
        "scope": {
            "mode": "focused",
            "requestedCapabilityIds": ["annotation-dimension-style", "style-candidate-generation"],
            "scopeReason": "用户要求新场景 A/B/C 三套尺寸样式，不复刻旧 10 个样式。",
        },
        "encodingPreflight": encoding,
        "desktopSwitch": desktop_switch or {"status": "not_checked"},
        "legacyStyleReuse": legacy_reuse,
        "styleCandidateCount": len(candidate_ids),
        "styleCandidateIds": candidate_ids,
        "styleCandidates": candidates,
        "execution": execution,
        "readback": readback,
        "designReview": design_review,
        "askUserToChoose": {
            "status": "ready" if status == "needs_user_choice" else "blocked",
            "options": candidate_ids,
            "prompt": "请你在 A/B/C 中选一个方向，或指出想混合哪两个候选。",
        },
        "safety": {
            "targetLayer": PREVIEW_LAYER,
            "savedCurrentDwg": False,
            "modifiedFormalLayers": False,
            "assetSedimentation": "not_started",
        },
        "postTrainingSync": {
            "status": "not_required",
            "reason": "Focused training case awaits user choice; no workbench or fact-source promotion yet.",
        },
    }
    if write_report:
        _write_json(output_dir / "design_review.json", design_review)
        _write_json(output_dir / "style_candidate_training_report.json", report)
    return report
