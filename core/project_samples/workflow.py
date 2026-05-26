"""Run blank-shell workflow for project samples (BETA-PROJECT-SAMPLE-03)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.project_samples.loader import load_sample_inputs
from core.project_samples.protocol import scan_project_sample
from core.workflows.blank_shell_pipeline import run_blank_shell_pipeline


DEFAULT_SAMPLE_ID = "sample_blank_shell"
DEFAULT_WORKFLOW_REL = Path("examples/workflows/sample_blank_shell_project_loop.json")

MANIFEST_REQUIRED_OUTPUT_KEYS = (
    "cad_plan",
    "dry_run_report",
    "verification_report",
)


def default_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_projects_root() -> Path:
    return default_project_root() / "projects"


def default_sample_workflow_path(project_root: Path | None = None) -> Path:
    root = project_root or default_project_root()
    return root / DEFAULT_WORKFLOW_REL


def run_sample_blank_shell_workflow(
    sample_id: str = DEFAULT_SAMPLE_ID,
    *,
    project_root: Path | None = None,
    output_dir: Path,
    workflow_path: Path | None = None,
    projects_root: Path | None = None,
) -> dict[str, Any]:
    """Run blank-shell pipeline using project sample fixtures after protocol scan."""

    root = project_root or default_project_root()
    projects = projects_root or (root / "projects")
    sample_dir = projects / sample_id
    scan = scan_project_sample(sample_dir, projects_root=projects)
    if scan["status"] != "pass":
        return {
            "status": "invalid",
            "errors": [f"sample protocol scan failed: {scan}"],
            "artifacts": {},
            "metrics": {},
        }
    load_sample_inputs(sample_id, projects_root=projects)

    workflow = workflow_path or default_sample_workflow_path(root)
    result = run_blank_shell_pipeline(workflow, output_dir=output_dir)
    result["sample_id"] = sample_id
    result["workflow_path"] = str(workflow)
    return result


def validate_sample_workflow_result(result: dict[str, Any]) -> list[str]:
    """Return errors when sample workflow output does not meet BETA-PROJECT-SAMPLE-03 contract."""

    errors: list[str] = []
    if result.get("status") != "ok":
        errors.append(f"pipeline status expected ok, got {result.get('status')!r}")
    artifacts = result.get("artifacts", {})
    if not isinstance(artifacts, dict):
        errors.append("artifacts must be an object")
        return errors
    for key in MANIFEST_REQUIRED_OUTPUT_KEYS:
        path = artifacts.get(key)
        if not path or not Path(path).is_file():
            errors.append(f"missing artifact file for {key}")

    dry_run = result.get("dry_run_report", {})
    if not isinstance(dry_run, dict):
        errors.append("dry_run_report missing")
    elif dry_run.get("status") != "valid":
        errors.append(f"dry_run_report.status expected valid, got {dry_run.get('status')!r}")

    verification = result.get("verification_report", {})
    if not isinstance(verification, dict):
        errors.append("verification_report missing")
    elif verification.get("status") != "unverified":
        errors.append(
            f"verification_report.status expected unverified without CAD readback, got {verification.get('status')!r}"
        )

    cad_plan_path = artifacts.get("cad_plan")
    if cad_plan_path and Path(cad_plan_path).is_file():
        plan = json.loads(Path(cad_plan_path).read_text(encoding="utf-8"))
        layer = plan.get("drawing", {}).get("layer")
        if layer != "CODEX_PREVIEW":
            errors.append(f"cad_plan layer expected CODEX_PREVIEW, got {layer!r}")

    summary = result.get("dry_run_summary", {})
    if isinstance(summary, dict) and summary.get("valid_count", 0) < 1:
        errors.append("dry_run_summary.valid_count must be >= 1")

    return errors


def write_sample_workflow_report(
    result: dict[str, Any],
    *,
    output_dir: Path,
) -> Path:
    """Persist a compact machine-readable summary beside pipeline artifacts."""

    payload = {
        "version": "0.1",
        "sample_id": result.get("sample_id", DEFAULT_SAMPLE_ID),
        "workflow_path": result.get("workflow_path", ""),
        "status": result.get("status", ""),
        "contract_errors": validate_sample_workflow_result(result),
        "metrics": result.get("metrics", {}),
        "dry_run_summary": result.get("dry_run_summary", {}),
        "verification_summary": result.get("verification_summary", {}),
        "artifacts": result.get("artifacts", {}),
        "evidence_claim": "non_cad_pipeline_only",
        "geometry_verified": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "sample_workflow_report.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
