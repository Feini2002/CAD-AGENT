"""Execute STYLE_CANDIDATES through preview-safe CAD_PLAN generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.drawing_standard.drawing_standard_profile import apply_drawing_standard_to_plan
from core.execution.execute_plan import CadPreviewDriver, execute_plan_file
from core.schemas.validator import validate_value
from core.safety.policy import PREVIEW_LAYER


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STYLE_CANDIDATES_SCHEMA = PROJECT_ROOT / "core" / "schemas" / "style_candidates.schema.json"


def _read_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def validate_style_candidates(payload: dict[str, Any]) -> list[str]:
    schema = _read_json_object(STYLE_CANDIDATES_SCHEMA)
    return validate_value(payload, schema)


def _point3(values: list[Any]) -> list[float]:
    result = [float(values[0]), float(values[1])]
    result.append(float(values[2]) if len(values) > 2 else 0.0)
    return result


def candidate_to_cad_plan(style_candidates: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    """Convert one style candidate into a deterministic preview CAD_PLAN."""

    scenario = style_candidates.get("scenario", {})
    if not isinstance(scenario, dict):
        scenario = {}
    parameters = candidate.get("parameters", {})
    if not isinstance(parameters, dict):
        raise ValueError("style candidate parameters must be an object")

    plan: dict[str, Any] = {
        "version": "0.1",
        "domain": str(scenario.get("domain", "generic")),
        "intent": "draw_object",
        "object": {
            "type": str(parameters["objectType"]),
            "name": str(parameters["objectName"]),
            "width": float(parameters["width"]),
            "depth": float(parameters["depth"]),
        },
        "placement": {
            "mode": "absolute",
            "base_point": _point3(list(parameters["basePoint"])),
        },
        "drawing": {
            "layer": PREVIEW_LAYER,
            "include_label": bool(parameters.get("includeLabel", False)),
            "include_dimensions": bool(parameters.get("includeDimensions", False)),
            "style_token": str(parameters.get("styleToken", "")),
            "style_assumptions": [
                f"styleCandidateId={candidate.get('candidateId')}",
                f"textHierarchy={parameters.get('textHierarchy')}",
                f"lineSpacing={parameters.get('lineSpacing')}",
                f"density={parameters.get('density')}",
                f"layerStrategy={parameters.get('layerStrategy')}",
            ],
        },
        "confidence": 0.9,
        "needs_confirmation": False,
        "drawing_standard_profile_id": "codex_preview_beta",
        "object_role": "furniture",
    }
    return apply_drawing_standard_to_plan(plan, object_role="furniture")


def execute_style_candidates_file(
    style_candidates_path: str | Path,
    *,
    driver: CadPreviewDriver,
    output_dir: str | Path,
    preview_only: bool = True,
) -> dict[str, Any]:
    """Validate and execute every candidate into CODEX_PREVIEW via CAD_PLAN."""

    source_path = Path(style_candidates_path)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    payload = _read_json_object(source_path)
    errors = validate_style_candidates(payload)
    if errors:
        raise ValueError("Invalid STYLE_CANDIDATES: " + "; ".join(errors))

    candidates = payload["candidates"]
    if not isinstance(candidates, list):
        raise ValueError("STYLE_CANDIDATES.candidates must be an array")

    candidate_summaries: list[dict[str, Any]] = []
    all_handles: list[str] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("STYLE_CANDIDATES candidates must be objects")
        candidate_id = str(candidate["candidateId"])
        cad_plan = candidate_to_cad_plan(payload, candidate)
        plan_path = output_root / f"{candidate_id}_cad_plan.json"
        plan_path.write_text(json.dumps(cad_plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        execution_summary = execute_plan_file(
            plan_path,
            driver=driver,
            preview_only=preview_only,
            allow_unconfirmed=True,
        )
        handles = [str(handle) for handle in execution_summary.get("created_handles", [])]
        all_handles.extend(handles)
        summary_path = output_root / f"{candidate_id}_execution_summary.json"
        summary_path.write_text(
            json.dumps(execution_summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        candidate_summaries.append(
            {
                "candidateId": candidate_id,
                "label": candidate.get("label", ""),
                "summary": candidate.get("summary", ""),
                "cadPlanPath": str(plan_path),
                "executionSummaryPath": str(summary_path),
                "executionSummary": execution_summary,
            }
        )

    report = {
        "schemaVersion": "style-candidate-execution/v1",
        "status": "executed",
        "source": str(source_path),
        "candidateCount": len(candidates),
        "candidateIds": [str(candidate["candidateId"]) for candidate in candidates if isinstance(candidate, dict)],
        "needsUserChoice": bool(payload.get("selection", {}).get("needsUserChoice")),
        "targetLayer": PREVIEW_LAYER,
        "savedCurrentDwg": False,
        "candidateSummaries": candidate_summaries,
        "createdHandles": list(dict.fromkeys(all_handles)),
        "createdHandleCount": len(dict.fromkeys(all_handles)),
        "evidenceBoundary": {
            "checked": [
                "style_candidates_schema",
                "cad_plan_generation",
                "validate_plan_inside_execute_plan",
                "preview_layer_write",
                "created_handles_returned",
            ],
            "notChecked": [
                "user_choice",
                "plot_output",
                "real_cad_readback_if_fake_driver",
                "visual_acceptance",
            ],
        },
    }
    (output_root / "style_candidate_execution_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report
