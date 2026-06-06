"""System asset sedimentation helpers.

This module records reusable CAD assets in ``libraries/system_library``.
It deliberately does not save or mutate the active DWG; native CAD writes are
handled by future explicit export/apply steps.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.assets.system_asset_library_governance import (
    audit_visual_rack_plan,
    build_asset_library_governance,
    build_asset_library_layout_plan,
)
from core.runtime.encoding_guard import assert_no_text_encoding_corruption


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SYSTEM_LIBRARY_REL = Path("libraries") / "system_library"
REGISTRY_REL = SYSTEM_LIBRARY_REL / "registry.json"
ALLOWED_ASSET_STATUSES = ("candidate", "systemized", "verified", "deprecated")
CONFLICT_POLICIES = ("update_existing", "new_variant", "reject")
ASSET_KINDS = ("object_block", "style_standard", "rule_recipe", "composite_template")
EXPORT_MODES = ("metadata_only", "block_export", "style_export", "recipe_export")
PRECISE_BLOCK_SOURCE_MODES = ("selected_handles", "created_handles", "active_dwg_handles", "explicit_bbox", "named_block")
FORBIDDEN_BULK_SOURCE_MODES = (
    "whole_codex_preview",
    "whole_modelspace",
    "current_screen",
    "all_visible",
    "training_panel",
    "global_preview_bbox",
)
LAYOUT_GRID_COLUMNS = 4


@dataclass(frozen=True)
class SystemAssetLocation:
    category: str
    category_path: str
    package_path: str
    contract_path: str
    native_dwg_path: str


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _read_json_object(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.is_file():
        return dict(default)
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return dict(default)
    return data if isinstance(data, dict) else dict(default)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _safe_token(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip().lower()).strip("_")
    if not token:
        raise ValueError("asset category tokens must not be empty")
    return token


def _category_tokens(category: str) -> list[str]:
    tokens = [_safe_token(token) for token in str(category).split(".")]
    if not tokens:
        raise ValueError("asset category must not be empty")
    return tokens


def _singular_token(token: str) -> str:
    if token.endswith("ies") and len(token) > 3:
        return token[:-3] + "y"
    if token.endswith("s") and len(token) > 1:
        return token[:-1]
    return token


def _default_native_stem(tokens: list[str]) -> str:
    if tokens[0] == "drawing_standards":
        return "standard"
    return _singular_token(tokens[-1])


def _unique_strings(values: list[str] | tuple[str, ...] | None) -> list[str]:
    result: list[str] = []
    for value in values or []:
        text = str(value).strip()
        if text and text not in result:
            result.append(text)
    return result


def _positive_number(value: Any) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _asset_contract_kind(asset: dict[str, Any]) -> str:
    manifest = _dict_or_empty(asset.get("exportManifest"))
    return str(asset.get("assetKind") or manifest.get("assetKind") or "")


def _asset_contract_export_mode(asset: dict[str, Any]) -> str:
    manifest = _dict_or_empty(asset.get("exportManifest"))
    return str(manifest.get("exportMode") or "")


def _asset_contract_lifecycle_status(asset: dict[str, Any]) -> str:
    lifecycle = _dict_or_empty(asset.get("lifecycle"))
    return str(lifecycle.get("status") or asset.get("lifecycleStatus") or asset.get("status") or "")


def _asset_contract_verification_status(asset: dict[str, Any]) -> str:
    verification = _dict_or_empty(asset.get("verification"))
    return str(asset.get("verificationStatus") or verification.get("status") or "")


def _has_native_visible_asset_evidence(asset: dict[str, Any]) -> bool:
    native = _dict_or_empty(asset.get("native"))
    verification = _dict_or_empty(asset.get("verification"))
    evidence = _dict_or_empty(verification.get("evidence"))
    candidates = [
        native.get("nativeVisiblePanelEvidence"),
        asset.get("nativeVisiblePanelEvidence"),
        evidence.get("nativeVisiblePanel"),
        evidence.get("nativeVisibleAsset"),
        evidence.get("visiblePanel"),
    ]
    for candidate in candidates:
        item = _dict_or_empty(candidate)
        status = str(item.get("status") or "").lower()
        if status not in {"pass", "ok", "captured", "native_visible_panel_readback", "written_to_standard_assets_dwg_modelspace"}:
            continue
        has_readback_count = any(
            _positive_number(item.get(key))
            for key in ("createdHandleCount", "entityCount", "dimensionReadbackCount", "readbackEntityCount")
        )
        has_visual_ref = any(item.get(key) for key in ("focusedScreenshot", "screenshot", "visualScreenshot", "report", "summary"))
        if has_readback_count and has_visual_ref:
            return True

    return bool(evidence.get("visualScreenshot") and _positive_number(evidence.get("entityCount")))


def _has_executable_reuse_probe(asset: dict[str, Any]) -> bool:
    native = _dict_or_empty(asset.get("native"))
    verification = _dict_or_empty(asset.get("verification"))
    evidence = _dict_or_empty(verification.get("evidence"))
    candidates = [
        asset.get("reuseWorkflowProbe"),
        native.get("reuseWorkflowProbe"),
        evidence.get("reuseWorkflowProbe"),
    ]
    for candidate in candidates:
        item = _dict_or_empty(candidate)
        status = str(item.get("status") or "").lower()
        if status not in {"ready", "pass"}:
            continue
        if item.get("savedCurrentDwg") is True:
            continue
        encoding_status = str(item.get("encodingPreflightStatus") or "").lower()
        if encoding_status == "fail":
            continue
        source_spec = _dict_or_empty(item.get("sourceSpec"))
        source_mode = str(item.get("sourceSpecMode") or source_spec.get("mode") or "")
        ready_count = _positive_number(item.get("readyTaskCount"))
        has_ready_plan = any(_dict_or_empty(plan).get("status") == "ready" for plan in item.get("reusePlans", []) if isinstance(plan, dict))
        if ready_count or source_mode or has_ready_plan:
            return True

    replay = _dict_or_empty(evidence.get("reuseReplay"))
    if str(replay.get("status") or "").lower() != "asset_reused":
        return False
    if replay.get("savedCurrentDwg") is True:
        return False
    return any(_positive_number(replay.get(key)) for key in ("createdHandleCount", "readbackEntityCount", "readbackCount"))


def _asset_status(value: str | None) -> str:
    status = str(value or "candidate").strip().lower()
    if status not in ALLOWED_ASSET_STATUSES:
        allowed = ", ".join(ALLOWED_ASSET_STATUSES)
        raise ValueError(f"unsupported asset status {status!r}; expected one of {allowed}")
    return status


def _conflict_policy(value: str | None) -> str:
    policy = str(value or "update_existing").strip().lower()
    if policy not in CONFLICT_POLICIES:
        allowed = ", ".join(CONFLICT_POLICIES)
        raise ValueError(f"unsupported conflict policy {policy!r}; expected one of {allowed}")
    return policy


def _infer_asset_kind(category: str, value: str | None) -> str:
    if value:
        asset_kind = str(value).strip().lower()
    elif category.startswith("drawing_standards."):
        asset_kind = "style_standard"
    elif category.startswith(("furniture.", "objects.", "blocks.", "symbols.")):
        asset_kind = "object_block"
    else:
        asset_kind = "rule_recipe"
    if asset_kind not in ASSET_KINDS:
        allowed = ", ".join(ASSET_KINDS)
        raise ValueError(f"unsupported asset kind {asset_kind!r}; expected one of {allowed}")
    return asset_kind


def _clean_export_mode(value: str | None) -> str:
    mode = str(value or "").strip().lower()
    if mode and mode not in EXPORT_MODES:
        allowed = ", ".join(EXPORT_MODES)
        raise ValueError(f"unsupported export mode {mode!r}; expected one of {allowed}")
    return mode


def _dimension_text(value: Any) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _source_boundary_contract(
    *,
    source: dict[str, Any] | None,
    source_boundary_mode: str | None,
    included_handles: list[str] | None,
    excluded_handles: list[str] | None,
) -> dict[str, Any]:
    source_data = source if isinstance(source, dict) else {}
    source_type = str(source_data.get("type", "manual_metadata")).strip() or "manual_metadata"
    mode = str(source_boundary_mode or source_type).strip().lower() or "manual_metadata"
    source_handles = source_data.get("handles", [])
    if not isinstance(source_handles, list):
        source_handles = []
    included = _unique_strings(included_handles or [str(handle) for handle in source_handles])
    excluded = _unique_strings(excluded_handles)
    contract: dict[str, Any] = {
        "mode": mode,
        "sourceType": source_type,
        "includedHandles": included,
        "excludedHandles": excluded,
        "precision": "precise" if mode in PRECISE_BLOCK_SOURCE_MODES else "unclear",
    }
    if "bbox" in source_data:
        contract["bbox"] = source_data["bbox"]
    if "activeDocument" in source_data:
        contract["activeDocument"] = source_data["activeDocument"]
    return contract


def _export_contracts(
    *,
    asset_kind: str,
    export_mode: str | None,
    source_boundary: dict[str, Any],
    block_name: str | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    requested_mode = _clean_export_mode(export_mode)
    boundary_mode = str(source_boundary.get("mode", "manual_metadata"))
    included_handles = source_boundary.get("includedHandles", [])
    if not isinstance(included_handles, list):
        included_handles = []

    if boundary_mode in FORBIDDEN_BULK_SOURCE_MODES and requested_mode == "block_export":
        raise ValueError(f"source boundary {boundary_mode!r} is too broad for block_export")

    if asset_kind == "style_standard":
        if requested_mode == "block_export":
            raise ValueError("style_standard assets must not use block_export")
        final_mode = requested_mode or "style_export"
        decision = "style_export_only" if final_mode == "style_export" else "metadata_only"
    elif asset_kind == "object_block":
        if requested_mode == "style_export":
            raise ValueError("object_block assets must not use style_export")
        has_precise_boundary = boundary_mode in PRECISE_BLOCK_SOURCE_MODES
        has_exportable_source = bool(included_handles) or boundary_mode in {"explicit_bbox", "named_block"}
        if requested_mode == "block_export":
            if not has_precise_boundary or not has_exportable_source:
                raise ValueError("block_export requires selected/created handles, explicit bbox, or named block source boundary")
            final_mode = "block_export"
        elif has_precise_boundary and has_exportable_source:
            final_mode = "block_export"
        else:
            final_mode = "metadata_only"
        decision = "export_manifest_ready" if final_mode == "block_export" else "defer_export_until_precise_source_boundary"
    else:
        if requested_mode in {"block_export", "style_export"}:
            raise ValueError(f"{asset_kind} assets must not use {requested_mode}")
        final_mode = requested_mode or "metadata_only"
        decision = "metadata_or_recipe_only"

    export_manifest = {
        "assetKind": asset_kind,
        "exportMode": final_mode,
        "sourceBoundary": source_boundary,
        "includedHandles": list(included_handles),
        "excludedHandles": source_boundary.get("excludedHandles", []),
        "targetBlockName": str(block_name).strip() if block_name else "",
        "nativeWrite": "deferred_until_explicit_cad_export_approval",
    }
    anti_contamination = {
        "decision": decision,
        "forbiddenSourceModes": list(FORBIDDEN_BULK_SOURCE_MODES),
        "preciseBlockSourceModes": list(PRECISE_BLOCK_SOURCE_MODES),
        "checks": [
            "do not export whole modelspace",
            "do not export whole CODEX_PREVIEW by default",
            "do not include labels, borders, dimensions, or training notes unless explicitly included",
            "record includedHandles and excludedHandles before native export",
        ],
    }
    return export_manifest, anti_contamination


def _retrieval_contract(
    *,
    name: str,
    aliases: list[str] | None,
    use_when: list[str] | None,
    tags: list[str] | None,
    scenario_tags: list[str] | None,
    dimensions: dict[str, Any] | None,
    constraints: list[str] | None,
) -> dict[str, Any]:
    clean_aliases = _unique_strings(aliases)
    clean_use_when = _unique_strings(use_when)
    clean_tags = _unique_strings(tags)
    clean_scenario_tags = _unique_strings(scenario_tags)
    clean_constraints = _unique_strings(constraints)
    clean_dimensions = dimensions or {}
    match_text = _unique_strings(
        [
            name,
            *clean_aliases,
            *clean_use_when,
            *clean_tags,
            *clean_scenario_tags,
            *clean_constraints,
            *[f"{key}:{_dimension_text(value)}" for key, value in sorted(clean_dimensions.items())],
        ]
    )
    return {
        "aliases": clean_aliases,
        "useWhen": clean_use_when,
        "tags": clean_tags,
        "scenarioTags": clean_scenario_tags,
        "constraints": clean_constraints,
        "dimensions": clean_dimensions,
        "matchText": match_text,
        "priority": "system_library_before_reference_library",
    }


def _verification_contract(*, native_dwg_exists: bool, export_manifest: dict[str, Any]) -> dict[str, Any]:
    not_checked = [
        "native DWG geometry reuse",
        "CAD insertion replay",
        "user visual approval",
    ]
    if not native_dwg_exists:
        not_checked.insert(0, "native DWG file")
    export_mode = str(export_manifest.get("exportMode", "metadata_only"))
    if export_mode == "metadata_only":
        not_checked.insert(0, "block export")
        not_checked.insert(1, "style export")
    elif export_mode == "block_export":
        not_checked.insert(0, "native block definition write")
    elif export_mode == "style_export":
        not_checked.insert(0, "native style definition write")
    return {
        "status": "metadata_only",
        "checked": [
            "system_library package path reserved",
            "machine contract written",
            "global registry updated",
            "lifecycle status recorded",
            "retrieval fields recorded",
            "native DWG layout plan recorded",
            "source boundary recorded",
            "anti-contamination gate recorded",
        ],
        "notChecked": not_checked,
    }


def _feedback_loop(
    *,
    feedback_refs: list[str] | None,
    promotion_refs: list[str] | None,
    failure_reason: str | None,
) -> dict[str, Any]:
    return {
        "feedbackRefs": _unique_strings(feedback_refs),
        "promotionRefs": _unique_strings(promotion_refs),
        "failureReason": str(failure_reason).strip() if failure_reason else "",
        "nextReviewAction": "reuse_failure_or_user_correction_should_update_this_asset_or_spawn_retraining",
    }


def _layout_plan(asset: dict[str, Any], index: int) -> dict[str, Any]:
    asset_id = str(asset.get("assetId", ""))
    export_manifest = _dict_or_empty(asset.get("exportManifest"))
    return build_asset_library_layout_plan(
        asset_id=asset_id,
        index=index,
        asset_name=str(asset.get("name") or asset_id),
        category=str(asset.get("category") or ""),
        asset_kind=str(asset.get("assetKind") or export_manifest.get("assetKind") or ""),
        export_manifest=export_manifest,
        evidence_refs=[str(ref) for ref in asset.get("evidenceRefs", []) if ref],
        native_write=str(export_manifest.get("nativeWrite") or "deferred_until_explicit_cad_export_approval"),
    )


def _assign_layout_plans(assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    planned_assets: list[dict[str, Any]] = []
    for index, asset in enumerate(sorted(assets, key=lambda row: str(row.get("assetId", "")))):
        planned = dict(asset)
        native = dict(planned.get("native", {}))
        export_manifest = _dict_or_empty(planned.get("exportManifest"))
        anti_contamination = _dict_or_empty(planned.get("antiContamination"))
        verification = _dict_or_empty(planned.get("verification"))
        native["layoutPlan"] = _layout_plan(planned, index)
        planned["native"] = native
        planned["libraryGovernance"] = build_asset_library_governance(
            asset_id=str(planned.get("assetId", "")),
            category=str(planned.get("category", "")),
            asset_kind=str(planned.get("assetKind") or export_manifest.get("assetKind") or ""),
            export_manifest=export_manifest,
            anti_contamination=anti_contamination,
            layout_plan=native["layoutPlan"],
            native_dwg_exists=bool(native.get("nativeDwgExists")),
            lifecycle_status=_asset_contract_lifecycle_status(planned),
            verification_status=str(verification.get("status") or planned.get("verificationStatus") or "metadata_only"),
            model_review_report=_dict_or_empty(
                planned.get("modelGovernorReview") or planned.get("modelAssetGovernorReview")
            ),
        )
        planned_assets.append(planned)
    return planned_assets


def _find_asset(assets: list[dict[str, Any]], asset_id: str) -> dict[str, Any] | None:
    for asset in assets:
        if isinstance(asset, dict) and str(asset.get("assetId", "")) == asset_id:
            return asset
    return None


def _material_conflict(existing: dict[str, Any] | None, *, dimensions: dict[str, Any] | None, block_name: str | None) -> bool:
    if not existing:
        return False
    existing_dimensions = existing.get("dimensions")
    if dimensions and isinstance(existing_dimensions, dict) and existing_dimensions and existing_dimensions != dimensions:
        return True
    existing_native = existing.get("native")
    existing_block_name = existing_native.get("blockName", "") if isinstance(existing_native, dict) else ""
    clean_block_name = str(block_name).strip() if block_name else ""
    return bool(clean_block_name and existing_block_name and clean_block_name != existing_block_name)


def _next_variant_asset_id(existing_assets: list[dict[str, Any]], base_asset_id: str) -> str:
    existing_ids = {str(asset.get("assetId", "")) for asset in existing_assets if isinstance(asset, dict)}
    index = 2
    while True:
        candidate = f"{base_asset_id}_v{index}"
        if candidate not in existing_ids:
            return candidate
        index += 1


def resolve_system_asset_location(
    category: str,
    *,
    native_library_stem: str | None = None,
) -> SystemAssetLocation:
    """Resolve a category like ``furniture.seating.sofas`` to stable paths."""

    tokens = _category_tokens(category)
    category_path = "/".join(tokens)
    package_rel = SYSTEM_LIBRARY_REL / Path(*tokens)
    native_stem = _safe_token(native_library_stem) if native_library_stem else _default_native_stem(tokens)
    native_rel = package_rel / f"{native_stem}_assets.dwg"
    contract_rel = package_rel / "assets.json"
    return SystemAssetLocation(
        category=".".join(tokens),
        category_path=category_path,
        package_path=package_rel.as_posix(),
        contract_path=contract_rel.as_posix(),
        native_dwg_path=native_rel.as_posix(),
    )


def _asset_entry(
    *,
    asset_id: str,
    name: str,
    category: str,
    location: SystemAssetLocation,
    aliases: list[str] | None,
    use_when: list[str] | None,
    tags: list[str] | None,
    scenario_tags: list[str] | None,
    constraints: list[str] | None,
    dimensions: dict[str, Any] | None,
    block_name: str | None,
    evidence_refs: list[str] | None,
    source: dict[str, Any] | None,
    asset_kind: str,
    export_manifest: dict[str, Any],
    anti_contamination: dict[str, Any],
    status: str,
    feedback_refs: list[str] | None,
    promotion_refs: list[str] | None,
    failure_reason: str | None,
    conflict_policy: str,
    derived_from_asset_id: str,
    revision: int,
    history: list[dict[str, Any]],
    native_dwg_exists: bool,
    generated_at: str,
) -> dict[str, Any]:
    clean_name = str(name).strip() or asset_id
    retrieval = _retrieval_contract(
        name=clean_name,
        aliases=aliases,
        use_when=use_when,
        tags=tags,
        scenario_tags=scenario_tags,
        dimensions=dimensions,
        constraints=constraints,
    )
    return {
        "assetId": asset_id,
        "name": clean_name,
        "category": category,
        "aliases": retrieval["aliases"],
        "useWhen": retrieval["useWhen"],
        "tags": retrieval["tags"],
        "dimensions": dimensions or {},
        "retrieval": retrieval,
        "native": {
            "dwg": location.native_dwg_path,
            "blockName": str(block_name).strip() if block_name else "",
            "nativeDwgExists": native_dwg_exists,
            "layoutPolicy": "append_to_category_library_grid",
        },
        "source": source or {"type": "manual_metadata"},
        "assetKind": asset_kind,
        "exportManifest": export_manifest,
        "antiContamination": anti_contamination,
        "evidenceRefs": _unique_strings(evidence_refs),
        "status": status,
        "lifecycle": {
            "status": status,
            "allowedStatuses": list(ALLOWED_ASSET_STATUSES),
            "promotionGate": [
                "metadata contract",
                "native DWG export or explicit native-deferred boundary",
                "reuse verification report",
                "user or machine acceptance evidence",
            ],
            "updatedAt": generated_at,
        },
        "versioning": {
            "revision": revision,
            "conflictPolicy": conflict_policy,
            "derivedFromAssetId": derived_from_asset_id,
            "history": history,
        },
        "verification": _verification_contract(native_dwg_exists=native_dwg_exists, export_manifest=export_manifest),
        "feedbackLoop": _feedback_loop(
            feedback_refs=feedback_refs,
            promotion_refs=promotion_refs,
            failure_reason=failure_reason,
        ),
        "updatedAt": generated_at,
        "evidenceBoundary": {
            "checked": [
                "system_library package path reserved",
                "machine contract written",
                "global registry updated",
                "asset lifecycle recorded",
                "retrieval contract recorded",
                "native DWG layout plan recorded",
                "source boundary recorded",
                "anti-contamination gate recorded",
            ],
            "not_checked": [
                "native DWG export",
                "active DWG save",
                "CAD geometry replay",
                "user visual approval",
            ],
        },
    }


def _upsert_asset(assets: list[dict[str, Any]], entry: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = {str(asset.get("assetId", "")): dict(asset) for asset in assets if isinstance(asset, dict)}
    by_id[str(entry["assetId"])] = entry
    return [by_id[asset_id] for asset_id in sorted(by_id)]


def _package_contract(
    *,
    location: SystemAssetLocation,
    existing: dict[str, Any],
    asset_entry: dict[str, Any],
    generated_at: str,
    native_dwg_exists: bool,
) -> dict[str, Any]:
    assets = existing.get("assets")
    if not isinstance(assets, list):
        assets = []
    return {
        "schemaVersion": 1,
        "packageId": location.category.replace(".", "-"),
        "category": location.category,
        "packagePath": location.package_path,
        "nativeDwg": location.native_dwg_path,
        "nativeDwgExists": native_dwg_exists,
        "updatedAt": generated_at,
        "lifecycle": {
            "allowedStatuses": list(ALLOWED_ASSET_STATUSES),
            "defaultStatus": "candidate",
            "promotionOrder": ["candidate", "systemized", "verified"],
            "retirementStatus": "deprecated",
        },
        "nativeLayout": _native_layout_contract(),
        "tools": {
            "apply": "scripts/sediment_system_asset.py",
            "verify": "scripts/sediment_system_asset.py --verify",
            "verifyContract": "core.assets.system_asset_sedimentation.verify_system_asset_package",
            "nativeExport": "deferred_until_explicit_cad_write_approval",
            "recordFeedback": "scripts/sediment_system_asset.py --feedback-ref",
        },
        "assets": _assign_layout_plans(_upsert_asset(assets, asset_entry)),
        "evidenceBoundary": {
            "checked": ["contract", "registry", "reserved native CAD library path", "lifecycle", "retrieval", "layout plan v2", "asset governance decision"],
            "not_checked": ["native CAD library file may not exist yet", "native geometry reuse is checked by a later CAD step"],
        },
    }


def _native_layout_contract(*, native_write: str = "deferred_until_explicit_cad_write_approval") -> dict[str, Any]:
    return {
        "schemaVersion": 2,
        "policy": "governed_category_library_zones",
        "gridColumns": LAYOUT_GRID_COLUMNS,
        "zones": ["00_INDEX", "01_CLEAN_ASSETS", "02_PREVIEW_CARDS", "03_REVIEW_QUARANTINE", "99_EVIDENCE_LINKS"],
        "nativeWrite": native_write,
    }


def _registry_asset_entry(asset: dict[str, Any], location: SystemAssetLocation) -> dict[str, Any]:
    native = asset.get("native", {}) if isinstance(asset.get("native"), dict) else {}
    verification = asset.get("verification", {}) if isinstance(asset.get("verification"), dict) else {}
    evidence = verification.get("evidence", {}) if isinstance(verification.get("evidence"), dict) else {}
    entry = {
        "assetId": asset["assetId"],
        "name": asset["name"],
        "category": location.category,
        "packagePath": location.package_path,
        "contractPath": location.contract_path,
        "nativeDwg": location.native_dwg_path,
        "nativeDwgExists": bool(native.get("nativeDwgExists") or asset.get("nativeDwgExists")),
        "aliases": asset.get("aliases", []),
        "useWhen": asset.get("useWhen", []),
        "tags": asset.get("tags", []),
        "retrieval": asset.get("retrieval", {}),
        "assetKind": asset.get("assetKind", ""),
        "exportManifest": asset.get("exportManifest", {}),
        "antiContaminationDecision": asset.get("antiContamination", {}).get("decision", ""),
        "evidenceRefs": asset.get("evidenceRefs", []),
        "status": asset.get("status", "contract_registered"),
        "lifecycleStatus": asset.get("lifecycle", {}).get("status", asset.get("status", "")),
        "verificationStatus": asset.get("verification", {}).get("status", ""),
        "nativeLayoutPlan": asset.get("native", {}).get("layoutPlan", {}),
        "libraryGovernance": asset.get("libraryGovernance", {}),
        "polishHardeningDecision": asset.get("libraryGovernance", {}).get("polishHardeningDecision", {}),
        "feedbackRefs": asset.get("feedbackLoop", {}).get("feedbackRefs", []),
        "updatedAt": asset.get("updatedAt", ""),
    }
    native_visible = native.get("nativeVisiblePanelEvidence") or asset.get("nativeVisiblePanelEvidence") or evidence.get("nativeVisiblePanel")
    if isinstance(native_visible, dict):
        entry["nativeVisiblePanelEvidence"] = native_visible
    reuse_probe = asset.get("reuseWorkflowProbe") or native.get("reuseWorkflowProbe") or evidence.get("reuseWorkflowProbe")
    if isinstance(reuse_probe, dict):
        entry["reuseWorkflowProbe"] = reuse_probe
    return entry


def _registry_package_entry(location: SystemAssetLocation, native_dwg_exists: bool, generated_at: str) -> dict[str, Any]:
    return {
        "category": location.category,
        "packagePath": location.package_path,
        "contractPath": location.contract_path,
        "nativeDwg": location.native_dwg_path,
        "nativeDwgExists": native_dwg_exists,
        "updatedAt": generated_at,
    }


def _registry_contract(
    *,
    existing: dict[str, Any],
    location: SystemAssetLocation,
    asset: dict[str, Any],
    native_dwg_exists: bool,
    generated_at: str,
) -> dict[str, Any]:
    packages = existing.get("packages")
    if not isinstance(packages, list):
        packages = []
    assets = existing.get("assets")
    if not isinstance(assets, list):
        assets = []

    package_entry = _registry_package_entry(location, native_dwg_exists, generated_at)
    package_by_category = {
        str(package.get("category", "")): dict(package)
        for package in packages
        if isinstance(package, dict)
    }
    package_by_category[location.category] = package_entry

    asset_entry = _registry_asset_entry(asset, location)
    asset_by_id = {
        str(row.get("assetId", "")): dict(row)
        for row in assets
        if isinstance(row, dict)
    }
    asset_by_id[str(asset_entry["assetId"])] = asset_entry

    return {
        "schemaVersion": 1,
        "updatedAt": generated_at,
        "description": "System asset registry. Use this before raw/reference libraries when a promoted self-owned asset matches the request.",
        "packages": [package_by_category[key] for key in sorted(package_by_category)],
        "assets": [asset_by_id[key] for key in sorted(asset_by_id)],
        "evidenceBoundary": {
            "checked": ["registry entries point to system_library contracts"],
            "not_checked": ["native DWG file existence is recorded per package"],
        },
    }


def refresh_system_asset_layout_metadata(
    *,
    project_root: Path = PROJECT_ROOT,
    category: str,
    native_library_stem: str | None = None,
    native_layout_write_status: str | None = None,
    visual_rack_plan: dict[str, Any] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Refresh layoutPlan v2 and registry search metadata for an existing package."""

    root = Path(project_root)
    generated = generated_at or _utc_now()
    encoding_preflight = assert_no_text_encoding_corruption(str(root), category, native_library_stem or "")
    location = resolve_system_asset_location(category, native_library_stem=native_library_stem)
    contract_path = root / location.contract_path
    registry_path = root / REGISTRY_REL
    contract = _read_json_object(contract_path, {})
    issues: list[str] = []
    if not contract:
        issues.append(f"missing package contract: {location.contract_path}")
    assets = contract.get("assets") if isinstance(contract, dict) else []
    if not isinstance(assets, list):
        assets = []
        issues.append("contract assets must be a list")
    if issues:
        return {
            "status": "fail",
            "category": location.category,
            "contractPath": location.contract_path,
            "registryPath": REGISTRY_REL.as_posix(),
            "issues": issues,
            "wroteContract": False,
            "wroteRegistry": False,
            "encodingPreflight": encoding_preflight,
        }

    visual_rack_audit: dict[str, Any] = {}
    if visual_rack_plan:
        visual_rack_audit = audit_visual_rack_plan(visual_rack_plan=visual_rack_plan)
        if visual_rack_audit.get("status") != "pass":
            return {
                "status": "fail",
                "category": location.category,
                "contractPath": location.contract_path,
                "registryPath": REGISTRY_REL.as_posix(),
                "issues": list(visual_rack_audit.get("issues", [])),
                "visualRackAudit": visual_rack_audit,
                "wroteContract": False,
                "wroteRegistry": False,
                "encodingPreflight": encoding_preflight,
            }

    planned_assets = _assign_layout_plans([dict(asset) for asset in assets if isinstance(asset, dict)])
    native_dwg_exists = (root / location.native_dwg_path).is_file()
    existing_native_layout = _dict_or_empty(contract.get("nativeLayout"))
    native_layout_write = str(
        native_layout_write_status
        or existing_native_layout.get("nativeWrite")
        or "deferred_until_explicit_cad_write_approval"
    )
    native_layout = _native_layout_contract(native_write=native_layout_write)
    if visual_rack_plan:
        native_layout["visualRackPlan"] = visual_rack_plan
    contract.update(
        {
            "schemaVersion": int(contract.get("schemaVersion") or 1),
            "packageId": location.category.replace(".", "-"),
            "category": location.category,
            "packagePath": location.package_path,
            "nativeDwg": location.native_dwg_path,
            "nativeDwgExists": native_dwg_exists,
            "updatedAt": generated,
            "lifecycle": {
                "allowedStatuses": list(ALLOWED_ASSET_STATUSES),
                "defaultStatus": "candidate",
                "promotionOrder": ["candidate", "systemized", "verified"],
                "retirementStatus": "deprecated",
            },
            "nativeLayout": native_layout,
            "tools": {
                "apply": "scripts/sediment_system_asset.py",
                "verify": "scripts/sediment_system_asset.py --verify",
                "verifyContract": "core.assets.system_asset_sedimentation.verify_system_asset_package",
                "nativeExport": "deferred_until_explicit_cad_write_approval",
                "recordFeedback": "scripts/sediment_system_asset.py --feedback-ref",
            },
            "assets": planned_assets,
            "evidenceBoundary": {
                "checked": ["contract", "registry", "layout plan v2", "asset governance decision"],
                "not_checked": ["native geometry reuse is checked by a later CAD step"],
            },
        }
    )
    _write_json(contract_path, contract)

    registry = _read_json_object(registry_path, {})
    for asset in planned_assets:
        registry = _registry_contract(
            existing=registry,
            location=location,
            asset=asset,
            native_dwg_exists=native_dwg_exists,
            generated_at=generated,
        )
    _write_json(registry_path, registry)

    return {
        "status": "pass",
        "category": location.category,
        "contractPath": location.contract_path,
        "registryPath": REGISTRY_REL.as_posix(),
        "nativeDwg": location.native_dwg_path,
        "nativeDwgExists": native_dwg_exists,
        "updatedAt": generated,
        "updatedAssetCount": len(planned_assets),
        "updatedAssetIds": [str(asset.get("assetId", "")) for asset in planned_assets],
        "layoutSchemaVersion": 2,
        "nativeLayoutWrite": native_layout_write,
        "visualRackPlan": visual_rack_plan or {},
        "visualRackAudit": visual_rack_audit,
        "wroteContract": True,
        "wroteRegistry": True,
        "encodingPreflight": encoding_preflight,
    }


