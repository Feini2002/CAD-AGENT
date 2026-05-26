"""Manifest loading and selection helpers for local CAD regression."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.schemas.validator import load_json, validate_value


PREVIEW_LAYER = "CODEX_PREVIEW"
DEFAULT_MANIFEST_RELATIVE_PATH = Path("examples") / "cad_regression" / "local_cad_regression_manifest.json"
MANIFEST_SCHEMA_RELATIVE_PATH = Path("core") / "schemas" / "cad_regression_manifest.schema.json"


def load_regression_manifest(path: Path) -> dict[str, Any]:
    """Load and validate the local CAD regression manifest contract."""

    manifest_path = path.resolve()
    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict):
        raise ValueError(f"Invalid local CAD regression manifest: {manifest_path} must contain a JSON object.")

    project_root = Path(__file__).resolve().parents[2]
    schema = load_json(project_root / MANIFEST_SCHEMA_RELATIVE_PATH)
    if not isinstance(schema, dict):
        raise ValueError("Invalid local CAD regression manifest schema.")

    errors = validate_value(manifest, schema)
    errors.extend(_validate_manifest_semantics(manifest))
    if errors:
        raise ValueError("Invalid local CAD regression manifest: " + "; ".join(errors))
    return manifest


def manifest_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    cases = manifest.get("cases", [])
    safe_cases = cases if isinstance(cases, list) else []
    return {
        "version": manifest.get("version"),
        "suite_id": manifest.get("suite_id"),
        "case_count": len(safe_cases),
        "cases": [
            {
                "id": case.get("id"),
                "requires_real_cad": case.get("requires_real_cad"),
                "expected_evidence_state": case.get("expected_evidence_state"),
                "output_path": case.get("output_path"),
            }
            for case in safe_cases
            if isinstance(case, dict)
        ],
    }


def manifest_case_ids(manifest: dict[str, Any]) -> list[str]:
    cases = manifest.get("cases", [])
    if not isinstance(cases, list):
        return []
    return [str(case.get("id")) for case in cases if isinstance(case, dict) and case.get("id")]


def select_manifest_case_ids(manifest: dict[str, Any], selected_case_ids: list[str] | None) -> list[str]:
    all_case_ids = manifest_case_ids(manifest)
    if not selected_case_ids:
        return all_case_ids

    requested = list(dict.fromkeys(selected_case_ids))
    unknown = [case_id for case_id in requested if case_id not in all_case_ids]
    if unknown:
        raise ValueError(f"unknown selected manifest case(s): {', '.join(unknown)}")
    return requested


def _validate_manifest_semantics(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    suite_safety = manifest.get("safety")
    if isinstance(suite_safety, dict):
        errors.extend(_validate_preview_safety(suite_safety, "$.safety"))

    seen_case_ids: set[str] = set()
    cases = manifest.get("cases", [])
    if isinstance(cases, list):
        for index, case in enumerate(cases):
            if not isinstance(case, dict):
                continue
            case_id = str(case.get("id") or "")
            if case_id in seen_case_ids:
                errors.append(f"$.cases[{index}].id must be unique.")
            seen_case_ids.add(case_id)
            safety = case.get("safety")
            if isinstance(safety, dict):
                errors.extend(_validate_preview_safety(safety, f"$.cases[{index}].safety"))
    return errors


def _validate_preview_safety(safety: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    expected = {
        "layer": PREVIEW_LAYER,
        "saved_dwg": False,
        "deleted_entities": False,
        "modified_formal_layers": False,
    }
    for key, value in expected.items():
        if safety.get(key) != value:
            errors.append(f"{path}.{key} must be {value!r}.")
    return errors
