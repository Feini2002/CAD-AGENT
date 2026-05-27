"""Commercial fitout de-identified sample: SHELL_MODEL / proposal -> user confirmation bundle (C-CFIT-05)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.agents.fitout_sample_specs import (
    DEFAULT_FITOUT_SAMPLE_ID,
    FITOUT_SAMPLE_ID,
    FitoutSampleSpec,
    resolve_fitout_sample_spec,
    resolve_fitout_sample_spec_for_workflow,
)
from core.project_samples.loader import load_sample_inputs
from core.project_samples.protocol import scan_project_sample
from core.proposal_engine.confirmed_finalize import finalize_confirmed_cad_plans
from core.proposal_engine.user_confirmation import (
    build_user_confirmation,
    load_user_confirmation,
    save_user_confirmation,
    validate_confirmation_against_proposal,
)
from core.schemas.validator import validate_value
from core.workflows.blank_shell_pipeline import run_blank_shell_pipeline

BUNDLE_VERSION = "0.1"
DEFAULT_CONFIRMATION_REL = Path("examples/confirmations/commercial_fitout_sample_confirmation.json")
SCHEMA_NAME = "commercial_fitout_sample_confirmation_bundle.schema.json"

CAD_ARTIFACT_KEYS = (
    "cad_plan",
    "cad_plans",
    "cad_plan_items",
    "dry_run_report",
    "dry_run_reports",
    "verification_report",
    "verification_reports",
)


def default_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_workflow_path(project_root: Path | None = None, *, sample_id: str | None = None) -> Path:
    spec = resolve_fitout_sample_spec(sample_id)
    return (project_root or default_project_root()) / spec.workflow_rel


def default_sample_dir(project_root: Path | None = None, *, sample_id: str | None = None) -> Path:
    spec = resolve_fitout_sample_spec(sample_id)
    return (project_root or default_project_root()) / "projects" / spec.sample_id


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_confirmation_notes(notes: list[Any]) -> tuple[list[str], list[str]]:
    """Split free-form confirmation notes into assumptions vs risks."""

    assumptions: list[str] = []
    risks: list[str] = []
    for item in notes:
        text = str(item).strip()
        if not text:
            continue
        lowered = text.lower()
        if lowered.startswith("risk:") or lowered.startswith("风险:"):
            risks.append(text.split(":", 1)[-1].strip() if ":" in text else text)
        elif lowered.startswith("assumption:") or lowered.startswith("假设:"):
            assumptions.append(text.split(":", 1)[-1].strip() if ":" in text else text)
        else:
            assumptions.append(text)
    return assumptions, risks


def build_assumptions_risks(
    *,
    brief: dict[str, Any],
    confirmation: dict[str, Any],
) -> dict[str, Any]:
    brief_assumptions = [str(item) for item in brief.get("assumptions", []) if str(item).strip()]
    local_prefs = confirmation.get("local_preferences", {})
    notes = local_prefs.get("notes", []) if isinstance(local_prefs, dict) else []
    note_assumptions, note_risks = classify_confirmation_notes(list(notes) if isinstance(notes, list) else [])
    return {
        "assumptions": brief_assumptions + note_assumptions,
        "risks": note_risks,
        "source": {
            "brief_id": str(brief.get("brief_id", "")),
            "confirmation_id": str(confirmation.get("confirmation_id", "")),
        },
    }


def assert_pre_confirmation_gate(result: dict[str, Any]) -> list[str]:
    """Ensure CAD_PLAN artifacts are absent before user confirmation."""

    errors: list[str] = []
    if result.get("status") != "confirmation_pending":
        errors.append(f"expected confirmation_pending, got {result.get('status')!r}")
    gate = result.get("confirmation_gate", {})
    if not isinstance(gate, dict):
        errors.append("confirmation_gate missing")
    elif gate.get("cad_plan_generation") != "blocked":
        errors.append("confirmation_gate.cad_plan_generation must be blocked")
    artifacts = result.get("artifacts", {})
    if not isinstance(artifacts, dict):
        errors.append("artifacts must be an object")
        return errors
    for key in CAD_ARTIFACT_KEYS:
        path = artifacts.get(key)
        if path and Path(path).exists():
            errors.append(f"pre-confirmation must not write {key}")
    proposal_path = artifacts.get("design_proposal")
    if not proposal_path or not Path(proposal_path).is_file():
        errors.append("design_proposal artifact required before confirmation")
    return errors


def build_confirmation_for_sample_proposal(
    proposal: dict[str, Any],
    *,
    spec: FitoutSampleSpec,
    action: str = "accept_with_risks",
    risk_notes: list[str] | None = None,
) -> dict[str, Any]:
    candidates = [item for item in proposal.get("candidates", []) if isinstance(item, dict)]
    if not candidates:
        raise ValueError("design_proposal has no candidates")
    selected = str(candidates[0].get("candidate_id", ""))
    rejected = [
        {
            "candidate_id": str(item.get("candidate_id", "")),
            "reason_code": "user_rejected",
            "reason_note": f"Not selected in {spec.sample_id} confirmation.",
        }
        for item in candidates
        if str(item.get("candidate_id", "")) != selected
    ]
    confirmation = build_user_confirmation(
        proposal=proposal,
        selected_candidate_id=selected,
        action=action,
        rejected_candidates=rejected,
    )
    confirmation["confirmation_id"] = spec.confirmation_id
    notes = list(spec.default_notes)
    if risk_notes:
        notes.extend(risk_notes)
    confirmation.setdefault("local_preferences", {})
    confirmation["local_preferences"]["notes"] = notes
    return confirmation


def run_fitout_sample_pre_confirmation(
    *,
    output_dir: Path,
    project_root: Path | None = None,
    workflow_path: Path | None = None,
    sample_id: str | None = None,
) -> dict[str, Any]:
    """Run blank-shell pipeline until DESIGN_PROPOSAL; block CAD_PLAN until user confirms."""

    root = project_root or default_project_root()
    workflow = workflow_path or default_workflow_path(root, sample_id=sample_id)
    spec = (
        resolve_fitout_sample_spec_for_workflow(workflow, project_root=root)
        if workflow_path is not None
        else resolve_fitout_sample_spec(sample_id)
    )
    sample_dir = root / "projects" / spec.sample_id
    scan = scan_project_sample(sample_dir, projects_root=root / "projects")
    if scan["status"] != "pass":
        return {
            "status": "invalid",
            "errors": [f"sample protocol scan failed: {scan}"],
            "artifacts": {},
        }
    load_sample_inputs(spec.sample_id, projects_root=root / "projects")
    result = run_blank_shell_pipeline(workflow, output_dir=output_dir)
    result["sample_id"] = spec.sample_id
    result["workflow_path"] = str(workflow)
    gate_errors = assert_pre_confirmation_gate(result)
    if gate_errors:
        result["status"] = "invalid"
        result.setdefault("errors", []).extend(gate_errors)
    return result


def build_sample_confirmation_bundle(
    *,
    artifact_dir: Path,
    brief: dict[str, Any],
    confirmation: dict[str, Any],
    finalize_report: dict[str, Any],
    confirmed_bundle: dict[str, Any],
    pre_confirmation: dict[str, Any],
    spec: FitoutSampleSpec,
) -> dict[str, Any]:
    assumptions_risks = build_assumptions_risks(brief=brief, confirmation=confirmation)
    return {
        "version": BUNDLE_VERSION,
        "sample_id": spec.sample_id,
        "workflow_path": str(pre_confirmation.get("workflow_path", "")),
        "proposal_id": str(confirmed_bundle.get("proposal_id", "")),
        "confirmation_id": str(confirmed_bundle.get("confirmation_id", "")),
        "assumptions_risks": assumptions_risks,
        "confirmation_gate": pre_confirmation.get("confirmation_gate", {}),
        "controlled_cad_policy": confirmed_bundle.get("controlled_cad_policy", {}),
        "confirmed_cad_plan_bundle": confirmed_bundle,
        "finalize_report": {
            "status": finalize_report.get("status"),
            "cad_plan_count": finalize_report.get("cad_plan_count"),
            "validation_all_valid": finalize_report.get("validation_all_valid"),
            "dry_run_valid_count": finalize_report.get("dry_run_valid_count"),
        },
        "evidence_claim": "non_cad_confirmation_loop_only",
        "geometry_verified": False,
    }


def run_fitout_sample_confirmation_closure(
    artifact_dir: Path,
    confirmation_path: Path,
    *,
    project_root: Path | None = None,
    sample_id: str | None = None,
    workflow_path: Path | None = None,
) -> dict[str, Any]:
    """Apply user confirmation and emit confirmed CAD_PLAN bundle plus assumptions/risks record."""

    root = project_root or default_project_root()
    workflow = workflow_path or default_workflow_path(root, sample_id=sample_id)
    spec = (
        resolve_fitout_sample_spec_for_workflow(workflow, project_root=root)
        if workflow_path is not None
        else resolve_fitout_sample_spec(sample_id)
    )
    artifact_dir = artifact_dir.resolve()
    brief_path = root / "projects" / spec.sample_id / "fixtures" / "design_brief.json"
    brief = _read_json(brief_path)
    proposal = _read_json(artifact_dir / "design_proposal.json")
    confirmation = load_user_confirmation(confirmation_path)
    validation_errors = validate_confirmation_against_proposal(confirmation, proposal)
    if validation_errors:
        return {"status": "invalid", "errors": validation_errors}

    finalize_report = finalize_confirmed_cad_plans(artifact_dir, confirmation_path)
    if finalize_report.get("status") != "ok":
        return finalize_report

    confirmed_bundle = _read_json(artifact_dir / "confirmed_cad_plan_bundle.json")
    pre_confirmation = {
        "workflow_path": str(workflow),
        "confirmation_gate": {
            "cad_plan_generation": "blocked",
            "needs_confirmation": True,
        },
    }
    sample_bundle = build_sample_confirmation_bundle(
        artifact_dir=artifact_dir,
        brief=brief,
        confirmation=confirmation,
        finalize_report=finalize_report,
        confirmed_bundle=confirmed_bundle,
        pre_confirmation=pre_confirmation,
        spec=spec,
    )
    schema_path = root / "core" / "schemas" / SCHEMA_NAME
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema_errors = validate_value(sample_bundle, schema)
    if schema_errors:
        return {"status": "invalid", "errors": schema_errors, "finalize_report": finalize_report}

    bundle_path = artifact_dir / spec.bundle_filename
    _write_json(bundle_path, sample_bundle)
    finalize_report["sample_confirmation_bundle_path"] = str(bundle_path)
    return finalize_report


def run_fitout_sample_confirmation_loop(
    output_dir: Path,
    confirmation_path: Path | None = None,
    *,
    project_root: Path | None = None,
    sample_id: str | None = None,
    workflow_path: Path | None = None,
) -> dict[str, Any]:
    """Full C-CFIT-05 loop: pre-confirmation gate -> user confirmation -> confirmed bundle."""

    root = project_root or default_project_root()
    workflow = workflow_path or default_workflow_path(root, sample_id=sample_id)
    spec = (
        resolve_fitout_sample_spec_for_workflow(workflow, project_root=root)
        if workflow_path is not None
        else resolve_fitout_sample_spec(sample_id)
    )
    output_dir = output_dir.resolve()
    pre = run_fitout_sample_pre_confirmation(
        output_dir=output_dir,
        project_root=root,
        workflow_path=workflow,
    )
    if pre.get("status") != "confirmation_pending":
        return pre

    proposal = _read_json(output_dir / "design_proposal.json")
    if confirmation_path and confirmation_path.is_file():
        confirmation = load_user_confirmation(confirmation_path)
    else:
        confirmation = build_confirmation_for_sample_proposal(proposal, spec=spec)
        confirmation_path = output_dir / "user_confirmation.json"
        save_user_confirmation(confirmation_path, confirmation)

    return run_fitout_sample_confirmation_closure(
        output_dir,
        confirmation_path,
        project_root=root,
        workflow_path=workflow,
    )
