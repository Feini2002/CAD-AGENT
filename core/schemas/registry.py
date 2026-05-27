"""Schema registry for high-level CAD Agent model files."""

from __future__ import annotations

from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = PROJECT_ROOT / "core" / "schemas"

MODEL_SCHEMAS = {
    "cad_context": "cad_context.schema.json",
    "cad_object": "cad_object.schema.json",
    "design_brief": "design_brief.schema.json",
    "drawing_model": "drawing_model.schema.json",
    "project_model": "project_model.schema.json",
    "object_spec": "object_spec.schema.json",
    "style_profile": "style_profile.schema.json",
    "block_library": "block_library.schema.json",
    "layer_preset": "layer_preset.schema.json",
    "drawing_standard_profile": "drawing_standard_profile.schema.json",
    "layout_proposal": "layout_proposal.schema.json",
    "design_proposal": "design_proposal.schema.json",
    "proposal_candidate_scoring": "proposal_candidate_scoring.schema.json",
    "proposal_comparison_summary": "proposal_comparison_summary.schema.json",
    "proposal_user_confirmation": "proposal_user_confirmation.schema.json",
    "confirmed_cad_plan_bundle": "confirmed_cad_plan_bundle.schema.json",
    "cad_plan": "cad_plan.schema.json",
    "verification_report": "verification_report.schema.json",
    "shell_model": "shell_model.schema.json",
    "circulation_model": "circulation_model.schema.json",
    "function_zone": "function_zone.schema.json",
    "project_sample_manifest": "project_sample_manifest.schema.json",
    "dwg_entity_summary": "dwg_entity_summary.schema.json",
    "dwg_geometry_candidates": "dwg_geometry_candidates.schema.json",
    "shell_candidate_confidence_report": "shell_candidate_confidence_report.schema.json",
    "shell_drawing_read_confirmation": "shell_drawing_read_confirmation.schema.json",
    "cad_regression_manifest": "cad_regression_manifest.schema.json",
    "cad_block_attribute_hatch_boundary": "cad_block_attribute_hatch_boundary.schema.json",
    "commercial_fitout_block_mapping": "commercial_fitout_block_mapping.schema.json",
    "commercial_fitout_cad_smoke_report": "commercial_fitout_cad_smoke_report.schema.json",
    "commercial_fitout_object_catalog": "commercial_fitout_object_catalog.schema.json",
    "commercial_fitout_product_alpha_boundary": "commercial_fitout_product_alpha_boundary.schema.json",
    "commercial_fitout_sample_confirmation_bundle": "commercial_fitout_sample_confirmation_bundle.schema.json",
    "commercial_fitout_scope": "commercial_fitout_scope.schema.json",
    "project_sample_cad_rollup": "project_sample_cad_rollup.schema.json",
    "project_sample_cad_rollup_report": "project_sample_cad_rollup_report.schema.json",
    "request_context": "request_context.schema.json",
    "route_audit_report": "route_audit_report.schema.json",
    "scene_registry": "scene_registry.schema.json",
    "symbol_graph": "symbol_graph.schema.json",
    "symbol_spec": "symbol_spec.schema.json",
    "cad_capability_registry": "cad_capability_registry.schema.json",
    "composition_template_catalog": "composition_template_catalog.schema.json",
    "evidence_trend": "evidence_trend.schema.json",
}


def get_schema_path(model_type: str) -> Path:
    try:
        return SCHEMA_ROOT / MODEL_SCHEMAS[model_type]
    except KeyError as exc:
        raise ValueError(f"Unknown model type: {model_type}") from exc


