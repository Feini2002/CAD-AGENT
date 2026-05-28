#!/usr/bin/env python
"""Two-seater sofa round12 — visual-parts render + audit before delivery."""

from __future__ import annotations

import json
import sys
from pathlib import Path

CASE_ROOT = Path(__file__).resolve().parents[1]
RUNS = Path(__file__).resolve().parent
CHECKLIST = CASE_ROOT / "expected" / "audit_checklist.json"
ROUND = "round12"
REF_HANDLE = "4A2"
GAP_MM = 400.0
VISUAL_PARTS = RUNS / f"{ROUND}_visual_parts.json"

_REPO = CASE_ROOT.parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
if str(RUNS) not in sys.path:
    sys.path.insert(0, str(RUNS))

from core.cad_io.autocad_com import PREVIEW_LAYER, AutoCADComDriver
from core.verification.training_geometry_audit import (
    load_training_audit_checklist,
    merge_legacy_audit_fields,
    run_training_geometry_audit,
)
from part_renderer import render_visual_parts

AGENT_REVIEW_ITEMS = (
    "visual_match_brief",
    "same_product_family_as_reference",
    "no_schematic_shortcut",
)


def _write_agent_review(
    *,
    audit_pass: bool,
    ready_for_user: bool,
    notes: dict[str, str],
    component_checks: dict[str, object],
) -> dict[str, object]:
    checks = {k: {"pass": ready_for_user, "note": notes.get(k, "")} for k in AGENT_REVIEW_ITEMS}
    review = {
        "round": ROUND,
        "audit_pass": audit_pass,
        "agent_review_all_pass": ready_for_user,
        "delivery_allowed": audit_pass and ready_for_user,
        "blocked_reason": "" if audit_pass and ready_for_user else ("agent_visual_review_pending" if audit_pass else "audit_failed"),
        "visual_parts": VISUAL_PARTS.name,
        "component_checks": component_checks,
        "checks": checks,
    }
    body = [
        f"# {ROUND} Agent 自检",
        "",
        f"- audit_pass: {audit_pass}",
        f"- delivery_allowed: {review['delivery_allowed']}",
        "",
        "| 项 | pass | 说明 |",
        "|---|---|---|",
    ]
    for k in AGENT_REVIEW_ITEMS:
        body.append(f"| {k} | {checks[k]['pass']} | {checks[k]['note']} |")
    if not review["delivery_allowed"]:
        body.extend(["", "**禁止请你验收** — 须 Repair 后再跑。"])
    RUNS.joinpath(f"{ROUND}_agent_review.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    RUNS.joinpath(f"{ROUND}_audit_review.md").write_text("\n".join(body) + "\n", encoding="utf-8")
    return review


def main() -> int:
    driver = AutoCADComDriver(connect_existing_only=True)
    driver.ensure_layer(PREVIEW_LAYER)
    ms = driver.model_space

    ref = None
    for i in range(ms.Count):
        ent = ms.Item(i)
        if str(getattr(ent, "Handle", "")) == REF_HANDLE:
            ref = ent
            break
    if ref is None:
        raise RuntimeError(f"Reference block {REF_HANDLE} not found.")

    checklist = load_training_audit_checklist(CHECKLIST)
    visual_parts = json.loads(VISUAL_PARTS.read_text(encoding="utf-8"))

    for i in range(ms.Count - 1, -1, -1):
        ent = ms.Item(i)
        if str(ent.Layer) == PREVIEW_LAYER:
            ent.Delete()

    bb = ref.GetBoundingBox()
    ref_min_y = float(bb[0][1])
    ref_max_x = float(bb[1][0])
    ref_h = float(bb[1][1]) - ref_min_y

    px0 = ref_max_x + GAP_MM
    sizing = visual_parts.get("sizing", {})
    w2 = float(sizing.get("target_width_mm", 1870))
    px1 = px0 + w2
    py0 = ref_min_y
    h = float(sizing.get("height_mm", ref_h))

    render_report = render_visual_parts(
        driver,
        visual_parts,
        origin=[px0, py0, 0],
        width=w2,
        height=h,
    )
    part_handles = render_report["part_handles"]
    created = [handle for handles in part_handles.values() for handle in handles]

    audit = run_training_geometry_audit(
        driver,
        checklist,
        preview_bounds={"x0": px0, "x1": px1, "y0": py0, "y1": py0 + h},
        reference_handle=REF_HANDLE,
    )
    audit_flat = merge_legacy_audit_fields(audit)

    component_checks = {
        part_id: {
            "declared": True,
            "created_handles": handles,
            "pass": bool(handles),
        }
        for part_id, handles in part_handles.items()
    }

    # Agent review gate: default block delivery; set True only after screenshot-based self-review.
    agent_review = _write_agent_review(
        audit_pass=bool(audit["audit_pass"]),
        ready_for_user=False,
        component_checks=component_checks,
        notes={
            "visual_match_brief": "待 Agent 读 round12_preview.png 确认",
            "same_product_family_as_reference": "待 Agent 对照左侧参考块确认",
            "no_schematic_shortcut": "机器未命中 schematic" if audit["audit_pass"] else "audit 未过",
        },
    )

    report = {
        "status": "executed_pending_agent_review" if audit["audit_pass"] else "audit_failed",
        "method": "round12_visual_parts_renderer",
        "round": ROUND,
        "reference_handle": REF_HANDLE,
        "visual_parts": VISUAL_PARTS.name,
        "created_count": len(created),
        "part_handles": part_handles,
        "audit": audit_flat,
        "agent_review": agent_review,
    }
    for name, obj in [
        (f"{ROUND}_vector_readback.json", report),
        (f"{ROUND}_geometry_audit.json", audit_flat),
        (
            f"{ROUND}_execution_summary.json",
            {
                "status": "executed",
                "created_handles": [REF_HANDLE, *created],
                "preview_created_handles": created,
                "part_handles": part_handles,
                "reference_handle": REF_HANDLE,
                "CODEX_PREVIEW_only": True,
            },
        ),
        (
            f"{ROUND}_intent.json",
            {
                "case_id": CASE_ROOT.name,
                "round": ROUND,
                "ready_to_draw": True,
                "execution_route": "visual_parts_renderer",
                "audit_checklist": str(CHECKLIST.relative_to(CASE_ROOT)),
                "visual_parts": VISUAL_PARTS.name,
                "target_width_mm": w2,
            },
        ),
    ]:
        RUNS.joinpath(name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not audit["audit_pass"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
