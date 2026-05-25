"""Schema registry for high-level CAD Agent model files."""

from __future__ import annotations

from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = PROJECT_ROOT / "core" / "schemas"

MODEL_SCHEMAS = {
    "design_brief": "design_brief.schema.json",
    "drawing_model": "drawing_model.schema.json",
    "project_model": "project_model.schema.json",
    "object_spec": "object_spec.schema.json",
    "style_profile": "style_profile.schema.json",
    "block_library": "block_library.schema.json",
    "layout_proposal": "layout_proposal.schema.json",
    "design_proposal": "design_proposal.schema.json",
    "cad_plan": "cad_plan.schema.json",
    "verification_report": "verification_report.schema.json",
    "shell_model": "shell_model.schema.json",
    "circulation_model": "circulation_model.schema.json",
    "function_zone": "function_zone.schema.json",
}


def get_schema_path(model_type: str) -> Path:
    try:
        return SCHEMA_ROOT / MODEL_SCHEMAS[model_type]
    except KeyError as exc:
        raise ValueError(f"Unknown model type: {model_type}") from exc


def infer_model_type(data: dict[str, Any]) -> str:
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
    if "layout_id" in data and "candidates" in data:
        return "layout_proposal"
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
    raise ValueError("Cannot infer model type.")
