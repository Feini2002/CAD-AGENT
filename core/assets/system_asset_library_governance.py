"""Asset-library governance and layout planning helpers."""

from __future__ import annotations

from typing import Any

from core.model_review.asset_governor_review import model_review_to_asset_governor_assistance


LAYOUT_PLAN_SCHEMA_VERSION = 2
LAYOUT_GRID_COLUMNS = 4
SLOT_WIDTH = 4200
SLOT_HEIGHT = 2600
SLOT_GAP = 600

LIBRARY_ZONES: tuple[dict[str, Any], ...] = (
    {
        "zoneId": "00_INDEX",
        "title": "资产目录区",
        "purpose": "Only catalog rows, asset ids, status, and slot references.",
        "copySourceAllowed": False,
    },
    {
        "zoneId": "01_CLEAN_ASSETS",
        "title": "干净资产区",
        "purpose": "Only reusable block geometry, style definitions, symbols, or clean source samples.",
        "copySourceAllowed": True,
    },
    {
        "zoneId": "02_PREVIEW_CARDS",
        "title": "资产卡片区",
        "purpose": "Human-readable preview cards with labels, dimensions, usage, and state.",
        "copySourceAllowed": False,
    },
    {
        "zoneId": "03_REVIEW_QUARANTINE",
        "title": "待复审区",
        "purpose": "Candidates with unclear source boundaries or unclean training output.",
        "copySourceAllowed": False,
    },
    {
        "zoneId": "99_EVIDENCE_LINKS",
        "title": "证据索引区",
        "purpose": "Evidence refs, reports, screenshots, and training provenance references.",
        "copySourceAllowed": False,
    },
)

TRAINING_CONTAMINATION_TYPES = (
    "training_title",
    "training_notes",
    "temporary_labels",
    "table_borders",
    "dimensions",
    "audit_notes",
    "evidence_text",
    "course_description",
    "screenshot_caption",
)

DEFAULT_CHILD_AGENTS = (
    "pipeline_asset_librarian",
    "pipeline_asset_dwg_curator",
    "pipeline_asset_reuse_auditor",
)
PRIMARY_WAREHOUSE_ZONES = ("01_CLEAN_ASSETS", "B_OBJECT_ASSET_INDEX")
REVIEW_ONLY_ZONES = ("02_PREVIEW_CARDS", "03_REVIEW_QUARANTINE", "99_EVIDENCE_LINKS")
REQUIRED_VISUAL_ACCEPTANCE_KEYS = (
    "slotContainment",
    "assetOwnership",
    "expansionCapacity",
    "copyPolicy",
    "screenshotBoundary",
)
FORBIDDEN_PROTECTED_CONTENT_LAYERS = {"CODEX_PREVIEW"}
PROOF_ROLE_CONFLICT_LAYERS = {"ASSET_SOURCE_BOUNDARY"}


def _unique(values: list[str] | tuple[str, ...] | None) -> list[str]:
    result: list[str] = []
    for value in values or []:
        text = str(value).strip()
        if text and text not in result:
            result.append(text)
    return result


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _zone(zone_id: str) -> dict[str, Any]:
    for zone in LIBRARY_ZONES:
        if zone["zoneId"] == zone_id:
            return dict(zone)
    raise ValueError(f"unknown asset library zone: {zone_id}")


def _slot_bbox(row: int, column: int, *, band_offset_y: int = 0) -> dict[str, int]:
    x = column * (SLOT_WIDTH + SLOT_GAP)
    y = band_offset_y - row * (SLOT_HEIGHT + SLOT_GAP)
    return {
        "minX": x,
        "minY": y - SLOT_HEIGHT,
        "maxX": x + SLOT_WIDTH,
        "maxY": y,
    }


def _source_mode(source_boundary: dict[str, Any]) -> str:
    return str(source_boundary.get("mode") or "manual_metadata")


def _bbox_area(bbox: Any) -> float:
    box = _dict(bbox)
    if {"min", "max"}.issubset(box):
        min_pt = box.get("min")
        max_pt = box.get("max")
        if isinstance(min_pt, list) and isinstance(max_pt, list) and len(min_pt) >= 2 and len(max_pt) >= 2:
            return max(0.0, float(max_pt[0]) - float(min_pt[0])) * max(0.0, float(max_pt[1]) - float(min_pt[1]))
    if {"minX", "minY", "maxX", "maxY"}.issubset(box):
        return max(0.0, float(box["maxX"]) - float(box["minX"])) * max(0.0, float(box["maxY"]) - float(box["minY"]))
    return 0.0


