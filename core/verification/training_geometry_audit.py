"""Training-period geometry audit — global engine, case-driven checklist.

Training cases declare thresholds in ``projects/<case>/expected/audit_checklist.json``.
Core provides reusable probes; lessons from cases promote new probes here (not case scripts).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from core.cad_io.autocad_com import PREVIEW_LAYER, AutoCADComDriver

CHECKLIST_SCHEMA_VERSION = 2

# Probes registered here are global; case checklists only set thresholds / enable flags.
GLOBAL_PROBE_IDS = (
    "cleanliness",
    "reference_profile",
    "preview_profile",
    "reference_profile_match",
    "forbidden_patterns",
)


def load_training_audit_checklist(path: Path | str) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("audit checklist must be a JSON object")
    data.setdefault("schema_version", 1)
    return data


def _find_reference(driver: AutoCADComDriver, handle: str) -> object:
    for i in range(driver.model_space.Count):
        ent = driver.model_space.Item(i)
        if str(getattr(ent, "Handle", "")) == handle:
            return ent
    raise RuntimeError(f"Reference block {handle} not found.")


def read_block_layout_profile(driver: AutoCADComDriver, *, ref_handle: str) -> dict[str, float]:
    """Generic layout profile from a block insert (dimensions only, no geometry clone)."""
    ref = _find_reference(driver, ref_handle)
    blk = driver.doc.Blocks.Item(str(ref.EffectiveName))
    xs: list[float] = []
    ys: list[float] = []
    horiz: list[tuple[float, float]] = []
    for i in range(blk.Count):
        ent = blk.Item(i)
        on = str(getattr(ent, "ObjectName", "")).lower()
        if "line" not in on or "poly" in on:
            continue
        sp = list(ent.StartPoint)
        ep = list(ent.EndPoint)
        xs.extend([sp[0], ep[0]])
        ys.extend([sp[1], ep[1]])
        ln = math.hypot(ep[0] - sp[0], ep[1] - sp[1])
        if abs(sp[1] - ep[1]) < 2 and ln > 500:
            horiz.append(((sp[1] + ep[1]) / 2, ln))

    if not xs:
        raise RuntimeError("Reference block has no readable line geometry.")

    xmn, xmx = min(xs), max(xs)
    ymn, ymx = min(ys), max(ys)
    w, h = xmx - xmn, ymx - ymn

    inner_horiz = [
        (y, ln)
        for y, ln in horiz
        if w * 0.55 < ln < w * 0.98 and (y - ymn) > h * 0.04 and (ymx - y) > h * 0.04
    ]
    inner_horiz.sort(key=lambda t: -t[1])
    if not inner_horiz:
        raise RuntimeError("Cannot detect internal horizontal split in reference block.")
    split_y = inner_horiz[0][0]

    vert_x: list[float] = []
    for i in range(blk.Count):
        ent = blk.Item(i)
        on = str(getattr(ent, "ObjectName", "")).lower()
        if "line" not in on or "poly" in on:
            continue
        sp = list(ent.StartPoint)
        ep = list(ent.EndPoint)
        if abs(sp[0] - ep[0]) < 2 and math.hypot(ep[0] - sp[0], ep[1] - sp[1]) > h * 0.35:
            vert_x.append((sp[0] + ep[0]) / 2)
    vert_x.sort()
    left_inner = [x for x in vert_x if xmn + 60 < x < xmn + 200]
    right_inner = [x for x in vert_x if xmx - 200 < x < xmx - 60]
    arm_l = min(left_inner) - xmn if left_inner else w * 0.043
    arm_r = xmx - max(right_inner) if right_inner else w * 0.043

    arc_r = 30.0
    for i in range(blk.Count):
        ent = blk.Item(i)
        if "arc" in str(getattr(ent, "ObjectName", "")).lower():
            arc_r = float(ent.Radius)
            break

    return {
        "arm_width_mm": round((arm_l + arm_r) / 2, 1),
        "seat_split_ratio": round((split_y - ymn) / h, 3),
        "back_band_ratio": round((ymx - split_y) / h, 3),
        "fillet_r_mm": round(arc_r, 1),
        "ref_width_mm": round(w, 1),
        "ref_height_mm": round(h, 1),
    }


def _preview_entities(driver: AutoCADComDriver, *, x0: float, x1: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i in range(driver.model_space.Count):
        ent = driver.model_space.Item(i)
        if str(ent.Layer) != PREVIEW_LAYER:
            continue
        on = str(getattr(ent, "ObjectName", "")).lower()
        if "line" in on:
            sp = list(ent.StartPoint)
            ep = list(ent.EndPoint)
            if max(sp[0], ep[0]) < x0 - 1 or min(sp[0], ep[0]) > x1 + 1:
                continue
            rows.append(
                {
                    "kind": "line",
                    "sp": sp,
                    "ep": ep,
                    "len": math.hypot(ep[0] - sp[0], ep[1] - sp[1]),
                }
            )
        elif "arc" in on:
            c = list(ent.Center)
            if c[0] < x0 - 50 or c[0] > x1 + 50:
                continue
            sp = list(ent.StartPoint)
            ep = list(ent.EndPoint)
            rows.append(
                {
                    "kind": "arc",
                    "center": c,
                    "r": float(ent.Radius),
                    "sp": sp,
                    "ep": ep,
                }
            )
    return rows


def extract_preview_layout_profile(
    driver: AutoCADComDriver,
    *,
    preview_x0: float,
    preview_x1: float,
    preview_y0: float,
    preview_y1: float,
) -> dict[str, float | int | bool]:
    ents = _preview_entities(driver, x0=preview_x0, x1=preview_x1)
    w = preview_x1 - preview_x0
    h = preview_y1 - preview_y0

    horiz: list[tuple[float, float]] = []
    vert: list[tuple[float, float]] = []
    arc_rs: list[float] = []
    xs: list[float] = []
    ys: list[float] = []
    line_count = arc_count = micro = 0
    pts: list[tuple[float, float]] = []

    for ent in ents:
        if ent["kind"] == "line":
            line_count += 1
            sp, ep = ent["sp"], ent["ep"]
            xs.extend([sp[0], ep[0]])
            ys.extend([sp[1], ep[1]])
            pts.append((round(sp[0], 1), round(sp[1], 1)))
            pts.append((round(ep[0], 1), round(ep[1], 1)))
            if ent["len"] < 6:
                micro += 1
            if abs(sp[1] - ep[1]) < 2 and ent["len"] > w * 0.25:
                horiz.append(((sp[1] + ep[1]) / 2, ent["len"]))
            if abs(sp[0] - ep[0]) < 2 and ent["len"] > h * 0.25:
                vert.append(((sp[0] + ep[0]) / 2, ent["len"]))
        else:
            arc_count += 1
            arc_rs.append(ent["r"])
            sp, ep = ent["sp"], ent["ep"]
            xs.extend([sp[0], ep[0]])
            ys.extend([sp[1], ep[1]])
            pts.append((round(sp[0], 1), round(sp[1], 1)))
            pts.append((round(ep[0], 1), round(ep[1], 1)))

    from collections import Counter

    open_eps = sum(1 for n in Counter((round(x * 2) / 2, round(y * 2) / 2) for x, y in pts).values() if n == 1)

    if not xs:
        return {"entity_count": 0, "line_count": 0, "arc_count": 0, "micro_line_count": 0, "open_endpoint_count": 0}

    horiz.sort(key=lambda t: -t[1])
    inner = [
        (y, ln)
        for y, ln in horiz
        if w * 0.35 < ln < w * 0.98 and (y - preview_y0) > h * 0.04 and (preview_y1 - y) > h * 0.04
    ]
    split_y = inner[0][0] if inner else preview_y0 + h * 0.5

    vert.sort()
    left_verts = [v[0] for v in vert if v[0] < preview_x0 + w * 0.2]
    right_verts = [v[0] for v in vert if v[0] > preview_x1 - w * 0.2]
    inner_left = [x for x in left_verts if x > preview_x0 + 40]
    inner_right = [x for x in right_verts if x < preview_x1 - 40]
    arm_l = min(inner_left) - preview_x0 if inner_left else (min(left_verts) - preview_x0 if left_verts else 0.0)
    arm_r = preview_x1 - max(inner_right) if inner_right else (preview_x1 - max(right_verts) if right_verts else 0.0)

    margin = 2.0
    inner_xs = [x for x in xs if preview_x0 + margin < x < preview_x1 - margin]
    inner_ys = [y for y in ys if preview_y0 + margin < y < preview_y1 - margin]
    max_inset = 0.0
    if inner_xs and inner_ys:
        max_inset = max(
            min(inner_xs) - preview_x0,
            preview_x1 - max(inner_xs),
            min(inner_ys) - preview_y0,
            preview_y1 - max(inner_ys),
        )

    return {
        "entity_count": len(ents),
        "entity_total": line_count + arc_count,
        "line_count": line_count,
        "arc_count": arc_count,
        "micro_line_count": micro,
        "open_endpoint_count": open_eps,
        "preview_width_mm": round(w, 1),
        "preview_height_mm": round(h, 1),
        "seat_split_ratio": round((split_y - preview_y0) / h, 3),
        "back_band_ratio": round((preview_y1 - split_y) / h, 3),
        "arm_width_left_mm": round(arm_l, 1),
        "arm_width_right_mm": round(arm_r, 1),
        "max_inset_mm": round(max_inset, 1),
        "arc_r_min": round(min(arc_rs), 1) if arc_rs else 0.0,
        "rounded_rect_shell": len(arc_rs) >= 4 and len(horiz) >= 2,
        "seat_front_bow_count": _count_seat_front_bows(ents, preview_y0=preview_y0, split_y=split_y),
    }


def _count_seat_front_bows(
    ents: list[dict[str, Any]],
    *,
    preview_y0: float,
    split_y: float,
) -> int:
    """Large arcs whose center sits below the seat/back split — bowed seat fronts."""
    count = 0
    seat_band = split_y - preview_y0
    if seat_band < 1:
        return 0
    for ent in ents:
        if ent.get("kind") != "arc":
            continue
        r = float(ent["r"])
        cy = float(ent["center"][1])
        if r < seat_band * 0.25:
            continue
        if cy < split_y - seat_band * 0.15:
            count += 1
    return count


def detect_forbidden_patterns(profile: dict[str, float | int | bool]) -> list[str]:
    """Global anti-patterns — promote new detectors here when training finds repeat failures."""
    hits: list[str] = []
    bows = int(profile.get("seat_front_bow_count", 0))
    full_width_split_count = int(profile.get("full_width_split_count", 0))
    back_cushion_count = int(profile.get("back_cushion_count", 0))
    hard_back_count = int(profile.get("hard_back_count", 0))
    required_part_count = int(profile.get("required_part_count", 0))
    closed_part_count = int(profile.get("closed_part_count", 0))
    seat_cushion_count = int(profile.get("seat_cushion_count", 0))
    rounded_rect_family_count = int(profile.get("rounded_rect_family_count", 0))
    distinct_shape_family_count = int(profile.get("distinct_shape_family_count", 0))
    part_gap_count = int(profile.get("part_gap_count", 0))
    part_overlap_count = int(profile.get("part_overlap_count", 0))

    complete_visual_parts = (
        required_part_count
        and closed_part_count >= required_part_count
        and back_cushion_count >= 2
        and seat_cushion_count >= 2
    )

    if (
        profile.get("rounded_rect_shell")
        and float(profile.get("max_inset_mm", 0)) > 20
        and not complete_visual_parts
    ):
        if int(profile.get("arc_count", 0)) >= 16 and int(profile.get("entity_count", 0)) < 70:
            hits.append("closed_outer_shell")
            if bows < 2:
                hits.append("schematic_equal_grid")
    if full_width_split_count > 0 and back_cushion_count <= 0:
        hits.append("split_as_backrest")
    if required_part_count and closed_part_count < required_part_count:
        hits.append("missing_required_parts")
    if required_part_count and (back_cushion_count < 2 or seat_cushion_count < 2):
        hits.append("missing_required_parts")
    if (
        required_part_count
        and rounded_rect_family_count >= required_part_count
        and distinct_shape_family_count <= 1
    ):
        hits.append("rounded_rect_only_parts")
    if part_gap_count > 0 or part_overlap_count > 0:
        hits.append("part_connection_defects")
    if complete_visual_parts and hard_back_count > 0 and int(profile.get("sofa_layer_order_pass", 1)) <= 0:
        hits.append("sofa_direction_semantics_inverted")
    return hits


def _visual_parts_summary_from_checklist(semantic: dict[str, Any]) -> dict[str, int]:
    summary = semantic.get("visual_parts_summary", {})
    if not isinstance(summary, dict):
        return {}
    allowed_keys = {
        "required_part_count",
        "closed_part_count",
        "seat_cushion_count",
        "back_cushion_count",
        "hard_back_count",
        "sofa_layer_order_pass",
        "full_width_split_count",
        "rounded_rect_family_count",
        "distinct_shape_family_count",
        "part_gap_count",
        "part_overlap_count",
    }
    normalized: dict[str, int] = {}
    for key in allowed_keys:
        value = summary.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            normalized[key] = value
    return normalized


def _check_range(value: float, spec: dict[str, float], key: str, failures: list[str]) -> None:
    if "min" in spec and value < float(spec["min"]):
        failures.append(key)
    if "max" in spec and value > float(spec["max"]):
        failures.append(key)


def _evaluate_reference_profile_match(
    preview: dict[str, float | int | bool],
    reference: dict[str, float],
    spec: dict[str, Any],
    failures: list[str],
    deltas: dict[str, float],
) -> None:
    split_tol = float(spec.get("seat_split_ratio_tol", 0.08))
    back_tol = float(spec.get("back_band_ratio_tol", 0.08))
    arm_tol = float(spec.get("arm_width_tol_mm", 35))
    max_inset = float(spec.get("max_inset_mm", 38))
    back_min = float(spec.get("back_band_min", 0.10))
    back_max = float(spec.get("back_band_max", 0.35))
    check_split_ratios = bool(spec.get("check_split_ratios", True))

    split_delta = abs(float(preview.get("seat_split_ratio", 0)) - reference["seat_split_ratio"])
    back_delta = abs(float(preview.get("back_band_ratio", 0)) - reference["back_band_ratio"])
    arm_delta = max(
        abs(float(preview.get("arm_width_left_mm", 999)) - reference["arm_width_mm"]),
        abs(float(preview.get("arm_width_right_mm", 999)) - reference["arm_width_mm"]),
    )
    deltas["seat_split_ratio"] = round(split_delta, 3)
    deltas["back_band_ratio"] = round(back_delta, 3)
    deltas["arm_width_mm"] = round(arm_delta, 1)

    if check_split_ratios:
        if split_delta > split_tol:
            failures.append("semantic_seat_split_ratio")
        back = float(preview.get("back_band_ratio", 0))
        if back_delta > back_tol or back < back_min or back > back_max:
            failures.append("semantic_back_band_ratio")
    if arm_delta > arm_tol:
        failures.append("semantic_arm_width")
    if float(preview.get("max_inset_mm", 999)) > max_inset:
        failures.append("semantic_excessive_inset")


def run_training_geometry_audit(
    driver: AutoCADComDriver,
    checklist: dict[str, Any],
    *,
    preview_bounds: dict[str, float],
    reference_handle: str | None = None,
) -> dict[str, Any]:
    """Run global probes with case checklist thresholds."""
    checks = checklist.get("checks", checklist)
    if not isinstance(checks, dict):
        raise ValueError("checklist.checks must be an object")

    px0 = float(preview_bounds["x0"])
    px1 = float(preview_bounds["x1"])
    py0 = float(preview_bounds["y0"])
    py1 = float(preview_bounds["y1"])

    ref_cfg = checklist.get("reference", {})
    ref_handle = reference_handle or (ref_cfg.get("handle") if isinstance(ref_cfg, dict) else None)

    preview = extract_preview_layout_profile(
        driver, preview_x0=px0, preview_x1=px1, preview_y0=py0, preview_y1=py1
    )
    reference: dict[str, float] | None = None
    if ref_handle and (ref_cfg.get("read_profile", True) if isinstance(ref_cfg, dict) else True):
        reference = read_block_layout_profile(driver, ref_handle=str(ref_handle))

    failures: list[str] = []
    deltas: dict[str, float] = {}
    forbidden_hits: list[str] = []

    cleanliness = checks.get("cleanliness", {})
    if isinstance(cleanliness, dict):
        if "preview_width_mm" in cleanliness:
            _check_range(float(preview.get("preview_width_mm", 0)), cleanliness["preview_width_mm"], "preview_width_mm", failures)
        if "micro_line_count_max" in cleanliness:
            if int(preview.get("micro_line_count", 0)) > int(cleanliness["micro_line_count_max"]):
                failures.append("micro_line_count")
        if "open_endpoint_count_max" in cleanliness:
            if int(preview.get("open_endpoint_count", 0)) > int(cleanliness["open_endpoint_count_max"]):
                failures.append("open_endpoint_count")
        if "entity_total_max" in cleanliness:
            if int(preview.get("entity_total", 0)) > int(cleanliness["entity_total_max"]):
                failures.append("entity_count_high")

    semantic = checks.get("semantic", {})
    if isinstance(semantic, dict):
        if reference and "reference_profile_match" in semantic:
            spec = semantic["reference_profile_match"]
            if isinstance(spec, dict):
                _evaluate_reference_profile_match(preview, reference, spec, failures, deltas)
        min_entities = semantic.get("min_entity_count")
        if min_entities is not None and int(preview.get("entity_count", 0)) < int(min_entities):
            failures.append("semantic_too_sparse")
        min_bows = semantic.get("min_seat_front_bow_count")
        if min_bows is not None and int(preview.get("seat_front_bow_count", 0)) < int(min_bows):
            failures.append("semantic_seat_front_bow")
        forbidden = semantic.get("forbidden_patterns", [])
        if forbidden:
            forbidden_profile = {**preview, **_visual_parts_summary_from_checklist(semantic)}
            forbidden_hits = detect_forbidden_patterns(forbidden_profile)
            for pattern in forbidden:
                if pattern in forbidden_hits:
                    failures.append(f"forbidden_{pattern}")

    semantic_pass = not any(
        f.startswith("semantic_") or f.startswith("forbidden_") for f in failures
    )
    cleanliness_pass = not any(
        f in failures
        for f in (
            "preview_width_mm",
            "micro_line_count",
            "open_endpoint_count",
            "entity_count_high",
        )
    )

    return {
        "schema_version": CHECKLIST_SCHEMA_VERSION,
        "engine": "core.verification.training_geometry_audit",
        "case_id": checklist.get("case_id"),
        "preview_profile": preview,
        "reference_profile": reference,
        "profile_deltas": deltas,
        "forbidden_pattern_hits": forbidden_hits,
        "cleanliness_pass": cleanliness_pass,
        "semantic_pass": semantic_pass,
        "audit_failures": failures,
        "audit_pass": len(failures) == 0,
        "agent_review_required": checklist.get(
            "agent_review_required",
            ["visual_match_brief", "no_schematic_shortcut"],
        ),
    }


def merge_legacy_audit_fields(report: dict[str, Any]) -> dict[str, Any]:
    """Flatten preview_profile fields for older consumers (geometry_audit.json)."""
    preview = report.get("preview_profile", {})
    if isinstance(preview, dict):
        merged = {**preview, **report}
        return merged
    return report