def sediment_system_asset(
    *,
    project_root: Path = PROJECT_ROOT,
    asset_id: str,
    name: str,
    category: str,
    aliases: list[str] | None = None,
    use_when: list[str] | None = None,
    tags: list[str] | None = None,
    scenario_tags: list[str] | None = None,
    constraints: list[str] | None = None,
    dimensions: dict[str, Any] | None = None,
    block_name: str | None = None,
    evidence_refs: list[str] | None = None,
    source: dict[str, Any] | None = None,
    asset_kind: str | None = None,
    export_mode: str | None = None,
    source_boundary_mode: str | None = None,
    included_handles: list[str] | None = None,
    excluded_handles: list[str] | None = None,
    status: str | None = None,
    feedback_refs: list[str] | None = None,
    promotion_refs: list[str] | None = None,
    failure_reason: str | None = None,
    conflict_policy: str | None = None,
    native_library_stem: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Create or update a system-library asset contract and global registry."""

    root = Path(project_root)
    encoding_preflight = assert_no_text_encoding_corruption(
        str(root),
        asset_id,
        name,
        category,
        aliases or [],
        use_when or [],
        tags or [],
        scenario_tags or [],
        constraints or [],
        evidence_refs or [],
        source or {},
        block_name or "",
        feedback_refs or [],
        promotion_refs or [],
        failure_reason or "",
        native_library_stem or "",
    )
    generated = generated_at or _utc_now()
    location = resolve_system_asset_location(category, native_library_stem=native_library_stem)
    native_dwg_exists = (root / location.native_dwg_path).is_file()
    clean_status = _asset_status(status)
    clean_conflict_policy = _conflict_policy(conflict_policy)
    clean_asset_id = _safe_token(asset_id)
    clean_asset_kind = _infer_asset_kind(location.category, asset_kind)
    source_boundary = _source_boundary_contract(
        source=source,
        source_boundary_mode=source_boundary_mode,
        included_handles=included_handles,
        excluded_handles=excluded_handles,
    )
    export_manifest, anti_contamination = _export_contracts(
        asset_kind=clean_asset_kind,
        export_mode=export_mode,
        source_boundary=source_boundary,
        block_name=block_name,
    )

    contract_path = root / location.contract_path
    existing_contract = _read_json_object(contract_path, {})
    existing_assets = existing_contract.get("assets")
    if not isinstance(existing_assets, list):
        existing_assets = []
    existing_asset = _find_asset(existing_assets, clean_asset_id)
    has_conflict = _material_conflict(existing_asset, dimensions=dimensions, block_name=block_name)
    derived_from_asset_id = ""
    if has_conflict and clean_conflict_policy == "reject":
        raise ValueError(f"asset {clean_asset_id!r} already exists with different dimensions or blockName")
    if has_conflict and clean_conflict_policy == "new_variant":
        derived_from_asset_id = clean_asset_id
        clean_asset_id = _next_variant_asset_id(existing_assets, clean_asset_id)
        existing_asset = None

    versioning = existing_asset.get("versioning", {}) if isinstance(existing_asset, dict) else {}
    history = versioning.get("history", []) if isinstance(versioning, dict) else []
    if not isinstance(history, list):
        history = []
    revision = int(versioning.get("revision", 0)) + 1 if isinstance(versioning, dict) else 1
    if existing_asset:
        history = [
            *history,
            {
                "assetId": existing_asset.get("assetId", ""),
                "name": existing_asset.get("name", ""),
                "status": existing_asset.get("status", ""),
                "updatedAt": existing_asset.get("updatedAt", ""),
            },
        ]

    entry = _asset_entry(
        asset_id=clean_asset_id,
        name=name,
        category=location.category,
        location=location,
        aliases=aliases,
        use_when=use_when,
        tags=tags,
        scenario_tags=scenario_tags,
        constraints=constraints,
        dimensions=dimensions,
        block_name=block_name,
        evidence_refs=evidence_refs,
        source=source,
        asset_kind=clean_asset_kind,
        export_manifest=export_manifest,
        anti_contamination=anti_contamination,
        status=clean_status,
        feedback_refs=feedback_refs,
        promotion_refs=promotion_refs,
        failure_reason=failure_reason,
        conflict_policy=clean_conflict_policy,
        derived_from_asset_id=derived_from_asset_id,
        revision=revision,
        history=history,
        native_dwg_exists=native_dwg_exists,
        generated_at=generated,
    )

    contract = _package_contract(
        location=location,
        existing=existing_contract,
        asset_entry=entry,
        generated_at=generated,
        native_dwg_exists=native_dwg_exists,
    )
    _write_json(contract_path, contract)
    final_asset = _find_asset(contract["assets"], clean_asset_id) or entry

    registry_path = root / REGISTRY_REL
    registry = _registry_contract(
        existing=_read_json_object(registry_path, {}),
        location=location,
        asset=final_asset,
        native_dwg_exists=native_dwg_exists,
        generated_at=generated,
    )
    _write_json(registry_path, registry)

    return {
        "status": "pass",
        "assetId": final_asset["assetId"],
        "assetStatus": final_asset["lifecycle"]["status"],
        "category": location.category,
        "packagePath": location.package_path,
        "contractPath": location.contract_path,
        "nativeDwg": location.native_dwg_path,
        "nativeDwgExists": native_dwg_exists,
        "registryPath": REGISTRY_REL.as_posix(),
        "verification": final_asset["verification"],
        "exportManifest": final_asset["exportManifest"],
        "antiContamination": final_asset["antiContamination"],
        "libraryGovernance": final_asset.get("libraryGovernance", {}),
        "nativeLayoutPlan": final_asset.get("native", {}).get("layoutPlan", {}),
        "polishHardeningDecision": final_asset.get("libraryGovernance", {}).get("polishHardeningDecision", {}),
        "wroteCad": False,
        "savedDwg": False,
        "deletedEntities": False,
        "modifiedFormalLayers": False,
        "location": asdict(location),
        "evidenceBoundary": final_asset["evidenceBoundary"],
        "encodingPreflight": encoding_preflight,
    }


def verify_system_asset_package(
    *,
    project_root: Path = PROJECT_ROOT,
    category: str,
    native_library_stem: str | None = None,
    asset_id: str | None = None,
) -> dict[str, Any]:
    """Verify the repository-side contract for a system asset package.

    This verification always checks metadata, then applies claim gates for
    stronger asset states. A style asset that claims native style definitions
    must also carry visible native asset evidence. A verified asset must also
    carry an executable reuse workflow probe or a real reuse replay summary.
    """

    root = Path(project_root)
    encoding_preflight = assert_no_text_encoding_corruption(
        str(root),
        category,
        native_library_stem or "",
        asset_id or "",
    )
    location = resolve_system_asset_location(category, native_library_stem=native_library_stem)
    contract_path = root / location.contract_path
    registry_path = root / REGISTRY_REL
    issues: list[str] = []
    checked: list[str] = []

    contract = _read_json_object(contract_path, {})
    if not contract:
        issues.append(f"missing package contract: {location.contract_path}")
    else:
        checked.append("metadata contract")
    registry = _read_json_object(registry_path, {})
    if not registry:
        issues.append(f"missing system asset registry: {REGISTRY_REL.as_posix()}")
    else:
        checked.append("global registry")

    assets = contract.get("assets") if isinstance(contract, dict) else []
    if not isinstance(assets, list):
        assets = []
        issues.append("contract assets must be a list")
    if asset_id:
        clean_asset_id = _safe_token(asset_id)
        assets = [asset for asset in assets if isinstance(asset, dict) and asset.get("assetId") == clean_asset_id]
        if not assets:
            issues.append(f"asset {clean_asset_id!r} not found in package")

    required_fields = (
        "lifecycle",
        "retrieval",
        "native",
        "verification",
        "feedbackLoop",
        "versioning",
        "exportManifest",
        "antiContamination",
        "libraryGovernance",
    )
    for asset in assets:
        if not isinstance(asset, dict):
            issues.append("asset rows must be objects")
            continue
        for field in required_fields:
            if not isinstance(asset.get(field), dict):
                issues.append(f"asset {asset.get('assetId', '<unknown>')} missing {field}")
        lifecycle = asset.get("lifecycle", {})
        if isinstance(lifecycle, dict) and lifecycle.get("status") not in ALLOWED_ASSET_STATUSES:
            issues.append(f"asset {asset.get('assetId', '<unknown>')} has invalid lifecycle status")
        retrieval = asset.get("retrieval", {})
        if isinstance(retrieval, dict) and not retrieval.get("matchText"):
            issues.append(f"asset {asset.get('assetId', '<unknown>')} has empty retrieval matchText")
        export_manifest = asset.get("exportManifest", {})
        if isinstance(export_manifest, dict):
            if export_manifest.get("assetKind") not in ASSET_KINDS:
                issues.append(f"asset {asset.get('assetId', '<unknown>')} has invalid assetKind")
            if export_manifest.get("exportMode") not in EXPORT_MODES:
                issues.append(f"asset {asset.get('assetId', '<unknown>')} has invalid exportMode")
            source_boundary = export_manifest.get("sourceBoundary", {})
            if not isinstance(source_boundary, dict) or not source_boundary.get("mode"):
                issues.append(f"asset {asset.get('assetId', '<unknown>')} missing source boundary mode")
        native = asset.get("native", {})
        if isinstance(native, dict):
            layout_plan = native.get("layoutPlan")
            if not isinstance(layout_plan, dict):
                issues.append(f"asset {asset.get('assetId', '<unknown>')} missing native layoutPlan")
            else:
                if int(layout_plan.get("schemaVersion", 0)) < 2:
                    issues.append(f"asset {asset.get('assetId', '<unknown>')} missing layoutPlan v2")
                for field in ("zones", "slot", "plannedBbox", "cleanSource", "previewCard", "evidenceLinks", "cleanupPolicy"):
                    if field not in layout_plan:
                        issues.append(f"asset {asset.get('assetId', '<unknown>')} layoutPlan missing {field}")
        governance = asset.get("libraryGovernance", {})
        if isinstance(governance, dict):
            if governance.get("governorAgentId") != "pipeline_asset_governor":
                issues.append(f"asset {asset.get('assetId', '<unknown>')} missing asset governor decision")
            if not isinstance(governance.get("polishHardeningDecision"), dict):
                issues.append(f"asset {asset.get('assetId', '<unknown>')} missing polish hardening decision")

    asset_verification_statuses: dict[str, str] = {}
    asset_evidence_checked: list[str] = []
    asset_evidence_not_checked: list[str] = []
    claim_gate_not_checked: list[str] = []
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        verification = asset.get("verification", {})
        if not isinstance(verification, dict):
            continue
        asset_key = str(asset.get("assetId", "<unknown>"))
        lifecycle_status = _asset_contract_lifecycle_status(asset)
        asset_kind = _asset_contract_kind(asset)
        export_mode = _asset_contract_export_mode(asset)
        verification_status = _asset_contract_verification_status(asset)
        manifest = _dict_or_empty(asset.get("exportManifest"))
        native_write = str(manifest.get("nativeWrite") or "")
        asset_verification_statuses[asset_key] = verification_status
        checked_items = verification.get("checked", [])
        if isinstance(checked_items, list):
            asset_evidence_checked.extend(str(item) for item in checked_items)
        not_checked_items = verification.get("notChecked", [])
        if isinstance(not_checked_items, list):
            asset_evidence_not_checked.extend(str(item) for item in not_checked_items)
        native_style_claim = (
            asset_kind == "style_standard"
            and export_mode == "style_export"
            and (verification_status == "native_style_definition_written" or native_write == "written_to_standard_assets_dwg")
        )
        if native_style_claim:
            if _has_native_visible_asset_evidence(asset):
                checked.append("native visible asset evidence")
            else:
                issues.append(f"asset {asset_key} missing native visible asset evidence")
                claim_gate_not_checked.append("native visible asset evidence")
        if lifecycle_status == "verified":
            if _has_executable_reuse_probe(asset):
                checked.append("executable reuse workflow probe")
            else:
                issues.append(f"asset {asset_key} missing executable reuse workflow probe")
                claim_gate_not_checked.append("executable reuse workflow probe")

    if assets:
        checked.extend([
            "lifecycle status",
            "retrieval fields",
            "native DWG layout plan",
            "native DWG layout plan v2",
            "asset library governance decision",
            "verification contract",
            "source boundary",
            "anti-contamination gate",
        ])

    native_dwg_exists = (root / location.native_dwg_path).is_file()
    if isinstance(contract, dict) and contract:
        if bool(contract.get("nativeDwgExists", False)) != native_dwg_exists:
            issues.append("contract nativeDwgExists does not match filesystem")
        else:
            checked.append("native DWG existence flag")

    registry_assets = registry.get("assets") if isinstance(registry, dict) else []
    if isinstance(registry_assets, list):
        registry_ids = {str(asset.get("assetId", "")) for asset in registry_assets if isinstance(asset, dict)}
        for asset in assets:
            if isinstance(asset, dict) and str(asset.get("assetId", "")) not in registry_ids:
                issues.append(f"asset {asset.get('assetId', '<unknown>')} missing from registry")
    elif registry:
        issues.append("registry assets must be a list")

    return {
        "status": "pass" if not issues else "fail",
        "category": location.category,
        "assetCount": len(assets),
        "contractPath": location.contract_path,
        "registryPath": REGISTRY_REL.as_posix(),
        "nativeDwg": location.native_dwg_path,
        "nativeDwgExists": native_dwg_exists,
        "checked": _unique_strings(checked),
        "assetVerificationStatuses": asset_verification_statuses,
        "assetEvidenceChecked": _unique_strings(asset_evidence_checked),
        "assetEvidenceNotChecked": _unique_strings(asset_evidence_not_checked),
        "notChecked": _unique_strings(
            [
                "native DWG geometry",
                "CAD insertion replay",
                "active DWG save",
                "user visual approval",
                *claim_gate_not_checked,
            ]
        ),
        "issues": issues,
        "wroteCad": False,
        "savedDwg": False,
        "encodingPreflight": encoding_preflight,
    }