def _add_layer_count(layer_counts: dict[str, int], layer: str, count: int = 1) -> None:
    text = str(layer).strip()
    if not text:
        return
    layer_counts[text] = layer_counts.get(text, 0) + max(0, int(count))


def _protected_content_layer_census(protected_content_report: dict[str, Any]) -> tuple[dict[str, int], list[str]]:
    """Return full protected-content layer counts and census issues.

    `layerSamples` is intentionally insufficient: it caused A1/A2 proof
    content on CODEX_PREVIEW to disappear from reports when the bad layer was
    outside the small sample window.
    """

    issues: list[str] = []
    layer_counts: dict[str, int] = {}
    saw_full_census = False
    saw_sample_only = False
    top_counts = protected_content_report.get("layerCounts")
    if isinstance(top_counts, dict) and top_counts:
        for layer, count in top_counts.items():
            _add_layer_count(layer_counts, str(layer), int(count or 0))
        return layer_counts, issues
    clusters = [cluster for cluster in _list(protected_content_report.get("clusters")) if isinstance(cluster, dict)]
    if not clusters:
        issues.append("protected asset content readback missing")
        return layer_counts, issues
    for cluster in clusters:
        cluster_counts = cluster.get("layerCounts")
        if isinstance(cluster_counts, dict) and cluster_counts:
            saw_full_census = True
            for layer, count in cluster_counts.items():
                _add_layer_count(layer_counts, str(layer), int(count or 0))
            continue
        full_layers = cluster.get("layers") or cluster.get("allLayers")
        if isinstance(full_layers, list) and full_layers:
            saw_full_census = True
            for layer in full_layers:
                _add_layer_count(layer_counts, str(layer), 1)
            continue
        if cluster.get("layerSamples"):
            saw_sample_only = True
            for layer in _list(cluster.get("layerSamples")):
                _add_layer_count(layer_counts, str(layer), 1)
    top_layers = protected_content_report.get("layers") or protected_content_report.get("allLayers")
    if isinstance(top_layers, list) and top_layers:
        saw_full_census = True
        for layer in top_layers:
            layer_counts.setdefault(str(layer), 0)
    if saw_sample_only and not saw_full_census:
        issues.append("protected content layer census missing; layerSamples is not enough")
    return layer_counts, issues