def infer_model_type(data: dict[str, Any]) -> str:
    if "unit" in data and "domain" in data and "layers" in data:
        return "cad_context"
    if "type" in data and "name" in data and "draw_method" in data:
        return "cad_object"
    if "brief_id" in data and "user_request" in data:
        return "design_brief"
    if "drawing_id" in data:
        return "drawing_model"
    if "project_id" in data and "spaces" in data and "requirements" in data:
        return "project_model"
    if "object_id" in data and "components" in data:
        return "object_spec"
    if "style_id" in data:
        return "style_profile"
    if "library_id" in data and "blocks" in data:
        return "block_library"
    if "preset_id" in data and "layers" in data:
        return "layer_preset"
    if "profile_id" in data and "object_role_bindings" in data:
        return "drawing_standard_profile"
    if "layout_id" in data and "candidates" in data:
        return "layout_proposal"
    if "rank" in data and "weighted_score" in data and "components" in data:
        return "proposal_candidate_scoring"
    if "object_coverage" in data and "ranking_reason_codes" in data:
        return "proposal_comparison_summary"
    if "confirmation_id" in data and "selected_candidate_id" in data:
        return "proposal_user_confirmation"
    if "confirmed_cad_plans" in data and "unselected_candidate_evidence" in data:
        return "confirmed_cad_plan_bundle"
    if "proposal_id" in data:
        return "design_proposal"
    if "intent" in data and "placement" in data and "drawing" in data:
        return "cad_plan"
    if "report_id" in data and "checks" in data:
        return "verification_report"
    if "shell_id" in data and "boundary" in data:
        return "shell_model"
    if "circulation_id" in data and "paths" in data:
        return "circulation_model"
    if "zone_id" in data and "purpose" in data:
        return "function_zone"
    if "sample_id" in data and "input_files" in data and "expected_artifacts" in data:
        return "project_sample_manifest"
    if "entity_count" in data and "layer_statistics" in data and "handles_sample" in data:
        return "dwg_entity_summary"
    if "wall_segment_candidates" in data and "door_opening_candidates" in data:
        return "dwg_geometry_candidates"
    if "confidence" in data and "shell_candidate_draft" in data and "human_confirmation_items" in data:
        return "shell_candidate_confidence_report"
    if "confirmation_id" in data and "report_ref" in data and "confirmed_items" in data:
        return "shell_drawing_read_confirmation"
    if "suite_id" in data and "cases" in data and "safety" in data and "description" in data:
        return "cad_regression_manifest"
    if "package_id" in data and "rollup_id" in data and "samples" in data:
        return "project_sample_cad_rollup"
    if "rollup_id" in data and "sample_results" in data:
        return "project_sample_cad_rollup_report"
    if "context_id" in data and "request_kind" in data and "cad_policy" in data:
        return "request_context"
    if "routing_summary" in data and "deferred_items" in data and "human_summary" in data:
        return "route_audit_report"
    if "registry_id" in data and "default_scene_id" in data and "scenes" in data:
        return "scene_registry"
    if "graph_id" in data and "nodes" in data:
        return "symbol_graph"
    if "symbol_id" in data and "archetype" in data and "readability_constraints" in data:
        return "symbol_spec"
    if "scene_id" in data and "subscenes" in data and "delivery_commitments" in data:
        return "commercial_fitout_scope"
    if "mapping_id" in data and "entries" in data and "block_library_path" in data:
        return "commercial_fitout_block_mapping"
    if "catalog_id" in data and "objects" in data and data.get("scene_id") == "commercial_fitout":
        return "commercial_fitout_object_catalog"
    if "rollup_id" in data and "declarable_capabilities" in data and "non_declarable" in data:
        return "commercial_fitout_product_alpha_boundary"
    if "assumptions_risks" in data and "confirmation_gate" in data and "finalize_report" in data:
        return "commercial_fitout_sample_confirmation_bundle"
    if "product_claim_boundary" in data and "plan_count" in data and "workflow_output_dir" in data:
        return "commercial_fitout_cad_smoke_report"
    if "boundary_id" in data and "capabilities" in data and data.get("package_id") == "LCAD-07-BLOCK-ATTRIBUTE-HATCH":
        return "cad_block_attribute_hatch_boundary"
    if "registry_id" in data and "capabilities" in data and data.get("version") == "0.1":
        first = data["capabilities"][0] if data.get("capabilities") else {}
        if isinstance(first, dict) and "claim_level" in first and "ladder_level" in first:
            return "cad_capability_registry"
    if "report_id" in data and "snapshots" in data and "vocabulary" in data:
        return "evidence_trend"
    raise ValueError("Cannot infer model type.")
