"""Apply human drawing-read confirmation to SHELL_MODEL (BETA-DRAWING-READ-04)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from core.drawing_analysis.shell_loader import ShellLoadError, load_manual_shell
from core.schemas.validator import validate_value

CONFIRMATION_VERSION = "0.1"
SCHEMA_NAME = "shell_drawing_read_confirmation.schema.json"
SCHEMA_ROOT = Path(__file__).resolve().parents[1] / "schemas"
ACCEPT_ACTIONS = frozenset({"accept", "accept_with_risks"})


class ShellConfirmationError(ValueError):
    """Raised when confirmation cannot be applied to a shell candidate report."""


def schema_path() -> Path:
    return SCHEMA_ROOT / SCHEMA_NAME


def validate_confirmation_document(confirmation: dict[str, Any]) -> list[str]:
    schema = json.loads(schema_path().read_text(encoding="utf-8"))
    return validate_value(confirmation, schema)


def validate_confirmation_against_report(
    confirmation: dict[str, Any],
    report: dict[str, Any],
) -> list[str]:
    errors = validate_confirmation_document(confirmation)
    if errors:
        return errors

    draft = report.get("shell_candidate_draft", {})
    if not isinstance(draft, dict):
        errors.append("report.shell_candidate_draft is required.")
        return errors

    expected_id = str(draft.get("shell_candidate_id", ""))
    report_ref = confirmation.get("report_ref", {})
    if str(report_ref.get("shell_candidate_id", "")) != expected_id:
        errors.append(
            f"report_ref.shell_candidate_id mismatch: expected {expected_id!r}, "
            f"got {report_ref.get('shell_candidate_id')!r}"
        )

    action = str(confirmation.get("action", ""))
    if action == "reject":
        return errors

    if action not in ACCEPT_ACTIONS:
        errors.append(f"unknown action: {action!r}")
        return errors

    if action == "accept" and not report.get("ready_for_human_confirmation_file"):
        errors.append("action accept requires report.ready_for_human_confirmation_file=true")

    required_ids = {
        str(item["item_id"])
        for item in report.get("human_confirmation_items", [])
        if isinstance(item, dict) and item.get("required") is True
    }
    confirmed = {
        str(item["item_id"])
        for item in confirmation.get("confirmed_items", [])
        if isinstance(item, dict) and item.get("status") == "confirmed"
    }
    missing = sorted(required_ids - confirmed)
    if missing:
        errors.append(f"missing confirmed required items: {', '.join(missing)}")

    return errors


def build_shell_drawing_read_confirmation(
    report: dict[str, Any],
    *,
    confirmation_id: str,
    action: str = "accept",
    shell_id: str = "shell-drawing-read-confirmed",
    excluded_draft_ids: list[str] | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    """Build a confirmation document that confirms all required human items."""

    draft = report.get("shell_candidate_draft", {})
    confirmed_items = [
        {"item_id": str(item["item_id"]), "status": "confirmed"}
        for item in report.get("human_confirmation_items", [])
        if isinstance(item, dict) and item.get("required") is True
    ]
    return {
        "version": CONFIRMATION_VERSION,
        "confirmation_id": confirmation_id,
        "report_ref": {
            "shell_candidate_id": str(draft.get("shell_candidate_id", "")),
            "source_fixture": str(report.get("source", {}).get("path", "")),
        },
        "action": action,
        "confirmed_items": confirmed_items,
        "overrides": {
            "shell_id": shell_id,
            "excluded_draft_ids": list(excluded_draft_ids or []),
        },
        "notes": list(notes or ["Auto-built confirmation for drawing-read shell export."]),
        "confirmed_by": "drawing_read_workflow",
    }


def _draft_opening_to_shell(opening: dict[str, Any]) -> dict[str, Any]:
    draft_id = str(opening.get("draft_opening_id", "opening"))
    opening_id = draft_id.replace("draft-opening-", "opening-")
    if opening_id == draft_id:
        opening_id = draft_id.replace("draft-", "")
    return {
        "opening_id": opening_id,
        "type": str(opening.get("type", "entry")),
        "center": list(opening.get("center", [0.0, 0.0])),
        "width": float(opening.get("width", 900.0)),
    }


def _draft_bbox_item_to_shell(item: dict[str, Any], *, id_key: str, prefix: str) -> dict[str, Any]:
    draft_id = str(item.get(f"draft_{id_key}_id", item.get("draft_obstacle_id", item.get("draft_zone_id", ""))))
    entity_id = draft_id.replace(f"draft-{prefix}-", f"{prefix}-")
    if entity_id == draft_id:
        entity_id = draft_id.replace("draft-", "")
    return {
        id_key: entity_id,
        "bbox": dict(item.get("bbox", {})),
    }


def _build_shell_payload(report: dict[str, Any], confirmation: dict[str, Any]) -> dict[str, Any]:
    draft = report["shell_candidate_draft"]
    overrides = confirmation.get("overrides", {})
    excluded = {str(item) for item in overrides.get("excluded_draft_ids", [])}

    boundary = dict(overrides.get("boundary") or draft.get("boundary", {}))
    openings = overrides.get("openings")
    if openings is None:
        openings = [
            _draft_opening_to_shell(item)
            for item in draft.get("proposed_openings", [])
            if isinstance(item, dict) and str(item.get("draft_opening_id", "")) not in excluded
        ]
    fixed_obstacles = overrides.get("fixed_obstacles")
    if fixed_obstacles is None:
        fixed_obstacles = [
            _draft_bbox_item_to_shell(item, id_key="obstacle_id", prefix="obstacle")
            for item in draft.get("proposed_fixed_obstacles", [])
            if isinstance(item, dict) and str(item.get("draft_obstacle_id", "")) not in excluded
        ]
    no_place_zones = overrides.get("no_place_zones")
    if no_place_zones is None:
        no_place_zones = [
            _draft_bbox_item_to_shell(item, id_key="zone_id", prefix="no-place")
            for item in draft.get("proposed_no_place_zones", [])
            if isinstance(item, dict) and str(item.get("draft_zone_id", "")) not in excluded
        ]

    shell_id = str(overrides.get("shell_id", "shell-drawing-read-confirmed"))
    uncertainties = list(report.get("limitations", []))
    uncertainties.extend(str(note) for note in confirmation.get("notes", []))
    uncertainties.append(f"Exported from drawing-read confirmation {confirmation.get('confirmation_id', '')}.")

    required_connections: list[dict[str, Any]] = []
    if openings:
        first = openings[0]
        required_connections.append(
            {
                "connection_id": "entry-main",
                "target": str(first.get("opening_id", "")),
                "point": list(first.get("center", [0.0, 0.0])),
            }
        )

    return {
        "version": "0.1",
        "shell_id": shell_id,
        "units": str(draft.get("units", "mm")),
        "boundary": boundary,
        "openings": openings,
        "fixed_obstacles": fixed_obstacles,
        "no_place_zones": no_place_zones,
        "required_connections": required_connections,
        "building_elements": [
            {"element_id": "exterior-wall-shell", "type": "exterior_wall"},
        ],
        "uncertainties": uncertainties,
        "source": {
            "type": "drawing_read_confirmation",
            "path": str(confirmation.get("confirmation_id", "")),
        },
    }


def apply_shell_drawing_read_confirmation(
    report: dict[str, Any],
    confirmation: dict[str, Any],
) -> dict[str, Any]:
    """Validate confirmation and return normalized SHELL_MODEL via shell_loader."""

    errors = validate_confirmation_against_report(confirmation, report)
    if errors:
        raise ShellConfirmationError("; ".join(errors))

    action = str(confirmation.get("action", ""))
    if action == "reject":
        raise ShellConfirmationError("confirmation action is reject; no SHELL_MODEL produced")

    payload = _build_shell_payload(report, confirmation)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        temp_path = Path(handle.name)

    try:
        return load_manual_shell(temp_path)
    except ShellLoadError as exc:
        raise ShellConfirmationError(str(exc)) from exc
    finally:
        temp_path.unlink(missing_ok=True)


def load_shell_drawing_read_confirmation(path: str | Path) -> dict[str, Any]:
    confirmation_path = Path(path)
    confirmation = json.loads(confirmation_path.read_text(encoding="utf-8"))
    errors = validate_confirmation_document(confirmation)
    if errors:
        raise ShellConfirmationError("; ".join(errors))
    return confirmation
