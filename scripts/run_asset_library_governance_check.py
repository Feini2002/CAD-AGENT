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
EVIDENCE_LIST_KEYS = {"evidenceRefs", "refs"}
EVIDENCE_DETAIL_KEYS = {
    "summary",
    "report",
    "screenshot",
    "focusedScreenshot",
    "reportPath",
    "screenshotPath",
    "preview",
    "previewPath",
}
EVIDENCE_SECTION_KEYS = {
    "nativeVisiblePanelEvidence",
    "reuseWorkflowProbe",
    "reuseReplay",
    "visiblePanelEvidence",
    "verification",
    "evidence",
    "evidenceLinks",
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _normalize_ref(value: str) -> str:
    text = str(value).strip().replace("\\", "/")
    if "#" in text:
        text = text.split("#", 1)[0]
    return text


def _looks_like_local_evidence_ref(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = _normalize_ref(value)
    if not text or text.startswith(("http://", "https://")):
        return False
    if "<" in text or ">" in text:
        return False
    suffix = Path(text).suffix.lower()
    if suffix not in {".json", ".png", ".jpg", ".jpeg", ".md", ".dwg", ".dwt", ".pdf"}:
        return False
    return text.startswith(("output/", "projects/", "docs/", "agents/", "libraries/"))


def _collect_evidence_refs(value: Any, *, parent_key: str = "") -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if key_text in EVIDENCE_LIST_KEYS and isinstance(item, list):
                refs.extend(_normalize_ref(str(ref)) for ref in item if _looks_like_local_evidence_ref(ref))
            if key_text in EVIDENCE_DETAIL_KEYS and _looks_like_local_evidence_ref(item):
                refs.append(_normalize_ref(str(item)))
            if isinstance(item, (dict, list)):
                refs.extend(_collect_evidence_refs(item, parent_key=key_text))
        return refs
    if isinstance(value, list):
        for item in value:
            refs.extend(_collect_evidence_refs(item, parent_key=parent_key))
    return refs


def _missing_evidence_refs(root: Path, package: dict[str, Any]) -> list[str]:
    refs = _collect_evidence_refs(package)
    missing: list[str] = []
    seen: set[str] = set()
    for ref in refs:
        if ref in seen:
            continue
        seen.add(ref)
        if not (root / ref).is_file():
            missing.append(ref)
    return missing


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
        missing_evidence = _missing_evidence_refs(root, package)
        if missing_evidence:
            issues.extend(f"referenced evidence file missing: {path}" for path in missing_evidence)
        else:
            checked.append("referenced evidence files exist")
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
        model_review = shelf_report.get("modelVisualReview", {}) if isinstance(shelf_report.get("modelVisualReview"), dict) else {}
        protected = shelf_report.get("protectedContentReadback", {}) if isinstance(shelf_report.get("protectedContentReadback"), dict) else {}
        created = shelf_report.get("createdEntityReadback", {}) if isinstance(shelf_report.get("createdEntityReadback"), dict) else {}
        latest_shelf_rack_audit = audit_visual_rack_plan(
            visual_rack_plan=shelf_report.get("rackPlan") if isinstance(shelf_report.get("rackPlan"), dict) else None,
            entity_readback=created,
            protected_content_report=protected,
            clearance_report=clearance,
            readability_report=readability,
            model_review_report=model_review,
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
            and (not model_review or model_review.get("status") == "pass")
        ):
            checked.append("latest shelf layout CAD readback, shelf/content clearance, and warehouse readability audit")
            if model_review:
                checked.append("model-backed visual layout review")
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
