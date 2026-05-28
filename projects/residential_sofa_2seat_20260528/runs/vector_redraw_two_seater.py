#!/usr/bin/env python
"""Two-seater from 5S03232: block-local X clip (drop middle third, shift right third)."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from core.cad_io.autocad_com import PREVIEW_LAYER, AutoCADComDriver

CASE_ROOT = Path(__file__).resolve().parents[1]
AUDIT_CHECKLIST = CASE_ROOT / "expected" / "audit_checklist.json"
ROUND = "round4"
SEAM_BAND_MM = 12.0
SEAM_CLUTTER_MAX_LEN = 20.0
SHORT_LINE_MM = 8.0
MICRO_LINE_MM = 6.0
DEGEN_LINE_MM = 1.0


def _polyline_local_points(ent: object) -> list[tuple[float, float]]:
    coords = list(ent.Coordinates)
    step = 3 if len(coords) >= 3 and len(coords) % 3 == 0 else 2
    pts: list[tuple[float, float]] = []
    for j in range(0, len(coords) - (step - 1), step):
        pts.append((float(coords[j]), float(coords[j + 1])))
    return pts


def _map_x_drop_middle(x: float, *, mid_lo: float, mid_hi: float, seat_w: float) -> float | None:
    """Drop interior of middle seat band; keep boundary at mid_lo as 2-seat center seam."""
    if mid_lo < x < mid_hi:
        return None
    if x >= mid_hi:
        return x - seat_w
    return x


def _clip_line_segments(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    x0: float,
    x1_limit: float,
    mid_lo: float,
    mid_hi: float,
    seat_w: float,
) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    def map_point(x: float, y: float) -> tuple[float, float] | None:
        mx = _map_x_drop_middle(x, mid_lo=mid_lo, mid_hi=mid_hi, seat_w=seat_w)
        if mx is None:
            return None
        if mx < x0 - 1 or mx > x1_limit + 1:
            return None
        return (mx, y)

    if abs(y1 - y2) < 2.0 and abs(x1 - x2) > seat_w * 2.0:
        y = (y1 + y2) / 2.0
        return [((x0, y), (x1_limit, y))]

    raw_pts: list[tuple[float, float, float]] = [(x1, y1, 0.0), (x2, y2, 1.0)]
    for x_cut in (mid_lo, mid_hi):
        pt = _interp_at_x(x1, y1, x2, y2, x_cut)
        if pt is not None:
            t = (x_cut - x1) / (x2 - x1) if abs(x2 - x1) > 1e-9 else 0.0
            raw_pts.append((pt[0], pt[1], t))
    raw_pts.sort(key=lambda p: p[0])

    mapped: list[tuple[float, float]] = []
    for x, y, _t in raw_pts:
        mp = map_point(x, y)
        if mp is not None:
            if not mapped or math.hypot(mp[0] - mapped[-1][0], mp[1] - mapped[-1][1]) > 0.01:
                mapped.append(mp)

    if len(mapped) < 2:
        return []
    out: list[tuple[tuple[float, float], tuple[float, float]]] = []
    seg_start = 0
    for i in range(1, len(mapped)):
        gap_x = mapped[i][0] - mapped[i - 1][0]
        if gap_x > seat_w * 0.5:
            if i - seg_start >= 2:
                out.append((mapped[seg_start], mapped[i - 1]))
            seg_start = i
    if len(mapped) - seg_start >= 2:
        out.append((mapped[seg_start], mapped[-1]))
    elif len(mapped) == 2:
        out.append((mapped[0], mapped[1]))
    filtered: list[tuple[tuple[float, float], tuple[float, float]]] = []
    preview_w = x1_limit - x0
    for p1, p2 in out:
        cx = (p1[0] + p2[0]) / 2.0
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        is_full_rail = abs(p1[1] - p2[1]) < 2.0 and length > preview_w * 0.7
        is_long_seam = abs(p1[0] - p2[0]) < 5.0 and length > 100.0
        if (
            abs(cx - mid_lo) <= SEAM_BAND_MM
            and length < SEAM_CLUTTER_MAX_LEN
            and not is_full_rail
            and not is_long_seam
        ):
            continue
        filtered.append((p1, p2))
    return filtered


def _interp_at_x(x1: float, y1: float, x2: float, y2: float, x_cut: float) -> tuple[float, float] | None:
    if abs(x2 - x1) < 1e-9:
        return None
    t = (x_cut - x1) / (x2 - x1)
    if t < -1e-9 or t > 1 + 1e-9:
        return None
    t = max(0.0, min(1.0, t))
    return (x_cut, y1 + t * (y2 - y1))


def _count_block_lines_expected(block: object, *, xmn: float, seat_w: float) -> int:
    mid_lo_l = xmn + seat_w
    mid_hi_l = xmn + 2 * seat_w
    kept = 0
    for i in range(block.Count):
        ent = block.Item(i)
        on = str(getattr(ent, "ObjectName", "")).lower()
        if "line" not in on or "poly" in on:
            continue
        try:
            sp = list(ent.StartPoint)
            ep = list(ent.EndPoint)
        except Exception:
            continue
        x1, x2 = min(sp[0], ep[0]), max(sp[0], ep[0])
        if x1 >= mid_lo_l and x2 <= mid_hi_l:
            continue
        kept += 1
    return kept


def _reference_short_line_baseline(block: object, *, xmn: float, seat_w: float) -> int:
    mid_lo_l = xmn + seat_w
    mid_hi_l = xmn + 2 * seat_w
    short = 0
    for i in range(block.Count):
        ent = block.Item(i)
        on = str(getattr(ent, "ObjectName", "")).lower()
        if "line" not in on or "poly" in on:
            continue
        try:
            sp = list(ent.StartPoint)
            ep = list(ent.EndPoint)
        except Exception:
            continue
        x1, x2 = min(sp[0], ep[0]), max(sp[0], ep[0])
        if x1 >= mid_lo_l and x2 <= mid_hi_l:
            continue
        if math.hypot(ep[0] - sp[0], ep[1] - sp[1]) < SHORT_LINE_MM:
            short += 1
    return short


def _reference_micro_line_baseline(block: object, *, xmn: float, seat_w: float) -> int:
    mid_lo_l = xmn + seat_w
    mid_hi_l = xmn + 2 * seat_w
    micro = 0
    for i in range(block.Count):
        ent = block.Item(i)
        on = str(getattr(ent, "ObjectName", "")).lower()
        if "line" not in on or "poly" in on:
            continue
        try:
            sp = list(ent.StartPoint)
            ep = list(ent.EndPoint)
        except Exception:
            continue
        x1, x2 = min(sp[0], ep[0]), max(sp[0], ep[0])
        if x1 >= mid_lo_l and x2 <= mid_hi_l:
            continue
        if math.hypot(ep[0] - sp[0], ep[1] - sp[1]) < MICRO_LINE_MM:
            micro += 1
    return micro


def _dedupe_overlapping_horizontals(driver: AutoCADComDriver) -> int:
    """Remove shorter horizontal when stacked on a longer one (same Y, overlapping X)."""
    entries: list[tuple[float, float, float, str, float]] = []
    for i in range(driver.model_space.Count):
        ent = driver.model_space.Item(i)
        if str(ent.Layer) != PREVIEW_LAYER:
            continue
        on = str(getattr(ent, "ObjectName", "")).lower()
        if "line" not in on:
            continue
        try:
            sp = list(ent.StartPoint)
            ep = list(ent.EndPoint)
            handle = str(ent.Handle)
        except Exception:
            continue
        if abs(sp[1] - ep[1]) > 2.0:
            continue
        x1, x2 = min(sp[0], ep[0]), max(sp[0], ep[0])
        if x2 - x1 < 40:
            continue
        y = (sp[1] + ep[1]) / 2.0
        entries.append((y, x1, x2, handle, x2 - x1))

    remove_handles: set[str] = set()
    for i in range(len(entries)):
        y1, a1, b1, h1, len1 = entries[i]
        if h1 in remove_handles:
            continue
        for j in range(i + 1, len(entries)):
            y2, a2, b2, h2, len2 = entries[j]
            if abs(y1 - y2) > 1.5:
                continue
            overlap = max(0.0, min(b1, b2) - max(a1, a2))
            shorter = min(len1, len2)
            if overlap < max(20.0, shorter * 0.5):
                continue
            if len1 >= len2:
                remove_handles.add(h2)
            else:
                remove_handles.add(h1)
                break

    deleted = 0
    for i in range(driver.model_space.Count - 1, -1, -1):
        ent = driver.model_space.Item(i)
        if str(getattr(ent, "Handle", "")) in remove_handles:
            ent.Delete()
            deleted += 1
    return deleted


def _cleanup_seam_clutter(
    driver: AutoCADComDriver,
    *,
    mid_lo: float,
) -> int:
    removed = 0
    for i in range(driver.model_space.Count - 1, -1, -1):
        ent = driver.model_space.Item(i)
        if str(ent.Layer) != PREVIEW_LAYER:
            continue
        on = str(getattr(ent, "ObjectName", "")).lower()
        if "line" not in on:
            continue
        try:
            sp = list(ent.StartPoint)
            ep = list(ent.EndPoint)
        except Exception:
            continue
        cx = (sp[0] + ep[0]) / 2.0
        length = math.hypot(ep[0] - sp[0], ep[1] - sp[1])
        is_long_seam = abs(sp[0] - ep[0]) < 5.0 and length > 100.0
        if abs(cx - mid_lo) > SEAM_BAND_MM:
            continue
        if length >= SEAM_CLUTTER_MAX_LEN or is_long_seam:
            continue
        ent.Delete()
        removed += 1
    return removed


def _classify_block_line(
    lx1: float,
    lx2: float,
    *,
    xmn: float,
    seat_w: float,
) -> str:
    mid_lo_l = xmn + seat_w
    mid_hi_l = xmn + 2 * seat_w
    if lx2 <= mid_lo_l + 0.5:
        return "left"
    if lx1 >= mid_hi_l - 0.5:
        return "right"
    if lx1 >= mid_lo_l - 0.5 and lx2 <= mid_hi_l + 0.5:
        return "middle"
    return "span"


def _map_block_line_endpoints(
    sp: list[float],
    ep: list[float],
    *,
    wcs_from_block_local,
    seat_w: float,
    xmn: float,
    zone: str,
) -> tuple[tuple[float, float], tuple[float, float]] | None:
    if zone == "middle":
        return None
    wsp = wcs_from_block_local(sp[0], sp[1])
    wep = wcs_from_block_local(ep[0], ep[1])
    if zone == "right":
        wsp = (wsp[0] - seat_w, wsp[1])
        wep = (wep[0] - seat_w, wep[1])
    return wsp, wep


def _remove_degenerate_lines(driver: AutoCADComDriver) -> int:
    removed = 0
    for i in range(driver.model_space.Count - 1, -1, -1):
        ent = driver.model_space.Item(i)
        if str(ent.Layer) != PREVIEW_LAYER:
            continue
        if "line" not in str(getattr(ent, "ObjectName", "")).lower():
            continue
        try:
            sp = list(ent.StartPoint)
            ep = list(ent.EndPoint)
        except Exception:
            continue
        if math.hypot(ep[0] - sp[0], ep[1] - sp[1]) < DEGEN_LINE_MM:
            ent.Delete()
            removed += 1
    return removed


def _remove_micro_fillet_ticks(
    driver: AutoCADComDriver,
    *,
    mid_lo: float,
) -> int:
    """Only remove tiny segments in the center seam band (not armrest fillets)."""
    removed = 0
    for i in range(driver.model_space.Count - 1, -1, -1):
        ent = driver.model_space.Item(i)
        if str(ent.Layer) != PREVIEW_LAYER:
            continue
        if "line" not in str(getattr(ent, "ObjectName", "")).lower():
            continue
        try:
            sp = list(ent.StartPoint)
            ep = list(ent.EndPoint)
        except Exception:
            continue
        length = math.hypot(ep[0] - sp[0], ep[1] - sp[1])
        if length >= 5.0:
            continue
        cx = (sp[0] + ep[0]) / 2.0
        if abs(cx - mid_lo) > SEAM_BAND_MM:
            continue
        if abs(sp[0] - ep[0]) < 5 and length > 100:
            continue
        ent.Delete()
        removed += 1
    return removed


def _remove_duplicate_lines(driver: AutoCADComDriver, *, tol: float = 0.8) -> int:
    seen: set[tuple[tuple[float, float], tuple[float, float]]] = set()
    removed = 0
    for i in range(driver.model_space.Count - 1, -1, -1):
        ent = driver.model_space.Item(i)
        if str(ent.Layer) != PREVIEW_LAYER:
            continue
        if "line" not in str(getattr(ent, "ObjectName", "")).lower():
            continue
        try:
            sp = list(ent.StartPoint)
            ep = list(ent.EndPoint)
        except Exception:
            continue
        a = (round(sp[0] / tol), round(sp[1] / tol))
        b = (round(ep[0] / tol), round(ep[1] / tol))
        key = tuple(sorted([a, b]))
        if key in seen:
            ent.Delete()
            removed += 1
        else:
            seen.add(key)
    return removed


def _count_preview_arcs(driver: AutoCADComDriver) -> int:
    n = 0
    for i in range(driver.model_space.Count):
        ent = driver.model_space.Item(i)
        if str(ent.Layer) != PREVIEW_LAYER:
            continue
        if "arc" in str(getattr(ent, "ObjectName", "")).lower():
            n += 1
    return n


def _audit_preview(
    driver: AutoCADComDriver,
    *,
    ref_min_y: float,
    ref_max_y: float,
    preview_x0: float,
    preview_x1: float,
    seat_w: float,
    expected_lines: int,
    ref_short_baseline: int,
    ref_micro_baseline: int,
) -> dict[str, object]:
    preview_lines = 0
    long_horiz = 0
    bottom_rail = False
    backrest_verticals = 0
    center_seam_vertical = False
    short_lines = 0
    seam_band_short = 0
    near_overlap_horiz = 0
    horiz_segments: list[tuple[float, float, float]] = []
    y_back_lo = ref_min_y + (ref_max_y - ref_min_y) * 0.55
    mid_lo = preview_x0 + seat_w
    seam_tol = seat_w * 0.08

    for i in range(driver.model_space.Count):
        ent = driver.model_space.Item(i)
        if str(ent.Layer) != PREVIEW_LAYER:
            continue
        on = str(getattr(ent, "ObjectName", "")).lower()
        if "line" not in on:
            continue
        preview_lines += 1
        try:
            sp = list(ent.StartPoint)
            ep = list(ent.EndPoint)
        except Exception:
            continue
        length = math.hypot(ep[0] - sp[0], ep[1] - sp[1])
        dy = abs(sp[1] - ep[1])
        dx = abs(sp[0] - ep[0])
        cx = (sp[0] + ep[0]) / 2.0
        if length < SHORT_LINE_MM:
            short_lines += 1
            if abs(cx - mid_lo) <= SEAM_BAND_MM:
                seam_band_short += 1
        if dy < 3 and length > (preview_x1 - preview_x0) * 0.7:
            long_horiz += 1
            if abs((sp[1] + ep[1]) / 2 - ref_min_y) < 30:
                bottom_rail = True
        if dy < 3 and length > 40:
            horiz_segments.append(((sp[1] + ep[1]) / 2, min(sp[0], ep[0]), max(sp[0], ep[0])))
        if dx < 5 and length > 15:
            cy = (sp[1] + ep[1]) / 2
            if cy > y_back_lo:
                backrest_verticals += 1
                if abs(cx - mid_lo) < seam_tol:
                    center_seam_vertical = True

    for i in range(len(horiz_segments)):
        y1, x1a, x1b = horiz_segments[i]
        for j in range(i + 1, len(horiz_segments)):
            y2, x2a, x2b = horiz_segments[j]
            if abs(y1 - y2) > 1.0:
                continue
            overlap = max(0.0, min(x1b, x2b) - max(x1a, x2a))
            if overlap > 20.0 and abs((x1b - x1a) - (x2b - x2a)) > 5.0:
                near_overlap_horiz += 1

    preview_width = preview_x1 - preview_x0
    ratio = round(preview_lines / max(expected_lines, 1), 3)
    short_delta = short_lines - ref_short_baseline
    line_delta = preview_lines - expected_lines
    checklist = json.loads(AUDIT_CHECKLIST.read_text(encoding="utf-8"))["checks"]
    failures: list[str] = []

    if not (checklist["preview_width_mm"]["min"] <= preview_width <= checklist["preview_width_mm"]["max"]):
        failures.append("preview_width_mm")
    if ratio < checklist["line_retention_ratio"]["min"]:
        failures.append("line_retention_ratio")
    if ratio > checklist["line_retention_ratio"].get("max", 999):
        failures.append("line_retention_ratio_high")
    if long_horiz < checklist["long_horizontal_count"]["min"]:
        failures.append("long_horizontal_count")
    if checklist["bottom_rail_present"]["required"] and not bottom_rail:
        failures.append("bottom_rail_present")
    if checklist["center_seam_vertical_present"]["required"] and not center_seam_vertical:
        failures.append("center_seam_vertical_present")
    if backrest_verticals < checklist["backrest_vertical_count"]["min"]:
        failures.append("backrest_vertical_count")
    if seam_band_short > checklist["seam_band_short_line_max"]:
        failures.append("seam_band_short_line_max")
    if near_overlap_horiz > checklist["near_overlap_horizontal_max"]:
        failures.append("near_overlap_horizontal_max")
    if short_delta > checklist["short_line_count_max_delta"]:
        failures.append("short_line_count_max_delta")
    if line_delta > checklist["preview_line_count_max_delta"]:
        failures.append("preview_line_count_max_delta")
    arc_count = _count_preview_arcs(driver)
    if arc_count < checklist.get("arc_count_min", {}).get("min", 0):
        failures.append("arc_count_min")
    micro_count = 0
    for i in range(driver.model_space.Count):
        ent = driver.model_space.Item(i)
        if str(ent.Layer) != PREVIEW_LAYER:
            continue
        if "line" not in str(getattr(ent, "ObjectName", "")).lower():
            continue
        try:
            sp = list(ent.StartPoint)
            ep = list(ent.EndPoint)
        except Exception:
            continue
        if math.hypot(ep[0] - sp[0], ep[1] - sp[1]) < MICRO_LINE_MM:
            micro_count += 1
    if micro_count > checklist.get("micro_line_count_max", {}).get("max", 9999):
        failures.append("micro_line_count_max")
    if micro_count - ref_micro_baseline > checklist.get("micro_line_count_max_delta", 999):
        failures.append("micro_line_count_max_delta")

    return {
        "preview_line_count": preview_lines,
        "expected_approx_lines": expected_lines,
        "preview_line_count_delta": line_delta,
        "preview_width_mm": round(preview_width, 3),
        "line_retention_ratio": ratio,
        "long_horizontal_count": long_horiz,
        "bottom_rail_present": bottom_rail,
        "center_seam_vertical_present": center_seam_vertical,
        "backrest_vertical_count": backrest_verticals,
        "short_line_count": short_lines,
        "reference_short_line_baseline": ref_short_baseline,
        "short_line_count_delta": short_delta,
        "seam_band_short_line_count": seam_band_short,
        "near_overlap_horizontal_count": near_overlap_horiz,
        "arc_count": arc_count,
        "micro_line_count": micro_count,
        "reference_micro_line_baseline": ref_micro_baseline,
        "audit_pass": len(failures) == 0,
        "audit_failures": failures,
    }


def _ensure_center_seam_from_block(
    driver: AutoCADComDriver,
    block: object,
    *,
    wcs_from_block_local,
    xmn: float,
    seat_w: float,
    mid_lo: float,
    y_back_lo: float,
    created: list[str],
) -> bool:
    """Middle-third backrest dividers sit slightly inside the band — merge to one center seam."""
    lo_band = xmn + seat_w - 30.0
    hi_band = xmn + 2.0 * seat_w + 30.0
    y_min_w: float | None = None
    y_max_w: float | None = None
    for i in range(block.Count):
        ent = block.Item(i)
        on = str(getattr(ent, "ObjectName", "")).lower()
        if "line" not in on or "poly" in on:
            continue
        try:
            sp = list(ent.StartPoint)
            ep = list(ent.EndPoint)
        except Exception:
            continue
        if abs(sp[0] - ep[0]) > 8:
            continue
        bx = (sp[0] + ep[0]) / 2.0
        if bx < lo_band or bx > hi_band:
            continue
        if abs(sp[1] - ep[1]) < 80:
            continue
        wsp = wcs_from_block_local(sp[0], sp[1])
        wep = wcs_from_block_local(ep[0], ep[1])
        if (wsp[1] + wep[1]) / 2 < y_back_lo:
            continue
        y_min_w = min(wsp[1], wep[1]) if y_min_w is None else min(y_min_w, wsp[1], wep[1])
        y_max_w = max(wsp[1], wep[1]) if y_max_w is None else max(y_max_w, wsp[1], wep[1])
    if y_min_w is None or y_max_w is None:
        return False
    r = driver.draw_line(
        start_point=[mid_lo, y_min_w, 0],
        end_point=[mid_lo, y_max_w, 0],
        layer=PREVIEW_LAYER,
        color="cyan",
    )
    created.append(r["handle"])
    return True


def main() -> int:
    driver = AutoCADComDriver(connect_existing_only=True)
    driver.ensure_layer(PREVIEW_LAYER)
    doc = driver.doc
    ms = driver.model_space

    ref = None
    for i in range(ms.Count):
        ent = ms.Item(i)
        if str(getattr(ent, "Handle", "")) == "4A2":
            ref = ent
            break
    if ref is None:
        raise RuntimeError("Reference block 4A2 not found.")

    for i in range(ms.Count - 1, -1, -1):
        ent = ms.Item(i)
        if str(ent.Layer) == PREVIEW_LAYER:
            ent.Delete()

    ref_bb = ref.GetBoundingBox()
    ref_min_x = float(ref_bb[0][0])
    ref_min_y = float(ref_bb[0][1])
    ref_max_x = float(ref_bb[1][0])
    ref_max_y = float(ref_bb[1][1])
    ref_w = ref_max_x - ref_min_x
    seat_w = ref_w / 3.0

    gap = 400.0
    preview_x0 = ref_max_x + gap
    preview_x1 = preview_x0 + (ref_w - seat_w)
    mid_lo = preview_x0 + seat_w
    mid_hi = preview_x0 + 2.0 * seat_w

    xmn_local, ymx_local = 162232.94155195105, 131901.7632147302
    block_name = str(getattr(ref, "EffectiveName", getattr(ref, "Name", "5S03232")))

    def wcs_from_block_local(lx: float, ly: float) -> tuple[float, float]:
        return preview_x0 + (lx - xmn_local), ref_min_y + (ymx_local - ly)

    block = doc.Blocks.Item(block_name)
    expected_lines = _count_block_lines_expected(block, xmn=xmn_local, seat_w=seat_w)
    ref_short_baseline = _reference_short_line_baseline(block, xmn=xmn_local, seat_w=seat_w)
    ref_micro_baseline = _reference_micro_line_baseline(block, xmn=xmn_local, seat_w=seat_w)
    y_back_lo = ref_min_y + (ref_max_y - ref_min_y) * 0.55

    created: list[str] = []
    skipped_arcs = 0

    for i in range(block.Count):
        ent = block.Item(i)
        on = str(getattr(ent, "ObjectName", "")).lower()
        if "line" in on and "poly" not in on:
            sp = list(ent.StartPoint)
            ep = list(ent.EndPoint)
            lx1, lx2 = min(sp[0], ep[0]), max(sp[0], ep[0])
            zone = _classify_block_line(lx1, lx2, xmn=xmn_local, seat_w=seat_w)
            if zone == "middle":
                continue
            if zone in ("left", "right"):
                mapped = _map_block_line_endpoints(
                    sp,
                    ep,
                    wcs_from_block_local=wcs_from_block_local,
                    seat_w=seat_w,
                    xmn=xmn_local,
                    zone=zone,
                )
                if mapped is None:
                    continue
                p1, p2 = mapped
                r = driver.draw_line(
                    start_point=[p1[0], p1[1], 0],
                    end_point=[p2[0], p2[1], 0],
                    layer=PREVIEW_LAYER,
                    color="cyan",
                )
                created.append(r["handle"])
                continue
            wsp1 = wcs_from_block_local(sp[0], sp[1])
            wep1 = wcs_from_block_local(ep[0], ep[1])
            segments = _clip_line_segments(
                wsp1[0],
                wsp1[1],
                wep1[0],
                wep1[1],
                x0=preview_x0,
                x1_limit=preview_x1,
                mid_lo=mid_lo,
                mid_hi=mid_hi,
                seat_w=seat_w,
            )
            for p1, p2 in segments:
                r = driver.draw_line(
                    start_point=[p1[0], p1[1], 0],
                    end_point=[p2[0], p2[1], 0],
                    layer=PREVIEW_LAYER,
                    color="cyan",
                )
                created.append(r["handle"])
        elif "arc" in on:
            c = list(ent.Center)
            lx_c = c[0]
            zone = _classify_block_line(lx_c, lx_c, xmn=xmn_local, seat_w=seat_w)
            if zone == "middle":
                skipped_arcs += 1
                continue
            wc = wcs_from_block_local(c[0], c[1])
            cx = wc[0]
            if zone == "right":
                cx -= seat_w
            elif mid_lo < cx < mid_hi:
                skipped_arcs += 1
                continue
            r = driver.draw_arc(
                center=[cx, wc[1], 0],
                radius=float(ent.Radius),
                start_angle=math.degrees(float(ent.StartAngle)),
                end_angle=math.degrees(float(ent.EndAngle)),
                layer=PREVIEW_LAYER,
                color="cyan",
            )
            created.append(r["handle"])
        elif "polyline" in on:
            pts_local = _polyline_local_points(ent)
            out_pts: list[list[float]] = []
            for lx, ly in pts_local:
                wx, wy = wcs_from_block_local(lx, ly)
                mx = _map_x_drop_middle(wx, mid_lo=mid_lo, mid_hi=mid_hi, seat_w=seat_w)
                if mx is None:
                    continue
                out_pts.append([mx, wy])
            if len(out_pts) >= 2:
                r = driver.draw_polyline(
                    points=out_pts,
                    closed=bool(ent.Closed),
                    layer=PREVIEW_LAYER,
                    color="cyan",
                )
                created.append(r["handle"])

    removed = _cleanup_seam_clutter(driver, mid_lo=mid_lo)
    deduped = _dedupe_overlapping_horizontals(driver)
    micro = _remove_micro_fillet_ticks(driver, mid_lo=mid_lo)
    dup = _remove_duplicate_lines(driver)
    degen = _remove_degenerate_lines(driver)
    if removed or deduped or micro or dup or degen:
        created = [
            str(driver.model_space.Item(i).Handle)
            for i in range(driver.model_space.Count)
            if str(driver.model_space.Item(i).Layer) == PREVIEW_LAYER
        ]

    audit = _audit_preview(
        driver,
        ref_min_y=ref_min_y,
        ref_max_y=ref_max_y,
        preview_x0=preview_x0,
        preview_x1=preview_x1,
        seat_w=seat_w,
        expected_lines=expected_lines,
        ref_short_baseline=ref_short_baseline,
        ref_micro_baseline=ref_micro_baseline,
    )

    if not audit["center_seam_vertical_present"]:
        repaired = _ensure_center_seam_from_block(
            driver,
            block,
            wcs_from_block_local=wcs_from_block_local,
            xmn=xmn_local,
            seat_w=seat_w,
            mid_lo=mid_lo,
            y_back_lo=y_back_lo,
            created=created,
        )
        if repaired:
            audit = _audit_preview(
                driver,
                ref_min_y=ref_min_y,
                ref_max_y=ref_max_y,
                preview_x0=preview_x0,
                preview_x1=preview_x1,
                seat_w=seat_w,
                expected_lines=expected_lines,
                ref_short_baseline=ref_short_baseline,
                ref_micro_baseline=ref_micro_baseline,
            )
            audit["center_seam_repaired"] = True

    if removed or deduped or micro or dup or degen:
        audit["cleanup"] = {
            "seam_clutter_removed": removed,
            "overlap_deduped": deduped,
            "micro_ticks_removed": micro,
            "duplicate_lines_removed": dup,
            "degenerate_removed": degen,
        }

    root = Path(__file__).resolve().parent
    report = {
        "status": "vector_redraw_complete" if audit["audit_pass"] else "audit_failed",
        "method": "block_local_zone_map_v4",
        "round": ROUND,
        "reference_handle": "4A2",
        "created_count": len(created),
        "skipped_middle_arcs": skipped_arcs,
        "preview_width_mm": ref_w - seat_w,
        "audit": audit,
    }

    root.joinpath(f"{ROUND}_vector_readback.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    root.joinpath(f"{ROUND}_geometry_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    root.joinpath(f"{ROUND}_execution_summary.json").write_text(
        json.dumps(
            {"status": "executed", "created_handles": ["4A2", *created], "reference_handle": "4A2"},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if audit["audit_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