def _rack_families_by_id(visual_rack_plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for family in _list(visual_rack_plan.get("rackFamilies")):
        if not isinstance(family, dict):
            continue
        rack_id = str(family.get("rackId") or "").strip()
        if rack_id:
            result[rack_id] = family
    return result


def _is_clean_source_ready(export_manifest: dict[str, Any]) -> bool:
    mode = str(export_manifest.get("exportMode") or "metadata_only")
    source_boundary = _dict(export_manifest.get("sourceBoundary"))
    source_mode = _source_mode(source_boundary)
    precision = str(source_boundary.get("precision") or "")
    included_handles = export_manifest.get("includedHandles")
    if not isinstance(included_handles, list):
        included_handles = []
    if mode == "style_export":
        return source_mode == "style_definition"
    if mode == "block_export":
        if precision != "precise":
            return False
        return bool(included_handles) or source_mode in {"explicit_bbox", "named_block"}
    return False


def audit_visual_rack_plan(
    *,
    visual_rack_plan: dict[str, Any] | None,
    zones: dict[str, Any] | None = None,
    entity_readback: dict[str, Any] | None = None,
    protected_content_report: dict[str, Any] | None = None,
    clearance_report: dict[str, Any] | None = None,
    readability_report: dict[str, Any] | None = None,
    model_review_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Audit whether a visual system-asset DWG plan behaves like a warehouse."""

    plan = _dict(visual_rack_plan)
    zone_bboxes = _dict(zones) or _dict(plan.get("zoneBboxes"))
    issues: list[str] = []
    checked: list[str] = []

    if int(plan.get("schemaVersion") or 0) < 2:
        issues.append("visualRackPlan schemaVersion must be >= 2")
    else:
        checked.append("visualRackPlan schemaVersion")
    if str(plan.get("layoutMode") or "") != "classified_expandable_visual_warehouse_v2":
        issues.append("visualRackPlan layoutMode must be classified_expandable_visual_warehouse_v2")
    else:
        checked.append("visual warehouse layout mode")

    architecture = _dict(plan.get("warehouseArchitecture"))
    if not architecture:
        issues.append("visualRackPlan missing warehouseArchitecture")
    else:
        checked.append("visual warehouse architecture")
        primary_zones = _unique([str(zone) for zone in _list(architecture.get("primaryWarehouseZones"))])
        review_zones = _unique([str(zone) for zone in _list(architecture.get("reviewOnlyZones"))])
        for zone in PRIMARY_WAREHOUSE_ZONES:
            if zone not in primary_zones:
                issues.append(f"warehouseArchitecture missing primary zone {zone}")
        for zone in REVIEW_ONLY_ZONES:
            if zone not in review_zones:
                issues.append(f"warehouseArchitecture missing review-only zone {zone}")
        if not architecture.get("expansionPolicy"):
            issues.append("warehouseArchitecture missing expansionPolicy")

    criteria = _dict(plan.get("acceptanceCriteria"))
    if not criteria:
        issues.append("visualRackPlan missing acceptanceCriteria")
    else:
        checked.append("visual warehouse acceptance criteria")
        for key in REQUIRED_VISUAL_ACCEPTANCE_KEYS:
            if not criteria.get(key):
                issues.append(f"acceptanceCriteria missing {key}")

    families = _rack_families_by_id(plan)
    base = families.get("A_BASE_SCAFFOLD")
    objects = families.get("B_OBJECT_ASSET_INDEX")
    if not base:
        issues.append("visualRackPlan missing A_BASE_SCAFFOLD rack")
    else:
        checked.append("base standards rack")
        if base.get("zoneId") != "01_CLEAN_ASSETS":
            issues.append("A_BASE_SCAFFOLD must belong to 01_CLEAN_ASSETS")
        if base.get("familyRole") != "reusable_style_source":
            issues.append("A_BASE_SCAFFOLD must declare familyRole=reusable_style_source")
        if base.get("copyPolicy") != "clean_source_slots_only":
            issues.append("A_BASE_SCAFFOLD must use copyPolicy=clean_source_slots_only")

    if not objects:
        issues.append("visualRackPlan missing B_OBJECT_ASSET_INDEX rack")
    else:
        if objects.get("zoneId") != "B_OBJECT_ASSET_INDEX":
            issues.append("B_OBJECT_ASSET_INDEX rack must belong to B_OBJECT_ASSET_INDEX zone")
        if objects.get("familyRole") != "cross_category_object_index":
            issues.append("B_OBJECT_ASSET_INDEX must declare familyRole=cross_category_object_index")
        if objects.get("copyPolicy") != "index_only_never_copy":
            issues.append("B_OBJECT_ASSET_INDEX must use copyPolicy=index_only_never_copy")
        else:
            checked.append("object index rack is never-copy")

    expansion_slot_count = 0
    owned_slot_count = 0
    for rack_id, family in families.items():
        slots = [slot for slot in _list(family.get("slots")) if isinstance(slot, dict)]
        if not slots:
            issues.append(f"{rack_id} rack has no slots")
            continue
        if int(family.get("minExpansionSlots") or 0) > 0:
            expansion_slot_count += int(family.get("minExpansionSlots") or 0)
        for slot in slots:
            slot_id = str(slot.get("slotId") or "").strip()
            if not slot_id:
                issues.append(f"{rack_id} contains a slot without slotId")
            if slot.get("copySourceAllowed") is True and rack_id == "B_OBJECT_ASSET_INDEX":
                issues.append(f"{slot_id} is index-only but allows copy source")
            status = str(slot.get("status") or "")
            if status in {"empty_reserved", "future_expansion"}:
                expansion_slot_count += 1
            asset_ids = _list(slot.get("assetIds"))
            if asset_ids or slot.get("category") or slot.get("nativeDwg"):
                owned_slot_count += 1
            if status == "index_only":
                if slot.get("copyPolicy") != "never_copy":
                    issues.append(f"{slot_id} index slot must use copyPolicy=never_copy")
                if not slot.get("category") or not slot.get("nativeDwg"):
                    issues.append(f"{slot_id} index slot must record category and nativeDwg")

    if expansion_slot_count <= 0:
        issues.append("visualRackPlan must leave explicit empty or future expansion slots")
    else:
        checked.append("expandable rack capacity")
    if owned_slot_count <= 0:
        issues.append("visualRackPlan must bind at least one slot to an asset, category, or nativeDwg")
    else:
        checked.append("slot ownership metadata")

    primary_area = sum(_bbox_area(zone_bboxes.get(zone)) for zone in PRIMARY_WAREHOUSE_ZONES)
    review_area = sum(_bbox_area(zone_bboxes.get(zone)) for zone in REVIEW_ONLY_ZONES)
    required_zone_area = primary_area + review_area
    for zone in (*PRIMARY_WAREHOUSE_ZONES, *REVIEW_ONLY_ZONES):
        if _bbox_area(zone_bboxes.get(zone)) <= 0:
            issues.append(f"missing or empty visual zone bbox: {zone}")
    primary_ratio = round(primary_area / required_zone_area, 4) if required_zone_area > 0 else 0.0
    if required_zone_area > 0:
        if primary_ratio < 0.7:
            issues.append("primary warehouse rack area must be at least 70% of rack+review zones")
        else:
            checked.append("primary warehouse rack area ratio")

    readback = _dict(entity_readback)
    readback_resolved_count = 0
    if readback:
        readback_resolved_count = int(readback.get("resolvedHandleCount") or 0)
        unresolved_count = int(readback.get("unresolvedHandleCount") or 0)
        unmanaged_count = int(readback.get("unmanagedLayerCount") or 0)
        if readback.get("status") not in {"ok", "pass"} or readback_resolved_count <= 0 or unresolved_count or unmanaged_count:
            issues.append("created shelf entity readback failed")
        else:
            checked.append("created shelf entity readback")

    protected = _dict(protected_content_report)
    protected_layer_counts: dict[str, int] = {}
    if protected:
        protected_layer_counts, census_issues = _protected_content_layer_census(protected)
        issues.extend(census_issues)
        if protected_layer_counts and not census_issues:
            checked.append("full protected content layer census")
        if any(layer in FORBIDDEN_PROTECTED_CONTENT_LAYERS for layer in protected_layer_counts):
            issues.append("protected asset proof content is still on CODEX_PREVIEW")
        if any(layer in PROOF_ROLE_CONFLICT_LAYERS for layer in protected_layer_counts):
            issues.append("source boundary layer is mixed into protected proof content")

    clearance = _dict(clearance_report)
    clearance_overlap_count = 0
    if clearance:
        clearance_overlap_count = int(clearance.get("overlapCount") or 0)
        if clearance.get("status") != "pass" or clearance_overlap_count:
            issues.append("visual shelf clearance audit failed")
        else:
            checked.append("visual shelf/content clearance")

    readability = _dict(readability_report)
    readability_issue_count = 0
    if readability:
        readability_issue_count = int(readability.get("issueCount") or len(_list(readability.get("issues"))))
        if readability.get("status") != "pass" or readability_issue_count:
            issues.append("visual warehouse readability audit failed")
        else:
            checked.append("visual warehouse readability")

    model_review = _dict(model_review_report)
    model_review_issue_count = 0
    if model_review:
        model_status = str(model_review.get("status") or "").casefold()
        blocking_reasons = _list(model_review.get("blockingReasons"))
        model_review_issue_count = len(blocking_reasons)
        if model_status not in {"pass", "ready", "ok"} or model_review_issue_count:
            issues.append("model-backed visual layout review failed")
        else:
            checked.append("model-backed visual layout review")

    status = "pass" if not issues else "fail"
    return {
        "status": status,
        "checked": _unique(checked),
        "issues": _unique(issues),
        "metrics": {
            "primaryWarehouseArea": round(primary_area, 3),
            "reviewOnlyArea": round(review_area, 3),
            "primaryWarehouseAreaRatio": primary_ratio,
            "rackFamilyCount": len(families),
            "ownedSlotCount": owned_slot_count,
            "expansionSlotCount": expansion_slot_count,
            "readbackResolvedHandleCount": readback_resolved_count,
            "clearanceOverlapCount": clearance_overlap_count,
            "readabilityIssueCount": readability_issue_count,
            "modelReviewIssueCount": model_review_issue_count,
            "protectedContentLayerCounts": protected_layer_counts,
        },
        "evidenceBoundary": {
            "checked": [
                "visualRackPlan v2 structure",
                "rack family ownership",
                "copy policy",
                "zone bbox ratios",
                *(
                    ["full protected content layer census"]
                    if protected and protected_layer_counts
                    else []
                ),
                *(
                    ["shelf/content clearance"]
                    if clearance
                    else []
                ),
                *(
                    ["warehouse readability metrics"]
                    if readability
                    else []
                ),
                *(
                    ["model-backed visual review"]
                    if model_review
                    else []
                ),
            ],
            "notChecked": [
                "actual CAD entity containment unless a readback report supplies handles and bboxes",
                *([] if protected else ["full protected content layer census unless protected content report is supplied"]),
                *([] if clearance else ["shelf/content clearance unless a clearance report is supplied"]),
                *([] if readability else ["warehouse visual readability unless a readability report is supplied"]),
                *([] if model_review else ["model-backed screenshot visual recognition"]),
            ],
        },
    }


def build_asset_library_layout_plan(
    *,
    asset_id: str,
    index: int,
    asset_name: str = "",
    category: str = "",
    asset_kind: str = "",
    export_manifest: dict[str, Any] | None = None,
    evidence_refs: list[str] | None = None,
    native_write: str = "deferred_until_explicit_cad_export_approval",
) -> dict[str, Any]:
    """Build an auditable system asset DWG layout plan.

    The plan is repository metadata. It does not prove that AutoCAD has written
    or saved native geometry.
    """

    manifest = _dict(export_manifest)
    source_boundary = _dict(manifest.get("sourceBoundary"))
    export_mode = str(manifest.get("exportMode") or "metadata_only")
    row = index // LAYOUT_GRID_COLUMNS
    column = index % LAYOUT_GRID_COLUMNS
    slot = {
        "slotKey": asset_id,
        "index": index,
        "row": row,
        "column": column,
        "columns": LAYOUT_GRID_COLUMNS,
    }
    clean_ready = _is_clean_source_ready(manifest)
    clean_zone_id = "01_CLEAN_ASSETS" if clean_ready else "03_REVIEW_QUARANTINE"
    clean_status = "ready_for_clean_reusable_source" if clean_ready else "blocked_until_source_boundary_review"
    reason = (
        "precise source boundary and export mode are present"
        if clean_ready
        else "metadata_only or unclear source boundary; keep candidate out of clean reusable source"
    )
    excluded_handles = source_boundary.get("excludedHandles")
    if not isinstance(excluded_handles, list):
        excluded_handles = []
    return {
        "schemaVersion": LAYOUT_PLAN_SCHEMA_VERSION,
        "policy": "governed_category_library_zones",
        "slotKey": asset_id,
        "label": asset_id,
        "assetName": asset_name or asset_id,
        "category": category,
        "assetKind": asset_kind,
        "nativeWrite": native_write,
        "zones": [dict(zone) for zone in LIBRARY_ZONES],
        "slot": slot,
        "grid": {
            "column": column,
            "row": row,
            "columns": LAYOUT_GRID_COLUMNS,
        },
        "plannedBbox": {
            "cleanSource": _slot_bbox(row, column, band_offset_y=0),
            "previewCard": _slot_bbox(row, column, band_offset_y=-12000),
            "quarantine": _slot_bbox(row, column, band_offset_y=-24000),
            "evidenceLinks": _slot_bbox(row, column, band_offset_y=-36000),
        },
        "cleanSource": {
            "zoneId": clean_zone_id,
            "status": clean_status,
            "reason": reason,
            "copySourceAllowed": clean_ready,
            "exportMode": export_mode,
            "sourceBoundaryMode": _source_mode(source_boundary),
            "includedHandles": _unique([str(handle) for handle in manifest.get("includedHandles", []) if handle]),
            "excludedHandles": _unique([str(handle) for handle in excluded_handles if handle]),
        },
        "previewCard": {
            "zoneId": "02_PREVIEW_CARDS",
            "title": asset_name or asset_id,
            "fields": ["assetId", "name", "category", "status", "dimensions", "useWhen"],
            "copySourceAllowed": False,
        },
        "evidenceLinks": {
            "zoneId": "99_EVIDENCE_LINKS",
            "refs": _unique(evidence_refs),
            "copySourceAllowed": False,
        },
        "cleanupPolicy": {
            "defaultAction": "exclude_training_or_review_content_from_clean_source",
            "excludedContentTypes": list(TRAINING_CONTAMINATION_TYPES),
            "includedOnlyWhen": "explicitly listed in includedHandles or represented by style_definition / named_block source",
            "excludedHandles": _unique([str(handle) for handle in excluded_handles if handle]),
        },
        "reviewQuarantine": {
            "zoneId": "03_REVIEW_QUARANTINE",
            "required": not clean_ready,
            "reason": "" if clean_ready else reason,
        },
    }


def evaluate_asset_library_hardening(
    *,
    layout_plan: dict[str, Any] | None = None,
    export_manifest: dict[str, Any] | None = None,
    native_dwg_exists: bool = False,
    lifecycle_status: str = "candidate",
    verification_status: str = "metadata_only",
) -> dict[str, Any]:
    """Return a machine-readable decision for follow-up hardening."""

    plan = _dict(layout_plan)
    manifest = _dict(export_manifest)
    clean_source = _dict(plan.get("cleanSource"))
    categories: list[str] = []
    if clean_source.get("copySourceAllowed") is not True:
        categories.append("needs_source_boundary_review")
    if not native_dwg_exists:
        categories.append("needs_native_cad_relayout")
    if str(lifecycle_status) == "verified" and verification_status in {"", "metadata_only"}:
        categories.append("needs_reuse_replay")
    if str(manifest.get("exportMode") or "metadata_only") == "metadata_only":
        categories.append("needs_reuse_replay")
    if not categories:
        categories.append("complete_for_current_scope")
    return {
        "status": categories[0],
        "categories": _unique(categories),
        "nativeCadRelayout": "checked" if native_dwg_exists else "not_run",
        "reuseReplay": "required_for_verified" if "needs_reuse_replay" in categories else "not_required_for_current_scope",
        "scope": "asset_library_governance",
        "evidenceBoundary": {
            "checked": ["layoutPlan v2 metadata", "governance decision"],
            "notChecked": [] if native_dwg_exists else ["native CAD relayout", "native DWG save/readback"],
        },
    }


def build_asset_library_governance(
    *,
    asset_id: str,
    category: str,
    asset_kind: str,
    export_manifest: dict[str, Any],
    anti_contamination: dict[str, Any],
    layout_plan: dict[str, Any],
    native_dwg_exists: bool,
    lifecycle_status: str,
    verification_status: str = "metadata_only",
    model_review_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the asset governor decision stored with system asset contracts."""

    source_boundary = _dict(export_manifest.get("sourceBoundary"))
    clean_source = _dict(layout_plan.get("cleanSource"))
    clean_allowed = clean_source.get("copySourceAllowed") is True
    if clean_allowed:
        decision = "ready_for_clean_source_layout"
    elif str(export_manifest.get("exportMode") or "metadata_only") == "metadata_only":
        decision = "metadata_only_until_native_cad_export"
    else:
        decision = "quarantine_until_source_boundary_review"
    hardening = evaluate_asset_library_hardening(
        layout_plan=layout_plan,
        export_manifest=export_manifest,
        native_dwg_exists=native_dwg_exists,
        lifecycle_status=lifecycle_status,
        verification_status=verification_status,
    )
    model_assisted = (
        model_review_to_asset_governor_assistance(model_review_report)
        if isinstance(model_review_report, dict)
        else None
    )
    result = {
        "governorAgentId": "pipeline_asset_governor",
        "managedChildAgents": list(DEFAULT_CHILD_AGENTS),
        "decision": decision,
        "assetId": asset_id,
        "category": category,
        "assetKind": asset_kind,
        "sourceBoundaryDecision": {
            "mode": _source_mode(source_boundary),
            "precision": source_boundary.get("precision", "unclear"),
            "includedHandleCount": len(export_manifest.get("includedHandles", []))
            if isinstance(export_manifest.get("includedHandles"), list)
            else 0,
            "cleanSourceAllowed": clean_allowed,
        },
        "layoutDecision": {
            "schemaVersion": layout_plan.get("schemaVersion"),
            "policy": layout_plan.get("policy"),
            "cleanSourceZone": clean_source.get("zoneId"),
            "slotKey": layout_plan.get("slotKey"),
        },
        "requiredGuards": [
            "encoding_preflight",
            "source_boundary",
            "asset_librarian_catalog",
            "asset_dwg_curator_layout",
            "asset_reuse_auditor_before_verified",
            *(
                ["model suggestions are advisory only"]
                if model_assisted
                else []
            ),
        ],
        "forbiddenBehaviors": _unique(
            [
                *[str(item) for item in anti_contamination.get("checks", []) if item],
                "do not copy training panels into clean source",
                "do not invent untracked global agents",
                *(
                    ["do not let model suggestions override source boundary, readback, reuse, or save gates"]
                    if model_assisted
                    else []
                ),
            ]
        ),
        "polishHardeningDecision": hardening,
    }
    if model_assisted:
        result["modelAssistedDecision"] = model_assisted
    return result
