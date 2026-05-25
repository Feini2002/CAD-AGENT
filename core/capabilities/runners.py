"""Runner adapters for Core capabilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.benchmarks.runner import run_benchmark_suite
from core.drawing_analysis.shell_loader import load_manual_shell
from core.layout_engine.basic_layout import create_layout_candidates
from core.layout_engine.path_generation import generate_circulation_candidates
from core.layout_engine.placement import create_zone_placements
from core.layout_engine.zone_splitter import split_zones
from core.object_engine.object_explainer import explain_object_spec
from core.plan_engine.model_to_plan import model_to_plans
from core.project_model.project_builder import build_project_model
from core.proposal_engine.proposal_comparison import compare_layout_candidates
from core.verification.verification_report import build_verification_report
from core.workflows.artifact_graph import build_artifact_graph_from_workflow
from core.workflows.blank_shell_pipeline import run_blank_shell_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _resolve_under_project_root(value: str, label: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    resolved = path.resolve()
    if not _is_relative_to(resolved, PROJECT_ROOT.resolve()):
        raise ValueError(f"{label} must stay under project root")
    return resolved


def _resolve_under_output_root(value: str, label: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    resolved = path.resolve()
    if not _is_relative_to(resolved, (PROJECT_ROOT / "output").resolve()):
        raise ValueError(f"{label} must stay under project output directory")
    return resolved


def _project_model_build(payload: dict[str, Any]) -> dict[str, Any]:
    return build_project_model(
        payload["brief"],
        payload["drawing_model"],
        shell_model=payload.get("shell_model"),
    ).project_model


def _layout_create_candidates(payload: dict[str, Any]) -> dict[str, Any]:
    return create_layout_candidates(
        project_model=payload["project_model"],
        object_specs=payload["object_specs"],
        preferences=payload.get("preferences", {}),
    )


def _layout_generate_circulation_candidates(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return generate_circulation_candidates(
        payload["project_model"],
        preferences=payload.get("preferences", {}),
    )


def _layout_split_function_zones(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return split_zones(
        payload["shell_model"],
        payload["circulation_model"],
        payload.get("constraints", {}),
    )


def _layout_create_zone_placements(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return create_zone_placements(
        payload["zones"],
        object_types=payload["object_types"],
        block_library=payload.get("block_library"),
        preferences=payload.get("preferences", {}),
        path_surfaces=payload.get("path_surfaces", []),
        fixed_obstacles=payload.get("fixed_obstacles", []),
    )


def _plan_model_to_plans(payload: dict[str, Any]) -> dict[str, Any]:
    return model_to_plans(
        object_spec=payload.get("object_spec"),
        object_specs=payload.get("object_specs"),
        layout_proposal=payload.get("layout_proposal"),
        design_proposal=payload.get("design_proposal"),
        confirmed=bool(payload.get("confirmed", False)),
    )


def _object_explain(payload: dict[str, Any]) -> dict[str, Any]:
    return explain_object_spec(payload["object_spec"], style_profile=payload.get("style_profile"))


def _proposal_compare_layout_candidates(payload: dict[str, Any]) -> dict[str, Any]:
    return compare_layout_candidates(payload["layout_proposal"])


def _verification_no_cad_report(payload: dict[str, Any]) -> dict[str, Any]:
    plan_path = _resolve_under_project_root(payload["plan_path"], "plan_path")
    return build_verification_report(plan_path=plan_path)


def _workflow_artifact_graph(payload: dict[str, Any]) -> dict[str, Any]:
    workflow_path = _resolve_under_project_root(payload["workflow_path"], "workflow_path")
    graph = build_artifact_graph_from_workflow(workflow_path)
    return {
        "dependency_order": graph.dependency_order(),
        "artifacts": graph.to_index(),
        "path_checks": graph.validate_paths(PROJECT_ROOT),
    }


def _workflow_blank_shell_pipeline(payload: dict[str, Any]) -> dict[str, Any]:
    workflow_path = _resolve_under_project_root(payload["workflow_path"], "workflow_path")
    output_dir = _resolve_under_output_root(
        payload.get("output_dir", "output/test_artifacts/capabilities/blank_shell_pipeline"),
        "output_dir",
    )
    return run_blank_shell_pipeline(workflow_path, output_dir=output_dir)


def _benchmark_non_cad_suite(payload: dict[str, Any]) -> dict[str, Any]:
    suite_path = _resolve_under_project_root(payload["suite_path"], "suite_path")
    output_root = _resolve_under_output_root(
        payload.get("output_root", "output/test_artifacts/benchmarks/capability"),
        "output_root",
    )
    return run_benchmark_suite(suite_path, output_root=output_root)


def _drawing_analysis_load_shell_model(payload: dict[str, Any]) -> dict[str, Any]:
    shell_path = _resolve_under_project_root(payload["shell_path"], "shell_path")
    return load_manual_shell(shell_path)

