"""Executable semantic rules for CAD asset routing and safety gates."""

from __future__ import annotations

import re
from typing import Any

from core.runtime.encoding_guard import detect_text_encoding_corruption


CAD_SEMANTIC_RULES: list[dict[str, Any]] = [
    {
        "ruleId": "system_asset_sedimentation",
        "name": "系统资产沉淀",
        "triggers": ["沉淀", "通用资产", "收进资产库", "资产库", "保存为资产"],
        "aliases": ["沉淀资产", "系统资产", "通用资产"],
        "routes": ["system_asset_sedimentation"],
        "requiredGuards": [
            "encoding_preflight",
            "asset_library_governor",
            "source_boundary",
            "layout_plan_v2",
            "training_contamination_cleanup",
            "save_asset_dwg",
            "native_visible_asset_gate",
            "reuse_workflow_probe",
            "open_asset_dwg_for_review",
        ],
        "forbiddenBehaviors": ["save_current_business_dwg", "whole_modelspace_block_export", "metadata_only_claimed_as_verified"],
        "validationHooks": ["asset_contract_verify", "asset_governance_decision", "native_dwg_saved_readback", "native_visible_asset_evidence", "system_asset_reuse_workflow", "registry_encoding_preflight"],
        "evidenceBoundary": "system asset governor, DWG save/open review, visible native evidence, and reuse workflow readiness are distinct gates; none may be inferred from metadata alone",
        "priority": 100,
    },
    {
        "ruleId": "linetype_style_summary_table",
        "name": "线型样式与颜色归纳表",
        "triggers": ["线型表", "线型样式", "线宽线型", "开启范围线", "样线", "颜色归纳"],
        "aliases": ["线型表", "线型归纳表", "线型样式与颜色归纳表", "开启范围线样例"],
        "routes": ["system_asset_reuse", "cad_plan"],
        "requiredGuards": ["encoding_preflight", "no_solid_fill", "sample_cell_containment", "adaptive_table_layout"],
        "forbiddenBehaviors": ["solid_fill_background", "fixed_24_row_limit", "group_row_vertical_split", "sample_out_of_cell"],
        "validationHooks": ["linetype_table_layout_audit", "style_readback", "visible_text_readback"],
        "evidenceBoundary": "entity readback proves CAD properties; screenshots only prove visual preview",
        "priority": 90,
    },
    {
        "ruleId": "system_asset_reuse",
        "name": "系统资产跨 DWG 复用",
        "triggers": ["调用", "复用", "插入", "套用", "放到当前图", "放到当前dwg", "使用资产", "asset", "reuse"],
        "aliases": ["复用资产", "跨dwg调用", "插入资产"],
        "routes": ["system_asset_reuse"],
        "requiredGuards": ["registry_encoding_preflight", "native_source_gate", "reuse_workflow_probe", "created_handles_readback", "no_current_dwg_save"],
        "forbiddenBehaviors": ["weak_match_auto_reuse", "metadata_only_reuse", "save_current_business_dwg"],
        "validationHooks": ["system_asset_reuse_workflow", "readback_ok_gate"],
        "evidenceBoundary": "ready plan requires sourceSpec; asset_reused requires created handles and readbackStatus=ok; style_definition plans must not copy training panels",
        "priority": 80,
    },
    {
        "ruleId": "local_repair_first",
        "name": "局部错误原位修复",
        "triggers": ["修一下", "不对", "画错", "局部", "重修", "微调", "不要重画"],
        "aliases": ["原位修复", "局部修复", "repair_plan"],
        "routes": ["repair_plan"],
        "requiredGuards": ["target_handles_or_bbox", "preview_layer_only"],
        "forbiddenBehaviors": ["whole_modelspace_delete", "global_redraw_without_need", "formal_layer_mutation"],
        "validationHooks": ["target_readback", "post_repair_audit"],
        "evidenceBoundary": "repair scope must be locked by handles or bbox",
        "priority": 40,
    },
]


def _norm(value: object) -> str:
    return re.sub(r"\s+", "", str(value or "").lower())


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def match_semantic_rules(phrase: str) -> list[dict[str, Any]]:
    """Return semantic rules whose triggers or aliases appear in the phrase."""

    text = _norm(phrase)
    if not text:
        return []
    matches: list[dict[str, Any]] = []
    for rule in CAD_SEMANTIC_RULES:
        matched_terms: list[str] = []
        for term in [*rule.get("triggers", []), *rule.get("aliases", [])]:
            if _norm(term) and _norm(term) in text:
                matched_terms.append(str(term))
        if matched_terms:
            matches.append(
                {
                    "ruleId": rule["ruleId"],
                    "name": rule["name"],
                    "matchedTerms": _unique(matched_terms),
                    "routes": list(rule.get("routes", [])),
                    "requiredGuards": list(rule.get("requiredGuards", [])),
                    "forbiddenBehaviors": list(rule.get("forbiddenBehaviors", [])),
                    "validationHooks": list(rule.get("validationHooks", [])),
                    "evidenceBoundary": rule.get("evidenceBoundary", ""),
                    "priority": int(rule.get("priority", 0)),
                }
            )
    matches.sort(key=lambda item: (-int(item["priority"]), str(item["ruleId"])))
    return matches


def _asset_text_payload(asset: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key in ("assetId", "name", "category", "aliases", "useWhen", "tags", "assetKind", "verificationStatus"):
        if key in asset:
            payload[key] = asset[key]
    for key in ("retrieval", "native", "exportManifest", "verification", "feedbackLoop"):
        value = asset.get(key)
        if isinstance(value, dict):
            payload[key] = value
    return payload


def asset_registry_encoding_preflight(assets: list[dict[str, Any]]) -> dict[str, Any]:
    """Run text-corruption preflight over searchable system-asset registry fields."""

    payload = [_asset_text_payload(asset) for asset in assets]
    report = detect_text_encoding_corruption(payload)
    return {
        **report,
        "scope": "system_asset_registry_text",
        "assetCount": len(assets),
    }


def semantic_rule_summary(phrase: str) -> dict[str, Any]:
    matches = match_semantic_rules(phrase)
    return {
        "status": "matched" if matches else "none",
        "phrase": phrase,
        "matchedRuleCount": len(matches),
        "matchedRules": matches,
    }
