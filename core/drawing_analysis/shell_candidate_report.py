"""Shell candidate confidence, gaps, and human confirmation points (BETA-DRAWING-READ-03)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.drawing_analysis.geometry_candidates import read_geometry_candidates_from_fixture

REPORT_VERSION = "0.1"
CONFIDENCE_THRESHOLD_LOW = 0.75
OVERALL_READY_THRESHOLD = 0.65


def _avg_confidence(candidates: list[dict[str, Any]]) -> float:
    if not candidates:
        return 0.0
    return round(sum(float(item.get("confidence", 0.0)) for item in candidates) / len(candidates), 2)


def _union_bbox_from_candidates(candidates: list[dict[str, Any]]) -> dict[str, list[float]]:
    bbox_union: dict[str, list[float]] | None = None
    for candidate in candidates:
        bbox = candidate.get("bbox")
        if not isinstance(bbox, dict):
            continue
        addition = {"min": list(bbox["min"]), "max": list(bbox["max"])}
        if bbox_union is None:
            bbox_union = addition
            continue
        bbox_union = {
            "min": [min(bbox_union["min"][0], addition["min"][0]), min(bbox_union["min"][1], addition["min"][1])],
            "max": [max(bbox_union["max"][0], addition["max"][0]), max(bbox_union["max"][1], addition["max"][1])],
        }
    return bbox_union or {"min": [0.0, 0.0], "max": [0.0, 0.0]}


def _boundary_closure_bonus(walls: list[dict[str, Any]]) -> float:
    if len(walls) < 4:
        return 0.0
    return 0.15 if len(walls) >= 4 else 0.05


def _infer_opening_width(door: dict[str, Any]) -> tuple[float, bool]:
    bbox = door.get("bbox", {})
    if isinstance(bbox, dict) and "min" in bbox and "max" in bbox:
        width = abs(float(bbox["max"][0]) - float(bbox["min"][0]))
        if width > 0:
            return width, False
    return 900.0, True


def _gap(code: str, message: str, *, severity: str) -> dict[str, str]:
    return {"code": code, "message": message, "severity": severity}


def _human_item(
    *,
    item_id: str,
    code: str,
    message: str,
    required: bool,
    related_candidate_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "item_id": item_id,
        "code": code,
        "message": message,
        "required": required,
        "related_candidate_ids": list(related_candidate_ids or []),
    }


def build_shell_candidate_confidence_report(
    geometry_candidates: dict[str, Any],
    *,
    summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Roll up READ-02 candidates into a machine-assertable confidence report."""

    walls = list(geometry_candidates.get("wall_segment_candidates", []))
    doors = list(geometry_candidates.get("door_opening_candidates", []))
    columns = list(geometry_candidates.get("column_candidates", []))
    no_place = list(geometry_candidates.get("no_place_zone_candidates", []))

    wall_avg = _avg_confidence(walls)
    boundary_score = min(0.95, round(wall_avg + _boundary_closure_bonus(walls), 2)) if walls else 0.0
    openings_score = _avg_confidence(doors) if doors else 0.0
    obstacles_score = _avg_confidence(columns) if columns else 0.0
    no_place_score = _avg_confidence(no_place) if no_place else 0.0

    boundary_bbox = _union_bbox_from_candidates(walls) if walls else {"min": [0.0, 0.0], "max": [0.0, 0.0]}

    proposed_openings: list[dict[str, Any]] = []
    for index, door in enumerate(doors, start=1):
        width, inferred = _infer_opening_width(door)
        geometry = door.get("geometry", {})
        insertion = geometry.get("insertion_point", [0.0, 0.0])
        center = [float(insertion[0]), float(insertion[1])] if len(insertion) >= 2 else [0.0, 0.0]
        proposed_openings.append(
            {
                "draft_opening_id": f"draft-opening-{index:02d}",
                "type": "entry" if index == 1 else "door",
                "center": center,
                "width": round(width, 2),
                "confidence": float(door.get("confidence", 0.0)),
                "source_candidate_id": str(door.get("candidate_id", "")),
                "width_inferred": inferred,
            }
        )

    proposed_obstacles = [
        {
            "draft_obstacle_id": f"draft-obstacle-{index:02d}",
            "bbox": dict(candidate.get("bbox", {})),
            "confidence": float(candidate.get("confidence", 0.0)),
            "source_candidate_id": str(candidate.get("candidate_id", "")),
        }
        for index, candidate in enumerate(columns, start=1)
    ]

    proposed_no_place = [
        {
            "draft_zone_id": f"draft-no-place-{index:02d}",
            "bbox": dict(candidate.get("bbox", {})),
            "confidence": float(candidate.get("confidence", 0.0)),
            "source_candidate_id": str(candidate.get("candidate_id", "")),
        }
        for index, candidate in enumerate(no_place, start=1)
    ]

    gaps: list[dict[str, str]] = []
    human_items: list[dict[str, Any]] = []

    if not walls:
        gaps.append(_gap("missing_boundary_walls", "No wall segment candidates detected.", severity="blocker"))
    elif len(walls) < 4:
        gaps.append(
            _gap(
                "boundary_not_closed",
                f"Only {len(walls)} wall segments; expected at least 4 for a closed shell outline.",
                severity="blocker",
            )
        )
    if boundary_score < CONFIDENCE_THRESHOLD_LOW and walls:
        gaps.append(
            _gap(
                "boundary_low_confidence",
                f"Boundary confidence {boundary_score} is below {CONFIDENCE_THRESHOLD_LOW}.",
                severity="warning",
            )
        )
    if not doors:
        gaps.append(_gap("missing_entry_opening", "No door opening candidates detected.", severity="blocker"))
    for door in proposed_openings:
        if door.get("width_inferred"):
            gaps.append(
                _gap(
                    "opening_width_inferred",
                    f"Opening {door['draft_opening_id']} width inferred as {door['width']} mm.",
                    severity="warning",
                )
            )

    entity_count = int(geometry_candidates.get("entity_summary_ref", {}).get("entity_count", 0))
    mapped = len(walls) + len(doors) + len(columns) + len(no_place)
    if summary and entity_count > mapped:
        gaps.append(
            _gap(
                "unmapped_entities",
                f"{entity_count - mapped} entities were not mapped to shell feature candidates.",
                severity="warning",
            )
        )

    if walls and boundary_bbox["max"] != boundary_bbox["min"]:
        human_items.append(
            _human_item(
                item_id="confirm-boundary-bbox",
                code="confirm_boundary_bbox",
                message="Confirm boundary bbox derived from wall segments before SHELL_MODEL export.",
                required=True,
                related_candidate_ids=[str(item.get("candidate_id", "")) for item in walls],
            )
        )
    for opening in proposed_openings:
        if opening.get("width_inferred"):
            human_items.append(
                _human_item(
                    item_id=f"confirm-{opening['draft_opening_id']}-width",
                    code="confirm_opening_width",
                    message=f"Confirm opening width for {opening['draft_opening_id']}.",
                    required=True,
                    related_candidate_ids=[opening["source_candidate_id"]],
                )
            )
    for obstacle in proposed_obstacles:
        human_items.append(
            _human_item(
                item_id=f"confirm-{obstacle['draft_obstacle_id']}",
                code="confirm_fixed_obstacle",
                message=f"Confirm fixed obstacle placement for {obstacle['draft_obstacle_id']}.",
                required=True,
                related_candidate_ids=[obstacle["source_candidate_id"]],
            )
        )
    for zone in proposed_no_place:
        human_items.append(
            _human_item(
                item_id=f"confirm-{zone['draft_zone_id']}",
                code="confirm_no_place_zone",
                message=f"Confirm no-place zone for {zone['draft_zone_id']}.",
                required=True,
                related_candidate_ids=[zone["source_candidate_id"]],
            )
        )

    for candidate in walls + doors + columns + no_place:
        confidence = float(candidate.get("confidence", 0.0))
        if confidence < CONFIDENCE_THRESHOLD_LOW:
            candidate_id = str(candidate.get("candidate_id", ""))
            human_items.append(
                _human_item(
                    item_id=f"review-low-confidence-{candidate_id}",
                    code="review_low_confidence_candidate",
                    message=f"Candidate {candidate_id} confidence {confidence} is below {CONFIDENCE_THRESHOLD_LOW}.",
                    required=True,
                    related_candidate_ids=[candidate_id],
                )
            )

    for index, gap in enumerate(gaps):
        if gap["severity"] == "blocker":
            human_items.append(
                _human_item(
                    item_id=f"resolve-gap-{gap['code']}-{index}",
                    code="resolve_gap",
                    message=gap["message"],
                    required=True,
                )
            )

    aspect_scores = [score for score in [boundary_score, openings_score, obstacles_score, no_place_score] if score > 0]
    overall = round(sum(aspect_scores) / len(aspect_scores), 2) if aspect_scores else 0.0
    has_blocker = any(item["severity"] == "blocker" for item in gaps)

    return {
        "version": REPORT_VERSION,
        "read_only": True,
        "source": dict(geometry_candidates.get("source", {"type": "geometry_candidates"})),
        "geometry_candidates_ref": {
            "version": geometry_candidates.get("version"),
            "counts": dict(geometry_candidates.get("counts", {})),
        },
        "confidence": {
            "overall": overall,
            "boundary": boundary_score,
            "openings": openings_score,
            "fixed_obstacles": obstacles_score,
            "no_place_zones": no_place_score,
        },
        "shell_candidate_draft": {
            "shell_candidate_id": "draft-shell-from-drawing-read",
            "units": "mm",
            "boundary": {"type": "bbox", **boundary_bbox},
            "proposed_openings": proposed_openings,
            "proposed_fixed_obstacles": proposed_obstacles,
            "proposed_no_place_zones": proposed_no_place,
        },
        "gaps": gaps,
        "human_confirmation_items": human_items,
        "ready_for_human_confirmation_file": (not has_blocker and overall >= OVERALL_READY_THRESHOLD),
        "limitations": [
            "draft shell only; not a validated SHELL_MODEL",
            "human confirmation file is READ-04; do not drive blank-shell CAD until confirmed",
        ],
    }


def read_shell_candidate_report_from_fixture(fixture_path: Path) -> dict[str, Any]:
    geometry_candidates = read_geometry_candidates_from_fixture(fixture_path)
    return build_shell_candidate_confidence_report(geometry_candidates)
