"""Shared evidence-state vocabulary and CAD capability contract metadata."""

from __future__ import annotations

from typing import Any

CONTRACT_VERSION = "phase-r-cad-v1"

NON_CAD_GEOMETRY_ACCURACY = "not_verified_without_cad_readback"
SCREENSHOT_VISUAL_AID_ONLY = "visual_aid_only"
SCREENSHOT_NOT_APPLICABLE = "not_applicable"

EVIDENCE_CAD_CAPABILITY_VERIFIED = "cad_capability_verified"
EVIDENCE_READBACK_GEOMETRY_VERIFIED = "readback_geometry_verified"
EVIDENCE_DEFERRED_CAD_READBACK = "deferred_cad_readback_required"
EVIDENCE_BENCHMARK_PASS_NON_CAD = "benchmark_pass_non_cad"

GEOMETRY_VERIFIED_BY_READBACK = "verified_by_cad_readback"
GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE = "verified_by_cad_capability_readback"

ENTITY_CONTRACTS: dict[str, dict[str, Any]] = {
    "line": {
        "intents": ["draw_line"],
        "write_fields": ["start_point", "end_point", "layer"],
        "readback_fields": ["handle", "type", "start_point", "end_point", "layer"],
        "tolerance_mm": 1.0,
        "failure_classes": ["write_failed", "handle_missing", "readback_missing", "geometry_mismatch", "layer_mismatch"],
        "evidence_state_when_verified": EVIDENCE_CAD_CAPABILITY_VERIFIED,
    },
    "rectangle": {
        "intents": ["draw_rectangle", "draw_object"],
        "write_fields": ["corner1", "corner2", "bbox", "layer"],
        "readback_fields": ["handles", "type_counts", "bbox", "layer"],
        "tolerance_mm": 1.0,
        "failure_classes": ["partial_handles", "bbox_mismatch", "base_point_mismatch", "layer_mismatch"],
        "evidence_state_when_verified": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    },
    "circle": {
        "intents": ["draw_circle"],
        "write_fields": ["center", "radius", "layer"],
        "readback_fields": ["handle", "type", "center", "radius", "bbox", "layer"],
        "tolerance_mm": 1.0,
        "failure_classes": ["radius_mismatch", "center_mismatch", "bbox_mismatch"],
        "evidence_state_when_verified": EVIDENCE_CAD_CAPABILITY_VERIFIED,
    },
    "arc": {
        "intents": ["draw_arc"],
        "write_fields": ["center", "radius", "start_angle", "end_angle", "layer"],
        "readback_fields": ["handle", "type", "center", "radius", "start_angle", "end_angle", "bbox", "layer"],
        "tolerance_mm": 1.0,
        "angle_tolerance_deg": 0.5,
        "failure_classes": ["angle_mismatch", "direction_mismatch", "radius_mismatch"],
        "evidence_state_when_verified": EVIDENCE_CAD_CAPABILITY_VERIFIED,
    },
    "polyline": {
        "intents": ["draw_polyline"],
        "write_fields": ["points", "closed", "layer"],
        "readback_fields": ["handle", "type", "points", "closed", "bbox", "layer"],
        "tolerance_mm": 1.0,
        "failure_classes": ["point_count_mismatch", "closed_mismatch", "bbox_mismatch"],
        "evidence_state_when_verified": EVIDENCE_CAD_CAPABILITY_VERIFIED,
    },
    "text": {
        "intents": ["draw_text"],
        "write_fields": ["text", "position", "height", "layer"],
        "readback_fields": ["handle", "type", "text", "position", "layer"],
        "tolerance_mm": 1.0,
        "failure_classes": ["text_mismatch", "position_mismatch", "style_unverified"],
        "evidence_state_when_verified": EVIDENCE_CAD_CAPABILITY_VERIFIED,
    },
    "dimension": {
        "intents": ["add_dimension"],
        "write_fields": ["start_point", "end_point", "text_position", "layer"],
        "readback_fields": ["handle", "type", "text", "bbox", "layer"],
        "tolerance_mm": 2.0,
        "failure_classes": ["dimension_count_mismatch", "dimension_position_unverified", "style_unverified"],
        "evidence_state_when_verified": EVIDENCE_CAD_CAPABILITY_VERIFIED,
    },
    "block_reference": {
        "intents": ["insert_block_alpha"],
        "write_fields": ["block_id", "cad_identity.block_name", "base_point", "rotation", "scale", "layer"],
        "readback_fields": ["handle", "type", "block_name", "insertion_point", "rotation", "scale", "layer", "bbox"],
        "tolerance_mm": 2.0,
        "failure_classes": [
            "definition_missing",
            "insert_failed",
            "block_name_mismatch",
            "anchor_mismatch",
            "rotation_mismatch",
            "attribute_unverified",
        ],
        "evidence_state_when_verified": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
        "implementation_status": "deferred",
    },
}

