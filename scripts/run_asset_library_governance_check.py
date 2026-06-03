#!/usr/bin/env python3
"""Check asset-library governance wiring and emit a hardening decision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.assets.system_asset_library_governance import audit_visual_rack_plan  # noqa: E402


REQUIRED_AGENTS = (
    "pipeline_asset_governor",
    "pipeline_asset_librarian",
    "pipeline_asset_dwg_curator",
    "pipeline_asset_reuse_auditor",
)
REQUIRED_ZONES = (
    "00_INDEX",
    "01_CLEAN_ASSETS",
    "02_PREVIEW_CARDS",
    "03_REVIEW_QUARANTINE",
    "99_EVIDENCE_LINKS",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def run_check(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    root = Path(project_root)
    issues: list[str] = []
    checked: list[str] = []
    visual_rack_audit: dict[str, Any] = {}
    latest_shelf_rack_audit: dict[str, Any] = {}
    latest_shelf_cad_proof = False

    manifest_path = root / "agents/pipeline/pipeline_manifest.json"
    manifest = _read_json(manifest_path)
    agent_ids = {str(agent.get("agent_id", "")) for agent in manifest.get("agents", []) if isinstance(agent, dict)}
    for agent_id in REQUIRED_AGENTS:
        if agent_id in agent_ids:
            checked.append(f"agent registered: {agent_id}")
        else:
            issues.append(f"missing agent registration: {agent_id}")
        agent_file = root / "agents/pipeline" / agent_id.replace("pipeline_", "") / "agent.json"
        if agent_file.is_file():
            checked.append(f"agent definition exists: {agent_id}")
        else:
            issues.append(f"missing agent definition: {agent_file.as_posix()}")

    orchestration = manifest.get("orchestration", {}) if isinstance(manifest.get("orchestration"), dict) else {}
    flow_variants = orchestration.get("flow_variants", {}) if isinstance(orchestration.get("flow_variants"), dict) else {}
    sedimentation_flow = flow_variants.get("system_asset_sedimentation", [])
    if isinstance(sedimentation_flow, list) and "pipeline_asset_governor" in sedimentation_flow:
        checked.append("system_asset_sedimentation flow routes through governor")
    else:
        issues.append("system_asset_sedimentation flow does not route through governor")
    hard_gates = orchestration.get("hard_gates", {}) if isinstance(orchestration.get("hard_gates"), dict) else {}
    if "asset_governance" in hard_gates:
        checked.append("asset_governance hard gate")
    else:
        issues.append("missing asset_governance hard gate")

    protocol_text = (root / "docs/architecture/system-asset-sedimentation-protocol.md").read_text(encoding="utf-8")
    for zone in REQUIRED_ZONES:
        if zone in protocol_text:
            checked.append(f"protocol zone documented: {zone}")
        else:
            issues.append(f"protocol missing zone: {zone}")
    if "polishHardeningDecision" in protocol_text:
        checked.append("protocol documents polishHardeningDecision")
    else:
        issues.append("protocol missing polishHardeningDecision")

    package_path = root / "libraries/system_library/drawing_standards/basic/assets.json"
    if package_path.is_file():
        package = _read_json(package_path)
        native_layout = package.get("nativeLayout", {}) if isinstance(package.get("nativeLayout"), dict) else {}
        visual_rack_plan = native_layout.get("visualRackPlan")
        visual_rack_audit = audit_visual_rack_plan(visual_rack_plan=visual_rack_plan)
        if visual_rack_audit.get("status") == "pass":
            checked.append("visualRackPlan v2 warehouse audit")
        else:
            issues.extend(str(issue) for issue in visual_rack_audit.get("issues", []))
    else:
        issues.append("missing drawing_standards.basic system asset package for visualRackPlan audit")

    shelf_report_path = root / "output/validation_runs/system-assets/asset-library-shelves/shelf_layout_report.json"
    if shelf_report_path.is_file():
        shelf_report = _read_json(shelf_report_path)
        clearance = shelf_report.get("visualClearanceAudit", {}) if isinstance(shelf_report.get("visualClearanceAudit"), dict) else {}
        readability = shelf_report.get("visualReadabilityAudit", {}) if isinstance(shelf_report.get("visualReadabilityAudit"), dict) else {}
        protected = shelf_report.get("protectedContentReadback", {}) if isinstance(shelf_report.get("protectedContentReadback"), dict) else {}
        created = shelf_report.get("createdEntityReadback", {}) if isinstance(shelf_report.get("createdEntityReadback"), dict) else {}
        latest_shelf_rack_audit = audit_visual_rack_plan(
            visual_rack_plan=shelf_report.get("rackPlan") if isinstance(shelf_report.get("rackPlan"), dict) else None,
            entity_readback=created,
            clearance_report=clearance,
            readability_report=readability,
        )
        if (
            shelf_report.get("status") == "pass"
            and shelf_report.get("savedAssetDwg") is True
            and shelf_report.get("savedCurrentBusinessDwg") is False
            and clearance.get("status") == "pass"
            and int(clearance.get("overlapCount") or 0) == 0
            and readability.get("status") == "pass"
            and int(readability.get("issueCount") or 0) == 0
            and protected.get("status") == "ok"
            and created.get("status") == "ok"
            and latest_shelf_rack_audit.get("status") == "pass"
            and isinstance(created.get("entityBboxes"), list)
            and len(created.get("entityBboxes")) > 0
        ):
            checked.append("latest shelf layout CAD readback, shelf/content clearance, and warehouse readability audit")
            latest_shelf_cad_proof = True
        else:
            issues.append("latest shelf layout report does not prove saved CAD readback with zero shelf/content overlap and readable warehouse layout")
            issues.extend(str(issue) for issue in latest_shelf_rack_audit.get("issues", []))
    else:
        issues.append("missing latest shelf layout report for CAD readback and shelf/content clearance audit")

    status = "pass" if not issues else "fail"
    categories = ["complete_for_current_scope"] if not issues else ["needs_agent_rule_review"]
    if visual_rack_audit and visual_rack_audit.get("status") != "pass":
        categories = ["needs_visual_warehouse_relayout", *categories]
    return {
        "status": status,
        "governorAgentId": "pipeline_asset_governor",
        "checked": checked,
        "issues": issues,
        "visualRackAudit": visual_rack_audit,
        "latestShelfRackAudit": latest_shelf_rack_audit,
        "polishHardeningDecision": {
            "status": categories[0],
            "categories": categories,
            "nativeCadRelayout": "checked" if latest_shelf_cad_proof else "not_run",
            "reuseReplay": "not_run",
            "scope": "asset_library_governance_package",
            "evidenceBoundary": {
                "checked": checked,
                "notChecked": ["real CAD reuse replay"]
                if latest_shelf_cad_proof
                else ["native CAD relayout", "native DWG save/readback", "real CAD reuse replay"],
            },
        },
        "wroteCad": False,
        "savedDwg": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check system asset-library governance wiring.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_check(project_root=args.project_root)
    if args.output:
        output = args.output if args.output.is_absolute() else args.project_root / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
