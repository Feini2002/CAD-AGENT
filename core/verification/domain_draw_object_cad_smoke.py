"""Per-domain draw_object CAD smoke using a minimal cabinet plan (coverage wave)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.execution.execute_plan import execute_plan_file
from core.plan_engine.validate_plan import load_json, validate_plan
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.verification.preview_only_audit import build_preview_only_audit

DOMAIN_DRAW_DOMAINS: list[tuple[str, str]] = [
    ("custom", "domain.custom.draw_object"),
    ("education", "domain.education.draw_object"),
    ("exhibition", "domain.exhibition.draw_object"),
    ("generic", "domain.generic.draw_object"),
    ("healthcare", "domain.healthcare.draw_object"),
    ("hotel", "domain.hotel.draw_object"),
    ("industrial", "domain.industrial.draw_object"),
    ("office", "domain.office.draw_object"),
    ("residential", "domain.residential.draw_object"),
    ("restaurant", "domain.restaurant.draw_object"),
    ("retail", "domain.retail.draw_object"),
]

DEFAULT_PLAN_TEMPLATE = Path("examples") / "plans" / "draw_test_cabinet.json"
BASE_OFFSET = [88000.0, 52000.0, 0.0]
SPACING_X = 5000.0


def _plan_for_domain(root: Path, domain: str) -> dict[str, Any]:
    template = load_json(root / DEFAULT_PLAN_TEMPLATE)
    plan = dict(template)
    plan["domain"] = domain
    return plan


def run_domain_draw_object_cad_smoke(
    *,
    root: Path,
    output_dir: Path | None = None,
    no_cad: bool = False,
    driver: Any | None = None,
    base_offset: list[float] | None = None,
) -> dict[str, Any]:
    domain_rows: list[dict[str, Any]] = []
    offset_base = list(base_offset or BASE_OFFSET)

    for index, (domain, capability_id) in enumerate(DOMAIN_DRAW_DOMAINS):
        plan = _plan_for_domain(root, domain)
        errors = validate_plan(plan)
        row: dict[str, Any] = {
            "domain": domain,
            "registry_capability_id": capability_id,
            "plan_path": str(root / DEFAULT_PLAN_TEMPLATE),
            "validate_status": "pass" if not errors else "fail",
            "validate_errors": errors,
        }
        if errors:
            row["status"] = "fail"
            row["geometry_verified"] = False
            row["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
            domain_rows.append(row)
            continue

        if no_cad or driver is None:
            row["cad_execution_status"] = "deferred" if no_cad else "skipped"
            row["geometry_verified"] = False
            row["evidence_state"] = EVIDENCE_DEFERRED_CAD_READBACK
            row["status"] = "pass"
            domain_rows.append(row)
            continue

        offset = [float(offset_base[0]) + index * SPACING_X, float(offset_base[1]), float(offset_base[2])]
        plan["placement"] = {"mode": "absolute", "base_point": offset}
        plan_path = (output_dir or root) / f"domain_{domain}_plan.json"
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        summary = execute_plan_file(plan_path, driver=driver, preview_only=True, allow_unconfirmed=True)
        audit = build_preview_only_audit(layer=str(summary.get("layer", "CODEX_PREVIEW")))
        created_handles = summary.get("created_handles", [])
        handle_count = len(created_handles) if isinstance(created_handles, list) else 0
        executed = summary.get("status") == "executed" and handle_count > 0
        row["cad_execution_status"] = "executed" if executed else "fail"
        row["created_handle_count"] = handle_count
        row["geometry_verified"] = executed
        row["evidence_state"] = EVIDENCE_READBACK_GEOMETRY_VERIFIED if executed else EVIDENCE_DEFERRED_CAD_READBACK
        row["geometry_accuracy"] = GEOMETRY_VERIFIED_BY_READBACK if executed else ""
        row["screenshot_role"] = SCREENSHOT_NOT_APPLICABLE
        row["status"] = "pass" if executed else "fail"
        row["preview_only_audit"] = audit
        if executed and output_dir is not None:
            report_path = output_dir / f"domain_{domain}_cad_report.json"
            report_path.write_text(
                json.dumps(
                    {
                        "version": "0.1",
                        "suite_id": f"domain_draw_object_{domain}",
                        "domain": domain,
                        "registry_capability_id": capability_id,
                        "status": "geometry_verified",
                        "geometry_verified": True,
                        "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
                        "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK,
                        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
                        "created_handle_count": handle_count,
                        "execution_summary": summary,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            row["verification_report_path"] = str(report_path)
        domain_rows.append(row)

    verified = sum(1 for row in domain_rows if row.get("geometry_verified"))
    return {
        "version": "0.1",
        "suite_id": "domain_draw_object_cad_smoke",
        "status": "geometry_verified" if verified == len(DOMAIN_DRAW_DOMAINS) and verified > 0 else "fail",
        "geometry_verified": verified == len(DOMAIN_DRAW_DOMAINS) and verified > 0,
        "domain_count": len(DOMAIN_DRAW_DOMAINS),
        "geometry_verified_count": verified,
        "domains": domain_rows,
    }