DEFERRED_VERIFICATION: list[str] = [
    "real_company_block_library",
    "attribute_blocks",
    "hatch",
    "dim_style_and_text_style_accuracy",
    "arbitrary_rotation_block_bbox",
    "non_uniform_scale_mirror_dynamic_nested_blocks",
    "arbitrary_cad_plan_and_formal_layers",
    "automatic_dwg_pdf_block_matching",
]

REQUIRED_CAPABILITY_PROBE_FIELDS = (
    "contract_version",
    "evidence_state",
    "geometry_accuracy",
    "screenshot_role",
    "contract",
    "deferred_verification",
    "limitations",
)

REQUIRED_READBACK_REPORT_FIELDS = (
    "evidence_state",
    "geometry_accuracy",
    "screenshot_role",
)


def contract_metadata() -> dict[str, Any]:
    return {
        "version": CONTRACT_VERSION,
        "entities": ENTITY_CONTRACTS,
        "deferred_verification": list(DEFERRED_VERIFICATION),
    }


def capability_probe_evidence(*, status: str) -> dict[str, str]:
    if status == "cad_capability_verified":
        return {
            "evidence_state": EVIDENCE_CAD_CAPABILITY_VERIFIED,
            "geometry_accuracy": GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE,
            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        }
    if status == "external_blocker":
        return {
            "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        }
    return {
        "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
    }


def readback_report_evidence(*, status: str, screenshot_path: str | None = None) -> dict[str, str]:
    screenshot_role = SCREENSHOT_VISUAL_AID_ONLY if screenshot_path else SCREENSHOT_NOT_APPLICABLE
    if status == "geometry_verified":
        return {
            "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
            "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK,
            "screenshot_role": screenshot_role,
        }
    return {
        "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
        "screenshot_role": screenshot_role,
    }


def apply_capability_probe_contract(report: dict[str, Any]) -> dict[str, Any]:
    status = str(report.get("status", ""))
    evidence = capability_probe_evidence(status=status)
    report["contract_version"] = CONTRACT_VERSION
    report.update(evidence)
    report["contract"] = contract_metadata()
    report["deferred_verification"] = list(DEFERRED_VERIFICATION)
    limitations = list(report.get("limitations", []))
    limitations.append(
        "cad_capability_verified only covers preview-layer primitive write/readback; "
        "it does not prove block insertion, real block libraries, or arbitrary CAD_PLAN accuracy."
    )
    report["limitations"] = limitations
    return report


def apply_readback_report_contract(report: dict[str, Any], *, screenshot_path: str | None = None) -> dict[str, Any]:
    status = str(report.get("status", ""))
    evidence = readback_report_evidence(status=status, screenshot_path=screenshot_path)
    report.update(evidence)
    if status != "geometry_verified":
        limitations = list(report.get("limitations", []))
        if NON_CAD_GEOMETRY_ACCURACY not in " ".join(limitations):
            limitations.append("Geometry accuracy requires created-handle readback with geometry_verified status.")
        report["limitations"] = limitations
    return report


def validate_capability_probe_evidence(report: dict[str, Any]) -> str:
    for field in REQUIRED_CAPABILITY_PROBE_FIELDS:
        if field not in report:
            return f"cad_capability_probe missing required field: {field}"

    status = str(report.get("status", ""))
    expected = capability_probe_evidence(status=status)
    for key, value in expected.items():
        if report.get(key) != value:
            return f"cad_capability_probe.{key}={report.get(key)!r}; expected {value!r} for status={status!r}"

    if status == "cad_capability_verified" and report.get("geometry_accuracy") == GEOMETRY_VERIFIED_BY_READBACK:
        return "cad_capability_probe must not claim baseline readback_geometry_verified geometry_accuracy"

    return ""


def validate_readback_report_evidence(report: dict[str, Any]) -> str:
    for field in REQUIRED_READBACK_REPORT_FIELDS:
        if field not in report:
            return f"readback_report missing required field: {field}"

    status = str(report.get("status", ""))
    screenshot_path = str(report.get("evidence", {}).get("screenshot", "") or "")
    expected = readback_report_evidence(status=status, screenshot_path=screenshot_path or None)
    for key, value in expected.items():
        if report.get(key) != value:
            return f"readback_report.{key}={report.get(key)!r}; expected {value!r} for status={status!r}"

    if status == "geometry_verified" and report.get("evidence_state") != EVIDENCE_READBACK_GEOMETRY_VERIFIED:
        return "readback_report geometry_verified requires evidence_state=readback_geometry_verified"

    if status != "geometry_verified" and report.get("geometry_accuracy") == GEOMETRY_VERIFIED_BY_READBACK:
        return "readback_report must not claim verified_by_cad_readback without geometry_verified status"

    return ""
