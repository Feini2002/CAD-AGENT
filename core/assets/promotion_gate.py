"""Promotion gate for CAD system assets.

The gate is deliberately conservative. It records the highest safe claim level
from local evidence and does not mutate libraries by itself.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATUS_ORDER = ["reference_only", "candidate", "case_verified", "system_verified"]


def _read_json_object(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.is_file():
        return None, f"file_missing:{path}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"invalid_json:{exc.msg}"
    if not isinstance(data, dict):
        return None, "json_root_not_object"
    return data, None


def _path_exists(root: Path, value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.exists()


def _check(name: str, passed: bool, detail: str, blocking_for: list[str]) -> dict[str, Any]:
    return {
        "name": name,
        "status": "pass" if passed else "fail",
        "detail": detail,
        "blocking_for": blocking_for,
    }


def _max_allowed_status(checks: list[dict[str, Any]]) -> str:
    failed_by_status = {
        status
        for check in checks
        if check.get("status") != "pass"
        for status in check.get("blocking_for", [])
    }
    if "candidate" in failed_by_status:
        return "reference_only"
    if "case_verified" in failed_by_status:
        return "candidate"
    if "system_verified" in failed_by_status:
        return "case_verified"
    return "system_verified"


def evaluate_asset_promotion(
    candidate_path: Path,
    *,
    project_root: Path = PROJECT_ROOT,
    target_status: str | None = None,
) -> dict[str, Any]:
    """Evaluate whether an asset candidate can claim the requested status."""

    root = Path(project_root)
    candidate_path = Path(candidate_path)
    if not candidate_path.is_absolute():
        candidate_path = root / candidate_path

    data, error = _read_json_object(candidate_path)
    if error:
        return {
            "status": "fail",
            "candidate_path": str(candidate_path),
            "requested_status": target_status or "candidate",
            "max_allowed_status": "reference_only",
            "checks": [_check("parse", False, error, ["candidate", "case_verified", "system_verified"])],
            "blocking_reasons": [error],
            "not_checked": [],
        }

    assert data is not None
    requested_status = target_status or str(data.get("validation_status") or "candidate")
    if requested_status not in STATUS_ORDER:
        requested_status = "candidate"

    representation = data.get("representation")
    source_lineage = data.get("source_lineage")
    parts = data.get("parts")
    parameters = data.get("parameters")
    evidence_refs = data.get("evidence_refs")
    benchmark_refs = data.get("benchmark_refs")
    boundary_ref = data.get("evidence_boundary_ref")

    checks = [
        _check(
            "source_gate",
            isinstance(source_lineage, list) and bool(source_lineage),
            "source_lineage records where the asset came from",
            ["candidate", "case_verified", "system_verified"],
        ),
        _check(
            "structure_gate",
            all(
                [
                    isinstance(data.get("id"), str),
                    isinstance(data.get("asset_type"), str),
                    isinstance(data.get("canonical_name"), str),
                    isinstance(parts, list) and bool(parts),
                    isinstance(parameters, dict),
                    isinstance(representation, dict) and bool(representation),
                ]
            ),
            "asset has id, type, canonical_name, parts, parameters and representation",
            ["candidate", "case_verified", "system_verified"],
        ),
        _check(
            "evidence_boundary_gate",
            isinstance(boundary_ref, str) and bool(boundary_ref.strip()),
            "asset points to checked / not_checked / assumptions",
            ["candidate", "case_verified", "system_verified"],
        ),
        _check(
            "execution_evidence_gate",
            isinstance(evidence_refs, list) and bool(evidence_refs),
            "case_verified requires execution or audit evidence refs",
            ["case_verified", "system_verified"],
        ),
        _check(
            "evidence_file_gate",
            isinstance(evidence_refs, list) and any(_path_exists(root, ref) for ref in evidence_refs),
            "at least one evidence_ref resolves in this workspace",
            ["case_verified", "system_verified"],
        ),
        _check(
            "generalization_gate",
            isinstance(benchmark_refs, list) and bool(benchmark_refs),
            "system_verified requires benchmark_refs or multi-variant checks",
            ["system_verified"],
        ),
    ]

    max_allowed_status = _max_allowed_status(checks)
    requested_index = STATUS_ORDER.index(requested_status)
    allowed_index = STATUS_ORDER.index(max_allowed_status)
    blocking_reasons = [
        f"{check['name']}:{check['detail']}"
        for check in checks
        if check["status"] != "pass" and requested_status in check.get("blocking_for", [])
    ]

    return {
        "status": "pass" if requested_index <= allowed_index else "fail",
        "candidate_path": str(candidate_path.relative_to(root) if candidate_path.is_relative_to(root) else candidate_path),
        "asset_id": data.get("id", candidate_path.stem),
        "requested_status": requested_status,
        "max_allowed_status": max_allowed_status,
        "checks": checks,
        "blocking_reasons": blocking_reasons,
        "not_checked": [
            "user_visual_satisfaction",
            "construction_document_compliance",
            "production_block_authorization",
            "table_c_registry_writeback",
        ],
    }
