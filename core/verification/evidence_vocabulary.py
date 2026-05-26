"""Shared evidence vocabulary constants for CAD and non-CAD verification."""

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
EVIDENCE_BLOCKED_EXPECTED_NON_CAD = "blocked_expected_non_cad"
EVIDENCE_DRY_RUN_VALID_PLAN_ONLY = "dry_run_valid_plan_only"
EVIDENCE_INVALID_CONFIGURATION = "invalid_configuration"

GEOMETRY_VERIFIED_BY_READBACK = "verified_by_cad_readback"
GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE = "verified_by_cad_capability_readback"
GEOMETRY_NOT_VERIFIED_BY_SCREENSHOT = "not_verified_by_screenshot"

EVIDENCE_STATE_VALUES: frozenset[str] = frozenset(
    {
        EVIDENCE_CAD_CAPABILITY_VERIFIED,
        EVIDENCE_READBACK_GEOMETRY_VERIFIED,
        EVIDENCE_DEFERRED_CAD_READBACK,
        EVIDENCE_BENCHMARK_PASS_NON_CAD,
        EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
        EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
        EVIDENCE_INVALID_CONFIGURATION,
    }
)

GEOMETRY_ACCURACY_VALUES: frozenset[str] = frozenset(
    {
        GEOMETRY_VERIFIED_BY_READBACK,
        GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE,
        NON_CAD_GEOMETRY_ACCURACY,
        GEOMETRY_NOT_VERIFIED_BY_SCREENSHOT,
    }
)

SCREENSHOT_ROLE_VALUES: frozenset[str] = frozenset(
    {
        SCREENSHOT_VISUAL_AID_ONLY,
        SCREENSHOT_NOT_APPLICABLE,
    }
)

GEOMETRY_VERIFIED_EVIDENCE_STATES: frozenset[str] = frozenset(
    {
        EVIDENCE_READBACK_GEOMETRY_VERIFIED,
        EVIDENCE_CAD_CAPABILITY_VERIFIED,
    }
)

FAILURE_EVIDENCE_STATES: frozenset[str] = frozenset(
    {
        EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
        EVIDENCE_INVALID_CONFIGURATION,
    }
)

BENCHMARK_FAILURE_CATEGORIES: frozenset[str] = frozenset(
    {
        "insufficient_space",
        "entry_clearance_conflict",
        "clearance_conflict",
        "circulation_conflict",
        "obstacle_conflict",
        "layout_blocked",
    }
)

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
        "write_fields": ["points", "closed", "layer", "layer_role"],
        "readback_fields": ["handle", "type", "points", "closed", "bbox", "layer"],
        "tolerance_mm": 1.0,
        "failure_classes": ["point_count_mismatch", "closed_mismatch", "bbox_mismatch", "layer_mismatch"],
        "evidence_state_when_verified": EVIDENCE_CAD_CAPABILITY_VERIFIED,
        "implementation_status": "beta_entity_level_probe",
    },
    "hatch": {
        "intents": ["draw_hatch"],
        "write_fields": ["boundary_points", "pattern", "layer", "layer_role"],
        "readback_fields": ["handle", "type", "pattern", "layer"],
        "tolerance_mm": 2.0,
        "failure_classes": ["hatch_unverified", "layer_mismatch"],
        "evidence_state_when_verified": EVIDENCE_DEFERRED_CAD_READBACK,
        "implementation_status": "deferred",
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
        "implementation_status": "alpha_verified_controlled_sample",
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
